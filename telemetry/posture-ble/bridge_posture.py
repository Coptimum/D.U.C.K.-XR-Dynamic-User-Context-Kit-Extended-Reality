"""
Parse POSTURE,... lines into JSON events; ingest from BLE (default) or stdin.

Same BLE discovery as read_posture_ble (scan by name / service UUID, or --address).

Examples:
  python bridge_posture.py
  python bridge_posture.py --log posture.jsonl --udp 127.0.0.1:5599
  python bridge_posture.py --ws-port 8765
  python read_posture_ble.py | python bridge_posture.py --stdin
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import socket
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

from read_posture_ble import iter_posture_ble_lines

# One CSV-ish line from firmware: POSTURE,<state>[,extra fields...]
POSTURE_RE = re.compile(r"^POSTURE,([^,]+)(?:,(.*))?$")


def parse_posture_line(line: str) -> dict[str, Any] | None:
    """
    Turn one firmware text line into a dict for logs / UDP / Unity bridges.
    Returns None if the line is not a POSTURE message.
    """
    line = line.strip()
    if not line:
        return None
    m = POSTURE_RE.match(line)
    if not m:
        return None

    state = m.group(1)  # good | slouched | off
    rest = m.group(2).split(",") if m.group(2) else []

    evt: dict[str, Any] = {
        "source": "posture-ble",
        "ts": datetime.now(timezone.utc).isoformat(),
        "raw_line": line,
        "state": state,
    }

    if state == "good":
        if len(rest) >= 1 and rest[0].lstrip("-").isdigit():
            evt["deviation_deg"] = int(rest[0])
    elif state == "slouched":
        if len(rest) >= 1 and rest[0].lstrip("-").isdigit():
            evt["raw"] = int(rest[0])
        if len(rest) >= 2 and rest[1].lstrip("-").isdigit():
            evt["deviation_deg"] = int(rest[1])
    elif state == "off" and rest:
        evt["reason"] = ",".join(rest)

    return evt


def _open_udp(host: str, port: int) -> socket.socket:
    """Datagram socket for fire-and-forget JSON to another process on the same machine or LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return s


def _emit(
    evt: dict[str, Any],
    *,
    print_stdout: bool,
    log_fp,
    udp_sock: socket.socket | None,
    udp_addr: tuple[str, int] | None,
) -> None:
    """One event → stdout and/or JSONL file and/or UDP (stdin mode uses this)."""
    blob = json.dumps(evt, separators=(",", ":"))
    if print_stdout:
        print(blob, flush=True)
    if log_fp:
        log_fp.write(blob + "\n")
        log_fp.flush()
    if udp_sock and udp_addr:
        udp_sock.sendto(blob.encode("utf-8"), udp_addr)


async def _run_ble_bridge(args, log_fp, udp_sock, udp_addr, ws_clients: set) -> None:
    """Read lines from BLE (iter_posture_ble_lines), parse, fan-out to stdout/log/UDP/WebSocket."""

    async def _broadcast_ws(blob: str) -> None:
        """Push one JSON string to every connected WebSocket client; drop broken connections."""
        if not ws_clients:
            return
        dead: list[Any] = []
        for ws in list(ws_clients):
            try:
                await ws.send(blob)
            except Exception:
                dead.append(ws)
        for ws in dead:
            ws_clients.discard(ws)

    print("Listening for POSTURE lines (Ctrl+C to stop)…", file=sys.stderr)
    line_count = 0
    async for line in iter_posture_ble_lines(
        args.address, args.name, args.timeout, stderr=sys.stderr
    ):
        evt = parse_posture_line(line)
        if not evt:
            continue
        line_count += 1
        if line_count == 1:
            print("First POSTURE line received; fan-out active.", file=sys.stderr)
        blob = json.dumps(evt, separators=(",", ":"))
        if args.print_stdout:
            print(blob, flush=True)
        if log_fp:
            log_fp.write(blob + "\n")
            log_fp.flush()
        if udp_sock and udp_addr:
            udp_sock.sendto(blob.encode("utf-8"), udp_addr)
        await _broadcast_ws(blob)
    print(
        f"BLE stream ended after {line_count} line(s). Exiting bridge.",
        file=sys.stderr,
    )


async def _ws_serve(host: str, port: int, ws_clients: set) -> None:
    """Run forever: accept WebSocket clients so _broadcast_ws can push live JSON."""
    import websockets

    async def handler(ws):
        # Track client until they disconnect; we only send to them, ignore inbound messages.
        ws_clients.add(ws)
        try:
            async for _ in ws:
                pass
        finally:
            ws_clients.discard(ws)

    async with websockets.serve(handler, host, port):
        print(f"WebSocket server ws://{host}:{port}/ (JSON broadcast)", file=sys.stderr)
        await asyncio.Future()  # Never completes; Ctrl+C stops the process.


async def _async_main(args) -> None:
    """Open outputs (log, UDP), optionally start WS server + BLE loop together."""
    log_fp = open(args.log, "a", encoding="utf-8") if args.log else None
    udp_sock = None
    udp_addr = None
    if args.udp:
        # "127.0.0.1:5599" → host + port (rpartition splits on last ':' so host can contain ':').
        host, _, ps = args.udp.rpartition(":")
        if not ps.isdigit():
            print("--udp must be host:port", file=sys.stderr)
            sys.exit(2)
        udp_sock = _open_udp(host or "127.0.0.1", int(ps))
        udp_addr = (host or "127.0.0.1", int(ps))

    ws_clients: set = set()

    try:
        if args.ws_port is not None:
            # Two concurrent tasks: WS accept loop + BLE read loop (same ws_clients set).
            ws_task = asyncio.create_task(
                _ws_serve(args.ws_host, args.ws_port, ws_clients), name="ws_serve"
            )
            ble_task = asyncio.create_task(
                _run_ble_bridge(args, log_fp, udp_sock, udp_addr, ws_clients),
                name="ble_bridge",
            )
            done, pending = await asyncio.wait(
                {ws_task, ble_task}, return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass
            for t in done:
                exc = t.exception()
                if exc is not None:
                    print(f"[{t.get_name()}] crashed:", file=sys.stderr)
                    traceback.print_exception(type(exc), exc, exc.__traceback__)
        else:
            await _run_ble_bridge(args, log_fp, udp_sock, udp_addr, ws_clients)
    finally:
        if log_fp:
            log_fp.close()
        if udp_sock:
            udp_sock.close()


def _stdin_main(args) -> None:
    """No BLE: read raw POSTURE lines from another process (e.g. pipe from read_posture_ble)."""
    log_fp = open(args.log, "a", encoding="utf-8") if args.log else None
    udp_sock = None
    udp_addr = None
    if args.udp:
        host, _, ps = args.udp.rpartition(":")
        if not ps.isdigit():
            print("--udp must be host:port", file=sys.stderr)
            sys.exit(2)
        udp_sock = _open_udp(host or "127.0.0.1", int(ps))
        udp_addr = (host or "127.0.0.1", int(ps))
    try:
        for line in sys.stdin:
            evt = parse_posture_line(line)
            if not evt:
                continue
            _emit(
                evt,
                print_stdout=args.print_stdout,
                log_fp=log_fp,
                udp_sock=udp_sock,
                udp_addr=udp_addr,
            )
    finally:
        if log_fp:
            log_fp.close()
        if udp_sock:
            udp_sock.close()


def main() -> None:
    """CLI entry: BLE+outputs, or --stdin for piped raw lines."""
    p = argparse.ArgumentParser(description="Parse POSTURE lines → JSON; BLE or stdin")
    p.add_argument(
        "--stdin",
        action="store_true",
        help="Read raw POSTURE lines from stdin (pipe from read_posture_ble.py)",
    )
    p.add_argument(
        "--name",
        default=os.environ.get("DUCK_POSTURE_BLE_NAME", "DUCK Posture"),
        help="BLE name when using integrated BLE",
    )
    p.add_argument(
        "--address",
        default=os.environ.get("DUCK_POSTURE_BLE_ADDRESS"),
        help="BLE address (integrated BLE)",
    )
    p.add_argument("--timeout", type=float, default=15.0, help="BLE scan timeout (s)")
    p.add_argument(
        "--log",
        metavar="FILE",
        help="Append one JSON object per line (JSONL)",
    )
    p.add_argument(
        "--udp",
        metavar="HOST:PORT",
        help="Send each JSON object as one UTF-8 UDP datagram",
    )
    p.add_argument(
        "--ws-port",
        type=int,
        default=None,
        metavar="PORT",
        help="Run WebSocket server on this port; broadcast JSON to all clients",
    )
    p.add_argument(
        "--ws-host",
        default="127.0.0.1",
        help="WebSocket bind address (default 127.0.0.1)",
    )
    p.add_argument(
        "--no-print",
        action="store_true",
        help="Do not print JSON to stdout (use with --log / --udp / --ws-port)",
    )
    args = p.parse_args()
    args.address = (args.address or "").strip() or None
    args.print_stdout = not args.no_print

    if args.stdin:
        if args.ws_port is not None:
            print("--ws-port is not supported with --stdin", file=sys.stderr)
            sys.exit(2)
        _stdin_main(args)
        return

    try:
        asyncio.run(_async_main(args))
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        print(f"RuntimeError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Any other crash (BleakError, OSError, etc.) — print full traceback so
        # the failure is visible instead of a silent exit.
        print("Bridge crashed with unhandled exception:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
