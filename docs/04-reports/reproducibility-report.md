# Stage 11 — Data Integrity and Reproducibility Report

**Version:** 1.0  
**Date:** 2026-11-24  
**Status:** Completed  
**Pipeline Milestone:** Milestone 4 — Product  

---

## 1. Executive Summary

Stage 11 performs the end-to-end reproducibility audit of the IoT-23 dataset preparation pipeline. Every transformation stage from raw ingestion to scenario-partitioned Parquet storage has been independently verified against the core invariants and mathematical reconciliation identities.

All generated manifests, reports, and data artifacts are cryptographically registered in `docs/04-reports/prepared-checksums.sha256`.

---

## 2. Invariant Compliance Audit Matrix

| Invariant | Description | Audit Method | Result | Evidence |
|---|---|---|---|---|
| **Invariant 1** | Raw data is read-only | Archive checksum verification against Stratosphere DOI | **PASS** | `docs/04-reports/raw-checksums.sha256` |
| **Invariant 2** | Original labels never silently changed | Schema isolation; `label_flag` used for contradictions | **PASS** | `docs/04-reports/cleaning-report.md` |
| **Invariant 3** | Zero balancing / SMOTE / class deletion | Natural distribution preserved; row count identity | **PASS** | `docs/04-reports/class-distribution.csv` |
| **Invariant 4** | Whole scenarios only (no cross-partition split) | Pairwise set intersection across partitions ($\emptyset$) | **PASS** | `docs/04-reports/partition-manifest.csv` |
| **Invariant 5** | Nothing fitted outside training data | 100% of learned parameters have `fit_source = train` | **PASS** | `docs/04-reports/preprocessing-params.csv` |
| **Invariant 6** | Attributable removals in cleaning log | Exact mathematical identity: $\text{raw} = \text{clean} + \text{removed}$ | **PASS** | `docs/04-reports/cleaning-log.csv` |

---

## 3. End-to-End Reconciliation Summary

$$\text{Total Raw Rows: } 325,307,816 = \text{Quarantined Rows: } 0 + \text{Cleaned Rows: } 325,307,816$$
$$\text{Partitioned Scenarios: } 18 = \text{Train: } 10 + \text{Validation: } 4 + \text{Test: } 4$$
$$\text{Parquet Storage Files: } 18 = \text{Train: } 10 + \text{Validation: } 4 + \text{Test: } 4$$
$$\text{Partition Pairwise Intersection: } \text{Train} \cap \text{Val} = \emptyset, \quad \text{Train} \cap \text{Test} = \emptyset, \quad \text{Val} \cap \text{Test} = \emptyset$$

---

## 4. Cryptographic Artifact Registry

All 22 project reports and manifests have their SHA-256 hashes registered in `docs/04-reports/prepared-checksums.sha256`. Any downstream researcher re-executing this pipeline on the raw Stratosphere archives will reproduce identical outputs.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest --with pyarrow pytest tests/gates/test_stage_11_gate.py -v
```
