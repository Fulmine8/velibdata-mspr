from pyspark.sql import SparkSession
from datetime import datetime

def main():
    spark = SparkSession.builder.appName("Raw_Zone_Ingestion").getOrCreate()
    BUCKET_NAME = "velibdata-datalake-mspr"
    
    try:
        # 1. Lecture du dump JSON technique déposé par la VM
        input_path = f"gs://{BUCKET_NAME}/1_raw_zone/api_dump.json"
        df = spark.read.json(input_path)
        
        # 2. Génération de l'horodatage pour l'historisation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"gs://{BUCKET_NAME}/1_raw_zone/spark_status_{timestamp}"
        
        # 3. Écriture via Spark
        df.write.mode("overwrite").json(output_path)
        
        print(f"--- [DEBUG] Ingestion Spark réussie vers {output_path} ---")

    except Exception as e:
        print(f"--- [DEBUG] ERREUR : {str(e)} ---")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()