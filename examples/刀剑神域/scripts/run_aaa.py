"""Runner: Execute AAA_build.py in Blender via socket"""

import json
import socket

s = socket.socket()
s.settimeout(180)
s.connect(("127.0.0.1", 9876))

code = """
import bpy
g = {"__builtins__": __builtins__, "bpy": bpy}
code = open(r"E:\\Projects\\blender-mcp\\examples\\刀剑神域\\scripts\\AAA_v2_kirito.py", encoding="utf-8").read()
exec(code, g)
"""

req = {
    "id": "aaa_build",
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
        print(output if output else "Success (no output)")
    else:
        err = resp.get("error", {})
        print(f"Error: {err.get('message', '?')}")
else:
    print("No response")
