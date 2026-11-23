"""Data quality audit checks and assessment engine for IoT-23."""
from typing import Dict, List, Set, Any, Tuple
from iot23.schema import ZEEK_UNSET_FIELD

def is_valid_port(port_val: Any) -> bool:
    """Validate that port is an integer in range 0-65535, or unset token."""
    if port_val is None or str(port_val).strip() == ZEEK_UNSET_FIELD:
        return True
    try:
        p = int(port_val)
        return 0 <= p <= 65535
    except (ValueError, TypeError):
        return False

def has_negative_duration(duration_val: Any) -> bool:
    """Check if duration is negative (an invalid physical measurement)."""
    if duration_val is None or str(duration_val).strip() == ZEEK_UNSET_FIELD:
        return False
    try:
        d = float(duration_val)
        return d < 0.0
    except (ValueError, TypeError):
        return True

def is_valid_timestamp(ts_val: Any) -> bool:
    """Check if timestamp is a valid positive epoch time."""
    if ts_val is None or str(ts_val).strip() == ZEEK_UNSET_FIELD:
        return False
    try:
        t = float(ts_val)
        return t > 0.0
    except (ValueError, TypeError):
        return False

def is_consistent_label_pair(label: str, detailed_label: str) -> bool:
    """
    Check logical consistency between coarse label and detailed label.
    A benign flow should not carry an attack detailed label.
    """
    l_clean = (label or "").strip()
    dl_clean = (detailed_label or "").strip()

    if not l_clean or l_clean == ZEEK_UNSET_FIELD:
        return False

    if l_clean == "Benign":
        # Benign flows should have unset detailed label or benign sub-annotation
        attack_indicators = [
            "PartOfAHorizontalPortScan",
            "Okiru",
            "DDoS",
            "C&C",
            "Attack",
            "Torii",
            "Mirai",
            "Muhstik",
        ]
        for att in attack_indicators:
            if att.lower() in dl_clean.lower():
                return False

    return True

def find_duplicate_uids(records: List[Dict[str, Any]]) -> List[str]:
    """Identify duplicate connection UIDs within a record batch."""
    seen = set()
    duplicates = set()
    for r in records:
        uid = r.get("uid")
        if uid and uid != ZEEK_UNSET_FIELD:
            if uid in seen:
                duplicates.add(uid)
            else:
                seen.add(uid)
    return list(duplicates)

def audit_flow_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute full battery of quality checks over flow records."""
    total = len(records)
    invalid_ports = []
    negative_durations = []
    malformed_timestamps = []
    label_inconsistencies = []

    for idx, r in enumerate(records):
        # Port checks
        if not is_valid_port(r.get("id.orig_p")) or not is_valid_port(r.get("id.resp_p")):
            invalid_ports.append(idx)

        # Duration check
        if has_negative_duration(r.get("duration")):
            negative_durations.append(idx)

        # Timestamp check
        if not is_valid_timestamp(r.get("ts")):
            malformed_timestamps.append(idx)

        # Label consistency check
        lbl = r.get("label", "")
        dlbl = r.get("detailed-label", "")
        if not is_consistent_label_pair(lbl, dlbl):
            label_inconsistencies.append(idx)

    dup_uids = find_duplicate_uids(records)

    return {
        "total_records": total,
        "invalid_ports_count": len(invalid_ports),
        "negative_durations_count": len(negative_durations),
        "malformed_timestamps_count": len(malformed_timestamps),
        "label_inconsistencies_count": len(label_inconsistencies),
        "duplicate_uids_count": len(dup_uids),
        "invalid_port_indices": invalid_ports,
        "negative_duration_indices": negative_durations,
        "label_inconsistency_indices": label_inconsistencies,
    }
