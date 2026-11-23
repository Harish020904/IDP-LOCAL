# Stage 06 — Raw Data Cleaning Report

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Completed  
**Pipeline Milestone:** Milestone 3 — Transformation  

---

## 1. Executive Summary

Stage 06 implements the data cleaning transformations for the IoT-23 dataset according to the binding handling decisions established in the Stage 05 Data Quality Audit (`docs/04-reports/quality-issues.csv`). 

Every modification is tracked in `docs/04-reports/cleaning-log.csv`, and the core reconciliation identity holds exactly:
$$\text{raw\_rows} = \text{cleaned\_rows} + \text{removed\_rows}$$

---

## 2. The Reconciliation Identity

| Metric | Count | Proportion | Reconciliation Verification |
|---|---|---|---|
| Total Raw Rows Examined | 325,307,816 | 100.0% | $325,307,816$ |
| Quarantined (Removed) Rows | 0 | 0.0% | $+ 0$ |
| Retained (Cleaned) Rows | 325,307,816 | 100.0% | $= 325,307,816$ |
| **Reconciliation Status** | **EXACT MATCH** | **100.0%** | $\text{raw} \equiv \text{cleaned} + \text{removed}$ |

In the full capture audit across all 18 labelled captures, zero rows were found with truncated columns (Q01), malformed timestamps (Q02), invalid transport ports (Q04), or missing supervisory labels (Q06). Thus, zero flows required quarantine removal.

---

## 3. Cleaning Operations Catalog

All operations are registered in `docs/04-reports/cleaning-log.csv`:

| Op ID | Condition / Rule | Action | Audit Issue | Records Examined | Records Changed | Records Removed |
|---|---|---|---|---|---|---|
| **OP01** | `Column count != 23` | QUARANTINE | Q01 | 325,307,816 | 0 | 0 |
| **OP02** | `ts <= 0` or non-float | QUARANTINE | Q02 | 325,307,816 | 0 | 0 |
| **OP03** | `port < 0` or `> 65535` | QUARANTINE | Q04 | 325,307,816 | 0 | 0 |
| **OP04** | `label` is `'-'` or empty | QUARANTINE | Q06 | 325,307,816 | 0 | 0 |
| **OP05** | `duration < 0.0` | FLAG (`duration_flag`) | Q03 | 325,307,816 | 0 | 0 |
| **OP06** | Benign with attack sublabel | FLAG (`label_flag`) | Q07 | 325,307,816 | 0 | 0 |
| **OP07** | Metric field is `'-'` | PRESERVE | Q08 | 325,307,816 | 0 | 0 |
| **OP08** | Minority attack classes | PRESERVE | Q09 | 325,307,816 | 0 | 0 |

---

## 4. Invariant Compliance & Non-Negotiable Rules

1. **Raw Data Read-Only (Invariant 1):** The raw archive at Dataset A (`harishragavender0209/iot-23-raw`) was verified against `docs/04-reports/raw-checksums.sha256`. No file was modified in place.
2. **Original Labels Never Silently Changed (Invariant 2):** Any label inconsistencies are recorded in a separate `label_flag` column. `label` and `detailed-label` remain untouched.
3. **No Blanket Zero Fill:** Unset values represented by `-` (e.g. in `duration`, `orig_bytes`, `conn_state`) are preserved as unset tokens. They are not replaced with zeros.
4. **No Naive Deduplication:** Connection flows sharing duplicate features or duplicate UIDs across captures are not dropped, preserving realistic traffic volume and burst patterns.
5. **No Balancing or Minority Deletion (Invariant 3):** All minority attack classes (`Mirai`, `Torii`, `Okiru`, etc.) are retained in their natural frequency.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest pytest tests/gates/test_stage_06_gate.py -v
```
