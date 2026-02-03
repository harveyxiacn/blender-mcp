"""
角色处理器

处理角色相关的命令。
"""

from typing import Any, Dict
import bpy
import bmesh


def handle_create_humanoid(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建人形角色"""
    name = params.get("name", "Character")
    height = params.get("height", 1.8)
    body_type = params.get("body_type", "AVERAGE")
    gender = params.get("gender", "NEUTRAL")
    subdivisions = params.get("subdivisions", 2)
    
    # 体型参数
    body_params = {
        "SLIM": {"width": 0.8, "depth": 0.7},
        "AVERAGE": {"width": 1.0, "depth": 1.0},
        "MUSCULAR": {"width": 1.2, "depth": 1.1},
        "HEAVY": {"width": 1.3, "depth": 1.3}
    }
    
    bp = body_params.get(body_type, body_params["AVERAGE"])
    scale = height / 1.8  # 标准化到 1.8m
    
    # 创建基础网格
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height / 2))
    body = bpy.context.active_object
    body.name = name
    
    # 缩放到合适的身体比例
    body.scale = (0.35 * bp["width"] * scale, 0.2 * bp["depth"] * scale, height)
    
    # 应用缩放
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 添加细分修改器
    if subdivisions > 0:
        mod = body.modifiers.new(name="Subdivision", type='SUBSURF')
        mod.levels = subdivisions
        mod.render_levels = subdivisions
    
    # 添加平滑修改器
    mod_smooth = body.modifiers.new(name="Smooth", type='SMOOTH')
    mod_smooth.factor = 0.5
    mod_smooth.iterations = 2
    
    return {
        "success": True,
        "data": {
            "character_name": body.name,
            "height": height,
            "body_type": body_type
        }
    }


def handle_add_face_features(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加面部特征"""
    character_name = params.get("character_name")
    eye_size = params.get("eye_size", 1.0)
    nose_length = params.get("nose_length", 1.0)
    mouth_width = params.get("mouth_width", 1.0)
    jaw_width = params.get("jaw_width", 1.0)
    
    obj = bpy.data.objects.get(character_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"角色不存在: {character_name}"
            }
        }
    
    # 注意：这是一个简化实现
    # 完整实现需要使用形态键或顶点组来调整面部特征
    
    # 存储面部参数作为自定义属性
    obj["face_eye_size"] = eye_size
    obj["face_nose_length"] = nose_length
    obj["face_mouth_width"] = mouth_width
    obj["face_jaw_width"] = jaw_width
    
    return {
        "success": True,
        "data": {}
    }


def handle_add_hair(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加头发"""
    character_name = params.get("character_name")
    hair_style = params.get("hair_style", "SHORT")
    hair_color = params.get("hair_color", [0.1, 0.08, 0.05])
    use_particles = params.get("use_particles", True)
    
    obj = bpy.data.objects.get(character_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"角色不存在: {character_name}"
            }
        }
    
    if use_particles:
        # 创建粒子系统
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.particle_system_add()
        
        ps = obj.particle_systems[-1]
        ps.name = "Hair"
        
        settings = ps.settings
        settings.type = 'HAIR'
        
        # 根据发型设置长度
        length_map = {
            "BALD": 0.0,
            "SHORT": 0.05,
            "MEDIUM": 0.15,
            "LONG": 0.3
        }
        settings.hair_length = length_map.get(hair_style, 0.1)
        settings.count = 5000 if hair_style != "BALD" else 0
        
        # 创建头发材质
        hair_mat = bpy.data.materials.new(name=f"{character_name}_Hair")
        hair_mat.use_nodes = True
        nodes = hair_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            principled.inputs["Base Color"].default_value = hair_color + [1.0]
        
        # 应用材质
        settings.material = len(obj.material_slots)
        obj.data.materials.append(hair_mat)
    
    return {
        "success": True,
        "data": {}
    }


def handle_add_clothing(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加服装"""
    character_name = params.get("character_name")
    clothing_type = params.get("clothing_type")
    color = params.get("color", [0.5, 0.5, 0.5])
    
    obj = bpy.data.objects.get(character_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"角色不存在: {character_name}"
            }
        }
    
    # 简化实现：复制角色网格并缩放作为服装
    # 完整实现需要独立的服装网格和布料模拟
    
    # 复制角色网格
    clothing = obj.copy()
    clothing.data = obj.data.copy()
    clothing.name = f"{character_name}_{clothing_type}"
    
    # 稍微放大作为服装
    clothing.scale = (1.05, 1.05, 1.02)
    
    # 链接到场景
    bpy.context.collection.objects.link(clothing)
    
    # 设为角色的子对象
    clothing.parent = obj
    
    # 创建服装材质
    cloth_mat = bpy.data.materials.new(name=f"{clothing_type}_Material")
    cloth_mat.use_nodes = True
    nodes = cloth_mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color + [1.0]
        principled.inputs["Roughness"].default_value = 0.8
    
    # 应用材质
    if clothing.data.materials:
        clothing.data.materials[0] = cloth_mat
    else:
        clothing.data.materials.append(cloth_mat)
    
    return {
        "success": True,
        "data": {
            "clothing_name": clothing.name
        }
    }
