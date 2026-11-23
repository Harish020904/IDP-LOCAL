# Stage 00 — Project Definition

**Stage:** 00  
**Milestone:** M1 Foundation  
**Branch:** `stage/00-definition` → PR → `EDL-Pipeline`  
**Date:** 2026-11-23  
**Author:** data-engineer  
**Status:** complete — pending review

---

## What this stage does

Stage 0 is a documentation-only stage. No data is read. No notebook runs on Kaggle. The entire stage lives on the control plane.

The deliverable is a committed project brief (`docs/00-project/brief.md`) and a scope document (`docs/00-project/scope.md`). These two files define the problem precisely enough that every subsequent stage can be built against them without ambiguity.

---

## What was produced

| Artifact | Path | Status |
|---|---|---|
| Project brief | `docs/00-project/brief.md` | committed |
| Scope document | `docs/00-project/scope.md` | committed |
| Dataset source registry | `docs/00-project/dataset-sources.md` | committed (previous commit) |
| Stage note | `docs/02-stages/stage-00-definition.md` | this file |
| Gate test | `tests/gates/test_stage_00_gate.py` | committed |

---

## Numbers

No row counts. This stage produces no data artifact. The deliverables are documentation files verified by their existence and content, not by data properties.

---

## What the brief establishes

The brief (`docs/00-project/brief.md`) commits the following facts, which every later stage must treat as fixed:

1. **Source dataset:** IoT-23, Stratosphere Laboratory v1.0.0. DOI: `10.5281/zenodo.4743746`. 23 captures (20 malicious, 3 benign), Zeek `conn.log` format, labelled at the flow level.
2. **Dataset A slug:** `harishragavender0209/iot-23-raw`. 18 labeled files confirmed 2026-11-23. Immutable.
3. **Research question:** Reproduce a research-grade, scenario-partitioned dataset pipeline for NIDS model evaluation, such that any researcher starting from the same Dataset A reaches the same Dataset B from the committed code alone.
4. **Stage plan:** 13 stages (0-12), fixed numbering, four milestones, as specified in `AGENTS.md §6`.
5. **Dataset versioning:** Dataset A (read-only) and Dataset B (V0 placeholder through V5 final).
6. **Three critical invariants:** No balancing at any stage. No scenario crosses a partition boundary. Nothing fitted outside the training partition.
7. **Explicit non-goals:** No model training. No inference. No evaluation on external benchmarks. No feature selection study. No synthetic data generation.

---

## What the scope document establishes

`docs/00-project/scope.md` lists five items explicitly deferred from scope, each with a reason and the condition under which it may be revisited:

1. Feature selection or dimensionality reduction
2. Alternative label granularities (collapsed or aggregated labels)
3. Additional benign capture sources
4. Temporal splitting instead of scenario-level splitting
5. Packet-level or byte-level features (requires PCAP access)

---

## What was deliberately not done

- No Kaggle kernel was created. Stage 0 produces no data artifact and requires no compute.
- No ADR was filed. No decision was made that contradicts `AGENTS.md` or that cannot be cheaply undone. The brief restates existing commitments; it does not introduce new irreversible choices.
- The cleaning log was not started. It opens in Stage 6, when the first removal operation occurs.

---

## Gate test design

`tests/gates/test_stage_00_gate.py` contains 10 tests, one per acceptance criterion. Each test checks a specific, falsifiable property of the deliverable files:

- File existence (can fail if the file is missing or misnamed)
- Heading presence (can fail if a required section is omitted)
- Content substring (can fail if a required fact, slug, or citation is absent)

No test is a tautology. Each test names the criterion it covers so the manager can map a review comment to the test that would catch the defect.

---

## Checklist

- [x] branch rebased on current `EDL-Pipeline`
- [x] `pytest tests/gates/test_stage_00_gate.py -v` passes
- [x] every acceptance criterion has a named gate test
- [x] each gate test would fail if the work were wrong
- [x] stage note complete with numbers (none applicable) not adjectives
- [x] no ADR required (no irreversible decision made)
- [x] no data, Parquet or large binary staged
- [x] no Kaggle kernel created or needed
