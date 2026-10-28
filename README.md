
# FinSight — Financial Data Engineering Platform

An end-to-end portfolio project demonstrating data ingestion,
warehouse engineering, analytics and AI-assisted insights.

## Current capabilities

- Ingest GDP observations from the World Bank Indicators API.
- Retrieve paginated API responses.
- Preserve raw observations as JSON.
- Record ingestion metadata in a manifest.
- Test raw data persistence using pytest.
- Check code quality using Ruff.

## Technology

- Python
- REST APIs
- Git and GitHub
- pytest and Ruff

## Data source

World Bank Indicators API:
https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation

Indicator: GDP (current US$), `NY.GDP.MKTP.CD`

Countries: New Zealand, Australia and the United States.

## Local setup

Create and activate a Python virtual environment, then install:

    python -m pip install -e ".[dev]"

Run the ingestion pipeline:

    python -m finsight.ingestion.world_bank

Run automated tests:

    python -m pytest -v

Run linting:

    ruff check .

## Roadmap

- [x] Initial API ingestion
- [x] Raw JSON persistence and manifest
- [x] Automated persistence test
- [ ] Snowflake landing layer
- [ ] dbt transformations and data quality
- [ ] Airflow orchestration
- [ ] AI analytics with hosted and local models
- [ ] Dashboard and CI/CD
