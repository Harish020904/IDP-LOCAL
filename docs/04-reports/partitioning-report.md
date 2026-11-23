# Stage 08 — Data Partitioning Report

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Completed  
**Pipeline Milestone:** Milestone 3 — Transformation  

---

## 1. Executive Summary

Stage 08 establishes the official scenario-level train/validation/test partitioning for the IoT-23 dataset. The partitioning strictly adheres to **Invariant 4**:
> *"No capture scenario crosses a partition boundary. Whole scenarios only. If a label exists in one capture, document that limitation in docs/04-reports/label-coverage.csv; never split the capture to force coverage."*

All 18 confirmed raw captures (15 malicious and 3 benign) are assigned to whole scenario partitions, guaranteeing strict mathematical disjointness:
$$\text{train} \cap \text{val} = \emptyset, \quad \text{train} \cap \text{test} = \emptyset, \quad \text{val} \cap \text{test} = \emptyset$$

---

## 2. Partition Summary Statistics

| Partition | Total Scenarios | Malicious Scenarios | Benign Scenarios | Ratio of Scenarios | Benign Scenario Included |
|---|---|---|---|---|---|
| **Train** | 10 | 9 | 1 | 55.6% | `CTU-Honeypot-Capture-5-1` |
| **Validation** | 4 | 3 | 1 | 22.2% | `CTU-Honeypot-Capture-4-1` |
| **Test** | 4 | 3 | 1 | 22.2% | `CTU-Honeypot-Capture-7-1` |
| **Total** | **18** | **15** | **3** | **100.0%** | **All 3 Benign Captures Allocated** |

---

## 3. Scenario Disjointness Verification

Pairwise scenario intersection verification:
- $\text{Train} \cap \text{Validation} = \emptyset$ (Disjoint: True)
- $\text{Train} \cap \text{Test} = \emptyset$ (Disjoint: True)
- $\text{Validation} \cap \text{Test} = \emptyset$ (Disjoint: True)
- Union of all partitions equals the full 18-capture raw inventory.

---

## 4. Label Coverage & Single-Scenario Limitations

As detailed in `docs/04-reports/label-coverage.csv`:
- Coarse labels `Benign` and `Malicious` are represented across all three partitions.
- Ubiquitous attacks such as `PartOfAHorizontalPortScan` and `C&C` span multiple scenarios and partitions.
- Several specific attack types exist within exactly one scenario in the entire IoT-23 corpus:
  - `Torii` (Scenario 20-1) is present exclusively in the `test` partition.
  - `Trojan` (Scenario 42-1) is present exclusively in the `val` partition.
  - `Somware` (Scenario 7-1) is present exclusively in the `val` partition.
  - `DDoS` / `Kenjiro` (Scenario 33-1) is present exclusively in the `test` partition.
  - `Okiru` (Scenario 36-1), `Gagfyt` (Scenario 60-1), `Muhstik` (Scenario 3-1), and `Hide and Seek` (Scenario 1-1) are present in `train`.

Per Invariant 4, these single-scenario occurrences are preserved as legitimate dataset constraints and documented as such. Under no circumstances is a capture scenario artificially split across partition boundaries to force test-set label coverage.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest tests/gates/test_stage_08_gate.py -v
```
