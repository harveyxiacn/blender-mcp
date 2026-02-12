"""
新模块测试脚本 - 测试 simulation, hair, assets, addons, world, constraints
"""

import sys
import io

import asyncio
import socket
import json


def ensure_utf8_stdout() -> None:
    """仅在脚本直跑时调整 stdout 编码，避免影响 pytest 捕获"""
    if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "").lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TestClient:
    def __init__(self, host="127.0.0.1", port=9876):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 0
    
    async def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(False)
        print("[OK] Connected to Blender MCP")
    
    async def send(self, category, action, params=None):
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": f"{category}.{action}",
            "params": params or {}
        }
        data = json.dumps(request).encode('utf-8')
        length_prefix = len(data).to_bytes(4, byteorder='big')
        
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.socket, length_prefix + data)
        
        length_data = await loop.sock_recv(self.socket, 4)
        length = int.from_bytes(length_data, byteorder='big')
        response_data = b""
        while len(response_data) < length:
            chunk = await loop.sock_recv(self.socket, length - len(response_data))
            response_data += chunk
        
        return json.loads(response_data.decode('utf-8'))
    
    async def close(self):
        if self.socket:
            self.socket.close()


async def test(client, name, cat, act, params=None):
    try:
        r = await client.send(cat, act, params)
        if "result" in r and r["result"].get("success"):
            print(f"  [PASS] {name}")
            return True
        else:
            err = r.get("result", {}).get("error", {}).get("message", r.get("error", {}).get("message", "unknown"))
            print(f"  [FAIL] {name}: {err}")
            return False
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


async def main():
    print("=" * 60)
    print("NEW MODULES TEST - simulation, hair, assets, addons, world, constraints")
    print("=" * 60)
    
    client = TestClient()
    await client.connect()
    
    results = []
    
    # Clear scene
    await client.send("scene", "clear", {"keep_camera": True, "keep_light": True})
    
    # === SIMULATION ===
    print("\n--- Testing SIMULATION tools ---")
    await client.send("object", "create", {"type": "CUBE", "name": "FluidDomain", "location": [0, 0, 2], "scale": [2, 2, 2]})
    await client.send("object", "create", {"type": "SPHERE", "name": "FluidSource", "location": [0, 0, 3], "scale": [0.3, 0.3, 0.3]})
    await client.send("object", "create", {"type": "PLANE", "name": "OceanPlane", "location": [5, 0, 0], "scale": [3, 3, 1]})
    
    results.append(await test(client, "simulation.fluid_domain", "simulation", "fluid_domain", 
        {"object_name": "FluidDomain", "domain_type": "LIQUID", "resolution": 32}))
    results.append(await test(client, "simulation.fluid_flow", "simulation", "fluid_flow",
        {"object_name": "FluidSource", "flow_type": "INFLOW"}))
    results.append(await test(client, "simulation.ocean", "simulation", "ocean",
        {"object_name": "OceanPlane", "resolution": 5, "spatial_size": 20}))
    
    # === HAIR ===
    print("\n--- Testing HAIR tools ---")
    await client.send("object", "create", {"type": "SPHERE", "name": "HairSphere", "location": [10, 0, 0]})
    
    results.append(await test(client, "hair.add", "hair", "add",
        {"object_name": "HairSphere", "name": "TestHair", "hair_length": 0.2, "hair_count": 500}))
    results.append(await test(client, "hair.settings", "hair", "settings",
        {"object_name": "HairSphere", "hair_length": 0.3}))
    results.append(await test(client, "hair.children", "hair", "children",
        {"object_name": "HairSphere", "child_type": "INTERPOLATED", "child_count": 5}))
    results.append(await test(client, "hair.material", "hair", "material",
        {"object_name": "HairSphere", "color": [0.2, 0.1, 0.05, 1.0]}))
    
    # === ASSETS ===
    print("\n--- Testing ASSETS tools ---")
    await client.send("object", "create", {"type": "CUBE", "name": "AssetCube", "location": [15, 0, 0]})
    
    results.append(await test(client, "assets.mark", "assets", "mark",
        {"object_name": "AssetCube", "description": "Test asset", "tags": ["test"]}))
    results.append(await test(client, "assets.catalog", "assets", "catalog",
        {"action": "LIST"}))
    results.append(await test(client, "assets.search", "assets", "search",
        {"query": "asset"}))
    results.append(await test(client, "assets.preview", "assets", "preview",
        {"object_name": "AssetCube"}))
    results.append(await test(client, "assets.clear", "assets", "clear",
        {"object_name": "AssetCube"}))
    
    # === ADDONS ===
    print("\n--- Testing ADDONS tools ---")
    results.append(await test(client, "addons.list", "addons", "list", {}))
    results.append(await test(client, "addons.info", "addons", "info",
        {"addon_name": "blender_mcp_addon"}))
    
    # === WORLD ===
    print("\n--- Testing WORLD tools ---")
    results.append(await test(client, "world.create", "world", "create",
        {"name": "TestWorld", "use_nodes": True}))
    results.append(await test(client, "world.background", "world", "background",
        {"color": [0.1, 0.2, 0.4], "strength": 1.0}))
    results.append(await test(client, "world.sky", "world", "sky",
        {"sky_type": "NISHITA", "sun_elevation": 0.5}))
    results.append(await test(client, "world.fog", "world", "fog",
        {"use_fog": True, "density": 0.005}))
    results.append(await test(client, "world.ambient_occlusion", "world", "ambient_occlusion",
        {"use_ao": True, "distance": 1.0}))
    
    # === CONSTRAINTS ===
    print("\n--- Testing CONSTRAINTS tools ---")
    await client.send("object", "create", {"type": "CUBE", "name": "ConstraintCube", "location": [20, 0, 0]})
    await client.send("object", "create", {"type": "EMPTY", "name": "ConstraintTarget", "location": [20, 2, 0]})
    
    results.append(await test(client, "constraints.copy_location", "constraints", "copy_location",
        {"object_name": "ConstraintCube", "target": "ConstraintTarget", "influence": 0.5}))
    results.append(await test(client, "constraints.copy_rotation", "constraints", "copy_rotation",
        {"object_name": "ConstraintCube", "target": "ConstraintTarget"}))
    results.append(await test(client, "constraints.track_to", "constraints", "track_to",
        {"object_name": "ConstraintCube", "target": "ConstraintTarget"}))
    results.append(await test(client, "constraints.limit", "constraints", "limit",
        {"object_name": "ConstraintCube", "limit_type": "LOCATION", "min_x": -5, "max_x": 5}))
    results.append(await test(client, "constraints.list", "constraints", "list",
        {"object_name": "ConstraintCube"}))
    
    # Summary
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"NEW MODULES TEST: {passed}/{total} passed")
    print("=" * 60)
    
    await client.close()


if __name__ == "__main__":
    ensure_utf8_stdout()
    asyncio.run(main())
