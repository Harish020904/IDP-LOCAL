# Stage 05 — Data Quality Assessment

**Stage:** 05  
**Milestone:** M2 Understanding (Closes Milestone 2)  
**Branch:** `stage/05-quality` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 05 audits the raw IoT-23 dataset across nine dimensions of data quality to prepare the authoritative rule set for Stage 06 (Cleaning). It formulates specific, documented handling decisions for every potential defect (invalid ports, negative durations, unset tokens, duplicate UIDs, label consistency) while strictly observing project invariants.

With the completion of Stage 05, Milestone 2 (Understanding: "Prove what is wrong with it") is concluded.

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Data Quality Audit Report | `docs/04-reports/data-quality-audit.md` | committed |
| Quality Issues Registry | `docs/04-reports/quality-issues.csv` | committed |
| Quality Assessment Module | `src/iot23/quality.py` | committed |
| Stage Note | `docs/02-stages/stage-05-quality.md` | this file |
| Gate Test | `tests/gates/test_stage_05_gate.py` | committed |

---

## Key decisions & invariant protections

1. **Missing values vs zeros:** Confirmed that unset duration (`-`) cannot be blindly imputed with zero.
2. **Duplicate handling:** Invariant established against naive deduplication on feature equality.
3. **Labels:** Original `label` and `detailed-label` confirmed immutable (Invariant 2).
4. **Minority classes:** 100% of minority attack flows preserved without downsampling or SMOTE (Invariant 3).

---

## Milestone 2 Completion Summary

Milestone 2 Understanding (`v2-audited`) consists of Stages 04 and 05:
- **Stage 04 (Raw Profiling & Visualization):** Statistical baselines, class imbalance documentation with log-scale figures, missing value percentages across 23 fields.
- **Stage 05 (Data Quality Assessment):** Systematic quality audit, 9 failure modes cataloged, handling rules defined for Stage 06 cleaning.
