from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'geoffrey',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='velib_dataproc_pipeline',
    default_args=default_args,
    description='Pipeline Ingestion, Transformation et Chargement Velib',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['mspr', 'velib'],
) as dag:

    fetch_api_data = BashOperator(
        task_id="fetch_api_data",
        bash_command="python3 /opt/airflow/dags/fetch_velib.py",
    )

    run_pyspark_ingestion = DataprocSubmitJobOperator(
        task_id="run_pyspark_ingestion",
        job={
            "placement": {
                "cluster_name": "velib-spark-cluster"
            },
            "pyspark_job": {
                "main_python_file_uri": "gs://velibdata-datalake-mspr/scripts/ingestion_pyspark.py",
            }
        },
        region="europe-west9",
        project_id="velibdata-mspr",
        cancel_on_kill=True,
        wait_timeout=600,
    )

    run_pyspark_trusted = DataprocSubmitJobOperator(
        task_id="run_pyspark_trusted",
        job={
            "placement": {
                "cluster_name": "velib-spark-cluster"
            },
            "pyspark_job": {
                "main_python_file_uri": "gs://velibdata-datalake-mspr/scripts/transform_trusted_pyspark.py",
            }
        },
        region="europe-west9",
        project_id="velibdata-mspr",
        cancel_on_kill=True,
        wait_timeout=600,
    )

    load_trusted_to_bigquery = GCSToBigQueryOperator(
        task_id='load_trusted_to_bigquery',
        bucket='velibdata-datalake-mspr',
        source_objects=['2_trusted_zone/velib_cleaned.parquet/*.parquet'],
        destination_project_dataset_table='velibdata-mspr.trusted_zone.station_status',
        source_format='PARQUET',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        autodetect=True,
    )

    fetch_api_data >> run_pyspark_ingestion >> run_pyspark_trusted >> load_trusted_to_bigquery