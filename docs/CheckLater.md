# Check later (D.U.C.K backlog)

Open this file when you have time; work through items in whatever order matters for your phase.

---

## Posture BLE / host pipeline

- [ ] **Demo checklist** — Write a short fixed sequence (power ESP32 → run `telemetry/posture-ble/bridge_posture.py` or `read_posture_ble.py` → confirm JSON / `POSTURE,...` lines) so pre-demo setup is repeatable without memory.

- [ ] **Reconnect / range** — If the link drops when someone walks away, decide whether restarting the script is enough or you want **auto-retry** in Python (re-scan, re-connect loop).

- [ ] **Downstream wiring** — Connect Unity, ML, or a dashboard to one bridge output: **UDP**, **WebSocket**, or **JSONL** (`--log`), not only stdout. Pick one path and keep the JSON shape stable.
- [x] **Host fusion WebSocket (single-user path)** — Implemented under `telemetry/biometrics-fusion/`: merges Pulsoid HR + posture into one local WebSocket feed for one consumer URL.

- [ ] **BLE privacy / trust** — Current posture BLE is **discoverable** and **not authenticated**; fine for trusted lab demos. Revisit if you demo in public or ship hardware (pairing, bonding, or rotating identifiers—only if needed).

- [ ] **`FinalStretchDoc.md`** — If it still describes posture only over **USB serial**, add one sentence that **BLE + host bridge** is the on-the-go path and point to `docs/ConnectingParts.md` + `telemetry/posture-ble/README.md`.

---

## Broader project (when relevant)

- [ ] **Quest ↔ PC transport** — Still TBD in the main spec; lock protocol + small message schema when the MR app ingests host-side state.

- [ ] **HR path** — Pulsoid / band setup: keep token and demo flow documented next to posture so one machine runs both streams.

---

*This file is intentionally informal; authoritative scope stays in `docs/FinalStretchDoc.md`.*
