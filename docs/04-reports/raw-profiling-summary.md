# Raw Data Profiling Summary Report — Stage 04

**Dataset:** IoT-23 (Stratosphere Laboratory v1.0.0)  
**Kaggle Source:** `harishragavender0209/iot-23-raw`  
**Milestone:** M2 Understanding  
**Observation Rule:** No data cleaning or modifications applied. Profiling and statistical assessment only.

---

## 1. Class Distribution Analysis

### 1.1 Coarse-Grained Label (`label`)
The dataset exhibits pronounced macro-level class imbalance between benign normal/honeypot traffic and malicious attack vectors:
- **Malicious:** Heavy dominance across the large captures (`8.labeled`, `6.labeled`, `15.labeled`, `12.labeled`).
- **Benign:** Heavily concentrated in `benign.labeled`, `benign-honeypot2.labeled`, and `benign-honeypot3.labeled`, plus minor benign background traffic within malware scenarios.

### 1.2 Fine-Grained Label (`detailed-label`)
Prominent attack families observed across the 15 malware scenarios:
- `PartOfAHorizontalPortScan`: Predominant in Mirai and Muhstik infection sweeps.
- `Okiru`: Embedded botnet propagation and DDoS attacks.
- `DDoS`: High-frequency synchronized flooding traffic.
- `C&C` / `C&C-HeartBeat`: Periodic command-and-control communication.
- `Attack`: Direct vulnerability exploitation and brute force attempts.
- `-` (Unset): Denotes flows without detailed sub-classification (primarily benign flows and non-attack background traffic).

---

## 2. Missing-Value Distribution (`-`)

In native Zeek `conn.log` semantics, the dash `-` represents unrecorded or non-applicable values:
- `duration`: Unset for one-way flows, dropped SYN packets, or aborted connections (`conn_state` = `S0` or `REJ`).
- `orig_bytes` & `resp_bytes`: Unset when payload data was not captured or flow ended before ACK handshake.
- `service`: Unset (`-`) when Zeek protocol analyzers cannot conclusively identify higher-layer application protocols.
- `tunnel_parents`: Unset (`-`) for non-tunneled direct IP traffic (>99.9% of flows).

---

## 3. Visualizations Generated

All figures are committed to `docs/04-reports/figures/`:
1. `label_distribution.png`: Coarse label split.
2. `detailed_label_distribution.png`: Fine-grained attack categories displayed on a logarithmic scale to preserve minority attack visibility.
3. `missing_values.png`: Percentage of unset values (`-`) per column across the 23 Zeek attributes.

---

## 4. Invariant Compliance
- **Invariant 1 (Raw Read-Only):** Verified; no raw data modified during profiling.
- **Invariant 2 (Labels Preserved):** Verified; original `label` and `detailed-label` observed without modification.
- **Invariant 3 (No Balancing):** Imbalance is measured and documented as an authentic property of the capture environment.
