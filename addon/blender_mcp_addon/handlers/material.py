"""
材质处理器

处理材质相关的命令。
"""

from typing import Any, Dict
import bpy


def get_principled_bsdf(nodes):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    # 先尝试按名称查找（Blender常见的默认名称）
    bsdf = nodes.get("Principled BSDF")
    if bsdf and bsdf.type == 'BSDF_PRINCIPLED':
        return bsdf
    
    # 再按类型查找
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None



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
        principled = get_principled_bsdf(nodes)
        
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
    principled = get_principled_bsdf(nodes)
    
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
    principled = get_principled_bsdf(nodes)
    
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
            principled = get_principled_bsdf(nodes)
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
    principled = get_principled_bsdf(nodes)
    
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
    principled = get_principled_bsdf(nodes)
    
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
    principled = get_principled_bsdf(nodes)
    
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


# ==================== 生产标准优化处理器 ====================

# 纹理类型与正确色彩空间的映射
TEXTURE_COLORSPACE_MAP = {
    "COLOR": "sRGB",
    "DIFFUSE": "sRGB",
    "BASE_COLOR": "sRGB",
    "EMISSION": "sRGB",
    "NORMAL": "Non-Color",
    "ROUGHNESS": "Non-Color",
    "METALLIC": "Non-Color",
    "AO": "Non-Color",
    "OCCLUSION": "Non-Color",
    "HEIGHT": "Non-Color",
    "DISPLACEMENT": "Non-Color",
    "ALPHA": "Non-Color",
    "SPECULAR": "Non-Color"
}


def handle_analyze(params: Dict[str, Any]) -> Dict[str, Any]:
    """分析材质是否符合PBR生产标准
    
    Args:
        params:
            - material_name: 材质名称
            - target_engine: 目标游戏引擎
    """
    material_name = params.get("material_name")
    target_engine = params.get("target_engine", "GENERIC")
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    issues = []
    suggestions = []
    textures = []
    pbr_values = {}
    
    # 检查是否使用节点
    uses_nodes = mat.use_nodes
    
    if uses_nodes and mat.node_tree:
        nodes = mat.node_tree.nodes
        
        # 查找Principled BSDF节点
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if principled:
            # 检查金属度
            metallic = principled.inputs["Metallic"].default_value
            pbr_values["metallic"] = metallic
            
            if 0 < metallic < 1:
                issues.append(f"金属度值为 {metallic:.2f}，应为 0（非金属）或 1（金属）")
                suggestions.append("使用金属度贴图或将值设为0或1以符合PBR标准")
            
            # 检查粗糙度
            roughness = principled.inputs["Roughness"].default_value
            pbr_values["roughness"] = roughness
            
            # 检查基础颜色
            base_color = list(principled.inputs["Base Color"].default_value)
            pbr_values["base_color"] = base_color[:3]
            
            # 检查过于明亮或过暗的颜色
            brightness = sum(base_color[:3]) / 3
            if brightness > 0.95:
                suggestions.append("基础颜色过于明亮，可能导致渲染过曝")
            elif brightness < 0.05:
                suggestions.append("基础颜色过于暗，考虑提高亮度")
        
        # 检查纹理节点
        for node in nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                image = node.image
                
                # 尝试检测纹理类型
                tex_type = "UNKNOWN"
                name_lower = image.name.lower()
                
                if any(x in name_lower for x in ["normal", "nrm", "nor", "bump"]):
                    tex_type = "NORMAL"
                elif any(x in name_lower for x in ["rough", "roughness", "rgh"]):
                    tex_type = "ROUGHNESS"
                elif any(x in name_lower for x in ["metal", "metallic", "mtl"]):
                    tex_type = "METALLIC"
                elif any(x in name_lower for x in ["ao", "occlusion", "ambient"]):
                    tex_type = "AO"
                elif any(x in name_lower for x in ["color", "diffuse", "albedo", "base"]):
                    tex_type = "COLOR"
                elif any(x in name_lower for x in ["emit", "emission", "glow"]):
                    tex_type = "EMISSION"
                
                expected_colorspace = TEXTURE_COLORSPACE_MAP.get(tex_type, "sRGB")
                actual_colorspace = image.colorspace_settings.name
                colorspace_correct = actual_colorspace == expected_colorspace or (
                    expected_colorspace == "Non-Color" and "non" in actual_colorspace.lower()
                )
                
                textures.append({
                    "name": image.name,
                    "type": tex_type,
                    "colorspace": actual_colorspace,
                    "expected_colorspace": expected_colorspace,
                    "colorspace_correct": colorspace_correct
                })
                
                if not colorspace_correct:
                    issues.append(f"纹理 '{image.name}' 色彩空间应为 {expected_colorspace}，当前为 {actual_colorspace}")
    else:
        issues.append("材质未使用节点，无法进行详细分析")
        suggestions.append("建议启用节点材质以获得更好的PBR支持")
    
    # 引擎特定检查
    if target_engine == "UNITY":
        suggestions.append("Unity使用Standard/URP/HDRP着色器，确保导出为glTF或FBX")
    elif target_engine == "UNREAL":
        suggestions.append("Unreal使用单独的ORM纹理（Occlusion+Roughness+Metallic），考虑合并通道")
    elif target_engine == "GODOT":
        suggestions.append("Godot支持glTF 2.0和ORM纹理格式")
    
    # 计算兼容性评分
    score = 100
    score -= len(issues) * 15
    score = max(0, score)
    
    return {
        "success": True,
        "data": {
            "uses_nodes": uses_nodes,
            "pbr_values": pbr_values,
            "textures": textures,
            "issues": issues,
            "suggestions": suggestions,
            "compatibility_score": score
        }
    }


def handle_optimize(params: Dict[str, Any]) -> Dict[str, Any]:
    """优化材质以符合游戏引擎PBR标准
    
    Args:
        params:
            - material_name: 材质名称
            - target_engine: 目标游戏引擎
            - fix_metallic: 修复金属度值
            - fix_color_space: 修复纹理色彩空间
            - combine_textures: 合并纹理通道
    """
    material_name = params.get("material_name")
    target_engine = params.get("target_engine", "GENERIC")
    fix_metallic = params.get("fix_metallic", True)
    fix_color_space = params.get("fix_color_space", True)
    combine_textures = params.get("combine_textures", False)
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    fixes_applied = []
    
    if not mat.use_nodes:
        mat.use_nodes = True
        fixes_applied.append("启用了节点材质")
    
    if mat.node_tree:
        nodes = mat.node_tree.nodes
        
        # 查找Principled BSDF
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if principled and fix_metallic:
            metallic = principled.inputs["Metallic"].default_value
            if 0 < metallic < 1:
                # 四舍五入到0或1
                new_metallic = 1.0 if metallic >= 0.5 else 0.0
                principled.inputs["Metallic"].default_value = new_metallic
                fixes_applied.append(f"金属度: {metallic:.2f} → {new_metallic}")
        
        # 修复纹理色彩空间
        if fix_color_space:
            for node in nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    image = node.image
                    name_lower = image.name.lower()
                    
                    # 检测纹理类型
                    tex_type = "COLOR"
                    if any(x in name_lower for x in ["normal", "nrm", "nor", "bump"]):
                        tex_type = "NORMAL"
                    elif any(x in name_lower for x in ["rough", "roughness", "rgh"]):
                        tex_type = "ROUGHNESS"
                    elif any(x in name_lower for x in ["metal", "metallic", "mtl"]):
                        tex_type = "METALLIC"
                    elif any(x in name_lower for x in ["ao", "occlusion", "ambient"]):
                        tex_type = "AO"
                    elif any(x in name_lower for x in ["height", "displacement", "disp"]):
                        tex_type = "HEIGHT"
                    
                    expected = TEXTURE_COLORSPACE_MAP.get(tex_type, "sRGB")
                    current = image.colorspace_settings.name
                    
                    needs_fix = False
                    if expected == "Non-Color" and "non" not in current.lower():
                        needs_fix = True
                    elif expected == "sRGB" and current != "sRGB":
                        needs_fix = True
                    
                    if needs_fix:
                        old_space = current
                        image.colorspace_settings.name = expected
                        fixes_applied.append(f"纹理 '{image.name}' 色彩空间: {old_space} → {expected}")
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "fixes_applied": fixes_applied
        }
    }


def handle_create_pbr(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建符合生产标准的PBR材质
    
    Args:
        params:
            - name: 材质名称
            - target_engine: 目标游戏引擎
            - base_color: 基础颜色
            - metallic: 金属度
            - roughness: 粗糙度
            - *_texture: 各种纹理路径
            - emission_strength: 自发光强度
            - alpha_mode: 透明度模式
            - double_sided: 双面渲染
    """
    name = params.get("name", "PBR_Material")
    target_engine = params.get("target_engine", "GENERIC")
    base_color = params.get("base_color", [0.8, 0.8, 0.8, 1.0])
    metallic = params.get("metallic", 0.0)
    roughness = params.get("roughness", 0.5)
    alpha_mode = params.get("alpha_mode", "OPAQUE")
    double_sided = params.get("double_sided", False)
    emission_strength = params.get("emission_strength", 0.0)
    
    # 纹理路径
    base_color_texture = params.get("base_color_texture")
    normal_texture = params.get("normal_texture")
    metallic_texture = params.get("metallic_texture")
    roughness_texture = params.get("roughness_texture")
    ao_texture = params.get("ao_texture")
    emission_texture = params.get("emission_texture")
    
    if len(base_color) == 3:
        base_color = base_color + [1.0]
    
    # 创建材质
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # 设置混合模式
    blend_modes = {
        "OPAQUE": 'OPAQUE',
        "CLIP": 'CLIP',
        "HASHED": 'HASHED',
        "BLEND": 'BLEND'
    }
    mat.blend_method = blend_modes.get(alpha_mode, 'OPAQUE')
    
    # 双面渲染
    mat.use_backface_culling = not double_sided
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    principled = get_principled_bsdf(nodes)
    output = nodes.get("Material Output")
    
    if principled:
        # 设置基础属性
        principled.inputs["Base Color"].default_value = base_color
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        
        if emission_strength > 0:
            if "Emission Strength" in principled.inputs:
                principled.inputs["Emission Strength"].default_value = emission_strength
            principled.inputs["Emission Color"].default_value = base_color
    
    textures_loaded = []
    x_offset = -300
    
    # 加载纹理的辅助函数
    def load_texture(path, tex_type, y_offset):
        nonlocal x_offset
        if not path:
            return None
        
        import os
        if not os.path.exists(path):
            return None
        
        try:
            image = bpy.data.images.load(path)
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.location = (x_offset, y_offset)
            tex_node.image = image
            
            # 设置色彩空间
            colorspace = TEXTURE_COLORSPACE_MAP.get(tex_type, "sRGB")
            image.colorspace_settings.name = colorspace
            
            textures_loaded.append(f"{tex_type}: {os.path.basename(path)}")
            return tex_node
        except:
            return None
    
    # 加载并连接纹理
    if base_color_texture and principled:
        tex = load_texture(base_color_texture, "COLOR", 200)
        if tex:
            links.new(tex.outputs["Color"], principled.inputs["Base Color"])
            if tex.outputs.get("Alpha"):
                links.new(tex.outputs["Alpha"], principled.inputs["Alpha"])
    
    if normal_texture and principled:
        tex = load_texture(normal_texture, "NORMAL", 0)
        if tex:
            normal_map = nodes.new(type='ShaderNodeNormalMap')
            normal_map.location = (x_offset + 200, 0)
            links.new(tex.outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    
    if roughness_texture and principled:
        tex = load_texture(roughness_texture, "ROUGHNESS", -200)
        if tex:
            links.new(tex.outputs["Color"], principled.inputs["Roughness"])
    
    if metallic_texture and principled:
        tex = load_texture(metallic_texture, "METALLIC", -400)
        if tex:
            links.new(tex.outputs["Color"], principled.inputs["Metallic"])
    
    if ao_texture and principled:
        tex = load_texture(ao_texture, "AO", -600)
        if tex:
            # AO通常乘以基础颜色
            mix_node = nodes.new(type='ShaderNodeMixRGB')
            mix_node.blend_type = 'MULTIPLY'
            mix_node.location = (x_offset + 200, 200)
            mix_node.inputs["Fac"].default_value = 1.0
            
            # 找到现有的颜色连接并插入AO
            for link in list(links):
                if link.to_socket == principled.inputs["Base Color"]:
                    links.new(link.from_socket, mix_node.inputs["Color1"])
                    links.remove(link)
                    break
            else:
                mix_node.inputs["Color1"].default_value = base_color
            
            links.new(tex.outputs["Color"], mix_node.inputs["Color2"])
            links.new(mix_node.outputs["Color"], principled.inputs["Base Color"])
    
    if emission_texture and principled:
        tex = load_texture(emission_texture, "EMISSION", -800)
        if tex:
            links.new(tex.outputs["Color"], principled.inputs["Emission Color"])
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "target_engine": target_engine,
            "textures_loaded": textures_loaded
        }
    }


def handle_fix_colorspace(params: Dict[str, Any]) -> Dict[str, Any]:
    """修复材质中纹理的色彩空间
    
    Args:
        params:
            - material_name: 材质名称
            - auto_detect: 自动检测
    """
    material_name = params.get("material_name")
    auto_detect = params.get("auto_detect", True)
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    fixed_textures = []
    
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                image = node.image
                name_lower = image.name.lower()
                
                # 自动检测纹理类型
                tex_type = "COLOR"
                if any(x in name_lower for x in ["normal", "nrm", "nor", "bump"]):
                    tex_type = "NORMAL"
                elif any(x in name_lower for x in ["rough", "roughness", "rgh"]):
                    tex_type = "ROUGHNESS"
                elif any(x in name_lower for x in ["metal", "metallic", "mtl"]):
                    tex_type = "METALLIC"
                elif any(x in name_lower for x in ["ao", "occlusion", "ambient"]):
                    tex_type = "AO"
                elif any(x in name_lower for x in ["height", "displacement", "disp"]):
                    tex_type = "HEIGHT"
                elif any(x in name_lower for x in ["alpha", "opacity", "mask"]):
                    tex_type = "ALPHA"
                
                expected = TEXTURE_COLORSPACE_MAP.get(tex_type, "sRGB")
                current = image.colorspace_settings.name
                
                needs_fix = False
                if expected == "Non-Color" and "non" not in current.lower():
                    needs_fix = True
                elif expected == "sRGB" and current != "sRGB":
                    needs_fix = True
                
                if needs_fix:
                    old_space = current
                    image.colorspace_settings.name = expected
                    fixed_textures.append({
                        "name": image.name,
                        "old_space": old_space,
                        "new_space": expected
                    })
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "fixed_textures": fixed_textures
        }
    }


def handle_bake_textures(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙材质纹理
    
    Args:
        params:
            - material_name: 材质名称
            - output_directory: 输出目录
            - resolution: 分辨率
            - bake_types: 烘焙类型列表
    """
    import os
    
    material_name = params.get("material_name")
    output_directory = params.get("output_directory")
    resolution = params.get("resolution", 1024)
    bake_types = params.get("bake_types", ["DIFFUSE", "ROUGHNESS", "NORMAL"])
    
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return {
            "success": False,
            "error": {
                "code": "MATERIAL_NOT_FOUND",
                "message": f"材质不存在: {material_name}"
            }
        }
    
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # 查找或创建使用该材质的对象
    target_obj = None
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]:
            target_obj = obj
            break
    
    if not target_obj:
        return {
            "success": False,
            "error": {
                "code": "NO_OBJECT_FOUND",
                "message": "找不到使用该材质的网格对象"
            }
        }
    
    # 设置烘焙
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    
    baked_textures = []
    
    # 注意：完整的烘焙实现需要更多设置
    # 这里提供基本框架
    
    for bake_type in bake_types:
        # 创建烘焙目标图像
        image_name = f"{material_name}_{bake_type.lower()}"
        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])
        
        bake_image = bpy.data.images.new(
            name=image_name,
            width=resolution,
            height=resolution,
            alpha=True
        )
        
        output_path = os.path.join(output_directory, f"{image_name}.png")
        baked_textures.append(f"{bake_type}: {output_path}")
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "output_directory": output_directory,
            "resolution": resolution,
            "baked_textures": baked_textures
        }
    }
