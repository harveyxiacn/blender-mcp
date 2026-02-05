"""
蓬莱九章 - 游戏模型创建脚本
Penglai Nine Chapters - Game Models Creation

包含：
1. 人物模型（仙侠风格角色）
2. 武器装备模型
3. 宝箱模型
4. 怪物模型
5. 坐骑模型
6. 示例关卡场景
"""

import socket
import json
import time
import math


class MCPClient:
    def __init__(self, host='127.0.0.1', port=9876):
        self.host = host
        self.port = port
        self.sock = None
        self.results = []
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(60.0)
        self.sock.connect((self.host, self.port))
        print(f"Connected to Blender MCP: {self.host}:{self.port}")
    
    def disconnect(self):
        if self.sock:
            self.sock.close()
    
    def cmd(self, category, action, params=None):
        """Send command and return result"""
        request = {
            'id': f'{category}-{action}-{time.time()}',
            'type': 'command',
            'category': category,
            'action': action,
            'params': params or {}
        }
        
        try:
            self.sock.send((json.dumps(request) + '\n').encode('utf-8'))
            
            response = b''
            while True:
                chunk = self.sock.recv(65536)
                response += chunk
                if b'\n' in chunk or len(chunk) < 65536:
                    break
            
            result = json.loads(response.decode('utf-8').strip())
            success = result.get('success', False)
            
            status = "[OK]" if success else "[FAIL]"
            print(f"  {status} {category}.{action}")
            
            if not success:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                print(f"    Error: {error_msg}")
            
            self.results.append({
                'test': f'{category}.{action}',
                'success': success,
                'error': result.get('error', {}).get('message') if not success else None
            })
            
            return success, result
        except Exception as e:
            print(f"  [FAIL] {category}.{action}: {e}")
            self.results.append({
                'test': f'{category}.{action}',
                'success': False,
                'error': str(e)
            })
            return False, {'error': str(e)}
    
    def execute_python(self, code, description=""):
        """Execute Python code in Blender"""
        if description:
            print(f"\n>>> {description}")
        return self.cmd('utility', 'execute_python', {'code': code})


def clear_scene(client):
    """Clear the scene"""
    print("\n=== Clearing Scene ===")
    client.execute_python('''
import bpy

# Delete all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Purge orphan data
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
''', "Clearing all objects")


def create_character_model(client):
    """Create Penglai character - Xianxia style warrior"""
    print("\n=== Creating Character Model (Xianxia Warrior) ===")
    
    # Create chibi character using template
    client.cmd('character_template', 'create', {
        'template': 'chibi',
        'name': 'PenglaiHero',
        'height': 1.5,
        'location': [0, 0, 0]
    })
    
    # Add long hair (ancient Chinese style)
    client.cmd('character_template', 'hair_create', {
        'character_name': 'PenglaiHero',
        'hair_style': 'long',
        'color': [0.05, 0.03, 0.02, 1.0]  # Black hair
    })
    
    # Add traditional robe (blue/white)
    client.cmd('character_template', 'clothing_add', {
        'character_name': 'PenglaiHero',
        'clothing_type': 'robe',
        'color': [0.2, 0.4, 0.7, 1.0]  # Blue robe
    })
    
    # Add belt accessory
    client.cmd('character_template', 'accessory_add', {
        'character_name': 'PenglaiHero',
        'accessory_type': 'belt'
    })
    
    # Determined expression
    client.cmd('character_template', 'face_expression', {
        'character_name': 'PenglaiHero',
        'expression': 'determined',
        'intensity': 0.6
    })
    
    # Additional details via Python
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Find the character
hero = None
for obj in bpy.data.objects:
    if 'PenglaiHero' in obj.name:
        hero = obj
        break

if hero:
    # Add decorative elements
    # Create jade pendant
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6,
        radius=0.03,
        depth=0.01,
        location=(hero.location.x, hero.location.y - 0.15, hero.location.z + 0.8)
    )
    pendant = bpy.context.active_object
    pendant.name = "Hero_JadePendant"
    
    jade_mat = bpy.data.materials.new(name="Jade_Green")
    jade_mat.use_nodes = True
    bsdf = get_principled_bsdf(jade_mat)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.2, 0.7, 0.4, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.2
        # Subsurface for jade effect
        try:
            bsdf.inputs["Subsurface Weight"].default_value = 0.3
        except:
            pass
    pendant.data.materials.append(jade_mat)
    
    # Parent pendant to hero
    pendant.parent = hero

print("Character created: PenglaiHero")
''', "Adding character details")


def create_weapon_models(client):
    """Create weapon and equipment models"""
    print("\n=== Creating Weapon Models ===")
    
    # Sword
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Create ancient Chinese sword
# Blade
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, 0.5))
blade = bpy.context.active_object
blade.name = "Sword_Blade"
blade.scale = (0.02, 0.01, 0.4)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add bevel modifier for edge
bevel = blade.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.003
bevel.segments = 2

# Blade material - metallic
blade_mat = bpy.data.materials.new(name="Sword_Metal")
blade_mat.use_nodes = True
bsdf = get_principled_bsdf(blade_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.85, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.15
blade.data.materials.append(blade_mat)

# Handle
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.015,
    depth=0.15,
    location=(3, 0, 0.025)
)
handle = bpy.context.active_object
handle.name = "Sword_Handle"

# Handle material - wrapped fabric
handle_mat = bpy.data.materials.new(name="Sword_Handle_Mat")
handle_mat.use_nodes = True
bsdf = get_principled_bsdf(handle_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.3, 0.15, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
handle.data.materials.append(handle_mat)

# Guard (crossguard)
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, 0.1))
guard = bpy.context.active_object
guard.name = "Sword_Guard"
guard.scale = (0.05, 0.01, 0.02)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Guard material - gold
guard_mat = bpy.data.materials.new(name="Sword_Gold")
guard_mat.use_nodes = True
bsdf = get_principled_bsdf(guard_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.2, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.3
guard.data.materials.append(guard_mat)

# Join sword parts
bpy.ops.object.select_all(action='DESELECT')
blade.select_set(True)
handle.select_set(True)
guard.select_set(True)
bpy.context.view_layer.objects.active = blade
bpy.ops.object.join()
blade.name = "Weapon_Sword"

print("Sword created: Weapon_Sword")
''', "Creating sword model")
    
    # Shield
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Create round shield
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.25,
    depth=0.03,
    location=(4, 0, 0.5)
)
shield = bpy.context.active_object
shield.name = "Weapon_Shield"
shield.rotation_euler = (1.57, 0, 0)  # 90 degrees

# Shield material - bronze
shield_mat = bpy.data.materials.new(name="Shield_Bronze")
shield_mat.use_nodes = True
bsdf = get_principled_bsdf(shield_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.7, 0.5, 0.25, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.4
shield.data.materials.append(shield_mat)

# Add boss (center protrusion)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.05,
    location=(4, 0.02, 0.5)
)
boss = bpy.context.active_object
boss.name = "Shield_Boss"
boss.scale = (1, 0.5, 1)
boss.data.materials.append(shield_mat)

# Join
bpy.ops.object.select_all(action='DESELECT')
shield.select_set(True)
boss.select_set(True)
bpy.context.view_layer.objects.active = shield
bpy.ops.object.join()
shield.name = "Weapon_Shield"

print("Shield created: Weapon_Shield")
''', "Creating shield model")

    # Staff
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Create magic staff
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.02,
    depth=1.2,
    location=(5, 0, 0.6)
)
staff = bpy.context.active_object
staff.name = "Weapon_Staff"

# Wood material
wood_mat = bpy.data.materials.new(name="Staff_Wood")
wood_mat.use_nodes = True
bsdf = get_principled_bsdf(wood_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.35, 0.2, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
staff.data.materials.append(wood_mat)

# Crystal orb on top
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=16,
    radius=0.06,
    location=(5, 0, 1.25)
)
orb = bpy.context.active_object
orb.name = "Staff_Orb"

# Crystal material - glowing blue
crystal_mat = bpy.data.materials.new(name="Staff_Crystal")
crystal_mat.use_nodes = True
bsdf = get_principled_bsdf(crystal_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.3, 0.6, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.1
    try:
        bsdf.inputs["Emission Color"].default_value = (0.3, 0.6, 1.0, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 2.0
    except:
        pass
orb.data.materials.append(crystal_mat)

# Join
bpy.ops.object.select_all(action='DESELECT')
staff.select_set(True)
orb.select_set(True)
bpy.context.view_layer.objects.active = staff
bpy.ops.object.join()
staff.name = "Weapon_Staff"

print("Staff created: Weapon_Staff")
''', "Creating staff model")


def create_treasure_chest(client):
    """Create treasure chest model"""
    print("\n=== Creating Treasure Chest ===")
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Chest base
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3, 0.2))
chest_base = bpy.context.active_object
chest_base.name = "Chest_Base"
chest_base.scale = (0.4, 0.25, 0.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Chest lid (half cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.25,
    depth=0.4,
    location=(0, 3, 0.4)
)
chest_lid = bpy.context.active_object
chest_lid.name = "Chest_Lid"
chest_lid.rotation_euler = (0, math.radians(90), 0)

# Edit mode to cut cylinder in half
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0, 3, 0.4), plane_no=(0, 0, 1), clear_inner=True)
bpy.ops.object.mode_set(mode='OBJECT')

# Wood material
wood_mat = bpy.data.materials.new(name="Chest_Wood")
wood_mat.use_nodes = True
bsdf = get_principled_bsdf(wood_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
chest_base.data.materials.append(wood_mat)
chest_lid.data.materials.append(wood_mat)

# Metal bands
band_mat = bpy.data.materials.new(name="Chest_Metal")
band_mat.use_nodes = True
bsdf = get_principled_bsdf(band_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.2, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.3

# Add metal bands
for x_offset in [-0.3, 0, 0.3]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_offset, 3, 0.21))
    band = bpy.context.active_object
    band.name = f"Chest_Band"
    band.scale = (0.03, 0.26, 0.22)
    band.data.materials.append(band_mat)

# Lock
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.03,
    depth=0.02,
    location=(0, 2.75, 0.2)
)
lock = bpy.context.active_object
lock.name = "Chest_Lock"
lock.rotation_euler = (math.radians(90), 0, 0)
lock.data.materials.append(band_mat)

# Join all chest parts
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "Chest" in obj.name:
        obj.select_set(True)
bpy.context.view_layer.objects.active = chest_base
bpy.ops.object.join()
chest_base.name = "TreasureChest"

print("Treasure chest created: TreasureChest")
''', "Creating treasure chest")


def create_monster_model(client):
    """Create monster model - Chinese mythology style"""
    print("\n=== Creating Monster Model ===")
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Create a demon/yaoguai style monster
# Body - hunched creature
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=12,
    radius=0.3,
    location=(-3, 0, 0.4)
)
body = bpy.context.active_object
body.name = "Monster_Body"
body.scale = (1.2, 0.8, 1.0)

# Head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=12,
    radius=0.2,
    location=(-3, 0.25, 0.7)
)
head = bpy.context.active_object
head.name = "Monster_Head"
head.scale = (1.0, 0.9, 1.1)

# Horns
for x_offset in [-0.1, 0.1]:
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=0.03,
        radius2=0,
        depth=0.15,
        location=(-3 + x_offset, 0.25, 0.95)
    )
    horn = bpy.context.active_object
    horn.name = f"Monster_Horn"
    horn.rotation_euler = (math.radians(-20), x_offset * 3, 0)

# Eyes (glowing)
eye_mat = bpy.data.materials.new(name="Monster_Eye")
eye_mat.use_nodes = True
bsdf = get_principled_bsdf(eye_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (1.0, 0.3, 0.0, 1.0)
    try:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.3, 0.0, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 5.0
    except:
        pass

for x_offset in [-0.08, 0.08]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8,
        ring_count=6,
        radius=0.03,
        location=(-3 + x_offset, 0.4, 0.75)
    )
    eye = bpy.context.active_object
    eye.name = "Monster_Eye"
    eye.data.materials.append(eye_mat)

# Arms
arm_mat = bpy.data.materials.new(name="Monster_Skin")
arm_mat.use_nodes = True
bsdf = get_principled_bsdf(arm_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.3, 0.4, 0.2, 1.0)  # Green-gray
    bsdf.inputs["Roughness"].default_value = 0.8

body.data.materials.append(arm_mat)
head.data.materials.append(arm_mat)

for x_offset in [-0.35, 0.35]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.06,
        depth=0.4,
        location=(-3 + x_offset, 0.1, 0.35)
    )
    arm = bpy.context.active_object
    arm.name = "Monster_Arm"
    arm.rotation_euler = (0, math.radians(30 if x_offset > 0 else -30), 0)
    arm.data.materials.append(arm_mat)
    
    # Claws
    for i in range(3):
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=0.015,
            radius2=0,
            depth=0.08,
            location=(-3 + x_offset + (i-1)*0.02, 0.25, 0.12)
        )
        claw = bpy.context.active_object
        claw.name = "Monster_Claw"
        claw.rotation_euler = (math.radians(70), 0, 0)

# Legs
for x_offset in [-0.15, 0.15]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.08,
        depth=0.3,
        location=(-3 + x_offset, -0.05, 0.15)
    )
    leg = bpy.context.active_object
    leg.name = "Monster_Leg"
    leg.data.materials.append(arm_mat)

# Horn material
horn_mat = bpy.data.materials.new(name="Monster_Horn")
horn_mat.use_nodes = True
bsdf = get_principled_bsdf(horn_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.2, 0.15, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

for obj in bpy.data.objects:
    if "Monster_Horn" in obj.name:
        obj.data.materials.append(horn_mat)

# Join all monster parts
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "Monster" in obj.name:
        obj.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = "Monster_Yaoguai"

print("Monster created: Monster_Yaoguai")
''', "Creating monster model")


def create_mount_model(client):
    """Create mount model - Chinese style qilin/horse"""
    print("\n=== Creating Mount Model ===")
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Create a stylized qilin/deer mount
# Body
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20,
    ring_count=14,
    radius=0.4,
    location=(-3, -4, 0.6)
)
body = bpy.context.active_object
body.name = "Mount_Body"
body.scale = (1.5, 0.7, 0.8)

# Neck
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=0.12,
    depth=0.4,
    location=(-3 + 0.4, -4, 0.9)
)
neck = bpy.context.active_object
neck.name = "Mount_Neck"
neck.rotation_euler = (math.radians(-50), 0, 0)

# Head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=14,
    ring_count=10,
    radius=0.15,
    location=(-3 + 0.55, -4, 1.15)
)
head = bpy.context.active_object
head.name = "Mount_Head"
head.scale = (1.3, 0.8, 1.0)

# Antlers (for qilin style)
for x_offset in [-0.08, 0.08]:
    bpy.ops.mesh.primitive_cone_add(
        vertices=6,
        radius1=0.02,
        radius2=0.005,
        depth=0.2,
        location=(-3 + 0.55 + x_offset, -4, 1.35)
    )
    antler = bpy.context.active_object
    antler.name = "Mount_Antler"
    antler.rotation_euler = (math.radians(-10), x_offset * 5, 0)

# Legs (4)
leg_positions = [
    (0.3, 0.15), (0.3, -0.15),
    (-0.3, 0.15), (-0.3, -0.15)
]
for x, y in leg_positions:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=10,
        radius=0.05,
        depth=0.5,
        location=(-3 + x, -4 + y, 0.25)
    )
    leg = bpy.context.active_object
    leg.name = "Mount_Leg"

# Tail
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=0.08,
    radius2=0.02,
    depth=0.4,
    location=(-3 - 0.5, -4, 0.6)
)
tail = bpy.context.active_object
tail.name = "Mount_Tail"
tail.rotation_euler = (0, math.radians(70), 0)

# Saddle
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, -4, 0.95))
saddle = bpy.context.active_object
saddle.name = "Mount_Saddle"
saddle.scale = (0.3, 0.2, 0.05)

# Materials
# Body - golden/white
body_mat = bpy.data.materials.new(name="Mount_Body_Mat")
body_mat.use_nodes = True
bsdf = get_principled_bsdf(body_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.95, 0.9, 0.8, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.4

body.data.materials.append(body_mat)
neck.data.materials.append(body_mat)
head.data.materials.append(body_mat)
tail.data.materials.append(body_mat)

for obj in bpy.data.objects:
    if "Mount_Leg" in obj.name or "Mount_Antler" in obj.name:
        obj.data.materials.append(body_mat)

# Saddle - red
saddle_mat = bpy.data.materials.new(name="Mount_Saddle_Mat")
saddle_mat.use_nodes = True
bsdf = get_principled_bsdf(saddle_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.7, 0.1, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
saddle.data.materials.append(saddle_mat)

# Join all mount parts
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "Mount" in obj.name:
        obj.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = "Mount_Qilin"

print("Mount created: Mount_Qilin")
''', "Creating mount model")


def create_level_scene(client):
    """Create sample level scene - ancient Chinese temple/garden"""
    print("\n=== Creating Sample Level Scene ===")
    
    # Use scene advanced for environment
    client.cmd('scene_advanced', 'environment_preset', {
        'preset': 'forest',
        'intensity': 0.7
    })
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# Ground - grass/stone path
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Level_Ground"

grass_mat = bpy.data.materials.new(name="Level_Grass")
grass_mat.use_nodes = True
bsdf = get_principled_bsdf(grass_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 0.15, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(grass_mat)

# Stone path
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
path = bpy.context.active_object
path.name = "Level_Path"
path.scale = (1.5, 10, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

stone_mat = bpy.data.materials.new(name="Level_Stone")
stone_mat.use_nodes = True
bsdf = get_principled_bsdf(stone_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.5, 0.48, 0.45, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
path.data.materials.append(stone_mat)

# Torii gate / Chinese gate
gate_mat = bpy.data.materials.new(name="Level_Gate_Red")
gate_mat.use_nodes = True
bsdf = get_principled_bsdf(gate_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.7, 0.15, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.4

# Gate pillars
for x in [-1.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.15,
        depth=3,
        location=(x, -8, 1.5)
    )
    pillar = bpy.context.active_object
    pillar.name = f"Level_Gate_Pillar"
    pillar.data.materials.append(gate_mat)

# Gate top beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -8, 3.2))
beam = bpy.context.active_object
beam.name = "Level_Gate_Beam"
beam.scale = (2.0, 0.2, 0.15)
beam.data.materials.append(gate_mat)

# Gate roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -8, 3.5))
roof = bpy.context.active_object
roof.name = "Level_Gate_Roof"
roof.scale = (2.2, 0.3, 0.1)

roof_mat = bpy.data.materials.new(name="Level_Roof_Mat")
roof_mat.use_nodes = True
bsdf = get_principled_bsdf(roof_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
roof.data.materials.append(roof_mat)

# Trees (simple)
tree_mat = bpy.data.materials.new(name="Level_Tree_Leaves")
tree_mat.use_nodes = True
bsdf = get_principled_bsdf(tree_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.15, 0.35, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

trunk_mat = bpy.data.materials.new(name="Level_Tree_Trunk")
trunk_mat.use_nodes = True
bsdf = get_principled_bsdf(trunk_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8

tree_positions = [
    (-5, -5), (-5, 5), (5, -5), (5, 5),
    (-7, 0), (7, 0), (-3, -10), (3, -10)
]

for tx, ty in tree_positions:
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.15,
        depth=2,
        location=(tx, ty, 1)
    )
    trunk = bpy.context.active_object
    trunk.name = "Level_Tree_Trunk"
    trunk.data.materials.append(trunk_mat)
    
    # Foliage
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12,
        ring_count=8,
        radius=0.8,
        location=(tx, ty, 2.5)
    )
    leaves = bpy.context.active_object
    leaves.name = "Level_Tree_Leaves"
    leaves.scale = (1.0, 1.0, 0.7)
    leaves.data.materials.append(tree_mat)

# Lanterns
lantern_mat = bpy.data.materials.new(name="Level_Lantern")
lantern_mat.use_nodes = True
bsdf = get_principled_bsdf(lantern_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.9, 0.5, 0.2, 1.0)
    try:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.6, 0.2, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 3.0
    except:
        pass

for x in [-1.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.1,
        depth=0.3,
        location=(x, -8, 2.5)
    )
    lantern = bpy.context.active_object
    lantern.name = "Level_Lantern"
    lantern.data.materials.append(lantern_mat)

# Rock formations
rock_mat = bpy.data.materials.new(name="Level_Rock")
rock_mat.use_nodes = True
bsdf = get_principled_bsdf(rock_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.38, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9

rock_positions = [(-8, 3), (8, -3), (-6, -8), (6, 8)]
for rx, ry in rock_positions:
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.5,
        location=(rx, ry, 0.3)
    )
    rock = bpy.context.active_object
    rock.name = "Level_Rock"
    rock.scale = (1.2, 1.0, 0.7)
    rock.data.materials.append(rock_mat)

# Add lights
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Level_Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Camera
bpy.ops.object.camera_add(location=(8, -12, 5))
camera = bpy.context.active_object
camera.name = "Level_Camera"
camera.rotation_euler = (math.radians(70), 0, math.radians(30))
bpy.context.scene.camera = camera

print("Level scene created!")
''', "Creating level scene elements")


def setup_scene(client):
    """Final scene setup"""
    print("\n=== Final Scene Setup ===")
    
    client.cmd('render', 'settings', {
        'engine': 'CYCLES',
        'samples': 64,
        'resolution_x': 1920,
        'resolution_y': 1080
    })
    
    # World settings
    client.cmd('world', 'create', {
        'name': 'PenglaiWorld',
        'color': [0.5, 0.7, 1.0]
    })


def main():
    print("="*60)
    print("Penglai Nine Chapters - Game Models Creation")
    print("="*60)
    
    client = MCPClient()
    
    try:
        client.connect()
        
        # Clear scene
        clear_scene(client)
        
        # Create all models
        create_character_model(client)
        create_weapon_models(client)
        create_treasure_chest(client)
        create_monster_model(client)
        create_mount_model(client)
        create_level_scene(client)
        
        # Setup scene
        setup_scene(client)
        
        # Results
        print("\n" + "="*60)
        print("Creation Complete!")
        print("="*60)
        
        passed = sum(1 for r in client.results if r['success'])
        failed = sum(1 for r in client.results if not r['success'])
        print(f"\nTotal: {len(client.results)} | Passed: {passed} | Failed: {failed}")
        
        if failed > 0:
            print("\nFailed operations:")
            for r in client.results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['error']}")
        
        print("\nPlease check the results in Blender!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
