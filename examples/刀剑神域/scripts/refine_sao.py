"""
SAO 模型精细化 - 通过 utility.execute_python 添加:
  1. 平滑着色
  2. SubSurf修改器
  3. 卡通赛璐璐材质替换
  4. Solidify描边
  5. TOON渲染设置
"""
import socket
import json
import time

class BlenderExec:
    def __init__(self, host="127.0.0.1", port=9876):
        self.host = host
        self.port = port
        self._id = 0
    
    def run(self, code, timeout=30):
        self._id += 1
        request = {
            "id": f"ref_{self._id}",
            "type": "command",
            "category": "utility",
            "action": "execute_python",
            "params": {"code": code, "timeout": timeout}
        }
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout + 5)
        try:
            sock.connect((self.host, self.port))
            sock.send((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
            buf = ""
            while "\n" not in buf:
                d = sock.recv(8192)
                if not d: break
                buf += d.decode("utf-8")
            resp = json.loads(buf.strip()) if buf.strip() else {}
            if resp.get("success"):
                out = resp.get("data", {}).get("output", "")
                if out.strip():
                    print(f"    {out.strip()}")
                return True
            else:
                err = resp.get("error", {})
                print(f"    ✗ {err.get('message', 'unknown error')}")
                return False
        except Exception as e:
            print(f"    ✗ {e}")
            return False
        finally:
            sock.close()

B = BlenderExec()

print("\n" + "="*60)
print("  SAO 模型精细化")
print("="*60)

# ============================================================
# Step 1: 平滑着色
# ============================================================
print("\n[Step 1] 批量平滑着色...")
B.run("""
import bpy
count = 0
for obj in bpy.data.objects:
    if obj.name.startswith(('CHR_','WPN_')) and obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)
        count += 1
print(f"Smooth shading applied to {count} objects")
""")

# ============================================================
# Step 2: SubSurf修改器
# ============================================================
print("\n[Step 2] 添加SubSurf修改器...")
B.run("""
import bpy
subsurface_targets = {
    # 桐人
    'CHR_Kirito_Torso': 2, 'CHR_Kirito_Head': 2,
    'CHR_Kirito_Arm_L': 1, 'CHR_Kirito_Arm_R': 1,
    'CHR_Kirito_Leg_L': 1, 'CHR_Kirito_Leg_R': 1,
    'CHR_Kirito_Hand_L': 1, 'CHR_Kirito_Hand_R': 1,
    'CHR_Kirito_Boot_L': 1, 'CHR_Kirito_Boot_R': 1,
    'CHR_Kirito_HairBase': 1, 'CHR_Kirito_Coat': 2,
    # 亚丝娜
    'CHR_Asuna_Torso': 2, 'CHR_Asuna_Head': 2,
    'CHR_Asuna_Arm_L': 1, 'CHR_Asuna_Arm_R': 1,
    'CHR_Asuna_Leg_L': 1, 'CHR_Asuna_Leg_R': 1,
    'CHR_Asuna_Hand_L': 1, 'CHR_Asuna_Hand_R': 1,
    'CHR_Asuna_Boot_L': 1, 'CHR_Asuna_Boot_R': 1,
    'CHR_Asuna_HairBase': 1, 'CHR_Asuna_LongHair': 2,
    'CHR_Asuna_ChestArmor': 2,
    # 克莱因
    'CHR_Klein_Torso': 2, 'CHR_Klein_Head': 2,
    'CHR_Klein_Arm_L': 1, 'CHR_Klein_Arm_R': 1,
    'CHR_Klein_Leg_L': 1, 'CHR_Klein_Leg_R': 1,
    'CHR_Klein_HairBase': 1,
    # 武器
    'WPN_Elucidator_Blade': 1, 'WPN_Elucidator_Guard': 1,
}
count = 0
for name, level in subsurface_targets.items():
    obj = bpy.data.objects.get(name)
    if obj and not any(m.type == 'SUBSURF' for m in obj.modifiers):
        mod = obj.modifiers.new('SubSurf', 'SUBSURF')
        mod.levels = level
        mod.render_levels = level
        count += 1
print(f"SubSurf added to {count} objects")
""")

# ============================================================
# Step 3: 卡通赛璐璐材质替换
# ============================================================
print("\n[Step 3] 升级为赛璐璐材质...")
B.run("""
import bpy

def upgrade_to_toon(mat_name, base_rgb, shadow_mult=(0.6,0.55,0.65), ramp_pos=0.45):
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.use_nodes:
        return False
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 检查是否已经是toon(有ShaderToRGB节点)
    if any(n.type == 'SHADERTORGB' for n in nodes):
        return False
    
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
    return True

toon_mats = {
    'SAO_Skin':          (0.95, 0.82, 0.73),
    'SAO_Kirito_Black':  (0.04, 0.04, 0.04),
    'SAO_Kirito_Hair':   (0.04, 0.04, 0.06),
    'SAO_Asuna_White':   (0.96, 0.96, 0.96),
    'SAO_Asuna_Red':     (0.80, 0.20, 0.20),
    'SAO_Asuna_Hair':    (0.78, 0.46, 0.20),
    'SAO_Asuna_Eye':     (0.55, 0.41, 0.08),
    'SAO_Klein_Red':     (0.72, 0.26, 0.18),
    'SAO_Klein_Hair':    (0.72, 0.26, 0.18),
    'SAO_Klein_Cream':   (0.91, 0.86, 0.78),
    'SAO_Klein_Brown':   (0.29, 0.19, 0.13),
    'SAO_Leather_Brown': (0.29, 0.16, 0.08),
    'SAO_Fabric_White':  (0.92, 0.92, 0.90),
    'SAO_Eye_Black':     (0.02, 0.02, 0.02),
    'SAO_Sachi_Blue':    (0.17, 0.17, 0.43),
    'SAO_Liz_DarkRed':   (0.55, 0.13, 0.19),
}

count = sum(1 for n,c in toon_mats.items() if upgrade_to_toon(n, c))
print(f"Upgraded {count} materials to toon/cel-shading")
""")

# 金属材质单独处理(保留金属感 + toon)
B.run("""
import bpy

def create_metallic_toon(mat_name, base_rgb, metallic_strength=0.8):
    mat = bpy.data.materials.get(mat_name)
    if not mat: return False
    if any(n.type == 'SHADERTORGB' for n in mat.node_tree.nodes): return False
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    glossy = nodes.new('ShaderNodeBsdfGlossy')
    glossy.inputs['Color'].default_value = (*base_rgb, 1.0)
    glossy.inputs['Roughness'].default_value = 0.15
    glossy.location = (-200, 0)
    
    s2rgb = nodes.new('ShaderNodeShaderToRGB')
    s2rgb.location = (0, 0)
    links.new(glossy.outputs['BSDF'], s2rgb.inputs['Shader'])
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    dark = (base_rgb[0]*0.3, base_rgb[1]*0.3, base_rgb[2]*0.35, 1.0)
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].color = (*base_rgb, 1.0)
    ramp.color_ramp.elements[1].position = 0.4
    
    # 高光层
    highlight = ramp.color_ramp.elements.new(0.85)
    highlight.color = (min(1,base_rgb[0]+0.3), min(1,base_rgb[1]+0.3), min(1,base_rgb[2]+0.3), 1.0)
    
    links.new(s2rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])
    return True

metal_mats = {
    'SAO_Metal_Silver':     (0.70, 0.70, 0.72),
    'SAO_Metal_Gold':       (0.83, 0.69, 0.22),
    'SAO_Metal_Dark':       (0.08, 0.08, 0.08),
    'SAO_Kirito_Silver':    (0.75, 0.75, 0.75),
    'SAO_Asuna_Gold':       (0.83, 0.69, 0.22),
    'SAO_Elucidator':       (0.03, 0.03, 0.04),
    'SAO_LambentLight':     (0.91, 0.91, 0.94),
}
count = sum(1 for n,c in metal_mats.items() if create_metallic_toon(n, c))
print(f"Upgraded {count} metallic materials to toon")
""")

# 自发光材质
B.run("""
import bpy

mat = bpy.data.materials.get('SAO_Eye_Highlight')
if mat:
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1,1,1,1)
    emission.inputs['Strength'].default_value = 2.0
    emission.location = (100, 0)
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    print("Eye highlight emission material set")
""")

# ============================================================
# Step 4: 描边 (Solidify翻转法线)
# ============================================================
print("\n[Step 4] 添加描边效果...")
B.run("""
import bpy

# 描边材质
outline_mat = bpy.data.materials.get('SAO_Outline')
if not outline_mat:
    outline_mat = bpy.data.materials.new('SAO_Outline')
    outline_mat.use_nodes = True
    outline_mat.use_backface_culling = True
    nodes = outline_mat.node_tree.nodes
    links = outline_mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (0,0,0,1)
    emission.inputs['Strength'].default_value = 0
    emission.location = (100, 0)
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

outline_targets = [
    'CHR_Kirito_Torso','CHR_Kirito_Head','CHR_Kirito_Coat','CHR_Kirito_HairBase',
    'CHR_Kirito_Arm_L','CHR_Kirito_Arm_R','CHR_Kirito_Leg_L','CHR_Kirito_Leg_R',
    'CHR_Asuna_Torso','CHR_Asuna_Head','CHR_Asuna_HairBase','CHR_Asuna_LongHair',
    'CHR_Asuna_Arm_L','CHR_Asuna_Arm_R','CHR_Asuna_Leg_L','CHR_Asuna_Leg_R',
    'CHR_Asuna_ChestArmor','CHR_Asuna_SkirtOuter',
    'CHR_Klein_Torso','CHR_Klein_Head','CHR_Klein_HairBase',
    'CHR_Klein_Arm_L','CHR_Klein_Arm_R','CHR_Klein_Leg_L','CHR_Klein_Leg_R',
]

count = 0
for name in outline_targets:
    obj = bpy.data.objects.get(name)
    if obj and not any(m.name == 'Outline' for m in obj.modifiers):
        mod = obj.modifiers.new('Outline', 'SOLIDIFY')
        mod.thickness = 0.008
        mod.offset = -1
        mod.use_flip_normals = True
        mod.material_offset = len(obj.data.materials)
        obj.data.materials.append(outline_mat)
        count += 1
print(f"Outline added to {count} objects")
""")

# ============================================================
# Step 5: EEVEE渲染设置
# ============================================================
print("\n[Step 5] 优化EEVEE渲染设置...")
B.run("""
import bpy
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.film_transparent = True
scene.view_settings.view_transform = 'Standard'

# 灯光调整
for name in ['SAO_KeyLight','SAO_FillLight','SAO_RimLight']:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'LIGHT':
        obj.data.type = 'SUN'
        
key = bpy.data.objects.get('SAO_KeyLight')
if key: key.data.energy = 3.0; key.data.color = (1.0, 0.95, 0.9)

fill = bpy.data.objects.get('SAO_FillLight')
if fill: fill.data.energy = 1.0; fill.data.color = (0.85, 0.9, 1.0)

rim = bpy.data.objects.get('SAO_RimLight')
if rim: rim.data.energy = 1.5

# 摄像机设置
cam = bpy.data.objects.get('SAO_Camera')
if cam:
    cam.data.lens = 85
    cam.data.clip_end = 1000
    scene.camera = cam

print("EEVEE + Standard color + 85mm lens configured")
""")

# ============================================================
# Step 6: 保存文件
# ============================================================
print("\n[Step 6] 保存文件...")
B.run("""
import bpy
filepath = bpy.data.filepath
if filepath:
    bpy.ops.wm.save_mainfile(filepath=filepath)
    print(f"Saved to {filepath}")
else:
    print("No filepath set, save manually")
""")

print("\n" + "="*60)
print("  精细化完成!")
print("="*60)
print("  ✓ 平滑着色")
print("  ✓ SubSurf修改器 (身体/头部Lv2, 四肢Lv1)")
print("  ✓ 赛璐璐材质 (Shader→RGB + ColorRamp)")
print("  ✓ 金属卡通材质 (Glossy + 3阶色阶)")
print("  ✓ Solidify描边 (25个对象)")
print("  ✓ EEVEE渲染优化")
print("="*60)
