# velibdata-mspr

Script d’ingestion des données Vélib’ en temps réel vers Google Cloud Storage.


## Équipe

Fulmine OKAN, Chaimae JEDDA, Ismail BENNINE, Geoffrey LECLUSE — EPSI
-----

## Description

`main.py` est une Google Cloud Function (v2) déclenchée toutes les minutes via Cloud Scheduler et Pub/Sub. Elle récupère les données de disponibilité des stations depuis l’API Open Data Paris, les convertit en format NDJSON et les stocke dans la zone `raw` du Data Lake (bucket GCS).

-----

## Structure

```
velibdata-mspr/
├── main.py            # Cloud Function — ingestion Vélib'
└── requirements.txt   # Dépendances Python
```

-----

## Prérequis

- Un projet Google Cloud Platform avec les APIs activées : Cloud Functions, Cloud Storage, Pub/Sub, Cloud Scheduler
- Un bucket GCS nommé `velibdata-datalake-mspr` avec un dossier `1_raw_zone/`
- Python 3.10+

-----

## Installation

```bash
git clone https://github.com/Fulmine8/velibdata-mspr.git
cd velibdata-mspr
pip install -r requirements.txt
```

-----

## Déploiement

```bash
gcloud functions deploy fetch_velib_data \
  --gen2 \
  --runtime=python310 \
  --region=europe-west9 \
  --source=. \
  --entry-point=fetch_velib_data \
  --trigger-topic=velib-trigger
```

-----

## Dépendances

```
functions-framework==3.*
google-cloud-storage
```

-----

## Données

- **Source** : API Open Data Paris — disponibilité Vélib’ en temps réel (format JSON)
- **Fréquence** : 1 appel par minute (~2M enregistrements/jour)
- **Format de sortie** : NDJSON
- **Destination** : `gs://velibdata-datalake-mspr/1_raw_zone/`
