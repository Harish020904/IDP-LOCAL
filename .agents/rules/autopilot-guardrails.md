---
trigger: always_on
description: "Limits on the autopilot itself: what it may automate and what stays human, and the rule that the core project rules cannot be changed mid-run."
---

# Autopilot guardrails

The autopilot runs the project unattended. These are its limits.

## The core rules are immutable during a run

`AGENTS.md`, `.agents/rules/*.md`, `.agents/hooks.json` and the gate checks in
`autopilot/autopilot.py` define what "done" means. The autopilot may not:

- edit any file under `.agents/`
- edit `AGENTS.md`
- edit `autopilot/policy.yaml` to widen a chain in order to get past a failure
- edit the gate functions in `autopilot.py`
- disable a hook, or pass `--dangerously-skip-permissions` to get past a deny

If a rule is genuinely wrong, stop the run and raise it. A rule changed by the process it constrains is not a rule.

## What is automated

- choosing the next stage and phase
- delegating build, review and verify to the three agents
- routing between models as budget allows
- checking the gates against files on disk
- merging a stage PR into `EDL-Pipeline` when both keys agree
- running audit passes indefinitely until the model budget is exhausted
- writing the state, the log and the model ledger

## Endless mode

`--until-exhausted` keeps the driver working after stage 12 by re-verifying every stage.
It may not:

- invent a stage, or renumber one
- skip a gate because the stage "already passed once"
- merge anything in an audit pass that has nothing to merge
- treat quota exhaustion as a failure — it is the intended stop condition
- keep retrying a cooling model; the router falls down the chain and then stops

The natural end of an endless run is exit code 3: every model, floor included, is
cooling. Anything else ending the run is a defect, a block, or a cap.

## What stays human

- **Any S1 defect.** The pipeline halts and waits. It does not attempt a fix.
- **The attempt cap.** After the configured number of rework rounds, a human looks.
- **Scope changes.** New stages, dropped deliverables, reordered milestones.
- **Publishing.** Making a Kaggle dataset public is a human decision, every time.
- **The milestone PR.** `EDL-Pipeline` → `main` is opened and merged by a person, never by the autopilot.
- **The first authenticated session.** Headless mode uses cached credentials; the first `agy` run must be interactive.

## The gates are code, not opinions

A model may claim anything. The driver merges only when:

1. the manager's decision is `approve`
2. the tester's verdict is `PASS` or `PASS WITH CONDITIONS`
3. `s1 == 0` and `s2 == 0`
4. `docs/03-reviews/stage-NN-review.md` exists and contains `VERDICT: PASS`
5. the worktree is clean
6. CI is green on the PR

No prompt, no agent and no rule can relax this list. Only a human editing `autopilot.py` can, and that edit is visible in the diff.

## Exit 0 does not mean the work happened

In headless mode a tool that needs approval is **soft-denied**: the run continues, exits 0, and prints a notice to stderr. The driver treats a soft-deny as a failed turn and stops. Never read exit 0 as success on its own.

## Stop conditions

The run halts, with the reason written to `autopilot/state.json`, when: an S1 is reported, the attempt cap is reached, a merge gate fails, every model including the floor is cooling down, or a tool was soft-denied.
