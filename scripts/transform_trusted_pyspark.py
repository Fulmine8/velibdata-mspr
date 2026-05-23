from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    spark = SparkSession.builder.appName("Trusted_Zone_Processing").getOrCreate()
    BUCKET_NAME = "velibdata-datalake-mspr"
    
    try:
        input_path = f"gs://{BUCKET_NAME}/1_raw_zone/spark_status_*"
        df_raw = spark.read.json(input_path)
        
        df_trusted = df_raw.select(
            col("stationcode").cast("string").alias("station_code"),
            col("name").cast("string").alias("station_name"),
            col("capacity").cast("integer"),
            col("numbikesavailable").cast("integer").alias("bikes_available"),
            col("numdocksavailable").cast("integer").alias("docks_available"),
            col("is_installed").cast("string")
        )
        
        df_trusted = df_trusted.dropDuplicates(["station_code"]).dropna(subset=["station_code"])
        df_trusted = df_trusted.filter(col("is_installed") == "OUI")
        
        output_path = f"gs://{BUCKET_NAME}/2_trusted_zone/velib_cleaned.parquet"
        df_trusted.coalesce(1).write.mode("overwrite").parquet(output_path)
        
        print(f"--- [DEBUG] Succès : {df_trusted.count()} stations actives écrites ---")

    except Exception as e:
        print(f"--- [DEBUG] ERREUR : {str(e)} ---")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()