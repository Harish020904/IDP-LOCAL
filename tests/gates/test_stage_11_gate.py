from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.reproducibility import (
    compute_file_sha256,
    verify_checksum_registry,
    audit_all_invariants,
)

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "reproducibility-report.md"
CHECKSUMS_PATH = REPO_ROOT / "docs" / "04-reports" / "prepared-checksums.sha256"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-11-reproducibility.md"

def test_criterion_1_reproducibility_report_and_checksums_exist():
    assert REPORT_PATH.is_file(), "reproducibility-report.md missing"
    content = REPORT_PATH.read_text()
    assert "Stage 11 — Data Integrity and Reproducibility Report" in content
    assert "Invariant Compliance Audit Matrix" in content
    assert "Cryptographic Artifact Registry" in content

    assert CHECKSUMS_PATH.is_file(), "prepared-checksums.sha256 missing"
    lines = [line.strip() for line in CHECKSUMS_PATH.read_text().splitlines() if line.strip() and not line.startswith("#")]
    assert len(lines) >= 20

def test_criterion_2_checksum_verification_function():
    results = verify_checksum_registry(CHECKSUMS_PATH)
    assert len(results) >= 20
    # Every verified file should have a passing checksum
    for fname, is_valid in results.items():
        assert is_valid is True, f"Checksum verification failed for {fname}"

def test_criterion_3_programmatic_invariant_audit():
    audit_results = audit_all_invariants(REPO_ROOT)
    assert audit_results["all_invariants_passed"] is True
    assert audit_results["invariant_1_raw_readonly"] is True
    assert audit_results["invariant_2_label_preservation"] is True
    assert audit_results["invariant_3_no_balancing"] is True
    assert audit_results["invariant_4_scenario_disjointness"] is True
    assert audit_results["invariant_5_fit_on_train_only"] is True
    assert audit_results["invariant_6_attributable_removals"] is True

def test_criterion_4_end_to_end_reconciliation_identity():
    # End-to-end reconciliation across all pipeline deliverables
    import csv
    manifest_path = REPO_ROOT / "docs" / "04-reports" / "partition-manifest.csv"
    storage_path = REPO_ROOT / "docs" / "04-reports" / "storage-manifest.csv"
    cleaning_path = REPO_ROOT / "docs" / "04-reports" / "cleaning-log.csv"

    with open(manifest_path, "r", encoding="utf-8") as f:
        part_rows = list(csv.DictReader(f))
    with open(storage_path, "r", encoding="utf-8") as f:
        store_rows = list(csv.DictReader(f))
    with open(cleaning_path, "r", encoding="utf-8") as f:
        clean_ops = list(csv.DictReader(f))

    assert len(part_rows) == 18
    assert len(store_rows) == 18

    # Scenario IDs must match 1:1 between partitioning and storage
    part_scens = {r["scenario_id"] for r in part_rows}
    store_scens = {r["scenario_id"] for r in store_rows}
    assert part_scens == store_scens

    # Cleaning operations must account for all examined rows
    for op in clean_ops:
        assert int(op["records_examined"]) == 325307816

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file(), "stage-11-reproducibility.md missing"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 11" in content
    assert "Invariants Programmatically Audited" in content
    assert "SHA-256" in content
    assert "EXACT MATCH" in content
