# Stage 07 — Feature Governance Report

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Completed  
**Pipeline Milestone:** Milestone 3 — Transformation  

---

## 1. Executive Summary

Stage 07 establishes the formal feature governance policy for the IoT-23 dataset. Every column across canonical Zeek fields and Stage 06 diagnostic additions is explicitly mapped to a role: `feature`, `target`, or `metadata`. 

Furthermore, all potential data leakage vectors are cataloged in `docs/04-reports/leakage-register.csv`. In strict compliance with project invariants and data safety rules, IP addresses (`id.orig_h`, `id.resp_h`) are **not** dropped blindly to avoid leakage; rather, their leakage risks are recorded and their roles are governed as `metadata`, retaining complete forensic traceability.

---

## 2. Column Roles Summary

| Role | Count | Description | Columns Included |
|---|---|---|---|
| **feature** | 14 | Network flow predictors suitable for model training | `id.orig_p`, `id.resp_p`, `proto`, `service`, `duration`, `orig_bytes`, `resp_bytes`, `conn_state`, `missed_bytes`, `history`, `orig_pkts`, `orig_ip_bytes`, `resp_pkts`, `resp_ip_bytes` |
| **target** | 2 | Supervisory ground truth annotations | `label`, `detailed-label` |
| **metadata** | 10 | Identifiers, temporal markers, local flags, and diagnostic audit flags | `ts`, `uid`, `id.orig_h`, `id.resp_h`, `local_orig`, `local_resp`, `tunnel_parents`, `duration_flag`, `label_flag`, `cleaning_status` |
| **Total** | 26 | Complete governed column space | All canonical 23 + 3 cleaning diagnostic columns |

---

## 3. Data Leakage Vectors & Mitigation Strategy

As registered in `docs/04-reports/leakage-register.csv`:

| Leakage ID | Vector Name | Affected Columns | Risk Level | Mitigation Strategy |
|---|---|---|---|---|
| **LEAK01** | Device IP Memorization | `id.orig_h` | High | Governed as `metadata`; excluded from training feature tensor $X$ while retained for scenario tracing. |
| **LEAK02** | Target/C&C IP Memorization | `id.resp_h` | High | Governed as `metadata`; excluded from training feature tensor $X$ while retained for forensic validation. |
| **LEAK03** | Temporal Timeline Leakage | `ts` | High | Governed as `metadata`; excluded from feature tensor $X$ to prevent chronological memorization. |
| **LEAK04** | Zeek UID Artifact | `uid` | Medium | Governed as `metadata`; retained as primary key for relational joins. |
| **LEAK05** | Direct Target Leakage | `label`, `detailed-label` | Critical | Quarantined under `target` role; strictly prohibited from input predictors. |
| **LEAK06** | Sensor Environment Flags | `local_orig`, `local_resp`, `tunnel_parents` | Low | Governed as `metadata`; excluded from model inputs. |

---

## 4. Traceability vs Leakage (Non-Negotiable Rule)

A common flawed practice in intrusion detection research is the uncritical deletion of IP address columns under the guise of "preventing data leakage." As codified in `AGENTS.md` and `data-safety.md`:
> *"Never drop IP columns 'to avoid leakage': It removes traceability; record the risk instead."*

Removing IP addresses destroys the ability to trace traffic back to specific physical infected devices, verify benign baseline subnet allocations, or perform packet capture post-mortems. By categorizing `id.orig_h` and `id.resp_h` as `metadata`, the pipeline achieves both goals:
1. Prevents model shortcut learning by excluding them from the input feature set $X$.
2. Preserves full scientific traceability in the exported dataset.

---

## 5. Verification Commands

Gate verification command:
```bash
uv run --with pytest tests/gates/test_stage_07_gate.py -v
```
