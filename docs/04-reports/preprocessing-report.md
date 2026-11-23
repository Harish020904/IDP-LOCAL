# Stage 09 — Preprocessing Report

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Completed  
**Pipeline Milestone:** Milestone 3 — Transformation  

---

## 1. Executive Summary

Stage 09 implements the feature transformation pipeline (numerical imputation, standard scaling, and categorical encoding) for the IoT-23 dataset. The implementation strictly enforces **Invariant 5**:
> *"Nothing fitted outside training data. Imputation values, scaling parameters, encoders, category frequencies, feature-selection thresholds: computed on train only, applied unchanged to validation and test. Record the fit source with every parameter."*

Every learned transformation parameter is registered in `docs/04-reports/preprocessing-params.csv` with `fit_source = train` and `partition_learned = train`.

---

## 2. Parameter Catalog Summary

| Category | Transformed Columns | Operations | Parameter Count | Fit Source Guarantee |
|---|---|---|---|---|
| **Numerical Features** | 10 columns (`id.orig_p`, `id.resp_p`, `duration`, `orig_bytes`, `resp_bytes`, `missed_bytes`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`) | Median Imputation + Standardization (mean, std) | 30 parameters (3 per column) | `train` strictly |
| **Categorical Features** | 4 columns (`proto`, `service`, `conn_state`, `history`) | Vocabulary Indexing with `<UNK>` fallback | 4 vocabulary sizes | `train` strictly |
| **Total** | **14 feature columns** | **Impute, Scale, Encode** | **34 parameters** | **100% train partition** |

---

## 3. Anti-Leakage Architecture (Invariant 5)

1. **Isolation of Fit Phase:** The `FitOnTrainPreprocessor.fit()` method accepts a `partition_name` argument. If `partition_name != "train"`, the preprocessor raises a runtime `ValueError` to prevent accidental leakage.
2. **Unseen Categorical Handling (OOV Safety):** All categorical vocabularies reserve index 0 for `<UNK>`. When an unseen protocol, service, connection state, or TCP history string appears in the validation or test partitions, it is mapped gracefully to index 0 rather than raising an execution error or corrupting the feature tensor.
3. **Imputation Policy:** Missing values represented by the Zeek unset token `-` are imputed using the **median of the training partition** for that feature. No future or cross-partition statistics leak into imputed values.
4. **Uniform Schema Across Partitions:** Transformed train, validation, and test batches have identical feature columns, ordering, and data types.

---

## 4. Verification Commands

Gate verification command:
```bash
uv run --with pytest tests/gates/test_stage_09_gate.py -v
```
