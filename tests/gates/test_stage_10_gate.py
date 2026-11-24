import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.storage import (
    get_canonical_parquet_schema,
    records_to_pyarrow_table,
    write_scenario_parquet,
    read_and_validate_parquet,
    write_storage_manifest,
    DEFAULT_COMPRESSION,
)
from iot23.profiling import parse_zeek_log_file

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "storage-report.md"
MANIFEST_PATH = REPO_ROOT / "docs" / "04-reports" / "storage-manifest.csv"
SAMPLE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample-capture" / "sample.log"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-10-storage.md"

def test_criterion_1_storage_report_and_manifest_exist():
    assert REPORT_PATH.is_file(), "storage-report.md missing"
    content = REPORT_PATH.read_text()
    assert "Stage 10 — Storage and Organisation Report" in content
    assert "Directory & Partition Hierarchy" in content
    assert "Snappy" in content

    assert MANIFEST_PATH.is_file(), "storage-manifest.csv missing"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 18
    for r in rows:
        assert r["compression"] == "SNAPPY"
        assert r["format"] == "parquet"
        assert int(r["row_count"]) > 0

def test_criterion_2_parquet_schema_definition():
    schema = get_canonical_parquet_schema()
    assert len(schema) == 39
    names = set(schema.names)
    assert "scenario_id" in names
    assert "ts" in names
    assert "uid" in names
    assert "id.orig_h" in names
    assert "id.resp_h" in names
    assert "proto_encoded" in names
    assert "duration_scaled" in names
    assert "label" in names
    assert "detailed-label" in names

def test_criterion_3_parquet_write_and_read_validation(tmp_path):
    assert SAMPLE_PATH.is_file()
    sample_records = parse_zeek_log_file(SAMPLE_PATH)
    assert len(sample_records) == 10

    # Add encoded and scaled dummy fields for testing
    for r in sample_records:
        r["proto_encoded"] = 1
        r["service_encoded"] = 0
        r["conn_state_encoded"] = 1
        r["history_encoded"] = 1
        r["duration_scaled"] = 0.5
        r["orig_bytes_scaled"] = 0.1
        r["resp_bytes_scaled"] = 0.2
        r["missed_bytes_scaled"] = 0.0
        r["orig_pkts_scaled"] = 1.0
        r["orig_ip_bytes_scaled"] = 1.0
        r["resp_pkts_scaled"] = 1.0
        r["resp_ip_bytes_scaled"] = 1.0
        r["duration_flag"] = "VALID"
        r["label_flag"] = "CONSISTENT"
        r["cleaning_status"] = "CLEANED"

    scenario_id = "CTU-IoT-Malware-Capture-1-1"
    output_path = write_scenario_parquet(sample_records, scenario_id, tmp_path)
    assert output_path.is_file()
    assert "partition=train" in str(output_path)
    assert f"scenario={scenario_id}" in str(output_path)

    # Re-open independently and validate
    val_info = read_and_validate_parquet(output_path)
    assert val_info["num_rows"] == 10
    assert val_info["num_columns"] == 39
    assert val_info["compression"] == "SNAPPY"
    assert val_info["serialized_size"] > 0

def test_criterion_4_storage_hierarchy_and_partition_disjointness():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    parts = {"train": 0, "val": 0, "test": 0}
    scenarios_seen = set()
    for r in rows:
        part = r["partition"]
        scen = r["scenario_id"]
        assert scen not in scenarios_seen, f"Duplicate scenario in manifest: {scen}"
        scenarios_seen.add(scen)
        parts[part] += 1
        assert r["file_path"].startswith(f"partition={part}/scenario={scen}/")

    assert parts["train"] == 10
    assert parts["val"] == 4
    assert parts["test"] == 4

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file(), "stage-10-storage.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 10" in content
    assert "Parquet" in content
    assert "Snappy" in content
    assert "39" in content
