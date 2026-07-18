{{ config(materialized='table') }}

WITH combined AS (
    SELECT * FROM {{ ref('bronze_earthquakes_usgs') }}
    UNION ALL
    SELECT * FROM {{ ref('bronze_earthquakes_usp') }}
),

cleaned AS (
    SELECT
        id,
        source,
        CAST(magnitude AS DOUBLE)                          AS magnitude,
        TRIM(place)                                        AS place,
        CAST(time_utc AS TIMESTAMP WITH TIME ZONE)         AS time_utc,
        CAST(updated_utc AS TIMESTAMP WITH TIME ZONE)      AS updated_utc,
        CAST(depth_km AS DOUBLE)                           AS depth_km,
        CAST(longitude AS DOUBLE)                          AS longitude,
        CAST(latitude AS DOUBLE)                           AS latitude,
        UPPER(COALESCE(magnitude_type, 'UNKNOWN'))         AS magnitude_type,
        LOWER(COALESCE(alert, 'none'))                     AS alert,
        url,
        CAST(extracted_at AS TIMESTAMP WITH TIME ZONE)     AS extracted_at,

        CASE
            WHEN magnitude < 2.0  THEN 'micro'
            WHEN magnitude < 4.0  THEN 'minor'
            WHEN magnitude < 5.0  THEN 'moderate'
            WHEN magnitude < 6.0  THEN 'strong'
            WHEN magnitude < 7.0  THEN 'major'
            ELSE 'great'
        END AS magnitude_class,

        CASE
            WHEN depth_km < 70   THEN 'shallow'
            WHEN depth_km < 300  THEN 'intermediate'
            ELSE 'deep'
        END AS depth_class,

        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY extracted_at DESC
        ) AS rn

    FROM combined
    WHERE magnitude IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
)

SELECT
    id, source, magnitude, place, time_utc, updated_utc, depth_km,
    longitude, latitude, magnitude_type, alert, url, extracted_at,
    magnitude_class, depth_class
FROM cleaned
WHERE rn = 1