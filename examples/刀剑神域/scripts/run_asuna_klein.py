"""Runner: Execute Asuna + Klein scripts in Blender via socket"""

import json
import socket
import time


def run_script(filepath, label) -> bool:
    print(f"\n{'='*50}")
    print(f"  Running: {label}")
    print(f"{'='*50}")

    s = socket.socket()
    s.settimeout(180)
    s.connect(("127.0.0.1", 9876))

    code = f"""
import bpy
g = {{"__builtins__": __builtins__, "bpy": bpy}}
code = open(r"{filepath}", encoding="utf-8").read()
exec(code, g)
"""

    req = {
        "id": label,
        "type": "command",
        "category": "utility",
        "action": "execute_python",
        "params": {"code": code, "timeout": 120},
    }

    s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

    buf = ""
    while "\n" not in buf:
        d = s.recv(8192)
        if not d:
            break
        buf += d.decode("utf-8")
    s.close()

    if buf.strip():
        resp = json.loads(buf.strip())
        if resp.get("success"):
            output = resp.get("data", {}).get("output", "")
            print(output if output else "OK")
        else:
            err = resp.get("error", {})
            print(f"ERROR: {err.get('message', '?')}")
            return False
    return True


base = r"E:\\Projects\\blender-mcp\\examples\\刀剑神域\\scripts"

run_script(f"{base}\\AAA_v2_asuna.py", "Asuna + Lambent Light")
time.sleep(1)
run_script(f"{base}\\AAA_v2_klein.py", "Klein + Katana + Elucidator")

print("\n" + "=" * 50)
print("  ALL DONE!")
print("=" * 50)
