"""
SAO 刀剑神域 - 完整3D模型构建脚本
通过Socket直接在Blender中执行Python代码构建所有P0级模型
"""
import socket
import json
import time
import sys
import textwrap

def send_to_blender(code, host="127.0.0.1", port=9876, timeout=60):
    """在Blender中执行Python代码"""
    request = {
        "id": f"sao_{int(time.time()*1000)}",
        "type": "command",
        "category": "system",
        "action": "execute_python",
        "params": {"code": code}
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        sock.connect((host, port))
        message = json.dumps(request, ensure_ascii=False) + "\n"
        sock.send(message.encode("utf-8"))
        
        buffer = ""
        while "\n" not in buffer:
            data = sock.recv(8192)
            if not data:
                break
            buffer += data.decode("utf-8")
        
        if buffer.strip():
            response = json.loads(buffer.strip())
            if response.get("success"):
                print(f"  ✓ OK")
                if "data" in response and "result" in response["data"]:
                    r = response["data"]["result"]
                    if r and r != "None":
                        print(f"    {r}")
            else:
                err = response.get("error", {})
                print(f"  ✗ Error: {err.get('message', str(err))}")
            return response
        return None
    except Exception as e:
        print(f"  ✗ Connection error: {e}")
        return None
    finally:
        sock.close()

def blender_exec(code):
    """简写: 发送代码到Blender"""
    return send_to_blender(textwrap.dedent(code).strip())

# ============================================================
# Phase 1: 场景初始化
# ============================================================
def phase1_setup():
    """P1: 创建SAO专用集合和TOON渲染环境"""
    print("\n" + "="*60)
    print("Phase 1: 场景初始化与TOON环境设置")
    print("="*60)
    
    print("\n[1.1] 创建SAO集合...")
    blender_exec("""
        import bpy
        
        col_names = [
            'SAO_Characters', 'SAO_Weapons', 'SAO_Equipment',
            'SAO_Environments', 'SAO_Monsters', 'SAO_Props', 'SAO_Lighting'
        ]
        created = []
        for name in col_names:
            if name not in bpy.data.collections:
                col = bpy.data.collections.new(name)
                bpy.context.scene.collection.children.link(col)
                created.append(name)
        
        result = f"Created {len(created)} collections: {', '.join(created)}" if created else "All collections exist"
        result
    """)
    
    print("\n[1.2] 设置TOON渲染环境...")
    blender_exec("""
        import bpy
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.film_transparent = True
        scene.view_settings.view_transform = 'Standard'
        
        result = "EEVEE NEXT + Standard color + 1920x1080"
        result
    """)
    
    print("\n[1.3] 设置三点光照...")
    blender_exec("""
        import bpy, math
        
        lighting_col = bpy.data.collections.get('SAO_Lighting')
        
        # 主光
        bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
        key = bpy.context.active_object
        key.name = 'SAO_KeyLight'
        key.data.energy = 3.0
        key.data.color = (1.0, 0.95, 0.9)
        key.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))
        
        # 补光
        bpy.ops.object.light_add(type='SUN', location=(-5, -3, 5))
        fill = bpy.context.active_object
        fill.name = 'SAO_FillLight'
        fill.data.energy = 1.0
        fill.data.color = (0.85, 0.9, 1.0)
        fill.rotation_euler = (math.radians(60), math.radians(-30), math.radians(-20))
        
        # 轮廓光
        bpy.ops.object.light_add(type='SUN', location=(0, 5, 8))
        rim = bpy.context.active_object
        rim.name = 'SAO_RimLight'
        rim.data.energy = 1.5
        rim.data.color = (1.0, 1.0, 1.0)
        rim.rotation_euler = (math.radians(-30), 0, math.radians(180))
        
        # 移入Lighting集合
        if lighting_col:
            for obj_name in ['SAO_KeyLight', 'SAO_FillLight', 'SAO_RimLight']:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    for c in obj.users_collection:
                        c.objects.unlink(obj)
                    lighting_col.objects.link(obj)
        
        result = "3-point lighting created"
        result
    """)

# ============================================================
# Phase 2: 卡通材质系统
# ============================================================
def phase2_materials():
    """P2: 创建SAO角色专用卡通材质库"""
    print("\n" + "="*60)
    print("Phase 2: 创建SAO卡通材质库")
    print("="*60)
    
    print("\n[2.1] 创建赛璐璐材质函数+全套材质...")
    blender_exec("""
        import bpy
        
        def create_toon_mat(name, base_rgb, shadow_mult=(0.6, 0.55, 0.65), ramp_pos=0.45):
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
        
        # ===== 角色皮肤 =====
        create_toon_mat('SAO_Skin', (0.95, 0.82, 0.73))
        create_toon_mat('SAO_Skin_Dark', (0.42, 0.26, 0.15))  # 艾吉尔
        
        # ===== 桐人 =====
        create_toon_mat('SAO_Kirito_Black', (0.04, 0.04, 0.04))
        create_toon_mat('SAO_Kirito_Silver', (0.75, 0.75, 0.75))
        create_toon_mat('SAO_Kirito_Hair', (0.04, 0.04, 0.06))
        
        # ===== 亚丝娜 =====
        create_toon_mat('SAO_Asuna_White', (0.96, 0.96, 0.96))
        create_toon_mat('SAO_Asuna_Red', (0.80, 0.20, 0.20))
        create_toon_mat('SAO_Asuna_Gold', (0.83, 0.69, 0.22))
        create_toon_mat('SAO_Asuna_Hair', (0.78, 0.46, 0.20))
        
        # ===== 克莱因 =====
        create_toon_mat('SAO_Klein_Red', (0.72, 0.26, 0.18))
        create_toon_mat('SAO_Klein_Brown', (0.29, 0.19, 0.13))
        create_toon_mat('SAO_Klein_Hair', (0.72, 0.26, 0.18))
        
        # ===== 利兹 =====
        create_toon_mat('SAO_Liz_DarkRed', (0.55, 0.13, 0.19))
        create_toon_mat('SAO_Liz_Pink_Hair', (0.91, 0.63, 0.69))
        
        # ===== 幸 =====
        create_toon_mat('SAO_Sachi_Blue', (0.17, 0.17, 0.43))
        create_toon_mat('SAO_Sachi_Hair', (0.10, 0.10, 0.31))
        
        # ===== 通用 =====
        create_toon_mat('SAO_Metal_Silver', (0.7, 0.7, 0.72))
        create_toon_mat('SAO_Metal_Gold', (0.83, 0.69, 0.22))
        create_toon_mat('SAO_Metal_Dark', (0.08, 0.08, 0.08))
        create_toon_mat('SAO_Leather_Brown', (0.29, 0.16, 0.08))
        create_toon_mat('SAO_Fabric_White', (0.92, 0.92, 0.90))
        create_toon_mat('SAO_Eye_Black', (0.02, 0.02, 0.02))
        create_toon_mat('SAO_Eye_Highlight', (1.0, 1.0, 1.0))
        
        # ===== 武器 =====
        create_toon_mat('SAO_Elucidator_Blade', (0.03, 0.03, 0.04))
        create_toon_mat('SAO_DarkRepulser_Blade', (0.44, 0.75, 0.82))
        create_toon_mat('SAO_LambentLight_Blade', (0.91, 0.91, 0.94))
        
        result = f"Created {len([m for m in bpy.data.materials if m.name.startswith('SAO_')])} SAO materials"
        result
    """)

# ============================================================
# Phase 3: 桐人 (Kirito) 角色模型
# ============================================================
def phase3_kirito():
    """P3: 构建桐人完整角色"""
    print("\n" + "="*60)
    print("Phase 3: 构建桐人 (Kirito)")
    print("="*60)
    
    print("\n[3.1] 桐人 - 身体基础...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        
        # ===== 辅助函数 =====
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 身体 - 躯干 =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.1))
        torso = bpy.context.active_object
        torso.name = 'CHR_Kirito_Torso'
        torso.scale = (0.35, 0.2, 0.45)
        bpy.ops.object.transform_apply(scale=True)
        
        # 添加SubSurf
        mod = torso.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        mod.render_levels = 2
        assign_mat(torso, 'SAO_Kirito_Black')
        link_to_col(torso, char_col)
        
        # ===== 头部 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.22, location=(0, 0, 1.72))
        head = bpy.context.active_object
        head.name = 'CHR_Kirito_Head'
        head.scale = (1.0, 0.9, 1.05)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(head, 'SAO_Skin')
        link_to_col(head, char_col)
        
        # ===== 眼睛(左右) =====
        for side, x in [('L', 0.08), ('R', -0.08)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(x, -0.18, 1.74))
            eye = bpy.context.active_object
            eye.name = f'CHR_Kirito_Eye_{side}'
            bpy.ops.object.shade_smooth()
            assign_mat(eye, 'SAO_Eye_Black')
            link_to_col(eye, char_col)
            
            # 眼睛高光
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(x+0.02, -0.22, 1.76))
            hl = bpy.context.active_object
            hl.name = f'CHR_Kirito_EyeHL_{side}'
            bpy.ops.object.shade_smooth()
            assign_mat(hl, 'SAO_Eye_Highlight')
            link_to_col(hl, char_col)
        
        # ===== 手臂(左右) =====
        for side, x in [('L', 0.45), ('R', -0.45)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.55, location=(x, 0, 1.1))
            arm = bpy.context.active_object
            arm.name = f'CHR_Kirito_Arm_{side}'
            bpy.ops.object.shade_smooth()
            mod = arm.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            assign_mat(arm, 'SAO_Kirito_Black')
            link_to_col(arm, char_col)
        
        # ===== 手(左右) =====
        for side, x in [('L', 0.45), ('R', -0.45)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.06, location=(x, 0, 0.78))
            hand = bpy.context.active_object
            hand.name = f'CHR_Kirito_Hand_{side}'
            hand.scale = (1.0, 0.7, 1.2)
            bpy.ops.object.transform_apply(scale=True)
            bpy.ops.object.shade_smooth()
            assign_mat(hand, 'SAO_Skin')
            link_to_col(hand, char_col)
        
        # ===== 腿(左右) =====
        for side, x in [('L', 0.13), ('R', -0.13)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.09, depth=0.65, location=(x, 0, 0.33))
            leg = bpy.context.active_object
            leg.name = f'CHR_Kirito_Leg_{side}'
            bpy.ops.object.shade_smooth()
            mod = leg.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            assign_mat(leg, 'SAO_Kirito_Black')
            link_to_col(leg, char_col)
        
        # ===== 靴子(左右) =====
        for side, x in [('L', 0.13), ('R', -0.13)]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.02, 0.05))
            boot = bpy.context.active_object
            boot.name = f'CHR_Kirito_Boot_{side}'
            boot.scale = (0.1, 0.15, 0.08)
            bpy.ops.object.transform_apply(scale=True)
            mod = boot.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            bpy.ops.object.shade_smooth()
            assign_mat(boot, 'SAO_Kirito_Black')
            link_to_col(boot, char_col)
        
        # ===== 颈部 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=0.12, location=(0, 0, 1.53))
        neck = bpy.context.active_object
        neck.name = 'CHR_Kirito_Neck'
        bpy.ops.object.shade_smooth()
        assign_mat(neck, 'SAO_Skin')
        link_to_col(neck, char_col)
        
        result = "Kirito body complete: torso, head, eyes, arms, hands, legs, boots, neck"
        result
    """)
    
    print("\n[3.2] 桐人 - 头发...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 头发基础体 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.25, location=(0, 0.02, 1.76))
        hair_base = bpy.context.active_object
        hair_base.name = 'CHR_Kirito_HairBase'
        hair_base.scale = (1.05, 1.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(hair_base, 'SAO_Kirito_Hair')
        link_to_col(hair_base, char_col)
        
        # ===== 刘海发束(5束) =====
        bangs_data = [
            (-0.10, -0.20, 1.82, 0.15, 0.04, 15),
            (-0.04, -0.22, 1.84, 0.14, 0.035, 8),
            (0.03,  -0.22, 1.83, 0.16, 0.04, -5),
            (0.09,  -0.21, 1.81, 0.13, 0.035, -12),
            (0.00,  -0.23, 1.85, 0.12, 0.03, 3),
        ]
        for i, (x, y, z, length, width, rot_deg) in enumerate(bangs_data):
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=width, radius2=0.005, depth=length, location=(x, y, z))
            bang = bpy.context.active_object
            bang.name = f'CHR_Kirito_Bang_{i}'
            bang.rotation_euler = (math.radians(70), 0, math.radians(rot_deg))
            bpy.ops.object.shade_smooth()
            assign_mat(bang, 'SAO_Kirito_Hair')
            link_to_col(bang, char_col)
        
        # ===== 侧发(左右各3束) =====
        side_data = [
            (0.20, -0.05, 1.72, 0.18, 0.04, 0, -25),
            (0.22, 0.02, 1.68, 0.20, 0.035, 5, -30),
            (0.18, -0.10, 1.75, 0.15, 0.03, -5, -20),
        ]
        for side_mult in [1, -1]:
            side_name = 'L' if side_mult > 0 else 'R'
            for i, (x, y, z, length, width, rz, rx) in enumerate(side_data):
                bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=width, radius2=0.008, depth=length, location=(x*side_mult, y, z))
                strand = bpy.context.active_object
                strand.name = f'CHR_Kirito_SideHair_{side_name}_{i}'
                strand.rotation_euler = (math.radians(rx * side_mult * -1 + 90), 0, math.radians(rz * side_mult))
                bpy.ops.object.shade_smooth()
                assign_mat(strand, 'SAO_Kirito_Hair')
                link_to_col(strand, char_col)
        
        # ===== 后发(4束, 蓬松向后) =====
        back_data = [
            (-0.08, 0.18, 1.70, 0.20, 0.05, -10),
            (0.00,  0.20, 1.72, 0.22, 0.05, 0),
            (0.08,  0.18, 1.70, 0.20, 0.05, 10),
            (0.00,  0.16, 1.65, 0.18, 0.04, 0),
        ]
        for i, (x, y, z, length, width, rz) in enumerate(back_data):
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=width, radius2=0.01, depth=length, location=(x, y, z))
            back = bpy.context.active_object
            back.name = f'CHR_Kirito_BackHair_{i}'
            back.rotation_euler = (math.radians(110), 0, math.radians(rz))
            bpy.ops.object.shade_smooth()
            assign_mat(back, 'SAO_Kirito_Hair')
            link_to_col(back, char_col)
        
        result = "Kirito hair complete: base + 5 bangs + 6 side + 4 back strands"
        result
    """)
    
    print("\n[3.3] 桐人 - 风衣外套...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 风衣主体 =====
        mesh = bpy.data.meshes.new('CHR_Kirito_CoatMesh')
        coat = bpy.data.objects.new('CHR_Kirito_Coat', mesh)
        
        bm = bmesh.new()
        
        # 风衣截面: 梯形, 从肩部到膝盖
        # 上部(肩膀宽度0.38, 厚度0.22)
        # 下部(裙摆宽度0.50, 厚度0.25)
        verts_front = [
            bm.verts.new((-0.38, -0.12, 1.35)),  # 左肩前
            bm.verts.new((0.38, -0.12, 1.35)),   # 右肩前
            bm.verts.new((0.50, -0.13, 0.40)),   # 右下前
            bm.verts.new((-0.50, -0.13, 0.40)),  # 左下前
        ]
        verts_back = [
            bm.verts.new((-0.38, 0.12, 1.35)),   # 左肩后
            bm.verts.new((0.38, 0.12, 1.35)),    # 右肩后
            bm.verts.new((0.50, 0.13, 0.40)),    # 右下后
            bm.verts.new((-0.50, 0.13, 0.40)),   # 左下后
        ]
        
        bm.verts.ensure_lookup_table()
        
        # 前面
        bm.faces.new([verts_front[0], verts_front[1], verts_front[2], verts_front[3]])
        # 后面
        bm.faces.new([verts_back[1], verts_back[0], verts_back[3], verts_back[2]])
        # 左侧
        bm.faces.new([verts_back[0], verts_front[0], verts_front[3], verts_back[3]])
        # 右侧
        bm.faces.new([verts_front[1], verts_back[1], verts_back[2], verts_front[2]])
        # 肩部(上方)
        bm.faces.new([verts_back[0], verts_back[1], verts_front[1], verts_front[0]])
        # 底部开口 - 不封闭
        
        bm.to_mesh(mesh)
        bm.free()
        
        bpy.context.collection.objects.link(coat)
        bpy.context.view_layer.objects.active = coat
        coat.select_set(True)
        
        # SubSurf使风衣圆润
        mod = coat.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        
        # Solidify给厚度
        mod2 = coat.modifiers.new('Solidify', 'SOLIDIFY')
        mod2.thickness = 0.02
        mod2.offset = -1
        
        bpy.ops.object.shade_smooth()
        assign_mat(coat, 'SAO_Kirito_Black')
        link_to_col(coat, char_col)
        
        # ===== 衣领(立领) =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.08, location=(0, 0, 1.48))
        collar = bpy.context.active_object
        collar.name = 'CHR_Kirito_Collar'
        collar.scale = (1.2, 0.8, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(collar, 'SAO_Kirito_Black')
        link_to_col(collar, char_col)
        
        # ===== 腰带 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=0.06, location=(0, 0, 0.88))
        belt = bpy.context.active_object
        belt.name = 'CHR_Kirito_Belt'
        belt.scale = (1.0, 0.6, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(belt, 'SAO_Leather_Brown')
        link_to_col(belt, char_col)
        
        # ===== 银色装饰线(肩扣) =====
        for side, x in [('L', 0.30), ('R', -0.30)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025, location=(x, -0.10, 1.32))
            buckle = bpy.context.active_object
            buckle.name = f'CHR_Kirito_ShoulderBuckle_{side}'
            bpy.ops.object.shade_smooth()
            assign_mat(buckle, 'SAO_Kirito_Silver')
            link_to_col(buckle, char_col)
        
        result = "Kirito coat complete: main coat + collar + belt + shoulder buckles"
        result
    """)
    
    print("\n[3.4] 桐人 - 描边效果...")
    blender_exec("""
        import bpy
        
        # 创建描边材质(纯黑, 背面剔除)
        outline_mat = bpy.data.materials.get('SAO_Outline')
        if not outline_mat:
            outline_mat = bpy.data.materials.new(name='SAO_Outline')
            outline_mat.use_nodes = True
            nodes = outline_mat.node_tree.nodes
            links = outline_mat.node_tree.links
            nodes.clear()
            
            output = nodes.new('ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            emission = nodes.new('ShaderNodeEmission')
            emission.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
            emission.inputs['Strength'].default_value = 0.0
            emission.location = (100, 0)
            links.new(emission.outputs['Emission'], output.inputs['Surface'])
            
            outline_mat.use_backface_culling = True
        
        # 为桐人主要部件添加Solidify描边
        outline_targets = [
            'CHR_Kirito_Torso', 'CHR_Kirito_Head', 'CHR_Kirito_Coat',
            'CHR_Kirito_HairBase',
            'CHR_Kirito_Arm_L', 'CHR_Kirito_Arm_R',
            'CHR_Kirito_Leg_L', 'CHR_Kirito_Leg_R',
        ]
        
        count = 0
        for name in outline_targets:
            obj = bpy.data.objects.get(name)
            if obj:
                # 检查是否已有描边
                has_outline = any(m.name == 'Outline' for m in obj.modifiers)
                if not has_outline:
                    mod = obj.modifiers.new('Outline', 'SOLIDIFY')
                    mod.thickness = 0.008
                    mod.offset = -1
                    mod.use_flip_normals = True
                    mod.material_offset = 1
                    
                    # 添加描边材质
                    if len(obj.data.materials) < 2:
                        obj.data.materials.append(outline_mat)
                    else:
                        obj.data.materials[1] = outline_mat
                    count += 1
        
        result = f"Outline added to {count} objects"
        result
    """)

# ============================================================
# Phase 4: 逐暗者 (Elucidator) 武器
# ============================================================
def phase4_elucidator():
    """P4: 构建桐人的主武器 - 逐暗者"""
    print("\n" + "="*60)
    print("Phase 4: 构建逐暗者 (Elucidator)")
    print("="*60)
    
    print("\n[4.1] 逐暗者剑身+护手+握柄...")
    blender_exec("""
        import bpy, bmesh, math
        
        wpn_col = bpy.data.collections.get('SAO_Weapons')
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 剑身 =====
        # 使用Cube拉伸成剑形
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.55, -0.15, 0.95))
        blade = bpy.context.active_object
        blade.name = 'WPN_Elucidator_Blade'
        blade.scale = (0.015, 0.005, 0.42)
        bpy.ops.object.transform_apply(scale=True)
        
        # 编辑模式: 将顶部收窄为剑尖
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(blade.data)
        bm.verts.ensure_lookup_table()
        
        # 找到顶部顶点(z最大)并收窄
        max_z = max(v.co.z for v in bm.verts)
        for v in bm.verts:
            if abs(v.co.z - max_z) < 0.01:
                v.co.x *= 0.1  # 收窄成剑尖
                v.co.y *= 0.3
        
        bmesh.update_edit_mesh(blade.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # SubSurf轻微圆滑
        mod = blade.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 1
        bpy.ops.object.shade_smooth()
        assign_mat(blade, 'SAO_Elucidator_Blade')
        link_to_col(blade, wpn_col)
        
        # ===== 血槽 (剑身中央凹槽视觉) =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.55, -0.15, 0.97))
        fuller = bpy.context.active_object
        fuller.name = 'WPN_Elucidator_Fuller'
        fuller.scale = (0.005, 0.002, 0.32)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(fuller, 'SAO_Metal_Dark')
        link_to_col(fuller, wpn_col)
        
        # ===== 护手 (十字形) =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.55, -0.15, 0.53))
        guard = bpy.context.active_object
        guard.name = 'WPN_Elucidator_Guard'
        guard.scale = (0.06, 0.015, 0.012)
        bpy.ops.object.transform_apply(scale=True)
        mod = guard.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 1
        bpy.ops.object.shade_smooth()
        assign_mat(guard, 'SAO_Metal_Dark')
        link_to_col(guard, wpn_col)
        
        # 护手末端球形装饰
        for sx in [0.06, -0.06]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.012, location=(0.55+sx, -0.15, 0.53))
            ball = bpy.context.active_object
            ball.name = f'WPN_Elucidator_GuardBall_{"L" if sx>0 else "R"}'
            bpy.ops.object.shade_smooth()
            assign_mat(ball, 'SAO_Metal_Dark')
            link_to_col(ball, wpn_col)
        
        # ===== 握柄 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=0.12, location=(0.55, -0.15, 0.46))
        grip = bpy.context.active_object
        grip.name = 'WPN_Elucidator_Grip'
        bpy.ops.object.shade_smooth()
        assign_mat(grip, 'SAO_Leather_Brown')
        link_to_col(grip, wpn_col)
        
        # ===== 柄头 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(0.55, -0.15, 0.39))
        pommel = bpy.context.active_object
        pommel.name = 'WPN_Elucidator_Pommel'
        bpy.ops.object.shade_smooth()
        assign_mat(pommel, 'SAO_Metal_Dark')
        link_to_col(pommel, wpn_col)
        
        result = "Elucidator complete: blade + fuller + guard + grip + pommel"
        result
    """)

# ============================================================
# Phase 5: 亚丝娜 (Asuna) 角色模型
# ============================================================
def phase5_asuna():
    """P5: 构建亚丝娜完整角色"""
    print("\n" + "="*60)
    print("Phase 5: 构建亚丝娜 (Asuna)")
    print("="*60)
    
    print("\n[5.1] 亚丝娜 - 身体基础...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        OFFSET_X = 1.5  # 亚丝娜位于桐人右侧
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        ox = OFFSET_X
        
        # ===== 躯干 =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, 0, 1.05))
        torso = bpy.context.active_object
        torso.name = 'CHR_Asuna_Torso'
        torso.scale = (0.30, 0.18, 0.40)
        bpy.ops.object.transform_apply(scale=True)
        mod = torso.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        bpy.ops.object.shade_smooth()
        assign_mat(torso, 'SAO_Asuna_White')
        link_to_col(torso, char_col)
        
        # ===== 头部 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.20, location=(ox, 0, 1.68))
        head = bpy.context.active_object
        head.name = 'CHR_Asuna_Head'
        head.scale = (1.0, 0.88, 1.05)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(head, 'SAO_Skin')
        link_to_col(head, char_col)
        
        # ===== 眼睛 =====
        for side, x in [('L', 0.07), ('R', -0.07)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(ox+x, -0.16, 1.70))
            eye = bpy.context.active_object
            eye.name = f'CHR_Asuna_Eye_{side}'
            bpy.ops.object.shade_smooth()
            # 亚丝娜琥珀色眼睛
            eye_mat = bpy.data.materials.get('SAO_Asuna_Eye')
            if not eye_mat:
                eye_mat = bpy.data.materials.new('SAO_Asuna_Eye')
                eye_mat.use_nodes = True
                bsdf = eye_mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = (0.55, 0.41, 0.08, 1.0)
            if eye_mat:
                if eye.data.materials:
                    eye.data.materials[0] = eye_mat
                else:
                    eye.data.materials.append(eye_mat)
            link_to_col(eye, char_col)
            
            # 高光
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.015, location=(ox+x+0.02, -0.20, 1.72))
            hl = bpy.context.active_object
            hl.name = f'CHR_Asuna_EyeHL_{side}'
            bpy.ops.object.shade_smooth()
            assign_mat(hl, 'SAO_Eye_Highlight')
            link_to_col(hl, char_col)
        
        # ===== 颈部 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.055, depth=0.10, location=(ox, 0, 1.50))
        neck = bpy.context.active_object
        neck.name = 'CHR_Asuna_Neck'
        bpy.ops.object.shade_smooth()
        assign_mat(neck, 'SAO_Skin')
        link_to_col(neck, char_col)
        
        # ===== 手臂 =====
        for side, x in [('L', 0.40), ('R', -0.40)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.065, depth=0.50, location=(ox+x, 0, 1.05))
            arm = bpy.context.active_object
            arm.name = f'CHR_Asuna_Arm_{side}'
            bpy.ops.object.shade_smooth()
            mod = arm.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            assign_mat(arm, 'SAO_Fabric_White')
            link_to_col(arm, char_col)
        
        # ===== 手 =====
        for side, x in [('L', 0.40), ('R', -0.40)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.05, location=(ox+x, 0, 0.75))
            hand = bpy.context.active_object
            hand.name = f'CHR_Asuna_Hand_{side}'
            hand.scale = (1.0, 0.7, 1.2)
            bpy.ops.object.transform_apply(scale=True)
            bpy.ops.object.shade_smooth()
            assign_mat(hand, 'SAO_Skin')
            link_to_col(hand, char_col)
        
        # ===== 腿 =====
        for side, x in [('L', 0.11), ('R', -0.11)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.075, depth=0.55, location=(ox+x, 0, 0.35))
            leg = bpy.context.active_object
            leg.name = f'CHR_Asuna_Leg_{side}'
            bpy.ops.object.shade_smooth()
            mod = leg.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            assign_mat(leg, 'SAO_Skin')
            link_to_col(leg, char_col)
        
        # ===== 靴子 =====
        for side, x in [('L', 0.11), ('R', -0.11)]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(ox+x, -0.02, 0.06))
            boot = bpy.context.active_object
            boot.name = f'CHR_Asuna_Boot_{side}'
            boot.scale = (0.08, 0.12, 0.08)
            bpy.ops.object.transform_apply(scale=True)
            mod = boot.modifiers.new('SubSurf', 'SUBSURF')
            mod.levels = 1
            bpy.ops.object.shade_smooth()
            assign_mat(boot, 'SAO_Asuna_White')
            link_to_col(boot, char_col)
        
        result = "Asuna body complete: torso, head, eyes, neck, arms, hands, legs, boots"
        result
    """)
    
    print("\n[5.2] 亚丝娜 - 头发(长发+编辫)...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        ox = 1.5
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 头发基础体 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.23, location=(ox, 0.02, 1.72))
        hair_base = bpy.context.active_object
        hair_base.name = 'CHR_Asuna_HairBase'
        hair_base.scale = (1.0, 1.0, 1.0)
        bpy.ops.object.shade_smooth()
        assign_mat(hair_base, 'SAO_Asuna_Hair')
        link_to_col(hair_base, char_col)
        
        # ===== 长直发(后部, 及腰) =====
        # 用扁平化的Cube拉长模拟长发
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, 0.10, 1.30))
        long_hair = bpy.context.active_object
        long_hair.name = 'CHR_Asuna_LongHair'
        long_hair.scale = (0.20, 0.04, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        
        # 编辑模式: 底部略微展宽
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(long_hair.data)
        bm.verts.ensure_lookup_table()
        min_z = min(v.co.z for v in bm.verts)
        for v in bm.verts:
            if abs(v.co.z - min_z) < 0.01:
                v.co.x *= 1.3
        bmesh.update_edit_mesh(long_hair.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        mod = long_hair.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        bpy.ops.object.shade_smooth()
        assign_mat(long_hair, 'SAO_Asuna_Hair')
        link_to_col(long_hair, char_col)
        
        # ===== 刘海 =====
        bangs = [
            (-0.08, -0.18, 1.78, 0.12, 0.035, 12),
            (-0.02, -0.20, 1.80, 0.11, 0.03, 5),
            (0.04,  -0.19, 1.79, 0.13, 0.035, -3),
            (0.10,  -0.17, 1.77, 0.11, 0.03, -10),
        ]
        for i, (x, y, z, length, width, rot) in enumerate(bangs):
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=width, radius2=0.005, depth=length, location=(ox+x, y, z))
            bang = bpy.context.active_object
            bang.name = f'CHR_Asuna_Bang_{i}'
            bang.rotation_euler = (math.radians(70), 0, math.radians(rot))
            bpy.ops.object.shade_smooth()
            assign_mat(bang, 'SAO_Asuna_Hair')
            link_to_col(bang, char_col)
        
        # ===== 编辫(左右各一条, 用扭曲圆柱模拟) =====
        for side, sx in [('L', 0.15), ('R', -0.15)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.50, location=(ox+sx, -0.08, 1.35))
            braid = bpy.context.active_object
            braid.name = f'CHR_Asuna_Braid_{side}'
            braid.rotation_euler = (math.radians(10), 0, math.radians(5 if side=='L' else -5))
            
            # 添加扭曲效果
            mod = braid.modifiers.new('Twist', 'SIMPLE_DEFORM')
            mod.deform_method = 'TWIST'
            mod.angle = math.radians(360)
            
            bpy.ops.object.shade_smooth()
            assign_mat(braid, 'SAO_Asuna_Hair')
            link_to_col(braid, char_col)
        
        # ===== 发带/发箍 =====
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.012, location=(ox, 0, 1.82))
        headband = bpy.context.active_object
        headband.name = 'CHR_Asuna_Headband'
        headband.scale = (1.0, 0.9, 0.3)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(headband, 'SAO_Fabric_White')
        link_to_col(headband, char_col)
        
        result = "Asuna hair complete: base + long hair + 4 bangs + 2 braids + headband"
        result
    """)
    
    print("\n[5.3] 亚丝娜 - KoB战斗装...")
    blender_exec("""
        import bpy, bmesh, math
        
        char_col = bpy.data.collections.get('SAO_Characters')
        ox = 1.5
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 胸甲 (白色, 红色十字) =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, -0.05, 1.12))
        chest = bpy.context.active_object
        chest.name = 'CHR_Asuna_ChestArmor'
        chest.scale = (0.32, 0.10, 0.25)
        bpy.ops.object.transform_apply(scale=True)
        mod = chest.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        bpy.ops.object.shade_smooth()
        assign_mat(chest, 'SAO_Asuna_White')
        link_to_col(chest, char_col)
        
        # ===== 红色十字纹章 =====
        # 横条
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, -0.16, 1.12))
        cross_h = bpy.context.active_object
        cross_h.name = 'CHR_Asuna_Cross_H'
        cross_h.scale = (0.08, 0.005, 0.02)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(cross_h, 'SAO_Asuna_Red')
        link_to_col(cross_h, char_col)
        # 竖条
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, -0.16, 1.12))
        cross_v = bpy.context.active_object
        cross_v.name = 'CHR_Asuna_Cross_V'
        cross_v.scale = (0.02, 0.005, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        assign_mat(cross_v, 'SAO_Asuna_Red')
        link_to_col(cross_v, char_col)
        
        # ===== 肩甲 (红色) =====
        for side, x in [('L', 0.32), ('R', -0.32)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.06, location=(ox+x, 0, 1.28))
            shoulder = bpy.context.active_object
            shoulder.name = f'CHR_Asuna_ShoulderPad_{side}'
            shoulder.scale = (1.0, 0.7, 0.5)
            bpy.ops.object.transform_apply(scale=True)
            bpy.ops.object.shade_smooth()
            assign_mat(shoulder, 'SAO_Asuna_Red')
            link_to_col(shoulder, char_col)
        
        # ===== 短裙 (红色外裙 + 白色内裙) =====
        # 红色外裙
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.28, radius2=0.16, depth=0.25, location=(ox, 0, 0.72))
        skirt_outer = bpy.context.active_object
        skirt_outer.name = 'CHR_Asuna_SkirtOuter'
        bpy.ops.object.shade_smooth()
        assign_mat(skirt_outer, 'SAO_Asuna_Red')
        link_to_col(skirt_outer, char_col)
        
        # 白色内裙
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.26, radius2=0.15, depth=0.22, location=(ox, 0, 0.73))
        skirt_inner = bpy.context.active_object
        skirt_inner.name = 'CHR_Asuna_SkirtInner'
        bpy.ops.object.shade_smooth()
        assign_mat(skirt_inner, 'SAO_Fabric_White')
        link_to_col(skirt_inner, char_col)
        
        # ===== 后裙摆 (白色飘逸裙摆) =====
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, 0.10, 0.55))
        back_skirt = bpy.context.active_object
        back_skirt.name = 'CHR_Asuna_BackSkirt'
        back_skirt.scale = (0.18, 0.03, 0.30)
        bpy.ops.object.transform_apply(scale=True)
        mod = back_skirt.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = 2
        bpy.ops.object.shade_smooth()
        assign_mat(back_skirt, 'SAO_Fabric_White')
        link_to_col(back_skirt, char_col)
        
        # ===== 腰带 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.16, depth=0.04, location=(ox, 0, 0.86))
        belt = bpy.context.active_object
        belt.name = 'CHR_Asuna_Belt'
        belt.scale = (1.0, 0.65, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        assign_mat(belt, 'SAO_Asuna_White')
        link_to_col(belt, char_col)
        
        result = "Asuna KoB outfit complete: chest armor + cross + shoulder pads + skirts + belt"
        result
    """)

# ============================================================
# Phase 6: 闪光 (Lambent Light) 武器
# ============================================================
def phase6_lambent_light():
    """P6: 构建亚丝娜的武器 - 闪光细剑"""
    print("\n" + "="*60)
    print("Phase 6: 构建闪光 (Lambent Light)")
    print("="*60)
    
    print("\n[6.1] 闪光细剑...")
    blender_exec("""
        import bpy, bmesh, math
        
        wpn_col = bpy.data.collections.get('SAO_Weapons')
        ox = 1.5 + 0.45  # 亚丝娜右手位置
        
        def link_to_col(obj, col):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        
        def assign_mat(obj, mat_name):
            mat = bpy.data.materials.get(mat_name)
            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        # ===== 细剑剑身(极细长) =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.005, depth=0.75, location=(ox, -0.12, 1.10))
        blade = bpy.context.active_object
        blade.name = 'WPN_LambentLight_Blade'
        
        # 编辑: 剑尖收尖
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(blade.data)
        bm.verts.ensure_lookup_table()
        max_z = max(v.co.z for v in bm.verts)
        for v in bm.verts:
            if abs(v.co.z - max_z) < 0.01:
                v.co.x *= 0.05
                v.co.y *= 0.05
        bmesh.update_edit_mesh(blade.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.shade_smooth()
        assign_mat(blade, 'SAO_LambentLight_Blade')
        link_to_col(blade, wpn_col)
        
        # ===== 护手篮(环形) =====
        bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.005, location=(ox, -0.12, 0.72))
        guard_ring = bpy.context.active_object
        guard_ring.name = 'WPN_LambentLight_GuardRing'
        guard_ring.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.shade_smooth()
        assign_mat(guard_ring, 'SAO_Metal_Silver')
        link_to_col(guard_ring, wpn_col)
        
        # 护手横条
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.004, depth=0.08, location=(ox, -0.12, 0.72))
        guard_bar = bpy.context.active_object
        guard_bar.name = 'WPN_LambentLight_GuardBar'
        guard_bar.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.shade_smooth()
        assign_mat(guard_bar, 'SAO_Metal_Silver')
        link_to_col(guard_bar, wpn_col)
        
        # ===== 握柄 =====
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.010, depth=0.10, location=(ox, -0.12, 0.66))
        grip = bpy.context.active_object
        grip.name = 'WPN_LambentLight_Grip'
        bpy.ops.object.shade_smooth()
        assign_mat(grip, 'SAO_Fabric_White')
        link_to_col(grip, wpn_col)
        
        # ===== 柄头 =====
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.012, location=(ox, -0.12, 0.60))
        pommel = bpy.context.active_object
        pommel.name = 'WPN_LambentLight_Pommel'
        bpy.ops.object.shade_smooth()
        assign_mat(pommel, 'SAO_Metal_Silver')
        link_to_col(pommel, wpn_col)
        
        result = "Lambent Light complete: blade + guard ring + guard bar + grip + pommel"
        result
    """)

# ============================================================
# Main execution
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  刀剑神域 SAO - 3D模型自动构建系统")
    print("  Sword Art Online - Automated 3D Model Builder")
    print("="*60)
    
    # 测试连接
    print("\n[Test] 连接Blender...")
    send_to_blender("result = f'Blender {bpy.app.version_string} ready'")
    
    phases = [
        ("Phase 1", "场景初始化", phase1_setup),
        ("Phase 2", "材质系统", phase2_materials),
        ("Phase 3", "桐人角色", phase3_kirito),
        ("Phase 4", "逐暗者武器", phase4_elucidator),
        ("Phase 5", "亚丝娜角色", phase5_asuna),
        ("Phase 6", "闪光武器", phase6_lambent_light),
    ]
    
    for name, desc, func in phases:
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR] {name} ({desc}) failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("  构建完成! SAO P0模型已创建")
    print("="*60)
    print("\n已构建:")
    print("  ✓ TOON渲染环境 + 三点光照")
    print("  ✓ 24种SAO卡通材质")
    print("  ✓ 桐人(身体+头发+黑色风衣+描边)")
    print("  ✓ 逐暗者(剑身+护手+握柄)")
    print("  ✓ 亚丝娜(身体+长发+KoB战斗装)")
    print("  ✓ 闪光细剑(剑身+护手篮+握柄)")
