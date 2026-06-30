# Earthquake Pipeline

Real-time data engineering pipeline for global earthquake monitoring.

## Stack

- **Ingestion**: Python + USGS Earthquake API
- **Orchestration**: Apache Airflow 3
- **Storage**: Google Cloud Storage (Parquet partitioned by date)
- **Data Warehouse**: BigQuery
- **Transformation**: dbt (bronze/silver/gold layers)
- **Dashboard**: Looker Studio
- **Infra**: Docker + Docker Compose

## Architecture

```
USGS API → Python → Airflow → GCS → dbt → BigQuery → Looker Studio
```

## Project Structure

```
earthquake-pipeline/
├── dags/
│   └── ingestion/
│       └── usgs_client.py   # USGS API client
├── dbt/
│   └── models/
│       ├── bronze/
│       ├── silver/
│       └── gold/
├── config/                  # GCP credentials (not versioned)
└── docker-compose.yml
```

## Progress

- [x] Phase 1 — Environment (Docker + Airflow 3)
- [x] Phase 2 — Local ingestion (USGS API + Parquet)
- [x] Phase 3 — Orchestration with Airflow
- [ ] Phase 4 — dbt + BigQuery
- [ ] Phase 5 — Looker Studio