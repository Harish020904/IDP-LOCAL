# Dataset Sources

This file is the single source of truth for all Kaggle dataset references used in this project.
Every kernel metadata file and every pipeline notebook must use these exact slugs.

---

## Dataset A — Raw Original (read-only)

| Property | Value |
|---|---|
| Kaggle slug | `harishragavender0209/iot-23-raw` |
| URL | https://www.kaggle.com/datasets/harishragavender0209/iot-23-raw |
| Mounted at (kernel) | `/kaggle/input/iot-23-raw/` |
| Status | **Never modified. Never re-uploaded. Treated as immutable.** |
| Uploaded | 2026-03-03 |

### Confirmed files (18 labeled captures)

| File | Size (bytes) |
|---|---|
| `2.labeled` | 3,070,319,722 |
| `3.labeled` | 853,630,635 |
| `4.labeled` | 531,738,215 |
| `5.labeled` | 31,179 |
| `6.labeled` | 9,363,261,631 |
| `7.labeled` | 585,829 |
| `8.labeled` | 10,885,361,439 |
| `9.labeled` | 1,787,852,355 |
| `10.labeled` | 1,340,179,107 |
| `11.labeled` | 3,019,311 |
| `12.labeled` | 7,867,920,121 |
| `13.labeled` | 428,943 |
| `14.labeled` | 419,604 |
| `15.labeled` | 8,139,370,158 |
| `benign.labeled` | 61,653 |
| `benign-honeypot2.labeled` | 182,147 |
| `benign-honeypot3.labeled` | 18,024 |
| `conn.log.labeled` | 467,559,811 |

Total: 18 files. Sizes recorded 2026-11-23 from `kaggle datasets files`.

---

## Dataset B — Prepared (versioned outputs)

| Property | Value |
|---|---|
| Kaggle slug | `harishragavender0209/iot23-prepared` *(to be created at M1)* |
| Mounted at (kernel) | `/kaggle/input/iot23-prepared/` |
| Versions | V0 placeholder → V1 (M1) → V2 (M2) → V3 (M3) → V5 (M4) |

---

## Kernel metadata `dataset_sources` field

Every `kernel-metadata.json` in this project must include Dataset A:

```json
"dataset_sources": ["harishragavender0209/iot-23-raw"]
```

Stages that also read from Dataset B add it second:

```json
"dataset_sources": [
  "harishragavender0209/iot-23-raw",
  "harishragavender0209/iot23-prepared"
]
```

---

## Attribution

Garcia, S., Parmisano, A., & Erquiaga, M. J. (2020). IoT-23: A labeled dataset with malicious
and benign IoT network traffic (Version 1.0.0). Stratosphere Laboratory.
https://doi.org/10.5281/zenodo.4743746
