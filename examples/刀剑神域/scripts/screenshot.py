import json
import socket

s = socket.socket()
s.settimeout(10)
s.connect(("127.0.0.1", 9876))
req = {
    "id": "ss",
    "type": "command",
    "category": "utility",
    "action": "viewport_screenshot",
    "params": {
        "output_path": "E:/Projects/blender-mcp/examples/刀剑神域/sao_preview.png",
        "width": 1280,
        "height": 720,
    },
}
s.send((json.dumps(req, ensure_ascii=False) + "\n").encode())
buf = ""
while "\n" not in buf:
    d = s.recv(8192)
    if not d:
        break
    buf += d.decode()
r = json.loads(buf.strip())
if r.get("success"):
    print(f"Screenshot: {r['data']}")
else:
    print(f"Error: {r.get('error',{}).get('message','?')}")
s.close()
