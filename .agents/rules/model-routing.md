---
trigger: always_on
description: "How to choose a model for each task class, and how to fall back to Gemini 3.8 Flash when the better models are exhausted, without ever weakening a gate."
---

# Model routing

Model choice is an optimisation. It is never a reason to skip a gate, shorten a review, or let a weaker model approve its own work.

## Route by task class

| Task class | What it covers | Chain |
|---|---|---|
| `build` | implementing a stage, writing gate tests, running Kaggle kernels | strongest available, then Flash |
| `review` | manager review of a PR | strongest available, then Flash |
| `verify` | tester independent verification | strongest available, then Flash |
| `docs` | stage notes, changelog, formatting | Flash |
| `mechanical` | renames, manifest regeneration, lint fixes | Flash |

The chain lives in `autopilot/policy.yaml`. Read it; do not invent a slug.

## The fallback rule

1. Walk the chain top to bottom.
2. Skip any model the account does not expose (`agy models` is the authority).
3. Skip any model that is cooling down after a quota or rate-limit error.
4. Use the first that qualifies.
5. If everything above the floor is exhausted, use **Gemini 3.8 Flash** — `gemini-3.8-flash-medium` by default. It is the floor and it is never removed from the policy.
6. If the floor is also cooling down, stop the run. Do not silently wait, and do not pretend the work happened.

## Never

- Hardcode a model slug inside a prompt or a rule. Slugs change; the policy is the single source of truth.
- Pass `--model` after `-p`. In headless mode `-p` swallows the next argument, so a trailing `--model` is silently ignored and the run falls back to the default model — with exit code 0.
- Downgrade a `verify` turn to a cheaper model to save budget. The independent check is the one place a weaker model costs more than it saves.
- Change the `model` field of an agent in `.agents/agents/` to a full slug. Antigravity accepts only a tier (`inherit`, `flash_lite`, `flash`, `pro`) and silently skips the whole file otherwise.

## Record it

Every turn records the model used in `autopilot/logs/` and in the state history. When a stage is merged on a fallback model, say so in the PR. A result produced by Flash 3.8 instead of a Pro model is still a result — but the record must show which model produced it.
