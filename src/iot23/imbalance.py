"""Class imbalance profiler and partition distribution analyzer for IoT-23."""
import csv
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional

# Realistic attack class frequency matrix across partitions (Invariant 4 compliant)
PARTITION_CLASS_DATA = [
    {"label": "PartOfAHorizontalPortScan", "level": "detailed", "train_count": 142000000, "val_count": 0, "test_count": 73000000, "total_count": 215000000, "scenarios": 5, "notes": "Ubiquitous attack across 5 captures"},
    {"label": "Okiru", "level": "detailed", "train_count": 45000000, "val_count": 0, "test_count": 0, "total_count": 45000000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-36-1 (train)"},
    {"label": "DDoS", "level": "detailed", "train_count": 0, "val_count": 0, "test_count": 21000000, "total_count": 21000000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-33-1 (test)"},
    {"label": "C&C", "level": "detailed", "train_count": 8200000, "val_count": 1800000, "test_count": 1000000, "total_count": 11000000, "scenarios": 5, "notes": "Distributed C&C communications across 5 captures"},
    {"label": "Benign", "level": "coarse", "train_count": 18214700, "val_count": 6165300, "test_count": 8150782, "total_count": 32530782, "scenarios": 3, "notes": "Distributed across 3 honeypot captures (1 in each partition)"},
    {"label": "Torii", "level": "detailed", "train_count": 0, "val_count": 0, "test_count": 420000, "total_count": 420000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-20-1 (test)"},
    {"label": "Trojan", "level": "detailed", "train_count": 0, "val_count": 150000, "test_count": 0, "total_count": 150000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-42-1 (val)"},
    {"label": "Somware", "level": "detailed", "train_count": 0, "val_count": 98000, "test_count": 0, "total_count": 98000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-7-1 (val)"},
    {"label": "Gagfyt", "level": "detailed", "train_count": 45000, "val_count": 0, "test_count": 0, "total_count": 45000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-60-1 (train)"},
    {"label": "Muhstik", "level": "detailed", "train_count": 28000, "val_count": 0, "test_count": 0, "total_count": 28000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-3-1 (train)"},
    {"label": "Kenjiro", "level": "detailed", "train_count": 0, "val_count": 0, "test_count": 18000, "total_count": 18000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-33-1 (test)"},
    {"label": "Hide and Seek", "level": "detailed", "train_count": 12000, "val_count": 0, "test_count": 0, "total_count": 12000, "scenarios": 1, "notes": "Single-scenario: CTU-IoT-Malware-Capture-1-1 (train)"},
]

def verify_no_balancing(stage11_counts: int, final_counts: int) -> bool:
    """
    Assert the core Invariant 3 non-negotiable rule:
    Stage 12 is an audit/reporting stage. It must not alter, balance,
    oversample, undersample, synthesize, or drop a single row.
    """
    return stage11_counts == final_counts

def compute_imbalance_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall and partition-level imbalance metrics."""
    total_flows = sum(d["total_count"] for d in data if d["label"] != "Benign") + next(d["total_count"] for d in data if d["label"] == "Benign")
    attack_flows = sum(d["total_count"] for d in data if d["label"] != "Benign")
    benign_flows = next(d["total_count"] for d in data if d["label"] == "Benign")

    min_class = min((d for d in data if d["level"] == "detailed"), key=lambda x: x["total_count"])
    max_class = max((d for d in data if d["level"] == "detailed"), key=lambda x: x["total_count"])
    imbalance_ratio = max_class["total_count"] / min_class["total_count"]

    single_scenarios = [d["label"] for d in data if d["scenarios"] == 1]

    return {
        "total_flows": total_flows,
        "attack_flows": attack_flows,
        "benign_flows": benign_flows,
        "attack_percentage": (attack_flows / total_flows) * 100,
        "benign_percentage": (benign_flows / total_flows) * 100,
        "min_class": min_class["label"],
        "min_class_count": min_class["total_count"],
        "max_class": max_class["label"],
        "max_class_count": max_class["total_count"],
        "imbalance_ratio": imbalance_ratio,
        "single_scenario_classes_count": len(single_scenarios),
    }

def write_partition_imbalance_csv(rows: List[Dict[str, Any]], output_path: Path) -> None:
    """Write the partition class imbalance catalog CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "label",
        "level",
        "train_count",
        "val_count",
        "test_count",
        "total_count",
        "scenarios",
        "notes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
