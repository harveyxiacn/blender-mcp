"""
SAO 模型构建器 - 通过Socket直接调用Blender Addon API
使用现有 object.create / material.create / material.assign 等命令
"""

import json
import math
import socket
import sys


class BlenderSocket:
    def __init__(self, host="127.0.0.1", port=9876) -> None:
        self.host = host
        self.port = port
        self._id = 0

    def cmd(self, category, action, params=None):
        self._id += 1
        request = {
            "id": f"sao_{self._id}",
            "type": "command",
            "category": category,
            "action": action,
            "params": params or {},
        }
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        try:
            sock.connect((self.host, self.port))
            sock.send((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
            buf = ""
            while "\n" not in buf:
                d = sock.recv(8192)
                if not d:
                    break
                buf += d.decode("utf-8")
            resp = json.loads(buf.strip()) if buf.strip() else {}
            if not resp.get("success"):
                err = resp.get("error", {})
                print(f"    ✗ {category}.{action}: {err.get('message','unknown')}")
            return resp
        except Exception as e:
            print(f"    ✗ Connection error: {e}")
            return {}
        finally:
            sock.close()

    def create(
        self, obj_type, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mesh_params=None
    ):
        return self.cmd(
            "object",
            "create",
            {
                "type": obj_type,
                "name": name,
                "location": list(loc),
                "rotation": list(rot),
                "scale": list(scale),
                "mesh_params": mesh_params or {},
            },
        )

    def transform(self, name, loc=None, rot=None, scale=None):
        p = {"name": name}
        if loc:
            p["location"] = list(loc)
        if rot:
            p["rotation"] = list(rot)
        if scale:
            p["scale"] = list(scale)
        return self.cmd("object", "transform", p)

    def mat_create(self, name, color, metallic=0.0, roughness=0.5):
        return self.cmd(
            "material",
            "create",
            {
                "name": name,
                "color": list(color) + [1.0] if len(color) == 3 else list(color),
                "metallic": metallic,
                "roughness": roughness,
            },
        )

    def mat_assign(self, obj_name, mat_name):
        return self.cmd("material", "assign", {"object_name": obj_name, "material_name": mat_name})

    def light(self, name, loc, rot, energy, color) -> bool:
        """创建灯光(使用object.create然后调整)"""
        self.create("LIGHT", name, loc=loc, rot=rot)
        return True


B = BlenderSocket()

# ============================================================
print("\n" + "=" * 60)
print("  刀剑神域 SAO - Socket API 构建器")
print("=" * 60)

# 测试连接
r = B.cmd("system", "get_info")
if r.get("success"):
    d = r["data"]
    print(f"  Blender {d['version_string']} | 对象: {d['objects_count']}")
else:
    print("  ✗ 无法连接Blender! 请确保MCP服务在运行")
    sys.exit(1)

# ============================================================
# Phase 1: 场景设置
# ============================================================
print("\n[Phase 1] 创建集合和灯光...")

B.cmd("scene", "create", {"name": "SAO_Scene"})

# 灯光
B.create(
    "LIGHT",
    "SAO_KeyLight",
    loc=(5, -5, 10),
    rot=(math.radians(45), math.radians(15), math.radians(30)),
)
B.create(
    "LIGHT",
    "SAO_FillLight",
    loc=(-5, -3, 5),
    rot=(math.radians(60), math.radians(-30), math.radians(-20)),
)
B.create("LIGHT", "SAO_RimLight", loc=(0, 5, 8), rot=(math.radians(-30), 0, math.radians(180)))

# 摄像机
B.create("CAMERA", "SAO_Camera", loc=(0, -10, 1.5), rot=(math.radians(85), 0, 0))

print("  ✓ 灯光+摄像机")

# ============================================================
# Phase 2: 材质
# ============================================================
print("\n[Phase 2] 创建材质库...")

materials = {
    "SAO_Skin": ((0.95, 0.82, 0.73), 0.0, 0.6),
    "SAO_Skin_Dark": ((0.42, 0.26, 0.15), 0.0, 0.6),
    "SAO_Kirito_Black": ((0.04, 0.04, 0.04), 0.0, 0.7),
    "SAO_Kirito_Silver": ((0.75, 0.75, 0.75), 0.8, 0.3),
    "SAO_Kirito_Hair": ((0.04, 0.04, 0.06), 0.0, 0.5),
    "SAO_Asuna_White": ((0.96, 0.96, 0.96), 0.0, 0.4),
    "SAO_Asuna_Red": ((0.80, 0.20, 0.20), 0.0, 0.5),
    "SAO_Asuna_Gold": ((0.83, 0.69, 0.22), 0.8, 0.3),
    "SAO_Asuna_Hair": ((0.78, 0.46, 0.20), 0.0, 0.5),
    "SAO_Asuna_Eye": ((0.55, 0.41, 0.08), 0.0, 0.3),
    "SAO_Klein_Red": ((0.72, 0.26, 0.18), 0.0, 0.6),
    "SAO_Klein_Brown": ((0.29, 0.19, 0.13), 0.0, 0.7),
    "SAO_Klein_Hair": ((0.72, 0.26, 0.18), 0.0, 0.5),
    "SAO_Klein_Cream": ((0.91, 0.86, 0.78), 0.0, 0.6),
    "SAO_Metal_Silver": ((0.70, 0.70, 0.72), 0.9, 0.2),
    "SAO_Metal_Gold": ((0.83, 0.69, 0.22), 0.9, 0.2),
    "SAO_Metal_Dark": ((0.08, 0.08, 0.08), 0.95, 0.15),
    "SAO_Leather_Brown": ((0.29, 0.16, 0.08), 0.0, 0.7),
    "SAO_Fabric_White": ((0.92, 0.92, 0.90), 0.0, 0.8),
    "SAO_Eye_Black": ((0.02, 0.02, 0.02), 0.0, 0.3),
    "SAO_Eye_Highlight": ((1.0, 1.0, 1.0), 0.0, 0.0),
    "SAO_Elucidator": ((0.03, 0.03, 0.04), 0.95, 0.1),
    "SAO_LambentLight": ((0.91, 0.91, 0.94), 0.95, 0.05),
    "SAO_Sachi_Blue": ((0.17, 0.17, 0.43), 0.0, 0.5),
    "SAO_Sachi_Hair": ((0.10, 0.10, 0.31), 0.0, 0.5),
    "SAO_Liz_DarkRed": ((0.55, 0.13, 0.19), 0.0, 0.6),
    "SAO_Liz_Pink": ((0.91, 0.63, 0.69), 0.0, 0.5),
}

for name, (color, met, rough) in materials.items():
    B.mat_create(name, color, met, rough)

print(f"  ✓ {len(materials)} 种材质")

# ============================================================
# Phase 3: 桐人 (Kirito)
# ============================================================
print("\n[Phase 3] 构建桐人...")

# 躯干
B.create("CUBE", "CHR_Kirito_Torso", loc=(0, 0, 1.1), scale=(0.35, 0.20, 0.45))
B.mat_assign("CHR_Kirito_Torso", "SAO_Kirito_Black")

# 头
B.create(
    "UV_SPHERE",
    "CHR_Kirito_Head",
    loc=(0, 0, 1.72),
    scale=(1.0, 0.9, 1.05),
    mesh_params={"segments": 16, "ring_count": 12, "radius": 0.22},
)
B.mat_assign("CHR_Kirito_Head", "SAO_Skin")

# 颈
B.create(
    "CYLINDER",
    "CHR_Kirito_Neck",
    loc=(0, 0, 1.53),
    mesh_params={"vertices": 10, "radius": 0.06, "depth": 0.12},
)
B.mat_assign("CHR_Kirito_Neck", "SAO_Skin")

# 眼睛
for side, x in [("L", 0.08), ("R", -0.08)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Kirito_Eye_{side}",
        loc=(x, -0.18, 1.74),
        mesh_params={"segments": 12, "ring_count": 8, "radius": 0.045},
    )
    B.mat_assign(f"CHR_Kirito_Eye_{side}", "SAO_Eye_Black")
    B.create(
        "UV_SPHERE",
        f"CHR_Kirito_EyeHL_{side}",
        loc=(x + 0.02, -0.22, 1.76),
        mesh_params={"segments": 8, "ring_count": 6, "radius": 0.015},
    )
    B.mat_assign(f"CHR_Kirito_EyeHL_{side}", "SAO_Eye_Highlight")

# 手臂
for side, x in [("L", 0.45), ("R", -0.45)]:
    B.create(
        "CYLINDER",
        f"CHR_Kirito_Arm_{side}",
        loc=(x, 0, 1.1),
        mesh_params={"vertices": 12, "radius": 0.08, "depth": 0.55},
    )
    B.mat_assign(f"CHR_Kirito_Arm_{side}", "SAO_Kirito_Black")

# 手
for side, x in [("L", 0.45), ("R", -0.45)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Kirito_Hand_{side}",
        loc=(x, 0, 0.78),
        scale=(1.0, 0.7, 1.2),
        mesh_params={"segments": 10, "ring_count": 8, "radius": 0.06},
    )
    B.mat_assign(f"CHR_Kirito_Hand_{side}", "SAO_Skin")

# 腿
for side, x in [("L", 0.13), ("R", -0.13)]:
    B.create(
        "CYLINDER",
        f"CHR_Kirito_Leg_{side}",
        loc=(x, 0, 0.33),
        mesh_params={"vertices": 12, "radius": 0.09, "depth": 0.65},
    )
    B.mat_assign(f"CHR_Kirito_Leg_{side}", "SAO_Kirito_Black")

# 靴
for side, x in [("L", 0.13), ("R", -0.13)]:
    B.create("CUBE", f"CHR_Kirito_Boot_{side}", loc=(x, -0.02, 0.05), scale=(0.10, 0.15, 0.08))
    B.mat_assign(f"CHR_Kirito_Boot_{side}", "SAO_Kirito_Black")

# 头发基础
B.create(
    "UV_SPHERE",
    "CHR_Kirito_HairBase",
    loc=(0, 0.02, 1.76),
    scale=(1.05, 1.0, 1.0),
    mesh_params={"segments": 16, "ring_count": 12, "radius": 0.25},
)
B.mat_assign("CHR_Kirito_HairBase", "SAO_Kirito_Hair")

# 刘海 (5束)
bangs = [
    (-0.10, -0.20, 1.82, 0.15, 0.04, 15),
    (-0.04, -0.22, 1.84, 0.14, 0.035, 8),
    (0.03, -0.22, 1.83, 0.16, 0.04, -5),
    (0.09, -0.21, 1.81, 0.13, 0.035, -12),
    (0.00, -0.23, 1.85, 0.12, 0.03, 3),
]
for i, (x, y, z, ln, w, rot) in enumerate(bangs):
    B.create(
        "CONE",
        f"CHR_Kirito_Bang_{i}",
        loc=(x, y, z),
        rot=(math.radians(70), 0, math.radians(rot)),
        mesh_params={"vertices": 8, "radius1": w, "radius2": 0.005, "depth": ln},
    )
    B.mat_assign(f"CHR_Kirito_Bang_{i}", "SAO_Kirito_Hair")

# 侧发 (左右各3)
sides = [
    (0.20, -0.05, 1.72, 0.18, 0.04, 0, -25),
    (0.22, 0.02, 1.68, 0.20, 0.035, 5, -30),
    (0.18, -0.10, 1.75, 0.15, 0.03, -5, -20),
]
for mult in [1, -1]:
    sn = "L" if mult > 0 else "R"
    for i, (x, y, z, ln, w, rz, rx) in enumerate(sides):
        B.create(
            "CONE",
            f"CHR_Kirito_Side_{sn}_{i}",
            loc=(x * mult, y, z),
            rot=(math.radians(rx * mult * -1 + 90), 0, math.radians(rz * mult)),
            mesh_params={"vertices": 8, "radius1": w, "radius2": 0.008, "depth": ln},
        )
        B.mat_assign(f"CHR_Kirito_Side_{sn}_{i}", "SAO_Kirito_Hair")

# 后发 (4束)
backs = [
    (-0.08, 0.18, 1.70, 0.20, 0.05, -10),
    (0.00, 0.20, 1.72, 0.22, 0.05, 0),
    (0.08, 0.18, 1.70, 0.20, 0.05, 10),
    (0.00, 0.16, 1.65, 0.18, 0.04, 0),
]
for i, (x, y, z, ln, w, rz) in enumerate(backs):
    B.create(
        "CONE",
        f"CHR_Kirito_Back_{i}",
        loc=(x, y, z),
        rot=(math.radians(110), 0, math.radians(rz)),
        mesh_params={"vertices": 8, "radius1": w, "radius2": 0.01, "depth": ln},
    )
    B.mat_assign(f"CHR_Kirito_Back_{i}", "SAO_Kirito_Hair")

# 风衣(使用大锥体近似)
B.create(
    "CONE",
    "CHR_Kirito_Coat",
    loc=(0, 0, 0.88),
    mesh_params={"vertices": 16, "radius1": 0.50, "radius2": 0.35, "depth": 0.95},
)
B.mat_assign("CHR_Kirito_Coat", "SAO_Kirito_Black")

# 立领
B.create(
    "CYLINDER",
    "CHR_Kirito_Collar",
    loc=(0, 0, 1.48),
    scale=(1.2, 0.8, 1.0),
    mesh_params={"vertices": 16, "radius": 0.12, "depth": 0.08},
)
B.mat_assign("CHR_Kirito_Collar", "SAO_Kirito_Black")

# 腰带
B.create(
    "CYLINDER",
    "CHR_Kirito_Belt",
    loc=(0, 0, 0.88),
    scale=(1.0, 0.6, 1.0),
    mesh_params={"vertices": 16, "radius": 0.18, "depth": 0.06},
)
B.mat_assign("CHR_Kirito_Belt", "SAO_Leather_Brown")

# 肩扣
for side, x in [("L", 0.30), ("R", -0.30)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Kirito_Buckle_{side}",
        loc=(x, -0.10, 1.32),
        mesh_params={"segments": 8, "ring_count": 6, "radius": 0.025},
    )
    B.mat_assign(f"CHR_Kirito_Buckle_{side}", "SAO_Kirito_Silver")

print("  ✓ 桐人完成 (身体+头发+风衣)")

# ============================================================
# Phase 4: 逐暗者 (Elucidator)
# ============================================================
print("\n[Phase 4] 构建逐暗者...")
sx = 0.55

# 剑身
B.create("CUBE", "WPN_Elucidator_Blade", loc=(sx, -0.15, 0.95), scale=(0.015, 0.005, 0.42))
B.mat_assign("WPN_Elucidator_Blade", "SAO_Elucidator")

# 血槽
B.create("CUBE", "WPN_Elucidator_Fuller", loc=(sx, -0.15, 0.97), scale=(0.005, 0.002, 0.32))
B.mat_assign("WPN_Elucidator_Fuller", "SAO_Metal_Dark")

# 护手
B.create("CUBE", "WPN_Elucidator_Guard", loc=(sx, -0.15, 0.53), scale=(0.06, 0.015, 0.012))
B.mat_assign("WPN_Elucidator_Guard", "SAO_Metal_Dark")

# 护手球
for dx, s in [(0.06, "L"), (-0.06, "R")]:
    B.create(
        "UV_SPHERE",
        f"WPN_Eluc_Ball_{s}",
        loc=(sx + dx, -0.15, 0.53),
        mesh_params={"segments": 8, "ring_count": 6, "radius": 0.012},
    )
    B.mat_assign(f"WPN_Eluc_Ball_{s}", "SAO_Metal_Dark")

# 握柄
B.create(
    "CYLINDER",
    "WPN_Elucidator_Grip",
    loc=(sx, -0.15, 0.46),
    mesh_params={"vertices": 10, "radius": 0.012, "depth": 0.12},
)
B.mat_assign("WPN_Elucidator_Grip", "SAO_Leather_Brown")

# 柄头
B.create(
    "UV_SPHERE",
    "WPN_Elucidator_Pommel",
    loc=(sx, -0.15, 0.39),
    mesh_params={"segments": 8, "ring_count": 6, "radius": 0.015},
)
B.mat_assign("WPN_Elucidator_Pommel", "SAO_Metal_Dark")

print("  ✓ 逐暗者完成")

# ============================================================
# Phase 5: 亚丝娜 (Asuna)
# ============================================================
print("\n[Phase 5] 构建亚丝娜...")
ox = 1.5

# 躯干
B.create("CUBE", "CHR_Asuna_Torso", loc=(ox, 0, 1.05), scale=(0.30, 0.18, 0.40))
B.mat_assign("CHR_Asuna_Torso", "SAO_Asuna_White")

# 头
B.create(
    "UV_SPHERE",
    "CHR_Asuna_Head",
    loc=(ox, 0, 1.68),
    scale=(1.0, 0.88, 1.05),
    mesh_params={"segments": 16, "ring_count": 12, "radius": 0.20},
)
B.mat_assign("CHR_Asuna_Head", "SAO_Skin")

# 颈
B.create(
    "CYLINDER",
    "CHR_Asuna_Neck",
    loc=(ox, 0, 1.50),
    mesh_params={"vertices": 10, "radius": 0.055, "depth": 0.10},
)
B.mat_assign("CHR_Asuna_Neck", "SAO_Skin")

# 眼 (琥珀色)
for side, x in [("L", 0.07), ("R", -0.07)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Asuna_Eye_{side}",
        loc=(ox + x, -0.16, 1.70),
        mesh_params={"segments": 12, "ring_count": 8, "radius": 0.045},
    )
    B.mat_assign(f"CHR_Asuna_Eye_{side}", "SAO_Asuna_Eye")
    B.create(
        "UV_SPHERE",
        f"CHR_Asuna_EyeHL_{side}",
        loc=(ox + x + 0.02, -0.20, 1.72),
        mesh_params={"segments": 8, "ring_count": 6, "radius": 0.015},
    )
    B.mat_assign(f"CHR_Asuna_EyeHL_{side}", "SAO_Eye_Highlight")

# 手臂
for side, x in [("L", 0.40), ("R", -0.40)]:
    B.create(
        "CYLINDER",
        f"CHR_Asuna_Arm_{side}",
        loc=(ox + x, 0, 1.05),
        mesh_params={"vertices": 12, "radius": 0.065, "depth": 0.50},
    )
    B.mat_assign(f"CHR_Asuna_Arm_{side}", "SAO_Fabric_White")

# 手
for side, x in [("L", 0.40), ("R", -0.40)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Asuna_Hand_{side}",
        loc=(ox + x, 0, 0.75),
        scale=(1.0, 0.7, 1.2),
        mesh_params={"segments": 10, "ring_count": 8, "radius": 0.05},
    )
    B.mat_assign(f"CHR_Asuna_Hand_{side}", "SAO_Skin")

# 腿
for side, x in [("L", 0.11), ("R", -0.11)]:
    B.create(
        "CYLINDER",
        f"CHR_Asuna_Leg_{side}",
        loc=(ox + x, 0, 0.35),
        mesh_params={"vertices": 12, "radius": 0.075, "depth": 0.55},
    )
    B.mat_assign(f"CHR_Asuna_Leg_{side}", "SAO_Skin")

# 靴
for side, x in [("L", 0.11), ("R", -0.11)]:
    B.create("CUBE", f"CHR_Asuna_Boot_{side}", loc=(ox + x, -0.02, 0.06), scale=(0.08, 0.12, 0.08))
    B.mat_assign(f"CHR_Asuna_Boot_{side}", "SAO_Asuna_White")

# 头发
B.create(
    "UV_SPHERE",
    "CHR_Asuna_HairBase",
    loc=(ox, 0.02, 1.72),
    mesh_params={"segments": 16, "ring_count": 12, "radius": 0.23},
)
B.mat_assign("CHR_Asuna_HairBase", "SAO_Asuna_Hair")

# 长发
B.create("CUBE", "CHR_Asuna_LongHair", loc=(ox, 0.10, 1.30), scale=(0.20, 0.04, 0.55))
B.mat_assign("CHR_Asuna_LongHair", "SAO_Asuna_Hair")

# 刘海
a_bangs = [
    (-0.08, -0.18, 1.78, 0.12, 0.035, 12),
    (-0.02, -0.20, 1.80, 0.11, 0.03, 5),
    (0.04, -0.19, 1.79, 0.13, 0.035, -3),
    (0.10, -0.17, 1.77, 0.11, 0.03, -10),
]
for i, (x, y, z, ln, w, rot) in enumerate(a_bangs):
    B.create(
        "CONE",
        f"CHR_Asuna_Bang_{i}",
        loc=(ox + x, y, z),
        rot=(math.radians(70), 0, math.radians(rot)),
        mesh_params={"vertices": 8, "radius1": w, "radius2": 0.005, "depth": ln},
    )
    B.mat_assign(f"CHR_Asuna_Bang_{i}", "SAO_Asuna_Hair")

# 编辫
for side, sx2 in [("L", 0.15), ("R", -0.15)]:
    B.create(
        "CYLINDER",
        f"CHR_Asuna_Braid_{side}",
        loc=(ox + sx2, -0.08, 1.35),
        rot=(math.radians(10), 0, math.radians(5 if side == "L" else -5)),
        mesh_params={"vertices": 8, "radius": 0.025, "depth": 0.50},
    )
    B.mat_assign(f"CHR_Asuna_Braid_{side}", "SAO_Asuna_Hair")

# 发箍
B.create(
    "TORUS",
    "CHR_Asuna_Headband",
    loc=(ox, 0, 1.82),
    scale=(1.0, 0.9, 0.3),
    mesh_params={"major_radius": 0.22, "minor_radius": 0.012},
)
B.mat_assign("CHR_Asuna_Headband", "SAO_Fabric_White")

# === KoB战斗装 ===
# 胸甲
B.create("CUBE", "CHR_Asuna_ChestArmor", loc=(ox, -0.05, 1.12), scale=(0.32, 0.10, 0.25))
B.mat_assign("CHR_Asuna_ChestArmor", "SAO_Asuna_White")

# 红色十字
B.create("CUBE", "CHR_Asuna_Cross_H", loc=(ox, -0.16, 1.12), scale=(0.08, 0.005, 0.02))
B.mat_assign("CHR_Asuna_Cross_H", "SAO_Asuna_Red")
B.create("CUBE", "CHR_Asuna_Cross_V", loc=(ox, -0.16, 1.12), scale=(0.02, 0.005, 0.08))
B.mat_assign("CHR_Asuna_Cross_V", "SAO_Asuna_Red")

# 肩甲
for side, x in [("L", 0.32), ("R", -0.32)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Asuna_Shoulder_{side}",
        loc=(ox + x, 0, 1.28),
        scale=(1.0, 0.7, 0.5),
        mesh_params={"segments": 10, "ring_count": 8, "radius": 0.06},
    )
    B.mat_assign(f"CHR_Asuna_Shoulder_{side}", "SAO_Asuna_Red")

# 红裙
B.create(
    "CONE",
    "CHR_Asuna_SkirtOuter",
    loc=(ox, 0, 0.72),
    mesh_params={"vertices": 16, "radius1": 0.28, "radius2": 0.16, "depth": 0.25},
)
B.mat_assign("CHR_Asuna_SkirtOuter", "SAO_Asuna_Red")

# 白裙
B.create(
    "CONE",
    "CHR_Asuna_SkirtInner",
    loc=(ox, 0, 0.73),
    mesh_params={"vertices": 16, "radius1": 0.26, "radius2": 0.15, "depth": 0.22},
)
B.mat_assign("CHR_Asuna_SkirtInner", "SAO_Fabric_White")

# 腰带
B.create(
    "CYLINDER",
    "CHR_Asuna_Belt",
    loc=(ox, 0, 0.86),
    scale=(1.0, 0.65, 1.0),
    mesh_params={"vertices": 16, "radius": 0.16, "depth": 0.04},
)
B.mat_assign("CHR_Asuna_Belt", "SAO_Asuna_White")

print("  ✓ 亚丝娜完成 (身体+长发+KoB装)")

# ============================================================
# Phase 6: 闪光 (Lambent Light)
# ============================================================
print("\n[Phase 6] 构建闪光细剑...")
lx = ox + 0.45

# 剑身
B.create(
    "CYLINDER",
    "WPN_LL_Blade",
    loc=(lx, -0.12, 1.10),
    mesh_params={"vertices": 8, "radius": 0.005, "depth": 0.75},
)
B.mat_assign("WPN_LL_Blade", "SAO_LambentLight")

# 护手环
B.create(
    "TORUS",
    "WPN_LL_GuardRing",
    loc=(lx, -0.12, 0.72),
    rot=(math.radians(90), 0, 0),
    mesh_params={"major_radius": 0.04, "minor_radius": 0.005},
)
B.mat_assign("WPN_LL_GuardRing", "SAO_Metal_Silver")

# 护手横条
B.create(
    "CYLINDER",
    "WPN_LL_GuardBar",
    loc=(lx, -0.12, 0.72),
    rot=(0, math.radians(90), 0),
    mesh_params={"vertices": 8, "radius": 0.004, "depth": 0.08},
)
B.mat_assign("WPN_LL_GuardBar", "SAO_Metal_Silver")

# 握柄
B.create(
    "CYLINDER",
    "WPN_LL_Grip",
    loc=(lx, -0.12, 0.66),
    mesh_params={"vertices": 8, "radius": 0.010, "depth": 0.10},
)
B.mat_assign("WPN_LL_Grip", "SAO_Fabric_White")

# 柄头
B.create(
    "UV_SPHERE",
    "WPN_LL_Pommel",
    loc=(lx, -0.12, 0.60),
    mesh_params={"segments": 8, "ring_count": 6, "radius": 0.012},
)
B.mat_assign("WPN_LL_Pommel", "SAO_Metal_Silver")

print("  ✓ 闪光完成")

# ============================================================
# Phase 7: 克莱因 (Klein)
# ============================================================
print("\n[Phase 7] 构建克莱因...")
kx = -1.5

# 躯干
B.create("CUBE", "CHR_Klein_Torso", loc=(kx, 0, 1.1), scale=(0.38, 0.22, 0.45))
B.mat_assign("CHR_Klein_Torso", "SAO_Klein_Red")

# 头
B.create(
    "UV_SPHERE",
    "CHR_Klein_Head",
    loc=(kx, 0, 1.72),
    scale=(1.0, 0.92, 1.0),
    mesh_params={"segments": 16, "ring_count": 12, "radius": 0.22},
)
B.mat_assign("CHR_Klein_Head", "SAO_Skin")

# 颈
B.create(
    "CYLINDER",
    "CHR_Klein_Neck",
    loc=(kx, 0, 1.53),
    mesh_params={"vertices": 10, "radius": 0.07, "depth": 0.12},
)
B.mat_assign("CHR_Klein_Neck", "SAO_Skin")

# 眼 (细长)
for side, x in [("L", 0.08), ("R", -0.08)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Klein_Eye_{side}",
        loc=(kx + x, -0.18, 1.74),
        scale=(1.2, 1.0, 0.7),
        mesh_params={"segments": 12, "ring_count": 8, "radius": 0.035},
    )
    B.mat_assign(f"CHR_Klein_Eye_{side}", "SAO_Eye_Black")

# 手臂
for side, x in [("L", 0.48), ("R", -0.48)]:
    B.create(
        "CYLINDER",
        f"CHR_Klein_Arm_{side}",
        loc=(kx + x, 0, 1.1),
        mesh_params={"vertices": 12, "radius": 0.09, "depth": 0.55},
    )
    B.mat_assign(f"CHR_Klein_Arm_{side}", "SAO_Klein_Red")

# 手
for side, x in [("L", 0.48), ("R", -0.48)]:
    B.create(
        "UV_SPHERE",
        f"CHR_Klein_Hand_{side}",
        loc=(kx + x, 0, 0.78),
        mesh_params={"segments": 10, "ring_count": 8, "radius": 0.065},
    )
    B.mat_assign(f"CHR_Klein_Hand_{side}", "SAO_Skin")

# 腿
for side, x in [("L", 0.14), ("R", -0.14)]:
    B.create(
        "CYLINDER",
        f"CHR_Klein_Leg_{side}",
        loc=(kx + x, 0, 0.33),
        mesh_params={"vertices": 12, "radius": 0.11, "depth": 0.65},
    )
    B.mat_assign(f"CHR_Klein_Leg_{side}", "SAO_Klein_Cream")

# 凉鞋
for side, x in [("L", 0.14), ("R", -0.14)]:
    B.create(
        "CUBE", f"CHR_Klein_Sandal_{side}", loc=(kx + x, -0.02, 0.04), scale=(0.10, 0.14, 0.04)
    )
    B.mat_assign(f"CHR_Klein_Sandal_{side}", "SAO_Leather_Brown")

# 头发基础
B.create(
    "UV_SPHERE",
    "CHR_Klein_HairBase",
    loc=(kx, 0.02, 1.78),
    mesh_params={"segments": 14, "ring_count": 10, "radius": 0.24},
)
B.mat_assign("CHR_Klein_HairBase", "SAO_Klein_Hair")

# 刺猬发
spikes = [
    (0.00, -0.10, 1.95, 0.18, 0.05, 50, 0),
    (-0.10, -0.05, 1.98, 0.16, 0.04, 40, -15),
    (0.10, -0.05, 1.98, 0.16, 0.04, 40, 15),
    (-0.15, 0.05, 1.95, 0.14, 0.04, 20, -30),
    (0.15, 0.05, 1.95, 0.14, 0.04, 20, 30),
    (0.00, 0.15, 1.92, 0.15, 0.04, -10, 0),
    (-0.12, 0.12, 1.93, 0.13, 0.035, -5, -20),
    (0.12, 0.12, 1.93, 0.13, 0.035, -5, 20),
]
for i, (x, y, z, ln, w, rx, rz) in enumerate(spikes):
    B.create(
        "CONE",
        f"CHR_Klein_Spike_{i}",
        loc=(kx + x, y, z),
        rot=(math.radians(rx), 0, math.radians(rz)),
        mesh_params={"vertices": 6, "radius1": w, "radius2": 0.005, "depth": ln},
    )
    B.mat_assign(f"CHR_Klein_Spike_{i}", "SAO_Klein_Hair")

# 头带
B.create(
    "TORUS",
    "CHR_Klein_Headband",
    loc=(kx, 0, 1.80),
    scale=(1.0, 0.9, 0.3),
    mesh_params={"major_radius": 0.24, "minor_radius": 0.015},
)
B.mat_assign("CHR_Klein_Headband", "SAO_Klein_Red")

# 护胸甲
B.create("CUBE", "CHR_Klein_ChestArmor", loc=(kx, -0.05, 1.12), scale=(0.34, 0.08, 0.22))
B.mat_assign("CHR_Klein_ChestArmor", "SAO_Klein_Brown")

# 腰带
B.create(
    "CYLINDER",
    "CHR_Klein_Belt",
    loc=(kx, 0, 0.88),
    scale=(1.0, 0.6, 1.0),
    mesh_params={"vertices": 16, "radius": 0.19, "depth": 0.06},
)
B.mat_assign("CHR_Klein_Belt", "SAO_Leather_Brown")

# 武士刀
B.create(
    "CUBE",
    "WPN_Katana_Blade",
    loc=(kx - 0.25, -0.10, 0.95),
    scale=(0.012, 0.004, 0.40),
    rot=(0, 0, math.radians(-5)),
)
B.mat_assign("WPN_Katana_Blade", "SAO_Metal_Silver")

B.create(
    "CYLINDER",
    "WPN_Katana_Tsuba",
    loc=(kx - 0.25, -0.10, 0.55),
    mesh_params={"vertices": 16, "radius": 0.025, "depth": 0.005},
)
B.mat_assign("WPN_Katana_Tsuba", "SAO_Metal_Dark")

B.create(
    "CYLINDER",
    "WPN_Katana_Handle",
    loc=(kx - 0.25, -0.10, 0.47),
    mesh_params={"vertices": 10, "radius": 0.012, "depth": 0.15},
)
B.mat_assign("WPN_Katana_Handle", "SAO_Klein_Red")

print("  ✓ 克莱因完成 (身体+刺猬发+武士装+武士刀)")

# ============================================================
print("\n" + "=" * 60)
print("  SAO 构建完成!")
print("=" * 60)
r = B.cmd("system", "get_info")
if r.get("success"):
    print(f"  场景对象总数: {r['data']['objects_count']}")
print("  ✓ 桐人 + 逐暗者")
print("  ✓ 亚丝娜 + 闪光")
print("  ✓ 克莱因 + 武士刀")
print("  ✓ 27种SAO材质")
print("  ✓ 三点光照 + 摄像机")
print("=" * 60)
