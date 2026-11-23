from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BRIEF_PATH = REPO_ROOT / "docs" / "00-project" / "brief.md"
SCOPE_PATH = REPO_ROOT / "docs" / "00-project" / "scope.md"
STAGE_NOTE_PATH = REPO_ROOT / "docs" / "02-stages" / "stage-00-definition.md"

def test_criterion_1_brief_exists():
    assert BRIEF_PATH.is_file(), f"Brief file not found at {BRIEF_PATH}"
    assert BRIEF_PATH.stat().st_size > 0, "Brief file is empty"

def test_criterion_2_source_dataset_citation_and_doi():
    content = BRIEF_PATH.read_text()
    assert "10.5281/zenodo.4743746" in content, "DOI missing in brief"
    assert "Stratosphere Laboratory" in content, "Publisher missing in brief"
    assert "Garcia, S." in content, "Author citation missing in brief"

def test_criterion_3_kaggle_dataset_a_slug():
    content = BRIEF_PATH.read_text()
    assert "harishragavender0209/iot-23-raw" in content, "Dataset A slug missing in brief"

def test_criterion_4_research_question():
    content = BRIEF_PATH.read_text()
    assert "Research Question" in content, "Research Question section missing in brief"
    assert "NIDS" in content, "NIDS context missing in brief"
    assert "scenario-partitioned" in content or "scenario-partitioned" in content.lower(), "Scenario-partitioning claim missing in brief"

def test_criterion_5_thirteen_stages_and_milestones():
    content = BRIEF_PATH.read_text()
    # Check all 13 stages 00 to 12
    for stage_num in range(13):
        stage_str = f"{stage_num:02d}"
        assert stage_str in content, f"Stage {stage_str} missing in brief"
    assert "M1 Foundation" in content
    assert "M2 Understanding" in content
    assert "M3 Transformation" in content
    assert "M4 Product" in content

def test_criterion_6_dataset_versioning_scheme():
    content = BRIEF_PATH.read_text()
    assert "harishragavender0209/iot23-prepared" in content, "Dataset B slug missing in brief"
    assert "V0" in content
    assert "V1" in content
    assert "V2" in content
    assert "V3" in content
    assert "V5" in content

def test_criterion_7_three_hard_invariants():
    content = BRIEF_PATH.read_text()
    assert "No balancing" in content or "no balancing" in content.lower(), "No balancing invariant missing in brief"
    assert "No scenario crosses a partition boundary" in content or "partition boundary" in content, "No scenario crossing invariant missing in brief"
    assert "Nothing fitted outside" in content or "fitted outside" in content, "Fit on train only invariant missing in brief"

def test_criterion_8_what_pipeline_does_not_do():
    content = BRIEF_PATH.read_text()
    assert "What This Pipeline Does Not Do" in content or "Non-goal" in content
    assert "Model training" in content
    assert "Inference" in content
    assert "Evaluation on external benchmarks" in content or "benchmarks" in content

def test_criterion_9_scope_exists_and_defers_items():
    assert SCOPE_PATH.is_file(), f"Scope file not found at {SCOPE_PATH}"
    content = SCOPE_PATH.read_text()
    assert "Deferred" in content, "Deferred section missing in scope"
    deferred_count = content.count("### D")
    assert deferred_count >= 3, f"Expected at least 3 deferred items, found {deferred_count}"

def test_criterion_10_stage_note_exists():
    assert STAGE_NOTE_PATH.is_file(), f"Stage note not found at {STAGE_NOTE_PATH}"
    content = STAGE_NOTE_PATH.read_text()
    assert "Stage 00" in content, "Stage 00 header missing in stage note"
    assert "What this stage does" in content or "What was produced" in content
