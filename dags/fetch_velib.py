import requests
import json
from google.cloud import storage

def fetch_data():
    # URL de l'API Open Data Paris pour les disponibilités Vélib'
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/exports/json"
    
    print("--- [DEBUG] Téléchargement des données de l'API Vélib' ---")
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    
    # Sauvegarde locale temporaire sur la VM Airflow
    local_path = "/tmp/api_dump.json"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    print("--- [DEBUG] Upload vers Google Cloud Storage ---")
    client = storage.Client(project="velibdata-mspr")
    bucket = client.bucket("velibdata-datalake-mspr")
    
    # Écrasement systématique du fichier technique api_dump.json
    blob = bucket.blob("1_raw_zone/api_dump.json")
    blob.upload_from_filename(local_path)
    
    print("--- [DEBUG] Extraction terminée avec succès ---")

if __name__ == "__main__":
    fetch_data()