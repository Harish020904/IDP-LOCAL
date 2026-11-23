## Stage
Stage NN — <name> · Issue: #NN · Milestone: M1/M2/M3/M4

## What this PR does
<!-- Two sentences. What artifact now exists that did not before. -->

## Evidence pack
- [ ] Full gate-suite log from the Kaggle run, attached (`out/stage-NN/run.log`)
- [ ] Numbers table below, matching the committed reports exactly
- [ ] Artifact committed: `docs/04-reports/...`
- [ ] Stage note: `docs/02-stages/stage-NN-*.md`
- [ ] ADR, if an irreversible choice was made: `docs/01-decisions/ADR-*.md`

| Measure | Value |
|---|---|
| Raw rows | |
| Removed (logged) | |
| Cleaned / output rows | |
| Reconciliation | exact / difference <n> |
| Rare labels retained | n of n |
| Checksum (run 1 = run 2) | |

## Kaggle run
- Kernel: `<KAGGLE_USERNAME>/iot23-stage-NN`
- Status: complete · Runtime: <m>
- Output dataset version published: V<n> (or "none — reports only")

## Acceptance criteria (copied from build-guide.md §5.2)
- [ ] criterion 1 → `tests/gates/test_stage_NN_gate.py::test_...`
- [ ] criterion 2 → `tests/gates/test_stage_NN_gate.py::test_...`

## Invariants
- [ ] Raw archive checksum unchanged
- [ ] Original labels preserved
- [ ] No balancing applied
- [ ] No scenario crosses a partition
- [ ] Nothing fitted outside the training partition

## Risk and reversibility
<!-- What could this break? Can it be undone? Does it weaken an invariant? -->

## Tester
- [ ] Routed to tester
- [ ] Verdict received: PASS / PASS WITH CONDITIONS / FAIL
