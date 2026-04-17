# D.U.C.K – Posture sensor firmware (ESP32)

ESP32 firmware for the DIY posture sensor. Reads an analog posture sensor (e.g. flex or accelerometer), supports calibration, and streams posture state over **USB serial** and **Bluetooth LE notify** (same line format). Vibe motor triggers only when slouched.

- **Build/upload:** Arduino IDE or PlatformIO (select ESP32 board).
- **Hardware and BCI pipeline:** See [docs/ProjectProposal.md](../docs/ProjectProposal.md).

## Hardware (this design)

- **ESP32** – main MCU.
- **Z_PIN (GPIO 35)** – analog input (e.g. flex sensor with voltage divider, or other posture sensor).
- **VIBE_PIN (GPIO 25)** – vibration motor for haptic feedback on slouch.

## Transport: serial + BLE

- **USB serial** — **115200** baud; use for bench testing and Arduino Serial Monitor.
- **BLE** — Advertised name **`DUCK Posture`**; GATT notify on characteristic `beb5483e-36e1-4688-b7f5-ea07361b26a8` under service `4fafc201-1fb5-459e-8fcc-c5c9c331914b`. No Wi‑Fi required.

**Arduino ESP32 core:** sketch uses **NimBLE** (`NimBLEDevice.h`). On **2.x**, set **Tools → Bluetooth → NimBLE**; **3.x** defaults to NimBLE.

Host-side test client: [`telemetry/posture-ble/`](../telemetry/posture-ble/).

## Line protocol (serial and BLE)

Real-time, one line per update (~10 Hz, see `OUTPUT_INTERVAL_MS` in the sketch):

- `POSTURE,good,<deviation_deg>`
- `POSTURE,slouched,<raw>,<deviation_deg>`
- `POSTURE,off,30s_bad` (firmware stops normal output after prolonged slouch)

A host PC or bridge can parse these lines for logging or forwarding to the MR app later.

## Calibration

On startup the device samples the analog input for 3 seconds. **Hold good posture** during that time to set the baseline. After calibration, any deviation from baseline above `SLOUCH_THRESHOLD` (see `posture.ino`) is reported as slouched. Tune `SLOUCH_THRESHOLD` in code if the sensor is too sensitive or not sensitive enough.

## Placement and validation

- **Placement (user):** Back of neck (or upper back / thoracic per literature). Secure the sensor so it doesn’t shift during movement.
- **Validation (per plan):** Test in multiple positions (obvious bad posture, subtle slouch) and in both **sedentary** and **active** environments. Confirm Serial output shows `POSTURE,good` when posture is good and `POSTURE,slouched,<value>` when slouched, and that the vibe pulses only when slouched.
- **Limitations:** Baseline is set at power-on only; if the sensor is moved or the user changes seating, re-power or add a recalibration trigger later. Single analog channel; for multi-axis posture (e.g. lateral lean) additional sensors would be needed.
