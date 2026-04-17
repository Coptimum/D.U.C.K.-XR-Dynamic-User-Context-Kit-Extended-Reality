# Pulsoid heart rate — quick test (D.U.C.K)

Minimal script to confirm your **Pulsoid access token** and **watch** path: connects to Pulsoid’s real-time WebSocket and prints BPM. See also [`docs/ConnectingParts.md`](../../docs/ConnectingParts.md).

## Prerequisites

- [Node.js](https://nodejs.org/) **LTS** (includes `npm`). In PowerShell, `node -v` and `npm -v` should print versions.

## Before you run

1. **Pulsoid mobile app** (or desktop): same account as your API token.
2. **Xiaomi band** paired; **live heart rate** visible in the app (continuous or workout-style HR as Pulsoid requires).

## Setup (Windows PowerShell)

```powershell
cd "path\to\D.U.C.K\telemetry\pulsoid-hr"
npm install
Copy-Item .env.example .env
# Edit .env and set PULSOID_TOKEN=your_token_here
npm run hr
```

Or set the token for one session only:

```powershell
$env:PULSOID_TOKEN="your_token_here"
npm run hr
```

## Expected output

Lines like:

```text
Connected to Pulsoid. Waiting for heart rate…
[2026-04-06T12:34:56.789Z] 72 BPM
```

Press **Ctrl+C** to stop.

## Troubleshooting

| Symptom | What to check |
|--------|----------------|
| `Missing PULSOID_TOKEN` | `.env` in this folder or `$env:PULSOID_TOKEN` |
| Connects but no BPM | App not logged in, band not connected, or HR not live |
| Auth / error events | Token expired or wrong scopes (`data:heart_rate:read` for WebSocket) |

This repo uses **`new PulsoidSocket(token)`** then **`socket.connect()`** (matches `@pulsoid/socket` **v1.3+**; older docs may still show `PulsoidSocket.create()`, which was removed).

Official docs: [Read heart rate via WebSocket](https://docs.pulsoid.net/read-heart-rate/read-heart-rate-via-websocket), [`@pulsoid/socket`](https://www.npmjs.com/package/@pulsoid/socket).
