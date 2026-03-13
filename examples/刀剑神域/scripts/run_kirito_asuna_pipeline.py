"""Run Kirito + Asuna build/pose pipeline through Blender MCP socket."""

from __future__ import annotations

import contextlib
import json
import socket
import sys
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 9876
TIMEOUT = 300

BASE_DIR = Path(__file__).resolve().parent
PIPELINE = [
    ("AAA_v2_kirito.py", "Build Kirito"),
    ("AAA_v2_asuna.py", "Build Asuna + Lambent Light"),
    ("AAA_pose_kirito_asuna.py", "Bind Weapons + Action Keys"),
]


def recv_json_line(sock: socket.socket) -> dict:
    buffer = ""
    while "\n" not in buffer:
        chunk = sock.recv(8192)
        if not chunk:
            break
        buffer += chunk.decode("utf-8", errors="replace")
    line = buffer.split("\n", 1)[0].strip()
    if not line:
        raise RuntimeError("No response from Blender MCP")
    return json.loads(line)


def execute_script(script_path: Path, timeout: int = TIMEOUT) -> tuple[bool, str]:
    code = f"""
import bpy
path = r"{script_path}"
ns = {{"__name__": "__main__", "__file__": path, "__builtins__": __builtins__}}
with open(path, "r", encoding="utf-8") as f:
    src = f.read()
exec(compile(src, path, "exec"), ns)
"""
    request = {
        "id": f"run-{int(time.time()*1000)}",
        "type": "command",
        "category": "utility",
        "action": "execute_python",
        "params": {"code": code, "timeout": timeout},
    }

    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((HOST, PORT))
        sock.send((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
        resp = recv_json_line(sock)
    finally:
        sock.close()

    if resp.get("success"):
        output = resp.get("data", {}).get("output", "").strip()
        return True, output

    err = resp.get("error", {}).get("message", "Unknown error")
    return False, err


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(Exception):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"Blender MCP target: {HOST}:{PORT}")
    for filename, label in PIPELINE:
        script_path = BASE_DIR / filename
        if not script_path.exists():
            print(f"[FAIL] Missing script: {script_path}")
            return 1

        print(f"\n{'=' * 60}")
        print(f"[RUN] {label}")
        print(f"Script: {script_path}")
        print(f"{'=' * 60}")

        ok, message = execute_script(script_path)
        if not ok:
            print(f"[FAIL] {label}: {message}")
            return 2

        if message:
            print(message.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
        else:
            print("[OK] Completed with empty output.")

    print("\n[OK] Pipeline completed.")
    print("Output blend: E:\\Projects\\blender-mcp\\examples\\sao_kirito_asuna_action.blend")
    print("Output still: E:\\Projects\\blender-mcp\\examples\\sao_kirito_asuna_action_f24.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
