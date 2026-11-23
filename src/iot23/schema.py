"""Canonical Zeek conn.log schema definition and validator for IoT-23."""
import csv
from pathlib import Path
from typing import Dict, List, Set, Any

ZEEK_SEPARATOR = "\t"
ZEEK_UNSET_FIELD = "-"
ZEEK_EMPTY_FIELD = "(empty)"

# Canonical 23 fields in exact Zeek order
CANONICAL_FIELDS: List[str] = [
    "ts",
    "uid",
    "id.orig_h",
    "id.orig_p",
    "id.resp_h",
    "id.resp_p",
    "proto",
    "service",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "conn_state",
    "local_orig",
    "local_resp",
    "missed_bytes",
    "history",
    "orig_pkts",
    "orig_ip_bytes",
    "resp_pkts",
    "resp_ip_bytes",
    "tunnel_parents",
    "label",
    "detailed-label",
]

TARGET_COLUMNS: Set[str] = {"label", "detailed-label"}
METRIC_COLUMNS: Set[str] = {
    "duration",
    "orig_bytes",
    "resp_bytes",
    "missed_bytes",
    "orig_pkts",
    "orig_ip_bytes",
    "resp_pkts",
    "resp_ip_bytes",
}
IDENTIFIER_COLUMNS: Set[str] = {"uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p"}

def validate_schema_fields(fields: List[str]) -> bool:
    """Validate that the given fields match the canonical 23 IoT-23 columns."""
    if len(fields) != len(CANONICAL_FIELDS):
        return False
    return fields == CANONICAL_FIELDS

def load_data_dictionary(path: Path) -> List[Dict[str, str]]:
    """Load data dictionary CSV."""
    if not path.is_file():
        raise FileNotFoundError(f"Data dictionary not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))
