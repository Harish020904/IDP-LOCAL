# Scope — IoT-23 Dataset Engineering Pipeline

**Version:** 1.0  
**Date:** 2026-11-23  
**Status:** Authoritative — changes require a manager-approved PR with rationale

This document lists items that are explicitly in scope, out of scope, and deferred.

---

## In Scope

| Item | Why |
|---|---|
| Ingesting the IoT-23 conn.log captures from Dataset A | Core purpose |
| Inventorying, profiling, and auditing the raw data | M1 and M2 deliverables |
| Cleaning with fully logged, attributable operations | M3 deliverable |
| Assigning feature roles and documenting leakage risks | M3 deliverable |
| Partitioning into train/validation/test at the scenario level | M3 deliverable |
| Preprocessing (imputation, scaling, encoding) fitted on train only | M3 deliverable |
| Publishing the prepared dataset as versioned Kaggle Dataset B | M4 deliverable |
| Verifying end-to-end reproducibility from Dataset A | M4 deliverable |
| Documenting the class imbalance (not correcting it) | M4 deliverable |

---

## Explicitly Out of Scope

The following will not be implemented. A PR that adds any of them without a prior manager-approved scope change is rejected.

| Item | Reason deferred | Who decides to add it |
|---|---|---|
| Model training of any kind | Pipeline is a data artifact, not a modelling experiment | Manager + new ADR |
| Inference, prediction, or scoring | No model is built | Manager + new ADR |
| Evaluation on external benchmarks (UNSW-NB15, CIC-IDS, etc.) | Requires separate datasets and a model | Manager + new ADR |
| Feature selection or dimensionality reduction | A modelling choice for the downstream researcher | Manager + new ADR |
| Balancing, oversampling, undersampling, or synthetic flow generation | Prohibited by Invariant 3 | Requires ADR — Invariant 3 means high bar |
| Cross-dataset comparison or harmonisation | Out of scope; separate project | Manager + new ADR |
| Online or streaming data ingestion | Source data is a static historical capture | Manager + new ADR |
| Automated hyperparameter tuning | No model, no hyperparameters | Manager + new ADR |
| Visualisation dashboards or interactive reports | Static committed figures only | Manager + new ADR |
| Data augmentation | Equivalent to balancing; Invariant 3 applies | Requires ADR |

---

## Deferred — May Be Revisited

### D1 — Feature selection

Deferred because: Feature selection requires knowing which model family will consume the data. The pipeline is model-agnostic by design. Applying feature selection here would embed a modelling assumption into a data preparation artifact.

Condition to revisit: A downstream researcher publishes a model requirement that cannot be met without selection, and the manager approves a new ADR that names the selection method and its rationale.

### D2 — Alternative label granularities

Deferred because: label (coarse) and detailed-label (fine) are both preserved as-is. Collapsing them to binary is prohibited by Invariant 2. Creating additional aggregated label columns is a valid research question but not part of the base pipeline.

Condition to revisit: A named research question requires a specific aggregation, documented in an ADR, with the original labels preserved alongside any new column.

### D3 — Additional benign capture sources

Deferred because: IoT-23 contains 3 benign captures. Supplementing with external sources would change the dataset distribution in ways not attributable to the original source.

Condition to revisit: The class imbalance report (Stage 12) documents the benign proportion. Supplementation requires its own pipeline design decision.

### D4 — Temporal splitting instead of scenario-level splitting

Deferred because: Scenario-level splitting is the most conservative partition strategy for scenario-based intrusion datasets. Temporal splitting within a capture would split network conditions, allowing the model to have seen the network environment of the test scenario.

Condition to revisit: A published research argument that temporal splitting is more appropriate for a specific evaluation protocol, reviewed by the manager and documented in an ADR superseding the scenario-splitting decision.

### D5 — Packet-level or byte-level features

Deferred because: The IoT-23 source data is conn.log (flow-level). Packet-level features require the raw PCAP files, which are not part of the Kaggle dataset.

Condition to revisit: If PCAP access is established and storage constraints are addressed, a parallel pipeline stage could extract packet features. That is a separate branch of work.

---

## Scope Change Process

1. Open a GitHub issue titled "Scope change: [item]".
2. Manager decides: accept, defer, or reject. Writes one line of rationale.
3. If accepted: update this file and the relevant section of docs/00-project/brief.md in the same PR.
4. If the change contradicts an invariant in AGENTS.md section 7, file an ADR that names the invariant and accepts the risk in writing.
5. Tell both agents in the same message.
