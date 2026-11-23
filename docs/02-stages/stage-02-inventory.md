# Stage 02 — Raw Dataset Inventory

**Stage:** 02  
**Milestone:** M1 Foundation  
**Branch:** `stage/02-inventory` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 02 creates the canonical raw dataset inventory and capture manifest. It catalogs all 18 captures present in Dataset A (`harishragavender0209/iot-23-raw`), maps file names to official Stratosphere scenario IDs (`CTU-IoT-Malware-Capture-*` and `CTU-Honeypot-Capture-*`), measures byte allocations, and provides an importable programmatic interface in `src/iot23/inventory.py`.

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Capture Manifest CSV | `docs/04-reports/capture-manifest.csv` | committed |
| Raw Inventory Report | `docs/04-reports/raw-inventory.md` | committed |
| Inventory Programmatic Module | `src/iot23/inventory.py` | committed |
| Stage Note | `docs/02-stages/stage-02-inventory.md` | this file |
| Gate Test | `tests/gates/test_stage_02_gate.py` | committed |

---

## The numbers

| Metric | Value |
|---|---|
| Total Captures Mapped | 18 |
| Malicious Scenarios | 15 (44,311,678,060 bytes) |
| Benign Scenarios | 3 (261,824 bytes) |
| Total Uncompressed Size | 44,311,939,884 bytes |
| Largest Capture | `8.labeled` (10,885,361,439 bytes) |
| Smallest Capture | `benign-honeypot3.labeled` (18,024 bytes) |
| Scenario Attribution | 100% of captures mapped to official CTU scenario identifiers |

---

## Gate test design

`tests/gates/test_stage_02_gate.py` asserts:
1. `capture-manifest.csv` exists, contains headers, and contains exactly 18 rows.
2. `raw-inventory.md` exists and contains correct storage metrics.
3. `load_capture_manifest` correctly loads and parses integers.
4. Total byte sum equals 44,311,939,884 bytes and file count equals 18.
5. Scenario mapping matches canonical CTU naming convention.
