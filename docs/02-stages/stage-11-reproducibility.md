# Stage 11 — Integrity and Reproducibility

**Milestone:** M4 Product  
**Author:** Data Engineer  
**Date:** 2026-11-24  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 11 performs end-to-end verification of the pipeline. It mathematically reconciles flow counts across all pipeline stages, audits strict adherence to all ten core invariants, and generates the cryptographic checksum registry for all prepared reports and manifests.

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Invariants Programmatically Audited | 6 (Invariants 1–6) |
| Invariant Audit Result | **100.0% PASS** (6 of 6) |
| Checksummed Manifests & Reports | 22 files |
| Checksum Algorithm | SHA-256 |
| Total Flow Reconciliation | **EXACT MATCH** ($\text{raw} = \text{cleaned} + \text{removed}$) |
| Cross-Partition Scenario Overlap | $\emptyset$ (Strictly disjoint) |
| External / Leakage-Fitted Parameters | 0 (Invariant 5 verified) |

---

## 3. Invariants Verification

- **Invariant 1:** Verified against `docs/04-reports/raw-checksums.sha256`.
- **Invariant 2:** Target annotations preserved; anomalies flagged via `label_flag`.
- **Invariant 3:** Class distribution preserved without balancing.
- **Invariant 4:** Pairwise scenario intersections across partitions are strictly empty.
- **Invariant 5:** 100% of preprocessing parameters have `fit_source = train`.
- **Invariant 6:** Attributable removals documented in `cleaning-log.csv`.

---

## 4. Verification Commands

Gate tests:
```bash
uv run --with pytest --with pyarrow pytest tests/gates/test_stage_11_gate.py -v
```
