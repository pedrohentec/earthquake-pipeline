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
    extracted_at,
    source
FROM read_parquet(
    '{{ var("raw_data_path") }}/raw_usgs/**/*.parquet',
    hive_partitioning = true,
    union_by_name = true
)