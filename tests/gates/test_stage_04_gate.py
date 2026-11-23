import csv
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from iot23.profiling import parse_zeek_log_file, profile_dataset
from iot23.schema import CANONICAL_FIELDS

REPORT_PATH = REPO_ROOT / "docs" / "04-reports" / "raw-profiling-summary.md"
CLASS_CSV = REPO_ROOT / "docs" / "04-reports" / "class-distribution.csv"
SCENARIO_CSV = REPO_ROOT / "docs" / "04-reports" / "scenario-distribution.csv"
FIGURES_DIR = REPO_ROOT / "docs" / "04-reports" / "figures"
SAMPLE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample-capture" / "sample.log"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-04-profiling.md"

def test_criterion_1_profiling_report_exists():
    assert REPORT_PATH.is_file(), "raw-profiling-summary.md missing"
    content = REPORT_PATH.read_text()
    assert "Class Distribution Analysis" in content
    assert "Missing-Value Distribution" in content
    assert "Visualizations Generated" in content

def test_criterion_2_class_and_scenario_distribution_csvs():
    assert CLASS_CSV.is_file(), "class-distribution.csv missing"
    assert SCENARIO_CSV.is_file(), "scenario-distribution.csv missing"

    with open(CLASS_CSV, "r") as f:
        class_rows = list(csv.DictReader(f))
    assert len(class_rows) >= 2
    levels = {r["level"] for r in class_rows}
    assert "coarse" in levels
    assert "detailed" in levels

    with open(SCENARIO_CSV, "r") as f:
        scen_rows = list(csv.DictReader(f))
    assert len(scen_rows) == 18, f"Expected 18 scenarios, found {len(scen_rows)}"

def test_criterion_3_figures_generated_and_valid():
    assert FIGURES_DIR.is_dir(), "figures directory missing"
    png_files = list(FIGURES_DIR.glob("*.png"))
    assert len(png_files) >= 3, f"Expected at least 3 figures, found {len(png_files)}"
    for fig in png_files:
        assert fig.stat().st_size > 1000, f"Figure {fig.name} is suspiciously small"

def test_criterion_4_parser_and_profiling_logic():
    assert SAMPLE_PATH.is_file(), "sample.log missing"
    records = parse_zeek_log_file(SAMPLE_PATH)
    assert len(records) == 10
    for r in records:
        assert set(r.keys()) == set(CANONICAL_FIELDS)

    prof = profile_dataset(records)
    assert prof["total_records"] == 10
    assert "Malicious" in prof["label_counts"]
    assert "Benign" in prof["label_counts"]
    # Coarse label percentages must sum to 100%
    coarse_pct_sum = sum(prof["label_percentages"].values())
    assert pytest.approx(coarse_pct_sum, rel=1e-3) == 100.0

def test_criterion_5_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file()
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 04" in content
    assert "Key findings and numbers" in content
