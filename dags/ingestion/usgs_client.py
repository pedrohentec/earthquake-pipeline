import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
from pathlib import Path


USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def fetch_earthquakes() -> dict:
    response = requests.get(USGS_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_earthquakes(raw: dict) -> pd.DataFrame:
    features = raw.get("features", [])

    records = []
    for feature in features:
        props = feature["properties"]
        geo = feature["geometry"]
        records.append({
            "id": feature["id"],
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time_utc": datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc),
            "updated_utc": datetime.fromtimestamp(props["updated"] / 1000, tz=timezone.utc),
            "url": props.get("url"),
            "alert": props.get("alert"),
            "magnitude_type": props.get("magType"),
            "depth_km": geo["coordinates"][2] if geo else None,
            "longitude": geo["coordinates"][0] if geo else None,
            "latitude": geo["coordinates"][1] if geo else None,
            "extracted_at": datetime.now(tz=timezone.utc),
        })

    return pd.DataFrame(records)


def save_local_parquet(df: pd.DataFrame, base_path: str = "data/raw") -> Path:
    now = datetime.now(tz=timezone.utc)
    partition = Path(base_path) / f"year={now.year}" / f"month={now.month:02d}" / f"day={now.day:02d}"
    partition.mkdir(parents=True, exist_ok=True)

    filename = f"earthquakes_{now.strftime('%Y%m%d_%H%M')}.parquet"
    filepath = partition / filename

    table = pa.Table.from_pandas(df)
    pq.write_table(table, filepath)

    return filepath


if __name__ == "__main__":
    print("Fetching data from USGS...")
    raw = fetch_earthquakes()
    df = parse_earthquakes(raw)
    print(f"{len(df)} events found")
    print(df[["magnitude", "place", "time_utc", "depth_km"]].head())

    path = save_local_parquet(df)
    print(f"Saved to: {path}")