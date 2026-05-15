"""
Module pour l'ingestion des données Vélib' en temps réel vers Google Cloud Storage.
Ce script est conçu pour être exécuté comme une Google Cloud Function (v2).
Il récupère les données de l'API Open Data Paris, les transforme en format NDJSON
et les stocke dans un bucket de la zone 'raw' du Data Lake.
"""

import json
import urllib.request
from datetime import datetime
from google.cloud import storage
import functions_framework

@functions_framework.cloud_event
def fetch_velib_data(cloud_event):
    """
    Fonction déclenchée par un Cloud Event (ex: Cloud Scheduler via Pub/Sub) 
    pour récupérer et stocker les données de disponibilité Vélib'.
    
    Args:
        cloud_event: L'événement qui a déclenché la fonction.
    """
    # URL de l'API Open Data Paris pour les disponibilités Vélib' en temps réel (format JSON)
    API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/exports/json"
    
    # Configuration du stockage Cloud Storage
    # IMPORTANT : Assurez-vous que ce bucket existe dans votre projet GCP
    BUCKET_NAME = "velibdata-datalake-mspr" 
    FOLDER = "1_raw_zone/"

    try:
        # Configuration de la requête avec un User-Agent pour éviter d'être bloqué
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        
        # Récupération des données depuis l'API
        print(f"Récupération des données depuis {API_URL}...")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        # Génération d'un horodatage pour le nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{FOLDER}station_status_{timestamp}.json"

        # Initialisation du client Storage et accès au bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        # Transformation des données au format NDJSON (Newline Delimited JSON)
        # Ce format est optimal pour l'ingestion dans BigQuery par la suite.
        # On transforme le tableau JSON en chaînes de caractères séparées par des sauts de ligne.
        print("Transformation des données au format NDJSON...")
        ndjson_data = "\n".join([json.dumps(record) for record in data])
        
        # Upload des données vers GCS
        blob.upload_from_string(ndjson_data, content_type='application/json')

        print(f"Succès : Le fichier {filename} a été enregistré au format NDJSON dans le bucket {BUCKET_NAME}.")
        
    except Exception as e:
        # Capture et affichage des erreurs (visible dans Cloud Logging)
        print(f"Erreur lors de l'ingestion : {e}")