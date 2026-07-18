{{ config(materialized='table') }}

SELECT
    id,
    magnitude,
    magnitude_class,
    place,
    time_utc,
    depth_km,
    depth_class,
    latitude,
    longitude,
    alert,
    url
FROM {{ ref('silver_earthquakes_unified') }}
WHERE magnitude >= 5.0
ORDER BY magnitude DESC, time_utc DESC