from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ingestion.usgs_client import fetch_earthquakes_usgs, parse_earthquakes_usgs, save_local_parquet_usgs
from ingestion.usp_client import fetch_earthquakes_usp, parse_earthquakes_usp, save_local_parquet_usp
from ingestion.minio_client import upload_to_minio


def ingest_usgs():
    print("Fetching earthquake data from USGS...")
    raw = fetch_earthquakes_usgs()
    df = parse_earthquakes_usgs(raw)
    print(f"{len(df)} events found")

    filepath = save_local_parquet_usgs(df)
    print(f"Saved locally: {filepath}")

    minio_path = upload_to_minio(str(filepath), prefix="earthquakes_usgs")
    print(f"Uploaded to MinIO: {minio_path}")

    return minio_path


def ingest_usp():
    print("Fetching earthquake data from USP/IAG...")
    raw = fetch_earthquakes_usp()
    df = parse_earthquakes_usp(raw)
    print(f"{len(df)} events found")

    filepath = save_local_parquet_usp(df)
    print(f"Saved locally: {filepath}")

    minio_path = upload_to_minio(str(filepath), prefix="earthquakes_usp")
    print(f"Uploaded to MinIO: {minio_path}")

    return minio_path


default_args = {
    "owner": "Pedro Henrique",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="earthquake_pipeline",
    description="Fetches real-time earthquake data from USGS and USP/IAG, stores as Parquet",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 6, 28),
    catchup=False,
    default_args=default_args,
    tags=["earthquake", "usgs", "usp", "ingestion"],
) as dag:

    ingest_usgs_task = PythonOperator(
        task_id="ingest_usgs",
        python_callable=ingest_usgs,
    )

    ingest_usp_task = PythonOperator(
        task_id="ingest_usp",
        python_callable=ingest_usp,
    )

    [ingest_usgs_task, ingest_usp_task]