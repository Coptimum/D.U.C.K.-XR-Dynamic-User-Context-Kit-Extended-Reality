# Telemetry (host PC)

Small **host-side** tools to ingest live signals for D.U.C.K (heart rate via Pulsoid, posture via BLE or serial).

| Folder | Purpose |
|--------|--------|
| [`pulsoid-hr/`](pulsoid-hr/) | Minimal Node script: Pulsoid WebSocket → print BPM (verify token + band). |
| [`posture-ble/`](posture-ble/) | Python + [`bleak`](https://github.com/hbldh/bleak): ESP32 posture GATT notify → `POSTURE,...` lines; `bridge_posture.py` → JSON / JSONL / UDP / WebSocket. |
| [`biometrics-fusion/`](biometrics-fusion/) | Node host service: consumes Pulsoid HR + local posture WebSocket, publishes one merged local WebSocket stream. |

See [`docs/ConnectingParts.md`](../docs/ConnectingParts.md) for how this fits the full pipeline.
