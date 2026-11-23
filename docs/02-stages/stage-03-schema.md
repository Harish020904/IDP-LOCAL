# Stage 03 — Understand the Raw Zeek Schema

**Stage:** 03  
**Milestone:** M1 Foundation (Closes Milestone 1)  
**Branch:** `stage/03-schema` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 03 establishes the definitive schema for the IoT-23 dataset. It documents the Zeek `conn.log` tab-delimited format, declares types and categories for all 23 columns, identifies the analyst annotation columns (`label` and `detailed-label`), documents missing value representations (`-`), implements programmatic schema validation in `src/iot23/schema.py`, and enforces Invariant 2.

With the completion of Stage 03, Milestone 1 (Foundation: "Know what you have") is fully achieved.

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Data Dictionary CSV | `docs/04-reports/data-dictionary.csv` | committed |
| Zeek Schema Report | `docs/04-reports/zeek-schema.md` | committed |
| Schema Code Module | `src/iot23/schema.py` | committed |
| Stage Note | `docs/02-stages/stage-03-schema.md` | this file |
| Gate Test | `tests/gates/test_stage_03_gate.py` | committed |

---

## The numbers

| Metric | Value |
|---|---|
| Total Fields in Schema | 23 |
| Native Zeek Fields | 21 |
| Analyst Annotation Fields | 2 (`label`, `detailed-label`) |
| Metric Columns | 8 |
| Identifier Columns | 5 |
| Missing-value token | `-` (dash) |
| Delimiter | `\t` (ASCII 0x09) |
| Invariant 2 Status | Verified (Labels treated as immutable targets) |

---

## Milestone 1 Completion Summary

Milestone 1 Foundation (`v1-inspected`) consists of Stages 00–03:
- **Stage 00 (Project Definition):** Project brief, scope boundaries, deferred items, non-goals, and repository constitution.
- **Stage 01 (Acquisition & Integrity):** Provenance check against Stratosphere DOI (10.5281/zenodo.4743746), file registry of 18 captures, Invariant 1 verified.
- **Stage 02 (Raw Inventory):** Full capture manifest mapping 18 files to CTU scenario IDs, 44,311,939,884 bytes accounted for.
- **Stage 03 (Zeek Schema):** 23-column data dictionary, Zeek tab delimiter, missing value token `-`, Invariant 2 verified.
