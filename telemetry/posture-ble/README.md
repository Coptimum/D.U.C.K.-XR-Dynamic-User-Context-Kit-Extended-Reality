# Posture BLE stream (host PC)

Reads live posture lines from the ESP32 sketch [`arduino/posture/posture.ino`](../../arduino/posture/posture.ino) over **Bluetooth Low Energy** (GATT notify). Same `POSTURE,...` text as USB serial—useful for **on-the-go demos** without Wi‑Fi.

## Setup

```text
cd telemetry/posture-ble
pip install -r requirements.txt
python read_posture_ble.py
```

Ensure **Bluetooth is on**, the ESP32 is powered and running the NimBLE firmware, then wait for the script to find **`DUCK Posture`** and subscribe.

## Options

| Flag / env | Purpose |
|------------|---------|
| `--list` | Print nearby BLE devices (name + address) |
| `--address AA:BB:...` or `DUCK_POSTURE_BLE_ADDRESS` | Skip scan; connect by MAC |
| `--name ...` or `DUCK_POSTURE_BLE_NAME` | Override advertised name (default `DUCK Posture`) |
| `--timeout N` | Scan timeout seconds (default 15) |

## UUIDs (must match firmware)

- Service: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- Notify characteristic: `beb5483e-36e1-4688-b7f5-ea07361b26a8`

## Parser bridge (`bridge_posture.py`)

Turns each `POSTURE,...` line into **one JSON object** (UTC `ts`, `state`, fields). Connects to the ESP32 over BLE by default (same options as `read_posture_ble.py` for `--name`, `--address`, `--timeout`).

```text
python bridge_posture.py
python bridge_posture.py --log posture.jsonl
python bridge_posture.py --udp 127.0.0.1:5599
python bridge_posture.py --ws-port 8765
python bridge_posture.py --log out.jsonl --udp 127.0.0.1:5599 --ws-port 8765 --no-print
```

| Flag | Purpose |
|------|--------|
| `--stdin` | Read raw lines from stdin (e.g. `python read_posture_ble.py \| python bridge_posture.py --stdin`) |
| `--log FILE` | Append **JSONL** (one JSON per line) |
| `--udp HOST:PORT` | Send each event as one **UDP** datagram (UTF-8 JSON) |
| `--ws-port PORT` | **WebSocket** server on `--ws-host` (default `127.0.0.1`); broadcasts each JSON to connected clients |
| `--no-print` | Suppress JSON on stdout (useful with only `--log` / `--udp` / `--ws-port`) |

`parse_posture_line()` is available for reuse: `from bridge_posture import parse_posture_line`.

## How the PC finds the ESP32 (Bluetooth)

1. **Advertising** — When the sketch runs, the ESP32 periodically broadcasts short **BLE advertisement** packets over the air. Those packets can include a **local name** (`DUCK Posture`) and/or **service UUIDs** (our custom `4fafc201-...`). They are public beacons: any nearby radio can hear them (no Wi‑Fi, no pairing yet).

2. **Scan** — `bleak` asks Windows (Bluetooth driver) to **listen** for a few seconds. Every device that advertises nearby shows up as a **BLE address** (MAC-like id) plus whatever fields the OS parsed from the packet.

3. **Pick a device** — If you passed **`--address`**, we skip the scan and connect straight to that address. Otherwise **`find_device_by_name`** stops at the first advertisement whose **local name** matches `DUCK Posture`. If Windows hid the name, **`find_device_by_filter`** falls back to “advertisement lists our **SERVICE_UUID**”.

4. **Connect + GATT** — After we know the address, **`BleakClient`** opens a normal BLE connection. We then **subscribe** to the **notify** characteristic (`beb5483e-...`). The ESP32 pushes each `POSTURE,...` line as one notification payload.

5. **`--list`** — Runs a single scan and prints **address + name** for everything heard—useful when the name is missing and you need the address for `--address`.

See [`docs/ConnectingParts.md`](../../docs/ConnectingParts.md) for the full pipeline.
