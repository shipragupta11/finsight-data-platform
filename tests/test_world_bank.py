
import json

import pytest

from finsight.ingestion.world_bank import (
    create_session,
    save_raw,
    validate_api_response,
)


def test_validate_api_response_accepts_valid_payload():
    payload = [
        {"pages": 1},
        [{"country": {"id": "NZ"}, "date": "2023", "value": 100}],
    ]

    metadata, records = validate_api_response(payload)

    assert metadata["pages"] == 1
    assert len(records) == 1


def test_validate_api_response_rejects_invalid_pages():
    payload = [{"pages": "invalid"}, []]

    with pytest.raises(ValueError, match="Invalid pagination metadata"):
        validate_api_response(payload)


def test_validate_api_response_rejects_missing_observation_fields():
    payload = [{"pages": 1}, [{"country": {"id": "NZ"}}]]

    with pytest.raises(ValueError, match="missing required fields"):
        validate_api_response(payload)


def test_create_session_configures_retries():
    session = create_session()

    try:
        adapter = session.get_adapter("https://")
        retries = adapter.max_retries

        assert retries.total == 4
        assert retries.connect == 4
        assert retries.read == 4
        assert retries.status == 4
        assert 429 in retries.status_forcelist
        assert 503 in retries.status_forcelist
        assert retries.allowed_methods == ["GET"]
    finally:
        session.close()

def test_save_raw_creates_data_and_manifest(tmp_path):
    records = [
        {
            "country": {"id": "NZ"},
            "date": "2023",
            "value": 100,
        }
    ]

    data_path = save_raw(records, output_dir=tmp_path)

    assert data_path.exists()
    assert json.loads(data_path.read_text(encoding="utf-8")) == records

    manifest_path = data_path.parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["record_count"] == 1
    assert manifest["indicator"] == "NY.GDP.MKTP.CD"
    assert manifest["data_file"] == "data.json"
