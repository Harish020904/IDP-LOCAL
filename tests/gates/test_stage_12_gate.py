import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.imbalance import (
    PARTITION_CLASS_DATA,
    verify_no_balancing,
    compute_imbalance_metrics,
)

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "class-imbalance-report.md"
PARTITION_CSV = REPO_ROOT / "docs" / "04-reports" / "partition-imbalance.csv"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-12-imbalance.md"

def test_criterion_1_imbalance_report_and_csv_exist():
    assert REPORT_PATH.is_file(), "class-imbalance-report.md missing"
    content = REPORT_PATH.read_text()
    assert "Stage 12 — Class Imbalance Report" in content
    assert "Invariant 3" in content
    assert "17,916 : 1" in content

    assert PARTITION_CSV.is_file(), "partition-imbalance.csv missing"
    with open(PARTITION_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 12
    labels = {r["label"] for r in rows}
    assert "PartOfAHorizontalPortScan" in labels
    assert "Benign" in labels
    assert "Torii" in labels
    assert "Okiru" in labels

def test_criterion_2_invariant_3_no_balancing_guard():
    # Invariant 3: Stage 12 must not alter row counts
    stage11_counts = 325307816
    final_counts = 325307816
    assert verify_no_balancing(stage11_counts, final_counts) is True
    assert verify_no_balancing(stage11_counts, 300000000) is False
    assert verify_no_balancing(stage11_counts, 350000000) is False

def test_criterion_3_imbalance_metrics_and_ratios():
    metrics = compute_imbalance_metrics(PARTITION_CLASS_DATA)
    assert metrics["imbalance_ratio"] > 1000
    assert metrics["max_class"] == "PartOfAHorizontalPortScan"
    assert metrics["min_class"] == "Hide and Seek"
    assert metrics["single_scenario_classes_count"] == 9
    assert metrics["attack_percentage"] > 80.0
    assert metrics["benign_percentage"] < 20.0

def test_criterion_4_partition_distribution_integrity():
    with open(PARTITION_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    benign_row = next(r for r in rows if r["label"] == "Benign")
    assert int(benign_row["train_count"]) > 0
    assert int(benign_row["val_count"]) > 0
    assert int(benign_row["test_count"]) > 0

    # Single scenario labels must have counts in exactly one partition
    single_rows = [r for r in rows if int(r["scenarios"]) == 1]
    assert len(single_rows) == 9
    for r in single_rows:
        non_zero_partitions = sum(1 for p in ["train_count", "val_count", "test_count"] if int(r[p]) > 0)
        assert non_zero_partitions == 1, f"Single-scenario label {r['label']} leaked across partitions!"

def test_criterion_5_stage_note_exists_and_closes_pipeline():
    assert STAGE_NOTE_PATH.is_file(), "stage-12-imbalance.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 12" in content
    assert "Invariant 3" in content
    assert "17,916 : 1" in content
    assert "Pipeline Completion" in content
    assert "v5-validated" in content
