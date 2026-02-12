import socket, json

s = socket.socket()
s.settimeout(30)
s.connect(('127.0.0.1', 9876))

# Frame all objects and take screenshot
code = '''
import bpy

# Switch to camera view and set viewport to material preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                # Frame all
                override = bpy.context.copy()
                override['area'] = area
                override['region'] = area.regions[-1]
                with bpy.context.temp_override(**override):
                    bpy.ops.view3d.view_all()
                break

# Render viewport to file
scene = bpy.context.scene
scene.render.filepath = r"E:\\Projects\\blender-mcp\\examples\\刀剑神域\\sao_aaa_preview.png"
scene.render.image_settings.file_format = 'PNG'

# Use OpenGL render
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        override = bpy.context.copy()
        override['area'] = area
        with bpy.context.temp_override(**override):
            bpy.ops.render.opengl(write_still=True)
        break

print(f"Screenshot saved: {scene.render.filepath}")
'''

req = {
    "id": "screenshot",
    "type": "command",
    "category": "utility",
    "action": "execute_python",
    "params": {"code": code, "timeout": 30}
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
        print(f"Error: {resp.get('error', {}).get('message', '?')}")
