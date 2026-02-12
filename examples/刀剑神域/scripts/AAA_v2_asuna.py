"""
亚丝娜 (Asuna) - 基于参考图精确重建
参考图关键特征:
- 超长橙棕色头发(过腰), 额前刘海, 两侧编辫, 白色发箍
- 大琥珀色动漫眼, 精致面容
- 白色胸甲+大红色十字纹章
- 红色尖角肩甲
- 红色百褶裙(外)+白色内裙
- 白色长袖(胸甲下)
- 白色膝上靴
- 金色腰带/腰扣
"""
import bpy, bmesh, math
from mathutils import Vector

def loft(name, profiles, ns=16, cap_top=False, cap_bot=False):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for z, rx, ry, ox, oy in profiles:
        ring = []
        for i in range(ns):
            a = 2*math.pi*i/ns
            x = ox + rx*math.cos(a)
            y = oy + ry*math.sin(a)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for r in range(len(rings)-1):
        for i in range(ns):
            v1, v2 = rings[r][i], rings[r][(i+1)%ns]
            v3, v4 = rings[r+1][(i+1)%ns], rings[r+1][i]
            bm.faces.new([v1, v4, v3, v2])
    if cap_bot and rings: bm.faces.new(rings[0])
    if cap_top and rings: bm.faces.new(list(reversed(rings[-1])))
    bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def setup(obj, mat_name, col_name='Characters', ss=2, outline=0.004):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials: obj.data.materials[0] = mat
        else: obj.data.materials.append(mat)
    col = bpy.data.collections.get(col_name)
    if col:
        for c in obj.users_collection: c.objects.unlink(obj)
        col.objects.link(obj)
    if ss > 0:
        m = obj.modifiers.new('SS','SUBSURF'); m.levels=ss; m.render_levels=ss
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True); bpy.ops.object.shade_smooth(); obj.select_set(False)
    if outline > 0:
        om = bpy.data.materials.get('M_Outline')
        if om:
            m = obj.modifiers.new('Outline','SOLIDIFY')
            m.thickness=outline; m.offset=-1; m.use_flip_normals=True
            m.material_offset=len(obj.data.materials); obj.data.materials.append(om)

def hair_strip(name, loc, rot_deg, length, base_w, tip_w, mat='M_AsunaHair', thickness=0.010, ns=6):
    profiles = [
        (0, base_w, thickness, 0, 0),
        (length*0.3, base_w*0.88, thickness*0.9, 0, 0),
        (length*0.6, base_w*0.65, thickness*0.7, 0, 0),
        (length*0.85, base_w*0.35, thickness*0.4, 0, 0),
        (length, tip_w*0.3, thickness*0.1, 0, 0),
    ]
    obj = loft(name, profiles, ns=ns, cap_top=True, cap_bot=True)
    obj.location = loc
    obj.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    setup(obj, mat, ss=1, outline=0.003)
    return obj

ax = 1.0  # 亚丝娜位置

print("\n[亚丝娜] Building...")

# === 头部 ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.115, location=(ax, 0, 1.58))
head = bpy.context.active_object; head.name='A_Head'
head.scale = (1.0, 0.88, 1.08)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < 1.52:
        f = max(0, (1.52 - v.co.z) / 0.08)
        v.co.x *= (1.0 - f * 0.48)
        v.co.y *= (1.0 - f * 0.38)
    if v.co.y > 0.02: v.co.y *= 0.88
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode='OBJECT')
setup(head, 'M_Skin', outline=0.004)

# === 大眼睛 (琥珀色, 比桐人更大更圆) ===
for side, sx in [('L', 1), ('R', -1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.032,
        location=(ax+sx*0.038, -0.090, 1.585))
    ew = bpy.context.active_object; ew.name=f'A_EyeW{side}'
    ew.scale=(1.0, 0.5, 1.35); bpy.ops.object.transform_apply(scale=True)
    setup(ew, 'M_EyeWhite', ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.026,
        location=(ax+sx*0.038, -0.105, 1.583))
    iris = bpy.context.active_object; iris.name=f'A_Iris{side}'
    iris.scale=(1.0, 0.5, 1.35); bpy.ops.object.transform_apply(scale=True)
    setup(iris, 'M_AsunaEye', ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.012,
        location=(ax+sx*0.038, -0.115, 1.580))
    pupil = bpy.context.active_object; pupil.name=f'A_Pupil{side}'
    pupil.scale=(1.0, 0.5, 1.2); bpy.ops.object.transform_apply(scale=True)
    setup(pupil, 'M_EyeBlack', ss=0, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.009,
        location=(ax+sx*0.048, -0.118, 1.598))
    hl = bpy.context.active_object; hl.name=f'A_HL{side}'
    setup(hl, 'M_EyeHighlight', ss=0, outline=0)

# 鼻/嘴
bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.006,
    location=(ax, -0.108, 1.555))
nose = bpy.context.active_object; nose.name='A_Nose'
nose.scale=(0.5,0.5,0.7); bpy.ops.object.transform_apply(scale=True)
setup(nose, 'M_Skin', ss=1, outline=0)

# 眉毛
for side, sx in [('L', 1), ('R', -1)]:
    bpy.ops.mesh.primitive_cube_add(size=0.008, location=(ax+sx*0.038, -0.108, 1.618))
    brow = bpy.context.active_object; brow.name=f'A_Brow{side}'
    brow.scale=(3.0, 0.3, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(brow, 'M_AsunaHair', ss=1, outline=0)

print("  Head done")

# === 身体 (女性体型, 较纤细) ===
torso = loft('A_Torso', [
    (0.78, 0.125, 0.082, ax, 0),
    (0.85, 0.130, 0.088, ax, 0),
    (0.92, 0.138, 0.092, ax, 0),
    (0.98, 0.152, 0.100, ax, 0),
    (1.05, 0.158, 0.105, ax, 0),
    (1.12, 0.155, 0.100, ax, 0),
    (1.18, 0.148, 0.092, ax, 0),
    (1.25, 0.140, 0.085, ax, 0),
    (1.30, 0.085, 0.062, ax, 0),
    (1.35, 0.048, 0.044, ax, 0),
    (1.40, 0.042, 0.040, ax, 0),
    (1.44, 0.040, 0.038, ax, 0),
], ns=18)
setup(torso, 'M_Skin', outline=0.003)

# 手臂
for side, mx in [('L', 1), ('R', -1)]:
    arm = loft(f'A_Arm{side}', [
        (1.28, 0.040, 0.038, ax+mx*0.15, 0),
        (1.20, 0.034, 0.032, ax+mx*0.19, 0),
        (1.10, 0.030, 0.028, ax+mx*0.22, 0),
        (1.00, 0.028, 0.026, ax+mx*0.24, 0),
        (0.90, 0.025, 0.023, ax+mx*0.26, 0),
        (0.82, 0.023, 0.021, ax+mx*0.27, 0),
        (0.76, 0.021, 0.019, ax+mx*0.28, 0),
    ], ns=12)
    setup(arm, 'M_AsunaWhite', outline=0.003)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.022,
        location=(ax+mx*0.28, 0, 0.72))
    hand = bpy.context.active_object; hand.name=f'A_Hand{side}'
    hand.scale=(0.85, 0.5, 1.2); bpy.ops.object.transform_apply(scale=True)
    setup(hand, 'M_Skin', ss=1, outline=0)

# 腿
for side, mx in [('L', 1), ('R', -1)]:
    leg = loft(f'A_Leg{side}', [
        (0.78, 0.056, 0.048, ax+mx*0.058, 0),
        (0.68, 0.052, 0.046, ax+mx*0.062, 0),
        (0.55, 0.046, 0.042, ax+mx*0.065, 0),
        (0.42, 0.040, 0.036, ax+mx*0.065, 0),
        (0.32, 0.036, 0.033, ax+mx*0.065, 0),
        (0.22, 0.032, 0.030, ax+mx*0.065, 0),
        (0.14, 0.030, 0.028, ax+mx*0.065, 0),
        (0.08, 0.028, 0.026, ax+mx*0.065, 0),
    ], ns=14)
    setup(leg, 'M_Skin', outline=0.003)

# 白色膝上靴 (参考图: 白色, 有小跟)
for side, mx in [('L', 1), ('R', -1)]:
    boot = loft(f'A_Boot{side}', [
        (0.38, 0.038, 0.035, ax+mx*0.065, 0),
        (0.30, 0.040, 0.037, ax+mx*0.065, 0),
        (0.22, 0.042, 0.039, ax+mx*0.065, 0),
        (0.14, 0.043, 0.040, ax+mx*0.065, 0),
        (0.08, 0.044, 0.044, ax+mx*0.065, -0.005),
        (0.04, 0.044, 0.055, ax+mx*0.065, -0.012),
        (0.02, 0.042, 0.058, ax+mx*0.065, -0.015),
        (0.008, 0.040, 0.058, ax+mx*0.065, -0.015),
    ], ns=14, cap_bot=True)
    setup(boot, 'M_AsunaWhite', ss=1, outline=0.004)

    # 靴口金边
    bt = loft(f'A_BootTrim{side}', [
        (0.37, 0.040, 0.037, ax+mx*0.065, 0),
        (0.39, 0.042, 0.039, ax+mx*0.065, 0),
        (0.40, 0.040, 0.037, ax+mx*0.065, 0),
    ], ns=14)
    setup(bt, 'M_AsunaGold', ss=0, outline=0)

print("  Body done")

# === 头发 (超长橙棕色, 到腰部) ===
# 头发底球
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.130,
    location=(ax, 0.012, 1.62))
hb = bpy.context.active_object; hb.name='A_HairBase'
hb.scale=(1.05, 1.0, 1.02)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(hb.data)
bm.verts.ensure_lookup_table()
to_del = [v for v in bm.verts if v.co.z < 1.56 and v.co.y < 0.01]
bmesh.ops.delete(bm, geom=to_del, context='VERTS')
bmesh.update_edit_mesh(hb.data)
bpy.ops.object.mode_set(mode='OBJECT')
setup(hb, 'M_AsunaHair', outline=0.004)

# 刘海 (参考图: 整齐的中分式刘海)
a_bangs = [
    (-0.05, -0.09, 1.68, (58, 3, 12), 0.12, 0.040, 0.006),
    (-0.02, -0.10, 1.69, (62, 0, 5),  0.13, 0.035, 0.005),
    ( 0.02, -0.10, 1.69, (62, 0, -5), 0.13, 0.035, 0.005),
    ( 0.05, -0.09, 1.68, (58, -3,-12), 0.12, 0.040, 0.006),
    ( 0.00, -0.10, 1.70, (65, 0, 0),  0.11, 0.030, 0.004),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(a_bangs):
    hair_strip(f'A_Bang{i}', (ax+x, y, z), rot, ln, bw, tw)

# 超长后发 (参考图: 到腰部, 大片状) 
longhair_profiles = [
    (1.62, 0.11, 0.042, ax, 0.06),
    (1.50, 0.12, 0.048, ax, 0.07),
    (1.35, 0.13, 0.050, ax, 0.08),
    (1.15, 0.12, 0.048, ax, 0.07),
    (0.95, 0.11, 0.045, ax, 0.06),
    (0.80, 0.10, 0.040, ax, 0.05),
    (0.65, 0.09, 0.035, ax, 0.04),
    (0.50, 0.08, 0.028, ax, 0.03),
]
lh = loft('A_LongHair', longhair_profiles, ns=12)
setup(lh, 'M_AsunaHair', outline=0.004)

# 侧发 (框脸)
for side, sx in [('L', 1), ('R', -1)]:
    hair_strip(f'A_SideHair{side}0', (ax+sx*0.10, -0.03, 1.64), (82, sx*(-5), sx*(-20)), 0.28, 0.035, 0.006)
    hair_strip(f'A_SideHair{side}1', (ax+sx*0.12, 0.00, 1.62), (90, sx*(-3), sx*(-28)), 0.30, 0.032, 0.005)

# 编辫 (参考图: 两侧各一条粗辫子)
for side, sx in [('L', 1), ('R', -1)]:
    braid = loft(f'A_Braid{side}', [
        (1.52, 0.022, 0.020, ax+sx*0.10, 0.04),
        (1.38, 0.025, 0.022, ax+sx*0.11, 0.05),
        (1.22, 0.024, 0.020, ax+sx*0.10, 0.06),
        (1.05, 0.022, 0.018, ax+sx*0.09, 0.05),
        (0.90, 0.020, 0.016, ax+sx*0.08, 0.04),
        (0.78, 0.015, 0.012, ax+sx*0.07, 0.03),
    ], ns=8)
    setup(braid, 'M_AsunaHair', ss=1, outline=0.003)

    # 辫子末端蝴蝶结
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.012,
        location=(ax+sx*0.07, 0.03, 0.77))
    ribbon = bpy.context.active_object; ribbon.name=f'A_Ribbon{side}'
    setup(ribbon, 'M_AsunaRed', ss=0, outline=0)

# 发箍 (参考图: 白色头箍)
bpy.ops.mesh.primitive_torus_add(major_radius=0.122, minor_radius=0.007,
    location=(ax, 0, 1.67))
hband = bpy.context.active_object; hband.name='A_Headband'
hband.scale=(1.0, 0.90, 0.28)
bpy.ops.object.transform_apply(scale=True)
setup(hband, 'M_FabricWhite', ss=0, outline=0.002)

print("  Hair done")

# === KoB战斗装 ===
# 白色胸甲 (参考图: 覆盖上身的白色甲)
chest = loft('A_ChestArmor', [
    (0.96, 0.155, 0.102, ax, 0),
    (1.00, 0.162, 0.108, ax, 0),
    (1.05, 0.168, 0.112, ax, 0),
    (1.10, 0.172, 0.115, ax, 0),
    (1.15, 0.168, 0.108, ax, 0),
    (1.20, 0.162, 0.100, ax, 0),
    (1.26, 0.155, 0.092, ax, 0),
], ns=18)
setup(chest, 'M_AsunaWhite', outline=0.004)

# 大红色十字纹章 (参考图中央最显眼的标志)
bpy.ops.mesh.primitive_cube_add(size=0.008, location=(ax, -0.118, 1.10))
crH = bpy.context.active_object; crH.name='A_CrossH'
crH.scale=(7, 0.5, 1.5); bpy.ops.object.transform_apply(scale=True)
setup(crH, 'M_AsunaRed', ss=0, outline=0)

bpy.ops.mesh.primitive_cube_add(size=0.008, location=(ax, -0.118, 1.10))
crV = bpy.context.active_object; crV.name='A_CrossV'
crV.scale=(1.5, 0.5, 7); bpy.ops.object.transform_apply(scale=True)
setup(crV, 'M_AsunaRed', ss=0, outline=0)

# 红色尖角肩甲 (参考图: 明显的三角形肩甲)
for side, mx in [('L', 1), ('R', -1)]:
    sp = loft(f'A_ShoulderPad{side}', [
        (1.24, 0.010, 0.008, ax+mx*0.14, -0.01),
        (1.27, 0.035, 0.025, ax+mx*0.16, -0.02),
        (1.30, 0.045, 0.030, ax+mx*0.17, -0.01),
        (1.32, 0.035, 0.022, ax+mx*0.16, 0.00),
        (1.34, 0.010, 0.008, ax+mx*0.15, 0.00),
    ], ns=10)
    setup(sp, 'M_AsunaRed', ss=1, outline=0.003)

    # 肩甲金边
    bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.003,
        location=(ax+mx*0.16, -0.01, 1.28))
    spt = bpy.context.active_object; spt.name=f'A_ShoulderTrim{side}'
    spt.scale=(1.0, 0.7, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(spt, 'M_AsunaGold', ss=0, outline=0)

# 红色百褶裙 (参考图: 红色外裙+白色内层)
skirt_out = loft('A_SkirtOuter', [
    (0.82, 0.140, 0.095, ax, 0),
    (0.78, 0.155, 0.105, ax, 0),
    (0.72, 0.178, 0.118, ax, 0),
    (0.65, 0.200, 0.132, ax, 0),
    (0.58, 0.218, 0.142, ax, 0),
    (0.52, 0.235, 0.150, ax, 0),
], ns=20)
setup(skirt_out, 'M_AsunaRed', outline=0.004)

# 白色内裙 (底部露出)
skirt_in = loft('A_SkirtInner', [
    (0.80, 0.135, 0.092, ax, 0),
    (0.74, 0.152, 0.102, ax, 0),
    (0.66, 0.175, 0.115, ax, 0),
    (0.58, 0.195, 0.128, ax, 0),
    (0.52, 0.210, 0.138, ax, 0),
    (0.48, 0.225, 0.148, ax, 0),
], ns=20)
setup(skirt_in, 'M_FabricWhite', ss=1, outline=0)

# 裙摆金边
skirt_trim = loft('A_SkirtTrim', [
    (0.51, 0.237, 0.152, ax, 0),
    (0.53, 0.240, 0.154, ax, 0),
    (0.55, 0.238, 0.152, ax, 0),
], ns=20)
setup(skirt_trim, 'M_AsunaGold', ss=0, outline=0)

# 金色腰带
a_belt = loft('A_Belt', [
    (0.82, 0.143, 0.098, ax, 0),
    (0.84, 0.148, 0.102, ax, 0),
    (0.86, 0.145, 0.100, ax, 0),
], ns=18)
setup(a_belt, 'M_AsunaGold', ss=1, outline=0.002)

# 腰带扣
bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.010,
    location=(ax, -0.105, 0.84))
ab = bpy.context.active_object; ab.name='A_BeltBuckle'
ab.scale=(1.2, 0.5, 1.0); bpy.ops.object.transform_apply(scale=True)
setup(ab, 'M_AsunaGold', ss=0, outline=0)

print("  KoB outfit done")
print("✓ 亚丝娜完成")

# ============================================================
# 闪光 (Lambent Light)
# ============================================================
print("\n[闪光] Building...")
lx = ax + 0.35

ll_blade = loft('LL_Blade', [
    (0.65, 0.004, 0.003, lx, -0.08),
    (0.80, 0.0045, 0.0032, lx, -0.08),
    (1.00, 0.004, 0.0028, lx, -0.08),
    (1.20, 0.0035, 0.0024, lx, -0.08),
    (1.38, 0.002, 0.0015, lx, -0.08),
    (1.45, 0.0005, 0.0004, lx, -0.08),
], ns=6, cap_top=True, cap_bot=True)
setup(ll_blade, 'M_LambentLight', col_name='Weapons', ss=1, outline=0)

bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.004,
    location=(lx, -0.08, 0.64))
guard = bpy.context.active_object; guard.name='LL_Guard'
guard.rotation_euler=(math.radians(90), 0, 0)
setup(guard, 'M_MetalSilver', col_name='Weapons', ss=0, outline=0)

ll_grip = loft('LL_Grip', [
    (0.63, 0.008, 0.007, lx, -0.08),
    (0.60, 0.009, 0.008, lx, -0.08),
    (0.57, 0.009, 0.008, lx, -0.08),
    (0.54, 0.008, 0.007, lx, -0.08),
], ns=8)
setup(ll_grip, 'M_FabricWhite', col_name='Weapons', ss=1, outline=0)

bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.009,
    location=(lx, -0.08, 0.53))
pm = bpy.context.active_object; pm.name='LL_Pommel'
setup(pm, 'M_MetalSilver', col_name='Weapons', ss=1, outline=0)

print("✓ 闪光完成")

# Save
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
print(f"\nSaved. Objects: {len(bpy.data.objects)}")
