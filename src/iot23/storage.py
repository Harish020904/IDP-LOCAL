"""Columnar Parquet storage engine and dataset organization for IoT-23 (Dataset B)."""
import csv
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple

import pyarrow as pa
import pyarrow.parquet as pq

from iot23.partitioning import SCENARIO_PARTITIONS, get_scenario_partition

DEFAULT_COMPRESSION = "SNAPPY"

# Canonical schema definition for Dataset B Parquet storage
PARQUET_FIELD_DEFINITIONS = [
    # Metadata & Identifiers
    ("scenario_id", pa.string()),
    ("ts", pa.float64()),
    ("uid", pa.string()),
    ("id.orig_h", pa.string()),
    ("id.resp_h", pa.string()),
    ("local_orig", pa.string()),
    ("local_resp", pa.string()),
    ("tunnel_parents", pa.string()),
    ("duration_flag", pa.string()),
    ("label_flag", pa.string()),
    ("cleaning_status", pa.string()),
    
    # Raw & Scaled Features
    ("id.orig_p", pa.int64()),
    ("id.resp_p", pa.int64()),
    ("proto", pa.string()),
    ("proto_encoded", pa.int64()),
    ("service", pa.string()),
    ("service_encoded", pa.int64()),
    ("duration", pa.float64()),
    ("duration_scaled", pa.float64()),
    ("orig_bytes", pa.float64()),
    ("orig_bytes_scaled", pa.float64()),
    ("resp_bytes", pa.float64()),
    ("resp_bytes_scaled", pa.float64()),
    ("conn_state", pa.string()),
    ("conn_state_encoded", pa.int64()),
    ("missed_bytes", pa.float64()),
    ("missed_bytes_scaled", pa.float64()),
    ("history", pa.string()),
    ("history_encoded", pa.int64()),
    ("orig_pkts", pa.float64()),
    ("orig_pkts_scaled", pa.float64()),
    ("orig_ip_bytes", pa.float64()),
    ("orig_ip_bytes_scaled", pa.float64()),
    ("resp_pkts", pa.float64()),
    ("resp_pkts_scaled", pa.float64()),
    ("resp_ip_bytes", pa.float64()),
    ("resp_ip_bytes_scaled", pa.float64()),
    
    # Supervisory Targets
    ("label", pa.string()),
    ("detailed-label", pa.string()),
]

def get_canonical_parquet_schema() -> pa.Schema:
    """Return the formal PyArrow schema for prepared IoT-23 Parquet files."""
    return pa.schema([(name, dtype) for name, dtype in PARQUET_FIELD_DEFINITIONS])

def records_to_pyarrow_table(records: List[Dict[str, Any]], scenario_id: str) -> pa.Table:
    """Convert a batch of prepared flow dictionaries to a typed PyArrow Table."""
    schema = get_canonical_parquet_schema()
    cols = {field.name: [] for field in schema}

    for r in records:
        for field in schema:
            name = field.name
            dtype = field.type
            if name == "scenario_id":
                cols[name].append(scenario_id)
                continue

            raw_val = r.get(name)
            if raw_val is None or str(raw_val).strip() == "-" or str(raw_val).strip() == "":
                # Nullable default based on type
                if pa.types.is_floating(dtype):
                    cols[name].append(None)
                elif pa.types.is_integer(dtype):
                    cols[name].append(None)
                else:
                    cols[name].append("-")
            else:
                try:
                    if pa.types.is_floating(dtype):
                        cols[name].append(float(raw_val))
                    elif pa.types.is_integer(dtype):
                        cols[name].append(int(float(raw_val)))
                    else:
                        cols[name].append(str(raw_val))
                except (ValueError, TypeError):
                    cols[name].append(None)

    arrays = [pa.array(cols[field.name], type=field.type) for field in schema]
    return pa.Table.from_arrays(arrays, schema=schema)

def write_scenario_parquet(
    records: List[Dict[str, Any]],
    scenario_id: str,
    output_base_dir: Path,
    compression: str = DEFAULT_COMPRESSION,
) -> Path:
    """
    Write a scenario's flows to a partitioned Parquet file:
    output_base_dir/partition={part}/scenario={scen}/data.parquet
    """
    partition = get_scenario_partition(scenario_id)
    target_dir = output_base_dir / f"partition={partition}" / f"scenario={scenario_id}"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "data.parquet"

    table = records_to_pyarrow_table(records, scenario_id)
    pq.write_table(table, target_path, compression=compression)
    return target_path

def read_and_validate_parquet(parquet_path: Path) -> Dict[str, Any]:
    """Read a Parquet file and return validation statistics."""
    if not parquet_path.is_file():
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

    parquet_file = pq.ParquetFile(parquet_path)
    metadata = parquet_file.metadata
    table = parquet_file.read()

    return {
        "num_rows": table.num_rows,
        "num_columns": table.num_columns,
        "column_names": table.column_names,
        "serialized_size": parquet_path.stat().st_size,
        "num_row_groups": metadata.num_row_groups,
        "compression": metadata.row_group(0).column(0).compression if metadata.num_row_groups > 0 else "UNKNOWN",
    }

def write_storage_manifest(manifest_rows: List[Dict[str, Any]], output_path: Path) -> None:
    """Write the Dataset B storage manifest CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scenario_id",
        "partition",
        "file_path",
        "row_count",
        "size_bytes",
        "compression",
        "format",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)
