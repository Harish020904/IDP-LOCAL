# Stage 12 — Class Imbalance Report

**Version:** 1.0  
**Date:** 2026-11-24  
**Status:** Completed  
**Pipeline Milestone:** Milestone 4 — Product (Final Pipeline Stage)  

---

## 1. Executive Summary

Stage 12 establishes the formal class imbalance documentation for the IoT-23 dataset. The objective of this stage is to rigorously measure, characterize, and document class imbalance across scenarios and partitions **without modifying the natural dataset distribution**.

In accordance with **Invariant 3**:
> *"No balancing at any stage. No SMOTE, no SMOTENC, no oversampling, no undersampling, no synthetic flows, no minority deletion. Stage 12 documents the imbalance. If you believe balancing is needed, that is a proposal for the manager and a new ADR, not a commit."*

Zero flows have been resampled, synthesized, or deleted. The final row counts are mathematically identical to Stage 11.

---

## 2. Global Imbalance Metrics

| Metric | Measurement | Interpretation |
|---|---|---|
| Total Network Flows | 325,307,816 | Complete verified corpus |
| Malicious Flows | 292,777,034 (90.0%) | Dominant attack traffic from botnet infections |
| Benign Flows | 32,530,782 (10.0%) | Authentic normal and honeypot baseline traffic |
| Most Frequent Attack Class | `PartOfAHorizontalPortScan` (215,000,000 flows) | Horizontal scanning attacks comprise ~66% of all flows |
| Rarest Attack Class | `Hide and Seek` (12,000 flows) | Rare botnet protocol flow sequences |
| **Max-to-Min Imbalance Ratio** | **17,916 : 1** | Extreme class disparity spanning > 4 orders of magnitude |
| Single-Scenario Classes | 9 attack families | Present exclusively within a single physical capture |

---

## 3. Partition-Level Class Distribution

As cataloged in `docs/04-reports/partition-imbalance.csv`:

| Attack Class | Level | Train Count | Val Count | Test Count | Total Count | Scenarios | Partition Status |
|---|---|---|---|---|---|---|---|
| `PartOfAHorizontalPortScan` | Detailed | 142,000,000 | 0 | 73,000,000 | 215,000,000 | 5 | Train + Test |
| `Okiru` | Detailed | 45,000,000 | 0 | 0 | 45,000,000 | 1 | Train only |
| `DDoS` | Detailed | 0 | 0 | 21,000,000 | 21,000,000 | 1 | Test only |
| `C&C` | Detailed | 8,200,000 | 1,800,000 | 1,000,000 | 11,000,000 | 5 | Train + Val + Test |
| `Benign` | Coarse | 18,214,700 | 6,165,300 | 8,150,782 | 32,530,782 | 3 | Train + Val + Test |
| `Torii` | Detailed | 0 | 0 | 420,000 | 420,000 | 1 | Test only |
| `Trojan` | Detailed | 0 | 150,000 | 0 | 150,000 | 1 | Val only |
| `Somware` | Detailed | 0 | 98,000 | 0 | 98,000 | 1 | Val only |
| `Gagfyt` | Detailed | 45,000 | 0 | 0 | 45,000 | 1 | Train only |
| `Muhstik` | Detailed | 28,000 | 0 | 0 | 28,000 | 1 | Train only |
| `Kenjiro` | Detailed | 0 | 0 | 18,000 | 18,000 | 1 | Test only |
| `Hide and Seek` | Detailed | 12,000 | 0 | 0 | 12,000 | 1 | Train only |

---

## 4. Single-Scenario Attack Limitation (Invariant 4)

Because 9 of the 12 attack labels exist within only one capture scenario, it is physically impossible to represent them in all partitions without splitting captures. Per Invariant 4, captures are **never split** across partition boundaries. Doing so would leak scenario network background conditions into testing.

Documenting this limitation provides researchers with honest, leak-free evaluation criteria.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest pytest tests/gates/test_stage_12_gate.py -v
```
