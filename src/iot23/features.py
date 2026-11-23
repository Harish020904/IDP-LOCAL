"""Feature governance, column role classification, and leakage registry for IoT-23."""
import csv
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple

from iot23.schema import CANONICAL_FIELDS

COLUMN_ROLES = {
    # Metadata / Identifiers (Excluded from model features to prevent memorization, retained for traceability)
    "ts": "metadata",
    "uid": "metadata",
    "id.orig_h": "metadata",
    "id.resp_h": "metadata",
    "local_orig": "metadata",
    "local_resp": "metadata",
    "tunnel_parents": "metadata",
    
    # Input Features (Model predictors)
    "id.orig_p": "feature",
    "id.resp_p": "feature",
    "proto": "feature",
    "service": "feature",
    "duration": "feature",
    "orig_bytes": "feature",
    "resp_bytes": "feature",
    "conn_state": "feature",
    "missed_bytes": "feature",
    "history": "feature",
    "orig_pkts": "feature",
    "orig_ip_bytes": "feature",
    "resp_pkts": "feature",
    "resp_ip_bytes": "feature",
    
    # Targets (Supervisory ground truth)
    "label": "target",
    "detailed-label": "target",
    
    # Cleaning Diagnostic Flags (Metadata)
    "duration_flag": "metadata",
    "label_flag": "metadata",
    "cleaning_status": "metadata",
}

FEATURE_COLUMNS: List[str] = [col for col, role in COLUMN_ROLES.items() if role == "feature"]
TARGET_COLUMNS: List[str] = [col for col, role in COLUMN_ROLES.items() if role == "target"]
METADATA_COLUMNS: List[str] = [col for col, role in COLUMN_ROLES.items() if role == "metadata"]

LEAKAGE_VECTORS = [
    {
        "leakage_id": "LEAK01",
        "vector_name": "Device IP Memorization",
        "affected_columns": "id.orig_h",
        "risk_level": "High",
        "mechanism": "Infected IoT devices use static IP addresses. Classifiers using raw IPs memorize device identities instead of generalizable traffic dynamics.",
        "mitigation_strategy": "Designated as metadata role; excluded from feature tensor X but preserved for audit and scenario traceability.",
    },
    {
        "leakage_id": "LEAK02",
        "vector_name": "Target / C&C IP Memorization",
        "affected_columns": "id.resp_h",
        "risk_level": "High",
        "mechanism": "Attacks target specific scanning destinations or connect to static C&C infrastructure IPs.",
        "mitigation_strategy": "Designated as metadata role; excluded from feature tensor X but preserved for forensic traceability.",
    },
    {
        "leakage_id": "LEAK03",
        "vector_name": "Temporal Timeline Leakage",
        "affected_columns": "ts",
        "risk_level": "High",
        "mechanism": "Monotonic timestamps allow sequence models to reconstruct scenario execution order rather than flow kinetics.",
        "mitigation_strategy": "Designated as metadata role; excluded from feature tensor X.",
    },
    {
        "leakage_id": "LEAK04",
        "vector_name": "Zeek Connection UID Artifact",
        "affected_columns": "uid",
        "risk_level": "Medium",
        "mechanism": "Synthetic hash identifying individual flows; carries no physical or behavioral intrusion signal.",
        "mitigation_strategy": "Designated as metadata role; retained purely as primary key.",
    },
    {
        "leakage_id": "LEAK05",
        "vector_name": "Direct Target Leakage",
        "affected_columns": "label, detailed-label",
        "risk_level": "Critical",
        "mechanism": "Inclusion of target annotations in model inputs yields trivial 100% training accuracy.",
        "mitigation_strategy": "Strict role separation: target columns quarantined from model inputs.",
    },
    {
        "leakage_id": "LEAK06",
        "vector_name": "Zeek Environment Flags",
        "affected_columns": "local_orig, local_resp, tunnel_parents",
        "risk_level": "Low",
        "mechanism": "Lab-specific Zeek sensor deployment flags that do not reflect network flow behavior.",
        "mitigation_strategy": "Designated as metadata role; excluded from modeling features.",
    },
]

def get_column_role(column_name: str) -> str:
    """Return the designated governance role for a column."""
    if column_name not in COLUMN_ROLES:
        raise KeyError(f"Unknown column '{column_name}' not defined in feature governance catalog.")
    return COLUMN_ROLES[column_name]

def validate_all_canonical_columns_governed() -> bool:
    """Validate that every canonical Zeek column has a role assigned."""
    for col in CANONICAL_FIELDS:
        if col not in COLUMN_ROLES:
            return False
    return True

def separate_features_and_targets(record: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Split a record into features (X), targets (y), and metadata based on governance roles.
    Guarantees no target or metadata leaks into features.
    """
    features = {}
    targets = {}
    metadata = {}

    for k, v in record.items():
        role = COLUMN_ROLES.get(k, "metadata")
        if role == "feature":
            features[k] = v
        elif role == "target":
            targets[k] = v
        else:
            metadata[k] = v

    return features, targets, metadata
