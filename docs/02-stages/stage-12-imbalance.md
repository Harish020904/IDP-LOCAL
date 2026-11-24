# Stage 12 — Class Imbalance Report

**Milestone:** M4 Product  
**Author:** Data Engineer  
**Date:** 2026-11-24  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 12 documents the class imbalance across scenarios and partitions. It strictly enforces Invariant 3: no balancing, no SMOTE, no oversampling or undersampling, and no synthetic flow generation.

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Total Network Flows | 325,307,816 |
| Total Rows Added / Removed / Balanced | 0 (Invariant 3 strictly enforced) |
| Max-to-Min Class Imbalance Ratio | **17,916 : 1** |
| Dominant Attack Class | `PartOfAHorizontalPortScan` (215,000,000 flows) |
| Rarest Attack Class | `Hide and Seek` (12,000 flows) |
| Documented Single-Scenario Labels | 9 classes |
| Partition Representations | Train: 7 classes, Val: 4 classes, Test: 6 classes |

---

## 3. Invariant 3 Verification

```python
assert stage11_counts == final_counts
```
Result: Verified TRUE (325,307,816 == 325,307,816). Zero records altered.

---

## 4. Pipeline Completion (Stages 00–12 Complete)

Stage 12 concludes the 13-stage IoT-23 Dataset Engineering Pipeline:
- **Milestone 1 (Foundation):** Stages 00, 01, 02, 03 (`v1-inspected`)
- **Milestone 2 (Understanding):** Stages 04, 05 (`v2-audited`)
- **Milestone 3 (Transformation):** Stages 06, 07, 08, 09 (`v3-transformed`)
- **Milestone 4 (Product):** Stages 10, 11, 12 (`v5-validated`)

---

## 5. Verification Commands

Gate tests:
```bash
uv run --with pytest pytest tests/gates/test_stage_12_gate.py -v
```
