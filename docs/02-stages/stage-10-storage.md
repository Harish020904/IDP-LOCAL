# Stage 10 — Storage and Organisation

**Milestone:** M4 Product  
**Author:** Data Engineer  
**Date:** 2026-11-24  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 10 implements the final columnar storage layout for Dataset B. It organizes cleaned, governed, partitioned, and preprocessed flows into scenario-level Parquet files partitioned by split (`train`, `val`, `test`).

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Total Scenarios Stored | 18 |
| Training Scenario Parquet Files | 10 |
| Validation Scenario Parquet Files | 4 |
| Test Scenario Parquet Files | 4 |
| Schema Columns | 39 strictly typed fields |
| Compression Codec | Snappy |
| File Format | Apache Parquet (v2.6) |
| Provenance Tracking | `scenario_id` and `uid` retained in 100% of rows |

---

## 3. Storage Hierarchy

- `partition=train/scenario={scenario_id}/data.parquet` (10 captures)
- `partition=val/scenario={scenario_id}/data.parquet` (4 captures)
- `partition=test/scenario={scenario_id}/data.parquet` (4 captures)

---

## 4. Invariant Compliance

- **Invariant 1 (Raw Read-Only):** Untouched original source; prepared data stored separately in Dataset B hierarchy.
- **Invariant 4 (No Scenario Crossing):** Parquet directory hierarchy mirrors scenario-partition boundaries.
- **Traceability Rule:** `id.orig_h` and `id.resp_h` preserved alongside `scenario_id` for complete auditability.

---

## 5. Verification Commands

Gate tests:
```bash
uv run --with pytest --with pyarrow pytest tests/gates/test_stage_10_gate.py -v
```
