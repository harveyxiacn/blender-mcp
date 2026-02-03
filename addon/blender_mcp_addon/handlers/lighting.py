"""
灯光处理器

处理灯光相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建灯光"""
    light_type = params.get("type", "POINT")
    name = params.get("name")
    location = params.get("location", [0, 0, 5])
    rotation = params.get("rotation", [0, 0, 0])
    color = params.get("color", [1, 1, 1])
    energy = params.get("energy", 1000.0)
    radius = params.get("radius", 0.25)
    
    # 创建灯光数据
    light_data = bpy.data.lights.new(name=name or light_type, type=light_type)
    light_data.color = color
    light_data.energy = energy
    
    # 设置特定属性
    if light_type in ['POINT', 'SPOT']:
        light_data.shadow_soft_size = radius
    elif light_type == 'AREA':
        light_data.size = radius * 4
    
    # 创建灯光对象
    light_obj = bpy.data.objects.new(name=name or light_type, object_data=light_data)
    light_obj.location = location
    light_obj.rotation_euler = rotation
    
    # 链接到场景
    bpy.context.collection.objects.link(light_obj)
    
    return {
        "success": True,
        "data": {
            "light_name": light_obj.name
        }
    }


def handle_set_properties(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置灯光属性"""
    light_name = params.get("light_name")
    properties = params.get("properties", {})
    
    obj = bpy.data.objects.get(light_name)
    if not obj or obj.type != 'LIGHT':
        return {
            "success": False,
            "error": {
                "code": "LIGHT_NOT_FOUND",
                "message": f"灯光不存在: {light_name}"
            }
        }
    
    light = obj.data
    
    if "color" in properties:
        light.color = properties["color"]
    
    if "energy" in properties:
        light.energy = properties["energy"]
    
    if "radius" in properties:
        if light.type in ['POINT', 'SPOT']:
            light.shadow_soft_size = properties["radius"]
        elif light.type == 'AREA':
            light.size = properties["radius"] * 4
    
    if "spot_size" in properties and light.type == 'SPOT':
        light.spot_size = properties["spot_size"]
    
    if "spot_blend" in properties and light.type == 'SPOT':
        light.spot_blend = properties["spot_blend"]
    
    if "shadow_soft_size" in properties:
        light.shadow_soft_size = properties["shadow_soft_size"]
    
    if "use_shadow" in properties:
        light.use_shadow = properties["use_shadow"]
    
    return {
        "success": True,
        "data": {}
    }


def handle_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除灯光"""
    light_name = params.get("light_name")
    
    obj = bpy.data.objects.get(light_name)
    if not obj or obj.type != 'LIGHT':
        return {
            "success": False,
            "error": {
                "code": "LIGHT_NOT_FOUND",
                "message": f"灯光不存在: {light_name}"
            }
        }
    
    light_data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.lights.remove(light_data)
    
    return {
        "success": True,
        "data": {}
    }


def handle_hdri_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置 HDRI 环境光"""
    hdri_path = params.get("hdri_path")
    strength = params.get("strength", 1.0)
    rotation = params.get("rotation", 0.0)
    
    # 获取或创建世界
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    # 清除现有节点
    nodes.clear()
    
    # 创建节点
    output = nodes.new(type='ShaderNodeOutputWorld')
    output.location = (300, 0)
    
    background = nodes.new(type='ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs["Strength"].default_value = strength
    
    env_tex = nodes.new(type='ShaderNodeTexEnvironment')
    env_tex.location = (-300, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-500, 0)
    mapping.inputs["Rotation"].default_value[2] = rotation
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-700, 0)
    
    # 加载 HDRI
    try:
        image = bpy.data.images.load(hdri_path)
        env_tex.image = image
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "IMAGE_LOAD_ERROR",
                "message": f"无法加载 HDRI: {e}"
            }
        }
    
    # 连接节点
    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], env_tex.inputs["Vector"])
    links.new(env_tex.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    
    return {
        "success": True,
        "data": {}
    }
