# Stage 07 — Feature Governance

**Milestone:** M3 Transformation  
**Author:** Data Engineer  
**Date:** 2026-11-23  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 07 establishes feature governance for the IoT-23 pipeline. It classifies every column in the dataset into a strictly governed role (`feature`, `target`, or `metadata`), logs all potential information leakage pathways in a formal leakage register, and guarantees that IP address columns are not dropped blindly to avoid leakage.

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Total Governed Columns | 26 (23 canonical Zeek + 3 Stage 06 flags) |
| Feature Columns | 14 |
| Target Columns | 2 (`label`, `detailed-label`) |
| Metadata Columns | 10 |
| Dropped Columns | 0 |
| Registered Leakage Vectors | 6 (LEAK01–LEAK06) |
| Blind IP Deletions | 0 (Retained as metadata for traceability) |

---

## 3. Governance Catalog

- **Input Features (14):** `id.orig_p`, `id.resp_p`, `proto`, `service`, `duration`, `orig_bytes`, `resp_bytes`, `conn_state`, `missed_bytes`, `history`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes`.
- **Supervised Targets (2):** `label`, `detailed-label`.
- **Metadata & Traceability (10):** `ts`, `uid`, `id.orig_h`, `id.resp_h`, `local_orig`, `local_resp`, `tunnel_parents`, `duration_flag`, `label_flag`, `cleaning_status`.

---

## 4. Invariant Compliance

- **Invariant 2 (Label Preservation):** Supervised targets are governed separately and quarantined from feature sets.
- **Traceability Rule (Non-negotiable):** `id.orig_h` and `id.resp_h` are preserved in the dataset as `metadata`, satisfying forensic traceability while preventing model shortcut learning.
- **Invariant 5 (Fit on Train Only Pre-requisite):** Clear delineation of feature columns ensures subsequent scaling and encoding operates strictly on feature columns learned from the train partition.

---

## 5. Verification Commands

Gate tests:
```bash
uv run --with pytest pytest tests/gates/test_stage_07_gate.py -v
```
