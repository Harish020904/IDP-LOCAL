import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.preprocessing import (
    FitOnTrainPreprocessor,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    UNKNOWN_INDEX,
)
from iot23.profiling import parse_zeek_log_file

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "preprocessing-report.md"
PARAMS_CSV = REPO_ROOT / "docs" / "04-reports" / "preprocessing-params.csv"
SAMPLE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample-capture" / "sample.log"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-09-preprocessing.md"

def test_criterion_1_preprocessing_report_and_params_exist():
    assert REPORT_PATH.is_file(), "preprocessing-report.md missing"
    content = REPORT_PATH.read_text()
    assert "Stage 09 — Preprocessing Report" in content
    assert "Invariant 5" in content
    assert "Anti-Leakage Architecture" in content

    assert PARAMS_CSV.is_file(), "preprocessing-params.csv missing"
    with open(PARAMS_CSV, "r", encoding="utf-8") as f:
        params = list(csv.DictReader(f))
    assert len(params) >= 30
    param_names = {p["parameter_name"] for p in params}
    assert "duration_impute_median" in param_names
    assert "duration_scale_mean" in param_names
    assert "duration_scale_std" in param_names

def test_criterion_2_fit_source_is_strictly_train():
    with open(PARAMS_CSV, "r", encoding="utf-8") as f:
        params = list(csv.DictReader(f))
    for p in params:
        assert p["fit_source"] == "train", f"Leakage detected: parameter {p} fit_source != train"
        assert p["partition_learned"] == "train"

    # Enforce runtime guardrail: attempting to fit on val or test MUST fail
    assert SAMPLE_PATH.is_file()
    sample_records = parse_zeek_log_file(SAMPLE_PATH)
    prep = FitOnTrainPreprocessor()

    with pytest.raises(ValueError, match="Invariant 5 Violation"):
        prep.fit(sample_records, partition_name="val")

    with pytest.raises(ValueError, match="Invariant 5 Violation"):
        prep.fit(sample_records, partition_name="test")

def test_criterion_3_unseen_category_handling():
    sample_records = parse_zeek_log_file(SAMPLE_PATH)
    prep = FitOnTrainPreprocessor()
    prep.fit(sample_records, partition_name="train")

    # Construct test record with unseen categories
    unseen_record = {
        "id.orig_p": "80",
        "id.resp_p": "443",
        "duration": "1.0",
        "orig_bytes": "100",
        "resp_bytes": "200",
        "missed_bytes": "0",
        "orig_pkts": "1",
        "orig_ip_bytes": "40",
        "resp_pkts": "1",
        "resp_ip_bytes": "40",
        "proto": "unseen_protocol_xyz",
        "service": "unseen_service_abc",
        "conn_state": "UNSEEN_STATE",
        "history": "UNSEEN_HIST",
        "label": "Malicious",
        "detailed-label": "Torii",
    }

    transformed = prep.transform([unseen_record])
    assert len(transformed) == 1
    t = transformed[0]

    # Unseen categories must map gracefully to UNKNOWN_INDEX (0) without raising exception
    assert t["proto_encoded"] == UNKNOWN_INDEX
    assert t["service_encoded"] == UNKNOWN_INDEX
    assert t["conn_state_encoded"] == UNKNOWN_INDEX
    assert t["history_encoded"] == UNKNOWN_INDEX

def test_criterion_4_schema_consistency_across_partitions():
    sample_records = parse_zeek_log_file(SAMPLE_PATH)
    prep = FitOnTrainPreprocessor()
    prep.fit(sample_records, partition_name="train")

    # Transform two batches representing train and val/test
    batch_train = sample_records[:5]
    batch_val = sample_records[5:]

    trans_train = prep.transform(batch_train)
    trans_val = prep.transform(batch_val)

    assert len(trans_train) > 0
    assert len(trans_val) > 0

    train_keys = list(trans_train[0].keys())
    val_keys = list(trans_val[0].keys())
    assert train_keys == val_keys, "Schema mismatch across partitions!"

    # Ensure no NaN or None in scaled numerical fields
    for r in trans_train + trans_val:
        for col in NUMERICAL_FEATURES:
            scaled_val = r[f"{col}_scaled"]
            assert isinstance(scaled_val, (int, float))
            assert not (scaled_val != scaled_val) # check not NaN

def test_criterion_5_stage_note_exists_and_closes_m3():
    assert STAGE_NOTE_PATH.is_file(), "stage-09-preprocessing.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 09" in content
    assert "Invariant 5" in content
    assert "Milestone 3 Completion Summary" in content
    assert "34" in content
