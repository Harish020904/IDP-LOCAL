# Stage 04 — Raw Data Profiling and Visualisation

**Stage:** 04  
**Milestone:** M2 Understanding  
**Branch:** `stage/04-profiling` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 04 establishes the empirical statistical baseline of the raw IoT-23 dataset prior to any data transformation. It provides:
1. Exact parsing of Zeek tab-delimited records.
2. Distribution profiling for coarse `label` and fine-grained `detailed-label`.
3. Systematic measurement of missing-value tokens (`-`) per column.
4. Generation of publication-grade figures committed to `docs/04-reports/figures/`.
5. Tabulation of scenario distributions and class breakdowns.

Strict observation discipline: no cleaning, imputation, outlier trimming, or resampling was performed.

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Raw Profiling Summary | `docs/04-reports/raw-profiling-summary.md` | committed |
| Class Distribution Table | `docs/04-reports/class-distribution.csv` | committed |
| Scenario Distribution Table | `docs/04-reports/scenario-distribution.csv` | committed |
| Visualization Collection | `docs/04-reports/figures/*.png` | committed |
| Profiling Code Module | `src/iot23/profiling.py` | committed |
| Sample Capture Fixture | `tests/fixtures/sample-capture/sample.log` | committed |
| Stage Note | `docs/02-stages/stage-04-profiling.md` | this file |
| Gate Test | `tests/gates/test_stage_04_gate.py` | committed |

---

## Key findings and numbers

- Coarse labels identified: `Malicious`, `Benign`.
- Detailed labels identified: `PartOfAHorizontalPortScan`, `Okiru`, `DDoS`, `C&C`, `-`.
- Log-scale visualization verified: minority classes remain clearly distinguished.
- Missing values (`-`): High in `tunnel_parents` and `service`, moderate in `duration`, `orig_bytes`, and `resp_bytes` for unestablished connections (`S0`/`REJ`).
- Invariant 3 (no balancing): Verified; raw imbalance preserved without artificial alteration.
