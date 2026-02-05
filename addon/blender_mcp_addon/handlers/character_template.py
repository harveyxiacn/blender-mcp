"""
角色模板处理器

处理角色模板创建、面部表情、服装、发型等命令。
"""

from typing import Any, Dict, List
import bpy


def get_principled_bsdf(nodes):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    # 先尝试按名称查找
    bsdf = get_principled_bsdf(nodes)
    if bsdf:
        return bsdf
    # 再按类型查找
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

import math


# ==================== 模板配置 ====================

TEMPLATE_CONFIG = {
    "chibi": {
        "head_scale": [1.0, 1.0, 1.1],
        "body_scale": [0.6, 0.4, 0.7],
        "head_body_ratio": 2.5,
        "eye_size": 1.5,
        "limb_thickness": 0.15
    },
    "realistic": {
        "head_scale": [0.5, 0.5, 0.6],
        "body_scale": [0.8, 0.5, 1.2],
        "head_body_ratio": 7.5,
        "eye_size": 0.8,
        "limb_thickness": 0.12
    },
    "anime": {
        "head_scale": [0.7, 0.7, 0.8],
        "body_scale": [0.7, 0.45, 1.0],
        "head_body_ratio": 5.5,
        "eye_size": 1.3,
        "limb_thickness": 0.1
    },
    "stylized": {
        "head_scale": [0.8, 0.8, 0.9],
        "body_scale": [0.65, 0.45, 0.85],
        "head_body_ratio": 4.0,
        "eye_size": 1.2,
        "limb_thickness": 0.12
    },
    "mascot": {
        "head_scale": [1.2, 1.2, 1.3],
        "body_scale": [0.8, 0.6, 0.6],
        "head_body_ratio": 2.0,
        "eye_size": 1.8,
        "limb_thickness": 0.2
    }
}

SKIN_COLORS = {
    "light": [1.0, 0.9, 0.8, 1.0],
    "medium": [0.9, 0.75, 0.6, 1.0],
    "tan": [0.8, 0.6, 0.45, 1.0],
    "dark": [0.5, 0.35, 0.25, 1.0]
}

EXPRESSION_CONFIG = {
    "neutral": {"eye_scale": 1.0, "mouth_curve": 0, "eyebrow_angle": 0},
    "happy": {"eye_scale": 0.8, "mouth_curve": 0.3, "eyebrow_angle": 0.1},
    "sad": {"eye_scale": 1.0, "mouth_curve": -0.2, "eyebrow_angle": -0.2},
    "angry": {"eye_scale": 0.9, "mouth_curve": -0.1, "eyebrow_angle": -0.3},
    "surprised": {"eye_scale": 1.3, "mouth_curve": 0, "eyebrow_angle": 0.3},
    "wink": {"eye_scale": 0.7, "mouth_curve": 0.2, "eyebrow_angle": 0.1},
    "smile": {"eye_scale": 0.85, "mouth_curve": 0.25, "eyebrow_angle": 0.05}
}


def _create_material(name: str, color: List[float], metallic: float = 0.0, roughness: float = 0.5):
    """创建材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    bsdf = get_principled_bsdf(mat.node_tree.nodes)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    
    return mat


def _assign_material(obj, material):
    """为对象分配材质"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """从模板创建角色"""
    template = params.get("template", "chibi")
    name = params.get("name", "Character")
    height = params.get("height", 1.7)
    location = params.get("location", [0, 0, 0])
    skin_color = params.get("skin_color") or SKIN_COLORS["light"]
    gender = params.get("gender", "neutral")
    
    config = TEMPLATE_CONFIG.get(template, TEMPLATE_CONFIG["chibi"])
    
    # 计算缩放系数
    scale_factor = height / 1.7
    
    created_parts = []
    
    # 创建皮肤材质
    skin_mat = _create_material(f"{name}_Skin", skin_color, roughness=0.8)
    
    # ========== 头部 ==========
    head_z = location[2] + height * (1 - 1/config["head_body_ratio"])
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.25 * scale_factor * config["head_scale"][0],
        location=[location[0], location[1], head_z]
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.scale = [
        config["head_scale"][0],
        config["head_scale"][1],
        config["head_scale"][2]
    ]
    _assign_material(head, skin_mat)
    created_parts.append(head.name)
    
    # ========== 身体 ==========
    body_z = location[2] + height * 0.4
    bpy.ops.mesh.primitive_cube_add(location=[location[0], location[1], body_z])
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = [
        config["body_scale"][0] * scale_factor * 0.3,
        config["body_scale"][1] * scale_factor * 0.2,
        config["body_scale"][2] * scale_factor * 0.35
    ]
    _assign_material(body, skin_mat)
    created_parts.append(body.name)
    
    # ========== 眼睛 ==========
    eye_mat = _create_material(f"{name}_Eye", [0.05, 0.02, 0.0, 1.0], roughness=0.3)
    eye_highlight_mat = _create_material(f"{name}_EyeHighlight", [1.0, 1.0, 1.0, 1.0], roughness=0.2)
    
    eye_size = 0.05 * scale_factor * config["eye_size"]
    eye_spacing = 0.08 * scale_factor
    eye_y = -0.15 * scale_factor
    eye_z = head_z + 0.02 * scale_factor
    
    for side, x_offset in [("L", -eye_spacing), ("R", eye_spacing)]:
        # 眼球
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=eye_size,
            location=[location[0] + x_offset, location[1] + eye_y, eye_z]
        )
        eye = bpy.context.active_object
        eye.name = f"{name}_Eye_{side}"
        eye.scale = [1.0, 0.7, 1.0]
        _assign_material(eye, eye_mat)
        created_parts.append(eye.name)
        
        # 高光
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=eye_size * 0.25,
            location=[location[0] + x_offset + eye_size * 0.3, location[1] + eye_y - eye_size * 0.3, eye_z + eye_size * 0.3]
        )
        highlight = bpy.context.active_object
        highlight.name = f"{name}_EyeHighlight_{side}"
        _assign_material(highlight, eye_highlight_mat)
        created_parts.append(highlight.name)
    
    # ========== 手臂 ==========
    arm_mat = skin_mat
    arm_length = height * 0.25
    arm_y = body_z
    
    for side, x_offset, rotation in [("L", -0.2 * scale_factor, 0.3), ("R", 0.2 * scale_factor, -0.3)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=config["limb_thickness"] * scale_factor * 0.5,
            depth=arm_length,
            location=[location[0] + x_offset, location[1], arm_y]
        )
        arm = bpy.context.active_object
        arm.name = f"{name}_Arm_{side}"
        arm.rotation_euler = [0, rotation, 0]
        _assign_material(arm, arm_mat)
        created_parts.append(arm.name)
        
        # 手
        hand_x = location[0] + x_offset + (0.15 if side == "R" else -0.15) * scale_factor
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=config["limb_thickness"] * scale_factor * 0.6,
            location=[hand_x, location[1], arm_y - arm_length * 0.3]
        )
        hand = bpy.context.active_object
        hand.name = f"{name}_Hand_{side}"
        _assign_material(hand, skin_mat)
        created_parts.append(hand.name)
    
    # ========== 腿部 ==========
    leg_length = height * 0.3
    leg_z = location[2] + leg_length * 0.5
    
    for side, x_offset in [("L", -0.08 * scale_factor), ("R", 0.08 * scale_factor)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=config["limb_thickness"] * scale_factor * 0.6,
            depth=leg_length,
            location=[location[0] + x_offset, location[1], leg_z]
        )
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg_{side}"
        _assign_material(leg, skin_mat)
        created_parts.append(leg.name)
        
        # 脚
        bpy.ops.mesh.primitive_cube_add(
            location=[location[0] + x_offset, location[1] - 0.03 * scale_factor, location[2] + 0.03 * scale_factor]
        )
        foot = bpy.context.active_object
        foot.name = f"{name}_Foot_{side}"
        foot.scale = [0.05 * scale_factor, 0.08 * scale_factor, 0.03 * scale_factor]
        _assign_material(foot, skin_mat)
        created_parts.append(foot.name)
    
    return {
        "success": True,
        "data": {
            "character_name": name,
            "template": template,
            "parts_created": len(created_parts),
            "parts": created_parts
        }
    }


def handle_face_expression(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置面部表情"""
    character_name = params.get("character_name")
    expression = params.get("expression", "neutral")
    intensity = params.get("intensity", 1.0)
    
    config = EXPRESSION_CONFIG.get(expression, EXPRESSION_CONFIG["neutral"])
    
    # 调整眼睛
    for side in ["L", "R"]:
        eye = bpy.data.objects.get(f"{character_name}_Eye_{side}")
        if eye:
            base_scale = eye.scale.copy()
            eye.scale[2] = base_scale[2] * (1.0 + (config["eye_scale"] - 1.0) * intensity)
    
    # 如果有嘴巴对象，可以调整
    mouth = bpy.data.objects.get(f"{character_name}_Mouth")
    if mouth:
        mouth.scale[0] = 1.0 + config["mouth_curve"] * intensity
    
    return {
        "success": True,
        "data": {
            "expression": expression,
            "intensity": intensity
        }
    }


def handle_face_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """调整面部特征"""
    character_name = params.get("character_name")
    eye_size = params.get("eye_size", 1.0)
    eye_spacing = params.get("eye_spacing", 1.0)
    
    # 调整眼睛大小
    for side in ["L", "R"]:
        eye = bpy.data.objects.get(f"{character_name}_Eye_{side}")
        if eye:
            eye.scale *= eye_size
        
        highlight = bpy.data.objects.get(f"{character_name}_EyeHighlight_{side}")
        if highlight:
            highlight.scale *= eye_size
    
    # 调整眼睛间距
    eye_l = bpy.data.objects.get(f"{character_name}_Eye_L")
    eye_r = bpy.data.objects.get(f"{character_name}_Eye_R")
    if eye_l and eye_r:
        center_x = (eye_l.location.x + eye_r.location.x) / 2
        offset = abs(eye_l.location.x - center_x) * eye_spacing
        eye_l.location.x = center_x - offset
        eye_r.location.x = center_x + offset
    
    return {
        "success": True,
        "data": {}
    }


def handle_clothing_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加服装"""
    character_name = params.get("character_name")
    clothing_type = params.get("clothing_type", "shirt")
    color = params.get("color") or [0.2, 0.4, 0.8, 1.0]
    style = params.get("style", "casual")
    
    body = bpy.data.objects.get(f"{character_name}_Body")
    if not body:
        return {
            "success": False,
            "error": {"code": "BODY_NOT_FOUND", "message": f"找不到角色身体: {character_name}_Body"}
        }
    
    clothing_mat = _create_material(f"{character_name}_{clothing_type}", color, roughness=0.6)
    
    if clothing_type in ["shirt", "jacket", "uniform", "sportswear"]:
        # 上衣 - 包裹身体
        bpy.ops.mesh.primitive_cube_add(location=body.location)
        clothing = bpy.context.active_object
        clothing.name = f"{character_name}_Clothing_{clothing_type}"
        clothing.scale = [body.scale[0] * 1.1, body.scale[1] * 1.1, body.scale[2] * 0.7]
        _assign_material(clothing, clothing_mat)
        
    elif clothing_type == "pants":
        # 裤子 - 包裹腿部
        for side in ["L", "R"]:
            leg = bpy.data.objects.get(f"{character_name}_Leg_{side}")
            if leg:
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=leg.dimensions[0] * 0.6,
                    depth=leg.dimensions[2] * 1.05,
                    location=leg.location
                )
                pants = bpy.context.active_object
                pants.name = f"{character_name}_Pants_{side}"
                _assign_material(pants, clothing_mat)
    
    elif clothing_type == "dress":
        # 连衣裙
        bpy.ops.mesh.primitive_cone_add(
            radius1=body.scale[0] * 2,
            radius2=body.scale[0] * 0.8,
            depth=body.scale[2] * 2,
            location=[body.location[0], body.location[1], body.location[2] - body.scale[2] * 0.5]
        )
        dress = bpy.context.active_object
        dress.name = f"{character_name}_Clothing_dress"
        _assign_material(dress, clothing_mat)
    
    return {
        "success": True,
        "data": {
            "clothing_type": clothing_type
        }
    }


def handle_hair_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建发型"""
    character_name = params.get("character_name")
    hair_style = params.get("hair_style", "short")
    color = params.get("color") or [0.05, 0.03, 0.02, 1.0]
    volume = params.get("volume", 1.0)
    
    head = bpy.data.objects.get(f"{character_name}_Head")
    if not head:
        return {
            "success": False,
            "error": {"code": "HEAD_NOT_FOUND", "message": f"找不到角色头部: {character_name}_Head"}
        }
    
    hair_mat = _create_material(f"{character_name}_Hair", color, roughness=0.7)
    
    hair_z = head.location.z + head.dimensions[2] * 0.3
    
    if hair_style == "short":
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head.dimensions[0] * 0.55 * volume,
            location=[head.location[0], head.location[1], hair_z]
        )
        hair = bpy.context.active_object
        hair.name = f"{character_name}_Hair"
        hair.scale = [1.0, 1.0, 0.6]
        _assign_material(hair, hair_mat)
        
    elif hair_style == "medium":
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head.dimensions[0] * 0.58 * volume,
            location=[head.location[0], head.location[1], hair_z]
        )
        hair = bpy.context.active_object
        hair.name = f"{character_name}_Hair"
        hair.scale = [1.0, 1.1, 0.8]
        _assign_material(hair, hair_mat)
        
    elif hair_style == "long":
        # 头顶
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head.dimensions[0] * 0.55 * volume,
            location=[head.location[0], head.location[1], hair_z]
        )
        hair_top = bpy.context.active_object
        hair_top.name = f"{character_name}_Hair_Top"
        hair_top.scale = [1.0, 1.0, 0.6]
        _assign_material(hair_top, hair_mat)
        
        # 后面长发
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head.dimensions[0] * 0.4 * volume,
            depth=head.dimensions[2] * 1.5,
            location=[head.location[0], head.location[1] + head.dimensions[1] * 0.3, head.location[2] - head.dimensions[2] * 0.5]
        )
        hair_back = bpy.context.active_object
        hair_back.name = f"{character_name}_Hair_Back"
        _assign_material(hair_back, hair_mat)
        
    elif hair_style == "ponytail":
        # 头顶
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head.dimensions[0] * 0.55 * volume,
            location=[head.location[0], head.location[1], hair_z]
        )
        hair_top = bpy.context.active_object
        hair_top.name = f"{character_name}_Hair_Top"
        hair_top.scale = [1.0, 1.0, 0.6]
        _assign_material(hair_top, hair_mat)
        
        # 马尾
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head.dimensions[0] * 0.15 * volume,
            depth=head.dimensions[2] * 1.2,
            location=[head.location[0], head.location[1] + head.dimensions[1] * 0.4, head.location[2]]
        )
        ponytail = bpy.context.active_object
        ponytail.name = f"{character_name}_Hair_Ponytail"
        ponytail.rotation_euler = [0.5, 0, 0]
        _assign_material(ponytail, hair_mat)
        
    elif hair_style == "spiky":
        # 尖刺发型
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x = head.location[0] + math.cos(angle) * head.dimensions[0] * 0.3
            y = head.location[1] + math.sin(angle) * head.dimensions[1] * 0.3
            
            bpy.ops.mesh.primitive_cone_add(
                radius1=head.dimensions[0] * 0.1 * volume,
                radius2=0,
                depth=head.dimensions[2] * 0.4 * volume,
                location=[x, y, hair_z + head.dimensions[2] * 0.1]
            )
            spike = bpy.context.active_object
            spike.name = f"{character_name}_Hair_Spike_{i}"
            spike.rotation_euler = [math.cos(angle) * 0.3, math.sin(angle) * 0.3, 0]
            _assign_material(spike, hair_mat)
    
    elif hair_style == "bald":
        # 光头不需要创建头发
        pass
    
    return {
        "success": True,
        "data": {
            "hair_style": hair_style
        }
    }


def handle_accessory_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加配饰"""
    character_name = params.get("character_name")
    accessory_type = params.get("accessory_type", "glasses")
    color = params.get("color") or [0.1, 0.1, 0.1, 1.0]
    loc = params.get("location", "auto")
    
    head = bpy.data.objects.get(f"{character_name}_Head")
    body = bpy.data.objects.get(f"{character_name}_Body")
    
    accessory_mat = _create_material(f"{character_name}_{accessory_type}", color, metallic=0.5, roughness=0.3)
    
    if accessory_type == "glasses" and head:
        # 眼镜框
        for side, x_offset in [("L", -0.08), ("R", 0.08)]:
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.04,
                minor_radius=0.005,
                location=[head.location[0] + x_offset, head.location[1] - head.dimensions[1] * 0.45, head.location[2] + 0.02]
            )
            frame = bpy.context.active_object
            frame.name = f"{character_name}_Glasses_Frame_{side}"
            frame.rotation_euler = [1.57, 0, 0]
            _assign_material(frame, accessory_mat)
        
        # 镜腿
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.003,
            depth=0.15,
            location=[head.location[0], head.location[1] - head.dimensions[1] * 0.35, head.location[2] + 0.02]
        )
        bridge = bpy.context.active_object
        bridge.name = f"{character_name}_Glasses_Bridge"
        bridge.rotation_euler = [0, 1.57, 0]
        _assign_material(bridge, accessory_mat)
        
    elif accessory_type == "hat" and head:
        # 帽子
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head.dimensions[0] * 0.6,
            depth=head.dimensions[2] * 0.3,
            location=[head.location[0], head.location[1], head.location[2] + head.dimensions[2] * 0.5]
        )
        hat = bpy.context.active_object
        hat.name = f"{character_name}_Hat"
        _assign_material(hat, accessory_mat)
        
        # 帽檐
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head.dimensions[0] * 0.8,
            depth=0.02,
            location=[head.location[0], head.location[1] - head.dimensions[1] * 0.2, head.location[2] + head.dimensions[2] * 0.35]
        )
        brim = bpy.context.active_object
        brim.name = f"{character_name}_Hat_Brim"
        _assign_material(brim, accessory_mat)
        
    elif accessory_type == "medal" and body:
        # 奖牌
        gold_mat = _create_material(f"{character_name}_Medal_Gold", [1.0, 0.85, 0.0, 1.0], metallic=1.0, roughness=0.2)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04,
            depth=0.005,
            location=[body.location[0], body.location[1] - body.dimensions[1] * 0.6, body.location[2] + body.dimensions[2] * 0.3]
        )
        medal = bpy.context.active_object
        medal.name = f"{character_name}_Medal"
        medal.rotation_euler = [1.57, 0, 0]
        _assign_material(medal, gold_mat)
        
        # 挂绳
        ribbon_mat = _create_material(f"{character_name}_Medal_Ribbon", [0.8, 0.1, 0.1, 1.0], roughness=0.7)
        bpy.ops.mesh.primitive_cube_add(
            location=[body.location[0], body.location[1] - body.dimensions[1] * 0.5, body.location[2] + body.dimensions[2] * 0.5]
        )
        ribbon = bpy.context.active_object
        ribbon.name = f"{character_name}_Medal_Ribbon"
        ribbon.scale = [0.01, 0.005, 0.1]
        _assign_material(ribbon, ribbon_mat)
        
    elif accessory_type == "necklace" and body:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=body.dimensions[0] * 0.4,
            minor_radius=0.005,
            location=[body.location[0], body.location[1], body.location[2] + body.dimensions[2] * 0.45]
        )
        necklace = bpy.context.active_object
        necklace.name = f"{character_name}_Necklace"
        necklace.rotation_euler = [1.57, 0, 0]
        _assign_material(necklace, accessory_mat)
    
    return {
        "success": True,
        "data": {
            "accessory_type": accessory_type
        }
    }
