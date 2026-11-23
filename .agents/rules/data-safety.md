---
trigger: always_on
description: "Data-safety invariants for the IoT-23 pipeline: raw immutability, label preservation, no balancing, no scenario crossing, fit-on-train-only."
---

# Data safety

These five invariants hold in every stage, in every agent, at all times. Violating one is an S1 defect and blocks the merge.

## 1. Raw data is read-only

The original IoT-23 archive is never modified, moved, or re-extracted in place. Verify its SHA-256 in every stage that touches data and compare against `docs/04-reports/checksums.sha256`.

If a stage needs a modified input: copy it to a working directory, modify the copy, log the copy's checksum.

## 2. Original labels are never silently changed

`label` and `detailed-label` are analyst annotations produced under documented rules. If a value is wrong, add `label_corrected` or `label_flag` with the reason and leave the original intact.

Never rewrite a label in place. Never collapse labels into binary. Never drop a label value without an ADR.

## 3. No balancing

No SMOTE, no SMOTENC, no oversampling, no undersampling, no synthetic flows, no minority deletion, at any stage.

Stage 12 *documents* the imbalance. If you believe balancing is needed, that is a proposal for the manager and a new ADR — never a commit.

## 4. No capture scenario crosses a partition boundary

Whole scenarios go to exactly one of train, validation, test. Never split a capture to force a rare label into every partition.

If a label exists in only one capture, document the limitation in the label-coverage report. That limitation is a property of the dataset, not a bug to engineer around.

## 5. Nothing is fitted outside training data

Imputation values, scaling parameters, encoding dictionaries, category frequencies, feature-selection thresholds: computed on the training partition only, then applied unchanged to validation and test.

Record the fit source with every parameter so a gate test can assert it.

## Enforcement

Each invariant has a gate test. If you are about to do something that no gate test would catch, that is the signal to write the test first.
