import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO


USP_URL = "https://www.moho.iag.usp.br/fdsnws/event/1/query"


def fetch_earthquakes_usp(limit: int = 100) -> str:
    params = {
        "format": "text",
        "minmagnitude": 0,
        "limit": limit,
    }
    response = requests.get(USP_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.text


def parse_earthquakes_usp(raw_text: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(raw_text), sep="|")
    df.columns = [c.strip().lstrip("#") for c in df.columns]

    parsed = pd.DataFrame({
        "id": df["EventID"],
        "magnitude": pd.to_numeric(df["Magnitude"], errors="coerce"),
        "place": df["EventLocationName"],
        "time_utc": pd.to_datetime(df["Time"], utc=True, errors="coerce"),
        "updated_utc": pd.to_datetime(df["Time"], utc=True, errors="coerce"),
        "url": None,
        "alert": None,
        "magnitude_type": df["MagType"],
        "depth_km": pd.to_numeric(df["Depth/km"], errors="coerce"),
        "longitude": pd.to_numeric(df["Longitude"], errors="coerce"),
        "latitude": pd.to_numeric(df["Latitude"], errors="coerce"),
        "extracted_at": datetime.now(tz=timezone.utc),
        "source": "USP",
    })

    return parsed


def save_local_parquet_usp(df: pd.DataFrame, base_path: str = "data/raw_usp") -> Path:
    now = datetime.now(tz=timezone.utc)
    partition = Path(base_path) / f"year={now.year}" / f"month={now.month:02d}" / f"day={now.day:02d}"
    partition.mkdir(parents=True, exist_ok=True)

    filename = f"earthquakes_usp_{now.strftime('%Y%m%d_%H%M')}.parquet"
    filepath = partition / filename

    table = pa.Table.from_pandas(df)
    pq.write_table(table, filepath)

    return filepath


if __name__ == "__main__":
    print("Fetching earthquake data from USP/IAG...")
    raw = fetch_earthquakes_usp()
    df = parse_earthquakes_usp(raw)
    print(f"{len(df)} events found")
    print(df[["magnitude", "place", "time_utc", "depth_km"]].head(10))

    path = save_local_parquet_usp(df)
    print(f"Saved locally: {path}")