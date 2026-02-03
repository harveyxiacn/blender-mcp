"""
新工具综合测试脚本

测试新增的工具模块:
- simulation (高级模拟)
- hair (毛发系统)
- assets (资产管理)
- addons (插件管理)
- world (世界/环境)
- constraints (约束系统)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
import socket
import json
import time


class BlenderMCPTestClient:
    """测试客户端"""
    
    def __init__(self, host="127.0.0.1", port=9876):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 0
    
    async def connect(self):
        """连接到 Blender"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(False)
        print(f"[OK] 已连接到 Blender ({self.host}:{self.port})")
    
    async def send_command(self, category: str, action: str, params: dict = None):
        """发送命令"""
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
        
        # 接收响应
        length_data = await loop.sock_recv(self.socket, 4)
        if len(length_data) < 4:
            raise Exception("连接关闭")
        
        length = int.from_bytes(length_data, byteorder='big')
        response_data = b""
        while len(response_data) < length:
            chunk = await loop.sock_recv(self.socket, length - len(response_data))
            if not chunk:
                raise Exception("连接关闭")
            response_data += chunk
        
        return json.loads(response_data.decode('utf-8'))
    
    async def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()


async def run_test(client, name, category, action, params=None, expected_success=True):
    """运行单个测试"""
    try:
        result = await client.send_command(category, action, params)
        
        if "result" in result:
            success = result["result"].get("success", False)
            if success == expected_success:
                print(f"  [PASS] {name}")
                return True
            else:
                error = result["result"].get("error", {})
                print(f"  [FAIL] {name}: {error.get('message', '未知错误')}")
                return False
        else:
            error = result.get("error", {})
            print(f"  [FAIL] {name}: {error.get('message', '未知错误')}")
            return False
    
    except Exception as e:
        print(f"  [FAIL] {name}: 异常 - {e}")
        return False


async def test_simulation(client):
    """测试高级模拟工具"""
    print("\n=== 测试 Simulation 模块 ===")
    results = []
    
    # 先创建测试对象
    await client.send_command("object", "create", {"type": "CUBE", "name": "SimDomain", "location": [0, 0, 2], "scale": [3, 3, 3]})
    await client.send_command("object", "create", {"type": "SPHERE", "name": "SimFlow", "location": [0, 0, 3], "scale": [0.3, 0.3, 0.3]})
    await client.send_command("object", "create", {"type": "PLANE", "name": "OceanPlane", "location": [0, 0, 0], "scale": [5, 5, 1]})
    
    # 流体域
    results.append(await run_test(client, "fluid_domain", "simulation", "fluid_domain", {
        "object_name": "SimDomain",
        "domain_type": "LIQUID",
        "resolution": 32
    }))
    
    # 流体流入
    results.append(await run_test(client, "fluid_flow", "simulation", "fluid_flow", {
        "object_name": "SimFlow",
        "flow_type": "INFLOW"
    }))
    
    # 海洋
    results.append(await run_test(client, "ocean", "simulation", "ocean", {
        "object_name": "OceanPlane",
        "resolution": 5,
        "spatial_size": 20
    }))
    
    return results


async def test_hair(client):
    """测试毛发系统"""
    print("\n=== 测试 Hair 模块 ===")
    results = []
    
    # 创建测试对象
    await client.send_command("object", "create", {"type": "SPHERE", "name": "HairBase", "location": [5, 0, 0]})
    
    # 添加毛发
    results.append(await run_test(client, "hair_add", "hair", "add", {
        "object_name": "HairBase",
        "name": "TestHair",
        "hair_length": 0.2,
        "hair_count": 500
    }))
    
    # 毛发设置
    results.append(await run_test(client, "hair_settings", "hair", "settings", {
        "object_name": "HairBase",
        "hair_length": 0.3
    }))
    
    # 毛发子代
    results.append(await run_test(client, "hair_children", "hair", "children", {
        "object_name": "HairBase",
        "child_type": "INTERPOLATED",
        "child_count": 5
    }))
    
    # 毛发材质
    results.append(await run_test(client, "hair_material", "hair", "material", {
        "object_name": "HairBase",
        "color": [0.2, 0.1, 0.05, 1.0]
    }))
    
    return results


async def test_assets(client):
    """测试资产管理"""
    print("\n=== 测试 Assets 模块 ===")
    results = []
    
    # 创建测试对象
    await client.send_command("object", "create", {"type": "CUBE", "name": "AssetCube", "location": [10, 0, 0]})
    
    # 标记为资产
    results.append(await run_test(client, "asset_mark", "assets", "mark", {
        "object_name": "AssetCube",
        "description": "测试资产",
        "tags": ["test", "cube"]
    }))
    
    # 列出资产
    results.append(await run_test(client, "asset_catalog", "assets", "catalog", {
        "action": "LIST"
    }))
    
    # 搜索资产
    results.append(await run_test(client, "asset_search", "assets", "search", {
        "query": "asset"
    }))
    
    # 生成预览
    results.append(await run_test(client, "asset_preview", "assets", "preview", {
        "object_name": "AssetCube"
    }))
    
    # 清除资产
    results.append(await run_test(client, "asset_clear", "assets", "clear", {
        "object_name": "AssetCube"
    }))
    
    return results


async def test_addons(client):
    """测试插件管理"""
    print("\n=== 测试 Addons 模块 ===")
    results = []
    
    # 列出插件
    results.append(await run_test(client, "addon_list", "addons", "list", {}))
    
    # 获取插件信息
    results.append(await run_test(client, "addon_info", "addons", "info", {
        "addon_name": "blender_mcp_addon"
    }))
    
    return results


async def test_world(client):
    """测试世界/环境设置"""
    print("\n=== 测试 World 模块 ===")
    results = []
    
    # 创建世界
    results.append(await run_test(client, "world_create", "world", "create", {
        "name": "TestWorld",
        "use_nodes": True
    }))
    
    # 设置背景
    results.append(await run_test(client, "world_background", "world", "background", {
        "color": [0.1, 0.2, 0.3],
        "strength": 1.0
    }))
    
    # 设置天空
    results.append(await run_test(client, "world_sky", "world", "sky", {
        "sky_type": "NISHITA",
        "sun_elevation": 0.5
    }))
    
    # 设置雾
    results.append(await run_test(client, "world_fog", "world", "fog", {
        "use_fog": True,
        "density": 0.005
    }))
    
    # 设置AO
    results.append(await run_test(client, "world_ambient_occlusion", "world", "ambient_occlusion", {
        "use_ao": True,
        "distance": 1.0
    }))
    
    return results


async def test_constraints(client):
    """测试约束系统"""
    print("\n=== 测试 Constraints 模块 ===")
    results = []
    
    # 创建测试对象
    await client.send_command("object", "create", {"type": "CUBE", "name": "ConstraintCube", "location": [15, 0, 0]})
    await client.send_command("object", "create", {"type": "EMPTY", "name": "ConstraintTarget", "location": [15, 2, 0]})
    
    # 位置约束
    results.append(await run_test(client, "copy_location", "constraints", "copy_location", {
        "object_name": "ConstraintCube",
        "target": "ConstraintTarget",
        "use_x": True,
        "use_y": True,
        "use_z": False,
        "influence": 0.5
    }))
    
    # 旋转约束
    results.append(await run_test(client, "copy_rotation", "constraints", "copy_rotation", {
        "object_name": "ConstraintCube",
        "target": "ConstraintTarget",
        "influence": 1.0
    }))
    
    # 跟踪约束
    results.append(await run_test(client, "track_to", "constraints", "track_to", {
        "object_name": "ConstraintCube",
        "target": "ConstraintTarget",
        "track_axis": "TRACK_NEGATIVE_Z",
        "up_axis": "UP_Y"
    }))
    
    # 限制约束
    results.append(await run_test(client, "limit", "constraints", "limit", {
        "object_name": "ConstraintCube",
        "limit_type": "LOCATION",
        "min_x": -5,
        "max_x": 5
    }))
    
    # 列出约束
    results.append(await run_test(client, "constraint_list", "constraints", "list", {
        "object_name": "ConstraintCube"
    }))
    
    return results


async def main():
    """主测试函数"""
    print("=" * 60)
    print("Blender MCP 新工具综合测试")
    print("=" * 60)
    
    client = BlenderMCPTestClient()
    
    try:
        await client.connect()
        
        # 清空场景
        print("\n准备测试环境...")
        await client.send_command("scene", "clear", {"keep_camera": True, "keep_light": True})
        
        all_results = []
        
        # 测试各模块
        all_results.extend(await test_simulation(client))
        all_results.extend(await test_hair(client))
        all_results.extend(await test_assets(client))
        all_results.extend(await test_addons(client))
        all_results.extend(await test_world(client))
        all_results.extend(await test_constraints(client))
        
        # 统计结果
        passed = sum(all_results)
        total = len(all_results)
        
        print("\n" + "=" * 60)
        print(f"测试完成: {passed}/{total} 通过")
        print("=" * 60)
        
        if passed == total:
            print("所有测试通过!")
        else:
            print(f"有 {total - passed} 个测试失败")
    
    except Exception as e:
        print(f"\n测试出错: {e}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
