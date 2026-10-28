
import json
from datetime import UTC, datetime
from pathlib import Path

import requests

BASE_URL = "https://api.worldbank.org/v2/country"
COUNTRIES = ["NZL", "AUS", "USA"]
INDICATOR = "NY.GDP.MKTP.CD"
RAW_DIR = Path("data/raw/world_bank/gdp")


def fetch_gdp():
    """Fetch all available GDP observations for selected countries."""
    observations = []
    page = 1

    with requests.Session() as session:
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

            if not isinstance(payload, list) or len(payload) < 2:
                raise ValueError("Unexpected API response")

            metadata, records = payload

            if not isinstance(records, list):
                raise TypeError("Expected observation records to be a list")

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
