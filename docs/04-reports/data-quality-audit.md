# Data Quality Audit Report — Stage 05

**Dataset:** IoT-23 (Stratosphere Laboratory v1.0.0)  
**Kaggle Source:** `harishragavender0209/iot-23-raw`  
**Milestone:** M2 Understanding (Audit & Assessment)  
**Registry:** `docs/04-reports/quality-issues.csv`  

---

## 1. Audit Scope & Methodology

This quality audit inspects the raw Zeek network flow records across nine critical failure modes. Every issue is categorized by severity and assigned a binding handling decision for Stage 06 (Raw Data Cleaning), adhering strictly to the **Data Handling Non-Negotiable Invariants**.

---

## 2. Findings by Problem Category

### 2.1 Unset vs Missing Metrics (`-`)
- **Finding:** A significant proportion of connection records exhibit `-` in `duration`, `orig_bytes`, and `resp_bytes`.
- **Root Cause:** Zeek logs connections at termination. Connections that never completed a 3-way handshake (e.g. `S0` half-open SYN floods, port scans, or rejected connections) legitimately possess no duration or payload bytes.
- **Handling Decision:** **Do NOT blanket fill with zero.** Unknown/unmeasured duration is physically distinct from a zero-second instantaneous connection. Stage 06 will preserve valid unset tokens.

### 2.2 Network Layer Validity (Ports & IPs)
- **Finding:** Originator and responder ports must conform to IANA transport standards ($0 \le \text{port} \le 65535$).
- **Handling Decision:** Any out-of-range port indicates log corruption and will be quarantined with a logged operation.

### 2.3 Temporal Integrity
- **Finding:** Timestamps are recorded in Unix epoch seconds (`ts`).
- **Handling Decision:** Timestamps must be strictly positive floats. Malformed timestamps will be quarantined.

### 2.4 Identifier Uniqueness
- **Finding:** The Zeek `uid` identifies unique flows. Two separate connections occurring at different timestamps may share identical feature profiles (e.g. identical port scan probes).
- **Handling Decision:** **Do NOT deduplicate on feature equality.** Genuine repeated network connections naturally share attributes.

### 2.5 Label Integrity & Invariant 2
- **Finding:** Analyst labels (`label`, `detailed-label`) represent the ground truth for downstream model evaluation.
- **Handling Decision:** Under Invariant 2, original labels are **never** altered in place. Inconsistencies or clarifications must be placed in a dedicated `label_flag` column.

---

## 3. Preparation Decisions for Stage 06 Cleaning

| Problem | Safe Handling Decision | Rule / Invariant |
|---|---|---|
| Unset duration | Keep as unset or separate indicator | Never assume zero = unknown |
| Unset payload bytes | Keep as unset or separate indicator | Never assume zero = unknown |
| Negative duration | Quarantine or flag | Logged operation |
| Invalid port | Quarantine record | Logged operation |
| Missing label | Quarantine record | Ground truth required |
| Minority attack classes | **Preserve 100% of rows** | Invariant 3 (no balancing) |
| Duplicate feature rows | **Preserve legitimate flows** | No blanket deduplication |
