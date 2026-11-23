import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.schema import CANONICAL_FIELDS
from iot23.features import (
    COLUMN_ROLES,
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
    METADATA_COLUMNS,
    LEAKAGE_VECTORS,
    get_column_role,
    validate_all_canonical_columns_governed,
    separate_features_and_targets,
)

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "feature-governance-report.md"
ROLES_CSV = REPO_ROOT / "docs" / "04-reports" / "feature-roles.csv"
LEAKAGE_CSV = REPO_ROOT / "docs" / "04-reports" / "leakage-register.csv"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-07-features.md"

def test_criterion_1_feature_governance_report_and_roles_exist():
    assert REPORT_PATH.is_file(), "feature-governance-report.md missing"
    content = REPORT_PATH.read_text()
    assert "Feature Governance Report" in content
    assert "Column Roles Summary" in content
    assert "Traceability vs Leakage" in content

    assert ROLES_CSV.is_file(), "feature-roles.csv missing"
    with open(ROLES_CSV, "r", encoding="utf-8") as f:
        roles = list(csv.DictReader(f))
    assert len(roles) >= 23
    role_types = {r["role"] for r in roles}
    assert role_types == {"feature", "target", "metadata"}

def test_criterion_2_all_canonical_columns_governed():
    assert validate_all_canonical_columns_governed() is True
    for col in CANONICAL_FIELDS:
        assert col in COLUMN_ROLES
        assert get_column_role(col) in ["feature", "target", "metadata"]

def test_criterion_3_target_quarantine_from_features():
    assert "label" in TARGET_COLUMNS
    assert "detailed-label" in TARGET_COLUMNS
    assert "label" not in FEATURE_COLUMNS
    assert "detailed-label" not in FEATURE_COLUMNS

    sample_record = {
        "ts": "1525878532.0",
        "uid": "U1",
        "id.orig_h": "192.168.1.1",
        "id.orig_p": 80,
        "id.resp_h": "192.168.1.2",
        "id.resp_p": 443,
        "proto": "tcp",
        "label": "Malicious",
        "detailed-label": "DDoS",
    }
    feats, targets, meta = separate_features_and_targets(sample_record)
    assert "label" not in feats
    assert "detailed-label" not in feats
    assert targets["label"] == "Malicious"
    assert targets["detailed-label"] == "DDoS"
    assert feats["proto"] == "tcp"
    assert meta["id.orig_h"] == "192.168.1.1"

def test_criterion_4_ip_columns_retained_with_leakage_risk():
    # Non-negotiable rule: IP columns MUST NOT be dropped
    assert get_column_role("id.orig_h") == "metadata"
    assert get_column_role("id.resp_h") == "metadata"
    assert "id.orig_h" not in FEATURE_COLUMNS
    assert "id.resp_h" not in FEATURE_COLUMNS

    assert LEAKAGE_CSV.is_file(), "leakage-register.csv missing"
    with open(LEAKAGE_CSV, "r", encoding="utf-8") as f:
        leak_rows = list(csv.DictReader(f))
    leak_ids = {r["leakage_id"] for r in leak_rows}
    assert "LEAK01" in leak_ids
    assert "LEAK02" in leak_ids

    orig_leak = next(r for r in leak_rows if r["leakage_id"] == "LEAK01")
    assert "id.orig_h" in orig_leak["affected_columns"]
    assert "metadata" in orig_leak["mitigation_strategy"]
    assert "traceability" in orig_leak["mitigation_strategy"].lower()

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file(), "stage-07-features.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 07" in content
    assert "14" in content
    assert "Traceability Rule" in content
