---
trigger: always_on
description: "Where compute happens. The dataset lives on Kaggle; the laptop is a control plane and must never process the data."
---

# Compute placement

## The rule

The laptop is a **control plane**. Kaggle is the **compute and storage plane**.

- Every operation over the data runs inside a Kaggle kernel.
- Only small outputs return to the laptop: reports, manifests, checksums, figures, row counts.
- Never download the dataset. Never download Parquet. Never pull the full data to "just check something".

## Why

The dataset is roughly 21 GB compressed and larger extracted. This machine has 12 GB of RAM and 250 GB of disk. It cannot hold the dataset plus intermediates, and a laptop is not a reproducible compute environment. Kaggle is both, and it is where the published dataset has to live anyway.

The separation is the same one a company makes between a developer workstation and a build farm.

## What this means in practice

| Task | Where |
|---|---|
| Count rows per capture | Kaggle kernel |
| Profile a column | Kaggle kernel |
| Clean, transform, split | Kaggle kernel |
| Run gate tests on real data | Kaggle kernel |
| Read a 40-line report | locally, fine |
| Edit a notebook or `src/` | locally, fine |
| `git`, `gh`, `agy` | locally, fine |

## Output discipline

A kernel's output folder is the only thing that comes back. Keep it small and deliberate:

```
out/stage-NN/
├── reports/      # markdown, csv under 5 MB
├── manifests/    # csv, one row per scenario or per operation
├── figures/      # png
├── checksums.txt
└── run.log
```

If an output file is larger than 20 MB it does not belong in git. Commit the checksum and the row count instead.

## Kaggle runs are ephemeral

A kernel's disk is destroyed when the run ends. Anything the next stage needs must be published as a new **Kaggle Dataset version** before the run finishes. That is the checkpoint, and it is also the release mechanism (V0–V5).
