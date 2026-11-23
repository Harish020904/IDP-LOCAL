import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.quality import (
    is_valid_port,
    has_negative_duration,
    is_valid_timestamp,
    is_consistent_label_pair,
    find_duplicate_uids,
    audit_flow_records,
)
from iot23.profiling import parse_zeek_log_file

AUDIT_PATH = REPO_ROOT / "docs" / "04-reports" / "data-quality-audit.md"
ISSUES_CSV = REPO_ROOT / "docs" / "04-reports" / "quality-issues.csv"
SAMPLE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample-capture" / "sample.log"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-05-quality.md"

def test_criterion_1_audit_report_exists_and_detailed():
    assert AUDIT_PATH.is_file(), "data-quality-audit.md missing"
    content = AUDIT_PATH.read_text()
    assert "Audit Scope & Methodology" in content
    assert "Findings by Problem Category" in content
    assert "Preparation Decisions for Stage 06 Cleaning" in content
    assert "Do NOT blanket fill with zero" in content

def test_criterion_2_quality_issues_registry():
    assert ISSUES_CSV.is_file(), "quality-issues.csv missing"
    with open(ISSUES_CSV, "r") as f:
        issues = list(csv.DictReader(f))
    assert len(issues) >= 5
    for iss in issues:
        assert "issue_id" in iss
        assert "check_name" in iss
        assert "severity" in iss
        assert "handling_decision" in iss

def test_criterion_3_programmatic_quality_checks():
    # Port validation
    assert is_valid_port(80) is True
    assert is_valid_port("443") is True
    assert is_valid_port("-") is True
    assert is_valid_port(-1) is False
    assert is_valid_port(70000) is False
    assert is_valid_port("invalid") is False

    # Duration validation
    assert has_negative_duration(0.0) is False
    assert has_negative_duration("1.25") is False
    assert has_negative_duration("-") is False
    assert has_negative_duration(-0.01) is True
    assert has_negative_duration("-1.5") is True

    # Timestamp validation
    assert is_valid_timestamp(1525878532.0) is True
    assert is_valid_timestamp("1525878532.0") is True
    assert is_valid_timestamp(0) is False
    assert is_valid_timestamp("-") is False

    # Label consistency
    assert is_consistent_label_pair("Benign", "-") is True
    assert is_consistent_label_pair("Malicious", "PartOfAHorizontalPortScan") is True
    assert is_consistent_label_pair("Benign", "DDoS") is False
    assert is_consistent_label_pair("Benign", "PartOfAHorizontalPortScan") is False

def test_criterion_4_audit_sample_records():
    assert SAMPLE_PATH.is_file()
    records = parse_zeek_log_file(SAMPLE_PATH)
    results = audit_flow_records(records)
    assert results["total_records"] == 10
    assert results["invalid_ports_count"] == 0
    assert results["negative_durations_count"] == 0
    assert results["label_inconsistencies_count"] == 0
    assert results["duplicate_uids_count"] == 0

    # Inject deliberate defects to ensure detector triggers
    corrupted = [
        {"id.orig_p": 99999, "duration": "-0.5", "ts": "0", "label": "Benign", "detailed-label": "DDoS", "uid": "DUP1"},
        {"id.orig_p": 80, "duration": "1.0", "ts": "100", "label": "Benign", "detailed-label": "-", "uid": "DUP1"},
    ]
    corrupted_results = audit_flow_records(corrupted)
    assert corrupted_results["invalid_ports_count"] == 1
    assert corrupted_results["negative_durations_count"] == 1
    assert corrupted_results["malformed_timestamps_count"] == 1
    assert corrupted_results["label_inconsistencies_count"] == 1
    assert corrupted_results["duplicate_uids_count"] == 1

def test_criterion_5_stage_note_exists_and_closes_m2():
    assert STAGE_NOTE_PATH.is_file()
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 05" in content
    assert "Milestone 2 Completion Summary" in content
    assert "v2-audited" in content
