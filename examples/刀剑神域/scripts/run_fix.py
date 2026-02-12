"""Runner: Execute fix script in Blender via socket"""
import socket, json

s = socket.socket()
s.settimeout(60)
s.connect(('127.0.0.1', 9876))

code = '''
import bpy
g = {"__builtins__": __builtins__, "bpy": bpy}
code = open(r"E:\\Projects\\blender-mcp\\examples\\刀剑神域\\scripts\\fix_v2.py", encoding="utf-8").read()
exec(code, g)
'''

req = {
    "id": "fix",
    "type": "command",
    "category": "utility",
    "action": "execute_python",
    "params": {"code": code, "timeout": 60}
}

s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

buf = ""
while "\n" not in buf:
    d = s.recv(8192)
    if not d: break
    buf += d.decode("utf-8")
s.close()

if buf.strip():
    resp = json.loads(buf.strip())
    if resp.get("success"):
        print(resp.get("data", {}).get("output", "OK"))
    else:
        print(f"ERROR: {resp.get('error', {}).get('message', '?')}")
