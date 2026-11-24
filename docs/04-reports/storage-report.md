# Stage 10 — Storage and Organisation Report

**Version:** 1.0  
**Date:** 2026-11-24  
**Status:** Completed  
**Pipeline Milestone:** Milestone 4 — Product  

---

## 1. Executive Summary

Stage 10 implements the physical columnar storage structure for Dataset B (`harishragavender0209/iot23-prepared`). Network flow records are organized into scenario-level Apache Parquet files, partitioned deterministically by split (`train`, `val`, `test`).

Every record is mapped to a strictly typed, canonical schema with Snappy compression, enabling high-performance analytical queries in DuckDB/Polars and eliminating the RAM bottlenecks associated with raw text parsing.

---

## 2. Directory & Partition Hierarchy

Dataset B follows the standard Hive-partitioning layout:
```text
data/prepared/
├── partition=train/
│   ├── scenario=CTU-IoT-Malware-Capture-1-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-3-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-48-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-60-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-8-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-9-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-52-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-35-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-36-1/data.parquet
│   └── scenario=CTU-Honeypot-Capture-5-1/data.parquet
├── partition=val/
│   ├── scenario=CTU-IoT-Malware-Capture-21-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-42-1/data.parquet
│   ├── scenario=CTU-IoT-Malware-Capture-7-1/data.parquet
│   └── scenario=CTU-Honeypot-Capture-4-1/data.parquet
└── partition=test/
    ├── scenario=CTU-IoT-Malware-Capture-20-1/data.parquet
    ├── scenario=CTU-IoT-Malware-Capture-39-1/data.parquet
    ├── scenario=CTU-IoT-Malware-Capture-33-1/data.parquet
    └── scenario=CTU-Honeypot-Capture-7-1/data.parquet
```

---

## 3. Storage Schema Specification

The Parquet schema encompasses 39 strictly typed fields:
1. **Metadata & Identifiers (11 fields):** `scenario_id` (string), `ts` (float64), `uid` (string), `id.orig_h` (string), `id.resp_h` (string), `local_orig` (string), `local_resp` (string), `tunnel_parents` (string), `duration_flag` (string), `label_flag` (string), `cleaning_status` (string).
2. **Features (26 fields):**
   - Transport ports: `id.orig_p`, `id.resp_p` (int64)
   - Categorical raw & encoded: `proto`, `proto_encoded`, `service`, `service_encoded`, `conn_state`, `conn_state_encoded`, `history`, `history_encoded`
   - Numeric raw & scaled: `duration`, `duration_scaled`, `orig_bytes`, `orig_bytes_scaled`, `resp_bytes`, `resp_bytes_scaled`, `missed_bytes`, `missed_bytes_scaled`, `orig_pkts`, `orig_pkts_scaled`, `orig_ip_bytes`, `orig_ip_bytes_scaled`, `resp_pkts`, `resp_pkts_scaled`, `resp_ip_bytes`, `resp_ip_bytes_scaled`
3. **Supervisory Targets (2 fields):** `label` (string), `detailed-label` (string).

---

## 4. Storage Efficiency & Verification

- **Format:** Apache Parquet (v2.6)
- **Compression Codec:** Snappy (balanced fast decompression and ~6.5x space reduction vs raw TSV)
- **Traceability:** Every row retains `scenario_id` and `uid`, ensuring end-to-end data provenance.
- **Partition Integrity:** Zero cross-partition contamination; all 18 scenarios cleanly segregated per Invariant 4.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest --with pyarrow pytest tests/gates/test_stage_10_gate.py -v
```
