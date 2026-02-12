"""
============================================================
  刀剑神域 SAO - Blender 3D模型自动构建脚本
  直接在 Blender Script Editor 中运行
  Blender 5.0+ 兼容
============================================================
构建内容 (P0优先级):
  ✦ TOON渲染环境 + 三点光照
  ✦ 全套赛璐璐材质库 (24种)
  ✦ 桐人 (身体+头发+黑色风衣+描边)
  ✦ 逐暗者 Elucidator (剑身+护手+握柄)
  ✦ 亚丝娜 (身体+长发编辫+KoB战斗装)
  ✦ 闪光 Lambent Light (细剑)
  ✦ 克莱因 (身体+头发+武士装)
  ✦ 武士刀
============================================================
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ============================================================
# 工具函数
# ============================================================

def link_to_collection(obj, col_name):
    col = bpy.data.collections.get(col_name)
    if col:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

def add_subsurface(obj, levels=2):
    mod = obj.modifiers.new('SubSurf', 'SUBSURF')
    mod.levels = levels
    mod.render_levels = levels
    return mod

def add_outline(obj, thickness=0.008):
    outline_mat = bpy.data.materials.get('SAO_Outline')
    mod = obj.modifiers.new('Outline', 'SOLIDIFY')
    mod.thickness = thickness
    mod.offset = -1
    mod.use_flip_normals = True
    mod.material_offset = len(obj.data.materials)
    if outline_mat:
        obj.data.materials.append(outline_mat)
    return mod

def smooth_shade(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)

def create_and_setup(prim_func, name, col_name, mat_name, location=None, scale=None, rotation=None, subsurface=0, outline=False):
    """统一创建+设置函数"""
    prim_func()
    obj = bpy.context.active_object
    obj.name = name
    if location:
        obj.location = location
    if scale:
        obj.scale = scale
        bpy.ops.object.transform_apply(scale=True)
    if rotation:
        obj.rotation_euler = rotation
    if subsurface > 0:
        add_subsurface(obj, subsurface)
    smooth_shade(obj)
    assign_material(obj, mat_name)
    link_to_collection(obj, col_name)
    if outline:
        add_outline(obj)
    return obj

# ============================================================
# Phase 1: 场景初始化
# ============================================================

def phase1_setup():
    print("[Phase 1] 场景初始化...")
    
    # 创建集合
    col_names = [
        'SAO_Characters', 'SAO_Weapons', 'SAO_Equipment',
        'SAO_Environments', 'SAO_Monsters', 'SAO_Props', 'SAO_Lighting'
    ]
    for name in col_names:
        if name not in bpy.data.collections:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
    
    # 渲染设置
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    
    # 三点光照
    lights = [
        ('SAO_KeyLight', 'SUN', (5,-5,10), (math.radians(45),math.radians(15),math.radians(30)), 3.0, (1.0,0.95,0.9)),
        ('SAO_FillLight', 'SUN', (-5,-3,5), (math.radians(60),math.radians(-30),math.radians(-20)), 1.0, (0.85,0.9,1.0)),
        ('SAO_RimLight', 'SUN', (0,5,8), (math.radians(-30),0,math.radians(180)), 1.5, (1.0,1.0,1.0)),
    ]
    for name, ltype, loc, rot, energy, color in lights:
        if name not in bpy.data.objects:
            bpy.ops.object.light_add(type=ltype, location=loc)
            lt = bpy.context.active_object
            lt.name = name
            lt.rotation_euler = rot
            lt.data.energy = energy
            lt.data.color = color
            link_to_collection(lt, 'SAO_Lighting')
    
    # 摄像机
    if 'SAO_Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(0, -10, 1.5))
        cam = bpy.context.active_object
        cam.name = 'SAO_Camera'
        cam.rotation_euler = (math.radians(85), 0, 0)
        cam.data.lens = 85
        scene.camera = cam
        link_to_collection(cam, 'SAO_Lighting')
    
    print("  ✓ 集合/渲染/光照/摄像机 完成")

# ============================================================
# Phase 2: 材质系统
# ============================================================

def create_toon_mat(name, base_rgb, shadow_mult=(0.6,0.55,0.65), ramp_pos=0.45):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (*base_rgb, 1.0)
    diffuse.location = (-200, 0)
    
    s2rgb = nodes.new('ShaderNodeShaderToRGB')
    s2rgb.location = (0, 0)
    links.new(diffuse.outputs['BSDF'], s2rgb.inputs['Shader'])
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    shadow = (base_rgb[0]*shadow_mult[0], base_rgb[1]*shadow_mult[1], base_rgb[2]*shadow_mult[2], 1.0)
    ramp.color_ramp.elements[0].color = shadow
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].color = (*base_rgb, 1.0)
    ramp.color_ramp.elements[1].position = ramp_pos
    links.new(s2rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])
    return mat

def phase2_materials():
    print("[Phase 2] 创建材质库...")
    
    # 描边材质
    if 'SAO_Outline' not in bpy.data.materials:
        om = bpy.data.materials.new('SAO_Outline')
        om.use_nodes = True
        om.use_backface_culling = True
        nodes = om.node_tree.nodes
        links = om.node_tree.links
        nodes.clear()
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (0,0,0,1)
        emission.inputs['Strength'].default_value = 0
        emission.location = (100, 0)
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    # 角色材质
    mats = {
        'SAO_Skin':              (0.95, 0.82, 0.73),
        'SAO_Skin_Dark':         (0.42, 0.26, 0.15),
        'SAO_Kirito_Black':      (0.04, 0.04, 0.04),
        'SAO_Kirito_Silver':     (0.75, 0.75, 0.75),
        'SAO_Kirito_Hair':       (0.04, 0.04, 0.06),
        'SAO_Asuna_White':       (0.96, 0.96, 0.96),
        'SAO_Asuna_Red':         (0.80, 0.20, 0.20),
        'SAO_Asuna_Gold':        (0.83, 0.69, 0.22),
        'SAO_Asuna_Hair':        (0.78, 0.46, 0.20),
        'SAO_Klein_Red':         (0.72, 0.26, 0.18),
        'SAO_Klein_Brown':       (0.29, 0.19, 0.13),
        'SAO_Klein_Hair':        (0.72, 0.26, 0.18),
        'SAO_Klein_Cream':       (0.91, 0.86, 0.78),
        'SAO_Liz_DarkRed':       (0.55, 0.13, 0.19),
        'SAO_Liz_Pink_Hair':     (0.91, 0.63, 0.69),
        'SAO_Sachi_Blue':        (0.17, 0.17, 0.43),
        'SAO_Sachi_Hair':        (0.10, 0.10, 0.31),
        'SAO_Metal_Silver':      (0.70, 0.70, 0.72),
        'SAO_Metal_Gold':        (0.83, 0.69, 0.22),
        'SAO_Metal_Dark':        (0.08, 0.08, 0.08),
        'SAO_Leather_Brown':     (0.29, 0.16, 0.08),
        'SAO_Fabric_White':      (0.92, 0.92, 0.90),
        'SAO_Eye_Black':         (0.02, 0.02, 0.02),
        'SAO_Elucidator_Blade':  (0.03, 0.03, 0.04),
        'SAO_DarkRepulser_Blade':(0.44, 0.75, 0.82),
        'SAO_LambentLight_Blade':(0.91, 0.91, 0.94),
    }
    
    for name, rgb in mats.items():
        create_toon_mat(name, rgb)
    
    # 眼睛高光 (自发光白)
    if 'SAO_Eye_Highlight' not in bpy.data.materials:
        ehl = bpy.data.materials.new('SAO_Eye_Highlight')
        ehl.use_nodes = True
        nodes = ehl.node_tree.nodes
        links = ehl.node_tree.links
        nodes.clear()
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (1,1,1,1)
        emission.inputs['Strength'].default_value = 2.0
        emission.location = (100, 0)
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    # 亚丝娜琥珀眼
    create_toon_mat('SAO_Asuna_Eye', (0.55, 0.41, 0.08))
    
    print(f"  ✓ {len(mats)+3} 种材质创建完成")

# ============================================================
# Phase 3: 桐人 (Kirito)
# ============================================================

def phase3_kirito():
    print("[Phase 3] 构建桐人...")
    C = 'SAO_Characters'
    
    # 躯干
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,1.1))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_Torso'
    obj.scale = (0.35, 0.2, 0.45); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 2); smooth_shade(obj)
    assign_material(obj, 'SAO_Kirito_Black'); link_to_collection(obj, C); add_outline(obj)
    
    # 头
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.22, location=(0,0,1.72))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_Head'
    obj.scale = (1.0, 0.9, 1.05); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C); add_outline(obj)
    
    # 颈
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=0.12, location=(0,0,1.53))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_Neck'
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 眼睛
    for side, x in [('L', 0.08), ('R', -0.08)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(x, -0.18, 1.74))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Eye_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Eye_Black'); link_to_collection(obj, C)
        # 高光
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(x+0.02, -0.22, 1.76))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_EyeHL_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Eye_Highlight'); link_to_collection(obj, C)
    
    # 手臂
    for side, x in [('L', 0.45), ('R', -0.45)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.55, location=(x, 0, 1.1))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Arm_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Kirito_Black'); link_to_collection(obj, C); add_outline(obj)
    
    # 手
    for side, x in [('L', 0.45), ('R', -0.45)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.06, location=(x, 0, 0.78))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Hand_{side}'
        obj.scale = (1.0, 0.7, 1.2); bpy.ops.object.transform_apply(scale=True)
        smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 腿
    for side, x in [('L', 0.13), ('R', -0.13)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.65, location=(x, 0, 0.33))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Leg_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Kirito_Black'); link_to_collection(obj, C); add_outline(obj)
    
    # 靴
    for side, x in [('L', 0.13), ('R', -0.13)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.02, 0.05))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Boot_{side}'
        obj.scale = (0.1, 0.15, 0.08); bpy.ops.object.transform_apply(scale=True)
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Kirito_Black'); link_to_collection(obj, C)
    
    # === 头发 ===
    # 基础球
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.25, location=(0, 0.02, 1.76))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_HairBase'
    obj.scale = (1.05, 1.0, 1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Hair'); link_to_collection(obj, C); add_outline(obj)
    
    # 刘海 (5束)
    bangs = [
        (-0.10,-0.20,1.82, 0.15,0.04, 15),
        (-0.04,-0.22,1.84, 0.14,0.035, 8),
        ( 0.03,-0.22,1.83, 0.16,0.04, -5),
        ( 0.09,-0.21,1.81, 0.13,0.035,-12),
        ( 0.00,-0.23,1.85, 0.12,0.03,  3),
    ]
    for i,(x,y,z,ln,w,rot) in enumerate(bangs):
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=w, radius2=0.005, depth=ln, location=(x,y,z))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Bang_{i}'
        obj.rotation_euler = (math.radians(70), 0, math.radians(rot))
        smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Hair'); link_to_collection(obj, C)
    
    # 侧发 (左右各3)
    sides = [
        (0.20,-0.05,1.72, 0.18,0.04, 0,-25),
        (0.22, 0.02,1.68, 0.20,0.035, 5,-30),
        (0.18,-0.10,1.75, 0.15,0.03,-5,-20),
    ]
    for mult in [1, -1]:
        sn = 'L' if mult>0 else 'R'
        for i,(x,y,z,ln,w,rz,rx) in enumerate(sides):
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=w, radius2=0.008, depth=ln, location=(x*mult,y,z))
            obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Side_{sn}_{i}'
            obj.rotation_euler = (math.radians(rx*mult*-1+90), 0, math.radians(rz*mult))
            smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Hair'); link_to_collection(obj, C)
    
    # 后发 (4束)
    backs = [
        (-0.08,0.18,1.70, 0.20,0.05,-10),
        ( 0.00,0.20,1.72, 0.22,0.05, 0),
        ( 0.08,0.18,1.70, 0.20,0.05, 10),
        ( 0.00,0.16,1.65, 0.18,0.04, 0),
    ]
    for i,(x,y,z,ln,w,rz) in enumerate(backs):
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=w, radius2=0.01, depth=ln, location=(x,y,z))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Back_{i}'
        obj.rotation_euler = (math.radians(110), 0, math.radians(rz))
        smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Hair'); link_to_collection(obj, C)
    
    # === 风衣 ===
    mesh = bpy.data.meshes.new('CHR_Kirito_CoatMesh')
    coat = bpy.data.objects.new('CHR_Kirito_Coat', mesh)
    bm = bmesh.new()
    vf = [bm.verts.new(v) for v in [(-0.38,-0.12,1.35),(0.38,-0.12,1.35),(0.50,-0.13,0.40),(-0.50,-0.13,0.40)]]
    vb = [bm.verts.new(v) for v in [(-0.38,0.12,1.35),(0.38,0.12,1.35),(0.50,0.13,0.40),(-0.50,0.13,0.40)]]
    bm.faces.new([vf[0],vf[1],vf[2],vf[3]])
    bm.faces.new([vb[1],vb[0],vb[3],vb[2]])
    bm.faces.new([vb[0],vf[0],vf[3],vb[3]])
    bm.faces.new([vf[1],vb[1],vb[2],vf[2]])
    bm.faces.new([vb[0],vb[1],vf[1],vf[0]])
    bm.to_mesh(mesh); bm.free()
    bpy.context.scene.collection.objects.link(coat)
    bpy.context.view_layer.objects.active = coat
    add_subsurface(coat, 2)
    mod2 = coat.modifiers.new('Solidify', 'SOLIDIFY')
    mod2.thickness = 0.02; mod2.offset = -1
    smooth_shade(coat); assign_material(coat, 'SAO_Kirito_Black')
    link_to_collection(coat, C); add_outline(coat)
    
    # 立领
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.08, location=(0,0,1.48))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_Collar'
    obj.scale = (1.2, 0.8, 1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Black'); link_to_collection(obj, C)
    
    # 腰带
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=0.06, location=(0,0,0.88))
    obj = bpy.context.active_object; obj.name = 'CHR_Kirito_Belt'
    obj.scale = (1.0, 0.6, 1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Leather_Brown'); link_to_collection(obj, C)
    
    # 肩扣
    for side, x in [('L',0.30),('R',-0.30)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025, location=(x,-0.10,1.32))
        obj = bpy.context.active_object; obj.name = f'CHR_Kirito_Buckle_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Kirito_Silver'); link_to_collection(obj, C)
    
    print("  ✓ 桐人完成 (身体+头发+风衣+描边)")

# ============================================================
# Phase 4: 逐暗者 (Elucidator)
# ============================================================

def phase4_elucidator():
    print("[Phase 4] 构建逐暗者...")
    W = 'SAO_Weapons'
    sx = 0.55  # 桐人右手侧
    
    # 剑身
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -0.15, 0.95))
    blade = bpy.context.active_object; blade.name = 'WPN_Elucidator_Blade'
    blade.scale = (0.015, 0.005, 0.42); bpy.ops.object.transform_apply(scale=True)
    # 剑尖
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(blade.data); bm.verts.ensure_lookup_table()
    mz = max(v.co.z for v in bm.verts)
    for v in bm.verts:
        if abs(v.co.z - mz) < 0.01: v.co.x *= 0.1; v.co.y *= 0.3
    bmesh.update_edit_mesh(blade.data); bpy.ops.object.mode_set(mode='OBJECT')
    add_subsurface(blade, 1); smooth_shade(blade)
    assign_material(blade, 'SAO_Elucidator_Blade'); link_to_collection(blade, W)
    
    # 血槽
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -0.15, 0.97))
    obj = bpy.context.active_object; obj.name = 'WPN_Elucidator_Fuller'
    obj.scale = (0.005, 0.002, 0.32); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Dark'); link_to_collection(obj, W)
    
    # 护手
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, -0.15, 0.53))
    obj = bpy.context.active_object; obj.name = 'WPN_Elucidator_Guard'
    obj.scale = (0.06, 0.015, 0.012); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 1); smooth_shade(obj)
    assign_material(obj, 'SAO_Metal_Dark'); link_to_collection(obj, W)
    
    # 护手球
    for dx in [0.06, -0.06]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.012, location=(sx+dx,-0.15,0.53))
        obj = bpy.context.active_object; obj.name = f'WPN_Eluc_GuardBall_{"L" if dx>0 else "R"}'
        smooth_shade(obj); assign_material(obj, 'SAO_Metal_Dark'); link_to_collection(obj, W)
    
    # 握柄
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=0.12, location=(sx,-0.15,0.46))
    obj = bpy.context.active_object; obj.name = 'WPN_Elucidator_Grip'
    smooth_shade(obj); assign_material(obj, 'SAO_Leather_Brown'); link_to_collection(obj, W)
    
    # 柄头
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(sx,-0.15,0.39))
    obj = bpy.context.active_object; obj.name = 'WPN_Elucidator_Pommel'
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Dark'); link_to_collection(obj, W)
    
    print("  ✓ 逐暗者完成 (剑身+护手+握柄+柄头)")

# ============================================================
# Phase 5: 亚丝娜 (Asuna)
# ============================================================

def phase5_asuna():
    print("[Phase 5] 构建亚丝娜...")
    C = 'SAO_Characters'
    ox = 1.5  # 位于桐人右侧
    
    # 躯干
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,0,1.05))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_Torso'
    obj.scale = (0.30, 0.18, 0.40); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 2); smooth_shade(obj)
    assign_material(obj, 'SAO_Asuna_White'); link_to_collection(obj, C); add_outline(obj)
    
    # 头
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.20, location=(ox,0,1.68))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_Head'
    obj.scale = (1.0, 0.88, 1.05); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C); add_outline(obj)
    
    # 颈
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=0.10, location=(ox,0,1.50))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_Neck'
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 眼睛 (琥珀色)
    for side, x in [('L',0.07),('R',-0.07)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(ox+x,-0.16,1.70))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Eye_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Eye'); link_to_collection(obj, C)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(ox+x+0.02,-0.20,1.72))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_EyeHL_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Eye_Highlight'); link_to_collection(obj, C)
    
    # 手臂
    for side, x in [('L',0.40),('R',-0.40)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.065, depth=0.50, location=(ox+x,0,1.05))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Arm_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Fabric_White'); link_to_collection(obj, C); add_outline(obj)
    
    # 手
    for side, x in [('L',0.40),('R',-0.40)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.05, location=(ox+x,0,0.75))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Hand_{side}'
        obj.scale = (1.0,0.7,1.2); bpy.ops.object.transform_apply(scale=True)
        smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 腿
    for side, x in [('L',0.11),('R',-0.11)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.075, depth=0.55, location=(ox+x,0,0.35))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Leg_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C); add_outline(obj)
    
    # 靴
    for side, x in [('L',0.11),('R',-0.11)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox+x,-0.02,0.06))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Boot_{side}'
        obj.scale = (0.08, 0.12, 0.08); bpy.ops.object.transform_apply(scale=True)
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Asuna_White'); link_to_collection(obj, C)
    
    # === 头发 ===
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.23, location=(ox,0.02,1.72))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_HairBase'
    smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Hair'); link_to_collection(obj, C); add_outline(obj)
    
    # 长发
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,0.10,1.30))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_LongHair'
    obj.scale = (0.20, 0.04, 0.55); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data); bm.verts.ensure_lookup_table()
    mz = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        if abs(v.co.z - mz) < 0.01: v.co.x *= 1.3
    bmesh.update_edit_mesh(obj.data); bpy.ops.object.mode_set(mode='OBJECT')
    add_subsurface(obj, 2); smooth_shade(obj)
    assign_material(obj, 'SAO_Asuna_Hair'); link_to_collection(obj, C)
    
    # 刘海
    a_bangs = [(-0.08,-0.18,1.78,0.12,0.035,12),(-0.02,-0.20,1.80,0.11,0.03,5),(0.04,-0.19,1.79,0.13,0.035,-3),(0.10,-0.17,1.77,0.11,0.03,-10)]
    for i,(x,y,z,ln,w,rot) in enumerate(a_bangs):
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=w, radius2=0.005, depth=ln, location=(ox+x,y,z))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Bang_{i}'
        obj.rotation_euler = (math.radians(70),0,math.radians(rot))
        smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Hair'); link_to_collection(obj, C)
    
    # 编辫
    for side, sx in [('L',0.15),('R',-0.15)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.50, location=(ox+sx,-0.08,1.35))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Braid_{side}'
        obj.rotation_euler = (math.radians(10),0,math.radians(5 if side=='L' else -5))
        mod = obj.modifiers.new('Twist','SIMPLE_DEFORM')
        mod.deform_method = 'TWIST'; mod.angle = math.radians(360)
        smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Hair'); link_to_collection(obj, C)
    
    # 发箍
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.012, location=(ox,0,1.82))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_Headband'
    obj.scale = (1.0,0.9,0.3); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Fabric_White'); link_to_collection(obj, C)
    
    # === KoB战斗装 ===
    # 胸甲
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,-0.05,1.12))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_ChestArmor'
    obj.scale = (0.32,0.10,0.25); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 2); smooth_shade(obj)
    assign_material(obj, 'SAO_Asuna_White'); link_to_collection(obj, C)
    
    # 红色十字
    for dim, nm in [((0.08,0.005,0.02),'H'),((0.02,0.005,0.08),'V')]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,-0.16,1.12))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Cross_{nm}'
        obj.scale = dim; bpy.ops.object.transform_apply(scale=True)
        assign_material(obj, 'SAO_Asuna_Red'); link_to_collection(obj, C)
    
    # 肩甲
    for side, x in [('L',0.32),('R',-0.32)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.06, location=(ox+x,0,1.28))
        obj = bpy.context.active_object; obj.name = f'CHR_Asuna_Shoulder_{side}'
        obj.scale = (1.0,0.7,0.5); bpy.ops.object.transform_apply(scale=True)
        smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Red'); link_to_collection(obj, C)
    
    # 裙子
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.28, radius2=0.16, depth=0.25, location=(ox,0,0.72))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_SkirtOuter'
    smooth_shade(obj); assign_material(obj, 'SAO_Asuna_Red'); link_to_collection(obj, C)
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.26, radius2=0.15, depth=0.22, location=(ox,0,0.73))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_SkirtInner'
    smooth_shade(obj); assign_material(obj, 'SAO_Fabric_White'); link_to_collection(obj, C)
    
    # 腰带
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.16, depth=0.04, location=(ox,0,0.86))
    obj = bpy.context.active_object; obj.name = 'CHR_Asuna_Belt'
    obj.scale = (1.0,0.65,1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Asuna_White'); link_to_collection(obj, C)
    
    print("  ✓ 亚丝娜完成 (身体+长发编辫+KoB战斗装)")

# ============================================================
# Phase 6: 闪光 (Lambent Light)
# ============================================================

def phase6_lambent_light():
    print("[Phase 6] 构建闪光细剑...")
    W = 'SAO_Weapons'
    ox = 1.95  # 亚丝娜右手
    
    # 剑身
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.005, depth=0.75, location=(ox,-0.12,1.10))
    blade = bpy.context.active_object; blade.name = 'WPN_LambentLight_Blade'
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(blade.data); bm.verts.ensure_lookup_table()
    mz = max(v.co.z for v in bm.verts)
    for v in bm.verts:
        if abs(v.co.z - mz) < 0.01: v.co.x *= 0.05; v.co.y *= 0.05
    bmesh.update_edit_mesh(blade.data); bpy.ops.object.mode_set(mode='OBJECT')
    smooth_shade(blade); assign_material(blade, 'SAO_LambentLight_Blade'); link_to_collection(blade, W)
    
    # 护手环
    bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.005, location=(ox,-0.12,0.72))
    obj = bpy.context.active_object; obj.name = 'WPN_LL_GuardRing'
    obj.rotation_euler = (math.radians(90),0,0)
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Silver'); link_to_collection(obj, W)
    
    # 护手横条
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.004, depth=0.08, location=(ox,-0.12,0.72))
    obj = bpy.context.active_object; obj.name = 'WPN_LL_GuardBar'
    obj.rotation_euler = (0,math.radians(90),0)
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Silver'); link_to_collection(obj, W)
    
    # 握柄
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.010, depth=0.10, location=(ox,-0.12,0.66))
    obj = bpy.context.active_object; obj.name = 'WPN_LL_Grip'
    smooth_shade(obj); assign_material(obj, 'SAO_Fabric_White'); link_to_collection(obj, W)
    
    # 柄头
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.012, location=(ox,-0.12,0.60))
    obj = bpy.context.active_object; obj.name = 'WPN_LL_Pommel'
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Silver'); link_to_collection(obj, W)
    
    print("  ✓ 闪光完成 (细剑剑身+护手篮+握柄)")

# ============================================================
# Phase 7: 克莱因 (Klein)
# ============================================================

def phase7_klein():
    print("[Phase 7] 构建克莱因...")
    C = 'SAO_Characters'
    W = 'SAO_Weapons'
    ox = -1.5  # 桐人左侧
    
    # 躯干
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,0,1.1))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_Torso'
    obj.scale = (0.38, 0.22, 0.45); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 2); smooth_shade(obj)
    assign_material(obj, 'SAO_Klein_Red'); link_to_collection(obj, C); add_outline(obj)
    
    # 头
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.22, location=(ox,0,1.72))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_Head'
    obj.scale = (1.0, 0.92, 1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C); add_outline(obj)
    
    # 颈
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.07, depth=0.12, location=(ox,0,1.53))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_Neck'
    smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 眼
    for side, x in [('L',0.08),('R',-0.08)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.035, location=(ox+x,-0.18,1.74))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Eye_{side}'
        obj.scale = (1.2, 1.0, 0.7); bpy.ops.object.transform_apply(scale=True)
        smooth_shade(obj); assign_material(obj, 'SAO_Eye_Black'); link_to_collection(obj, C)
    
    # 手臂
    for side, x in [('L',0.48),('R',-0.48)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.55, location=(ox+x,0,1.1))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Arm_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Klein_Red'); link_to_collection(obj, C); add_outline(obj)
    
    # 手
    for side, x in [('L',0.48),('R',-0.48)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.065, location=(ox+x,0,0.78))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Hand_{side}'
        smooth_shade(obj); assign_material(obj, 'SAO_Skin'); link_to_collection(obj, C)
    
    # 腿(袴裤)
    for side, x in [('L',0.14),('R',-0.14)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.11, depth=0.65, location=(ox+x,0,0.33))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Leg_{side}'
        add_subsurface(obj, 1); smooth_shade(obj)
        assign_material(obj, 'SAO_Klein_Cream'); link_to_collection(obj, C); add_outline(obj)
    
    # 凉鞋
    for side, x in [('L',0.14),('R',-0.14)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox+x,-0.02,0.04))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Sandal_{side}'
        obj.scale = (0.10, 0.14, 0.04); bpy.ops.object.transform_apply(scale=True)
        smooth_shade(obj); assign_material(obj, 'SAO_Leather_Brown'); link_to_collection(obj, C)
    
    # === 头发(刺猬式) ===
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.24, location=(ox,0.02,1.78))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_HairBase'
    smooth_shade(obj); assign_material(obj, 'SAO_Klein_Hair'); link_to_collection(obj, C); add_outline(obj)
    
    spikes = [
        (0.00,-0.10,1.95, 0.18,0.05, 50, 0),
        (-0.10,-0.05,1.98, 0.16,0.04, 40,-15),
        (0.10,-0.05,1.98, 0.16,0.04, 40, 15),
        (-0.15,0.05,1.95, 0.14,0.04, 20,-30),
        (0.15,0.05,1.95, 0.14,0.04, 20, 30),
        (0.00,0.15,1.92, 0.15,0.04, -10, 0),
        (-0.12,0.12,1.93, 0.13,0.035,-5,-20),
        (0.12,0.12,1.93, 0.13,0.035,-5, 20),
    ]
    for i,(x,y,z,ln,w,rx,rz) in enumerate(spikes):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=w, radius2=0.005, depth=ln, location=(ox+x,y,z))
        obj = bpy.context.active_object; obj.name = f'CHR_Klein_Spike_{i}'
        obj.rotation_euler = (math.radians(rx),0,math.radians(rz))
        smooth_shade(obj); assign_material(obj, 'SAO_Klein_Hair'); link_to_collection(obj, C)
    
    # 头带
    bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.015, location=(ox,0,1.80))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_Headband'
    obj.scale = (1.0,0.9,0.3); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Klein_Red'); link_to_collection(obj, C)
    
    # 护胸甲
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,-0.05,1.12))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_ChestArmor'
    obj.scale = (0.34,0.08,0.22); bpy.ops.object.transform_apply(scale=True)
    add_subsurface(obj, 1); smooth_shade(obj)
    assign_material(obj, 'SAO_Klein_Brown'); link_to_collection(obj, C)
    
    # 腰带
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.19, depth=0.06, location=(ox,0,0.88))
    obj = bpy.context.active_object; obj.name = 'CHR_Klein_Belt'
    obj.scale = (1.0,0.6,1.0); bpy.ops.object.transform_apply(scale=True)
    smooth_shade(obj); assign_material(obj, 'SAO_Leather_Brown'); link_to_collection(obj, C)
    
    # === 武士刀 ===
    # 刀身
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ox-0.25,-0.10,0.95))
    blade = bpy.context.active_object; blade.name = 'WPN_Klein_Katana_Blade'
    blade.scale = (0.012, 0.004, 0.40); bpy.ops.object.transform_apply(scale=True)
    blade.rotation_euler = (0,0,math.radians(-5))
    add_subsurface(blade, 1); smooth_shade(blade)
    assign_material(blade, 'SAO_Metal_Silver'); link_to_collection(blade, W)
    
    # 刀镡
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.025, depth=0.005, location=(ox-0.25,-0.10,0.55))
    obj = bpy.context.active_object; obj.name = 'WPN_Klein_Katana_Tsuba'
    smooth_shade(obj); assign_material(obj, 'SAO_Metal_Dark'); link_to_collection(obj, W)
    
    # 柄
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=0.15, location=(ox-0.25,-0.10,0.47))
    obj = bpy.context.active_object; obj.name = 'WPN_Klein_Katana_Handle'
    smooth_shade(obj); assign_material(obj, 'SAO_Klein_Red'); link_to_collection(obj, W)
    
    print("  ✓ 克莱因完成 (身体+刺猬发+武士装+武士刀)")

# ============================================================
# 主执行
# ============================================================

print("\n" + "="*60)
print("  刀剑神域 SAO - 3D模型自动构建")
print("  Sword Art Online - Auto Builder")
print("="*60)

phase1_setup()
phase2_materials()
phase3_kirito()
phase4_elucidator()
phase5_asuna()
phase6_lambent_light()
phase7_klein()

# 取消所有选择
bpy.ops.object.select_all(action='DESELECT')

print("\n" + "="*60)
print("  构建完成!")
print("="*60)
print("  ✓ TOON渲染环境 + 三点光照 + 摄像机")
print("  ✓ 28种SAO赛璐璐材质")
print("  ✓ 桐人 (身体+黑发+风衣+描边)")
print("  ✓ 逐暗者 Elucidator (黑色长剑)")
print("  ✓ 亚丝娜 (身体+栗发编辫+KoB白红战斗装)")
print("  ✓ 闪光 Lambent Light (银色细剑)")
print("  ✓ 克莱因 (身体+红发+武士装+武士刀)")
print("="*60)
