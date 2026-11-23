from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.schema import (
    CANONICAL_FIELDS,
    TARGET_COLUMNS,
    METRIC_COLUMNS,
    IDENTIFIER_COLUMNS,
    ZEEK_SEPARATOR,
    ZEEK_UNSET_FIELD,
    validate_schema_fields,
    load_data_dictionary,
)

DICT_PATH = REPO_ROOT / "docs" / "04-reports" / "data-dictionary.csv"
REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "zeek-schema.md"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-03-schema.md"

def test_criterion_1_data_dictionary_completeness():
    assert DICT_PATH.is_file(), "data-dictionary.csv missing"
    rows = load_data_dictionary(DICT_PATH)
    assert len(rows) == 23, f"Expected 23 fields in data dictionary, found {len(rows)}"
    field_names = [r["field_name"] for r in rows]
    assert field_names == CANONICAL_FIELDS
    for r in rows:
        assert r["missing_representation"] == "-"
        assert len(r["description"]) > 5

def test_criterion_2_zeek_schema_report_content():
    assert REPORT_PATH.is_file(), "zeek-schema.md missing"
    content = REPORT_PATH.read_text()
    assert "23 Columns" in content
    assert "label" in content
    assert "detailed-label" in content
    assert "conn.log" in content

def test_criterion_3_schema_module_definitions():
    assert len(CANONICAL_FIELDS) == 23
    assert validate_schema_fields(CANONICAL_FIELDS) is True
    assert validate_schema_fields(CANONICAL_FIELDS[:-1]) is False
    assert validate_schema_fields(["wrong"] * 23) is False
    assert ZEEK_SEPARATOR == "\t"
    assert ZEEK_UNSET_FIELD == "-"
    assert "label" in TARGET_COLUMNS
    assert "detailed-label" in TARGET_COLUMNS
    assert "duration" in METRIC_COLUMNS
    assert "uid" in IDENTIFIER_COLUMNS

def test_criterion_4_invariant_2_label_preservation():
    content = REPORT_PATH.read_text()
    assert "Invariant 2" in content
    assert "never" in content.lower()
    assert "label" in TARGET_COLUMNS
    assert "detailed-label" in TARGET_COLUMNS

def test_criterion_5_stage_note_exists_and_closes_m1():
    assert STAGE_NOTE_PATH.is_file()
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 03" in content
    assert "Milestone 1 Completion Summary" in content
    assert "v1-inspected" in content
