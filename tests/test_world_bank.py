
import json

from finsight.ingestion.world_bank import save_raw


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
