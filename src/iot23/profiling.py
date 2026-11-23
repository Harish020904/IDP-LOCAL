"""Profiling and statistical analysis utilities for IoT-23 Zeek conn.log."""
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from iot23.schema import CANONICAL_FIELDS, ZEEK_UNSET_FIELD

def parse_zeek_log_file(filepath: Path) -> List[Dict[str, Any]]:
    """Parse a Zeek conn.log file into a list of row dictionaries."""
    records = []
    fields = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                continue
            if line.startswith("#"):
                if line.startswith("#fields"):
                    fields = line.split("\t")[1:]
                continue
            parts = line.split("\t")
            if fields and len(parts) == len(fields):
                records.append(dict(zip(fields, parts)))
            elif len(parts) == len(CANONICAL_FIELDS):
                records.append(dict(zip(CANONICAL_FIELDS, parts)))
    return records

def profile_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute comprehensive statistical profile for a list of flow records."""
    total_count = len(records)
    if total_count == 0:
        return {"total_records": 0}

    missing_counts = {col: 0 for col in CANONICAL_FIELDS}
    unique_values = {col: set() for col in CANONICAL_FIELDS}
    label_counts: Dict[str, int] = {}
    detailed_label_counts: Dict[str, int] = {}
    proto_counts: Dict[str, int] = {}
    conn_state_counts: Dict[str, int] = {}

    numeric_fields = ["duration", "orig_bytes", "resp_bytes", "orig_pkts", "resp_pkts"]
    numeric_values = {col: [] for col in numeric_fields}

    for r in records:
        for col in CANONICAL_FIELDS:
            val = r.get(col, ZEEK_UNSET_FIELD)
            if val == ZEEK_UNSET_FIELD:
                missing_counts[col] += 1
            else:
                unique_values[col].add(val)

        # Categorical counts
        lbl = r.get("label", "Unknown")
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

        dlbl = r.get("detailed-label", ZEEK_UNSET_FIELD)
        detailed_label_counts[dlbl] = detailed_label_counts.get(dlbl, 0) + 1

        proto = r.get("proto", "Unknown")
        proto_counts[proto] = proto_counts.get(proto, 0) + 1

        cstate = r.get("conn_state", "Unknown")
        conn_state_counts[cstate] = conn_state_counts.get(cstate, 0) + 1

        # Numerical fields
        for nf in numeric_fields:
            val = r.get(nf, ZEEK_UNSET_FIELD)
            if val != ZEEK_UNSET_FIELD:
                try:
                    numeric_values[nf].append(float(val))
                except ValueError:
                    pass

    numeric_summary = {}
    for nf, vals in numeric_values.items():
        if vals:
            numeric_summary[nf] = {
                "count": len(vals),
                "min": min(vals),
                "max": max(vals),
                "mean": sum(vals) / len(vals),
            }
        else:
            numeric_summary[nf] = {"count": 0, "min": None, "max": None, "mean": None}

    return {
        "total_records": total_count,
        "missing_counts": missing_counts,
        "missing_percentages": {k: (v / total_count) * 100 for k, v in missing_counts.items()},
        "unique_counts": {k: len(v) for k, v in unique_values.items()},
        "label_counts": label_counts,
        "label_percentages": {k: (v / total_count) * 100 for k, v in label_counts.items()},
        "detailed_label_counts": detailed_label_counts,
        "proto_counts": proto_counts,
        "conn_state_counts": conn_state_counts,
        "numeric_summary": numeric_summary,
    }

def generate_profiling_figures(profile: Dict[str, Any], output_dir: Path) -> List[Path]:
    """Generate and save publication-grade distribution plots."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    # 1. Label Distribution Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    lbls = list(profile["label_counts"].keys())
    counts = [profile["label_counts"][k] for k in lbls]
    ax.bar(lbls, counts, color=["#f85149" if "Malicious" in l else "#3fb950" for l in lbls])
    ax.set_title("IoT-23 Label Distribution")
    ax.set_ylabel("Record Count")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    p1 = output_dir / "label_distribution.png"
    plt.savefig(p1, dpi=150)
    plt.close()
    generated.append(p1)

    # 2. Detailed Label Plot (Horizontal Bar with log scale)
    fig, ax = plt.subplots(figsize=(8, 5))
    d_lbls = list(profile["detailed_label_counts"].keys())
    d_counts = [profile["detailed_label_counts"][k] for k in d_lbls]
    ax.barh(d_lbls, d_counts, color="#58a6ff")
    ax.set_xscale("log")
    ax.set_title("IoT-23 Detailed Attack Labels (Log Scale)")
    ax.set_xlabel("Record Count (Log Scale)")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    p2 = output_dir / "detailed_label_distribution.png"
    plt.savefig(p2, dpi=150)
    plt.close()
    generated.append(p2)

    # 3. Missing Values Percentage Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    cols = list(profile["missing_percentages"].keys())
    pcts = [profile["missing_percentages"][k] for k in cols]
    ax.bar(cols, pcts, color="#d29922")
    ax.set_title("Missing Value Percentage per Field ('-')")
    ax.set_ylabel("Missing %")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=70, ha="right", fontsize=8)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    p3 = output_dir / "missing_values.png"
    plt.savefig(p3, dpi=150)
    plt.close()
    generated.append(p3)

    return generated
