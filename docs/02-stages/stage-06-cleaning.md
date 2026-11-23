# Stage 06 — Raw Data Cleaning

**Milestone:** M3 Transformation  
**Author:** Data Engineer  
**Date:** 2026-11-23  
**Status:** Complete  

---

## 1. Objectives & Scope

Stage 06 implements the cleaning logic and quarantine mechanisms for raw IoT-23 Zeek connection flows. Every removal or flag operation corresponds directly to decisions from the Stage 05 Data Quality Audit (`docs/04-reports/quality-issues.csv`) and is registered in the cleaning log.

The stage enforces:
- Attributable removals with explicit operation numbers (Invariant 6)
- The core reconciliation identity: $\text{raw\_rows} = \text{cleaned\_rows} + \text{removed\_rows}$
- Preservation of original labels via `label_flag` (Invariant 2)
- Preservation of rare attack classes without balancing (Invariant 3)
- Preservation of unset tokens `-` without blanket zero fill

---

## 2. Key Numbers

| Metric | Value |
|---|---|
| Total Raw Rows Examined | 325,307,816 |
| Total Rows Quarantined / Removed | 0 |
| Total Cleaned Rows Retained | 325,307,816 |
| Reconciliation Status | **EXACT MATCH** ($\text{raw} = \text{cleaned} + \text{removed}$) |
| Registered Cleaning Operations | 8 (OP01–OP08) |
| Missing Value Fill Applied | NONE (`-` preserved as unset) |
| Balancing or Class Deletion Applied | NONE (Invariant 3 enforced) |

---

## 3. Cleaning Operations Breakdown

| Op ID | Rule | Target Field | Action | Reason |
|---|---|---|---|---|
| **OP01** | Column count != 23 | Entire record | QUARANTINE | Truncated line failing canonical Zeek schema |
| **OP02** | ts <= 0 or non-float | `ts` | QUARANTINE | Invalid temporal epoch value |
| **OP03** | port < 0 or > 65535 | `id.orig_p`, `id.resp_p` | QUARANTINE | Out-of-bounds transport layer port |
| **OP04** | label is '-' or empty | `label` | QUARANTINE | Missing supervisory ground truth |
| **OP05** | duration < 0.0 | `duration` | FLAG (`duration_flag`) | Physically impossible duration flagged; raw value kept |
| **OP06** | Benign with attack sublabel | `label`, `detailed-label` | FLAG (`label_flag`) | Contradictory annotation flagged; labels preserved intact |
| **OP07** | Unset token '-' | Metric fields | PRESERVE | Avoid conflating unknown with zero |
| **OP08** | Minority attack classes | `label`, `detailed-label` | PRESERVE | Real-world class distribution preserved |

---

## 4. Invariants Enforced

- **Invariant 1 (Raw Read-Only):** Verified raw checksums against `docs/04-reports/raw-checksums.sha256`.
- **Invariant 2 (Label Integrity):** Original labels `label` and `detailed-label` are untouched. Inconsistencies produce `label_flag = 'INCONSISTENT_BENIGN_WITH_ATTACK_SUBLABEL'`.
- **Invariant 3 (No Balancing):** Zero synthetic sampling, zero oversampling/undersampling, zero minority pruning.
- **Invariant 6 (Attributable Removals):** Every quarantined record has `quarantine_op` and `quarantine_reason` referencing `cleaning-log.csv`.

---

## 5. Verification Commands

Gate tests:
```bash
uv run --with pytest pytest tests/gates/test_stage_06_gate.py -v
```
