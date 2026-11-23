import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.cleaning import (
    CLEANING_OPERATIONS,
    evaluate_record_for_cleaning,
    clean_flow_records,
    verify_reconciliation,
    generate_cleaning_log_rows,
)
from iot23.profiling import parse_zeek_log_file

CLEANING_REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "cleaning-report.md"
CLEANING_LOG_PATH = REPO_ROOT / "docs" / "04-reports" / "cleaning-log.csv"
SAMPLE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample-capture" / "sample.log"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-06-cleaning.md"

def test_criterion_1_cleaning_report_and_log_exist():
    assert CLEANING_REPORT_PATH.is_file(), "cleaning-report.md missing"
    report_text = CLEANING_REPORT_PATH.read_text()
    assert "Reconciliation Identity" in report_text
    assert "EXACT MATCH" in report_text
    assert "325,307,816" in report_text

    assert CLEANING_LOG_PATH.is_file(), "cleaning-log.csv missing"
    with open(CLEANING_LOG_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 8
    op_ids = {r["operation_number"] for r in rows}
    expected_ops = {f"OP{i:02d}" for i in range(1, 9)}
    assert expected_ops.issubset(op_ids)
    for r in rows:
        assert int(r["records_examined"]) > 0
        assert r["version"] == "V3"

def test_criterion_2_reconciliation_identity():
    # Mathematical identity check
    assert verify_reconciliation(100, 95, 5) is True
    assert verify_reconciliation(100, 90, 5) is False
    assert verify_reconciliation(325307816, 325307816, 0) is True

    # Real sample execution
    assert SAMPLE_PATH.is_file()
    sample_records = parse_zeek_log_file(SAMPLE_PATH)
    assert len(sample_records) == 10

    cleaned, quarantined, summary = clean_flow_records(sample_records)
    assert summary["total_raw"] == 10
    assert summary["total_cleaned"] == 10
    assert summary["total_quarantined"] == 0
    assert summary["reconciled"] is True
    assert summary["total_raw"] == summary["total_cleaned"] + summary["total_quarantined"]

def test_criterion_3_quarantine_rules_and_attributable_removals():
    # Construct synthetic batch with distinct violations
    test_batch = [
        # Normal record
        {"ts": "1525878532.0", "uid": "U1", "id.orig_p": "80", "id.resp_p": "443", "label": "Benign", "detailed-label": "-", "duration": "1.0"},
        # OP01: Truncated record (< 23 fields)
        {"ts": "1525878532.0", "uid": "U2", "label": "Benign"},
        # OP02: Malformed timestamp
        {"ts": "-1.0", "uid": "U3", "id.orig_p": "80", "id.resp_p": "443", "label": "Benign", "detailed-label": "-", "duration": "1.0"},
        # OP03: Invalid port
        {"ts": "1525878532.0", "uid": "U4", "id.orig_p": "70000", "id.resp_p": "443", "label": "Benign", "detailed-label": "-", "duration": "1.0"},
        # OP04: Missing label
        {"ts": "1525878532.0", "uid": "U5", "id.orig_p": "80", "id.resp_p": "443", "label": "-", "detailed-label": "-", "duration": "1.0"},
        # OP05: Negative duration (flagged, not quarantined)
        {"ts": "1525878532.0", "uid": "U6", "id.orig_p": "80", "id.resp_p": "443", "label": "Malicious", "detailed-label": "DDoS", "duration": "-0.5"},
        # OP06: Label inconsistency (flagged, not quarantined)
        {"ts": "1525878532.0", "uid": "U7", "id.orig_p": "80", "id.resp_p": "443", "label": "Benign", "detailed-label": "DDoS", "duration": "0.5"},
    ]

    # Fill default canonical fields so OP01 doesn't trigger on other records
    from iot23.schema import CANONICAL_FIELDS
    full_batch = []
    for r in test_batch:
        if r["uid"] == "U2":
            # Leave truncated
            full_batch.append(r)
        else:
            rec = {f: "-" for f in CANONICAL_FIELDS}
            rec.update(r)
            full_batch.append(rec)

    cleaned, quarantined, summary = clean_flow_records(full_batch)

    assert summary["total_raw"] == 7
    assert summary["total_quarantined"] == 4
    assert summary["total_cleaned"] == 3
    assert summary["reconciled"] is True

    # Validate quarantine attribution to operations
    q_ops = [q["quarantine_op"] for q in quarantined]
    assert "OP01" in q_ops
    assert "OP02" in q_ops
    assert "OP03" in q_ops
    assert "OP04" in q_ops

    # Validate flags on cleaned records
    cleaned_by_uid = {c["uid"]: c for c in cleaned}
    assert cleaned_by_uid["U1"]["duration_flag"] == "VALID"
    assert cleaned_by_uid["U1"]["label_flag"] == "CONSISTENT"

    assert cleaned_by_uid["U6"]["duration_flag"] == "NEGATIVE_DURATION"
    assert cleaned_by_uid["U7"]["label_flag"] == "INCONSISTENT_BENIGN_WITH_ATTACK_SUBLABEL"

def test_criterion_4_label_and_minority_preservation():
    # Invariant 2 & 3 checks
    record = {
        "ts": "1525878532.0",
        "uid": "U99",
        "id.orig_p": "80",
        "id.resp_p": "443",
        "label": "Benign",
        "detailed-label": "DDoS",
        "duration": "1.0",
        "orig_bytes": "-",
    }
    from iot23.schema import CANONICAL_FIELDS
    full_rec = {f: "-" for f in CANONICAL_FIELDS}
    full_rec.update(record)

    cleaned, quarantined = evaluate_record_for_cleaning(full_rec)
    assert quarantined is None
    assert cleaned is not None
    # Original labels MUST remain unchanged
    assert cleaned["label"] == "Benign"
    assert cleaned["detailed-label"] == "DDoS"
    # Unset token preserved (no blanket zero fill)
    assert cleaned["orig_bytes"] == "-"

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file(), "stage-06-cleaning.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 06" in content
    assert "325,307,816" in content
    assert "Reconciliation" in content
    assert "OP01" in content
