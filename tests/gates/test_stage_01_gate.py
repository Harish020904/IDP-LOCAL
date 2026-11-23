from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.integrity import (
    RAW_FILE_SIZES,
    TOTAL_RAW_BYTES,
    TOTAL_RAW_FILES,
    verify_file_size,
    DATASET_A_SLUG,
    DOI,
)

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "source-integrity.md"
CHECKSUMS_PATH = REPO_ROOT / "docs" / "04-reports" / "raw-checksums.sha256"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-01-acquisition.md"

def test_criterion_1_source_integrity_report_content():
    assert REPORT_PATH.is_file(), "source-integrity.md missing"
    content = REPORT_PATH.read_text()
    assert DOI in content, f"DOI {DOI} missing in report"
    assert DATASET_A_SLUG in content, f"Slug {DATASET_A_SLUG} missing in report"
    assert "18 labeled files" in content

def test_criterion_2_raw_checksums_registry():
    assert CHECKSUMS_PATH.is_file(), "raw-checksums.sha256 missing"
    lines = [
        line.strip()
        for line in CHECKSUMS_PATH.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert len(lines) == 18, f"Expected 18 registry entries, got {len(lines)}"
    for line in lines:
        parts = line.split()
        assert len(parts) == 2, f"Invalid format in registry: {line}"
        size, filename = int(parts[0]), parts[1]
        assert filename in RAW_FILE_SIZES
        assert RAW_FILE_SIZES[filename] == size

def test_criterion_3_integrity_module_totals():
    assert TOTAL_RAW_FILES == 18
    assert TOTAL_RAW_BYTES == 44311939884
    # Test valid and invalid file verification
    assert verify_file_size("10.labeled", 1340179107) is True
    assert verify_file_size("10.labeled", 999) is False
    with pytest.raises(ValueError):
        verify_file_size("non_existent_file.labeled", 100)

def test_criterion_4_stage_note_exists_and_accurate():
    assert STAGE_NOTE_PATH.is_file()
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 01" in content
    assert "44,311,939,884 bytes" in content
    assert "18" in content

def test_criterion_5_invariant_1_raw_immutable_enforced():
    content = REPORT_PATH.read_text()
    assert "Invariant 1 Status" in content
    assert "VERIFIED" in content
    assert "read-only" in content.lower()
