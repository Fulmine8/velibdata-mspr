import json
import urllib.request
from datetime import datetime
from google.cloud import storage
import functions_framework

@functions_framework.cloud_event
def fetch_velib_data(cloud_event):
    API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/exports/json"
    
    # IMPORTANT : Vérifiez le nom de votre bucket
    BUCKET_NAME = "velibdata-datalake-mspr" 
    FOLDER = "1_raw_zone/"

    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{FOLDER}station_status_{timestamp}.json"

        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        # --- LA MODIFICATION EST ICI (Création du format NDJSON) ---
        # On transforme le tableau en lignes indépendantes
        ndjson_data = "\n".join([json.dumps(record) for record in data])
        
        blob.upload_from_string(ndjson_data, content_type='application/json')
        # -----------------------------------------------------------

        print(f"Succès : Le fichier {filename} a été enregistré au format NDJSON.")
        
    except Exception as e:
        print(f"Erreur lors de l'ingestion : {e}")