from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.inventory import (
    load_capture_manifest,
    get_scenario_summary,
    get_file_scenario_map,
    MANIFEST_PATH,
)

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "raw-inventory.md"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-02-inventory.md"

def test_criterion_1_manifest_exists_and_valid():
    assert MANIFEST_PATH.is_file(), f"Manifest missing at {MANIFEST_PATH}"
    records = load_capture_manifest(MANIFEST_PATH)
    assert len(records) == 18, f"Expected 18 records, found {len(records)}"
    for r in records:
        assert "scenario_id" in r
        assert "file_name" in r
        assert "capture_type" in r
        assert r["capture_type"] in ("malicious", "benign")
        assert isinstance(r["size_bytes"], int)
        assert r["size_bytes"] > 0

def test_criterion_2_raw_inventory_report():
    assert REPORT_PATH.is_file(), "raw-inventory.md missing"
    content = REPORT_PATH.read_text()
    assert "44,311,939,884 bytes" in content
    assert "18" in content
    assert "CTU-IoT-Malware-Capture-8-1" in content
    assert "Mirai" in content

def test_criterion_3_inventory_summary_numbers():
    records = load_capture_manifest(MANIFEST_PATH)
    summary = get_scenario_summary(records)
    assert summary["total_files"] == 18
    assert summary["total_bytes"] == 44311939884
    assert summary["malicious_count"] == 15
    assert summary["benign_count"] == 3
    assert summary["benign_bytes"] == 261824

def test_criterion_4_scenario_mapping():
    records = load_capture_manifest(MANIFEST_PATH)
    mapping = get_file_scenario_map(records)
    assert mapping["conn.log.labeled"] == "CTU-IoT-Malware-Capture-1-1"
    assert mapping["8.labeled"] == "CTU-IoT-Malware-Capture-8-1"
    assert mapping["benign.labeled"] == "CTU-Honeypot-Capture-4-1"

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file()
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 02" in content
    assert "44,311,939,884" in content
