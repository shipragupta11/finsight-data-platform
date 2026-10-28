
import json
from datetime import UTC, datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.worldbank.org/v2/country"
COUNTRIES = ["NZL", "AUS", "USA"]
INDICATOR = "NY.GDP.MKTP.CD"
RAW_DIR = Path("data/raw/world_bank/gdp")

def create_session():
    """Create an HTTP session with retries for transient failures."""
    retry_strategy = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def validate_api_response(payload):
    """Validate the structure of a World Bank API response."""
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Unexpected API response")

    metadata, records = payload

    if not isinstance(metadata, dict):
        raise TypeError("Expected pagination metadata to be a dictionary")

    if not isinstance(records, list):
        raise TypeError("Expected observation records to be a list")

    try:
        pages = int(metadata["pages"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid pagination metadata: missing or invalid pages") from exc

    if pages < 1:
        raise ValueError("Invalid pagination metadata: pages must be at least 1")

    for record in records:
        if not isinstance(record, dict):
            raise TypeError("Expected each observation to be a dictionary")

        if "country" not in record or "date" not in record or "value" not in record:
            raise ValueError("Observation is missing required fields")

    return metadata, records


def fetch_gdp():
    """Fetch all available GDP observations for selected countries."""
    observations = []
    page = 1

    with create_session() as session:
        while True:
            url = (
                f"{BASE_URL}/"
                f"{';'.join(COUNTRIES)}"
                f"/indicator/{INDICATOR}"
            )

            response = session.get(
                url,
                params={
                    "format": "json",
                    "per_page": 1000,
                    "page": page,
                },
                timeout=30,
            )
            response.raise_for_status()

            payload = response.json()
            metadata, records = validate_api_response(payload)

            observations.extend(records)

            if page >= int(metadata["pages"]):
                break

            page += 1

    return observations


def save_raw(observations, output_dir=RAW_DIR):
    """Save raw observations and ingestion metadata."""
    timestamp = datetime.now(UTC)
    batch_id = timestamp.strftime("%Y%m%dT%H%M%SZ")

    batch_dir = output_dir / f"ingested_at={batch_id}"
    batch_dir.mkdir(parents=True, exist_ok=False)

    data_path = batch_dir / "data.json"
    data_path.write_text(
        json.dumps(observations, indent=2),
        encoding="utf-8",
    )

    manifest = {
        "source": "World Bank Indicators API",
        "indicator": INDICATOR,
        "countries": COUNTRIES,
        "ingested_at_utc": timestamp.isoformat(),
        "record_count": len(observations),
        "data_file": "data.json",
    }

    (batch_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return data_path


def main():
    records = fetch_gdp()
    path = save_raw(records)

    print(f"Records fetched: {len(records)}")
    print(f"Raw data saved: {path}")


if __name__ == "__main__":
    main()
