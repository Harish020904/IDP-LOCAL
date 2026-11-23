# Zeek Schema Analysis Report — Stage 03

**Dataset:** IoT-23 (Stratosphere Laboratory v1.0.0)  
**Log Type:** Zeek (formerly Bro) `conn.log` with analyst flow-level annotations  
**Dictionary:** `docs/04-reports/data-dictionary.csv`  

---

## 1. Zeek Header & Delimiter Conventions

Each raw capture file begins with Zeek header metadata lines prefixed with `#`:
- `#separator \x09` (Tab-delimited: `\t`)
- `#set_separator ,` (Comma for set elements)
- `#empty_field (empty)` (Signifies an empty string)
- `#unset_field -` (Signifies unrecorded, absent, or unanswered value)
- `#path conn`
- `#fields` (Names of the 23 columns)
- `#types` (Declared Zeek data types)

---

## 2. Field Structure (23 Columns)

The schema contains 21 native Zeek flow attributes plus 2 analyst annotation fields:
1. `ts` (time) — Epoch timestamp
2. `uid` (string) — Connection unique hash
3. `id.orig_h` (addr) — Source IP
4. `id.orig_p` (port) — Source port
5. `id.resp_h` (addr) — Destination IP
6. `id.resp_p` (port) — Destination port
7. `proto` (enum) — Transport protocol (`tcp`, `udp`, `icmp`)
8. `service` (string) — Application service
9. `duration` (interval) — Connection duration (or `-` for incomplete flows)
10. `orig_bytes` (count) — Originator payload bytes
11. `resp_bytes` (count) — Responder payload bytes
12. `conn_state` (string) — Zeek connection state summary flag
13. `local_orig` (bool) — Local origination flag
14. `local_resp` (bool) — Local responder flag
15. `missed_bytes` (count) — Missed bytes in payload
16. `history` (string) — Connection state history
17. `orig_pkts` (count) — Originator packet count
18. `orig_ip_bytes` (count) — Originator IP layer byte count
19. `resp_pkts` (count) — Responder packet count
20. `resp_ip_bytes` (count) — Responder IP layer byte count
21. `tunnel_parents` (set[string]) — Encapsulating tunnel parents
22. `label` (string) — Coarse target (`Malicious` or `Benign`)
23. `detailed-label` (string) — Fine-grained target attack pattern

---

## 3. Label Preservation & Invariant 2

- `label` and `detailed-label` are ground-truth security annotations created by Stratosphere security analysts.
- Under **Invariant 2**, original labels are immutable and must **never** be rewritten in place or collapsed into binary during cleaning or feature transformation. Any correction or normalization must reside in a newly created column (e.g. `label_corrected` or `label_flag`).
