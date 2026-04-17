"""
Subscribe to D.U.C.K posture lines over BLE (NimBLE GATT notify on ESP32).

Requires: Windows 10+ with Bluetooth, Python 3.10+, `pip install -r requirements.txt`.
ESP32 must run arduino/posture/posture.ino with BLE enabled (default).

Discovery (how the PC finds the ESP32): see module comments on _find_device and
iter_posture_ble_lines, and docs in telemetry/posture-ble/README.md.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import AsyncIterator

from bleak import BleakClient, BleakScanner

# --- IDs that must match firmware (arduino/posture/posture.ino) ---
# Friendly name the ESP32 puts in BLE advertisements ("DUCK Posture").
DEFAULT_NAME = "DUCK Posture"
# Custom GATT service UUID (advertised so scanners can spot us without the name).
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
# Characteristic we subscribe to; firmware pushes each line as a notify payload.
POSTURE_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"


def _uuid_in_advertisement(_d, ad) -> bool:
    """True if this scan packet lists our posture service UUID (Windows sometimes omits name)."""
    want = SERVICE_UUID.lower()
    return any(u.lower() == want for u in ad.service_uuids)


async def _find_device(name: str, timeout: float):
    """
    Pick which BLE radio to connect to.

    BLE devices periodically send short *advertising* packets. Those packets can
    include a *local name* and/or *service UUIDs*. bleak listens for a few seconds
    and returns the first device that matches either:
      1) local name == `name` (e.g. "DUCK Posture"), or
      2) advertisement lists SERVICE_UUID (fallback if name is missing).
    """
    found = await BleakScanner.find_device_by_name(name, timeout=timeout)
    if found:
        return found
    return await BleakScanner.find_device_by_filter(_uuid_in_advertisement, timeout=timeout)


async def iter_posture_ble_lines(
    address: str | None,
    name: str,
    timeout: float,
    *,
    stderr=sys.stderr,
) -> AsyncIterator[str]:
    """
    Async stream of each raw notify payload (one UTF-8 line: POSTURE,...).

    Flow:
      1) Resolve *target*: either BLE MAC (--address) or scan until _find_device matches.
      2) BleakClient connects over the OS Bluetooth stack (Windows: WinRT backend).
      3) start_notify registers `on_notify`; the stack calls it whenever the ESP32 sends.
      4) on_notify pushes text into a queue; we await queue.get() and yield (async for loop).
    """
    # Queue bridges BLE callback thread/context into this async generator.
    queue: asyncio.Queue[str] = asyncio.Queue()

    def on_notify(_: int, data: bytearray) -> None:
        """Called by bleak when the ESP32 fires a GATT notification on POSTURE_CHAR_UUID."""
        text = data.decode("utf-8", errors="replace").strip()
        if text:
            try:
                queue.put_nowait(text)
            except asyncio.QueueFull:
                pass

    if address:
        # Direct path: no scan. `address` is the BLE MAC string the OS reports (e.g. AA:BB:...).
        target = address
        print(f"Connecting to {target}…", file=stderr)
    else:
        # Scan path: OS listens for advertisements until name or SERVICE_UUID matches.
        print(f"Scanning for '{name}' (or service {SERVICE_UUID})…", file=stderr)
        device = await _find_device(name, timeout=timeout)
        if device is None:
            print(
                "No device found. Power the ESP32, ensure NimBLE firmware is flashed, "
                "and try --list or --address.",
                file=stderr,
            )
            raise RuntimeError("No BLE posture device found")
        target = device
        print(f"Connecting to {device.name} ({device.address})…", file=stderr)

    async with BleakClient(target) as client:
        print(f"BLE connected (is_connected={client.is_connected}).", file=stderr)
        # After connect, GATT subscribe: stack will invoke on_notify for each packet.
        await client.start_notify(POSTURE_CHAR_UUID, on_notify)
        print(
            f"Subscribed to notify {POSTURE_CHAR_UUID}. Waiting for POSTURE lines…",
            file=stderr,
        )
        while True:
            # If the peer disconnects, no more notifications will arrive; surface it
            # instead of hanging forever on queue.get().
            if not client.is_connected:
                print("BLE peer disconnected; exiting notify loop.", file=stderr)
                return
            try:
                line = await asyncio.wait_for(queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            yield line


async def _run(address: str | None, name: str, timeout: float) -> None:
    """CLI mode: print each raw line to stdout (for piping or quick checks)."""
    print("Listening for POSTURE lines (Ctrl+C to stop)…", file=sys.stderr)
    try:
        async for line in iter_posture_ble_lines(address, name, timeout, stderr=sys.stderr):
            print(line, flush=True)
    except RuntimeError:
        sys.exit(1)


async def _list_devices(timeout: float) -> None:
    """CLI --list: one scan pass; print address and name for everything heard nearby."""
    devices = await BleakScanner.discover(timeout=timeout)
    for d in devices:
        print(f"{d.address}\t{d.name or '(no name)'}")


def main() -> None:
    """Parse CLI flags, then either list devices or stream lines until Ctrl+C."""
    parser = argparse.ArgumentParser(description="Read D.U.C.K posture BLE notify stream")
    parser.add_argument(
        "--name",
        default=os.environ.get("DUCK_POSTURE_BLE_NAME", DEFAULT_NAME),
        help=f"BLE advertised name (default: {DEFAULT_NAME})",
    )
    parser.add_argument(
        "--address",
        default=os.environ.get("DUCK_POSTURE_BLE_ADDRESS"),
        help="BLE MAC address (skip scan), e.g. AA:BB:CC:DD:EE:FF",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Scan/connect timeout (seconds)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List nearby BLE devices and exit",
    )
    args = parser.parse_args()

    if args.list:
        asyncio.run(_list_devices(args.timeout))
        return

    addr = (args.address or "").strip() or None
    try:
        asyncio.run(_run(addr, args.name, args.timeout))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
