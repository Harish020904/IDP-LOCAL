# Stage 08 — Data Partitioning

**Milestone:** M3 Transformation  
**Author:** Data Engineer  
**Date:** 2026-11-23  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 08 defines the train/validation/test partitioning scheme at the scenario level for the IoT-23 dataset. It enforces Invariant 4: whole scenarios only, zero scenarios crossing partition boundaries, and explicit documentation of single-scenario attack labels.

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Total Scenarios Partitioned | 18 |
| Training Scenarios | 10 (9 malicious, 1 benign) |
| Validation Scenarios | 4 (3 malicious, 1 benign) |
| Test Scenarios | 4 (3 malicious, 1 benign) |
| Scenario Intersections | $\emptyset$ (Strictly disjoint across all pairs) |
| Benign Captures Allocated | 3 (1 in train, 1 in val, 1 in test) |
| Documented Single-Scenario Labels | 8 |

---

## 3. Disjointness Guarantees

Pairwise intersection of partition sets:
```python
for a, b in combinations(partitions, 2):
    assert partitions[a] & partitions[b] == set()
```
Result: Verified TRUE for all partition pairs.

---

## 4. Single-Scenario Limitations (Invariant 4)

Documented in `docs/04-reports/label-coverage.csv`:
- `Torii` appears only in `test` (Capture 20-1).
- `Trojan` appears only in `val` (Capture 42-1).
- `Somware` appears only in `val` (Capture 7-1).
- `DDoS` appears only in `test` (Capture 33-1).
- `Okiru` appears only in `train` (Capture 36-1).

These distributions reflect the authentic Stratosphere Lab capture methodology and are not artificially split.

---

## 5. Verification Commands

Gate tests:
```bash
uv run --with pytest pytest tests/gates/test_stage_08_gate.py -v
```
