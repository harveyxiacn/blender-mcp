"""
============================================================
  刀剑神域 SAO - AAA级3D模型构建脚本
  直接在Blender中执行 (通过MCP execute_python)

  技术规格:
  - BMesh拓扑建模 (截面放样)
  - SubSurf细分曲面 Lv2
  - Solidify描边 (赛璐璐风格)
  - 多层Toon材质 (Diffuse→ShaderToRGB→ColorRamp + Fresnel轮廓光)
  - 正确人体比例 (7.5头身)
  - 16边截面精度
============================================================
"""

import math

import bmesh
import bpy

# ============================================================
# 工具函数库
# ============================================================


def loft_mesh(name, profiles, ns=16, cap_top=False, cap_bot=False):
    """截面放样建模
    profiles: [(z, rx, ry, ox, oy), ...]
    z=高度, rx/ry=X/Y半径, ox/oy=中心偏移"""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for z, rx, ry, ox, oy in profiles:
        ring = []
        for i in range(ns):
            a = 2 * math.pi * i / ns
            x = ox + rx * math.cos(a)
            y = oy + ry * math.sin(a)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for r in range(len(rings) - 1):
        for i in range(ns):
            v1, v2 = rings[r][i], rings[r][(i + 1) % ns]
            v3, v4 = rings[r + 1][(i + 1) % ns], rings[r + 1][i]
            bm.faces.new([v1, v4, v3, v2])
    if cap_bot and rings:
        bm.faces.new(rings[0])
    if cap_top and rings:
        bm.faces.new(list(reversed(rings[-1])))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def loft_half(name, profiles, ns=8):
    """半截面放样 (用于Mirror修改器)
    只生成X>=0的半边, profiles: [(z, rx, ry, ox, oy)]"""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for z, rx, ry, ox, oy in profiles:
        ring = []
        for i in range(ns + 1):
            a = math.pi * i / ns  # 0到pi
            x = ox + rx * math.cos(a)
            y = oy + ry * math.sin(a)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for r in range(len(rings) - 1):
        n = ns + 1
        for i in range(n - 1):
            v1, v2 = rings[r][i], rings[r][i + 1]
            v3, v4 = rings[r + 1][i + 1], rings[r + 1][i]
            bm.faces.new([v1, v4, v3, v2])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    # 添加Mirror
    mir = obj.modifiers.new("Mirror", "MIRROR")
    mir.use_axis[0] = True
    mir.use_clip = True
    return obj


def setup_obj(obj, mat_name, col_name="Characters", subsurf=2, outline=0.003) -> None:
    """统一设置: 材质+集合+SubSurf+描边+平滑"""
    # 材质
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    # 集合
    col = bpy.data.collections.get(col_name)
    if col:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
    # SubSurf
    if subsurf > 0:
        m = obj.modifiers.new("SubSurf", "SUBSURF")
        m.levels = subsurf
        m.render_levels = subsurf
    # 平滑
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    # 描边
    if outline > 0:
        om = bpy.data.materials.get("M_Outline")
        if om:
            m = obj.modifiers.new("Outline", "SOLIDIFY")
            m.thickness = outline
            m.offset = -1
            m.use_flip_normals = True
            m.material_offset = len(obj.data.materials)
            obj.data.materials.append(om)


def make_eye(name, loc, radius=0.038, mat="M_EyeBlack"):
    """创建动漫风格眼睛 (椭圆形)"""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=radius, location=loc)
    eye = bpy.context.active_object
    eye.name = name
    eye.scale = (1.0, 0.65, 1.25)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(eye, mat, subsurf=1, outline=0)
    return eye


def make_highlight(name, loc, radius=0.012):
    """眼睛高光"""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=radius, location=loc)
    hl = bpy.context.active_object
    hl.name = name
    setup_obj(hl, "M_EyeHighlight", subsurf=0, outline=0)
    return hl


# ============================================================
# 桐人 (Kirito) - AAA级
# ============================================================
print("\n[Kirito] 开始高精度建模...")

# --- 躯干 (截面放样) ---
torso_profiles = [
    # (z,    rx,   ry,   ox,  oy)
    (0.82, 0.145, 0.095, 0, 0),  # 腰部
    (0.88, 0.150, 0.100, 0, 0),  # 腰上
    (0.95, 0.155, 0.105, 0, 0),  # 下胸
    (1.05, 0.175, 0.115, 0, 0),  # 胸部
    (1.15, 0.185, 0.120, 0, 0),  # 上胸
    (1.25, 0.190, 0.110, 0, 0),  # 锁骨
    (1.33, 0.175, 0.095, 0, 0),  # 肩膀
    (1.38, 0.100, 0.070, 0, 0),  # 肩颈
    (1.42, 0.055, 0.050, 0, 0),  # 颈底
    (1.48, 0.048, 0.045, 0, 0),  # 颈中
    (1.52, 0.045, 0.042, 0, 0),  # 颈顶
]
torso = loft_mesh("K_Torso", torso_profiles, ns=16)
setup_obj(torso, "M_KiritoBlack", outline=0.004)

# --- 头部 ---
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24, ring_count=16, radius=0.115, location=(0, 0, 1.66)
)
head = bpy.context.active_object
head.name = "K_Head"
head.scale = (1.0, 0.92, 1.08)
bpy.ops.object.transform_apply(scale=True)
# 动漫脸部微调: 下巴收窄
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < 1.60:  # 下颚区域
        factor = max(0, (1.60 - v.co.z) / 0.12)
        v.co.x *= 1.0 - factor * 0.35
        v.co.y *= 1.0 - factor * 0.25
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup_obj(head, "M_Skin", outline=0.003)

# --- 眼睛 ---
for s, x in [("L", 0.042), ("R", -0.042)]:
    make_eye(f"K_Eye{s}", (x, -0.085, 1.665), radius=0.032, mat="M_KiritoEye")
    make_highlight(f"K_EyeHL{s}", (x + 0.012, -0.110, 1.680), radius=0.009)
    # 瞳孔
    make_highlight(f"K_Pupil{s}", (x - 0.005, -0.108, 1.658), radius=0.006)

# --- 手臂 ---
for s, mx in [("L", 1), ("R", -1)]:
    arm_profiles = [
        (1.33, 0.050, 0.048, mx * 0.19, 0),  # 肩
        (1.25, 0.042, 0.040, mx * 0.24, 0),  # 上臂上
        (1.12, 0.038, 0.036, mx * 0.28, 0),  # 上臂中
        (1.02, 0.035, 0.033, mx * 0.30, 0),  # 肘
        (0.92, 0.032, 0.030, mx * 0.32, 0),  # 前臂上
        (0.82, 0.028, 0.026, mx * 0.33, 0),  # 前臂下
        (0.76, 0.025, 0.024, mx * 0.34, 0),  # 腕
    ]
    arm = loft_mesh(f"K_Arm{s}", arm_profiles, ns=12)
    setup_obj(arm, "M_KiritoBlack", outline=0.003)

# --- 手 ---
for s, mx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.028, location=(mx * 0.34, 0, 0.72)
    )
    hand = bpy.context.active_object
    hand.name = f"K_Hand{s}"
    hand.scale = (0.85, 0.55, 1.25)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(hand, "M_Skin", subsurf=1, outline=0)
    # 手指简化 (5指)
    for fi in range(5):
        fa = math.radians(-40 + fi * 20)
        fx = mx * 0.34 + mx * 0.015 * math.cos(fa)
        fy = 0.015 * math.sin(fa)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.006, depth=0.035, location=(fx, fy, 0.685)
        )
        finger = bpy.context.active_object
        finger.name = f"K_Finger{s}{fi}"
        setup_obj(finger, "M_Skin", subsurf=1, outline=0)

# --- 腿 ---
for s, mx in [("L", 1), ("R", -1)]:
    leg_profiles = [
        (0.82, 0.065, 0.055, mx * 0.075, 0),  # 大腿根
        (0.72, 0.060, 0.052, mx * 0.080, 0),  # 大腿上
        (0.58, 0.052, 0.048, mx * 0.085, 0),  # 大腿中
        (0.45, 0.045, 0.042, mx * 0.085, 0),  # 膝
        (0.35, 0.040, 0.038, mx * 0.085, 0),  # 小腿上
        (0.22, 0.035, 0.033, mx * 0.085, 0),  # 小腿中
        (0.12, 0.032, 0.030, mx * 0.085, 0),  # 踝上
        (0.06, 0.030, 0.028, mx * 0.085, 0),  # 踝
    ]
    leg = loft_mesh(f"K_Leg{s}", leg_profiles, ns=12)
    setup_obj(leg, "M_KiritoBlack", outline=0.003)

# --- 靴子 ---
for s, mx in [("L", 1), ("R", -1)]:
    boot_profiles = [
        (0.14, 0.038, 0.035, mx * 0.085, 0),  # 靴筒上
        (0.10, 0.040, 0.038, mx * 0.085, 0),  # 靴筒
        (0.06, 0.042, 0.040, mx * 0.085, 0),  # 踝
        (0.03, 0.045, 0.050, mx * 0.085, -0.005),  # 脚背
        (0.005, 0.042, 0.065, mx * 0.085, -0.015),  # 脚底
    ]
    boot = loft_mesh(f"K_Boot{s}", boot_profiles, ns=12, cap_bot=True)
    setup_obj(boot, "M_KiritoBlack", subsurf=1, outline=0.003)

print("  ✓ 桐人身体完成")

# ============================================================
# 桐人头发 - 多层网格条带
# ============================================================

# 基础球
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.125, location=(0, 0.01, 1.70)
)
hairbase = bpy.context.active_object
hairbase.name = "K_HairBase"
hairbase.scale = (1.05, 1.0, 1.02)
bpy.ops.object.transform_apply(scale=True)
setup_obj(hairbase, "M_KiritoHair", outline=0.004)

# 刘海 - 宽网格条带
bangs = [
    # (x, y, z, length, width, rot_x, rot_z, taper)
    (-0.06, -0.10, 1.75, 0.12, 0.035, 65, 12, 0.3),
    (-0.02, -0.11, 1.76, 0.13, 0.030, 68, 5, 0.25),
    (0.03, -0.11, 1.76, 0.14, 0.035, 70, -3, 0.28),
    (0.07, -0.10, 1.75, 0.12, 0.032, 65, -10, 0.30),
    (0.00, -0.12, 1.77, 0.11, 0.025, 72, 2, 0.22),
    (-0.04, -0.11, 1.76, 0.10, 0.028, 67, 8, 0.27),
    (0.05, -0.10, 1.75, 0.11, 0.030, 63, -7, 0.25),
]

for i, (x, y, z, ln, w, rx, rz, taper) in enumerate(bangs):
    profiles = [
        (0, w, 0.008, 0, 0),
        (ln * 0.3, w * 0.85, 0.007, 0, 0),
        (ln * 0.6, w * 0.6, 0.005, 0, 0),
        (ln * 0.85, w * taper, 0.003, 0, 0),
        (ln, w * 0.08, 0.001, 0, 0),
    ]
    bang = loft_mesh(f"K_Bang{i}", profiles, ns=6, cap_top=True, cap_bot=True)
    bang.location = (x, y, z)
    bang.rotation_euler = (math.radians(rx), 0, math.radians(rz))
    setup_obj(bang, "M_KiritoHair", subsurf=1, outline=0.002)

# 侧发
sides = [
    (0.10, -0.03, 1.70, 0.16, 0.030, 85, -20, 0.25),
    (0.12, 0.02, 1.68, 0.18, 0.028, 95, -28, 0.22),
    (0.09, -0.06, 1.72, 0.14, 0.025, 80, -15, 0.28),
]
for mult in [1, -1]:
    sn = "L" if mult > 0 else "R"
    for i, (x, y, z, ln, w, rx, rz, taper) in enumerate(sides):
        profiles = [
            (0, w, 0.008, 0, 0),
            (ln * 0.4, w * 0.8, 0.006, 0, 0),
            (ln * 0.75, w * 0.5, 0.004, 0, 0),
            (ln, w * taper * 0.3, 0.002, 0, 0),
        ]
        side = loft_mesh(f"K_Side{sn}{i}", profiles, ns=6, cap_top=True, cap_bot=True)
        side.location = (x * mult, y, z)
        side.rotation_euler = (math.radians(rx), 0, math.radians(rz * mult))
        setup_obj(side, "M_KiritoHair", subsurf=1, outline=0.002)

# 后发
backs = [
    (-0.05, 0.08, 1.68, 0.18, 0.035, 105, -8, 0.20),
    (0.00, 0.10, 1.69, 0.20, 0.038, 108, 0, 0.22),
    (0.05, 0.08, 1.68, 0.18, 0.035, 105, 8, 0.20),
    (0.00, 0.06, 1.65, 0.16, 0.030, 100, 0, 0.25),
    (-0.03, 0.09, 1.67, 0.17, 0.032, 103, -5, 0.23),
    (0.03, 0.09, 1.67, 0.17, 0.032, 103, 5, 0.23),
]
for i, (x, y, z, ln, w, rx, rz, taper) in enumerate(backs):
    profiles = [
        (0, w, 0.008, 0, 0),
        (ln * 0.35, w * 0.85, 0.007, 0, 0),
        (ln * 0.65, w * 0.6, 0.005, 0, 0),
        (ln * 0.85, w * 0.35, 0.003, 0, 0),
        (ln, w * taper * 0.2, 0.001, 0, 0),
    ]
    back = loft_mesh(f"K_Back{i}", profiles, ns=6, cap_top=True, cap_bot=True)
    back.location = (x, y, z)
    back.rotation_euler = (math.radians(rx), 0, math.radians(rz))
    setup_obj(back, "M_KiritoHair", subsurf=1, outline=0.002)

print("  ✓ 桐人头发完成")

# ============================================================
# 桐人黑色风衣 (长外套)
# ============================================================

coat_profiles = [
    # 衣领到下摆
    (1.42, 0.060, 0.055, 0, 0),  # 领口
    (1.38, 0.110, 0.080, 0, 0),  # 肩线
    (1.30, 0.195, 0.115, 0, 0),  # 上胸
    (1.20, 0.200, 0.125, 0, 0),  # 胸
    (1.10, 0.195, 0.120, 0, 0),  # 下胸
    (1.00, 0.170, 0.110, 0, 0),  # 腰
    (0.88, 0.165, 0.105, 0, 0),  # 腰带处
    (0.75, 0.190, 0.115, 0, 0),  # 臀
    (0.60, 0.220, 0.125, 0, 0),  # 大腿
    (0.45, 0.250, 0.135, 0, 0),  # 膝上
    (0.30, 0.280, 0.145, 0, 0),  # 膝下 (风衣摆)
    (0.18, 0.300, 0.150, 0, 0),  # 下摆
]
coat = loft_mesh("K_Coat", coat_profiles, ns=20)
setup_obj(coat, "M_KiritoBlack", outline=0.005)

# 立领
collar_profiles = [
    (1.42, 0.062, 0.058, 0, 0),
    (1.44, 0.065, 0.060, 0, 0),
    (1.46, 0.068, 0.055, 0, 0),
    (1.49, 0.058, 0.048, 0, 0),
]
collar = loft_mesh("K_Collar", collar_profiles, ns=16)
setup_obj(collar, "M_KiritoBlack", subsurf=1, outline=0.003)

# 腰带
belt_profiles = [
    (0.86, 0.168, 0.108, 0, 0),
    (0.88, 0.172, 0.112, 0, 0),
    (0.90, 0.170, 0.110, 0, 0),
]
belt = loft_mesh("K_Belt", belt_profiles, ns=16)
setup_obj(belt, "M_KiritoBelt", subsurf=1, outline=0.002)

# 腰带扣
bpy.ops.mesh.primitive_cube_add(size=0.025, location=(0, -0.115, 0.88))
buckle = bpy.context.active_object
buckle.name = "K_Buckle"
buckle.scale = (1.2, 0.5, 0.8)
bpy.ops.object.transform_apply(scale=True)
setup_obj(buckle, "M_KiritoSilver", subsurf=1, outline=0)

# 肩扣
for s, x in [("L", 0.18), ("R", -0.18)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.012, location=(x, -0.07, 1.32)
    )
    b = bpy.context.active_object
    b.name = f"K_ShoulderPin{s}"
    setup_obj(b, "M_KiritoSilver", subsurf=0, outline=0)

# 袖口
for s, mx in [("L", 1), ("R", -1)]:
    cuff_profiles = [
        (0.78, 0.032, 0.030, mx * 0.33, 0),
        (0.76, 0.035, 0.033, mx * 0.34, 0),
        (0.74, 0.033, 0.031, mx * 0.345, 0),
    ]
    cuff = loft_mesh(f"K_Cuff{s}", cuff_profiles, ns=10)
    setup_obj(cuff, "M_KiritoBlack", subsurf=1, outline=0.002)

print("  ✓ 桐人风衣完成")

# ============================================================
# 逐暗者 (Elucidator) - 高精度剑
# ============================================================
print("\n[Elucidator] 高精度建模...")
sx = 0.42

# 剑身 - 截面放样 (扁平六角截面)
blade_profiles = [
    # (z, rx, ry, ox, oy)
    (0.50, 0.014, 0.003, sx, -0.10),  # 护手接合
    (0.55, 0.015, 0.003, sx, -0.10),  # 剑身底
    (0.75, 0.016, 0.0028, sx, -0.10),  # 中段
    (1.00, 0.015, 0.0025, sx, -0.10),  # 上段
    (1.20, 0.013, 0.0022, sx, -0.10),  # 近尖
    (1.35, 0.008, 0.0018, sx, -0.10),  # 收窄
    (1.40, 0.002, 0.0008, sx, -0.10),  # 剑尖
]
blade = loft_mesh("E_Blade", blade_profiles, ns=6, cap_top=True, cap_bot=True)
setup_obj(blade, "M_Elucidator", col_name="Weapons", subsurf=1, outline=0)

# 血槽 (细长凹槽)
fuller_profiles = [
    (0.58, 0.004, 0.001, sx, -0.10),
    (0.90, 0.004, 0.001, sx, -0.10),
    (1.15, 0.003, 0.0008, sx, -0.10),
]
fuller = loft_mesh("E_Fuller", fuller_profiles, ns=4)
setup_obj(fuller, "M_MetalDark", col_name="Weapons", subsurf=0, outline=0)

# 护手 - 十字形
guard_profiles = [
    (0.495, 0.050, 0.008, sx, -0.10),
    (0.500, 0.055, 0.010, sx, -0.10),
    (0.505, 0.055, 0.010, sx, -0.10),
    (0.510, 0.050, 0.008, sx, -0.10),
]
guard = loft_mesh("E_Guard", guard_profiles, ns=8)
setup_obj(guard, "M_MetalDark", col_name="Weapons", subsurf=1, outline=0.002)

# 护手球形装饰
for dx in [0.055, -0.055]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.008, location=(sx + dx, -0.10, 0.50)
    )
    gb = bpy.context.active_object
    gb.name = f'E_GuardBall_{"L" if dx>0 else "R"}'
    setup_obj(gb, "M_MetalDark", col_name="Weapons", subsurf=1, outline=0)

# 握柄
grip_profiles = [
    (0.49, 0.010, 0.009, sx, -0.10),
    (0.47, 0.011, 0.010, sx, -0.10),
    (0.44, 0.012, 0.011, sx, -0.10),
    (0.41, 0.011, 0.010, sx, -0.10),
    (0.38, 0.010, 0.009, sx, -0.10),
]
grip = loft_mesh("E_Grip", grip_profiles, ns=8)
setup_obj(grip, "M_LeatherBrown", col_name="Weapons", subsurf=1, outline=0)

# 握柄纹路 (螺旋线)
for i in range(8):
    z = 0.39 + i * 0.012
    a = i * math.radians(45)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.013, minor_radius=0.002, location=(sx, -0.10, z)
    )
    wrap = bpy.context.active_object
    wrap.name = f"E_GripWrap{i}"
    wrap.scale = (1.0, 1.0, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(wrap, "M_KiritoBelt", col_name="Weapons", subsurf=0, outline=0)

# 柄头
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=10, ring_count=8, radius=0.012, location=(sx, -0.10, 0.37)
)
pommel = bpy.context.active_object
pommel.name = "E_Pommel"
pommel.scale = (1.0, 1.0, 0.7)
bpy.ops.object.transform_apply(scale=True)
setup_obj(pommel, "M_MetalDark", col_name="Weapons", subsurf=1, outline=0.002)

print("  ✓ 逐暗者完成")

# ============================================================
# 亚丝娜 (Asuna) - AAA级
# ============================================================
print("\n[Asuna] 高精度建模...")
ax = 1.2  # 位于桐人右侧

# 躯干
a_torso_profiles = [
    (0.80, 0.130, 0.085, ax, 0),
    (0.88, 0.135, 0.090, ax, 0),
    (0.95, 0.140, 0.095, ax, 0),
    (1.02, 0.160, 0.105, ax, 0),
    (1.10, 0.165, 0.108, ax, 0),
    (1.18, 0.160, 0.100, ax, 0),
    (1.25, 0.155, 0.095, ax, 0),
    (1.30, 0.140, 0.085, ax, 0),
    (1.36, 0.090, 0.065, ax, 0),
    (1.40, 0.050, 0.045, ax, 0),
    (1.45, 0.043, 0.040, ax, 0),
    (1.48, 0.040, 0.038, ax, 0),
]
a_torso = loft_mesh("A_Torso", a_torso_profiles, ns=16)
setup_obj(a_torso, "M_AsunaWhite", outline=0.003)

# 头
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24, ring_count=16, radius=0.108, location=(ax, 0, 1.61)
)
a_head = bpy.context.active_object
a_head.name = "A_Head"
a_head.scale = (1.0, 0.90, 1.10)
bpy.ops.object.transform_apply(scale=True)
# 下巴收窄
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(a_head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < 1.55:
        factor = max(0, (1.55 - v.co.z) / 0.10)
        v.co.x *= 1.0 - factor * 0.40
        v.co.y *= 1.0 - factor * 0.30
bmesh.update_edit_mesh(a_head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup_obj(a_head, "M_Skin", outline=0.003)

# 眼睛 (琥珀色大眼)
for s, x in [("L", 0.038), ("R", -0.038)]:
    make_eye(f"A_Eye{s}", (ax + x, -0.082, 1.615), radius=0.035, mat="M_AsunaEye")
    make_highlight(f"A_EyeHL{s}", (ax + x + 0.010, -0.105, 1.630), radius=0.010)

# 手臂
for s, mx in [("L", 1), ("R", -1)]:
    a_arm_profiles = [
        (1.30, 0.042, 0.040, ax + mx * 0.16, 0),
        (1.22, 0.036, 0.034, ax + mx * 0.20, 0),
        (1.10, 0.032, 0.030, ax + mx * 0.24, 0),
        (1.00, 0.030, 0.028, ax + mx * 0.26, 0),
        (0.90, 0.027, 0.025, ax + mx * 0.28, 0),
        (0.82, 0.024, 0.022, ax + mx * 0.29, 0),
        (0.76, 0.022, 0.020, ax + mx * 0.30, 0),
    ]
    a_arm = loft_mesh(f"A_Arm{s}", a_arm_profiles, ns=12)
    setup_obj(a_arm, "M_Skin", outline=0.003)

# 手
for s, mx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.024, location=(ax + mx * 0.30, 0, 0.72)
    )
    a_hand = bpy.context.active_object
    a_hand.name = f"A_Hand{s}"
    a_hand.scale = (0.85, 0.55, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(a_hand, "M_Skin", subsurf=1, outline=0)

# 腿
for s, mx in [("L", 1), ("R", -1)]:
    a_leg_profiles = [
        (0.80, 0.058, 0.050, ax + mx * 0.065, 0),
        (0.70, 0.054, 0.048, ax + mx * 0.068, 0),
        (0.55, 0.048, 0.044, ax + mx * 0.070, 0),
        (0.42, 0.042, 0.038, ax + mx * 0.070, 0),
        (0.32, 0.038, 0.035, ax + mx * 0.070, 0),
        (0.22, 0.033, 0.030, ax + mx * 0.070, 0),
        (0.12, 0.030, 0.028, ax + mx * 0.070, 0),
        (0.06, 0.028, 0.026, ax + mx * 0.070, 0),
    ]
    a_leg = loft_mesh(f"A_Leg{s}", a_leg_profiles, ns=12)
    setup_obj(a_leg, "M_Skin", outline=0.003)

# 靴子
for s, mx in [("L", 1), ("R", -1)]:
    a_boot_profiles = [
        (0.25, 0.036, 0.034, ax + mx * 0.070, 0),
        (0.18, 0.038, 0.036, ax + mx * 0.070, 0),
        (0.12, 0.040, 0.038, ax + mx * 0.070, 0),
        (0.06, 0.042, 0.042, ax + mx * 0.070, -0.005),
        (0.02, 0.040, 0.055, ax + mx * 0.070, -0.012),
        (0.005, 0.038, 0.058, ax + mx * 0.070, -0.015),
    ]
    a_boot = loft_mesh(f"A_Boot{s}", a_boot_profiles, ns=12, cap_bot=True)
    setup_obj(a_boot, "M_AsunaWhite", subsurf=1, outline=0.003)

print("  ✓ 亚丝娜身体完成")

# === 亚丝娜头发 ===
# 基础球
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.118, location=(ax, 0.01, 1.64)
)
a_hairbase = bpy.context.active_object
a_hairbase.name = "A_HairBase"
setup_obj(a_hairbase, "M_AsunaHair", outline=0.003)

# 长发 (背部垂下的大块)
longhair_profiles = [
    (1.62, 0.10, 0.035, ax, 0.05),
    (1.50, 0.11, 0.038, ax, 0.06),
    (1.35, 0.12, 0.040, ax, 0.07),
    (1.15, 0.11, 0.038, ax, 0.06),
    (0.95, 0.10, 0.035, ax, 0.05),
    (0.75, 0.09, 0.030, ax, 0.04),
    (0.60, 0.08, 0.025, ax, 0.03),
]
longhair = loft_mesh("A_LongHair", longhair_profiles, ns=10)
setup_obj(longhair, "M_AsunaHair", outline=0.003)

# 刘海
a_bangs = [
    (-0.05, -0.09, 1.69, 0.10, 0.030, 62, 10),
    (-0.01, -0.10, 1.70, 0.11, 0.025, 66, 4),
    (0.03, -0.10, 1.70, 0.12, 0.028, 68, -3),
    (0.06, -0.09, 1.69, 0.10, 0.025, 62, -9),
    (0.01, -0.10, 1.71, 0.09, 0.022, 70, 1),
]
for i, (x, y, z, ln, w, rx, rz) in enumerate(a_bangs):
    profiles = [
        (0, w, 0.007, 0, 0),
        (ln * 0.4, w * 0.8, 0.005, 0, 0),
        (ln * 0.75, w * 0.5, 0.003, 0, 0),
        (ln, w * 0.08, 0.001, 0, 0),
    ]
    bang = loft_mesh(f"A_Bang{i}", profiles, ns=6, cap_top=True, cap_bot=True)
    bang.location = (ax + x, y, z)
    bang.rotation_euler = (math.radians(rx), 0, math.radians(rz))
    setup_obj(bang, "M_AsunaHair", subsurf=1, outline=0.002)

# 辫子
for s, sx2 in [("L", 0.10), ("R", -0.10)]:
    braid_profiles = [
        (1.55, 0.020, 0.018, ax + sx2, 0.03),
        (1.40, 0.022, 0.020, ax + sx2, 0.04),
        (1.25, 0.020, 0.018, ax + sx2 * 0.95, 0.05),
        (1.10, 0.018, 0.016, ax + sx2 * 0.90, 0.04),
        (0.95, 0.015, 0.014, ax + sx2 * 0.85, 0.03),
    ]
    braid = loft_mesh(f"A_Braid{s}", braid_profiles, ns=8)
    setup_obj(braid, "M_AsunaHair", subsurf=1, outline=0.002)

# 发箍
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.008, location=(ax, 0, 1.72))
headband = bpy.context.active_object
headband.name = "A_Headband"
headband.scale = (1.0, 0.92, 0.25)
bpy.ops.object.transform_apply(scale=True)
setup_obj(headband, "M_FabricWhite", subsurf=0, outline=0)

print("  ✓ 亚丝娜头发完成")

# === KoB战斗装 ===
# 胸甲
chest_profiles = [
    (1.00, 0.162, 0.108, ax, 0),
    (1.05, 0.168, 0.112, ax, 0),
    (1.10, 0.172, 0.115, ax, 0),
    (1.15, 0.170, 0.110, ax, 0),
    (1.20, 0.165, 0.105, ax, 0),
    (1.25, 0.158, 0.098, ax, 0),
]
chest = loft_mesh("A_ChestArmor", chest_profiles, ns=16)
setup_obj(chest, "M_AsunaWhite", outline=0.003)

# 十字纹章
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(ax, -0.115, 1.12))
crossH = bpy.context.active_object
crossH.name = "A_CrossH"
crossH.scale = (5, 0.5, 1.2)
bpy.ops.object.transform_apply(scale=True)
setup_obj(crossH, "M_AsunaRed", subsurf=0, outline=0)

bpy.ops.mesh.primitive_cube_add(size=0.01, location=(ax, -0.115, 1.12))
crossV = bpy.context.active_object
crossV.name = "A_CrossV"
crossV.scale = (1.2, 0.5, 5)
bpy.ops.object.transform_apply(scale=True)
setup_obj(crossV, "M_AsunaRed", subsurf=0, outline=0)

# 肩甲
for s, mx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.035, location=(ax + mx * 0.16, 0, 1.28)
    )
    shoulder = bpy.context.active_object
    shoulder.name = f"A_Shoulder{s}"
    shoulder.scale = (1.0, 0.7, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(shoulder, "M_AsunaRed", subsurf=1, outline=0.002)

# 裙子 (外层红 + 内层白)
skirt_profiles = [
    (0.85, 0.145, 0.098, ax, 0),
    (0.80, 0.160, 0.108, ax, 0),
    (0.72, 0.185, 0.120, ax, 0),
    (0.63, 0.210, 0.135, ax, 0),
    (0.55, 0.230, 0.145, ax, 0),
]
skirt_out = loft_mesh("A_SkirtOuter", skirt_profiles, ns=16)
setup_obj(skirt_out, "M_AsunaRed", outline=0.003)

skirt_in_profiles = [
    (0.84, 0.140, 0.094, ax, 0),
    (0.78, 0.155, 0.104, ax, 0),
    (0.70, 0.180, 0.116, ax, 0),
    (0.62, 0.200, 0.130, ax, 0),
    (0.56, 0.220, 0.140, ax, 0),
]
skirt_in = loft_mesh("A_SkirtInner", skirt_in_profiles, ns=16)
setup_obj(skirt_in, "M_FabricWhite", subsurf=1, outline=0)

# 腰带
a_belt_profiles = [
    (0.84, 0.148, 0.100, ax, 0),
    (0.86, 0.150, 0.102, ax, 0),
    (0.88, 0.148, 0.100, ax, 0),
]
a_belt = loft_mesh("A_Belt", a_belt_profiles, ns=16)
setup_obj(a_belt, "M_AsunaGold", subsurf=1, outline=0.002)

print("  ✓ 亚丝娜KoB装完成")

# ============================================================
# 闪光 (Lambent Light)
# ============================================================
print("\n[Lambent Light] 高精度建模...")
lx = ax + 0.38

# 细剑身
ll_profiles = [
    (0.68, 0.004, 0.003, lx, -0.08),
    (0.80, 0.0045, 0.0032, lx, -0.08),
    (1.00, 0.004, 0.0028, lx, -0.08),
    (1.20, 0.0035, 0.0024, lx, -0.08),
    (1.38, 0.002, 0.0015, lx, -0.08),
    (1.45, 0.0005, 0.0004, lx, -0.08),
]
ll_blade = loft_mesh("LL_Blade", ll_profiles, ns=6, cap_top=True)
setup_obj(ll_blade, "M_LambentLight", col_name="Weapons", subsurf=1, outline=0)

# 护手篮
bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.004, location=(lx, -0.08, 0.67))
ll_guard = bpy.context.active_object
ll_guard.name = "LL_Guard"
ll_guard.rotation_euler = (math.radians(90), 0, 0)
setup_obj(ll_guard, "M_MetalSilver", col_name="Weapons", subsurf=0, outline=0)

# 护手横杆
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8, radius=0.003, depth=0.06, location=(lx, -0.08, 0.67)
)
ll_bar = bpy.context.active_object
ll_bar.name = "LL_Bar"
ll_bar.rotation_euler = (0, math.radians(90), 0)
setup_obj(ll_bar, "M_MetalSilver", col_name="Weapons", subsurf=0, outline=0)

# 握柄
ll_grip_profiles = [
    (0.66, 0.008, 0.007, lx, -0.08),
    (0.63, 0.009, 0.008, lx, -0.08),
    (0.60, 0.009, 0.008, lx, -0.08),
    (0.57, 0.008, 0.007, lx, -0.08),
]
ll_grip = loft_mesh("LL_Grip", ll_grip_profiles, ns=8)
setup_obj(ll_grip, "M_FabricWhite", col_name="Weapons", subsurf=1, outline=0)

# 柄头
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8, ring_count=6, radius=0.009, location=(lx, -0.08, 0.56)
)
ll_pommel = bpy.context.active_object
ll_pommel.name = "LL_Pommel"
setup_obj(ll_pommel, "M_MetalSilver", col_name="Weapons", subsurf=1, outline=0)

print("  ✓ 闪光完成")

# ============================================================
# 克莱因 (Klein) - AAA级
# ============================================================
print("\n[Klein] 高精度建模...")
kx = -1.2

# 躯干 (比桐人略壮)
k_torso_profiles = [
    (0.82, 0.155, 0.105, kx, 0),
    (0.88, 0.160, 0.110, kx, 0),
    (0.95, 0.168, 0.115, kx, 0),
    (1.05, 0.185, 0.125, kx, 0),
    (1.15, 0.195, 0.130, kx, 0),
    (1.25, 0.200, 0.120, kx, 0),
    (1.33, 0.185, 0.105, kx, 0),
    (1.38, 0.110, 0.075, kx, 0),
    (1.42, 0.060, 0.055, kx, 0),
    (1.48, 0.052, 0.050, kx, 0),
    (1.52, 0.050, 0.048, kx, 0),
]
k_torso = loft_mesh("KL_Torso", k_torso_profiles, ns=16)
setup_obj(k_torso, "M_KleinRed", outline=0.004)

# 头
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24, ring_count=16, radius=0.12, location=(kx, 0, 1.66)
)
k_head = bpy.context.active_object
k_head.name = "KL_Head"
k_head.scale = (1.0, 0.95, 1.02)
bpy.ops.object.transform_apply(scale=True)
# 下巴
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(k_head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < 1.58:
        factor = max(0, (1.58 - v.co.z) / 0.10)
        v.co.x *= 1.0 - factor * 0.30
        v.co.y *= 1.0 - factor * 0.20
bmesh.update_edit_mesh(k_head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup_obj(k_head, "M_Skin", outline=0.003)

# 眼 (细长型)
for s, x in [("L", 0.045), ("R", -0.045)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.025, location=(kx + x, -0.092, 1.665)
    )
    k_eye = bpy.context.active_object
    k_eye.name = f"KL_Eye{s}"
    k_eye.scale = (1.3, 0.6, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(k_eye, "M_EyeBlack", subsurf=1, outline=0)

# 手臂
for s, mx in [("L", 1), ("R", -1)]:
    k_arm_profiles = [
        (1.33, 0.055, 0.052, kx + mx * 0.20, 0),
        (1.22, 0.048, 0.045, kx + mx * 0.26, 0),
        (1.10, 0.042, 0.040, kx + mx * 0.30, 0),
        (1.00, 0.038, 0.036, kx + mx * 0.33, 0),
        (0.90, 0.035, 0.033, kx + mx * 0.35, 0),
        (0.82, 0.032, 0.030, kx + mx * 0.36, 0),
        (0.76, 0.028, 0.026, kx + mx * 0.37, 0),
    ]
    k_arm = loft_mesh(f"KL_Arm{s}", k_arm_profiles, ns=12)
    setup_obj(k_arm, "M_KleinRed", outline=0.003)

# 手
for s, mx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.032, location=(kx + mx * 0.37, 0, 0.72)
    )
    k_hand = bpy.context.active_object
    k_hand.name = f"KL_Hand{s}"
    k_hand.scale = (0.9, 0.6, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    setup_obj(k_hand, "M_Skin", subsurf=1, outline=0)

# 腿 (袴裤)
for s, mx in [("L", 1), ("R", -1)]:
    k_leg_profiles = [
        (0.82, 0.072, 0.060, kx + mx * 0.080, 0),
        (0.70, 0.075, 0.058, kx + mx * 0.085, 0),
        (0.55, 0.065, 0.052, kx + mx * 0.090, 0),
        (0.42, 0.055, 0.046, kx + mx * 0.090, 0),
        (0.30, 0.048, 0.040, kx + mx * 0.090, 0),
        (0.20, 0.040, 0.035, kx + mx * 0.090, 0),
        (0.12, 0.035, 0.032, kx + mx * 0.090, 0),
        (0.06, 0.032, 0.030, kx + mx * 0.090, 0),
    ]
    k_leg = loft_mesh(f"KL_Leg{s}", k_leg_profiles, ns=12)
    setup_obj(k_leg, "M_KleinCream", outline=0.003)

# 草鞋
for s, mx in [("L", 1), ("R", -1)]:
    k_shoe_profiles = [
        (0.08, 0.038, 0.036, kx + mx * 0.090, 0),
        (0.04, 0.042, 0.048, kx + mx * 0.090, -0.008),
        (0.01, 0.040, 0.060, kx + mx * 0.090, -0.015),
    ]
    k_shoe = loft_mesh(f"KL_Shoe{s}", k_shoe_profiles, ns=10, cap_bot=True)
    setup_obj(k_shoe, "M_LeatherBrown", subsurf=1, outline=0.002)

# 头发 (刺猬式)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=18, ring_count=12, radius=0.13, location=(kx, 0.01, 1.72)
)
k_hairbase = bpy.context.active_object
k_hairbase.name = "KL_HairBase"
setup_obj(k_hairbase, "M_KleinHair", outline=0.003)

# 发刺
spikes = [
    (0.00, -0.06, 1.88, 0.16, 0.042, 45, 0),
    (-0.06, -0.03, 1.90, 0.14, 0.038, 38, -12),
    (0.06, -0.03, 1.90, 0.14, 0.038, 38, 12),
    (-0.10, 0.03, 1.88, 0.12, 0.035, 18, -25),
    (0.10, 0.03, 1.88, 0.12, 0.035, 18, 25),
    (0.00, 0.10, 1.85, 0.13, 0.035, -8, 0),
    (-0.08, 0.08, 1.86, 0.11, 0.030, -3, -18),
    (0.08, 0.08, 1.86, 0.11, 0.030, -3, 18),
    (-0.04, -0.08, 1.87, 0.13, 0.035, 50, -6),
    (0.04, -0.08, 1.87, 0.13, 0.035, 50, 6),
]
for i, (x, y, z, ln, w, rx, rz) in enumerate(spikes):
    profiles = [
        (0, w, 0.010, 0, 0),
        (ln * 0.3, w * 0.7, 0.008, 0, 0),
        (ln * 0.6, w * 0.4, 0.005, 0, 0),
        (ln * 0.85, w * 0.15, 0.003, 0, 0),
        (ln, 0.002, 0.001, 0, 0),
    ]
    spike = loft_mesh(f"KL_Spike{i}", profiles, ns=6, cap_top=True, cap_bot=True)
    spike.location = (kx + x, y, z)
    spike.rotation_euler = (math.radians(rx), 0, math.radians(rz))
    setup_obj(spike, "M_KleinHair", subsurf=1, outline=0.002)

# 头带
bpy.ops.mesh.primitive_torus_add(major_radius=0.135, minor_radius=0.010, location=(kx, 0, 1.74))
k_headband = bpy.context.active_object
k_headband.name = "KL_Headband"
k_headband.scale = (1.0, 0.92, 0.28)
bpy.ops.object.transform_apply(scale=True)
setup_obj(k_headband, "M_KleinRed", subsurf=0, outline=0.002)

# 胸甲
k_chest_profiles = [
    (0.98, 0.172, 0.118, kx, 0),
    (1.05, 0.190, 0.128, kx, 0),
    (1.12, 0.198, 0.132, kx, 0),
    (1.20, 0.195, 0.125, kx, 0),
    (1.28, 0.185, 0.115, kx, 0),
]
k_chest = loft_mesh("KL_ChestArmor", k_chest_profiles, ns=16)
setup_obj(k_chest, "M_KleinBrown", subsurf=1, outline=0.003)

# 腰带
k_belt_profiles = [
    (0.86, 0.162, 0.112, kx, 0),
    (0.88, 0.166, 0.115, kx, 0),
    (0.90, 0.164, 0.113, kx, 0),
]
k_belt = loft_mesh("KL_Belt", k_belt_profiles, ns=16)
setup_obj(k_belt, "M_LeatherBrown", subsurf=1, outline=0.002)

print("  ✓ 克莱因完成")

# === 武士刀 ===
ksx = kx - 0.20

# 刀身 (弯曲)
katana_profiles = [
    (0.52, 0.010, 0.003, ksx, -0.08),
    (0.65, 0.011, 0.003, ksx - 0.005, -0.08),
    (0.80, 0.011, 0.0028, ksx - 0.010, -0.08),
    (0.95, 0.010, 0.0025, ksx - 0.015, -0.08),
    (1.10, 0.009, 0.0022, ksx - 0.018, -0.08),
    (1.25, 0.006, 0.0018, ksx - 0.020, -0.08),
    (1.32, 0.002, 0.0008, ksx - 0.022, -0.08),
]
katana_blade = loft_mesh("KT_Blade", katana_profiles, ns=6, cap_top=True, cap_bot=True)
setup_obj(katana_blade, "M_MetalSilver", col_name="Weapons", subsurf=1, outline=0)

# 刀镡 (圆形)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, radius=0.022, depth=0.004, location=(ksx, -0.08, 0.51)
)
tsuba = bpy.context.active_object
tsuba.name = "KT_Tsuba"
setup_obj(tsuba, "M_MetalDark", col_name="Weapons", subsurf=1, outline=0.002)

# 柄 (红色�的缠绕)
kt_grip_profiles = [
    (0.50, 0.009, 0.008, ksx, -0.08),
    (0.47, 0.010, 0.009, ksx, -0.08),
    (0.43, 0.010, 0.009, ksx, -0.08),
    (0.39, 0.009, 0.008, ksx, -0.08),
    (0.36, 0.008, 0.007, ksx, -0.08),
]
kt_grip = loft_mesh("KT_Grip", kt_grip_profiles, ns=8)
setup_obj(kt_grip, "M_KleinRed", col_name="Weapons", subsurf=1, outline=0)

# 柄头
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8, ring_count=6, radius=0.010, location=(ksx, -0.08, 0.35)
)
kt_pommel = bpy.context.active_object
kt_pommel.name = "KT_Pommel"
setup_obj(kt_pommel, "M_MetalDark", col_name="Weapons", subsurf=1, outline=0)

print("  ✓ 武士刀完成")

# ============================================================
# 最终设置
# ============================================================
bpy.ops.object.select_all(action="DESELECT")

# 保存
if bpy.data.filepath:
    bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
    print(f"\nSaved to {bpy.data.filepath}")

obj_count = len(bpy.data.objects)
mat_count = len(bpy.data.materials)

print(f"\n{'='*60}")
print("  SAO AAA级模型构建完成!")
print(f"{'='*60}")
print(f"  对象总数: {obj_count}")
print(f"  材质总数: {mat_count}")
print("  ✓ AAA多层赛璐璐材质 (Diffuse→Toon + Fresnel轮廓光)")
print("  ✓ 桐人 (截面放样躯干+头发条带+风衣+描边)")
print("  ✓ 逐暗者 (6角截面剑身+装饰纹路握柄)")
print("  ✓ 亚丝娜 (身体+长发辫+KoB白红战斗装)")
print("  ✓ 闪光 (细剑+护手篮)")
print("  ✓ 克莱因 (壮硕体型+刺猬发+武士装+武士刀)")
print("  ✓ SubSurf Lv2 + Solidify描边")
print(f"{'='*60}")
