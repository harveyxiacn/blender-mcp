"""
查询Blender场景中的对象
"""
import socket
import json
import time

def query_scene():
    """查询场景中的对象"""
    code = '''
import bpy

print("\\n=== Scene Objects ===")
print("Total objects:", len(bpy.data.objects))

# Group by collection
collections = {}
for obj in bpy.data.objects:
    col_names = [c.name for c in obj.users_collection]
    col_name = col_names[0] if col_names else "Scene Collection"
    if col_name not in collections:
        collections[col_name] = []
    collections[col_name].append(obj.name)

for col_name, objs in sorted(collections.items()):
    print("\\n[" + col_name + "] (" + str(len(objs)) + " objects):")
    for obj_name in sorted(objs)[:20]:
        print("  -", obj_name)
    if len(objs) > 20:
        print("  ... and", len(objs)-20, "more")

# Check for character objects
print("\\n=== Character Detection ===")
characters = []
for pfx in ["K_", "A_", "Klein_", "Asuna_", "Kirito_"]:
    char_objs = [o.name for o in bpy.data.objects if o.name.startswith(pfx)]
    if char_objs:
        characters.append((pfx, len(char_objs)))

if characters:
    for pfx, count in characters:
        print(pfx + ":", count, "objects")
else:
    print("No character objects detected")

# Check materials
print("\\nMaterials:", len(bpy.data.materials))
mat_names = [m.name for m in bpy.data.materials][:10]
if mat_names:
    print("Material list (first 10):")
    for m in mat_names:
        print("  -", m)
'''

    try:
        s = socket.socket()
        s.settimeout(30)
        s.connect(('127.0.0.1', 9876))

        req = {
            "id": f"query_{int(time.time())}",
            "type": "command",
            "category": "utility",
            "action": "execute_python",
            "params": {"code": code, "timeout": 30}
        }

        s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

        buf = ""
        while "\n" not in buf:
            d = s.recv(8192)
            if not d:
                break
            buf += d.decode("utf-8", errors='replace')

        s.close()

        if buf.strip():
            resp = json.loads(buf.strip())
            if resp.get("success"):
                output = resp.get("data", {}).get("output", "")
                print(output)
                return True
            else:
                err = resp.get("error", {})
                print(f"Error: {err.get('message', 'Unknown')}")
                return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    query_scene()
