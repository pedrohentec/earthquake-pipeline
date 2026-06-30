{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('day', time_utc)     AS event_date,
    magnitude_class,
    depth_class,
    COUNT(*)                        AS total_events,
    ROUND(AVG(magnitude), 2)        AS avg_magnitude,
    ROUND(MAX(magnitude), 2)        AS max_magnitude,
    ROUND(AVG(depth_km), 2)         AS avg_depth_km
FROM {{ ref('silver_earthquakes') }}
GROUP BY 1, 2, 3
ORDER BY 1 DESC