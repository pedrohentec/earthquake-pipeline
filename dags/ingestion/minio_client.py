import boto3
from botocore.client import Config
from pathlib import Path
from datetime import datetime, timezone


MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "earthquake-raw-data"


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def upload_to_minio(local_filepath: str) -> str:
    client = get_minio_client()
    path = Path(local_filepath)

    now = datetime.now(tz=timezone.utc)
    object_key = (
        f"earthquakes/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"{path.name}"
    )

    client.upload_file(str(path), BUCKET_NAME, object_key)

    return f"s3://{BUCKET_NAME}/{object_key}"


if __name__ == "__main__":
    import glob
    files = glob.glob("data/raw/**/*.parquet", recursive=True)
    if files:
        result = upload_to_minio(files[0])
        print(f"Uploaded: {result}")
    else:
        print("No parquet files found locally")