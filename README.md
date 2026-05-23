# Pipeline Data Engineering - Disponibilité Vélib' (MSPR)

## 📝 Description
Ce projet implémente une architecture Data Engineering distribuée de bout en bout sur Google Cloud Platform (GCP). Il a pour objectif l'ingestion, la transformation et la mise à disposition pour analyse des données en temps réel issues de l'API Open Data de la ville de Paris (disponibilité des stations Vélib').

## 🏗️ Architecture Technique
L'infrastructure s'articule autour de 4 piliers majeurs :

1. **Intégration Continue (CI/CD) :** `Cloud Build` écoute la branche principale de ce dépôt et déploie automatiquement les scripts vers Cloud Storage et la machine virtuelle (via tunnel IAP).
2. **Orchestration (IaaS) :** `Apache Airflow` hébergé sur une instance `Compute Engine` (via Docker Compose) coordonne séquentiellement l'ensemble du pipeline.
3. **Traitement Distribué (PaaS) :** Un cluster `Cloud Dataproc` exécute des jobs `PySpark` pour transformer la donnée brute (JSON) en format orienté colonne compressé (Parquet).
4. **Stockage & Data Warehouse :** - **1_raw_zone :** `Cloud Storage` (Stockage des données brutes API).
   - **2_trusted_zone :** `Cloud Storage` (Stockage des données nettoyées et typées).
   - **Data Warehouse :** `BigQuery` (Création et alimentation automatique de la table analytique).

## 📂 Arborescence du Dépôt

* **`cloudbuild.yaml`** : Configuration du pipeline CI/CD (Google Cloud Build).
* **`dags/`**
    * `velib_dataproc_dag.py` : DAG Airflow orchestrant les 4 étapes du pipeline.
    * `fetch_velib.py` : Script d'extraction locale de l'API Open Data.
* **`scripts/`**
    * `ingestion_pyspark.py` : Job Spark (Dépôt distribué dans la Raw Zone).
    * `transform_trusted_pyspark.py` : Job Spark (Nettoyage, typage et conversion Parquet).

## ⚙️ Flux de Données (ETL)
Le DAG Airflow `velib_dataproc_pipeline` exécute les tâches suivantes :

1. `fetch_api_data` : Interrogation de l'API et dépôt d'un fichier JSON technique (`api_dump.json`) sur GCS.
2. `run_pyspark_ingestion` : Inférence de schéma par Spark et historisation de la donnée brute dans un dossier horodaté.
3. `run_pyspark_trusted` : Lecture de la zone brute, déduplication, filtrage métier (stations physiquement installées) et écriture au format Parquet Snappy.
4. `load_trusted_to_bigquery` : Ingestion des fichiers Parquet vers BigQuery avec écrasement (TRUNCATE) pour mettre à jour le tableau de bord.

## 🚀 Déploiement
Toute modification poussée sur la branche principale déclenche l'exécution des instructions du fichier `cloudbuild.yaml` :
- Synchronisation des scripts Spark (`gsutil rsync`) vers le bucket Datalake.
- Copie sécurisée (SSH via IAP) des fichiers DAG vers le répertoire de la VM Airflow.