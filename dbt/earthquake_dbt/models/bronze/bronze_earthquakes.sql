{{ config(materialized='view') }}

SELECT
    id,
    magnitude,
    place,
    time_utc,
    updated_utc,
    url,
    alert,
    magnitude_type,
    depth_km,
    longitude,
    latitude,
    extracted_at
FROM read_parquet(
    'E:/PROJETOS/earthquake-pipeline/data/raw/**/*.parquet',
    hive_partitioning = true
)