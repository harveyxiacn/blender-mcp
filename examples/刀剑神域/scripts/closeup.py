import socket, json

s = socket.socket()
s.settimeout(30)
s.connect(('127.0.0.1', 9876))

code = (
    'import bpy, math\n'
    'cam = bpy.data.objects.get("MainCamera")\n'
    'if cam:\n'
    '    cam.location = (0, -3.5, 1.3)\n'
    '    cam.rotation_euler = (math.radians(88), 0, 0)\n'
    '    cam.data.lens = 50\n'
    'bpy.context.scene.render.filepath = r"E:\\Projects\\blender-mcp\\examples\\sao_closeup.png"\n'
    'bpy.context.scene.render.image_settings.file_format = "PNG"\n'
    'for area in bpy.context.screen.areas:\n'
    '    if area.type == "VIEW_3D":\n'
    '        for space in area.spaces:\n'
    '            if space.type == "VIEW_3D":\n'
    '                space.shading.type = "MATERIAL"\n'
    '                space.region_3d.view_perspective = "CAMERA"\n'
    '        override = bpy.context.copy()\n'
    '        override["area"] = area\n'
    '        with bpy.context.temp_override(**override):\n'
    '            bpy.ops.render.opengl(write_still=True)\n'
    '        break\n'
    'print("Closeup screenshot saved")\n'
)

req = {"id": "closeup", "type": "command", "category": "utility",
       "action": "execute_python", "params": {"code": code, "timeout": 30}}
s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

buf = ""
while "\n" not in buf:
    d = s.recv(8192)
    if not d: break
    buf += d.decode("utf-8")
s.close()

resp = json.loads(buf.strip()) if buf.strip() else {}
if resp.get("success"):
    print(resp.get("data", {}).get("output", "OK"))
else:
    print(f"Error: {resp.get('error', {}).get('message', '?')}")
