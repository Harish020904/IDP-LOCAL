# Where every file goes

Three archives, extracted into one repository. Order matters: **1, then 2, then 3** — later archives overwrite earlier ones, which is intended.

```bash
cd /home/harish/IDP-LOCAL
unzip -o ~/Downloads/IDP-LOCAL-agents.zip          -d .   # 1: the agent layer
unzip -o ~/Downloads/IDP-LOCAL-autopilot.zip       -d .   # 2: the autopilot
unzip -o ~/Downloads/IDP-LOCAL-autopilot-v2.zip    -d .   # 3: endless mode + fixes
```

Or just run `bash setup-tree.sh`, which does all of it, creates the empty directories, checks the branch and links the vault.

---

## 1. The tree, as it should end up

```
/home/harish/IDP-LOCAL/                      GitHub: Harish020904/IDP-LOCAL
│
├── AGENTS.md                                 project constitution, always loaded
├── build-guide.md  ─┐
├── manager.md       │  the five process documents from round 1
├── data-engineer.md │  → move into docs/ (see §4)
├── tester.md        │
├── README.md       ─┘
├── AUTOPILOT.md                              autopilot architecture and runbook
├── KAGGLE-COMPUTE.md                         three-plane setup and Kaggle commands
├── PLACEMENT.md                              this file
├── INSTALL.md                                agent-layer install notes
├── setup-tree.sh                             creates everything below and verifies
│
├── .agents/                                  ── ANTIGRAVITY LOADS FROM HERE ──
│   ├── hooks.json                            tool-event guard (deny + auto-approve)
│   ├── agents/
│   │   ├── manager.md                        Key 1 · reviews, merges
│   │   ├── data-engineer.md                  builds, pushes kernels, raises PRs
│   │   ├── tester.md                         Key 2 · independent verification
│   │   └── autopilot.md                      orchestrator
│   ├── rules/
│   │   ├── data-safety.md                    always_on
│   │   ├── kaggle-compute.md                 always_on
│   │   ├── model-routing.md                  always_on
│   │   ├── autopilot-guardrails.md           always_on
│   │   ├── stage-gate.md                     model_decision
│   │   └── python-conventions.md             glob: *.py, *.ipynb
│   └── skills/
│       ├── kaggle-run/SKILL.md               + scripts/kaggle_run.sh
│       ├── stage-gate/SKILL.md
│       └── obsidian-sync/SKILL.md            + scripts/sync_brain.sh
│
├── autopilot/                                ── THE DRIVER ──
│   ├── autopilot.py                          state machine, gates, merge, endless mode
│   ├── model_router.py                       model choice, cooldowns, Flash 3.8 floor
│   ├── policy.yaml                           chains, effort, cooldowns, floor model
│   ├── run-until-exhausted.sh                wrapper: run until quota dies
│   ├── prompts/
│   │   ├── build.md                          what the data-engineer is asked to do
│   │   ├── review.md                         what the manager is asked to check
│   │   └── verify.md                         what the tester is asked to prove
│   ├── hooks/hooks.py                        PreToolUse guard, PostToolUse audit
│   ├── state.json                            current stage/phase/pass (committed)
│   ├── model_ledger.json                     cooldowns (gitignored)
│   └── logs/                                 JSONL run logs (gitignored)
│
├── .github/
│   ├── CODEOWNERS
│   └── pull_request_template.md
│
├── docs/                                     ── THE SECOND BRAIN ──
│   ├── build-guide.md  manager.md  data-engineer.md  tester.md     ← from round 1
│   ├── 00-project/     brief.md  scope.md  dataset-sources.md  environment.md  glossary.md
│   ├── 01-decisions/   ADR-NNN-*.md
│   ├── 02-stages/      stage-NN-*.md            ← written in the same PR as the work
│   ├── 03-reviews/     stage-NN-review.md       ← the tester's verdict, read by the driver
│   ├── 04-reports/     cleaning-log.csv  checksums.sha256  figures/
│   └── 05-log/         changelog.md  work log
│
├── notebooks/                                stage-NN-*.ipynb + kernel-metadata.json
├── src/iot23/                                importable pipeline modules
├── tests/
│   ├── unit/                                 fast tests, sample capture, run in CI
│   ├── gates/                                test_stage_NN_gate.py — one per stage
│   └── fixtures/sample-capture/              ONE trimmed capture, committed
├── out/                                      pulled kernel outputs (gitignored)
└── data/                                     gitignored — the dataset lives on Kaggle
```

---

## 2. File-by-file

| Path | Comes from | What it does |
|---|---|---|
| `AGENTS.md` | 1 | Loaded on every turn in every agent. The ten invariants and the three planes. |
| `KAGGLE-COMPUTE.md` | 1, replaced by 3 | Kaggle CLI setup with your real slugs and mounts. |
| `INSTALL.md` | 1 | Agent-layer install and frontmatter troubleshooting. |
| `PLACEMENT.md` | 3 | This file. |
| `AUTOPILOT.md` | 2, replaced by 3 | Architecture, endless mode, runbook, troubleshooting. |
| `setup-tree.sh` | 3 | Creates the directory skeleton, extracts the archives, verifies every path. |
| `.agents/agents/manager.md` | 1 | Review checklist, merge conditions, "finished" definition. |
| `.agents/agents/data-engineer.md` | 1 | Build loop, evidence pack, data-handling rules. |
| `.agents/agents/tester.md` | 1 | Independent verification, severity, five-line verdict. |
| `.agents/agents/autopilot.md` | 2, replaced by 3 | Orchestrator: delegates to the other three, refuses to skip gates. |
| `.agents/rules/data-safety.md` | 1 | Five invariants as an always-on rule. |
| `.agents/rules/kaggle-compute.md` | 1 | "The dataset never touches the laptop." |
| `.agents/rules/stage-gate.md` | 1 | Gate tests, evidence pack, Definition of Done. |
| `.agents/rules/python-conventions.md` | 1 | Polars/DuckDB, determinism, no Pandas full-load. |
| `.agents/rules/model-routing.md` | 2 | Task class → chain, Flash 3.8 as the floor. |
| `.agents/rules/autopilot-guardrails.md` | 2, replaced by 3 | What the autopilot may automate and what stays human. |
| `.agents/skills/kaggle-run/SKILL.md` + `scripts/kaggle_run.sh` | 1 | push → poll → pull → verify checksums → version the dataset. |
| `.agents/skills/stage-gate/SKILL.md` | 1 | Run the gate suite on Kaggle, assemble the evidence pack. |
| `.agents/skills/obsidian-sync/SKILL.md` + `scripts/sync_brain.sh` | 1 | Link `docs/` into the vault. |
| `.agents/hooks.json` | 2 | Wires `hooks.py` into PreToolUse / PostToolUse / SessionStart / Stop. |
| `autopilot/autopilot.py` | 2, replaced by 3 | The driver. Endless mode lives here. |
| `autopilot/model_router.py` | 2, replaced by 3 | Model selection and cooldown ledger. |
| `autopilot/policy.yaml` | 2 | Edit this after `agy models`. |
| `autopilot/prompts/*.md` | 2, `build.md` replaced by 3 | The three phase prompts. |
| `autopilot/hooks/hooks.py` | 2, replaced by 3 | Command guard and audit log. |
| `autopilot/run-until-exhausted.sh` | 3 | Restart wrapper around `--until-exhausted`. |
| `.github/CODEOWNERS`, `pull_request_template.md` | 1 | Review ownership and the evidence-pack template. |
| `notebooks/kernel-metadata.template.json` | 1 | Copy per stage. |

---

## 3. What the archives do not create

These directories are empty on purpose — they fill up as stages run:

```bash
mkdir -p docs/{00-project,01-decisions,02-stages,03-reviews,04-reports,05-log}
mkdir -p notebooks src/iot23 tests/{unit,gates,fixtures} out data/{raw,prepared}
```

`setup-tree.sh` does this for you.

---

## 4. Move the five process documents into `docs/`

They were delivered as loose files in round 1. They belong under `docs/`, because that is where `AGENTS.md` and the rules point:

```bash
mv build-guide.md manager.md data-engineer.md tester.md README.md docs/ 2>/dev/null
```

Keep the root `README.md` if you prefer — but then keep a copy in `docs/` too, because the vault links to `docs/`.

---

## 5. Branch setup

Stage PRs target **`EDL-Pipeline`**. `main` is only updated by a milestone PR that you merge by hand.

```bash
cd /home/harish/IDP-LOCAL
git switch -c EDL-Pipeline          # create it once
git push -u origin EDL-Pipeline
```

Then, in GitHub → Settings → Branches, protect **both** branches:

| Setting | `EDL-Pipeline` | `main` |
|---|---|---|
| Require a pull request | on | on |
| Require approvals | 1 | 1 |
| Require review from Code Owners | on | on |
| Require status checks | on | on |
| Allow force pushes | off | off |
| Allow deletions | off | off |

---

## 6. Vault link

```bash
bash .agents/skills/obsidian-sync/scripts/sync_brain.sh
```

Creates `01 Stages`, `02 Decisions`, `03 Reports`, `04 Reviews`, `05 Log` inside `/home/harish/obsidian/IoT23 Dataset` as symlinks into `docs/`. Obsidian then shows the real files; git sees the same bytes.

---

## 7. Verify the placement

```bash
cd /home/harish/IDP-LOCAL
bash setup-tree.sh --verify-only
```

Expected: every line `OK`, zero `MISSING`. Then:

```bash
agy agents          # manager, data-engineer, tester, autopilot
agy                 # once, to accept the trust prompt
```

Inside the TUI: `/agents` lists four agents; `/kaggle-run`, `/stage-gate`, `/obsidian-sync` are slash commands.
