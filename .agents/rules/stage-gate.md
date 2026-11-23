---
trigger: model_decision
description: "How a stage is proven complete: gate tests, the evidence pack, and the Definition of Done. Use when implementing, reviewing or verifying any of the thirteen IoT-23 stages."
---

# The stage gate

A stage is complete when three things are true, not two:

1. The artifact exists — the manifest, the audit report, the Parquet dataset, whatever the stage produces.
2. The gate tests pass **on real data, in a Kaggle kernel** — not just the fast suite on the sample capture.
3. A second and third agent have looked — the tester verified independently, the manager reviewed and merged.

"It looked fine when I ran it" is not evidence.

## Gate tests

One file per stage: `tests/gates/test_stage_NN_gate.py`. Test names read like the exit criteria, so a review comment maps to a test.

Every gate test must be capable of failing. Reject:

- `assert df.shape[0] > 0`
- `assert True`
- a test that catches exceptions and passes
- a test asserting the implementation rather than the guarantee

## The three tests that matter most

**Reconciliation identity** — every raw row is kept or attributable to a logged operation.

```
raw_rows == cleaned_rows + removed_rows        # exactly, and per scenario
```

**Scenario disjointness** — the entire generalisation claim rests on this.

```
for a, b in combinations(partitions, 2):
    assert partitions[a] & partitions[b] == set()
```

**No-balancing guard** — Stage 12 is a reporting stage; it must not change a single row count.

```
assert stage11_counts == final_counts
```

## The evidence pack

Five items, attached to every stage PR:

1. Full-suite test output from the Kaggle run, with the command.
2. The numbers: row counts, class counts, checksums. They must match the committed reports exactly.
3. The artifact: committed report, manifest or spec — by path, never pasted.
4. The stage note in `docs/02-stages/`.
5. The ADR, if the stage made an irreversible choice.

A PR without the pack is not reviewable, however good the work is.

## Definition of Done

- deliverables exist and are committed
- every gate test passes, and the full suite passed on real data on Kaggle
- the evidence pack is attached
- the stage note and any ADR are written
- the tester's verdict is not FAIL
- the manager has merged and closed the issue
- the status board and changelog are updated
- the version tag is pushed if the stage closes a milestone

## Definition of Ready

Before a stage starts: the stage number and brief section are named, acceptance criteria are copied into the issue, evidence items are listed, the tester is assigned, dependencies are merged, and the manager has said start.
