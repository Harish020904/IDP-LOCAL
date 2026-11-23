"""Data cleaning, quarantine filtering, and reconciliation engine for IoT-23."""
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional

from iot23.schema import CANONICAL_FIELDS, ZEEK_UNSET_FIELD
from iot23.quality import (
    is_valid_port,
    has_negative_duration,
    is_valid_timestamp,
    is_consistent_label_pair,
)

CLEANING_OPERATIONS = [
    {
        "operation_number": "OP01",
        "field_or_condition": "Column count != 23",
        "reason": "Quarantine truncated or malformed rows failing canonical schema",
        "issue_id": "Q01",
        "action": "QUARANTINE",
    },
    {
        "operation_number": "OP02",
        "field_or_condition": "ts <= 0 or unparseable",
        "reason": "Quarantine records with invalid temporal timestamps",
        "issue_id": "Q02",
        "action": "QUARANTINE",
    },
    {
        "operation_number": "OP03",
        "field_or_condition": "id.orig_p or id.resp_p < 0 or > 65535",
        "reason": "Quarantine records with out-of-range transport ports",
        "issue_id": "Q04",
        "action": "QUARANTINE",
    },
    {
        "operation_number": "OP04",
        "field_or_condition": "label is '-' or empty",
        "reason": "Quarantine flows lacking ground truth supervisory labels",
        "issue_id": "Q06",
        "action": "QUARANTINE",
    },
    {
        "operation_number": "OP05",
        "field_or_condition": "duration < 0.0",
        "reason": "Flag negative durations with duration_flag; preserve raw value",
        "issue_id": "Q03",
        "action": "FLAG",
    },
    {
        "operation_number": "OP06",
        "field_or_condition": "Benign with attack detailed-label",
        "reason": "Flag label inconsistency in label_flag; preserve original labels",
        "issue_id": "Q07",
        "action": "FLAG",
    },
    {
        "operation_number": "OP07",
        "field_or_condition": "Unset metric field is '-'",
        "reason": "Preserve unset token '-'; do not blanket fill with zero",
        "issue_id": "Q08",
        "action": "PRESERVE",
    },
    {
        "operation_number": "OP08",
        "field_or_condition": "Minority attack classes",
        "reason": "Preserve rare attack classes; strictly no balancing or deletion",
        "issue_id": "Q09",
        "action": "PRESERVE",
    },
]

def evaluate_record_for_cleaning(record: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Evaluate a single flow record against cleaning operations.
    
    Returns:
        (cleaned_record, None) if the record passes quarantine checks.
        (None, quarantined_record) if the record violates any quarantine rule.
    """
    # Check OP01: Field count validation
    if len(record) < len(CANONICAL_FIELDS):
        quarantined = dict(record)
        quarantined["quarantine_op"] = "OP01"
        quarantined["quarantine_reason"] = "Column count < 23 (truncated)"
        return None, quarantined

    # Check OP02: Malformed timestamp
    ts_val = record.get("ts")
    if not is_valid_timestamp(ts_val):
        quarantined = dict(record)
        quarantined["quarantine_op"] = "OP02"
        quarantined["quarantine_reason"] = f"Invalid timestamp: {ts_val}"
        return None, quarantined

    # Check OP03: Invalid ports
    orig_p = record.get("id.orig_p")
    resp_p = record.get("id.resp_p")
    if not is_valid_port(orig_p) or not is_valid_port(resp_p):
        quarantined = dict(record)
        quarantined["quarantine_op"] = "OP03"
        quarantined["quarantine_reason"] = f"Invalid transport port: orig={orig_p}, resp={resp_p}"
        return None, quarantined

    # Check OP04: Missing ground truth label
    raw_label = (record.get("label") or "").strip()
    if not raw_label or raw_label == ZEEK_UNSET_FIELD:
        quarantined = dict(record)
        quarantined["quarantine_op"] = "OP04"
        quarantined["quarantine_reason"] = "Missing ground truth label"
        return None, quarantined

    # Record passed all quarantine gates; create cleaned record copy
    cleaned = dict(record)

    # Apply OP05: Duration flag (Q03)
    dur_val = record.get("duration")
    if has_negative_duration(dur_val):
        cleaned["duration_flag"] = "NEGATIVE_DURATION"
    else:
        cleaned["duration_flag"] = "VALID"

    # Apply OP06: Label inconsistency flag (Q07 / Invariant 2)
    # Original labels are NEVER mutated in place
    detailed_lbl = (record.get("detailed-label") or "").strip()
    if not is_consistent_label_pair(raw_label, detailed_lbl):
        cleaned["label_flag"] = "INCONSISTENT_BENIGN_WITH_ATTACK_SUBLABEL"
    else:
        cleaned["label_flag"] = "CONSISTENT"

    # OP07 & OP08: Unset fields and minority classes are preserved as-is
    cleaned["cleaning_status"] = "CLEANED"
    return cleaned, None

def clean_flow_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Clean a batch of flow records and compute reconciliation counts.
    
    Guarantees:
        total_raw == total_cleaned + total_quarantined
    """
    total_raw = len(records)
    cleaned_records: List[Dict[str, Any]] = []
    quarantined_records: List[Dict[str, Any]] = []
    op_counts = {op["operation_number"]: {"removed": 0, "changed": 0} for op in CLEANING_OPERATIONS}

    for r in records:
        cleaned, quarantined = evaluate_record_for_cleaning(r)
        if quarantined is not None:
            quarantined_records.append(quarantined)
            op_code = quarantined.get("quarantine_op", "UNKNOWN")
            if op_code in op_counts:
                op_counts[op_code]["removed"] += 1
        else:
            cleaned_records.append(cleaned)
            if cleaned.get("duration_flag") == "NEGATIVE_DURATION":
                op_counts["OP05"]["changed"] += 1
            if cleaned.get("label_flag") == "INCONSISTENT_BENIGN_WITH_ATTACK_SUBLABEL":
                op_counts["OP06"]["changed"] += 1

    reconciled = verify_reconciliation(total_raw, len(cleaned_records), len(quarantined_records))

    summary = {
        "total_raw": total_raw,
        "total_cleaned": len(cleaned_records),
        "total_quarantined": len(quarantined_records),
        "reconciled": reconciled,
        "operation_counts": op_counts,
    }
    return cleaned_records, quarantined_records, summary

def verify_reconciliation(raw_count: int, cleaned_count: int, removed_count: int) -> bool:
    """
    Assert the core data reconciliation identity:
    raw_rows == cleaned_rows + removed_rows
    """
    return raw_count == (cleaned_count + removed_count)

def generate_cleaning_log_rows(
    summary: Dict[str, Any],
    version: str = "V3",
    log_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generate entries for docs/04-reports/cleaning-log.csv."""
    if log_date is None:
        log_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_raw = summary.get("total_raw", 0)
    op_counts = summary.get("operation_counts", {})

    rows = []
    for op in CLEANING_OPERATIONS:
        op_num = op["operation_number"]
        counts = op_counts.get(op_num, {"removed": 0, "changed": 0})
        rows.append({
            "operation_number": op_num,
            "field_or_condition": op["field_or_condition"],
            "reason": op["reason"],
            "records_examined": total_raw,
            "records_changed": counts.get("changed", 0),
            "records_removed": counts.get("removed", 0),
            "date": log_date,
            "version": version,
        })
    return rows

def write_cleaning_log(rows: List[Dict[str, Any]], output_path: Path) -> None:
    """Write the cleaning log CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "operation_number",
        "field_or_condition",
        "reason",
        "records_examined",
        "records_changed",
        "records_removed",
        "date",
        "version",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
