# Autopilot

Unattended operation of the IoT-23 pipeline: one driver, three agents, thirteen stages, and gates that a model cannot talk its way past.

```
autopilot.py ──┬─▶ data-engineer   (build)    strongest model
               ├─▶ manager         (review)   strongest model   ─┐ Key 1
               ├─▶ tester          (verify)   strongest model   ─┤ Key 2
               └─▶ gate checks in code ────────────────────────┴─▶ merge → EDL-Pipeline
                        │
                        └─▶ fallback chain ends at Gemini 3.8 Flash
```

## Two layers

**Layer 1 — the agent.** `.agents/agents/autopilot.md` is an orchestrator you can talk to. It delegates with `invoke_subagent` and follows the same state machine. Use it when you want to watch or steer.

**Layer 2 — the driver.** `autopilot/autopilot.py` is the unattended version. It calls `agy` in headless mode, one turn per phase, and never depends on a model deciding that a gate passed. Use it overnight.

Both obey the same gates. Neither can change the rules.

## Two modes

**Bounded** — build the thirteen stages in order, then stop.

```bash
python3 autopilot/autopilot.py --stage 0
python3 autopilot/autopilot.py --max-stages 3
```

**Endless** — keep working until the model budget runs out.

```bash
python3 autopilot/autopilot.py --until-exhausted
bash autopilot/run-until-exhausted.sh                     # with restart-on-transient-error
bash autopilot/run-until-exhausted.sh --max-hours 8       # with a wall-clock guard
```

In endless mode the driver does not stop after stage 12. It starts an **audit pass**: the tester re-verifies every stage from scratch, in order. A stage that re-passes advances silently with nothing to merge. A stage that fails drops back into the full `build → review → verify → merge` cycle, because a finding is a real defect and gets a real fix with a real gate. Then the next pass begins.

It stops when:

| Condition | Exit | What it means |
|---|---|---|
| every model in the chain is cooling, floor included | 3 | quota exhausted — the natural end |
| `--max-passes` reached | 0 | audit sweeps completed |
| `--max-hours` reached | 0 | wall-clock guard fired |
| S1 defect, attempt cap, merge gate failure | 4 | a human is needed |
| N consecutive failed turns | 4 | something is broken, not merely slow |

An endless run therefore burns budget on re-proving the dataset, not on inventing new work. It cannot create a stage, skip a gate, or merge something unverified — the same `gate_merge()` runs in every pass.

## Quick start

```bash
cd /home/harish/IDP-LOCAL

# 1. once: authenticate interactively (headless uses cached credentials)
agy

# 2. see what models you actually have, and how the policy maps onto them
agy models
python3 autopilot/model_router.py --discover

# 3. edit autopilot/policy.yaml so the chains name slugs your account exposes

# 4. dry run — prints the exact commands, calls nothing
python3 autopilot/autopilot.py --dry-run --stage 0 --once

# 5. bounded: one stage
python3 autopilot/autopilot.py --stage 0

# 6. endless: until the quota dies
bash autopilot/run-until-exhausted.sh
```

## The state machine

```
todo -> build -> review -> verify -> merge -> done
                    |         |
                    +---------+--> build   (rework, capped by --max-attempts)
    verify with s1 > 0                     -> blocked (S1 veto, no auto-rework)

endless mode, stage already built:  -> verify -> (pass: next stage) | (fail: build)
```

State lives in `autopilot/state.json` and is committed. Every transition, model and result is appended to `autopilot/logs/autopilot-YYYYMMDD.jsonl`.

## Merge gates — checked in code, not by a model

`autopilot.py::gate_merge` refuses to merge unless all six hold:

1. manager decision is `approve`
2. tester verdict is `PASS` or `PASS WITH CONDITIONS`
3. `s1 == 0` and `s2 == 0`
4. `docs/03-reviews/stage-NN-review.md` exists and contains `VERDICT: PASS`
5. the worktree is clean
6. `gh pr checks` is green

This is the point of the design. A model can claim anything in its JSON response; the driver only believes files on disk. `AGENTS.md` remains the single source of truth for what the rules are — the driver enforces them, it does not restate them.

## Branch model

| PR | From | Into | Who merges |
|---|---|---|---|
| Stage PR | `stage/NN-name` | `EDL-Pipeline` | the driver, after both keys |
| Milestone PR | `EDL-Pipeline` | `main` | **you**, by hand |

The driver never opens or merges a milestone PR. That is a deliberate human decision point, once per milestone.

## Model routing

`autopilot/policy.yaml` maps a task class to an ordered chain. The router:

1. reads `agy models` (the authority on what your account exposes)
2. skips anything not listed, and anything cooling down after a quota error
3. takes the first that qualifies
4. ends at the floor — **Gemini 3.8 Flash** — when everything above is exhausted

| Task class | Used by | Chain |
|---|---|---|
| `build` | data-engineer | strongest → Flash High → Flash Medium |
| `review` | manager | strongest → Flash High → Flash Medium |
| `verify` | tester | strongest → Flash High → Flash Medium |
| `docs` | notes, changelog | Flash High → Flash Medium |
| `mechanical` | renames, manifests | Flash Medium |

When a model reports exhaustion the router writes a cooldown to `autopilot/model_ledger.json` (default 300 minutes; 30 for the floor) and the **same phase retries on the next model**. Only when the floor is also cooling does the run stop, with exit 3.

```bash
python3 autopilot/model_router.py --status     # who is cooling, and why
python3 autopilot/model_router.py --reset      # clear cooldowns after your quota resets
```

## Why `--model` must come before `-p`

In headless mode `-p` swallows the argument that follows it. `agy -p "..." --model X` silently runs the default model and exits 0 — the worst kind of failure, because it looks like success. The driver always builds `agy --model X --agent Y ... -p <prompt>`.

`--model` with an unknown slug is the opposite: it hard-fails with exit 1. That is why the router validates every slug against `agy models` first.

## Why exit 0 is not success

A tool that needs approval in headless mode is **soft-denied**: the run continues, exits 0, and prints a notice to stderr. The driver greps stderr for that notice, marks the turn failed, and stops. Without this check the autopilot would report a stage as built when nothing was written.

## The hook layer

`.agents/hooks.json` runs `autopilot/hooks/hooks.py` on tool events. It does two jobs:

- **auto-approves** read-only and pipeline commands (`git status`, `pytest`, `kaggle kernels status`, `gh pr view`) so they are not soft-denied
- **hard-denies** the commands that would break a core rule, whoever runs them: force-push, push to `main`, `git reset --hard`, `--no-verify`, recursive deletes, anything writing into `data/raw`, deleting a published dataset, force-re-tagging

A plain `git push` to a stage branch or to `EDL-Pipeline` is allowed; only `main` is blocked. Every decision is logged to `autopilot/logs/hooks.jsonl`.

## What stays human

- any S1 defect — the pipeline halts and waits
- the attempt cap — after N rework rounds, a person looks
- the milestone PR `EDL-Pipeline → main`
- scope changes and stage order
- making a Kaggle dataset public
- the first authenticated `agy` session

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| exit 3, `quota exhausted` | every chain entry and the floor are in cooldown | wait for `earliest recovery`, then re-run |
| `MERGE REFUSED: review file missing` | the tester returned JSON but wrote no file | re-run the verify phase |
| `MERGE REFUSED: worktree is dirty` | uncommitted work would ride into the merge | commit or stash |
| `MERGE REFUSED: PR #N checks are not green` | CI failed on the PR | fix, push, re-run |
| stops with `soft_denied: true` | a needed command was not approved | add it to `AUTO` in `hooks.py` |
| run ends at `no transition` (exit 5) | the state machine refused to move | inspect `state.json`; usually a phase mismatch |
| model is not what you expected | `--model` placed after `-p` | the driver orders it correctly; check hand-run commands |
| agent not found | invalid frontmatter, or `model` is not a tier | `agy agents`; use `model: pro`, not a full slug |

## Files

```
autopilot/
├── autopilot.py             driver, gates, endless mode
├── model_router.py          model selection, cooldowns, Flash 3.8 floor
├── policy.yaml              chains, effort, cooldowns, floor model
├── run-until-exhausted.sh   restart wrapper
├── prompts/                 build.md, review.md, verify.md
├── hooks/hooks.py           PreToolUse guard, PostToolUse audit
├── state.json               current stage/phase/pass (committed)
├── model_ledger.json        cooldowns (gitignored)
└── logs/                    JSONL run logs (gitignored)
```
