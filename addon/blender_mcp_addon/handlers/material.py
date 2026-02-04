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


def handle_node_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加材质节点
    
    Args:
        params:
            - material_name: 材质名称
            - node_type: 节点类型
                - SSS: 次表面散射节点配置
                - EMISSION: 发光节点
                - MIX_RGB: 混合 RGB
                - COLOR_RAMP: 颜色渐变
                - NOISE_TEXTURE: 噪波纹理
                - IMAGE_TEXTURE: 图像纹理
                - NORMAL_MAP: 法线贴图
                - BUMP: 凹凸贴图
            - settings: 节点设置
            - connect_to: 连接到的节点输入
    """
    material_name = params.get("material_name")
    node_type = params.get("node_type")
    settings = params.get("settings", {})
    connect_to = params.get("connect_to")
    location = params.get("location", [-300, 0])
    
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
    
    try:
        # 根据节点类型创建和配置节点
        if node_type == "SSS":
            # 配置 Principled BSDF 的次表面散射
            if principled:
                subsurface = settings.get("subsurface", 0.3)
                subsurface_color = settings.get("subsurface_color", [0.8, 0.2, 0.1])
                subsurface_radius = settings.get("subsurface_radius", [1.0, 0.2, 0.1])
                
                # Blender 4.0+ 使用不同的 SSS 接口
                if "Subsurface Weight" in principled.inputs:
                    principled.inputs["Subsurface Weight"].default_value = subsurface
                elif "Subsurface" in principled.inputs:
                    principled.inputs["Subsurface"].default_value = subsurface
                
                if "Subsurface Radius" in principled.inputs:
                    principled.inputs["Subsurface Radius"].default_value = subsurface_radius
                
                return {
                    "success": True,
                    "data": {
                        "node_type": "SSS",
                        "subsurface": subsurface
                    }
                }
        
        elif node_type == "EMISSION":
            # 配置发光
            if principled:
                emission_color = settings.get("color", [1.0, 1.0, 1.0, 1.0])
                emission_strength = settings.get("strength", 1.0)
                
                if len(emission_color) == 3:
                    emission_color = emission_color + [1.0]
                
                principled.inputs["Emission Color"].default_value = emission_color
                principled.inputs["Emission Strength"].default_value = emission_strength
                
                return {
                    "success": True,
                    "data": {
                        "node_type": "EMISSION",
                        "strength": emission_strength
                    }
                }
        
        elif node_type == "MIX_RGB":
            node = nodes.new(type='ShaderNodeMixRGB')
            node.location = location
            node.blend_type = settings.get("blend_type", "MIX")
            node.inputs["Fac"].default_value = settings.get("fac", 0.5)
        
        elif node_type == "COLOR_RAMP":
            node = nodes.new(type='ShaderNodeValToRGB')
            node.location = location
            # 设置颜色停点
            stops = settings.get("stops", [])
            for i, stop in enumerate(stops):
                if i < len(node.color_ramp.elements):
                    elem = node.color_ramp.elements[i]
                else:
                    elem = node.color_ramp.elements.new(stop.get("position", 0.5))
                elem.position = stop.get("position", i / max(len(stops) - 1, 1))
                elem.color = stop.get("color", [1, 1, 1, 1])
        
        elif node_type == "NOISE_TEXTURE":
            node = nodes.new(type='ShaderNodeTexNoise')
            node.location = location
            node.inputs["Scale"].default_value = settings.get("scale", 5.0)
            node.inputs["Detail"].default_value = settings.get("detail", 2.0)
            node.inputs["Roughness"].default_value = settings.get("roughness", 0.5)
        
        elif node_type == "IMAGE_TEXTURE":
            node = nodes.new(type='ShaderNodeTexImage')
            node.location = location
            image_path = settings.get("image_path")
            if image_path:
                try:
                    image = bpy.data.images.load(image_path)
                    node.image = image
                except:
                    pass
        
        elif node_type == "NORMAL_MAP":
            node = nodes.new(type='ShaderNodeNormalMap')
            node.location = location
            node.space = settings.get("space", "TANGENT")
            node.inputs["Strength"].default_value = settings.get("strength", 1.0)
        
        elif node_type == "BUMP":
            node = nodes.new(type='ShaderNodeBump')
            node.location = location
            node.inputs["Strength"].default_value = settings.get("strength", 1.0)
            node.inputs["Distance"].default_value = settings.get("distance", 0.1)
        
        else:
            # 尝试创建通用节点
            try:
                node = nodes.new(type=node_type)
                node.location = location
            except:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_NODE_TYPE",
                        "message": f"不支持的节点类型: {node_type}"
                    }
                }
        
        # 连接节点
        if connect_to and principled:
            if node_type not in ["SSS", "EMISSION"]:
                target_input = connect_to.get("input", "Base Color")
                output_socket = connect_to.get("output", "Color")
                
                if target_input in principled.inputs and hasattr(node.outputs, output_socket) or output_socket in [o.name for o in node.outputs]:
                    out_socket = node.outputs.get(output_socket) or node.outputs[0]
                    links.new(out_socket, principled.inputs[target_input])
        
        return {
            "success": True,
            "data": {
                "node_type": node_type,
                "node_name": node.name if 'node' in dir() else "N/A"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "NODE_ADD_ERROR",
                "message": str(e)
            }
        }


def handle_texture_apply(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用纹理贴图
    
    Args:
        params:
            - material_name: 材质名称
            - image_path: 图片文件路径
            - mapping_type: 映射类型
                - UV: UV 映射（默认）
                - BOX: 盒式映射
                - FLAT: 平面映射
                - SPHERE: 球形映射
            - texture_type: 纹理用途
                - COLOR: 颜色贴图
                - NORMAL: 法线贴图
                - ROUGHNESS: 粗糙度贴图
                - METALLIC: 金属度贴图
                - EMISSION: 发光贴图
                - ALPHA: 透明度贴图
    """
    material_name = params.get("material_name")
    image_path = params.get("image_path")
    mapping_type = params.get("mapping_type", "UV")
    texture_type = params.get("texture_type", "COLOR")
    
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
        image = bpy.data.images.load(image_path)
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
    tex_node.location = (-600, 0)
    
    # 创建纹理坐标和映射节点
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-1000, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-800, 0)
    
    # 连接纹理坐标
    coord_output = "UV" if mapping_type == "UV" else "Generated"
    if mapping_type == "BOX":
        coord_output = "Object"
    
    links.new(tex_coord.outputs[coord_output], mapping.outputs["Vector"])
    links.new(mapping.outputs["Vector"], tex_node.inputs["Vector"])
    
    # 根据纹理类型连接到对应输入
    input_map = {
        "COLOR": "Base Color",
        "NORMAL": None,  # 需要法线贴图节点
        "ROUGHNESS": "Roughness",
        "METALLIC": "Metallic",
        "EMISSION": "Emission Color",
        "ALPHA": "Alpha"
    }
    
    target_input = input_map.get(texture_type)
    
    if texture_type == "NORMAL":
        # 创建法线贴图节点
        normal_node = nodes.new(type='ShaderNodeNormalMap')
        normal_node.location = (-400, 0)
        links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
        links.new(normal_node.outputs["Normal"], principled.inputs["Normal"])
        image.colorspace_settings.name = 'Non-Color'
    elif target_input:
        links.new(tex_node.outputs["Color"], principled.inputs[target_input])
        if texture_type not in ["COLOR", "EMISSION"]:
            image.colorspace_settings.name = 'Non-Color'
        
        # 处理透明度
        if texture_type == "ALPHA":
            mat.blend_method = 'BLEND'
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "image_name": image.name,
            "texture_type": texture_type,
            "mapping_type": mapping_type
        }
    }


def handle_create_skin_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建皮肤材质
    
    预设的皮肤材质，包含 SSS 和适当的粗糙度设置。
    
    Args:
        params:
            - name: 材质名称
            - skin_tone: 肤色类型 (LIGHT, MEDIUM, DARK, CUSTOM)
            - custom_color: 自定义颜色（当 skin_tone 为 CUSTOM 时）
    """
    name = params.get("name", "SkinMaterial")
    skin_tone = params.get("skin_tone", "MEDIUM")
    custom_color = params.get("custom_color")
    
    # 预设肤色
    skin_colors = {
        "LIGHT": [0.95, 0.85, 0.75, 1.0],
        "MEDIUM": [0.87, 0.70, 0.55, 1.0],
        "DARK": [0.45, 0.30, 0.20, 1.0]
    }
    
    color = custom_color if skin_tone == "CUSTOM" and custom_color else skin_colors.get(skin_tone, skin_colors["MEDIUM"])
    if len(color) == 3:
        color = color + [1.0]
    
    # 创建材质
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    if principled:
        # 基础颜色
        principled.inputs["Base Color"].default_value = color
        
        # SSS 设置
        if "Subsurface Weight" in principled.inputs:
            principled.inputs["Subsurface Weight"].default_value = 0.3
        elif "Subsurface" in principled.inputs:
            principled.inputs["Subsurface"].default_value = 0.3
        
        if "Subsurface Radius" in principled.inputs:
            # 红色光散射最多，蓝色最少
            principled.inputs["Subsurface Radius"].default_value = [1.0, 0.2, 0.1]
        
        # 粗糙度
        principled.inputs["Roughness"].default_value = 0.4
        
        # 镜面反射
        if "Specular IOR Level" in principled.inputs:
            principled.inputs["Specular IOR Level"].default_value = 0.5
        elif "Specular" in principled.inputs:
            principled.inputs["Specular"].default_value = 0.5
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "skin_tone": skin_tone,
            "color": color[:3]
        }
    }


def handle_create_toon_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建卡通材质
    
    适用于 Q 版角色的风格化卡通材质。
    
    Args:
        params:
            - name: 材质名称
            - color: 基础颜色
            - shadow_color: 阴影颜色（可选）
            - outline: 是否添加描边效果
    """
    name = params.get("name", "ToonMaterial")
    color = params.get("color", [0.8, 0.8, 0.8, 1.0])
    shadow_color = params.get("shadow_color")
    outline = params.get("outline", False)
    
    if len(color) == 3:
        color = color + [1.0]
    
    # 创建材质
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默认节点
    for node in nodes:
        nodes.remove(node)
    
    # 创建输出节点
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # 创建 Principled BSDF（简化的卡通效果）
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (100, 0)
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.9  # 高粗糙度减少高光
    principled.inputs["Metallic"].default_value = 0.0
    
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.1
    elif "Specular" in principled.inputs:
        principled.inputs["Specular"].default_value = 0.1
    
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    
    # 如果需要描边，设置背面剔除
    if outline:
        mat.use_backface_culling = True
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "color": color[:3]
        }
    }
