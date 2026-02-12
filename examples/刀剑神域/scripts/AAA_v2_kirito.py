"""
桐人 (Kirito) - 基于参考图精确重建
参考图关键特征:
- 大块蓬松黑色刺发, 刘海遮额, 后发及领
- 女性化面容, 大而深色的动漫眼睛
- 标志性黑色长风衣, 所有边缘有银白色镶边线
- 胸前交叉皮带/背带, 银色扣环
- 黑色修身裤, 中筒黑靴(银扣)
- 无指手套
"""
import bpy, bmesh, math
from mathutils import Vector

# ============ 清场 ============
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ============ 工具函数 ============
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
    if cap_bot and rings:
        bm.faces.new(rings[0])
    if cap_top and rings:
        bm.faces.new(list(reversed(rings[-1])))
    bm.to_mesh(mesh)
    bm.free()
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
        m = obj.modifiers.new('SS','SUBSURF')
        m.levels = ss; m.render_levels = ss
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    if outline > 0:
        om = bpy.data.materials.get('M_Outline')
        if om:
            m = obj.modifiers.new('Outline','SOLIDIFY')
            m.thickness = outline; m.offset = -1
            m.use_flip_normals = True
            m.material_offset = len(obj.data.materials)
            obj.data.materials.append(om)

def hair_strip(name, loc, rot_deg, length, base_w, tip_w, thickness=0.012, ns=6):
    """创建锥形发束"""
    profiles = [
        (0,         base_w, thickness,   0, 0),
        (length*0.25, base_w*0.85, thickness*0.9, 0, 0),
        (length*0.5,  base_w*0.6, thickness*0.7, 0, 0),
        (length*0.75, base_w*0.35, thickness*0.5, 0, 0),
        (length*0.9,  tip_w*1.5, thickness*0.3, 0, 0),
        (length,      tip_w*0.3, thickness*0.1, 0, 0),
    ]
    obj = loft(name, profiles, ns=ns, cap_top=True, cap_bot=True)
    obj.location = loc
    rx, ry, rz = [math.radians(d) for d in rot_deg]
    obj.rotation_euler = (rx, ry, rz)
    setup(obj, 'M_KiritoHair', ss=1, outline=0.003)
    return obj

# ============ 集合 ============
for c in ['Characters','Weapons','Environment','Lighting']:
    if c not in bpy.data.collections:
        col = bpy.data.collections.new(c)
        bpy.context.scene.collection.children.link(col)

# ============ 材质系统 ============
def toon_mat(name, rgb, shadow=(0.55,0.50,0.60), rp=0.42, rim=0.3, spec=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True; mat.use_backface_culling = True
    N = mat.node_tree.nodes; L = mat.node_tree.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial'); out.location=(1200,0)
    diff = N.new('ShaderNodeBsdfDiffuse'); diff.inputs['Color'].default_value=(*rgb,1); diff.location=(-400,100)
    s2r = N.new('ShaderNodeShaderToRGB'); s2r.location=(-200,100)
    L.new(diff.outputs['BSDF'], s2r.inputs['Shader'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.location=(0,100)
    ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements[0].color=(rgb[0]*shadow[0],rgb[1]*shadow[1],rgb[2]*shadow[2],1)
    ramp.color_ramp.elements[1].color=(*rgb,1); ramp.color_ramp.elements[1].position=rp
    L.new(s2r.outputs['Color'], ramp.inputs['Fac'])
    fres = N.new('ShaderNodeFresnel'); fres.inputs['IOR'].default_value=1.45; fres.location=(-200,-200)
    rr = N.new('ShaderNodeValToRGB'); rr.location=(0,-200)
    rr.color_ramp.interpolation='CONSTANT'
    rr.color_ramp.elements[0].color=(0,0,0,1); rr.color_ramp.elements[1].color=(1,1,1,1)
    rr.color_ramp.elements[1].position=0.75
    L.new(fres.outputs['Fac'], rr.inputs['Fac'])
    mix = N.new('ShaderNodeMixRGB'); mix.blend_type='ADD'; mix.inputs['Fac'].default_value=rim; mix.location=(400,0)
    L.new(ramp.outputs['Color'], mix.inputs[1]); L.new(rr.outputs['Color'], mix.inputs[2])
    fi = mix
    if spec:
        gl = N.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value=0.3; gl.location=(-400,-400)
        sr2 = N.new('ShaderNodeShaderToRGB'); sr2.location=(-200,-400)
        L.new(gl.outputs['BSDF'], sr2.inputs['Shader'])
        sramp = N.new('ShaderNodeValToRGB'); sramp.location=(0,-400)
        sramp.color_ramp.interpolation='CONSTANT'
        sramp.color_ramp.elements[0].color=(0,0,0,1); sramp.color_ramp.elements[1].color=(1,1,1,1)
        sramp.color_ramp.elements[1].position=0.9
        L.new(sr2.outputs['Color'], sramp.inputs['Fac'])
        sa = N.new('ShaderNodeMixRGB'); sa.blend_type='ADD'; sa.inputs['Fac'].default_value=0.15; sa.location=(600,0)
        L.new(mix.outputs['Color'], sa.inputs[1]); L.new(sramp.outputs['Color'], sa.inputs[2])
        fi = sa
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1.0; em.location=(900,0)
    L.new(fi.outputs['Color'], em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def metal_mat(name, rgb):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True; mat.use_backface_culling = True
    N = mat.node_tree.nodes; L = mat.node_tree.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial'); out.location=(800,0)
    gl = N.new('ShaderNodeBsdfGlossy'); gl.inputs['Color'].default_value=(*rgb,1); gl.inputs['Roughness'].default_value=0.12; gl.location=(-300,0)
    s2r = N.new('ShaderNodeShaderToRGB'); s2r.location=(-100,0)
    L.new(gl.outputs['BSDF'], s2r.inputs['Shader'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.location=(100,0)
    ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements[0].color=(rgb[0]*0.25,rgb[1]*0.25,rgb[2]*0.3,1)
    ramp.color_ramp.elements[1].color=(*rgb,1); ramp.color_ramp.elements[1].position=0.35
    hl = ramp.color_ramp.elements.new(0.88)
    hl.color=(min(1,rgb[0]+0.35),min(1,rgb[1]+0.35),min(1,rgb[2]+0.35),1)
    L.new(s2r.outputs['Color'], ramp.inputs['Fac'])
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1.0; em.location=(400,0)
    L.new(ramp.outputs['Color'], em.inputs['Color']); L.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

# Outline mat
om = bpy.data.materials.new('M_Outline')
om.use_nodes=True; om.use_backface_culling=True
ns=om.node_tree.nodes; ls=om.node_tree.links; ns.clear()
o=ns.new('ShaderNodeOutputMaterial'); o.location=(300,0)
e=ns.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(0.01,0.01,0.02,1); e.inputs['Strength'].default_value=0; e.location=(100,0)
ls.new(e.outputs['Emission'], o.inputs['Surface'])

# Eye highlight
eh = bpy.data.materials.new('M_EyeHighlight')
eh.use_nodes=True
ns=eh.node_tree.nodes; ls=eh.node_tree.links; ns.clear()
o=ns.new('ShaderNodeOutputMaterial'); o.location=(300,0)
e=ns.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(1,1,1,1); e.inputs['Strength'].default_value=3.0; e.location=(100,0)
ls.new(e.outputs['Emission'], o.inputs['Surface'])

# Kirito materials
toon_mat('M_Skin', (0.94,0.80,0.70), rim=0.2)
toon_mat('M_KiritoBlack', (0.030,0.030,0.035), shadow=(0.5,0.5,0.5), rim=0.4)
toon_mat('M_KiritoHair', (0.025,0.025,0.04), shadow=(0.4,0.4,0.5), rim=0.5, spec=True)
toon_mat('M_KiritoBelt', (0.22,0.12,0.06), rim=0.15)
toon_mat('M_KiritoEye', (0.12,0.12,0.15), shadow=(0.4,0.4,0.4))
metal_mat('M_KiritoSilver', (0.78,0.78,0.80))
toon_mat('M_KiritoTrim', (0.70,0.70,0.72), shadow=(0.5,0.5,0.5), rim=0.2)
toon_mat('M_EyeBlack', (0.015,0.015,0.02))
toon_mat('M_EyeWhite', (0.95,0.95,0.95))

# 其他角色材质
toon_mat('M_AsunaWhite', (0.95,0.95,0.93), rim=0.25, spec=True)
toon_mat('M_AsunaRed', (0.78,0.18,0.18), rim=0.3)
toon_mat('M_AsunaHair', (0.76,0.44,0.18), shadow=(0.5,0.45,0.5), rim=0.35, spec=True)
toon_mat('M_AsunaEye', (0.52,0.38,0.06))
metal_mat('M_AsunaGold', (0.82,0.68,0.20))
toon_mat('M_KleinRed', (0.70,0.24,0.16), rim=0.3)
toon_mat('M_KleinHair', (0.70,0.24,0.16), shadow=(0.45,0.4,0.45), rim=0.4)
toon_mat('M_KleinCream', (0.90,0.85,0.76))
toon_mat('M_KleinBrown', (0.28,0.18,0.12))
toon_mat('M_FabricWhite', (0.91,0.91,0.89))
toon_mat('M_LeatherBrown', (0.28,0.15,0.07))
toon_mat('M_SkinTan', (0.72,0.52,0.38), rim=0.2)
metal_mat('M_Elucidator', (0.025,0.025,0.03))
metal_mat('M_MetalDark', (0.06,0.06,0.07))
metal_mat('M_MetalSilver', (0.68,0.68,0.70))
metal_mat('M_LambentLight', (0.90,0.90,0.93))
metal_mat('M_MetalGold', (0.82,0.68,0.20))

print(f"Materials: {len(bpy.data.materials)}")

# ============ 光照 ============
lcol = bpy.data.collections['Lighting']
bpy.ops.object.light_add(type='SUN', location=(5,-5,10))
kl = bpy.context.active_object; kl.name='KeyLight'
kl.rotation_euler=(math.radians(50),math.radians(10),math.radians(30))
kl.data.energy=3.5; kl.data.color=(1.0,0.95,0.88)
for c in kl.users_collection: c.objects.unlink(kl)
lcol.objects.link(kl)

bpy.ops.object.light_add(type='SUN', location=(-5,-3,5))
fl = bpy.context.active_object; fl.name='FillLight'
fl.rotation_euler=(math.radians(65),math.radians(-30),math.radians(-20))
fl.data.energy=1.2; fl.data.color=(0.82,0.88,1.0)
for c in fl.users_collection: c.objects.unlink(fl)
lcol.objects.link(fl)

bpy.ops.object.light_add(type='SUN', location=(0,5,8))
rl = bpy.context.active_object; rl.name='RimLight'
rl.rotation_euler=(math.radians(-30),0,math.radians(180))
rl.data.energy=2.0
for c in rl.users_collection: c.objects.unlink(rl)
lcol.objects.link(rl)

bpy.ops.object.camera_add(location=(0,-5,1.2))
cam = bpy.context.active_object; cam.name='MainCamera'
cam.rotation_euler=(math.radians(86),0,0); cam.data.lens=65
bpy.context.scene.camera = cam
for c in cam.users_collection: c.objects.unlink(cam)
lcol.objects.link(cam)

# EEVEE
sc = bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1920; sc.render.resolution_y=1080
sc.render.film_transparent=True
sc.view_settings.view_transform='Standard'

print("Lighting ready")

# ============================================================
# 桐人身体 - 基于参考图精确比例
# 参考图: 7.5头身, 纤细体型, 女性化面容
# ============================================================
print("\n[桐人] Building...")

# --- 头部 (更大, 更动漫化) ---
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.125, location=(0,0,1.62))
head = bpy.context.active_object; head.name='K_Head'
# 动漫化: 前额稍宽, 下巴尖
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    lz = v.co.z
    # 下巴收窄 (V形)
    if lz < 1.56:
        f = max(0, (1.56 - lz) / 0.10)
        v.co.x *= (1.0 - f * 0.45)
        v.co.y *= (1.0 - f * 0.35)
    # 颧骨略宽
    if 1.58 < lz < 1.65:
        v.co.x *= 1.05
    # 后脑略扁
    if v.co.y > 0.02:
        v.co.y *= 0.90
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode='OBJECT')
setup(head, 'M_Skin', outline=0.004)

# --- 眼睛 (大型动漫眼, 占脸宽1/4) ---
for side, sx in [('L', 1), ('R', -1)]:
    # 眼白
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.030,
        location=(sx*0.042, -0.095, 1.625))
    ew = bpy.context.active_object; ew.name=f'K_EyeW{side}'
    ew.scale = (1.0, 0.5, 1.3)
    bpy.ops.object.transform_apply(scale=True)
    setup(ew, 'M_EyeWhite', ss=1, outline=0)

    # 虹膜 (大)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.024,
        location=(sx*0.042, -0.112, 1.622))
    iris = bpy.context.active_object; iris.name=f'K_Iris{side}'
    iris.scale = (1.0, 0.5, 1.3)
    bpy.ops.object.transform_apply(scale=True)
    setup(iris, 'M_KiritoEye', ss=1, outline=0)

    # 瞳孔 (黑)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.012,
        location=(sx*0.042, -0.120, 1.620))
    pupil = bpy.context.active_object; pupil.name=f'K_Pupil{side}'
    pupil.scale = (1.0, 0.5, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    setup(pupil, 'M_EyeBlack', ss=0, outline=0)

    # 高光 (2个)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.008,
        location=(sx*0.052, -0.125, 1.638))
    hl1 = bpy.context.active_object; hl1.name=f'K_HL1{side}'
    setup(hl1, 'M_EyeHighlight', ss=0, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=4, radius=0.005,
        location=(sx*0.035, -0.122, 1.612))
    hl2 = bpy.context.active_object; hl2.name=f'K_HL2{side}'
    setup(hl2, 'M_EyeHighlight', ss=0, outline=0)

# 鼻子 (微小凸起)
bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.008,
    location=(0, -0.118, 1.595))
nose = bpy.context.active_object; nose.name='K_Nose'
nose.scale = (0.6, 0.6, 0.8)
bpy.ops.object.transform_apply(scale=True)
setup(nose, 'M_Skin', ss=1, outline=0)

# 嘴 (细线)
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(0, -0.112, 1.565))
mouth = bpy.context.active_object; mouth.name='K_Mouth'
mouth.scale = (2.5, 0.3, 0.2)
bpy.ops.object.transform_apply(scale=True)
setup(mouth, 'M_KiritoBelt', ss=1, outline=0)

# 眉毛
for side, sx in [('L', 1), ('R', -1)]:
    bpy.ops.mesh.primitive_cube_add(size=0.01, location=(sx*0.042, -0.118, 1.660))
    brow = bpy.context.active_object; brow.name=f'K_Brow{side}'
    brow.scale = (3.0, 0.3, 0.3)
    brow.rotation_euler = (0, 0, math.radians(sx*(-5)))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    setup(brow, 'M_KiritoHair', ss=1, outline=0)

print("  Head done")

# --- 躯干 (纤细, 参考图偏瘦) ---
torso = loft('K_Torso', [
    (0.82, 0.135, 0.088, 0, 0),
    (0.90, 0.140, 0.095, 0, 0),
    (0.98, 0.155, 0.102, 0, 0),
    (1.08, 0.170, 0.110, 0, 0),
    (1.18, 0.175, 0.112, 0, 0),
    (1.28, 0.168, 0.100, 0, 0),
    (1.34, 0.155, 0.090, 0, 0),
    (1.38, 0.085, 0.065, 0, 0),
    (1.42, 0.055, 0.050, 0, 0),
    (1.48, 0.048, 0.045, 0, 0),
], ns=20)
setup(torso, 'M_Skin', outline=0.003)

# --- 手臂 ---
for side, mx in [('L', 1), ('R', -1)]:
    arm = loft(f'K_Arm{side}', [
        (1.34, 0.045, 0.042, mx*0.17, 0),
        (1.25, 0.038, 0.036, mx*0.22, 0),
        (1.15, 0.035, 0.033, mx*0.26, 0),
        (1.05, 0.033, 0.031, mx*0.28, 0),
        (0.95, 0.030, 0.028, mx*0.30, 0),
        (0.86, 0.027, 0.025, mx*0.31, 0),
        (0.80, 0.025, 0.023, mx*0.32, 0),
    ], ns=12)
    setup(arm, 'M_Skin', outline=0.003)

    # 手 (带简化手指)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.025,
        location=(mx*0.32, 0, 0.76))
    hand = bpy.context.active_object; hand.name=f'K_Hand{side}'
    hand.scale = (0.9, 0.55, 1.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(hand, 'M_Skin', ss=1, outline=0)

# --- 腿 ---
for side, mx in [('L', 1), ('R', -1)]:
    leg = loft(f'K_Leg{side}', [
        (0.82, 0.062, 0.052, mx*0.070, 0),
        (0.72, 0.058, 0.050, mx*0.075, 0),
        (0.60, 0.052, 0.046, mx*0.078, 0),
        (0.48, 0.045, 0.040, mx*0.080, 0),
        (0.36, 0.040, 0.036, mx*0.080, 0),
        (0.25, 0.036, 0.032, mx*0.080, 0),
        (0.15, 0.033, 0.030, mx*0.080, 0),
        (0.08, 0.032, 0.028, mx*0.080, 0),
    ], ns=14)
    setup(leg, 'M_KiritoBlack', outline=0.003)

# --- 靴子 ---
for side, mx in [('L', 1), ('R', -1)]:
    boot = loft(f'K_Boot{side}', [
        (0.20, 0.040, 0.038, mx*0.080, 0),
        (0.14, 0.042, 0.040, mx*0.080, 0),
        (0.08, 0.044, 0.042, mx*0.080, 0),
        (0.04, 0.046, 0.052, mx*0.080, -0.008),
        (0.015, 0.044, 0.065, mx*0.080, -0.018),
        (0.003, 0.042, 0.068, mx*0.080, -0.020),
    ], ns=14, cap_bot=True)
    setup(boot, 'M_KiritoBlack', ss=1, outline=0.004)
    # 靴扣
    bpy.ops.mesh.primitive_cube_add(size=0.008, location=(mx*0.080, -0.040, 0.12))
    bk = bpy.context.active_object; bk.name=f'K_BootBuckle{side}'
    bk.scale = (1.5, 0.5, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    setup(bk, 'M_KiritoSilver', ss=0, outline=0)

print("  Body done")

# ============================================================
# 桐人头发 - 参考图: 大块蓬松刺发
# 关键: 比头大很多, 刘海厚重遮额, 侧发到耳下, 后发到领
# ============================================================

# 头发底层球 (比头大)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.145,
    location=(0, 0.015, 1.66))
hbase = bpy.context.active_object; hbase.name='K_HairBase'
hbase.scale = (1.08, 1.0, 1.05)
bpy.ops.object.transform_apply(scale=True)
# 裁掉下半 (只保留头顶)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(hbase.data)
bm.verts.ensure_lookup_table()
to_del = [v for v in bm.verts if v.co.z < 1.60 and v.co.y < 0.02]
bmesh.ops.delete(bm, geom=to_del, context='VERTS')
bmesh.update_edit_mesh(hbase.data)
bpy.ops.object.mode_set(mode='OBJECT')
setup(hbase, 'M_KiritoHair', outline=0.004)

# === 厚重刘海 (参考图: 5-6束大刘海覆盖额头, 达到眼睛上方) ===
bang_data = [
    # (x, y, z, rot_xyz_deg, length, base_w, tip_w)
    (-0.07, -0.10, 1.73, (60, 5, 15), 0.14, 0.045, 0.008),
    (-0.03, -0.11, 1.74, (65, 0, 6),  0.15, 0.040, 0.006),
    ( 0.02, -0.12, 1.75, (68, 0, -2), 0.16, 0.042, 0.007),
    ( 0.06, -0.11, 1.74, (64, -3, -8), 0.14, 0.038, 0.006),
    ( 0.10, -0.09, 1.72, (58, -5,-15), 0.13, 0.035, 0.008),
    (-0.01, -0.12, 1.75, (70, 2, 2),  0.13, 0.035, 0.005),
    ( 0.04, -0.11, 1.74, (66, -1, -5), 0.12, 0.030, 0.005),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(bang_data):
    hair_strip(f'K_Bang{i}', (x,y,z), rot, ln, bw, tw)

# === 侧发 (参考图: 大块侧发到耳下) ===
side_data = [
    # 左侧
    ( 0.12, -0.03, 1.68, (80, -8, -22), 0.20, 0.045, 0.008),
    ( 0.14,  0.00, 1.66, (90, -5, -30), 0.22, 0.040, 0.007),
    ( 0.11, -0.06, 1.70, (75, -3, -18), 0.18, 0.038, 0.008),
    ( 0.13,  0.03, 1.65, (95, -5, -35), 0.20, 0.035, 0.006),
    # 右侧
    (-0.12, -0.03, 1.68, (80, 8, 22), 0.20, 0.045, 0.008),
    (-0.14,  0.00, 1.66, (90, 5, 30), 0.22, 0.040, 0.007),
    (-0.11, -0.06, 1.70, (75, 3, 18), 0.18, 0.038, 0.008),
    (-0.13,  0.03, 1.65, (95, 5, 35), 0.20, 0.035, 0.006),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(side_data):
    hair_strip(f'K_Side{i}', (x,y,z), rot, ln, bw, tw)

# === 后发 (参考图: 到衣领高度, 多层) ===
back_data = [
    ( 0.00, 0.10, 1.68, (105, 0, 0),  0.22, 0.045, 0.008),
    (-0.05, 0.09, 1.67, (100, 5, -8), 0.20, 0.040, 0.007),
    ( 0.05, 0.09, 1.67, (100,-5,  8), 0.20, 0.040, 0.007),
    (-0.03, 0.11, 1.69, (108, 3, -4), 0.24, 0.042, 0.009),
    ( 0.03, 0.11, 1.69, (108,-3,  4), 0.24, 0.042, 0.009),
    ( 0.00, 0.08, 1.65, (98,  0,  0), 0.18, 0.038, 0.006),
    (-0.06, 0.07, 1.64, (95,  5,-12), 0.17, 0.035, 0.006),
    ( 0.06, 0.07, 1.64, (95, -5, 12), 0.17, 0.035, 0.006),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(back_data):
    hair_strip(f'K_Back{i}', (x,y,z), rot, ln, bw, tw)

# === 头顶翘发 (参考图: 几束向上/向后翘的发束) ===
top_data = [
    ( 0.00, -0.02, 1.78, (25, 0, 0),  0.10, 0.035, 0.005),
    (-0.04,  0.00, 1.79, (15, 5, -10), 0.09, 0.030, 0.004),
    ( 0.04,  0.00, 1.79, (15,-5,  10), 0.09, 0.030, 0.004),
    (-0.02,  0.04, 1.78, (0,  5, -5),  0.08, 0.028, 0.004),
    ( 0.02,  0.04, 1.78, (0, -5,  5),  0.08, 0.028, 0.004),
]
for i, (x, y, z, rot, ln, bw, tw) in enumerate(top_data):
    hair_strip(f'K_Top{i}', (x,y,z), rot, ln, bw, tw)

print("  Hair done")

# ============================================================
# 桐人风衣 - 关键特征: 银白色边线装饰
# 参考图: 长至膝下, 前开襟, 立领, 所有边缘有银色装饰线
# ============================================================

# 风衣主体
coat = loft('K_Coat', [
    (1.44, 0.062, 0.056, 0, 0),      # 领口
    (1.40, 0.095, 0.070, 0, 0),      # 领
    (1.36, 0.170, 0.098, 0, 0),      # 肩
    (1.28, 0.190, 0.115, 0, 0),      # 上胸
    (1.18, 0.195, 0.120, 0, 0),      # 胸
    (1.08, 0.185, 0.115, 0, 0),      # 下胸
    (0.98, 0.170, 0.108, 0, 0),      # 腰
    (0.88, 0.165, 0.105, 0, 0),      # 腰带
    (0.75, 0.185, 0.112, 0, 0),      # 臀
    (0.60, 0.215, 0.120, 0, 0),      # 大腿
    (0.45, 0.245, 0.130, 0, 0),      # 膝
    (0.32, 0.275, 0.140, 0, 0),      # 膝下
    (0.22, 0.290, 0.145, 0, 0),      # 下摆
], ns=24)
setup(coat, 'M_KiritoBlack', outline=0.005)

# === 银色镶边线 (风衣的标志性特征) ===
# 前襟左右边线 (从领到下摆的竖线)
for side, sx in [('L', 1), ('R', -1)]:
    trim_front = loft(f'K_TrimFront{side}', [
        (1.40, 0.006, 0.003, sx*0.060, -0.072),
        (1.28, 0.006, 0.003, sx*0.065, -0.118),
        (1.18, 0.006, 0.003, sx*0.058, -0.122),
        (1.08, 0.006, 0.003, sx*0.050, -0.118),
        (0.98, 0.006, 0.003, sx*0.045, -0.110),
        (0.88, 0.006, 0.003, sx*0.042, -0.108),
        (0.75, 0.006, 0.003, sx*0.048, -0.115),
        (0.60, 0.006, 0.003, sx*0.055, -0.122),
        (0.45, 0.006, 0.003, sx*0.062, -0.132),
        (0.32, 0.006, 0.003, sx*0.070, -0.142),
        (0.22, 0.006, 0.003, sx*0.075, -0.148),
    ], ns=6)
    setup(trim_front, 'M_KiritoTrim', ss=0, outline=0)

# 下摆边线 (环形)
trim_hem = loft('K_TrimHem', [
    (0.21, 0.292, 0.147, 0, 0),
    (0.23, 0.294, 0.148, 0, 0),
    (0.25, 0.292, 0.147, 0, 0),
], ns=24)
setup(trim_hem, 'M_KiritoTrim', ss=0, outline=0)

# 袖口边线
for side, mx in [('L', 1), ('R', -1)]:
    cuff_trim = loft(f'K_CuffTrim{side}', [
        (0.79, 0.030, 0.028, mx*0.32, 0),
        (0.81, 0.032, 0.030, mx*0.32, 0),
        (0.83, 0.030, 0.028, mx*0.32, 0),
    ], ns=10)
    setup(cuff_trim, 'M_KiritoTrim', ss=0, outline=0)

# 立领
collar = loft('K_Collar', [
    (1.44, 0.064, 0.058, 0, 0),
    (1.47, 0.068, 0.060, 0, 0),
    (1.50, 0.065, 0.052, 0, 0),
    (1.52, 0.055, 0.045, 0, 0),
], ns=16)
setup(collar, 'M_KiritoBlack', ss=1, outline=0.003)

# 领口边线
collar_trim = loft('K_CollarTrim', [
    (1.50, 0.067, 0.054, 0, 0),
    (1.52, 0.057, 0.047, 0, 0),
    (1.53, 0.055, 0.045, 0, 0),
], ns=16)
setup(collar_trim, 'M_KiritoTrim', ss=0, outline=0)

# === 胸前交叉背带/皮带 (参考图显示X形) ===
for side, sx in [('L', 1), ('R', -1)]:
    strap_profiles = [
        (1.30, 0.008, 0.004, sx*0.12, -0.10),
        (1.20, 0.008, 0.004, sx*0.06, -0.11),
        (1.10, 0.008, 0.004, 0.00,    -0.12),
        (1.00, 0.008, 0.004, -sx*0.04, -0.11),
        (0.90, 0.008, 0.004, -sx*0.06, -0.10),
    ]
    strap = loft(f'K_Strap{side}', strap_profiles, ns=6)
    setup(strap, 'M_KiritoBelt', ss=0, outline=0.002)

    # 银扣环
    bpy.ops.mesh.primitive_torus_add(major_radius=0.012, minor_radius=0.003,
        location=(0, -0.125, 1.10))
    buckle = bpy.context.active_object; buckle.name=f'K_StrapBuckle{side}'
    setup(buckle, 'M_KiritoSilver', ss=0, outline=0)

# 腰带
belt = loft('K_Belt', [
    (0.86, 0.170, 0.110, 0, 0),
    (0.88, 0.175, 0.114, 0, 0),
    (0.90, 0.173, 0.112, 0, 0),
], ns=20)
setup(belt, 'M_KiritoBelt', ss=1, outline=0.003)

# 腰带扣
bpy.ops.mesh.primitive_cube_add(size=0.015, location=(0, -0.116, 0.88))
bb = bpy.context.active_object; bb.name='K_BeltBuckle'
bb.scale = (1.5, 0.5, 0.8)
bpy.ops.object.transform_apply(scale=True)
setup(bb, 'M_KiritoSilver', ss=0, outline=0)

# 肩扣
for side, x in [('L', 0.17), ('R', -0.17)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.010,
        location=(x, -0.06, 1.34))
    pin = bpy.context.active_object; pin.name=f'K_ShoulderPin{side}'
    setup(pin, 'M_KiritoSilver', ss=0, outline=0)

# 无指手套
for side, mx in [('L', 1), ('R', -1)]:
    glove = loft(f'K_Glove{side}', [
        (0.80, 0.028, 0.026, mx*0.32, 0),
        (0.78, 0.030, 0.028, mx*0.32, 0),
        (0.76, 0.028, 0.026, mx*0.32, 0),
    ], ns=10)
    setup(glove, 'M_KiritoBlack', ss=0, outline=0.002)

print("  Coat done")
print("✓ 桐人完成")

# ============================================================
# 保存
# ============================================================
bpy.ops.object.select_all(action='DESELECT')
fp = r"E:\Projects\blender-mcp\examples\sao_xianjian_demo.blend"
bpy.ops.wm.save_mainfile(filepath=fp)
print(f"\nSaved: {fp}")
print(f"Objects: {len(bpy.data.objects)}")
