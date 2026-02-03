"""
材质处理器

处理材质相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建材质"""
    name = params.get("name", "Material")
    color = params.get("color", [0.8, 0.8, 0.8, 1.0])
    metallic = params.get("metallic", 0.0)
    roughness = params.get("roughness", 0.5)
    use_nodes = params.get("use_nodes", True)
    
    # 创建材质
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = use_nodes
    
    if use_nodes:
        # 获取 Principled BSDF 节点
        nodes = mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        
        if principled:
            # 设置颜色
            if len(color) == 3:
                color = color + [1.0]
            principled.inputs["Base Color"].default_value = color
            
            # 设置金属度和粗糙度
            principled.inputs["Metallic"].default_value = metallic
            principled.inputs["Roughness"].default_value = roughness
    else:
        mat.diffuse_color = color
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name
        }
    }


def handle_assign(params: Dict[str, Any]) -> Dict[str, Any]:
    """分配材质"""
    object_name = params.get("object_name")
    material_name = params.get("material_name")
    slot_index = params.get("slot_index", 0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    # 确保有足够的材质槽
    while len(obj.material_slots) <= slot_index:
        obj.data.materials.append(None)
    
    # 分配材质
    obj.material_slots[slot_index].material = mat
    
    return {
        "success": True,
        "data": {}
    }


def handle_set_properties(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置材质属性"""
    material_name = params.get("material_name")
    properties = params.get("properties", {})
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    if not mat.use_nodes:
        mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    if not principled:
        return {
            "success": False,
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "找不到 Principled BSDF 节点"
            }
        }
    
    # 设置属性
    if "color" in properties:
        color = properties["color"]
        if len(color) == 3:
            color = color + [1.0]
        principled.inputs["Base Color"].default_value = color
    
    if "metallic" in properties:
        principled.inputs["Metallic"].default_value = properties["metallic"]
    
    if "roughness" in properties:
        principled.inputs["Roughness"].default_value = properties["roughness"]
    
    if "specular" in properties:
        # Blender 4.0+ 使用 Specular IOR Level
        if "Specular IOR Level" in principled.inputs:
            principled.inputs["Specular IOR Level"].default_value = properties["specular"]
        elif "Specular" in principled.inputs:
            principled.inputs["Specular"].default_value = properties["specular"]
    
    if "emission_color" in properties:
        emission = properties["emission_color"]
        if len(emission) == 3:
            emission = emission + [1.0]
        principled.inputs["Emission Color"].default_value = emission
    
    if "emission_strength" in properties:
        principled.inputs["Emission Strength"].default_value = properties["emission_strength"]
    
    if "alpha" in properties:
        principled.inputs["Alpha"].default_value = properties["alpha"]
        mat.blend_method = 'BLEND' if properties["alpha"] < 1.0 else 'OPAQUE'
    
    if "blend_mode" in properties:
        mat.blend_method = properties["blend_mode"]
    
    return {
        "success": True,
        "data": {}
    }


def handle_add_texture(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加纹理"""
    material_name = params.get("material_name")
    texture_path = params.get("texture_path")
    texture_type = params.get("texture_type", "COLOR")
    mapping = params.get("mapping", "UV")
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    if not mat.use_nodes:
        mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    
    if not principled:
        return {
            "success": False,
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "找不到 Principled BSDF 节点"
            }
        }
    
    # 加载图像
    try:
        image = bpy.data.images.load(texture_path)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "IMAGE_LOAD_ERROR",
                "message": f"无法加载图像: {e}"
            }
        }
    
    # 创建图像纹理节点
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = image
    tex_node.location = (-400, 0)
    
    # 连接到对应输入
    input_map = {
        "COLOR": "Base Color",
        "NORMAL": None,  # 需要法线贴图节点
        "ROUGHNESS": "Roughness",
        "METALLIC": "Metallic",
        "EMISSION": "Emission Color"
    }
    
    target_input = input_map.get(texture_type)
    
    if texture_type == "NORMAL":
        # 创建法线贴图节点
        normal_node = nodes.new(type='ShaderNodeNormalMap')
        normal_node.location = (-200, 0)
        links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
        links.new(normal_node.outputs["Normal"], principled.inputs["Normal"])
        image.colorspace_settings.name = 'Non-Color'
    elif target_input:
        links.new(tex_node.outputs["Color"], principled.inputs[target_input])
        if texture_type != "COLOR":
            image.colorspace_settings.name = 'Non-Color'
    
    return {
        "success": True,
        "data": {}
    }


def handle_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出材质"""
    limit = params.get("limit", 50)
    
    materials = []
    for mat in bpy.data.materials[:limit]:
        mat_info = {"name": mat.name}
        
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            principled = nodes.get("Principled BSDF")
            if principled:
                mat_info["color"] = list(principled.inputs["Base Color"].default_value)
                mat_info["metallic"] = principled.inputs["Metallic"].default_value
                mat_info["roughness"] = principled.inputs["Roughness"].default_value
        
        materials.append(mat_info)
    
    return {
        "success": True,
        "data": {
            "materials": materials,
            "total": len(bpy.data.materials)
        }
    }


def handle_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除材质"""
    material_name = params.get("material_name")
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    bpy.data.materials.remove(mat)
    
    return {
        "success": True,
        "data": {}
    }
