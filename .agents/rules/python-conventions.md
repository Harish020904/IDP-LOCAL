---
trigger: glob
description: "Python and notebook conventions for the IoT-23 pipeline: Polars/DuckDB over Pandas, importable code, deterministic output."
globs: "*.py, *.ipynb"
---

# Python and notebook conventions

## Libraries

- **Polars** for transformation, **DuckDB** for SQL over Parquet, **PyArrow** for Parquet I/O.
- **Do not** load the full dataset into a single Pandas DataFrame. If you reach for Pandas on more than a sample, stop.
- **Scikit-learn** only for preprocessing utilities and group-aware splitting.
- No PyTorch, TensorFlow, Transformers, CUDA, or Zeek in this project.

## Structure

- The notebook orchestrates. The logic lives in `src/iot23/` and is importable.
- A function that computes a number a report depends on must live in `src/`, not in a cell.
- Notebooks must run top to bottom with no hidden state. Re-running from a fresh kernel must reproduce the output.
- No `df.head()` as evidence. Print the number you are asserting.

## Determinism

- Set and record seeds wherever randomness exists.
- Sort before writing. Unordered output changes checksums between runs.
- Record the checksum of every output file, and assert it is stable across two runs for stages that must be reproducible.
- Record package versions in the run log. A different Polars version is a different pipeline.

## Style

- `ruff` and `black`, enforced in CI. Do not hand-format.
- Type hints on public functions in `src/`.
- Docstrings state the guarantee, not the mechanics: "Every raw row is either retained or attributable to a logged cleaning operation."
- No bare `except:`. A swallowed exception in a data pipeline becomes a silently dropped partition.

## Logging over printing

Use a logger, write to `out/stage-NN/run.log`, and make every log line carry the stage, the scenario and the count where relevant. When a Kaggle run fails at 03:00, the log is the only witness.
