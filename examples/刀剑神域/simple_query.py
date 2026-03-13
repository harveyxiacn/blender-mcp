"""
简单查询Blender场景
"""

import json
import socket
import time

code = """
import bpy

print("=== Scene Info ===")
print("Total objects:", len(bpy.data.objects))
print("Total materials:", len(bpy.data.materials))

print("\\n=== Object Names (first 30) ===")
for i, obj in enumerate(list(bpy.data.objects)[:30]):
    print(obj.name)

print("\\n=== Material Names (first 20) ===")
for i, mat in enumerate(list(bpy.data.materials)[:20]):
    print(mat.name)

# Count character objects
k_count = len([o for o in bpy.data.objects if o.name.startswith("K_")])
a_count = len([o for o in bpy.data.objects if o.name.startswith("A_")])
klein_count = len([o for o in bpy.data.objects if o.name.startswith("Klein")])

print("\\n=== Character Objects ===")
print("K_ objects:", k_count)
print("A_ objects:", a_count)
print("Klein objects:", klein_count)
"""

try:
    s = socket.socket()
    s.settimeout(30)
    s.connect(("127.0.0.1", 9876))

    req = {
        "id": f"query_{int(time.time())}",
        "type": "command",
        "category": "utility",
        "action": "execute_python",
        "params": {"code": code, "timeout": 30},
    }

    s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

    buf = ""
    while "\n" not in buf:
        d = s.recv(8192)
        if not d:
            break
        buf += d.decode("utf-8", errors="replace")

    s.close()

    if buf.strip():
        resp = json.loads(buf.strip())
        if resp.get("success"):
            output = resp.get("data", {}).get("output", "")
            print(output)
        else:
            err = resp.get("error", {})
            print(f"Error: {err.get('message', 'Unknown')}")

except Exception as e:
    print(f"Error: {e}")
