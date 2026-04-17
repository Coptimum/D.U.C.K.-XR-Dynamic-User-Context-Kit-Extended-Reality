# Biometrics fusion (host WebSocket)

Merges two live streams on the host PC into one local WebSocket feed:

- Heart rate from Pulsoid (`@pulsoid/socket`)
- Posture JSON from [`../posture-ble/bridge_posture.py`](../posture-ble/bridge_posture.py)

## Why

One downstream consumer URL is simpler than wiring separate HR and posture streams into Unity / dashboards.

## Setup

```powershell
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
npm install
Copy-Item .env.example .env
# edit .env and set PULSOID_TOKEN
```

## Run order

1. Start posture bridge as local WebSocket source:

```powershell
cd "path\to\D.U.C.K\telemetry\posture-ble"
python bridge_posture.py --ws-host 127.0.0.1 --ws-port 8765 --no-print
```

2. Start fusion:

```powershell
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
npm run fusion
```

3. Connect your app/client to:

```text
ws://127.0.0.1:9090
```

## Output shape

Each message is one JSON object:

```json
{
  "type": "hr",
  "ts": "2026-04-13T22:10:00.123Z",
  "heartRate": 72,
  "heartMeasuredAt": "2026-04-13T22:09:59.950Z",
  "posture": {
    "source": "posture-ble",
    "state": "good",
    "ts": "2026-04-13T22:09:59.800Z",
    "raw_line": "POSTURE,good,3",
    "deviation_deg": 3
  }
}
```

`type` is:
- `snapshot`: sent immediately when a new client connects
- `hr`: emitted on each Pulsoid heart-rate update
- `posture`: emitted on posture updates (if `FUSION_EMIT_ON_POSTURE=1`)

## Environment variables

- `PULSOID_TOKEN` (required)
- `POSTURE_WS_URL` (default `ws://127.0.0.1:8765`)
- `FUSION_WS_HOST` (default `127.0.0.1`)
- `FUSION_WS_PORT` (default `9090`)
- `FUSION_EMIT_ON_POSTURE` (default `1`)

## Notes

- This is localhost-first for single-user demos.
- If posture bridge starts late, fusion retries with exponential backoff up to 15s.
