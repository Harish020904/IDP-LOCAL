"""Scenario-level data partitioning and label coverage engine for IoT-23."""
import csv
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple

# Deterministic scenario partitioning: Whole captures only (Invariant 4)
# 18 captures: 10 train (9 mal, 1 ben), 4 val (3 mal, 1 ben), 4 test (3 mal, 1 ben)
SCENARIO_PARTITIONS: Dict[str, str] = {
    # Train Partition (10 captures: 9 malicious, 1 benign)
    "CTU-IoT-Malware-Capture-1-1": "train",   # Hide and Seek botnet
    "CTU-IoT-Malware-Capture-3-1": "train",   # Muhstik botnet
    "CTU-IoT-Malware-Capture-48-1": "train",  # Mirai botnet
    "CTU-IoT-Malware-Capture-60-1": "train",  # Gagfyt botnet
    "CTU-IoT-Malware-Capture-8-1": "train",   # Mirai botnet
    "CTU-IoT-Malware-Capture-9-1": "train",   # Mirai botnet
    "CTU-IoT-Malware-Capture-52-1": "train",  # Mirai botnet
    "CTU-IoT-Malware-Capture-35-1": "train",  # Mirai botnet
    "CTU-IoT-Malware-Capture-36-1": "train",  # Okiru botnet
    "CTU-Honeypot-Capture-5-1": "train",      # Benign honeypot traffic
    
    # Validation Partition (4 captures: 3 malicious, 1 benign)
    "CTU-IoT-Malware-Capture-21-1": "val",    # Mirai botnet
    "CTU-IoT-Malware-Capture-42-1": "val",    # Trojan
    "CTU-IoT-Malware-Capture-7-1": "val",     # Somware botnet
    "CTU-Honeypot-Capture-4-1": "val",        # Benign normal traffic
    
    # Test Partition (4 captures: 3 malicious, 1 benign)
    "CTU-IoT-Malware-Capture-20-1": "test",   # Torii botnet
    "CTU-IoT-Malware-Capture-39-1": "test",   # IRec-Mirai botnet
    "CTU-IoT-Malware-Capture-33-1": "test",   # Kenjiro botnet
    "CTU-Honeypot-Capture-7-1": "test",       # Benign honeypot traffic
}

# Label scenario mapping: which scenario produces which labels
# Documented per Invariant 4 to highlight single-scenario labels
LABEL_SCENARIO_MAPPING: Dict[str, List[str]] = {
    "Benign": [
        "CTU-Honeypot-Capture-4-1",
        "CTU-Honeypot-Capture-5-1",
        "CTU-Honeypot-Capture-7-1",
    ],
    "Malicious": [
        "CTU-IoT-Malware-Capture-1-1",
        "CTU-IoT-Malware-Capture-3-1",
        "CTU-IoT-Malware-Capture-48-1",
        "CTU-IoT-Malware-Capture-60-1",
        "CTU-IoT-Malware-Capture-8-1",
        "CTU-IoT-Malware-Capture-9-1",
        "CTU-IoT-Malware-Capture-52-1",
        "CTU-IoT-Malware-Capture-35-1",
        "CTU-IoT-Malware-Capture-36-1",
        "CTU-IoT-Malware-Capture-21-1",
        "CTU-IoT-Malware-Capture-42-1",
        "CTU-IoT-Malware-Capture-7-1",
        "CTU-IoT-Malware-Capture-20-1",
        "CTU-IoT-Malware-Capture-39-1",
        "CTU-IoT-Malware-Capture-33-1",
    ],
    "PartOfAHorizontalPortScan": [
        "CTU-IoT-Malware-Capture-1-1",
        "CTU-IoT-Malware-Capture-48-1",
        "CTU-IoT-Malware-Capture-8-1",
        "CTU-IoT-Malware-Capture-9-1",
        "CTU-IoT-Malware-Capture-39-1",
    ],
    "Okiru": [
        "CTU-IoT-Malware-Capture-36-1",
    ],
    "DDoS": [
        "CTU-IoT-Malware-Capture-33-1",
    ],
    "C&C": [
        "CTU-IoT-Malware-Capture-1-1",
        "CTU-IoT-Malware-Capture-3-1",
        "CTU-IoT-Malware-Capture-20-1",
        "CTU-IoT-Malware-Capture-42-1",
        "CTU-IoT-Malware-Capture-7-1",
    ],
    "Torii": [
        "CTU-IoT-Malware-Capture-20-1",
    ],
    "Trojan": [
        "CTU-IoT-Malware-Capture-42-1",
    ],
    "Somware": [
        "CTU-IoT-Malware-Capture-7-1",
    ],
    "Gagfyt": [
        "CTU-IoT-Malware-Capture-60-1",
    ],
    "Muhstik": [
        "CTU-IoT-Malware-Capture-3-1",
    ],
    "Kenjiro": [
        "CTU-IoT-Malware-Capture-33-1",
    ],
    "Hide and Seek": [
        "CTU-IoT-Malware-Capture-1-1",
    ],
}

def get_scenario_partition(scenario_id: str) -> str:
    """Return the designated partition for a scenario ID."""
    if scenario_id not in SCENARIO_PARTITIONS:
        raise KeyError(f"Unknown scenario_id '{scenario_id}' not in partition registry.")
    return SCENARIO_PARTITIONS[scenario_id]

def validate_scenario_disjointness(partition_map: Dict[str, str]) -> bool:
    """
    Assert the core Invariant 4 requirement:
    No capture scenario crosses a partition boundary.
    Pairwise intersection of partition sets must be strictly empty.
    """
    partitions: Dict[str, Set[str]] = {"train": set(), "val": set(), "test": set()}
    for scen, part in partition_map.items():
        if part not in partitions:
            return False
        partitions[part].add(scen)

    for p1, p2 in combinations(partitions.keys(), 2):
        if partitions[p1] & partitions[p2] != set():
            return False

    return True

def get_partitions_summary(partition_map: Dict[str, str]) -> Dict[str, Any]:
    """Calculate partition counts and verification metrics."""
    counts = {"train": 0, "val": 0, "test": 0}
    for part in partition_map.values():
        if part in counts:
            counts[part] += 1

    disjoint = validate_scenario_disjointness(partition_map)
    total = len(partition_map)

    return {
        "total_scenarios": total,
        "train_scenarios": counts["train"],
        "val_scenarios": counts["val"],
        "test_scenarios": counts["test"],
        "is_disjoint": disjoint,
    }

def build_label_coverage_table() -> List[Dict[str, Any]]:
    """
    Generate label partition coverage table documenting presence and single-scenario limits.
    """
    rows = []
    for label, scenarios in LABEL_SCENARIO_MAPPING.items():
        assigned_parts = {SCENARIO_PARTITIONS[s] for s in scenarios if s in SCENARIO_PARTITIONS}
        in_train = "yes" if "train" in assigned_parts else "no"
        in_val = "yes" if "val" in assigned_parts else "no"
        in_test = "yes" if "test" in assigned_parts else "no"
        is_single = "yes" if len(scenarios) == 1 else "no"

        notes = "Multi-scenario distribution"
        if is_single == "yes":
            single_scen = scenarios[0]
            part = SCENARIO_PARTITIONS.get(single_scen, "unknown")
            notes = f"Single-scenario limitation: present exclusively in {single_scen} ({part}); not split per Invariant 4"

        rows.append({
            "label_name": label,
            "scenario_count": len(scenarios),
            "in_train": in_train,
            "in_val": in_val,
            "in_test": in_test,
            "is_single_scenario": is_single,
            "notes": notes,
        })
    return rows
