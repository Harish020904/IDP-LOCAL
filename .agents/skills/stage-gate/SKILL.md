---
name: stage-gate
description: Proves a stage is complete. Runs the gate tests for a stage on Kaggle, collects the five-item evidence pack, and writes the stage note. Use when finishing a stage, before raising the pull request, or when checking whether a stage may be closed.
---

# stage-gate

A stage is not finished when the notebook runs. It is finished when the gate tests pass on real data and the evidence pack exists.

## Step 1 — find the criteria

Open `docs/build-guide.md` §5.2 and read the block for this stage. It lists the deliverables, the gate tests, the evidence, and the "done when" sentence.

Copy the acceptance criteria verbatim into the issue if they are not already there. Paraphrased criteria are how a stage gets built against the wrong requirement.

## Step 2 — map every criterion to a test

For each criterion, there must be a test in `tests/gates/test_stage_NN_gate.py` whose name says what it checks.

```
criterion: "no scenario crosses a partition boundary"
test:      test_no_scenario_appears_in_two_partitions
```

If a criterion has no test, the stage is not done. If a test cannot fail, delete it and write one that can.

## Step 3 — run the gate suite on Kaggle

The full suite needs the real data, so it runs in a kernel — never locally.

```bash
# in the stage notebook's final cell
!pytest tests/gates -m "fast or full" -v --tb=short | tee /kaggle/working/run.log
```

Then pull the log with `kaggle-run`. CI runs only `-m fast` on the committed sample capture; that is a smoke test, not the gate.

## Step 4 — assemble the evidence pack

| # | Item | Where it comes from |
|---|---|---|
| 1 | Full-suite log from the Kaggle run | `out/stage-NN/run.log` |
| 2 | The numbers table | reports + manifests |
| 3 | The committed artifact | `docs/04-reports/` |
| 4 | The stage note | `docs/02-stages/stage-NN-*.md` |
| 5 | The ADR, if irreversible | `docs/01-decisions/` |

The numbers table is the part reviewers actually read. Make it exact:

| Measure | Value |
|---|---|
| Raw rows | |
| Removed (logged) | |
| Cleaned rows | |
| Reconciliation | exact / difference <n> |
| Rare labels retained | n of n |
| Output checksum (run 1 = run 2) | |

## Step 5 — write the stage note

Headings, in this order:

```
# Stage NN — <name>
## Objective            — one sentence from the brief
## What I did           — the operations, in order
## What I found         — the numbers, and what surprised me
## What I did NOT do     — the plausible options deliberately rejected, with reasons
## Evidence             — links to reports, manifests, gate tests
## Open questions       — anything the next stage must know
```

The "what I did NOT do" section is not optional. In a dataset project, the decisions not taken are half the reasoning.

## Step 6 — hand over

Stage note committed, evidence pack in the PR body, PR raised. Then stop. You do not merge and you do not declare the stage complete.

## Stage-specific reminders

- **Stage 5** is the one where a weak audit costs the most later. Every finding needs a decision, and every decision must survive the brief's "do not do blindly" table.
- **Stage 8** is the one where a mistake is invisible until evaluation. The disjointness test is the whole guarantee.
- **Stage 9** is the one where leakage hides. Every parameter must record `fit_source = train`.
- **Stage 11** is the one that must be reproducible. Run it twice; compare checksums.
- **Stage 12** is a reporting stage. If a row count changes, something is wrong.
