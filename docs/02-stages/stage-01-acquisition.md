# Stage 01 — Dataset Acquisition and Integrity Verification

**Stage:** 01  
**Milestone:** M1 Foundation  
**Branch:** `stage/01-acquisition` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 01 formally establishes the acquisition and integrity baselines for Dataset A (`harishragavender0209/iot-23-raw`). It validates the provenance of the raw data against the official Stratosphere Laboratory publication (DOI: 10.5281/zenodo.4743746), records exact byte sizes for all 18 captures, implements reusable verification tooling in `src/iot23/integrity.py`, and enforces Invariant 1 (raw data is read-only).

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Source & Integrity Report | `docs/04-reports/source-integrity.md` | committed |
| Raw Checksum / Size Registry | `docs/04-reports/raw-checksums.sha256` | committed |
| Integrity Code Module | `src/iot23/integrity.py` | committed |
| Stage Note | `docs/02-stages/stage-01-acquisition.md` | this file |
| Gate Test | `tests/gates/test_stage_01_gate.py` | committed |

---

## The numbers

| Measure | Value |
|---|---|
| Total Raw Files Accounted For | 18 |
| Malicious Capture Files | 15 |
| Benign Honeypot / Normal Files | 3 |
| Total Uncompressed Size | 44,311,939,884 bytes (~44.31 GB) |
| Smallest File | `benign-honeypot3.labeled` (18,024 bytes) |
| Largest File | `8.labeled` (10,885,361,439 bytes) |
| Missing or Corrupted Files | 0 |
| Invariant 1 Status | Verified (Read-only copy on Kaggle) |

---

## Gate test design

`tests/gates/test_stage_01_gate.py` checks:
1. `source-integrity.md` exists and contains correct DOI, URL, and Dataset A slug.
2. `raw-checksums.sha256` exists and accounts for all 18 files.
3. `src/iot23/integrity.py` correctly calculates total bytes and file counts.
4. Verification function rejects invalid file sizes and correctly validates canonical sizes.
5. Invariant 1 is enforced: Dataset A is declared read-only and immutable.
