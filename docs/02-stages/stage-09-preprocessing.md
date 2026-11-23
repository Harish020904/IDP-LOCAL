# Stage 09 — Preprocessing

**Milestone:** M3 Transformation  
**Author:** Data Engineer  
**Date:** 2026-11-23  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 09 implements feature preprocessing: numerical median imputation, standard scaling, and categorical vocabulary encoding. The implementation strictly enforces Invariant 5: every transformation parameter is learned exclusively on the training partition and recorded with `fit_source = train`. Unseen categories in validation and test partitions are handled safely without crashing.

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Features Transformed | 14 (10 numerical, 4 categorical) |
| Total Learned Parameters | 34 (30 numerical, 4 categorical vocabularies) |
| Fit Source | `train` strictly for all 34 parameters (100.0%) |
| Leakage Prevention | Strict runtime error if `fit()` is invoked with `partition_name != 'train'` |
| Out-of-Vocabulary Fallback | Reserved index 0 (`<UNK>`) for all categorical fields |
| Schema Consistency | Identical column count and naming across all transformed partitions |

---

## 3. Milestone 3 Completion Summary

With the completion of Stage 09, **Milestone 3 (Transformation)** is complete:
- **Stage 06 (Cleaning):** All 8 cleaning operations executed with exact reconciliation identity ($raw \equiv cleaned + removed$).
- **Stage 07 (Feature Governance):** All columns classified into roles; leakage vectors registered; IP addresses preserved as metadata for forensic traceability.
- **Stage 08 (Data Partitioning):** Whole scenario partitioning across 18 captures with pairwise disjointness; single-scenario attack labels documented.
- **Stage 09 (Preprocessing):** Imputation, scaling, and categorical encoding fitted exclusively on the training partition.

---

## 4. Verification Commands

Gate tests:
```bash
uv run --with pytest pytest tests/gates/test_stage_09_gate.py -v
```
