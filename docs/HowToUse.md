# How to use D.U.C.K

Step-by-step guide to start the live pipeline: **heart rate** (Pulsoid) + **posture** (ESP32 over BLE) → merged stream on `ws://127.0.0.1:9090/`.

Everything below assumes **Windows 10/11 + PowerShell**. For deep architecture details see [`hub_details.md`](hub_details.md); for scope see [`FinalStretchDoc.md`](FinalStretchDoc.md).

---

## 0. One-time setup (do this only the first time)

### 0.1 Install the tools

| Tool | Why | Install |
|------|-----|---------|
| [Node.js LTS](https://nodejs.org/) | Runs the HR + fusion services | Download installer, default options |
| [Python 3.10+](https://www.python.org/downloads/) | Runs the posture BLE bridge | Check "Add Python to PATH" during install |
| [Arduino IDE 2](https://www.arduino.cc/en/software) | Flashes ESP32 firmware (once per hardware change) | Default install |

Verify in a fresh PowerShell window:

```powershell
node -v
python --version
```

### 0.2 Flash the ESP32 (once per board)

1. Open Arduino IDE → **File → Open** → `arduino/posture/posture.ino`.
2. **File → Preferences → Additional boards manager URLs** — add `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`.
3. **Tools → Board → Boards Manager** — install **esp32** by Espressif (3.x recommended).
4. **Sketch → Include Library → Manage Libraries** — install **NimBLE-Arduino** by `h2zero`.
5. Pick board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**.
6. On ESP32 core **2.x only**: **Tools → Bluetooth → NimBLE** (on 3.x this is default — no option appears).
7. Plug the ESP32 in by USB, pick the COM port, click **Upload**.
8. Close the Serial Monitor when done — the bridge needs the ESP32 free.

### 0.3 Install the Python bridge dependencies

```powershell
cd "path\to\D.U.C.K\telemetry\posture-ble"
pip install -r requirements.txt
```

### 0.4 Install the Node services

```powershell
cd "path\to\D.U.C.K\telemetry\pulsoid-hr"
npm install

cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
npm install
```

### 0.5 Set up your Pulsoid token

1. Go to <https://pulsoid.net/> → sign in → developer settings → create a **token with scope `data:heart_rate:read`**.
2. Install the **Pulsoid mobile app** on your phone, sign in with the **same account**, and start HR streaming from the Xiaomi Smart Band 10.
3. Copy the token, then:

```powershell
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
Copy-Item .env.example .env
notepad .env
```

Paste the token into `PULSOID_TOKEN=`. Save and close. **Never commit `.env`** — it's already in `.gitignore`.

(Optional: do the same in `telemetry/pulsoid-hr/` if you want the standalone HR tester.)

### 0.6 Find your ESP32's BLE address (once)

Power on the ESP32 (USB or battery), make sure Bluetooth is on the PC, then:

```powershell
cd "path\to\D.U.C.K\telemetry\posture-ble"
python read_posture_ble.py --list
```

Look for a line like `F4:2D:C9:6B:2D:6E    DUCK Posture`. **Copy that address** — you'll use it every time you start the pipeline. (You *can* skip this and let the bridge scan by name, but `--address` is faster and more reliable.)

---

## 1. Daily startup — three terminals

Open **three separate PowerShell windows** (or three Cursor terminal tabs). Keep each one running — do **not** close them while using D.U.C.K.

### Before you press anything

1. **Charge and wear the Xiaomi band**, start live HR in the **Pulsoid app** on your phone (you should see BPM updating in the app).
2. **Power on the ESP32** (USB cable or battery).
3. Confirm Bluetooth is on in Windows settings.

### Terminal 1 — Posture bridge (Python)

Replace the address with what **you** saw in step 0.6 — every ESP32 has a different one:

```powershell
cd "path\to\D.U.C.K\telemetry\posture-ble"
python bridge_posture.py --address F4:2D:C9:6B:2D:6E --ws-host 127.0.0.1 --ws-port 8765 --no-print
```

Success looks like:

```
Listening for POSTURE lines (Ctrl+C to stop)…
Connecting to F4:2D:C9:6B:2D:6E…
WebSocket server ws://127.0.0.1:8765/ (JSON broadcast)
BLE connected (is_connected=True).
Subscribed to notify beb5483e-…
First POSTURE line received; fan-out active.
```

Leave it running.

### Terminal 2 — Fusion hub (Node)

```powershell
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
npm run fusion
```

Success looks like:

```
Fusion service started. Press Ctrl+C to stop.
Fusion WS server listening on ws://127.0.0.1:9090/
Posture input URL: ws://127.0.0.1:8765
Connected to posture bridge WebSocket.
Pulsoid WebSocket connected.
Pulsoid monitor is online.
```

Leave it running.

### Terminal 3 — A consumer (to verify OR your real client)

Two quick options to confirm data is flowing.

**Option A — tiny Node sanity check** (fastest):

```powershell
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
node -e "const WS=require('ws');const s=new WS('ws://127.0.0.1:9090/');s.on('open',()=>console.log('open'));s.on('message',m=>console.log(m.toString()))"
```

You should see `open`, then a `snapshot` line, then a stream of `hr` / `posture` JSON messages.

**Option B — browser DevTools:**

1. Go to **`about:blank`** (not an `https://` page — mixed content will block `ws://`).
2. Press **F12** → **Console** tab.
3. Paste:

```js
const s = new WebSocket('ws://127.0.0.1:9090/');
s.onopen = () => console.log('OPEN');
s.onmessage = (e) => console.log(JSON.parse(e.data));
```

In real use, Terminal 3 is replaced by your actual consumer — the Unity app on the Quest 3, a dashboard, or a logger. They all connect to the same URL: `ws://127.0.0.1:9090/`.

---

## 2. What you should see

Every message on `ws://127.0.0.1:9090/` is one JSON object like:

```json
{
  "type": "posture",
  "ts": "2026-04-17T04:01:15.421Z",
  "heartRate": 79,
  "heartMeasuredAt": "2026-04-17T04:01:15.805Z",
  "posture": {
    "state": "good",
    "deviation_deg": 1,
    "raw_line": "POSTURE,good,1",
    "source": "posture-ble",
    "ts": "2026-04-17T04:01:15.421436+00:00"
  }
}
```

- `type: "hr"` — fires on every heart-rate tick.
- `type: "posture"` — fires on every posture reading.
- `type: "snapshot"` — sent once when a new client connects.

If you want to confirm posture is live, **lean forward** — you should see `state` flip to `slouched` within ~1 second.

---

## 3. Stopping everything

In each terminal, press **Ctrl+C**. Order doesn't matter. The fusion hub and posture bridge both handle Ctrl+C cleanly.

Unplug the ESP32 (or turn off its battery switch) when you're done.

---

## 4. Common problems

| Symptom | Most likely cause | Fix |
|---------|-------------------|-----|
| Fusion: `ECONNREFUSED 127.0.0.1:8765` | Terminal 1 (posture bridge) isn't running | Start Terminal 1 first, then Terminal 2 |
| Bridge: `No device found` / silently exits | ESP32 off, low battery, or address changed | Power-cycle ESP32; re-run `python read_posture_ble.py --list`; update `--address` |
| Bridge exits right after "Connecting…" | Stale BLE session or Windows cache | Unplug/replug ESP32; toggle Windows Bluetooth off/on; try again |
| Fusion: `Pulsoid monitor is offline.` | Phone app not streaming or band not on wrist | Open Pulsoid app, confirm BPM is live, put band on wrist |
| Node: `Cannot find module 'ws'` | Wrong directory | `cd` into `telemetry/biometrics-fusion/` before running |
| Arduino: `NimBLEDevice.h: No such file` | NimBLE library not installed | Library Manager → install **NimBLE-Arduino** by `h2zero` |
| Browser console: immediate `CLOSE 1006` | You're on an `https://` page | Switch to `about:blank` or an `http://` page |

For deeper issues look at `hub_details.md` §9, or check [`docs/CheckLater.md`](CheckLater.md) for known-issue tracking.

---

## 5. Cheat sheet (copy-paste)

After the one-time setup, these three commands are all you need. Swap in **your** ESP32 address.

```powershell
# Terminal 1
cd "path\to\D.U.C.K\telemetry\posture-ble"
python bridge_posture.py --address YOUR:ESP:32:MAC:ADDR:HERE --ws-host 127.0.0.1 --ws-port 8765 --no-print

# Terminal 2
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
npm run fusion

# Terminal 3 (optional sanity check)
cd "path\to\D.U.C.K\telemetry\biometrics-fusion"
node -e "const WS=require('ws');const s=new WS('ws://127.0.0.1:9090/');s.on('open',()=>console.log('open'));s.on('message',m=>console.log(m.toString()))"
```

---

## 6. Related docs

- [`hub_details.md`](hub_details.md) — what the hub is, the full dependency graph, output schema, and the reserved slot for Quest 3 / Unity MorphCast input
- [`ConnectingParts.md`](ConnectingParts.md) — how every subsystem physically/logically connects
- [`FinalStretchDoc.md`](FinalStretchDoc.md) — authoritative project scope and goals
- [`MLOptions.md`](MLOptions.md) — what will consume the fusion stream (Random Forest + interval model)
- [`../arduino/README.md`](../arduino/README.md) — posture firmware details
- [`../telemetry/biometrics-fusion/README.md`](../telemetry/biometrics-fusion/README.md) — fusion service reference
- [`../telemetry/posture-ble/README.md`](../telemetry/posture-ble/README.md) — posture bridge reference
- [`../telemetry/pulsoid-hr/README.md`](../telemetry/pulsoid-hr/README.md) — Pulsoid token verifier
