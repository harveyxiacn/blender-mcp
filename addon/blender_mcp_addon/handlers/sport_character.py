"""
运动角色处理器

处理运动员角色创建、装备添加、运动服、运动姿势、参考图加载、模型优化等命令。
专为乒乓球运动员（特别是樊振东）3D模型制作优化。
"""

from typing import Any, Dict, List, Optional
import math
import os

import bpy


# ==================== 配置数据 ====================

# 运动角色风格配置
STYLE_CONFIG = {
    "CHIBI": {
        "head_body_ratio": 2.5,
        "head_scale": [1.0, 1.0, 1.05],
        "body_scale": [0.55, 0.4, 0.65],
        "eye_size": 1.6,
        "limb_thickness": 0.16,
        "hand_scale": 1.3,
        "foot_scale": 1.2,
        "face_roundness": 1.3,
    },
    "ANIME": {
        "head_body_ratio": 5.5,
        "head_scale": [0.65, 0.65, 0.75],
        "body_scale": [0.7, 0.45, 1.0],
        "eye_size": 1.3,
        "limb_thickness": 0.1,
        "hand_scale": 1.0,
        "foot_scale": 1.0,
        "face_roundness": 1.1,
    },
    "STYLIZED": {
        "head_body_ratio": 4.0,
        "head_scale": [0.75, 0.75, 0.85],
        "body_scale": [0.65, 0.45, 0.85],
        "eye_size": 1.2,
        "limb_thickness": 0.12,
        "hand_scale": 1.1,
        "foot_scale": 1.05,
        "face_roundness": 1.15,
    },
    "REALISTIC": {
        "head_body_ratio": 7.5,
        "head_scale": [0.5, 0.5, 0.6],
        "body_scale": [0.8, 0.5, 1.2],
        "eye_size": 0.8,
        "limb_thickness": 0.12,
        "hand_scale": 1.0,
        "foot_scale": 1.0,
        "face_roundness": 1.0,
    },
}

# 运动员预设配置
ATHLETE_PRESETS = {
    "FAN_ZHENDONG": {
        "name": "FanZhendong",
        "height_real": 1.72,      # 真实身高172cm
        "build": "athletic",
        "skin_color": [0.95, 0.82, 0.72, 1.0],  # 亚洲皮肤色
        "hair_color": [0.05, 0.03, 0.02, 1.0],   # 黑色短发
        "hair_style": "short",
        "eye_color": [0.15, 0.08, 0.05, 1.0],    # 深棕色眼
        "face_features": {
            "face_shape": "round",       # 圆脸
            "eyebrow_thickness": 1.2,    # 浓眉
            "eye_size": 1.1,             # 大眼
            "nose_size": 1.0,            # 标准鼻
            "mouth_width": 1.0,          # 标准嘴
            "jaw_width": 1.1,            # 微宽下巴
            "ear_size": 1.1,             # 略大耳朵（Q版特征）
        },
        "jersey_number": 20,
        "brand": "Li-Ning",
    },
}

# 队伍颜色配置
TEAM_COLORS = {
    "CHINA_NATIONAL": {
        "primary": [0.85, 0.1, 0.1, 1.0],     # 中国红
        "secondary": [1.0, 0.85, 0.0, 1.0],     # 金黄
        "accent": [1.0, 1.0, 1.0, 1.0],         # 白色
    },
    "CHINA_NATIONAL_BLUE": {
        "primary": [0.1, 0.2, 0.7, 1.0],       # 深蓝
        "secondary": [0.3, 0.5, 0.9, 1.0],      # 浅蓝
        "accent": [1.0, 1.0, 1.0, 1.0],         # 白色
    },
    "CHINA_NATIONAL_WHITE": {
        "primary": [1.0, 1.0, 1.0, 1.0],       # 白色
        "secondary": [0.85, 0.1, 0.1, 1.0],     # 红色条纹
        "accent": [0.1, 0.1, 0.1, 1.0],         # 黑色
    },
    "CLUB_SHENZHEN": {
        "primary": [0.0, 0.5, 0.8, 1.0],       # 天蓝
        "secondary": [1.0, 1.0, 1.0, 1.0],      # 白色
        "accent": [0.1, 0.1, 0.1, 1.0],         # 黑色
    },
    "TRAINING": {
        "primary": [0.2, 0.2, 0.2, 1.0],       # 深灰
        "secondary": [0.85, 0.1, 0.1, 1.0],     # 红色
        "accent": [1.0, 1.0, 1.0, 1.0],         # 白色
    },
}

# 乒乓球运动姿势骨骼旋转数据 (Euler XYZ in degrees)
SPORT_POSES = {
    "READY_STANCE": {
        "description": "准备接球姿势",
        "spine": (10, 0, 0),
        "spine.001": (5, 0, 0),
        "upper_arm.R": (-30, -20, 0),
        "forearm.R": (-60, 0, 0),
        "hand.R": (-10, 0, 0),
        "upper_arm.L": (-20, 20, 0),
        "forearm.L": (-40, 0, 0),
        "hand.L": (0, 0, 0),
        "thigh.R": (-20, 0, 5),
        "shin.R": (25, 0, 0),
        "thigh.L": (-20, 0, -5),
        "shin.L": (25, 0, 0),
    },
    "FOREHAND_ATTACK": {
        "description": "正手进攻",
        "spine": (15, 0, -30),
        "spine.001": (5, 0, -15),
        "upper_arm.R": (-45, -60, -30),
        "forearm.R": (-70, 0, 0),
        "hand.R": (-20, 0, 10),
        "upper_arm.L": (-20, 30, 0),
        "forearm.L": (-50, 0, 0),
        "thigh.R": (-25, 0, 10),
        "shin.R": (30, 0, 0),
        "thigh.L": (-15, 0, -5),
        "shin.L": (20, 0, 0),
    },
    "BACKHAND_ATTACK": {
        "description": "反手拉球",
        "spine": (15, 0, 20),
        "spine.001": (5, 0, 10),
        "upper_arm.R": (-40, 30, 20),
        "forearm.R": (-80, 0, 0),
        "hand.R": (-15, -20, 0),
        "upper_arm.L": (-25, 15, 0),
        "forearm.L": (-45, 0, 0),
        "thigh.R": (-20, 0, 5),
        "shin.R": (25, 0, 0),
        "thigh.L": (-25, 0, -10),
        "shin.L": (30, 0, 0),
    },
    "SERVE_TOSS": {
        "description": "发球抛球",
        "spine": (5, 0, 0),
        "spine.001": (-5, 0, 0),
        "upper_arm.R": (-30, -20, 0),
        "forearm.R": (-50, 0, 0),
        "hand.R": (-10, 0, 0),
        "upper_arm.L": (-120, 10, 0),
        "forearm.L": (-20, 0, 0),
        "hand.L": (30, 0, 0),
        "thigh.R": (-10, 0, 5),
        "shin.R": (15, 0, 0),
        "thigh.L": (-10, 0, -5),
        "shin.L": (15, 0, 0),
    },
    "SERVE_HIT": {
        "description": "发球击球",
        "spine": (20, 0, -15),
        "spine.001": (10, 0, -10),
        "upper_arm.R": (-60, -40, -20),
        "forearm.R": (-75, 0, 0),
        "hand.R": (-25, 0, 15),
        "upper_arm.L": (-30, 20, 0),
        "forearm.L": (-40, 0, 0),
        "thigh.R": (-15, 0, 5),
        "shin.R": (20, 0, 0),
        "thigh.L": (-15, 0, -5),
        "shin.L": (20, 0, 0),
    },
    "FOREHAND_LOOP": {
        "description": "正手弧圈球",
        "spine": (20, 0, -40),
        "spine.001": (10, 0, -20),
        "upper_arm.R": (-50, -70, -40),
        "forearm.R": (-60, 0, 0),
        "hand.R": (-25, 0, 20),
        "upper_arm.L": (-15, 40, 0),
        "forearm.L": (-60, 0, 0),
        "thigh.R": (-30, 0, 15),
        "shin.R": (35, 0, 0),
        "thigh.L": (-10, 0, -10),
        "shin.L": (15, 0, 0),
    },
    "CELEBRATE": {
        "description": "双臂举起庆祝",
        "spine": (-5, 0, 0),
        "spine.001": (-10, 0, 0),
        "upper_arm.R": (-150, -20, 0),
        "forearm.R": (-30, 0, 0),
        "hand.R": (0, 0, 0),
        "upper_arm.L": (-150, 20, 0),
        "forearm.L": (-30, 0, 0),
        "hand.L": (0, 0, 0),
        "thigh.R": (-5, 0, 5),
        "shin.R": (10, 0, 0),
        "thigh.L": (-5, 0, -5),
        "shin.L": (10, 0, 0),
    },
    "FIST_PUMP": {
        "description": "握拳吼叫（樊振东标志性动作）",
        "spine": (-5, 0, -10),
        "spine.001": (-10, 0, -5),
        "upper_arm.R": (-100, -30, -20),
        "forearm.R": (-90, 0, 0),
        "hand.R": (-20, 0, 0),
        "upper_arm.L": (-40, 20, 0),
        "forearm.L": (-60, 0, 0),
        "hand.L": (-30, 0, 0),
        "thigh.R": (-10, 0, 10),
        "shin.R": (15, 0, 0),
        "thigh.L": (-5, 0, -5),
        "shin.L": (10, 0, 0),
    },
    "HOLD_MEDAL": {
        "description": "双手展示奖牌",
        "spine": (0, 0, 0),
        "spine.001": (-5, 0, 0),
        "upper_arm.R": (-60, -20, 0),
        "forearm.R": (-70, 10, 0),
        "hand.R": (-10, 20, 0),
        "upper_arm.L": (-60, 20, 0),
        "forearm.L": (-70, -10, 0),
        "hand.L": (-10, -20, 0),
        "thigh.R": (-5, 0, 5),
        "shin.R": (8, 0, 0),
        "thigh.L": (-5, 0, -5),
        "shin.L": (8, 0, 0),
    },
    "RECEIVING_AWARD": {
        "description": "领奖台站姿",
        "spine": (-5, 0, 0),
        "spine.001": (-5, 0, 0),
        "upper_arm.R": (-10, -10, 0),
        "forearm.R": (-20, 0, 0),
        "hand.R": (0, 0, 0),
        "upper_arm.L": (-10, 10, 0),
        "forearm.L": (-20, 0, 0),
        "hand.L": (0, 0, 0),
        "thigh.R": (-3, 0, 3),
        "shin.R": (5, 0, 0),
        "thigh.L": (-3, 0, -3),
        "shin.L": (5, 0, 0),
    },
    "T_POSE": {
        "description": "T-Pose",
        "spine": (0, 0, 0),
        "spine.001": (0, 0, 0),
        "upper_arm.R": (0, -90, 0),
        "forearm.R": (0, 0, 0),
        "hand.R": (0, 0, 0),
        "upper_arm.L": (0, 90, 0),
        "forearm.L": (0, 0, 0),
        "hand.L": (0, 0, 0),
        "thigh.R": (0, 0, 5),
        "shin.R": (0, 0, 0),
        "thigh.L": (0, 0, -5),
        "shin.L": (0, 0, 0),
    },
    "A_POSE": {
        "description": "A-Pose",
        "spine": (0, 0, 0),
        "spine.001": (0, 0, 0),
        "upper_arm.R": (0, -60, 0),
        "forearm.R": (0, 0, 0),
        "hand.R": (0, 0, 0),
        "upper_arm.L": (0, 60, 0),
        "forearm.L": (0, 0, 0),
        "hand.L": (0, 0, 0),
        "thigh.R": (0, 0, 5),
        "shin.R": (0, 0, 0),
        "thigh.L": (0, 0, -5),
        "shin.L": (0, 0, 0),
    },
}

# 平台默认面数
PLATFORM_TRI_DEFAULTS = {
    "WEB": 4000,
    "MOBILE": 6000,
    "PC_CONSOLE": 15000,
    "PRINT_3D": 100000,
}


# ==================== 工具函数 ====================

def _get_principled_bsdf(nodes):
    """获取Principled BSDF节点（兼容中英文Blender）"""
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None


def _create_material(name: str, color: List[float],
                     metallic: float = 0.0, roughness: float = 0.5,
                     specular: float = 0.5) -> bpy.types.Material:
    """创建PBR材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    bsdf = _get_principled_bsdf(mat.node_tree.nodes)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color if len(color) == 4 else color + [1.0]
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        # Specular 在新版本中可能名称不同
        try:
            bsdf.inputs["Specular IOR Level"].default_value = specular
        except (KeyError, IndexError):
            try:
                bsdf.inputs["Specular"].default_value = specular
            except (KeyError, IndexError):
                pass

    return mat


def _assign_material(obj, material):
    """为对象分配材质"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def _ensure_object_mode():
    """确保在Object模式"""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')


def _deselect_all():
    """取消选择所有对象"""
    bpy.ops.object.select_all(action='DESELECT')


def _set_smooth_shading(obj):
    """设置平滑着色（兼容不同版本）"""
    try:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    except Exception:
        pass


def _parent_to(child_obj, parent_obj, keep_transform=True):
    """设置父子关系"""
    child_obj.parent = parent_obj
    if keep_transform:
        child_obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()


# ==================== 角色创建 ====================

def handle_create_character(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建运动角色"""
    _ensure_object_mode()

    name = params.get("name", "Athlete")
    sport = params.get("sport", "TABLE_TENNIS")
    style = params.get("style", "CHIBI")
    preset = params.get("preset", "CUSTOM")
    height = params.get("height", 1.0)
    head_body_ratio_override = params.get("head_body_ratio")
    skin_color = params.get("skin_color")
    build = params.get("build", "athletic")
    create_armature = params.get("create_armature", True)
    face_count_budget = params.get("face_count_budget", 4500)

    # 获取风格配置
    config = STYLE_CONFIG.get(style, STYLE_CONFIG["CHIBI"]).copy()
    if head_body_ratio_override:
        config["head_body_ratio"] = head_body_ratio_override

    # 获取运动员预设
    athlete = None
    if preset != "CUSTOM" and preset in ATHLETE_PRESETS:
        athlete = ATHLETE_PRESETS[preset]
        if not skin_color:
            skin_color = athlete["skin_color"]

    if not skin_color:
        skin_color = [0.95, 0.82, 0.72, 1.0]  # 默认亚洲肤色

    # 体格修正
    build_modifiers = {
        "slim": {"body_width": 0.85, "limb_thick": 0.9},
        "athletic": {"body_width": 1.0, "limb_thick": 1.0},
        "muscular": {"body_width": 1.15, "limb_thick": 1.15},
        "stocky": {"body_width": 1.1, "limb_thick": 1.2},
    }
    build_mod = build_modifiers.get(build, build_modifiers["athletic"])

    # 计算缩放
    ratio = config["head_body_ratio"]
    scale_factor = height / 1.7

    created_parts = []

    # 创建根空物体
    root_empty = bpy.data.objects.new(f"{name}_Root", None)
    bpy.context.collection.objects.link(root_empty)
    root_empty.empty_display_type = 'ARROWS'
    root_empty.empty_display_size = 0.1

    # 创建皮肤材质（SSS适合皮肤表现）
    skin_mat = _create_material(f"{name}_Skin", skin_color, roughness=0.75)
    # 为皮肤添加SSS
    bsdf = _get_principled_bsdf(skin_mat.node_tree.nodes)
    if bsdf:
        try:
            bsdf.inputs["Subsurface Weight"].default_value = 0.15
        except (KeyError, IndexError):
            try:
                bsdf.inputs["Subsurface"].default_value = 0.15
            except (KeyError, IndexError):
                pass

    # 根据面数预算决定细分级别
    if face_count_budget <= 3000:
        sphere_segments = 16
        sphere_rings = 12
        subdivisions = 0
    elif face_count_budget <= 5000:
        sphere_segments = 24
        sphere_rings = 16
        subdivisions = 1
    else:
        sphere_segments = 32
        sphere_rings = 24
        subdivisions = 2

    # ========== 头部 ==========
    head_z = height * (1 - 1 / ratio)
    head_radius = 0.25 * scale_factor * config["head_scale"][0] * config["face_roundness"]

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=sphere_segments,
        ring_count=sphere_rings,
        radius=head_radius,
        location=[0, 0, head_z]
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.scale = list(config["head_scale"])
    _set_smooth_shading(head)
    _assign_material(head, skin_mat)
    _parent_to(head, root_empty)
    created_parts.append(head.name)

    # ========== 眼睛（Q版和动漫需要大眼睛）==========
    eye_size = 0.06 * scale_factor * config["eye_size"]
    eye_y = -head_radius * 0.85
    eye_z = head_z + head_radius * 0.15
    eye_spacing = head_radius * 0.35

    eye_color = [0.15, 0.08, 0.05, 1.0]
    if athlete and "eye_color" in athlete:
        eye_color = athlete["eye_color"]
    eye_mat = _create_material(f"{name}_Eye", eye_color, roughness=0.1, specular=0.8)
    eye_white_mat = _create_material(f"{name}_EyeWhite", [1.0, 1.0, 1.0, 1.0], roughness=0.3)

    for side, x_offset in [("R", eye_spacing), ("L", -eye_spacing)]:
        # 眼白
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(12, sphere_segments // 2),
            ring_count=max(8, sphere_rings // 2),
            radius=eye_size * 1.3,
            location=[x_offset, eye_y, eye_z]
        )
        eye_white = bpy.context.active_object
        eye_white.name = f"{name}_EyeWhite_{side}"
        _set_smooth_shading(eye_white)
        _assign_material(eye_white, eye_white_mat)
        _parent_to(eye_white, head)

        # 瞳孔
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(12, sphere_segments // 2),
            ring_count=max(8, sphere_rings // 2),
            radius=eye_size,
            location=[x_offset, eye_y - eye_size * 0.3, eye_z]
        )
        eye_pupil = bpy.context.active_object
        eye_pupil.name = f"{name}_Eye_{side}"
        _set_smooth_shading(eye_pupil)
        _assign_material(eye_pupil, eye_mat)
        _parent_to(eye_pupil, head)

    created_parts.append(f"{name}_Eyes")

    # ========== 鼻子 ==========
    nose_size = 0.03 * scale_factor
    if style == "CHIBI":
        nose_size *= 0.6  # Q版鼻子更小
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=max(8, sphere_segments // 3),
        ring_count=max(6, sphere_rings // 3),
        radius=nose_size,
        location=[0, eye_y - nose_size, eye_z - head_radius * 0.3]
    )
    nose = bpy.context.active_object
    nose.name = f"{name}_Nose"
    nose.scale = [1.0, 0.6, 0.8]
    _set_smooth_shading(nose)
    # 鼻子略红（Q版特征）
    nose_color = list(skin_color[:3])
    nose_color[0] = min(1.0, nose_color[0] * 1.15)
    nose_mat = _create_material(f"{name}_Nose", nose_color + [1.0], roughness=0.7)
    _assign_material(nose, nose_mat)
    _parent_to(nose, head)
    created_parts.append(f"{name}_Nose")

    # ========== 嘴巴 ==========
    mouth_width = 0.06 * scale_factor
    mouth_z = eye_z - head_radius * 0.55
    bpy.ops.mesh.primitive_cube_add(
        size=0.01,
        location=[0, eye_y, mouth_z]
    )
    mouth = bpy.context.active_object
    mouth.name = f"{name}_Mouth"
    mouth.scale = [mouth_width * 10, 0.3, 0.2]
    mouth_mat = _create_material(f"{name}_Mouth", [0.7, 0.3, 0.3, 1.0], roughness=0.6)
    _assign_material(mouth, mouth_mat)
    _parent_to(mouth, head)
    created_parts.append(f"{name}_Mouth")

    # ========== 耳朵 ==========
    ear_size = 0.06 * scale_factor
    if athlete and "face_features" in athlete:
        ear_size *= athlete["face_features"].get("ear_size", 1.0)

    for side, x_mult in [("R", 1), ("L", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=ear_size,
            location=[x_mult * head_radius * 0.95, 0, eye_z - head_radius * 0.15]
        )
        ear = bpy.context.active_object
        ear.name = f"{name}_Ear_{side}"
        ear.scale = [0.4, 0.6, 1.0]
        _set_smooth_shading(ear)
        _assign_material(ear, skin_mat)
        _parent_to(ear, head)

    created_parts.append(f"{name}_Ears")

    # ========== 头发 ==========
    hair_color = [0.05, 0.03, 0.02, 1.0]  # 默认黑色
    if athlete and "hair_color" in athlete:
        hair_color = athlete["hair_color"]
    hair_mat = _create_material(f"{name}_Hair", hair_color, roughness=0.8)

    # 头发用多个球体组合（Q版风格）
    hair_base_z = head_z + head_radius * 0.3
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=sphere_segments,
        ring_count=sphere_rings,
        radius=head_radius * 1.08,
        location=[0, 0, hair_base_z]
    )
    hair_base = bpy.context.active_object
    hair_base.name = f"{name}_Hair"
    hair_base.scale = [1.05, 1.0, 0.9]
    _set_smooth_shading(hair_base)
    _assign_material(hair_base, hair_mat)
    _parent_to(hair_base, head)

    # 刘海（短发前额碎发）
    for i, (x, y_off) in enumerate([(-0.3, -0.2), (0, -0.3), (0.3, -0.2), (-0.15, -0.25), (0.15, -0.25)]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=head_radius * 0.25,
            location=[x * head_radius, y_off * head_radius - head_radius * 0.6, hair_base_z + head_radius * 0.1]
        )
        bang = bpy.context.active_object
        bang.name = f"{name}_HairBang_{i}"
        bang.scale = [0.8, 0.5, 1.2]
        _set_smooth_shading(bang)
        _assign_material(bang, hair_mat)
        _parent_to(bang, hair_base)

    created_parts.append(f"{name}_Hair")

    # ========== 身体 ==========
    body_z = height * 0.38
    body_width = config["body_scale"][0] * scale_factor * 0.3 * build_mod["body_width"]
    body_depth = config["body_scale"][1] * scale_factor * 0.2
    body_height = config["body_scale"][2] * scale_factor * 0.35

    bpy.ops.mesh.primitive_cube_add(location=[0, 0, body_z])
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = [body_width, body_depth, body_height]
    # 添加细分修改器使身体更圆润
    if subdivisions > 0:
        subsurf = body.modifiers.new("Subdivide", 'SUBSURF')
        subsurf.levels = subdivisions
        subsurf.render_levels = subdivisions
    _set_smooth_shading(body)
    _assign_material(body, skin_mat)
    _parent_to(body, root_empty)
    created_parts.append(f"{name}_Body")

    # ========== 手臂 ==========
    arm_thickness = config["limb_thickness"] * scale_factor * build_mod["limb_thick"]
    arm_length = height * 0.2
    shoulder_z = body_z + body_height * 0.8

    for side, x_mult in [("R", 1), ("L", -1)]:
        shoulder_x = x_mult * (body_width + arm_thickness * 0.5)

        # 上臂
        bpy.ops.mesh.primitive_cylinder_add(
            radius=arm_thickness,
            depth=arm_length,
            location=[shoulder_x, 0, shoulder_z - arm_length * 0.4]
        )
        upper_arm = bpy.context.active_object
        upper_arm.name = f"{name}_UpperArm_{side}"
        _set_smooth_shading(upper_arm)
        _assign_material(upper_arm, skin_mat)
        _parent_to(upper_arm, body)

        # 前臂
        bpy.ops.mesh.primitive_cylinder_add(
            radius=arm_thickness * 0.85,
            depth=arm_length * 0.9,
            location=[shoulder_x, 0, shoulder_z - arm_length * 1.2]
        )
        forearm = bpy.context.active_object
        forearm.name = f"{name}_Forearm_{side}"
        _set_smooth_shading(forearm)
        _assign_material(forearm, skin_mat)
        _parent_to(forearm, body)

        # 手
        hand_scale = config["hand_scale"]
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=arm_thickness * hand_scale,
            location=[shoulder_x, 0, shoulder_z - arm_length * 1.7]
        )
        hand = bpy.context.active_object
        hand.name = f"{name}_Hand_{side}"
        hand.scale = [1.0, 0.6, 1.2]
        _set_smooth_shading(hand)
        _assign_material(hand, skin_mat)
        _parent_to(hand, body)

    created_parts.append(f"{name}_Arms")

    # ========== 腿部 ==========
    leg_thickness = config["limb_thickness"] * scale_factor * 1.1 * build_mod["limb_thick"]
    leg_length = height * 0.22
    hip_z = body_z - body_height * 0.8

    for side, x_mult in [("R", 1), ("L", -1)]:
        leg_x = x_mult * body_width * 0.5

        # 大腿
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_thickness,
            depth=leg_length,
            location=[leg_x, 0, hip_z - leg_length * 0.3]
        )
        thigh = bpy.context.active_object
        thigh.name = f"{name}_Thigh_{side}"
        _set_smooth_shading(thigh)
        _assign_material(thigh, skin_mat)
        _parent_to(thigh, body)

        # 小腿
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_thickness * 0.85,
            depth=leg_length,
            location=[leg_x, 0, hip_z - leg_length * 1.2]
        )
        shin = bpy.context.active_object
        shin.name = f"{name}_Shin_{side}"
        _set_smooth_shading(shin)
        _assign_material(shin, skin_mat)
        _parent_to(shin, body)

        # 脚
        foot_scale = config["foot_scale"]
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[leg_x, -leg_thickness * 0.3, hip_z - leg_length * 2.0]
        )
        foot = bpy.context.active_object
        foot.name = f"{name}_Foot_{side}"
        foot.scale = [leg_thickness * 8 * foot_scale, leg_thickness * 15 * foot_scale, leg_thickness * 5]
        if subdivisions > 0:
            subsurf = foot.modifiers.new("Subdivide", 'SUBSURF')
            subsurf.levels = 1
            subsurf.render_levels = 1
        _set_smooth_shading(foot)
        # 鞋子材质
        shoe_mat = _create_material(f"{name}_Shoe", [0.1, 0.1, 0.9, 1.0], roughness=0.6)
        _assign_material(foot, shoe_mat)
        _parent_to(foot, body)

    created_parts.append(f"{name}_Legs")

    # ========== 骨骼系统（可选）==========
    has_armature = False
    if create_armature:
        try:
            # 创建骨骼
            bpy.ops.object.armature_add(location=[0, 0, 0])
            armature_obj = bpy.context.active_object
            armature_obj.name = f"{name}_Armature"
            armature = armature_obj.data
            armature.name = f"{name}_Armature"

            # 进入编辑模式添加骨骼
            bpy.ops.object.mode_set(mode='EDIT')

            # 根骨骼
            root_bone = armature.edit_bones[0]
            root_bone.name = "root"
            root_bone.head = (0, 0, 0)
            root_bone.tail = (0, 0, hip_z)

            # 脊柱
            spine = armature.edit_bones.new("spine")
            spine.head = (0, 0, hip_z)
            spine.tail = (0, 0, body_z)
            spine.parent = root_bone

            spine_001 = armature.edit_bones.new("spine.001")
            spine_001.head = (0, 0, body_z)
            spine_001.tail = (0, 0, shoulder_z)
            spine_001.parent = spine

            # 头部
            head_bone = armature.edit_bones.new("head")
            head_bone.head = (0, 0, shoulder_z)
            head_bone.tail = (0, 0, head_z + head_radius)
            head_bone.parent = spine_001

            # 手臂骨骼
            for side, x_mult in [("R", 1), ("L", -1)]:
                s_x = x_mult * (body_width + arm_thickness * 0.5)

                upper = armature.edit_bones.new(f"upper_arm.{side}")
                upper.head = (s_x * 0.5, 0, shoulder_z)
                upper.tail = (s_x, 0, shoulder_z - arm_length * 0.5)
                upper.parent = spine_001

                fore = armature.edit_bones.new(f"forearm.{side}")
                fore.head = (s_x, 0, shoulder_z - arm_length * 0.5)
                fore.tail = (s_x, 0, shoulder_z - arm_length * 1.3)
                fore.parent = upper

                hand_bone = armature.edit_bones.new(f"hand.{side}")
                hand_bone.head = (s_x, 0, shoulder_z - arm_length * 1.3)
                hand_bone.tail = (s_x, 0, shoulder_z - arm_length * 1.7)
                hand_bone.parent = fore

            # 腿部骨骼
            for side, x_mult in [("R", 1), ("L", -1)]:
                l_x = x_mult * body_width * 0.5

                thigh_bone = armature.edit_bones.new(f"thigh.{side}")
                thigh_bone.head = (l_x, 0, hip_z)
                thigh_bone.tail = (l_x, 0, hip_z - leg_length)
                thigh_bone.parent = root_bone

                shin_bone = armature.edit_bones.new(f"shin.{side}")
                shin_bone.head = (l_x, 0, hip_z - leg_length)
                shin_bone.tail = (l_x, 0, hip_z - leg_length * 2)
                shin_bone.parent = thigh_bone

                foot_bone = armature.edit_bones.new(f"foot.{side}")
                foot_bone.head = (l_x, 0, hip_z - leg_length * 2)
                foot_bone.tail = (l_x, -leg_thickness, hip_z - leg_length * 2)
                foot_bone.parent = shin_bone

            bpy.ops.object.mode_set(mode='OBJECT')

            _parent_to(armature_obj, root_empty)
            has_armature = True
            created_parts.append(f"{name}_Armature")

        except Exception as e:
            _ensure_object_mode()
            # 骨骼创建失败不影响整体
            pass

    return {
        "success": True,
        "data": {
            "name": name,
            "created_parts": created_parts,
            "head_body_ratio": config["head_body_ratio"],
            "has_armature": has_armature,
            "style": style,
            "sport": sport,
            "preset": preset,
        }
    }


# ==================== 装备添加 ====================

def handle_add_equipment(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加运动装备"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    equipment_type = params.get("equipment_type", "PADDLE")
    attach_to = params.get("attach_to", "auto")
    color = params.get("color")
    secondary_color = params.get("secondary_color")
    scale = params.get("scale", 1.0)

    # 查找角色根对象
    root_obj = bpy.data.objects.get(f"{character_name}_Root")
    hand_obj = bpy.data.objects.get(f"{character_name}_Hand_R")

    # 自动确定附着位置
    if attach_to == "auto":
        if equipment_type in ("PADDLE", "TROPHY"):
            attach_to = "right_hand"
        elif equipment_type in ("BALL",):
            attach_to = "left_hand"
        elif equipment_type in ("MEDAL_GOLD", "MEDAL_SILVER", "MEDAL_BRONZE"):
            attach_to = "neck"
        elif equipment_type in ("HEADBAND",):
            attach_to = "head"
        elif equipment_type in ("WRISTBAND",):
            attach_to = "right_hand"
        else:
            attach_to = "scene"

    # 获取附着点位置
    attach_location = [0, 0, 0]
    parent_obj = root_obj

    if attach_to == "right_hand":
        obj = bpy.data.objects.get(f"{character_name}_Hand_R")
        if obj:
            attach_location = list(obj.location)
            parent_obj = obj
    elif attach_to == "left_hand":
        obj = bpy.data.objects.get(f"{character_name}_Hand_L")
        if obj:
            attach_location = list(obj.location)
            parent_obj = obj
    elif attach_to == "neck":
        obj = bpy.data.objects.get(f"{character_name}_Body")
        if obj:
            attach_location = [0, -0.05, obj.location[2] + obj.scale[2] * 0.8]
            parent_obj = obj
    elif attach_to == "head":
        obj = bpy.data.objects.get(f"{character_name}_Head")
        if obj:
            attach_location = list(obj.location)
            attach_location[2] += 0.1
            parent_obj = obj

    equip_obj = None

    if equipment_type == "PADDLE":
        # 乒乓球拍
        paddle_color = color or [0.8, 0.1, 0.1]
        handle_color = secondary_color or [0.5, 0.3, 0.1]

        # 拍面
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=0.08 * scale,
            depth=0.01 * scale,
            location=attach_location
        )
        blade = bpy.context.active_object
        blade.name = f"{character_name}_Paddle_Blade"
        blade.scale[2] = 0.3  # 扁平
        blade_mat = _create_material(f"{character_name}_PaddleRubber",
                                     paddle_color + [1.0], roughness=0.9)
        _assign_material(blade, blade_mat)

        # 拍柄
        handle_loc = list(attach_location)
        handle_loc[2] -= 0.1 * scale
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.015 * scale,
            depth=0.08 * scale,
            location=handle_loc
        )
        handle = bpy.context.active_object
        handle.name = f"{character_name}_Paddle_Handle"
        handle_mat = _create_material(f"{character_name}_PaddleHandle",
                                      handle_color + [1.0], roughness=0.6)
        _assign_material(handle, handle_mat)

        # 组合
        _parent_to(handle, blade)
        equip_obj = blade
        if parent_obj:
            _parent_to(blade, parent_obj)

    elif equipment_type == "BALL":
        # 乒乓球
        ball_color = color or [1.0, 0.6, 0.0]  # 橙色乒乓球
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16,
            ring_count=12,
            radius=0.02 * scale,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Ball"
        _set_smooth_shading(equip_obj)
        ball_mat = _create_material(f"{character_name}_Ball",
                                    ball_color + [1.0], roughness=0.3)
        _assign_material(equip_obj, ball_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "TABLE":
        # 乒乓球台
        table_color = color or [0.0, 0.3, 0.5]  # 深蓝绿色
        # 台面
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[0, 0, 0.76 * scale]
        )
        table_top = bpy.context.active_object
        table_top.name = f"{character_name}_Table"
        table_top.scale = [1.525 * scale * 50, 0.7625 * scale * 50, 0.02 * scale * 50]
        table_mat = _create_material(f"{character_name}_Table",
                                     table_color + [1.0], roughness=0.4)
        _assign_material(table_top, table_mat)

        # 白色中线
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[0, 0, 0.761 * scale]
        )
        center_line = bpy.context.active_object
        center_line.name = f"{character_name}_TableLine"
        center_line.scale = [0.01 * 50, 0.76 * scale * 50, 0.005 * 50]
        line_mat = _create_material(f"{character_name}_TableLine",
                                    [1.0, 1.0, 1.0, 1.0], roughness=0.5)
        _assign_material(center_line, line_mat)
        _parent_to(center_line, table_top)

        equip_obj = table_top

    elif equipment_type == "NET":
        # 球网
        net_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[0, 0, 0.91 * scale]
        )
        net = bpy.context.active_object
        net.name = f"{character_name}_Net"
        net.scale = [0.01 * 50, 0.9125 * scale * 50, 0.1525 * scale * 50]
        net_mat = _create_material(f"{character_name}_Net",
                                   net_color + [1.0], roughness=0.8)
        net_mat.blend_method = 'CLIP' if hasattr(net_mat, 'blend_method') else None
        _assign_material(net, net_mat)
        equip_obj = net

    elif equipment_type.startswith("MEDAL_"):
        # 奖牌
        medal_colors = {
            "MEDAL_GOLD": [1.0, 0.85, 0.0],
            "MEDAL_SILVER": [0.8, 0.8, 0.85],
            "MEDAL_BRONZE": [0.8, 0.5, 0.2],
        }
        medal_color = color or medal_colors.get(equipment_type, [1.0, 0.85, 0.0])

        # 奖牌主体
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=0.04 * scale,
            depth=0.005 * scale,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_{equipment_type}"
        medal_mat = _create_material(f"{character_name}_{equipment_type}",
                                     medal_color + [1.0], metallic=0.9, roughness=0.2)
        _assign_material(equip_obj, medal_mat)

        # 绶带
        ribbon_color = [0.0, 0.2, 0.8]  # 蓝色绶带（巴黎奥运会风格）
        ribbon_loc = list(attach_location)
        ribbon_loc[2] += 0.06 * scale
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=ribbon_loc
        )
        ribbon = bpy.context.active_object
        ribbon.name = f"{character_name}_{equipment_type}_Ribbon"
        ribbon.scale = [0.015 * scale * 50, 0.002 * 50, 0.05 * scale * 50]
        ribbon_mat = _create_material(f"{character_name}_Ribbon",
                                      ribbon_color + [1.0], roughness=0.7)
        _assign_material(ribbon, ribbon_mat)
        _parent_to(ribbon, equip_obj)

        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "WRISTBAND":
        # 护腕
        wb_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.025 * scale,
            minor_radius=0.008 * scale,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Wristband"
        wb_mat = _create_material(f"{character_name}_Wristband",
                                  wb_color + [1.0], roughness=0.8)
        _assign_material(equip_obj, wb_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "HEADBAND":
        # 头带
        hb_color = color or [1.0, 0.1, 0.1]
        head_obj = bpy.data.objects.get(f"{character_name}_Head")
        head_radius = 0.25  # 默认头部半径
        if head_obj:
            head_radius = max(head_obj.dimensions) / 2
            attach_location = list(head_obj.location)
            attach_location[2] += head_radius * 0.3

        bpy.ops.mesh.primitive_torus_add(
            major_radius=head_radius * 1.05,
            minor_radius=0.01 * scale,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Headband"
        hb_mat = _create_material(f"{character_name}_Headband",
                                  hb_color + [1.0], roughness=0.8)
        _assign_material(equip_obj, hb_mat)
        if head_obj:
            _parent_to(equip_obj, head_obj)

    elif equipment_type == "TROPHY":
        # 奖杯
        trophy_color = color or [1.0, 0.85, 0.0]
        # 杯身
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24,
            radius=0.04 * scale,
            depth=0.12 * scale,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Trophy"
        trophy_mat = _create_material(f"{character_name}_Trophy",
                                      trophy_color + [1.0], metallic=0.95, roughness=0.15)
        _assign_material(equip_obj, trophy_mat)

        # 底座
        base_loc = list(attach_location)
        base_loc[2] -= 0.07 * scale
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24,
            radius=0.03 * scale,
            depth=0.02 * scale,
            location=base_loc
        )
        base = bpy.context.active_object
        base.name = f"{character_name}_Trophy_Base"
        base_mat = _create_material(f"{character_name}_TrophyBase",
                                    [0.15, 0.1, 0.05, 1.0], roughness=0.4)
        _assign_material(base, base_mat)
        _parent_to(base, equip_obj)

        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "TOWEL":
        # 毛巾
        towel_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Towel"
        equip_obj.scale = [0.3 * scale * 50, 0.002 * 50, 0.15 * scale * 50]
        towel_mat = _create_material(f"{character_name}_Towel",
                                     towel_color + [1.0], roughness=0.9)
        _assign_material(equip_obj, towel_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    if equip_obj is None:
        return {
            "success": False,
            "error": {"code": "UNKNOWN_EQUIPMENT", "message": f"未知装备类型: {equipment_type}"}
        }

    return {
        "success": True,
        "data": {
            "equipment_name": equip_obj.name,
            "equipment_type": equipment_type,
            "attached_to": attach_to,
        }
    }


# ==================== 运动服 ====================

def handle_create_uniform(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建运动服"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    team = params.get("team", "CHINA_NATIONAL")
    uniform_style = params.get("uniform_style", "MATCH_JERSEY")
    jersey_number = params.get("jersey_number", 20)
    player_name = params.get("player_name", "FAN ZHENDONG")
    brand = params.get("brand", "Li-Ning")
    custom_primary = params.get("custom_primary_color")
    custom_secondary = params.get("custom_secondary_color")

    # 获取队伍颜色
    if team == "CLUB_CUSTOM" and custom_primary:
        colors = {
            "primary": custom_primary + [1.0] if len(custom_primary) == 3 else custom_primary,
            "secondary": (custom_secondary or [1.0, 1.0, 1.0]) + [1.0] if custom_secondary and len(custom_secondary) == 3 else (custom_secondary or [1.0, 1.0, 1.0, 1.0]),
            "accent": [0.1, 0.1, 0.1, 1.0],
        }
    else:
        colors = TEAM_COLORS.get(team, TEAM_COLORS["CHINA_NATIONAL"])

    # 查找角色身体
    body_obj = bpy.data.objects.get(f"{character_name}_Body")
    if not body_obj:
        return {
            "success": False,
            "error": {"code": "CHARACTER_NOT_FOUND", "message": f"找不到角色: {character_name}"}
        }

    body_loc = list(body_obj.location)
    body_scale = list(body_obj.scale)
    created_items = []

    if uniform_style in ("MATCH_JERSEY", "TRAINING_WEAR"):
        # 球衣上衣
        jersey_color = colors["primary"]
        jersey_mat = _create_material(f"{character_name}_Jersey",
                                      jersey_color, roughness=0.7)

        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[body_loc[0], body_loc[1], body_loc[2]]
        )
        jersey = bpy.context.active_object
        jersey.name = f"{character_name}_Jersey"
        jersey.scale = [
            body_scale[0] * 1.08,
            body_scale[1] * 1.08,
            body_scale[2] * 1.02
        ]
        # 添加细分使衣服更自然
        subsurf = jersey.modifiers.new("Smooth", 'SUBSURF')
        subsurf.levels = 1
        subsurf.render_levels = 1
        _set_smooth_shading(jersey)
        _assign_material(jersey, jersey_mat)
        _parent_to(jersey, body_obj)
        created_items.append(jersey.name)

        # 球裤
        shorts_color = colors.get("accent", [0.1, 0.1, 0.1, 1.0])
        shorts_mat = _create_material(f"{character_name}_Shorts",
                                      shorts_color, roughness=0.7)

        # 查找大腿位置
        thigh_r = bpy.data.objects.get(f"{character_name}_Thigh_R")
        thigh_l = bpy.data.objects.get(f"{character_name}_Thigh_L")
        if thigh_r:
            shorts_z = thigh_r.location[2]
        else:
            shorts_z = body_loc[2] - body_scale[2] * 1.5

        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[body_loc[0], body_loc[1], shorts_z]
        )
        shorts = bpy.context.active_object
        shorts.name = f"{character_name}_Shorts"
        shorts.scale = [
            body_scale[0] * 1.2,
            body_scale[1] * 1.1,
            body_scale[2] * 0.6
        ]
        subsurf = shorts.modifiers.new("Smooth", 'SUBSURF')
        subsurf.levels = 1
        subsurf.render_levels = 1
        _set_smooth_shading(shorts)
        _assign_material(shorts, shorts_mat)
        _parent_to(shorts, body_obj)
        created_items.append(shorts.name)

    elif uniform_style == "AWARD_CEREMONY":
        # 领奖服（白底红条纹夹克）
        jacket_mat = _create_material(f"{character_name}_AwardJacket",
                                      colors["primary"], roughness=0.6)

        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[body_loc[0], body_loc[1], body_loc[2]]
        )
        jacket = bpy.context.active_object
        jacket.name = f"{character_name}_AwardJacket"
        jacket.scale = [
            body_scale[0] * 1.15,
            body_scale[1] * 1.15,
            body_scale[2] * 1.1
        ]
        subsurf = jacket.modifiers.new("Smooth", 'SUBSURF')
        subsurf.levels = 1
        _set_smooth_shading(jacket)
        _assign_material(jacket, jacket_mat)
        _parent_to(jacket, body_obj)
        created_items.append(jacket.name)

        # 运动裤（白色）
        pants_mat = _create_material(f"{character_name}_AwardPants",
                                     colors["primary"], roughness=0.6)
        thigh_r = bpy.data.objects.get(f"{character_name}_Thigh_R")
        pants_z = thigh_r.location[2] if thigh_r else body_loc[2] - body_scale[2] * 1.5

        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[body_loc[0], body_loc[1], pants_z]
        )
        pants = bpy.context.active_object
        pants.name = f"{character_name}_AwardPants"
        pants.scale = [
            body_scale[0] * 1.1,
            body_scale[1] * 1.05,
            body_scale[2] * 0.8
        ]
        subsurf = pants.modifiers.new("Smooth", 'SUBSURF')
        subsurf.levels = 1
        _set_smooth_shading(pants)
        _assign_material(pants, pants_mat)
        _parent_to(pants, body_obj)
        created_items.append(pants.name)

    elif uniform_style == "WARMUP_JACKET":
        # 热身外套
        jacket_mat = _create_material(f"{character_name}_WarmupJacket",
                                      colors["primary"], roughness=0.55)

        bpy.ops.mesh.primitive_cube_add(
            size=0.01,
            location=[body_loc[0], body_loc[1], body_loc[2] + body_scale[2] * 0.1]
        )
        jacket = bpy.context.active_object
        jacket.name = f"{character_name}_WarmupJacket"
        jacket.scale = [
            body_scale[0] * 1.2,
            body_scale[1] * 1.2,
            body_scale[2] * 1.15
        ]
        subsurf = jacket.modifiers.new("Smooth", 'SUBSURF')
        subsurf.levels = 1
        _set_smooth_shading(jacket)
        _assign_material(jacket, jacket_mat)
        _parent_to(jacket, body_obj)
        created_items.append(jacket.name)

    return {
        "success": True,
        "data": {
            "team": team,
            "uniform_style": uniform_style,
            "jersey_number": jersey_number,
            "player_name": player_name,
            "items_created": created_items,
        }
    }


# ==================== 运动姿势 ====================

def handle_set_pose(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置运动姿势"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    pose = params.get("pose", "READY_STANCE")
    intensity = params.get("intensity", 1.0)
    mirror = params.get("mirror", False)
    add_motion_trail = params.get("add_motion_trail", False)

    # 获取姿势数据
    pose_data = SPORT_POSES.get(pose)
    if not pose_data:
        return {
            "success": False,
            "error": {"code": "UNKNOWN_POSE", "message": f"未知姿势: {pose}"}
        }

    # 查找骨骼
    armature_obj = bpy.data.objects.get(f"{character_name}_Armature")
    if not armature_obj:
        return {
            "success": False,
            "error": {"code": "NO_ARMATURE", "message": f"找不到角色骨骼: {character_name}_Armature"}
        }

    # 进入Pose模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    applied_bones = []

    for bone_name, rotation in pose_data.items():
        if bone_name == "description":
            continue
        if not isinstance(rotation, tuple):
            continue

        # 镜像处理：交换L和R
        actual_bone_name = bone_name
        if mirror:
            if ".R" in bone_name:
                actual_bone_name = bone_name.replace(".R", ".L")
            elif ".L" in bone_name:
                actual_bone_name = bone_name.replace(".L", ".R")

        pose_bone = armature_obj.pose.bones.get(actual_bone_name)
        if pose_bone:
            # 应用旋转（带强度）
            rx = math.radians(rotation[0] * intensity)
            ry = math.radians(rotation[1] * intensity)
            rz = math.radians(rotation[2] * intensity)

            pose_bone.rotation_mode = 'XYZ'
            pose_bone.rotation_euler = (rx, ry, rz)
            applied_bones.append(actual_bone_name)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 运动轨迹效果（可选）
    has_motion_trail = False
    if add_motion_trail and pose in ("FOREHAND_ATTACK", "BACKHAND_ATTACK",
                                      "FOREHAND_LOOP", "SERVE_HIT"):
        # 创建弧形轨迹
        try:
            hand_obj = bpy.data.objects.get(f"{character_name}_Hand_R")
            if hand_obj:
                trail_points = []
                hand_loc = list(hand_obj.location)
                for i in range(5):
                    t = i / 4.0
                    trail_points.append((
                        hand_loc[0] + math.sin(t * math.pi) * 0.3,
                        hand_loc[1] - t * 0.2,
                        hand_loc[2] + math.cos(t * math.pi) * 0.1
                    ))

                curve_data = bpy.data.curves.new(f"{character_name}_MotionTrail", 'CURVE')
                curve_data.dimensions = '3D'
                spline = curve_data.splines.new('BEZIER')
                spline.bezier_points.add(len(trail_points) - 1)
                for i, point in enumerate(trail_points):
                    spline.bezier_points[i].co = point

                trail_obj = bpy.data.objects.new(f"{character_name}_MotionTrail", curve_data)
                bpy.context.collection.objects.link(trail_obj)
                curve_data.bevel_depth = 0.005
                trail_mat = _create_material(f"{character_name}_TrailMat",
                                             [1.0, 1.0, 1.0, 0.5], roughness=0.1)
                trail_obj.data.materials.append(trail_mat)
                has_motion_trail = True
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "pose": pose,
            "description": pose_data.get("description", ""),
            "applied_bones": applied_bones,
            "intensity": intensity,
            "mirrored": mirror,
            "has_motion_trail": has_motion_trail,
        }
    }


# ==================== 参考图加载 ====================

def handle_load_reference(params: Dict[str, Any]) -> Dict[str, Any]:
    """加载参考图"""
    _ensure_object_mode()

    image_path = params.get("image_path", "")
    view = params.get("view", "FRONT")
    opacity = params.get("opacity", 0.5)
    offset_x = params.get("offset_x", 0.0)
    offset_y = params.get("offset_y", 0.0)
    scale = params.get("scale", 1.0)

    # 检查文件是否存在
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"文件不存在: {image_path}"}
        }

    # 加载图像
    try:
        image = bpy.data.images.load(image_path)
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LOAD_ERROR", "message": f"加载图像失败: {str(e)}"}
        }

    image_name = os.path.basename(image_path)

    # 创建空物体作为参考图载体
    bpy.ops.object.empty_add(type='IMAGE', location=[offset_x, offset_y, 0])
    ref_obj = bpy.context.active_object
    ref_obj.name = f"Ref_{view}_{image_name}"
    ref_obj.data = image
    ref_obj.empty_display_size = scale
    ref_obj.empty_image_depth = 'BACK'
    ref_obj.color[3] = opacity

    # 根据视角旋转
    if view == "FRONT":
        ref_obj.rotation_euler = (math.pi / 2, 0, 0)
        ref_obj.location = (offset_x, -2, offset_y)
    elif view == "SIDE":
        ref_obj.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        ref_obj.location = (2, offset_x, offset_y)
    elif view == "BACK":
        ref_obj.rotation_euler = (math.pi / 2, 0, math.pi)
        ref_obj.location = (offset_x, 2, offset_y)
    elif view == "THREE_QUARTER":
        ref_obj.rotation_euler = (math.pi / 2, 0, math.pi / 4)
        ref_obj.location = (offset_x + 1.4, offset_y - 1.4, 0)

    # 设置为不可选择（避免干扰建模）
    ref_obj.hide_select = True

    return {
        "success": True,
        "data": {
            "image_name": image_name,
            "object_name": ref_obj.name,
            "view": view,
            "opacity": opacity,
        }
    }


# ==================== 模型优化 ====================

def handle_optimize_model(params: Dict[str, Any]) -> Dict[str, Any]:
    """优化运动角色模型"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    target = params.get("target", "WEB")
    target_tris = params.get("target_tris") or PLATFORM_TRI_DEFAULTS.get(target, 4000)
    texture_size = params.get("texture_size", 1024)
    generate_lod = params.get("generate_lod", False)
    lod_levels = params.get("lod_levels", 3)
    export_glb = params.get("export_glb", True)
    export_path = params.get("export_path")
    apply_draco = params.get("apply_draco_compression", True)

    # 查找角色所有网格对象
    root_obj = bpy.data.objects.get(f"{character_name}_Root")
    if not root_obj:
        # 尝试直接查找名称匹配的对象
        matching_objs = [obj for obj in bpy.data.objects if obj.name.startswith(character_name) and obj.type == 'MESH']
        if not matching_objs:
            return {
                "success": False,
                "error": {"code": "CHARACTER_NOT_FOUND", "message": f"找不到角色: {character_name}"}
            }
    else:
        matching_objs = [obj for obj in bpy.data.objects
                         if obj.name.startswith(character_name) and obj.type == 'MESH']

    # 统计原始面数
    original_tris = 0
    for obj in matching_objs:
        if obj.type == 'MESH':
            # 每个quad大约2个三角面
            original_tris += len(obj.data.polygons) * 2

    # 应用减面修改器
    if original_tris > target_tris and target != "PRINT_3D":
        ratio = target_tris / max(original_tris, 1)
        for obj in matching_objs:
            if obj.type == 'MESH' and len(obj.data.polygons) > 10:
                decimate = obj.modifiers.new("Decimate", 'DECIMATE')
                decimate.ratio = max(0.1, ratio)

    # 清理: 移除孤立顶点
    for obj in matching_objs:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            try:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete_loose()
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                _ensure_object_mode()

    # 统计最终面数
    final_tris = 0
    for obj in matching_objs:
        if obj.type == 'MESH':
            # 评估修改器后的面数
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            final_tris += len(eval_obj.data.polygons) * 2

    # LOD生成（可选）
    lod_count = 0
    if generate_lod:
        for level in range(1, lod_levels + 1):
            lod_ratio = 1.0 / (2 ** level)
            for obj in matching_objs:
                if obj.type == 'MESH' and len(obj.data.polygons) > 20:
                    # 复制对象
                    lod_obj = obj.copy()
                    lod_obj.data = obj.data.copy()
                    lod_obj.name = f"{obj.name}_LOD{level}"
                    bpy.context.collection.objects.link(lod_obj)

                    # 添加减面
                    decimate = lod_obj.modifiers.new(f"LOD{level}", 'DECIMATE')
                    decimate.ratio = max(0.05, lod_ratio)

                    # 隐藏LOD对象
                    lod_obj.hide_viewport = True
                    lod_obj.hide_render = True
                    lod_count += 1

    # GLB导出（可选）
    exported_path = None
    if export_glb:
        if not export_path:
            blend_path = bpy.data.filepath
            if blend_path:
                export_path = os.path.join(
                    os.path.dirname(blend_path),
                    f"{character_name}.glb"
                )
            else:
                export_path = os.path.join(
                    os.path.expanduser("~"),
                    f"{character_name}.glb"
                )

        try:
            # 选择角色对象
            bpy.ops.object.select_all(action='DESELECT')
            for obj in matching_objs:
                obj.select_set(True)
            # 也选择骨骼
            armature = bpy.data.objects.get(f"{character_name}_Armature")
            if armature:
                armature.select_set(True)

            # 导出GLB
            export_settings = {
                'filepath': export_path,
                'use_selection': True,
                'export_format': 'GLB',
                'export_apply': True,
            }

            # Draco压缩
            if apply_draco:
                export_settings['export_draco_mesh_compression_enable'] = True
                export_settings['export_draco_mesh_compression_level'] = 6

            bpy.ops.export_scene.gltf(**export_settings)
            exported_path = export_path

        except Exception as e:
            # 导出失败不影响其他结果
            pass

    return {
        "success": True,
        "data": {
            "character_name": character_name,
            "target": target,
            "original_tris": original_tris,
            "final_tris": final_tris,
            "texture_size": texture_size,
            "lod_count": lod_count,
            "export_path": exported_path,
        }
    }


# ==================== 场景设置 ====================

def handle_setup_scene(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置运动场景"""
    _ensure_object_mode()

    scene_type = params.get("scene_type", "PORTRAIT")
    character_name = params.get("character_name")
    background_color = params.get("background_color")
    use_hdri = params.get("use_hdri", False)
    camera_distance = params.get("camera_distance", 3.0)
    render_engine = params.get("render_engine", "EEVEE")

    scene = bpy.context.scene
    lights_count = 0

    # 设置渲染引擎
    if render_engine == "CYCLES":
        scene.render.engine = 'CYCLES'
    else:
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'ShaderNodeBsdfPrincipled') else 'BLENDER_EEVEE'

    # 设置色彩管理
    try:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'Medium Contrast'
    except Exception:
        pass

    # 删除默认灯光
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT' and obj.name in ('Light', 'Lamp'):
            bpy.data.objects.remove(obj, do_unlink=True)

    # 背景颜色
    if background_color:
        world = scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            scene.world = world
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs["Color"].default_value = background_color + [1.0] if len(background_color) == 3 else background_color

    # 根据场景类型设置灯光
    if scene_type == "PORTRAIT":
        # 三点布光：肖像展示
        # 主光（暖色，45度侧前方）
        bpy.ops.object.light_add(type='AREA', location=(2, -2, 3))
        key_light = bpy.context.active_object
        key_light.name = "KeyLight"
        key_light.data.energy = 200
        key_light.data.color = (1.0, 0.95, 0.9)  # 暖色
        key_light.data.size = 2
        key_light.rotation_euler = (math.radians(45), 0, math.radians(45))
        lights_count += 1

        # 辅光（冷色，对侧）
        bpy.ops.object.light_add(type='AREA', location=(-2, -1.5, 2))
        fill_light = bpy.context.active_object
        fill_light.name = "FillLight"
        fill_light.data.energy = 80
        fill_light.data.color = (0.9, 0.95, 1.0)  # 冷色
        fill_light.data.size = 3
        fill_light.rotation_euler = (math.radians(30), 0, math.radians(-30))
        lights_count += 1

        # 轮廓光（背面）
        bpy.ops.object.light_add(type='AREA', location=(0, 2, 2.5))
        rim_light = bpy.context.active_object
        rim_light.name = "RimLight"
        rim_light.data.energy = 150
        rim_light.data.color = (1.0, 1.0, 1.0)
        rim_light.data.size = 1
        rim_light.rotation_euler = (math.radians(60), 0, math.radians(180))
        lights_count += 1

    elif scene_type == "PRODUCT":
        # 产品/手办展示灯光
        # 顶部环境光
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 4))
        top_light = bpy.context.active_object
        top_light.name = "TopLight"
        top_light.data.energy = 150
        top_light.data.size = 4
        top_light.rotation_euler = (0, 0, 0)
        lights_count += 1

        # 前侧光
        bpy.ops.object.light_add(type='AREA', location=(1.5, -2, 1.5))
        front_light = bpy.context.active_object
        front_light.name = "FrontLight"
        front_light.data.energy = 100
        front_light.data.color = (1.0, 0.98, 0.95)
        front_light.data.size = 2
        front_light.rotation_euler = (math.radians(30), 0, math.radians(30))
        lights_count += 1

        # 底部补光（产品展示特有）
        bpy.ops.object.light_add(type='AREA', location=(0, -1, -0.5))
        bottom_light = bpy.context.active_object
        bottom_light.name = "BottomFill"
        bottom_light.data.energy = 30
        bottom_light.data.size = 3
        bottom_light.rotation_euler = (math.radians(-60), 0, 0)
        lights_count += 1

        # 展示底座
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.5,
            depth=0.05,
            location=(0, 0, -0.025)
        )
        base = bpy.context.active_object
        base.name = "DisplayBase"
        base_mat = _create_material("DisplayBase", [0.1, 0.1, 0.1, 1.0],
                                    metallic=0.3, roughness=0.2)
        _assign_material(base, base_mat)

    elif scene_type == "MATCH":
        # 比赛场景灯光（体育馆顶部灯光）
        for i, x_offset in enumerate([-2, 0, 2]):
            bpy.ops.object.light_add(type='AREA', location=(x_offset, 0, 5))
            light = bpy.context.active_object
            light.name = f"StadiumLight_{i}"
            light.data.energy = 300
            light.data.color = (1.0, 1.0, 0.98)
            light.data.size = 3
            lights_count += 1

        # 侧面补光
        bpy.ops.object.light_add(type='AREA', location=(4, -3, 2))
        side_light = bpy.context.active_object
        side_light.name = "SideLight"
        side_light.data.energy = 80
        side_light.data.size = 4
        lights_count += 1

    elif scene_type == "AWARD_CEREMONY":
        # 颁奖场景
        # 聚光灯（颁奖特效）
        bpy.ops.object.light_add(type='SPOT', location=(0, -3, 5))
        spot = bpy.context.active_object
        spot.name = "AwardSpotlight"
        spot.data.energy = 500
        spot.data.spot_size = math.radians(30)
        spot.data.color = (1.0, 0.95, 0.85)
        spot.rotation_euler = (math.radians(30), 0, 0)
        lights_count += 1

        # 环境补光
        bpy.ops.object.light_add(type='AREA', location=(2, -1, 3))
        fill = bpy.context.active_object
        fill.name = "AwardFill"
        fill.data.energy = 100
        fill.data.size = 3
        lights_count += 1

        # 领奖台
        for pos, h, color in [
            ((0, 0, 0), 0.3, [1.0, 0.85, 0.0, 1.0]),    # 金牌位（中间，最高）
            ((-0.6, 0, 0), 0.2, [0.75, 0.75, 0.8, 1.0]),  # 银牌位
            ((0.6, 0, 0), 0.15, [0.7, 0.45, 0.2, 1.0]),   # 铜牌位
        ]:
            bpy.ops.mesh.primitive_cube_add(
                size=0.01,
                location=(pos[0], pos[1], h / 2)
            )
            podium = bpy.context.active_object
            podium.name = f"Podium_{pos[0]}"
            podium.scale = [0.25 * 50, 0.2 * 50, h / 2 * 50]
            podium_mat = _create_material(f"Podium_{pos[0]}", color, roughness=0.3)
            _assign_material(podium, podium_mat)

    elif scene_type == "TRAINING":
        # 训练场景
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 4))
        overhead = bpy.context.active_object
        overhead.name = "TrainingLight"
        overhead.data.energy = 200
        overhead.data.size = 5
        lights_count += 1

        bpy.ops.object.light_add(type='AREA', location=(3, -2, 2))
        side = bpy.context.active_object
        side.name = "TrainingSide"
        side.data.energy = 60
        side.data.size = 3
        lights_count += 1

    # 设置相机
    # 删除默认相机
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA' and obj.name == 'Camera':
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_height = 1.0 if scene_type in ("PORTRAIT", "PRODUCT") else 1.5
    bpy.ops.object.camera_add(
        location=(0, -camera_distance, cam_height),
        rotation=(math.radians(80), 0, 0)
    )
    camera = bpy.context.active_object
    camera.name = "SportCamera"
    scene.camera = camera

    # 如果有角色，相机追踪角色
    if character_name:
        target_obj = bpy.data.objects.get(f"{character_name}_Root") or \
                     bpy.data.objects.get(f"{character_name}_Body")
        if target_obj:
            constraint = camera.constraints.new('TRACK_TO')
            constraint.target = target_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

    return {
        "success": True,
        "data": {
            "scene_type": scene_type,
            "render_engine": render_engine,
            "lights_count": lights_count,
            "camera_distance": camera_distance,
        }
    }
