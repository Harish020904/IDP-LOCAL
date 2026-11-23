---
name: kaggle-run
description: Runs a pipeline stage on Kaggle. Pushes a stage notebook as a Kaggle kernel, polls until it finishes, pulls back only the small outputs, and versions any large data output as a new Kaggle Dataset version. Use whenever a stage needs to execute against the real dataset, or when a kernel must be re-run after a fix.
---

# kaggle-run

The dataset is on Kaggle. This skill is how work actually executes.

## Preflight

Check these once per session, and stop with a clear message if any fails:

```bash
test -f ~/.kaggle/kaggle.json || echo "MISSING: run 'kaggle auth login' or place kaggle.json"
kaggle --version
kaggle datasets list -m | head -3        # proves auth works
echo "${KAGGLE_USERNAME:-$(python -c 'import json,os;print(json.load(open(os.path.expanduser("~/.kaggle/kaggle.json")))["username"])')}"
```

Never print the API key. Never `cat ~/.kaggle/kaggle.json`. Never commit it.

## Kernel metadata

Every stage notebook directory contains a `kernel-metadata.json` next to the `.ipynb`:

```json
{
  "id": "<KAGGLE_USERNAME>/iot23-stage-06-cleaning",
  "title": "IoT23 Stage 06 Cleaning",
  "code_file": "stage-06-cleaning.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_tpu": false,
  "enable_internet": true,
  "dataset_sources": ["<KAGGLE_USERNAME>/iot23-raw"],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

Rules:

- `id` must be `<username>/<slug>`, lowercase, hyphens only. The slug matches the notebook name.
- `dataset_sources` lists the datasets to mount at `/kaggle/input/`. Raw for stages 0–5; raw plus the previous stage's output for later stages.
- `enable_internet: true` only when the notebook installs packages or clones the repo. Leave it off otherwise — a kernel that cannot reach the network is a kernel that cannot leak data.
- `is_private: true` always, until the manager decides otherwise.
- Never edit `id` after the first push. A changed id creates a second kernel and orphans the run history.

## The run loop

```bash
# 1. Push (creates the kernel on the first push, updates it afterwards)
kaggle kernels push -p notebooks/stage-06-cleaning/

# 2. Poll. KernelQueue -> KernelRunning -> KernelComplete | KernelError
kaggle kernels status <KAGGLE_USERNAME>/iot23-stage-06-cleaning

# 3. Pull the outputs, small files only
kaggle kernels output <KAGGLE_USERNAME>/iot23-stage-06-cleaning -p out/stage-06/

# 4. Read the log before reading the numbers
tail -50 out/stage-06/run.log
```

Or use the wrapper, which does all four with backoff:

```bash
bash .agents/skills/kaggle-run/scripts/kaggle_run.sh 06
```

## Failure handling

| Status / symptom | Meaning | Action |
|---|---|---|
| `KernelError` | The notebook raised | Read `run.log` from the pulled output; fix; re-push. Do not guess from the status alone |
| Still `KernelRunning` past the budget | Long stage, or a hang | Check the log for progress lines; if it is genuinely long, split the stage by scenario and re-run |
| `403` / `401` | Auth or ownership | Check `kaggle.json`, and that `dataset_sources` datasets are yours or public |
| Dataset not found in `/kaggle/input` | Slug wrong, or the dataset version not attached | `kaggle datasets list -m` to confirm the slug; add it to `dataset_sources` |
| Out of disk | Intermediates not cleaned per scenario | Delete intermediates between scenarios inside the notebook |

Never re-push the same failing notebook without a change. Two identical failures means the diagnosis is wrong, not that it was unlucky.

## Publishing a data output

A kernel's disk dies with the run. Anything the next stage needs must be published as a **new dataset version** before the run ends.

Two ways, in order of preference:

**A. Publish from the kernel** (preferred — no download, no re-upload):

```python
# inside the notebook, after writing the output
import json, subprocess
subprocess.run(["kaggle", "datasets", "version", "-p", "/kaggle/working/prepared",
                "-m", "V3 preprocessed", "--dir-mode", "zip"], check=True)
```

This requires the dataset to already exist and the kernel to be running as the owning account with internet enabled.

**B. Publish from the laptop** — only for small outputs:

```bash
kaggle datasets version -p data/prepared -m "V3 preprocessed" --dir-mode zip
```

`--dir-mode zip` keeps the directory structure intact. Kaggle unpacks archives on upload, so the structure a consumer sees is the structure you uploaded — verify it with `kaggle datasets files <owner/slug>` after the first version.

## Version discipline

| Version | Dataset B state | Gate |
|---|---|---|
| V0 | original (Dataset A, never overwritten) | PR-002 checksums |
| V1 | inspected | PR-004 |
| V2 | audited and cleaned | PR-007 |
| V3 | preprocessed and partitioned | PR-010 |
| V4 | manifests final | PR-009 + PR-011 |
| V5 | validated | PR-012, PR-013, PR-014 |

Never overwrite V0. Never publish a version before its gate PR is merged. Every version message names the PR that produced it: `-m "V3 preprocessed (PR #10)"`.

## Chunking long runs

Twenty-three captures will not always fit in one kernel run. When a stage is too long:

1. Loop over scenarios inside the notebook, writing one output file per scenario.
2. Delete that scenario's intermediates before the next iteration.
3. Write a progress line per scenario to `run.log` so a timeout is diagnosable.
4. Make the notebook resumable: skip a scenario whose output file already exists and is valid.
5. If it still does not fit, split into one kernel per scenario group and merge in a final small kernel.

## What comes back, and what stays

**Comes back and is committed:** `reports/*.md`, `manifests/*.csv` under 5 MB, `figures/*.png`, `checksums.txt`, `run.log`.

**Stays on Kaggle:** Parquet files, the cleaned dataset, the partitions, anything over 20 MB.

A PR whose diff contains a Parquet file is a rejected PR.

## Verify before you trust

After pulling outputs, check the checksum file against what the notebook claimed:

```bash
cd out/stage-06 && sha256sum -c checksums.txt
```

A run that reports success but whose checksums do not verify did not succeed.
