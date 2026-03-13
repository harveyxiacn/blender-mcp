"""
克莱因 (Klein) - 基于参考图精确重建
参考图关键特征:
- 竖立红棕色刺猬发(向上), 红色头带(白色菱形花纹)
- 方脸, 窄眼, 下巴胡茬/山羊胡, 偏黝黑肤色
- 红色武士上衣+深棕色胸甲(背甲)
- 奶白色袴裤(宽松, 脚踝收束)
- 棕色草鞋+绑带
- 武士刀佩于腰间
"""

import math

import bmesh
import bpy


def loft(name, profiles, ns=16, cap_top=False, cap_bot=False):
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


def setup(obj, mat_name, col_name="Characters", ss=2, outline=0.004) -> None:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    col = bpy.data.collections.get(col_name)
    if col:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
    if ss > 0:
        m = obj.modifiers.new("SS", "SUBSURF")
        m.levels = ss
        m.render_levels = ss
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    if outline > 0:
        om = bpy.data.materials.get("M_Outline")
        if om:
            m = obj.modifiers.new("Outline", "SOLIDIFY")
            m.thickness = outline
            m.offset = -1
            m.use_flip_normals = True
            m.material_offset = len(obj.data.materials)
            obj.data.materials.append(om)


def hair_strip(name, loc, rot_deg, length, base_w, tip_w, mat="M_KleinHair", thickness=0.012, ns=6):
    profiles = [
        (0, base_w, thickness, 0, 0),
        (length * 0.25, base_w * 0.82, thickness * 0.85, 0, 0),
        (length * 0.5, base_w * 0.55, thickness * 0.65, 0, 0),
        (length * 0.75, base_w * 0.28, thickness * 0.4, 0, 0),
        (length * 0.9, tip_w * 1.2, thickness * 0.2, 0, 0),
        (length, tip_w * 0.15, thickness * 0.05, 0, 0),
    ]
    obj = loft(name, profiles, ns=ns, cap_top=True, cap_bot=True)
    obj.location = loc
    obj.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    setup(obj, mat, ss=1, outline=0.003)
    return obj


kx = -1.0  # 克莱因位置

print("\n[克莱因] Building...")

# === 头部 (方脸, 更男性化) ===
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=28, ring_count=18, radius=0.125, location=(kx, 0, 1.66)
)
head = bpy.context.active_object
head.name = "KL_Head"
head.scale = (1.02, 0.95, 1.0)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    lz = v.co.z
    # 下巴方形(不像桐人那样尖)
    if lz < 1.60:
        f = max(0, (1.60 - lz) / 0.10)
        v.co.x *= 1.0 - f * 0.25  # 没那么尖
        v.co.y *= 1.0 - f * 0.18
    # 颧骨
    if 1.62 < lz < 1.70:
        v.co.x *= 1.03
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(head, "M_SkinTan", outline=0.004)

# === 眼睛 (窄长型, 参考图: 比桐人/亚丝娜小且窄) ===
for side, sx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.022, location=(kx + sx * 0.045, -0.095, 1.665)
    )
    ew = bpy.context.active_object
    ew.name = f"KL_EyeW{side}"
    ew.scale = (1.4, 0.5, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    setup(ew, "M_EyeWhite", ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.016, location=(kx + sx * 0.045, -0.108, 1.663)
    )
    iris = bpy.context.active_object
    iris.name = f"KL_Iris{side}"
    iris.scale = (1.3, 0.5, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    setup(iris, "M_KleinBrown", ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6, radius=0.008, location=(kx + sx * 0.045, -0.115, 1.662)
    )
    pupil = bpy.context.active_object
    pupil.name = f"KL_Pupil{side}"
    pupil.scale = (1.0, 0.5, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    setup(pupil, "M_EyeBlack", ss=0, outline=0)

# 眉毛 (粗)
for side, sx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_cube_add(size=0.010, location=(kx + sx * 0.045, -0.110, 1.695))
    brow = bpy.context.active_object
    brow.name = f"KL_Brow{side}"
    brow.scale = (3.2, 0.35, 0.35)
    bpy.ops.object.transform_apply(scale=True)
    setup(brow, "M_KleinHair", ss=1, outline=0)

# 鼻子 (较明显)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8, ring_count=6, radius=0.010, location=(kx, -0.118, 1.635)
)
nose = bpy.context.active_object
nose.name = "KL_Nose"
nose.scale = (0.5, 0.7, 0.9)
bpy.ops.object.transform_apply(scale=True)
setup(nose, "M_SkinTan", ss=1, outline=0)

# 嘴
bpy.ops.mesh.primitive_cube_add(size=0.008, location=(kx, -0.112, 1.600))
mouth = bpy.context.active_object
mouth.name = "KL_Mouth"
mouth.scale = (2.5, 0.3, 0.2)
bpy.ops.object.transform_apply(scale=True)
setup(mouth, "M_KleinBrown", ss=1, outline=0)

# 胡茬/山羊胡 (参考图: 明显的下巴胡须)
goatee_profiles = [
    (1.555, 0.025, 0.010, kx, -0.08),
    (1.540, 0.030, 0.015, kx, -0.09),
    (1.525, 0.025, 0.012, kx, -0.08),
    (1.515, 0.015, 0.008, kx, -0.06),
]
goatee = loft("KL_Goatee", goatee_profiles, ns=8)
setup(goatee, "M_KleinHair", ss=1, outline=0)

print("  Head done")

# === 身体 (参考图: 比桐人壮, 武士体型) ===
torso = loft(
    "KL_Torso",
    [
        (0.85, 0.160, 0.110, kx, 0),
        (0.92, 0.168, 0.118, kx, 0),
        (1.00, 0.180, 0.125, kx, 0),
        (1.10, 0.198, 0.135, kx, 0),
        (1.20, 0.205, 0.132, kx, 0),
        (1.28, 0.200, 0.125, kx, 0),
        (1.34, 0.190, 0.110, kx, 0),
        (1.40, 0.100, 0.075, kx, 0),
        (1.44, 0.060, 0.055, kx, 0),
        (1.50, 0.054, 0.052, kx, 0),
    ],
    ns=18,
)
setup(torso, "M_KleinRed", outline=0.004)

# 手臂
for side, mx in [("L", 1), ("R", -1)]:
    arm = loft(
        f"KL_Arm{side}",
        [
            (1.34, 0.055, 0.050, kx + mx * 0.20, 0),
            (1.24, 0.048, 0.044, kx + mx * 0.25, 0),
            (1.12, 0.042, 0.038, kx + mx * 0.29, 0),
            (1.02, 0.038, 0.035, kx + mx * 0.32, 0),
            (0.92, 0.035, 0.032, kx + mx * 0.34, 0),
            (0.84, 0.032, 0.029, kx + mx * 0.35, 0),
            (0.78, 0.028, 0.025, kx + mx * 0.36, 0),
        ],
        ns=12,
    )
    setup(arm, "M_KleinRed", outline=0.003)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.030, location=(kx + mx * 0.36, 0, 0.74)
    )
    hand = bpy.context.active_object
    hand.name = f"KL_Hand{side}"
    hand.scale = (0.9, 0.6, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    setup(hand, "M_SkinTan", ss=1, outline=0)

# 袴裤腿 (参考图: 奶色宽松袴裤, 脚踝收束)
for side, mx in [("L", 1), ("R", -1)]:
    hakama = loft(
        f"KL_Hakama{side}",
        [
            (0.85, 0.078, 0.065, kx + mx * 0.072, 0),
            (0.75, 0.085, 0.072, kx + mx * 0.078, 0),
            (0.60, 0.080, 0.068, kx + mx * 0.082, 0),
            (0.45, 0.065, 0.055, kx + mx * 0.085, 0),
            (0.32, 0.050, 0.042, kx + mx * 0.085, 0),
            (0.22, 0.042, 0.036, kx + mx * 0.085, 0),
            (0.14, 0.038, 0.032, kx + mx * 0.085, 0),
        ],
        ns=14,
    )
    setup(hakama, "M_KleinCream", outline=0.003)

# 草鞋 (参考图: 棕色, 绑带式)
for side, mx in [("L", 1), ("R", -1)]:
    sandal = loft(
        f"KL_Sandal{side}",
        [
            (0.10, 0.040, 0.035, kx + mx * 0.085, 0),
            (0.06, 0.042, 0.045, kx + mx * 0.085, -0.005),
            (0.03, 0.040, 0.058, kx + mx * 0.085, -0.012),
            (0.008, 0.038, 0.060, kx + mx * 0.085, -0.015),
        ],
        ns=12,
        cap_bot=True,
    )
    setup(sandal, "M_LeatherBrown", ss=1, outline=0.003)

    # 绑带
    for zi in range(3):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.042, minor_radius=0.003, location=(kx + mx * 0.085, 0, 0.06 + zi * 0.035)
        )
        strap = bpy.context.active_object
        strap.name = f"KL_SandalStrap{side}{zi}"
        strap.scale = (1.0, 0.8, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        setup(strap, "M_LeatherBrown", ss=0, outline=0)

print("  Body done")

# === 头发 (参考图: 竖直向上的大束红色刺发) ===
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.135, location=(kx, 0.01, 1.72)
)
hb = bpy.context.active_object
hb.name = "KL_HairBase"
hb.scale = (1.05, 1.0, 0.95)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(hb.data)
bm.verts.ensure_lookup_table()
to_del = [v for v in bm.verts if v.co.z < 1.64 and v.co.y < 0.01]
bmesh.ops.delete(bm, geom=to_del, context="VERTS")
bmesh.update_edit_mesh(hb.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(hb, "M_KleinHair", outline=0.004)

# 竖立大发刺 (参考图: 向上和向外的大束发束, 非常夸张)
spike_data = [
    # 正面发刺 (向前上方)
    (0.00, -0.06, 1.82, (35, 0, 0), 0.18, 0.050, 0.006),
    (-0.04, -0.05, 1.83, (30, 3, 10), 0.16, 0.045, 0.005),
    (0.04, -0.05, 1.83, (30, -3, -10), 0.16, 0.045, 0.005),
    (-0.08, -0.03, 1.82, (25, 5, 20), 0.15, 0.042, 0.005),
    (0.08, -0.03, 1.82, (25, -5, -20), 0.15, 0.042, 0.005),
    # 顶部发刺 (向上)
    (0.00, 0.02, 1.85, (5, 0, 0), 0.20, 0.048, 0.006),
    (-0.05, 0.03, 1.84, (0, 5, -8), 0.18, 0.045, 0.005),
    (0.05, 0.03, 1.84, (0, -5, 8), 0.18, 0.045, 0.005),
    # 侧面发刺 (向外)
    (-0.10, 0.00, 1.80, (15, 8, 30), 0.14, 0.040, 0.005),
    (0.10, 0.00, 1.80, (15, -8, -30), 0.14, 0.040, 0.005),
    (-0.12, 0.04, 1.78, (5, 10, 40), 0.12, 0.035, 0.004),
    (0.12, 0.04, 1.78, (5, -10, -40), 0.12, 0.035, 0.004),
    # 后方发刺
    (0.00, 0.10, 1.80, (-15, 0, 0), 0.16, 0.045, 0.005),
    (-0.06, 0.09, 1.79, (-10, 5, -10), 0.14, 0.040, 0.005),
    (0.06, 0.09, 1.79, (-10, -5, 10), 0.14, 0.040, 0.005),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(spike_data):
    hair_strip(f"KL_Spike{i}", (kx + x, y, z), rot, ln, bw, tw)

# 红色头带 (参考图: 红底+白菱形花纹)
bpy.ops.mesh.primitive_torus_add(major_radius=0.140, minor_radius=0.012, location=(kx, 0, 1.74))
hband = bpy.context.active_object
hband.name = "KL_Headband"
hband.scale = (1.0, 0.92, 0.30)
bpy.ops.object.transform_apply(scale=True)
setup(hband, "M_KleinRed", ss=0, outline=0.003)

# 头带菱形花纹 (白色)
for xi in range(-2, 3):
    bpy.ops.mesh.primitive_cube_add(size=0.010, location=(kx + xi * 0.025, -0.130, 1.74))
    diamond = bpy.context.active_object
    diamond.name = f"KL_Diamond{xi+2}"
    diamond.scale = (0.6, 0.3, 0.6)
    diamond.rotation_euler = (0, 0, math.radians(45))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    setup(diamond, "M_FabricWhite", ss=0, outline=0)

print("  Hair done")

# === 武士装 ===
# 深棕色胸甲 (参考图: 覆盖上胸的暗色胸甲)
chest_armor = loft(
    "KL_ChestArmor",
    [
        (1.02, 0.185, 0.128, kx, 0),
        (1.08, 0.200, 0.138, kx, 0),
        (1.15, 0.210, 0.140, kx, 0),
        (1.22, 0.208, 0.135, kx, 0),
        (1.30, 0.200, 0.128, kx, 0),
        (1.36, 0.188, 0.118, kx, 0),
    ],
    ns=18,
)
setup(chest_armor, "M_KleinBrown", ss=1, outline=0.004)

# 背甲
back_armor = loft(
    "KL_BackArmor",
    [
        (1.05, 0.165, 0.100, kx, 0.035),
        (1.15, 0.170, 0.105, kx, 0.038),
        (1.25, 0.165, 0.098, kx, 0.035),
        (1.32, 0.155, 0.090, kx, 0.030),
    ],
    ns=14,
)
setup(back_armor, "M_KleinBrown", ss=1, outline=0.003)

# 腰带 (革製)
kl_belt = loft(
    "KL_Belt",
    [
        (0.88, 0.168, 0.116, kx, 0),
        (0.90, 0.172, 0.120, kx, 0),
        (0.92, 0.170, 0.118, kx, 0),
    ],
    ns=18,
)
setup(kl_belt, "M_LeatherBrown", ss=1, outline=0.003)

# 腰带扣
bpy.ops.mesh.primitive_cube_add(size=0.012, location=(kx, -0.122, 0.90))
kb = bpy.context.active_object
kb.name = "KL_BeltBuckle"
kb.scale = (1.2, 0.5, 0.8)
bpy.ops.object.transform_apply(scale=True)
setup(kb, "M_MetalSilver", ss=0, outline=0)

print("  Armor done")

# === 武士刀 (佩于腰间左侧) ===
print("\n[武士刀] Building...")
ksx = kx - 0.18

blade = loft(
    "KT_Blade",
    [
        (0.55, 0.010, 0.003, ksx, -0.08),
        (0.68, 0.011, 0.003, ksx - 0.004, -0.08),
        (0.82, 0.011, 0.0028, ksx - 0.008, -0.08),
        (0.96, 0.010, 0.0025, ksx - 0.012, -0.08),
        (1.10, 0.009, 0.0022, ksx - 0.016, -0.08),
        (1.22, 0.006, 0.0018, ksx - 0.018, -0.08),
        (1.30, 0.002, 0.0008, ksx - 0.020, -0.08),
    ],
    ns=6,
    cap_top=True,
    cap_bot=True,
)
setup(blade, "M_MetalSilver", col_name="Weapons", ss=1, outline=0)

bpy.ops.mesh.primitive_cylinder_add(
    vertices=16, radius=0.022, depth=0.005, location=(ksx, -0.08, 0.54)
)
tsuba = bpy.context.active_object
tsuba.name = "KT_Tsuba"
setup(tsuba, "M_MetalDark", col_name="Weapons", ss=1, outline=0.002)

kt_grip = loft(
    "KT_Grip",
    [
        (0.53, 0.010, 0.009, ksx, -0.08),
        (0.50, 0.011, 0.010, ksx, -0.08),
        (0.46, 0.011, 0.010, ksx, -0.08),
        (0.42, 0.010, 0.009, ksx, -0.08),
        (0.39, 0.009, 0.008, ksx, -0.08),
    ],
    ns=8,
)
setup(kt_grip, "M_KleinRed", col_name="Weapons", ss=1, outline=0)

# �的缠绕
for i in range(6):
    z = 0.40 + i * 0.022
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.012, minor_radius=0.002, location=(ksx, -0.08, z)
    )
    wr = bpy.context.active_object
    wr.name = f"KT_Wrap{i}"
    wr.scale = (1.0, 1.0, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    setup(wr, "M_FabricWhite", col_name="Weapons", ss=0, outline=0)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8, ring_count=6, radius=0.010, location=(ksx, -0.08, 0.38)
)
pm = bpy.context.active_object
pm.name = "KT_Pommel"
pm.scale = (1.0, 1.0, 0.7)
bpy.ops.object.transform_apply(scale=True)
setup(pm, "M_MetalDark", col_name="Weapons", ss=1, outline=0)

# 刀鞘 (挂在腰带)
sheath = loft(
    "KT_Sheath",
    [
        (0.50, 0.014, 0.008, ksx + 0.01, -0.05),
        (0.35, 0.015, 0.009, ksx + 0.01, -0.05),
        (0.20, 0.013, 0.008, ksx + 0.01, -0.05),
        (0.10, 0.010, 0.006, ksx + 0.01, -0.05),
    ],
    ns=8,
    cap_bot=True,
)
setup(sheath, "M_KleinBrown", col_name="Weapons", ss=1, outline=0.002)

print("✓ 克莱因+武士刀完成")

# === 逐暗者 (放在桐人旁边) ===
print("\n[逐暗者] Building...")
ex = 0.35

e_blade = loft(
    "E_Blade",
    [
        (0.50, 0.015, 0.003, ex, -0.10),
        (0.58, 0.016, 0.003, ex, -0.10),
        (0.80, 0.017, 0.0028, ex, -0.10),
        (1.05, 0.016, 0.0025, ex, -0.10),
        (1.25, 0.013, 0.0022, ex, -0.10),
        (1.40, 0.008, 0.0018, ex, -0.10),
        (1.48, 0.002, 0.0008, ex, -0.10),
    ],
    ns=6,
    cap_top=True,
    cap_bot=True,
)
setup(e_blade, "M_Elucidator", col_name="Weapons", ss=1, outline=0)

# 血槽
fuller = loft(
    "E_Fuller",
    [
        (0.62, 0.004, 0.001, ex, -0.10),
        (0.95, 0.004, 0.001, ex, -0.10),
        (1.20, 0.003, 0.0008, ex, -0.10),
    ],
    ns=4,
)
setup(fuller, "M_MetalDark", col_name="Weapons", ss=0, outline=0)

# 护手
guard = loft(
    "E_Guard",
    [
        (0.495, 0.055, 0.010, ex, -0.10),
        (0.500, 0.060, 0.012, ex, -0.10),
        (0.505, 0.060, 0.012, ex, -0.10),
        (0.510, 0.055, 0.010, ex, -0.10),
    ],
    ns=10,
)
setup(guard, "M_MetalDark", col_name="Weapons", ss=1, outline=0.002)

for dx in [0.060, -0.060]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.008, location=(ex + dx, -0.10, 0.50)
    )
    gb = bpy.context.active_object
    gb.name = f'E_GuardBall_{("L" if dx>0 else "R")}'
    setup(gb, "M_MetalDark", col_name="Weapons", ss=1, outline=0)

# 握柄
e_grip = loft(
    "E_Grip",
    [
        (0.49, 0.011, 0.010, ex, -0.10),
        (0.47, 0.012, 0.011, ex, -0.10),
        (0.44, 0.013, 0.012, ex, -0.10),
        (0.41, 0.012, 0.011, ex, -0.10),
        (0.39, 0.011, 0.010, ex, -0.10),
    ],
    ns=8,
)
setup(e_grip, "M_LeatherBrown", col_name="Weapons", ss=1, outline=0)

# 握柄纹路
for i in range(8):
    z = 0.395 + i * 0.012
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.014, minor_radius=0.002, location=(ex, -0.10, z)
    )
    wr = bpy.context.active_object
    wr.name = f"E_GripWrap{i}"
    wr.scale = (1.0, 1.0, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(wr, "M_KiritoBelt", col_name="Weapons", ss=0, outline=0)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=10, ring_count=8, radius=0.013, location=(ex, -0.10, 0.38)
)
pommel = bpy.context.active_object
pommel.name = "E_Pommel"
pommel.scale = (1.0, 1.0, 0.7)
bpy.ops.object.transform_apply(scale=True)
setup(pommel, "M_MetalDark", col_name="Weapons", ss=1, outline=0.002)

print("✓ 逐暗者完成")

# Save
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
print(f"\nSaved. Total objects: {len(bpy.data.objects)}")
