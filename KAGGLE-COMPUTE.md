# Kaggle as the compute plane

The dataset does not live on this laptop. Kaggle runs the code, Kaggle stores the data, and the laptop holds code, notes and small reports.

```
   Arch Linux laptop  ·  harish  ·  12 GB RAM          Kaggle
   ──────────────────────────────────────              ──────
   agy  (agents)                                       kernels   ← every scan, transform, test
   git  (code + docs)                      ──push──▶
   kaggle CLI                              ◀─pull──   outputs   ← reports, manifests, checksums
   Obsidian vault                                      datasets  ← A: raw, immutable
   small reports, manifests, checksums                            ← B: prepared, V0…V5
```

## The two datasets, as they exist

| | Dataset A | Dataset B |
|---|---|---|
| Slug | `harishragavender0209/iot-23-raw` | `harishragavender0209/iot23-prepared` |
| Mount | `/kaggle/input/iot-23-raw/` | `/kaggle/input/iot23-prepared/` |
| Role | raw original, immutable | prepared outputs |
| State | uploaded 2026-03-03, 18 files | versioned V0 → V5 |

Dataset A holds the labelled flow files (`conn.log.labeled`, `8.labeled`, `6.labeled`, `15.labeled`, … `benign-honeypot3.labeled`). Dataset A is never written to, never versioned, never re-uploaded.

Dataset B moves forward at milestone boundaries:

| Version | Published at | Contents |
|---|---|---|
| V0 | already exists | placeholder, to establish the dataset |
| V1 | Stage 6 | cleaned flows |
| V2 | Stage 8 | partitioned |
| V3 | Stage 9 | preprocessed |
| V4 | Stage 10 | final Parquet |
| V5 | Stage 12 / M4 | validated, integrity proven |

## One-time setup

```bash
# Arch
sudo pacman -S python-pip unzip
pipx install kaggle          # or: pip install --user kaggle
kaggle --version
```

Token: Kaggle → Account → Settings → API → Create New Token, then:

```bash
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
kaggle datasets list -m | head      # proves auth works
```

Never commit `kaggle.json`, never echo it. It is already gitignored.

## Confirm the mounts before writing any pipeline code

```python
import os
for root, dirs, files in os.walk("/kaggle/input"):
    depth = root.count("/") - 2
    if depth <= 2:
        print("  " * depth, root, len(files), "files")
```

Expected: `/kaggle/input/iot-23-raw/` with 18 files. If the structure differs, fix the kernel metadata now — not after the capture manifest is written.

## Kernel metadata per stage

```json
{
  "id": "harishragavender0209/iot23-stage-06",
  "title": "IoT23 Stage 06 Cleaning",
  "code_file": "stage-06-cleaning.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_tpu": false,
  "enable_internet": true,
  "dataset_sources": ["harishragavender0209/iot-23-raw"],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

From Stage 7 onwards, add `"harishragavender0209/iot23-prepared"` to `dataset_sources` — that is where the previous stage's output was published.

## The daily loop

```bash
bash .agents/skills/kaggle-run/scripts/kaggle_run.sh 06      # push, poll, pull, verify
git add docs/04-reports out/stage-06/checksums.txt out/stage-06/run.log
git commit -m "feat(stage-06): cleaning with logged operations"
gh pr create --base EDL-Pipeline --fill
```

## Publishing a version

```bash
# from the laptop, for small outputs
kaggle datasets version -p data/prepared -m "V3 preprocessed (PR #10)" --dir-mode zip

# from inside the kernel, for large outputs — preferred, no download/re-upload
!kaggle datasets version -p /kaggle/working/prepared -m "V3 preprocessed" --dir-mode zip
```

Rules: never overwrite V0; never publish before the stage PR is merged; every version message names the PR; verify the uploaded structure with `kaggle datasets files harishragavender0209/iot23-prepared`.

## Chunking long runs

Twenty-three captures will not always fit one kernel run. The pipeline is built to be resumable per scenario:

- one output file per scenario, written as the loop progresses
- intermediates deleted after each scenario
- a progress line per scenario in `run.log`
- a re-run skips scenarios whose output already exists and validates

If a stage still does not fit, split it into one kernel per scenario group plus a small merge kernel. Do not raise the timeout and hope.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `403` on push | kernel id belongs to another account | `id` must start with `harishragavender0209` |
| kernel runs, `/kaggle/input` empty | dataset not in `dataset_sources`, or wrong slug | `kaggle datasets list -m` |
| output empty after success | files written outside `/kaggle/working` | write only under `/kaggle/working` |
| run killed mid-way | time or disk limit | chunk by scenario, delete intermediates |
| `datasets version` fails | dataset missing, or limits exceeded | check `kaggle datasets files`; see limits |
| same failure twice identically | the diagnosis is wrong | change the hypothesis, not the retry |

## What never happens

- the dataset is never downloaded to the laptop
- Parquet files are never committed
- a stage is never "verified" by a local run
- a kernel output is never trusted before `sha256sum -c checksums.txt` passes

## Attribution

> Garcia, S., Parmisano, A., & Erquiaga, M. J. (2020). IoT-23: A labeled dataset with malicious and benign IoT network traffic (Version 1.0.0). Stratosphere Laboratory. https://doi.org/10.5281/zenodo.4743746
