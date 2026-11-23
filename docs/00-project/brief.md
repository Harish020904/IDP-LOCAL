# Project Brief — IoT-23 Dataset Engineering Pipeline

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Authoritative — changes require a manager-approved PR

---

## 1. Research Question

Reproduce the IoT-23 labelled network-flow dataset as a research-grade, scenario-partitioned artifact, such that any researcher starting from the same raw source reaches the same prepared output from the committed pipeline code alone — with every transformation documented, every removed row attributable, and every claim traceable to a committed script or notebook.

The pipeline serves NIDS (Network Intrusion Detection System) model evaluation research. It does not perform that evaluation.

---

## 2. Source Dataset

| Property | Value |
|---|---|
| Name | IoT-23 |
| Publisher | Stratosphere Laboratory, Czech Technical University |
| Version | 1.0.0 |
| Format | Zeek conn.log (tab-separated, labelled at the flow level) |
| Captures | 23 total — 20 malicious (IoT device scenarios), 3 benign |
| Label fields | label and detailed-label (analyst annotations) |
| DOI | 10.5281/zenodo.4743746 |
| Citation | Garcia, S., Parmisano, A., & Erquiaga, M. J. (2020). IoT-23: A labeled dataset with malicious and benign IoT network traffic (Version 1.0.0). Stratosphere Laboratory. https://doi.org/10.5281/zenodo.4743746 |

---

## 3. Kaggle Dataset Slugs

| Dataset | Slug | Purpose |
|---|---|---|
| Dataset A — Raw Original | harishragavender0209/iot-23-raw | Immutable source. Never modified. 18 labeled files confirmed 2026-11-23. |
| Dataset B — Prepared | harishragavender0209/iot23-prepared | Pipeline output. Versioned V0-V5. Created at M1. |

Dataset A URL: https://www.kaggle.com/datasets/harishragavender0209/iot-23-raw
Dataset A kernel mount: /kaggle/input/iot-23-raw/
Dataset B kernel mount: /kaggle/input/iot23-prepared/

---

## 4. The Thirteen Stages

Stage numbers are fixed. Do not renumber, merge or skip stages.

| Stage | Name | Milestone | Theme |
|---|---|---|---|
| 00 | Project Definition | M1 Foundation | Control plane only — no data read |
| 01 | Acquisition and Integrity | M1 Foundation | Archive checksum, capture inventory |
| 02 | Raw Inventory | M1 Foundation | Row counts, file manifest |
| 03 | Zeek Schema | M1 Foundation | Data dictionary, label fields confirmed |
| 04 | Raw Profiling and Visualisation | M2 Understanding | Column distributions, class counts |
| 05 | Data Quality Assessment | M2 Understanding | Audit: missing, out-of-range, impossible values |
| 06 | Cleaning | M3 Transformation | Logged removals, reconciliation identity |
| 07 | Feature Governance | M3 Transformation | Column roles, leakage register |
| 08 | Data Partitioning | M3 Transformation | Scenario-level train/val/test split |
| 09 | Preprocessing | M3 Transformation | Imputation, scaling, encoding — fit on train only |
| 10 | Storage and Organisation | M4 Product | Final Parquet structure |
| 11 | Integrity and Reproducibility | M4 Product | End-to-end re-run, checksum verification |
| 12 | Class Imbalance Report | M4 Product | Documents imbalance — does not fix it |

### Milestones and version tags

| Milestone | Stages | Tag | Dataset B version |
|---|---|---|---|
| M1 Foundation | 0-3 | v1-inspected | V1 |
| M2 Understanding | 4-5 | v2-audited | V2 |
| M3 Transformation | 6-9 | v3-transformed | V3 |
| M4 Product | 10-12 | v5-validated | V5 |

---

## 5. Dataset Versioning Scheme

Dataset A (harishragavender0209/iot-23-raw):
Read-only. Never versioned after initial upload. Its SHA-256 is verified in every stage that reads from it.

Dataset B (harishragavender0209/iot23-prepared):

| Version | Created when | Contents |
|---|---|---|
| V0 | Before M1 | Placeholder only — establishes the dataset slug |
| V1 | M1 complete | Inventory manifest, schema dictionary |
| V2 | M2 complete | Quality audit report |
| V3 | M3 complete | Cleaned, partitioned, preprocessed Parquet |
| V5 | M4 complete | Final validated dataset with integrity report and imbalance documentation |

V4 is intentionally skipped: V5 is the final published release.

---

## 6. The Three Hard Invariants

These three are most likely to be violated accidentally.

### 6.1 No balancing at any stage

No SMOTE, no SMOTENC, no oversampling, no undersampling, no synthetic flow generation, no minority class deletion — anywhere in this pipeline.

Stage 12 documents the class imbalance. It does not reduce it.

Rationale: Balancing changes the distribution the model is evaluated on. Recording the true distribution is a property of a research-grade dataset, not a limitation.

### 6.2 No scenario crosses a partition boundary

Whole capture scenarios are assigned to exactly one partition: train, validation, or test. A scenario is never split across partition boundaries.

If a label value exists in only one capture, it appears in only one partition. This is documented in Stage 12. It is a property of the dataset, not a problem to engineer around.

Rationale: Splitting a capture to force label coverage is data leakage at the scenario level.

### 6.3 Nothing fitted outside the training partition

Imputation values, scaling parameters, encoding dictionaries, category frequency tables — all computed exclusively on the training partition. Applied unchanged to validation and test. The fit source is recorded with every stored parameter.

Rationale: Computing a scaler on the full dataset leaks information about the test set into the model.

---

## 7. What This Pipeline Does Not Do

| Non-goal | Reason |
|---|---|
| Model training | The pipeline is a data preparation artifact. |
| Inference or prediction | No model is built. |
| Evaluation on external benchmarks | Requires a model and a benchmark — neither is in scope. |
| Feature selection or dimensionality reduction | A modelling choice; deferred to downstream researcher. |
| Cross-dataset comparison | IoT-23 only. |
| Synthetic data generation | Prohibited by Invariant 6.1. |
| Online or streaming processing | Source data is a static historical capture. |
| Automated hyperparameter tuning | No model, no hyperparameters. |

---

## 8. The Three Planes

| Plane | Machine | Holds |
|---|---|---|
| Control | Arch Linux laptop (harish) | Code, docs, tests, manifests, small reports. No dataset. |
| Compute | Kaggle kernels | Every scan, transform, and test that touches data. |
| Storage | Kaggle Datasets | Dataset A (immutable) and Dataset B (versioned). |

The dataset is 21 GB compressed. The laptop has 12 GB of RAM. The data never leaves Kaggle.

---

## 9. The Ten Invariants (reference)

Defined in full in AGENTS.md section 7.

1. Raw data is read-only. SHA-256 verified in every data-touching stage.
2. Original labels never silently changed. Corrections go in new columns with logged reasons.
3. No balancing. See section 6.1.
4. No scenario crosses a partition. See section 6.2.
5. Nothing fitted outside training data. See section 6.3.
6. Every removed row is attributable to a numbered cleaning-log operation.
7. Every number in a report is reproducible from a committed script.
8. Every change is reviewed before it reaches main.
9. A PR without its evidence pack is not reviewable.
10. An irreversible decision gets an ADR before it is implemented.

---

## 10. Authorship and Attribution

Pipeline author: Harish Ragavender K
Repository: https://github.com/Harish020904/IDP-LOCAL
Dataset A: https://www.kaggle.com/datasets/harishragavender0209/iot-23-raw

Source dataset citation:
Garcia, S., Parmisano, A., & Erquiaga, M. J. (2020). IoT-23: A labeled dataset with malicious and benign IoT network traffic (Version 1.0.0). Stratosphere Laboratory. https://doi.org/10.5281/zenodo.4743746
