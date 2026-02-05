"""
创建樊振东Q版人物模型 + 乒乓球拍 + 乒乓球 + 乒乓球台 + 巴黎奥运场景
Fan Zhendong Q-version Character + Ping Pong Scene for Paris Olympics
"""

import socket
import json
import time


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
        print(f"已连接到 Blender MCP: {self.host}:{self.port}")
    
    def disconnect(self):
        if self.sock:
            self.sock.close()
    
    def cmd(self, category, action, params=None):
        """发送命令并返回结果"""
        request = {
            'id': f'{category}-{action}-{time.time()}',
            'type': 'command',
            'category': category,
            'action': action,
            'params': params or {}
        }
        
        try:
            self.sock.send((json.dumps(request) + '\n').encode('utf-8'))
            
            # 接收完整响应
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
                print(f"    错误: {error_msg}")
            
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
        """执行Python代码"""
        if description:
            print(f"\n>>> {description}")
        return self.cmd('utility', 'execute_python', {'code': code})


def clear_scene(client):
    """清空场景"""
    print("\n=== 清空场景 ===")
    client.execute_python('''
import bpy

# 删除所有物体
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 清理孤立数据
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
''', "清空场景中的所有物体")


def create_fan_zhendong_character(client):
    """创建樊振东Q版人物"""
    print("\n=== 创建樊振东Q版人物 ===")
    
    # 使用character_template创建Q版角色
    client.cmd('character_template', 'create', {
        'template': 'chibi',
        'name': 'FanZhendong',
        'height': 1.2,
        'location': [0, 0, 0]
    })
    
    # 添加短发（黑色）
    client.cmd('character_template', 'hair_create', {
        'character_name': 'FanZhendong',
        'hair_style': 'short',
        'color': [0.02, 0.01, 0.01, 1.0]  # 黑色头发
    })
    
    # 添加运动服（红色中国队服）
    client.cmd('character_template', 'clothing_add', {
        'character_name': 'FanZhendong',
        'clothing_type': 'sportswear',
        'color': [0.8, 0.1, 0.1, 1.0]  # 红色
    })
    
    # 设置表情 - 专注
    client.cmd('character_template', 'face_expression', {
        'character_name': 'FanZhendong',
        'expression': 'determined',
        'intensity': 0.7
    })
    
    # 添加金牌配饰
    client.cmd('character_template', 'accessory_add', {
        'character_name': 'FanZhendong',
        'accessory_type': 'medal'
    })
    
    # 创建皮肤材质
    client.cmd('material', 'create', {
        'name': 'FanSkin',
        'base_color': [0.87, 0.72, 0.58, 1.0],  # 亚洲肤色
        'roughness': 0.5,
        'subsurface': 0.3
    })


def create_ping_pong_paddle(client):
    """创建乒乓球拍"""
    print("\n=== 创建乒乓球拍 ===")
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# 创建拍面 - 使用圆柱体并压扁
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.08,
    depth=0.015,
    location=(0.35, 0.05, 0.7)
)
paddle_face = bpy.context.active_object
paddle_face.name = "Paddle_Face"

# 稍微椭圆化
paddle_face.scale = (1.0, 0.85, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 创建手柄 - 使用立方体并调整
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.015,
    depth=0.12,
    location=(0.35, 0.05, 0.58)
)
handle = bpy.context.active_object
handle.name = "Paddle_Handle"

# 创建红色材质（正面）
red_mat = bpy.data.materials.new(name="Paddle_Red")
red_mat.use_nodes = True
bsdf = get_principled_bsdf(red_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
paddle_face.data.materials.append(red_mat)

# 创建木质手柄材质
wood_mat = bpy.data.materials.new(name="Paddle_Wood")
wood_mat.use_nodes = True
bsdf = get_principled_bsdf(wood_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
handle.data.materials.append(wood_mat)

# 合并为一个整体
bpy.ops.object.select_all(action='DESELECT')
paddle_face.select_set(True)
handle.select_set(True)
bpy.context.view_layer.objects.active = paddle_face
bpy.ops.object.join()
paddle_face.name = "PingPong_Paddle"

# 旋转以便握持
paddle_face.rotation_euler = (math.radians(15), 0, math.radians(-30))

print(f"乒乓球拍已创建: {paddle_face.name}")
''', "创建乒乓球拍模型")


def create_ping_pong_ball(client):
    """创建乒乓球"""
    print("\n=== 创建乒乓球 ===")
    
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# 创建球体
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=16,
    radius=0.02,
    location=(0.5, 0, 0.78)
)
ball = bpy.context.active_object
ball.name = "PingPong_Ball"

# 平滑着色
bpy.ops.object.shade_smooth()

# 创建橙色乒乓球材质
mat = bpy.data.materials.new(name="Ball_Orange")
mat.use_nodes = True
bsdf = get_principled_bsdf(mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.1, 1.0)  # 橙色
    bsdf.inputs["Roughness"].default_value = 0.3
    # 尝试设置Specular，兼容不同版本
    try:
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
    except:
        try:
            bsdf.inputs["Specular"].default_value = 0.5
        except:
            pass
ball.data.materials.append(mat)

print(f"乒乓球已创建: {ball.name}")
''', "创建乒乓球模型")


def create_ping_pong_table(client):
    """创建乒乓球台"""
    print("\n=== 创建乒乓球台 ===")
    
    client.execute_python('''
import bpy

def get_principled_bsdf(mat):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# 乒乓球台标准尺寸: 2.74m x 1.525m x 0.76m高
# 缩小比例用于Q版场景
scale = 0.5
table_length = 2.74 * scale
table_width = 1.525 * scale
table_height = 0.76 * scale
table_thickness = 0.02

# 创建台面
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, table_height)
)
table_top = bpy.context.active_object
table_top.name = "Table_Top"
table_top.scale = (table_length/2, table_width/2, table_thickness)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 创建深蓝色台面材质
blue_mat = bpy.data.materials.new(name="Table_Blue")
blue_mat.use_nodes = True
bsdf = get_principled_bsdf(blue_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.0, 0.15, 0.4, 1.0)  # 深蓝色
    bsdf.inputs["Roughness"].default_value = 0.2
table_top.data.materials.append(blue_mat)

# 创建4个桌腿
leg_radius = 0.03
leg_positions = [
    (table_length/2 - 0.1, table_width/2 - 0.1),
    (table_length/2 - 0.1, -table_width/2 + 0.1),
    (-table_length/2 + 0.1, table_width/2 - 0.1),
    (-table_length/2 + 0.1, -table_width/2 + 0.1)
]

leg_mat = bpy.data.materials.new(name="Table_Leg_Metal")
leg_mat.use_nodes = True
bsdf = get_principled_bsdf(leg_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3

for i, (x, y) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=leg_radius,
        depth=table_height - table_thickness,
        location=(x, y, (table_height - table_thickness) / 2)
    )
    leg = bpy.context.active_object
    leg.name = f"Table_Leg_{i+1}"
    leg.data.materials.append(leg_mat)

# 创建球网
net_height = 0.1525 * scale
bpy.ops.mesh.primitive_plane_add(
    size=1,
    location=(0, 0, table_height + net_height/2 + table_thickness)
)
net = bpy.context.active_object
net.name = "Table_Net"
net.scale = (0.01, table_width/2, net_height/2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 球网材质
net_mat = bpy.data.materials.new(name="Net_White")
net_mat.use_nodes = True
bsdf = get_principled_bsdf(net_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
net.data.materials.append(net_mat)

# 创建白色边线
# 中线
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, table_height + table_thickness + 0.001))
center_line = bpy.context.active_object
center_line.name = "Table_CenterLine"
center_line.scale = (0.002, table_width/2, 0.001)

# 边线材质
white_mat = bpy.data.materials.new(name="Line_White")
white_mat.use_nodes = True
bsdf = get_principled_bsdf(white_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
center_line.data.materials.append(white_mat)

# 合并所有桌子部件
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.name.startswith("Table_"):
        obj.select_set(True)
bpy.context.view_layer.objects.active = table_top
bpy.ops.object.join()
table_top.name = "PingPong_Table"

print(f"乒乓球台已创建: {table_top.name}")
''', "创建乒乓球台模型")


def create_paris_olympics_scene(client):
    """创建巴黎奥运场景"""
    print("\n=== 创建巴黎奥运场景 ===")
    
    # 使用场景高级功能创建体育馆环境
    client.cmd('scene_advanced', 'environment_preset', {
        'preset': 'stadium',
        'intensity': 0.9
    })
    
    client.execute_python('''
import bpy
import math

def get_principled_bsdf(mat):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

# 创建地板
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Stadium_Floor"

# 木地板材质
floor_mat = bpy.data.materials.new(name="Stadium_Wood")
floor_mat.use_nodes = True
bsdf = get_principled_bsdf(floor_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.6, 0.4, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.4
floor.data.materials.append(floor_mat)

# 创建看台（简化版）
for i in range(3):
    height = 0.5 + i * 0.3
    radius_inner = 8 + i * 1.5
    radius_outer = radius_inner + 1.0
    
    # 创建看台环
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius_outer,
        depth=0.3,
        location=(0, 0, height)
    )
    stand = bpy.context.active_object
    stand.name = f"Stadium_Stand_{i+1}"
    
    # 看台材质
    stand_mat = bpy.data.materials.new(name=f"Stand_Mat_{i+1}")
    stand_mat.use_nodes = True
    bsdf = get_principled_bsdf(stand_mat)
    # 法国国旗颜色 - 蓝白红
    colors = [(0.0, 0.15, 0.4, 1.0), (0.9, 0.9, 0.9, 1.0), (0.8, 0.1, 0.1, 1.0)]
    if bsdf:
        bsdf.inputs["Base Color"].default_value = colors[i % 3]
    stand.data.materials.append(stand_mat)

# 创建奥运五环标志（简化版）
ring_colors = [
    (0.0, 0.3, 0.7, 1.0),   # 蓝色
    (1.0, 0.8, 0.0, 1.0),   # 黄色
    (0.1, 0.1, 0.1, 1.0),   # 黑色
    (0.0, 0.6, 0.3, 1.0),   # 绿色
    (0.9, 0.1, 0.1, 1.0)    # 红色
]

ring_positions = [
    (-0.25, 0),
    (0.25, 0),
    (0, -0.15),
    (-0.25, -0.3),
    (0.25, -0.3)
]

for i, ((x, z), color) in enumerate(zip(ring_positions[:5], ring_colors)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.1,
        minor_radius=0.015,
        location=(x, -5, 2.5 + z)
    )
    ring = bpy.context.active_object
    ring.name = f"Olympic_Ring_{i+1}"
    
    ring_mat = bpy.data.materials.new(name=f"Ring_Color_{i+1}")
    ring_mat.use_nodes = True
    bsdf = get_principled_bsdf(ring_mat)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.3
    ring.data.materials.append(ring_mat)

# 创建巴黎2024标志文字
bpy.ops.object.text_add(location=(0, -5, 2.0))
text = bpy.context.active_object
text.data.body = "PARIS 2024"
text.data.size = 0.3
text.data.extrude = 0.02
text.name = "Paris_2024_Text"

# 文字材质
text_mat = bpy.data.materials.new(name="Text_Gold")
text_mat.use_nodes = True
bsdf = get_principled_bsdf(text_mat)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.1, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.2
text.data.materials.append(text_mat)

# 创建聚光灯
for angle in [0, 90, 180, 270]:
    x = 5 * math.cos(math.radians(angle))
    y = 5 * math.sin(math.radians(angle))
    
    bpy.ops.object.light_add(
        type='SPOT',
        radius=0.5,
        location=(x, y, 5)
    )
    light = bpy.context.active_object
    light.name = f"Stadium_Light_{angle}"
    light.data.energy = 500
    light.data.spot_size = math.radians(60)
    
    # 指向中心（使用正确的约束名称）
    try:
        constraint = light.constraints.new('TRACK_TO')
        # 创建空物体作为目标
        if "LightTarget" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
            target = bpy.context.active_object
            target.name = "LightTarget"
        else:
            target = bpy.data.objects["LightTarget"]
        constraint.target = target
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
    except Exception as e:
        print(f"约束设置跳过: {e}")

# 添加相机
bpy.ops.object.camera_add(location=(4, -4, 2))
camera = bpy.context.active_object
camera.name = "Scene_Camera"
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("巴黎奥运场景已创建")
''', "创建巴黎奥运会场景元素")


def position_character(client):
    """调整角色位置和姿势"""
    print("\n=== 调整角色位置 ===")
    
    client.execute_python('''
import bpy

# 移动樊振东到球台旁边
fan = bpy.data.objects.get("FanZhendong")
if fan:
    fan.location = (-0.8, 0, 0)
    fan.rotation_euler = (0, 0, 0)
    print(f"角色位置已调整: {fan.location}")
else:
    print("未找到角色 FanZhendong")

# 确保所有物体可见
for obj in bpy.data.objects:
    obj.hide_viewport = False
    obj.hide_render = False
''', "调整角色位置")


def add_lighting(client):
    """添加场景灯光"""
    print("\n=== 添加场景灯光 ===")
    
    client.cmd('lighting', 'create', {
        'light_type': 'SUN',
        'name': 'Main_Sun',
        'location': [5, 5, 10],
        'energy': 3.0
    })
    
    client.cmd('lighting', 'create', {
        'light_type': 'AREA',
        'name': 'Fill_Light',
        'location': [-3, -3, 5],
        'energy': 200.0
    })


def setup_render(client):
    """设置渲染参数"""
    print("\n=== 设置渲染参数 ===")
    
    client.cmd('render', 'settings', {
        'engine': 'CYCLES',
        'samples': 64,
        'resolution_x': 1920,
        'resolution_y': 1080
    })


def main():
    print("="*60)
    print("樊振东Q版人物 + 乒乓球场景 + 巴黎奥运")
    print("="*60)
    
    client = MCPClient()
    
    try:
        client.connect()
        
        # 1. 清空场景
        clear_scene(client)
        
        # 2. 创建巴黎奥运场景背景
        create_paris_olympics_scene(client)
        
        # 3. 创建乒乓球台
        create_ping_pong_table(client)
        
        # 4. 创建樊振东Q版角色
        create_fan_zhendong_character(client)
        
        # 5. 创建乒乓球拍
        create_ping_pong_paddle(client)
        
        # 6. 创建乒乓球
        create_ping_pong_ball(client)
        
        # 7. 调整位置
        position_character(client)
        
        # 8. 添加灯光
        add_lighting(client)
        
        # 9. 设置渲染
        setup_render(client)
        
        # 打印结果
        print("\n" + "="*60)
        print("创建完成!")
        print("="*60)
        
        passed = sum(1 for r in client.results if r['success'])
        failed = sum(1 for r in client.results if not r['success'])
        print(f"\n总计: {len(client.results)} | 成功: {passed} | 失败: {failed}")
        
        if failed > 0:
            print("\n失败的操作:")
            for r in client.results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['error']}")
        
        print("\n请在Blender中查看结果!")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
