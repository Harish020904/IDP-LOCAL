"""Inventory and capture manifest management for IoT-23 dataset."""
import csv
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "docs" / "04-reports" / "capture-manifest.csv"

def load_capture_manifest(manifest_path: Path = MANIFEST_PATH) -> List[Dict[str, Any]]:
    """Load and parse the capture manifest CSV."""
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Capture manifest not found at {manifest_path}")
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["size_bytes"] = int(row["size_bytes"])
            records.append(row)
    return records

def get_scenario_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics for the inventory."""
    total_files = len(records)
    total_bytes = sum(r["size_bytes"] for r in records)
    malicious_files = [r for r in records if r["capture_type"] == "malicious"]
    benign_files = [r for r in records if r["capture_type"] == "benign"]
    
    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "malicious_count": len(malicious_files),
        "benign_count": len(benign_files),
        "malicious_bytes": sum(r["size_bytes"] for r in malicious_files),
        "benign_bytes": sum(r["size_bytes"] for r in benign_files),
    }

def get_file_scenario_map(records: List[Dict[str, Any]]) -> Dict[str, str]:
    """Map filename to scenario ID."""
    return {r["file_name"]: r["scenario_id"] for r in records}
