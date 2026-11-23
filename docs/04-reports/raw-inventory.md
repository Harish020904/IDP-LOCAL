# Raw Dataset Inventory Report — Stage 02

**Dataset:** IoT-23 (Stratosphere Laboratory v1.0.0)  
**Kaggle Source:** `harishragavender0209/iot-23-raw`  
**Manifest:** `docs/04-reports/capture-manifest.csv`  

---

## 1. Inventory Summary

| Metric | Value |
|---|---|
| Total Capture Files | 18 |
| Malicious Scenarios | 15 files |
| Benign Scenarios | 3 files |
| Total Uncompressed Storage | 44,311,939,884 bytes (~41.26 GiB) |
| Malicious Traffic Storage | 44,311,678,060 bytes |
| Benign Traffic Storage | 261,824 bytes |
| Percentage Malicious by Storage | 99.999% |
| Percentage Benign by Storage | 0.001% |

---

## 2. Heavyweight vs Lightweight Captures

The top 4 largest capture files account for 36,255,913,349 bytes (81.8% of the entire dataset):
1. `8.labeled` (CTU-IoT-Malware-Capture-8-1, Mirai): 10,885,361,439 bytes (24.6%)
2. `6.labeled` (CTU-IoT-Malware-Capture-48-1, Mirai): 9,363,261,631 bytes (21.1%)
3. `15.labeled` (CTU-IoT-Malware-Capture-33-1, Kenjiro): 8,139,370,158 bytes (18.4%)
4. `12.labeled` (CTU-IoT-Malware-Capture-39-1, IRec-Mirai): 7,867,920,121 bytes (17.8%)

Smallest captures:
- `benign-honeypot3.labeled`: 18,024 bytes
- `5.labeled`: 31,179 bytes
- `benign.labeled`: 61,653 bytes
- `benign-honeypot2.labeled`: 182,147 bytes

---

## 3. Provenance & Invariant Guarantee

Each raw file corresponds to a single scenario capture. Throughout the pipeline:
- The `scenario_id` must remain attached as metadata to every flow.
- Scenarios must never be split across partitions (Invariant 4).
