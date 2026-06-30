from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ingestion.usgs_client import fetch_earthquakes, parse_earthquakes, save_local_parquet
from ingestion.minio_client import upload_to_minio


def ingest_earthquakes():
    print("Fetching earthquake data from USGS...")
    raw = fetch_earthquakes()
    df = parse_earthquakes(raw)
    print(f"{len(df)} events found")

    # Para salvar localmente
    filepath = save_local_parquet(df)
    print(f"Saved locally: {filepath}")

    # Uncomment when MinIO is configured:
    minio_path = upload_to_minio(filepath)
    print(f"Uploaded to MinIO: {minio_path}")

    return minio_path


default_args = {
    "owner": "pedrohentec",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="earthquake_pipeline",
    description="Fetches real-time earthquake data from USGS and stores as Parquet",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 6, 28),
    catchup=False,
    default_args=default_args,
    tags=["earthquake", "usgs", "ingestion"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest_earthquakes",
        python_callable=ingest_earthquakes,
    )