# IoT-23 Dataset Engineering — rules for every agent

This file is loaded into every conversation, in every agent, on every turn. It is the project constitution. Everything else in `.agents/` adds detail; nothing here is optional.

---

## 1. What this project is

Prepare the **IoT-23** labelled network-flow dataset (Stratosphere Laboratory, v1.0.0) into a reproducible, scenario-partitioned, research-grade dataset, in thirteen stages (0–12), with every transformation documented and every claim provable.

The deliverable is not a model. It is a **documented, reproducible dataset pipeline** whose output another researcher can regenerate.

---

## 2. The three planes

| Plane | Machine | Holds |
|---|---|---|
| **Control** | Arch Linux laptop (`harish`) | `agy` CLI, git, the Obsidian vault, the Kaggle CLI. Code, docs, manifests, small reports. **No dataset.** |
| **Compute** | Kaggle notebooks (kernels) | Every scan, count, join, transform, and test that touches the data. |
| **Storage** | Kaggle Datasets | Dataset A — untouched original. Dataset B — prepared outputs, versioned V0–V5. |

## 3. Hard rule: the data never touches the laptop

- Never run a pipeline stage locally. Never download the dataset to the laptop to "just check something".
- Every operation over the data happens inside a Kaggle kernel and is pushed with the Kaggle CLI.
- Only **small outputs** come back to the laptop: reports, manifests, checksums, figures, row counts. Never Parquet, never CSVs of the full data.
- If a task requires reading more than a few thousand rows, it belongs in a kernel.

Rationale: 12 GB of RAM and 250 GB of disk cannot hold a 21 GB dataset plus intermediates, and a laptop is not a reproducible compute environment. Kaggle is both. This is the same separation a company makes between a developer workstation and a build farm.

---

## 4. The agents

| Agent | Invoke it when | It may | It may not |
|---|---|---|---|
| **manager** | a PR needs review, a stage needs assigning, a verdict has arrived | read, run git/gh, comment, approve, merge | write pipeline code, merge without a tester verdict |
| **data-engineer** | a stage is assigned and needs building | read, edit, run commands, push kernels, raise PRs | merge, approve its own work |
| **tester** | a PR is ready for independent verification | read, run queries, run tests, write its review file | edit pipeline code, merge, fix defects |

Nobody merges their own work. The manager is the only merger, and only when both keys agree (manager review + tester verdict).

---

## 5. Where everything lives

| Thing | Path |
|---|---|
| Repository | `/home/harish/IDP-LOCAL` (override with `$IDP_REPO`) |
| Obsidian vault (the second brain) | `/home/harish/obsidian/IoT23 Dataset` (override with `$IDP_VAULT`) |
| Stage plan | `docs/00-project/brief.md` |
| Process rules | `docs/build-guide.md`, `docs/manager.md`, `docs/data-engineer.md`, `docs/tester.md` |
| Stage notes | `docs/02-stages/stage-NN-*.md`, mirrored into the vault |
| Generated reports | `docs/04-reports/` |
| Decisions (ADRs) | `docs/01-decisions/` |
| Reviews | `docs/03-reviews/` |
| Pipeline code | `src/iot23/` |
| Stage notebooks | `notebooks/stage-NN-*.ipynb` + `notebooks/stage-NN-kernel-metadata.json` |
| Tests | `tests/unit/`, `tests/gates/` |
| Kaggle credentials | `~/.kaggle/kaggle.json` — never committed, never echoed |

The Obsidian vault is the **human-readable** brain. Git is the **machine-readable** record. They are kept in sync by `sync-brain`; the vault is never the only copy of anything.

---

## 6. The stage plan

Thirteen stages, four milestones, one notebook and one PR each. Stage numbers are fixed; do not renumber, merge or skip stages.

| Milestone | Stages | Theme | Tag |
|---|---|---|---|
| M1 Foundation | 0, 1, 2, 3 | Know what you have | `v1-inspected` |
| M2 Understanding | 4, 5 | Prove what is wrong with it | `v2-audited` |
| M3 Transformation | 6, 7, 8, 9 | Change it deliberately | `v3-transformed` |
| M4 Product | 10, 11, 12 | Prove it, reproduce it, publish it | `v5-validated` |

Gate criteria per stage: `docs/build-guide.md` §5.2. Gate tests: `tests/gates/test_stage_NN_gate.py`.

---

## 7. The ten invariants

These hold in every stage, in every agent, at all times. Violating one is an S1 defect.

1. **Raw data is read-only.** The original archive is never modified, moved or re-extracted in place. Its SHA-256 is verified in every stage that touches data.
2. **Original labels are never silently changed.** Corrections go in a new column with a logged reason.
3. **No balancing.** No SMOTE, no oversampling, no undersampling, no synthetic flows, no minority deletion — anywhere in this project. Stage 12 *documents* the imbalance.
4. **No capture scenario crosses a partition boundary.** Whole scenarios only. If a label exists in one capture, that limitation is documented, not engineered around by splitting the capture.
5. **Nothing is fitted outside training data.** Imputation values, scaling parameters, encoders, category frequencies — training partition only, then applied unchanged.
6. **Every removed row is attributable** to a numbered operation in the cleaning log.
7. **Every number in a report is reproducible** from a committed script or notebook.
8. **Every change is reviewed before it reaches `main`.** Branch, PR, review, merge. No direct pushes.
9. **A PR without its evidence pack is not reviewable**, however good the work is.
10. **A decision that cannot be undone cheaply gets an ADR before it is implemented**, not after.

---

## 8. Command cheat sheet

```bash
# Kaggle — the only way data gets processed
kaggle kernels push   -p notebooks/stage-06-cleaning/
kaggle kernels status <KAGGLE_USERNAME>/iot23-stage-06
kaggle kernels output <KAGGLE_USERNAME>/iot23-stage-06 -p out/stage-06/
kaggle datasets version -p data/prepared -m "V3 preprocessed" --dir-mode zip

# Git — the only way work reaches main
git switch -c stage/06-cleaning
gh pr create --fill
gh pr merge --squash

# Brain
bash .agents/skills/obsidian-sync/scripts/sync_brain.sh
```

Full detail: skill `kaggle-run`. Setup: `KAGGLE-COMPUTE.md`.

---

## 9. What never enters git

`data/`, `*.parquet`, `*.pcap`, `*.zip`, `out/`, `.venv/`, `~/.kaggle/kaggle.json`, any credential, any file over 20 MB except committed figures.

What does enter git: checksums, manifests, row counts, reports, figures, notebooks, `src/`, `tests/`, ADRs, stage notes.

---

## 10. Writing style for anything you produce

- Numbers, not adjectives. "2,831,004 rows retained, 16,297 removed across 14 logged operations" — not "cleaning went well".
- Every claim traceable to a file, a command, or a test name.
- State what you did **not** do and why, when it was a plausible alternative.
- If you could not verify something, say so explicitly rather than omitting it.
- No emojis. No exclamation marks. Prose over bullets in stage notes.
