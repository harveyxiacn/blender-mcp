"""
Sport Character Handler

Handles athlete character creation, equipment addition, sportswear, sport poses,
reference image loading, model optimization and other commands.
Optimized for table tennis player (especially Fan Zhendong) 3D model creation.
"""

import contextlib
import math
import os
from typing import Any

import bpy

from .compat import get_eevee_engine

# ==================== Configuration Data ====================

# Sport character style configuration
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

# Athlete preset configuration
ATHLETE_PRESETS = {
    "FAN_ZHENDONG": {
        "name": "FanZhendong",
        "height_real": 1.72,  # Real height 172cm
        "build": "athletic",
        "skin_color": [0.95, 0.82, 0.72, 1.0],  # Asian skin tone
        "hair_color": [0.05, 0.03, 0.02, 1.0],  # Black short hair
        "hair_style": "short",
        "eye_color": [0.15, 0.08, 0.05, 1.0],  # Dark brown eyes
        "face_features": {
            "face_shape": "round",  # Round face
            "eyebrow_thickness": 1.2,  # Thick eyebrows
            "eye_size": 1.1,  # Large eyes
            "nose_size": 1.0,  # Standard nose
            "mouth_width": 1.0,  # Standard mouth
            "jaw_width": 1.1,  # Slightly wide jaw
            "ear_size": 1.1,  # Slightly large ears (chibi feature)
        },
        "jersey_number": 20,
        "brand": "Li-Ning",
    },
}

# Team color configuration
TEAM_COLORS = {
    "CHINA_NATIONAL": {
        "primary": [0.85, 0.1, 0.1, 1.0],  # China red
        "secondary": [1.0, 0.85, 0.0, 1.0],  # Gold
        "accent": [1.0, 1.0, 1.0, 1.0],  # White
    },
    "CHINA_NATIONAL_BLUE": {
        "primary": [0.1, 0.2, 0.7, 1.0],  # Dark blue
        "secondary": [0.3, 0.5, 0.9, 1.0],  # Light blue
        "accent": [1.0, 1.0, 1.0, 1.0],  # White
    },
    "CHINA_NATIONAL_WHITE": {
        "primary": [1.0, 1.0, 1.0, 1.0],  # White
        "secondary": [0.85, 0.1, 0.1, 1.0],  # Red stripes
        "accent": [0.1, 0.1, 0.1, 1.0],  # Black
    },
    "CLUB_SHENZHEN": {
        "primary": [0.0, 0.5, 0.8, 1.0],  # Sky blue
        "secondary": [1.0, 1.0, 1.0, 1.0],  # White
        "accent": [0.1, 0.1, 0.1, 1.0],  # Black
    },
    "TRAINING": {
        "primary": [0.2, 0.2, 0.2, 1.0],  # Dark gray
        "secondary": [0.85, 0.1, 0.1, 1.0],  # Red
        "accent": [1.0, 1.0, 1.0, 1.0],  # White
    },
}

# Table tennis sport pose bone rotation data (Euler XYZ in degrees)
SPORT_POSES = {
    "READY_STANCE": {
        "description": "Ready stance",
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
        "description": "Forehand attack",
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
        "description": "Backhand topspin",
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
        "description": "Serve toss",
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
        "description": "Serve hit",
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
        "description": "Forehand loop",
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
        "description": "Arms raised celebration",
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
        "description": "Fist pump yell (Fan Zhendong signature move)",
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
        "description": "Holding up medal with both hands",
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
        "description": "Podium stance",
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

# Platform default face counts
PLATFORM_TRI_DEFAULTS = {
    "WEB": 4000,
    "MOBILE": 6000,
    "PC_CONSOLE": 15000,
    "PRINT_3D": 100000,
}


# ==================== Utility Functions ====================


def _get_principled_bsdf(nodes):
    """Get Principled BSDF node (compatible with all Blender locales)"""
    for node in nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def _create_material(
    name: str,
    color: list[float],
    metallic: float = 0.0,
    roughness: float = 0.5,
    specular: float = 0.5,
) -> bpy.types.Material:
    """Create PBR material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    bsdf = _get_principled_bsdf(mat.node_tree.nodes)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color if len(color) == 4 else color + [1.0]
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        # Specular may have a different name in newer versions
        try:
            bsdf.inputs["Specular IOR Level"].default_value = specular
        except (KeyError, IndexError):
            with contextlib.suppress(KeyError, IndexError):
                bsdf.inputs["Specular"].default_value = specular

    return mat


def _assign_material(obj, material) -> None:
    """Assign material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def _ensure_object_mode() -> None:
    """Ensure in Object mode"""
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _deselect_all() -> None:
    """Deselect all objects"""
    bpy.ops.object.select_all(action="DESELECT")


def _set_smooth_shading(obj) -> None:
    """Set smooth shading (compatible across versions)"""
    try:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    except Exception:
        pass


def _parent_to(child_obj, parent_obj, keep_transform=True) -> None:
    """Set parent-child relationship"""
    child_obj.parent = parent_obj
    if keep_transform:
        child_obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()


# ==================== Character Creation ====================


def handle_create_character(params: dict[str, Any]) -> dict[str, Any]:
    """Create sport character"""
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

    # Get style configuration
    config = STYLE_CONFIG.get(style, STYLE_CONFIG["CHIBI"]).copy()
    if head_body_ratio_override:
        config["head_body_ratio"] = head_body_ratio_override

    # Get athlete preset
    athlete = None
    if preset != "CUSTOM" and preset in ATHLETE_PRESETS:
        athlete = ATHLETE_PRESETS[preset]
        if not skin_color:
            skin_color = athlete["skin_color"]

    if not skin_color:
        skin_color = [0.95, 0.82, 0.72, 1.0]  # Default Asian skin tone

    # Build modifier
    build_modifiers = {
        "slim": {"body_width": 0.85, "limb_thick": 0.9},
        "athletic": {"body_width": 1.0, "limb_thick": 1.0},
        "muscular": {"body_width": 1.15, "limb_thick": 1.15},
        "stocky": {"body_width": 1.1, "limb_thick": 1.2},
    }
    build_mod = build_modifiers.get(build, build_modifiers["athletic"])

    # Calculate scale
    ratio = config["head_body_ratio"]
    scale_factor = height / 1.7

    created_parts = []

    # Create root empty
    root_empty = bpy.data.objects.new(f"{name}_Root", None)
    bpy.context.collection.objects.link(root_empty)
    root_empty.empty_display_type = "ARROWS"
    root_empty.empty_display_size = 0.1

    # Create skin material (SSS suitable for skin rendering)
    skin_mat = _create_material(f"{name}_Skin", skin_color, roughness=0.75)
    # Add SSS to skin
    bsdf = _get_principled_bsdf(skin_mat.node_tree.nodes)
    if bsdf:
        try:
            bsdf.inputs["Subsurface Weight"].default_value = 0.15
        except (KeyError, IndexError):
            with contextlib.suppress(KeyError, IndexError):
                bsdf.inputs["Subsurface"].default_value = 0.15

    # Determine subdivision level based on face count budget
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

    # ========== Head ==========
    head_z = height * (1 - 1 / ratio)
    head_radius = 0.25 * scale_factor * config["head_scale"][0] * config["face_roundness"]

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=sphere_segments,
        ring_count=sphere_rings,
        radius=head_radius,
        location=[0, 0, head_z],
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.scale = list(config["head_scale"])
    _set_smooth_shading(head)
    _assign_material(head, skin_mat)
    _parent_to(head, root_empty)
    created_parts.append(head.name)

    # ========== Eyes (chibi and anime need large eyes) ==========
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
        # Eye white
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(12, sphere_segments // 2),
            ring_count=max(8, sphere_rings // 2),
            radius=eye_size * 1.3,
            location=[x_offset, eye_y, eye_z],
        )
        eye_white = bpy.context.active_object
        eye_white.name = f"{name}_EyeWhite_{side}"
        _set_smooth_shading(eye_white)
        _assign_material(eye_white, eye_white_mat)
        _parent_to(eye_white, head)

        # Pupil
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(12, sphere_segments // 2),
            ring_count=max(8, sphere_rings // 2),
            radius=eye_size,
            location=[x_offset, eye_y - eye_size * 0.3, eye_z],
        )
        eye_pupil = bpy.context.active_object
        eye_pupil.name = f"{name}_Eye_{side}"
        _set_smooth_shading(eye_pupil)
        _assign_material(eye_pupil, eye_mat)
        _parent_to(eye_pupil, head)

    created_parts.append(f"{name}_Eyes")

    # ========== Nose ==========
    nose_size = 0.03 * scale_factor
    if style == "CHIBI":
        nose_size *= 0.6  # Chibi nose is smaller
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=max(8, sphere_segments // 3),
        ring_count=max(6, sphere_rings // 3),
        radius=nose_size,
        location=[0, eye_y - nose_size, eye_z - head_radius * 0.3],
    )
    nose = bpy.context.active_object
    nose.name = f"{name}_Nose"
    nose.scale = [1.0, 0.6, 0.8]
    _set_smooth_shading(nose)
    # Slightly red nose (chibi feature)
    nose_color = list(skin_color[:3])
    nose_color[0] = min(1.0, nose_color[0] * 1.15)
    nose_mat = _create_material(f"{name}_Nose", nose_color + [1.0], roughness=0.7)
    _assign_material(nose, nose_mat)
    _parent_to(nose, head)
    created_parts.append(f"{name}_Nose")

    # ========== Mouth ==========
    mouth_width = 0.06 * scale_factor
    mouth_z = eye_z - head_radius * 0.55
    bpy.ops.mesh.primitive_cube_add(size=0.01, location=[0, eye_y, mouth_z])
    mouth = bpy.context.active_object
    mouth.name = f"{name}_Mouth"
    mouth.scale = [mouth_width * 10, 0.3, 0.2]
    mouth_mat = _create_material(f"{name}_Mouth", [0.7, 0.3, 0.3, 1.0], roughness=0.6)
    _assign_material(mouth, mouth_mat)
    _parent_to(mouth, head)
    created_parts.append(f"{name}_Mouth")

    # ========== Ears ==========
    ear_size = 0.06 * scale_factor
    if athlete and "face_features" in athlete:
        ear_size *= athlete["face_features"].get("ear_size", 1.0)

    for side, x_mult in [("R", 1), ("L", -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=ear_size,
            location=[x_mult * head_radius * 0.95, 0, eye_z - head_radius * 0.15],
        )
        ear = bpy.context.active_object
        ear.name = f"{name}_Ear_{side}"
        ear.scale = [0.4, 0.6, 1.0]
        _set_smooth_shading(ear)
        _assign_material(ear, skin_mat)
        _parent_to(ear, head)

    created_parts.append(f"{name}_Ears")

    # ========== Hair ==========
    hair_color = [0.05, 0.03, 0.02, 1.0]  # Default black
    if athlete and "hair_color" in athlete:
        hair_color = athlete["hair_color"]
    hair_mat = _create_material(f"{name}_Hair", hair_color, roughness=0.8)

    # Hair composed of multiple spheres (chibi style)
    hair_base_z = head_z + head_radius * 0.3
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=sphere_segments,
        ring_count=sphere_rings,
        radius=head_radius * 1.08,
        location=[0, 0, hair_base_z],
    )
    hair_base = bpy.context.active_object
    hair_base.name = f"{name}_Hair"
    hair_base.scale = [1.05, 1.0, 0.9]
    _set_smooth_shading(hair_base)
    _assign_material(hair_base, hair_mat)
    _parent_to(hair_base, head)

    # Bangs (short fringe hair)
    for i, (x, y_off) in enumerate(
        [(-0.3, -0.2), (0, -0.3), (0.3, -0.2), (-0.15, -0.25), (0.15, -0.25)]
    ):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=head_radius * 0.25,
            location=[
                x * head_radius,
                y_off * head_radius - head_radius * 0.6,
                hair_base_z + head_radius * 0.1,
            ],
        )
        bang = bpy.context.active_object
        bang.name = f"{name}_HairBang_{i}"
        bang.scale = [0.8, 0.5, 1.2]
        _set_smooth_shading(bang)
        _assign_material(bang, hair_mat)
        _parent_to(bang, hair_base)

    created_parts.append(f"{name}_Hair")

    # ========== Body ==========
    body_z = height * 0.38
    body_width = config["body_scale"][0] * scale_factor * 0.3 * build_mod["body_width"]
    body_depth = config["body_scale"][1] * scale_factor * 0.2
    body_height = config["body_scale"][2] * scale_factor * 0.35

    bpy.ops.mesh.primitive_cube_add(location=[0, 0, body_z])
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = [body_width, body_depth, body_height]
    # Add subdivision modifier for rounder body
    if subdivisions > 0:
        subsurf = body.modifiers.new("Subdivide", "SUBSURF")
        subsurf.levels = subdivisions
        subsurf.render_levels = subdivisions
    _set_smooth_shading(body)
    _assign_material(body, skin_mat)
    _parent_to(body, root_empty)
    created_parts.append(f"{name}_Body")

    # ========== Arms ==========
    arm_thickness = config["limb_thickness"] * scale_factor * build_mod["limb_thick"]
    arm_length = height * 0.2
    shoulder_z = body_z + body_height * 0.8

    for side, x_mult in [("R", 1), ("L", -1)]:
        shoulder_x = x_mult * (body_width + arm_thickness * 0.5)

        # Upper arm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=arm_thickness,
            depth=arm_length,
            location=[shoulder_x, 0, shoulder_z - arm_length * 0.4],
        )
        upper_arm = bpy.context.active_object
        upper_arm.name = f"{name}_UpperArm_{side}"
        _set_smooth_shading(upper_arm)
        _assign_material(upper_arm, skin_mat)
        _parent_to(upper_arm, body)

        # Forearm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=arm_thickness * 0.85,
            depth=arm_length * 0.9,
            location=[shoulder_x, 0, shoulder_z - arm_length * 1.2],
        )
        forearm = bpy.context.active_object
        forearm.name = f"{name}_Forearm_{side}"
        _set_smooth_shading(forearm)
        _assign_material(forearm, skin_mat)
        _parent_to(forearm, body)

        # Hand
        hand_scale = config["hand_scale"]
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=max(8, sphere_segments // 3),
            ring_count=max(6, sphere_rings // 3),
            radius=arm_thickness * hand_scale,
            location=[shoulder_x, 0, shoulder_z - arm_length * 1.7],
        )
        hand = bpy.context.active_object
        hand.name = f"{name}_Hand_{side}"
        hand.scale = [1.0, 0.6, 1.2]
        _set_smooth_shading(hand)
        _assign_material(hand, skin_mat)
        _parent_to(hand, body)

    created_parts.append(f"{name}_Arms")

    # ========== Legs ==========
    leg_thickness = config["limb_thickness"] * scale_factor * 1.1 * build_mod["limb_thick"]
    leg_length = height * 0.22
    hip_z = body_z - body_height * 0.8

    for side, x_mult in [("R", 1), ("L", -1)]:
        leg_x = x_mult * body_width * 0.5

        # Thigh
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_thickness, depth=leg_length, location=[leg_x, 0, hip_z - leg_length * 0.3]
        )
        thigh = bpy.context.active_object
        thigh.name = f"{name}_Thigh_{side}"
        _set_smooth_shading(thigh)
        _assign_material(thigh, skin_mat)
        _parent_to(thigh, body)

        # Shin
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_thickness * 0.85,
            depth=leg_length,
            location=[leg_x, 0, hip_z - leg_length * 1.2],
        )
        shin = bpy.context.active_object
        shin.name = f"{name}_Shin_{side}"
        _set_smooth_shading(shin)
        _assign_material(shin, skin_mat)
        _parent_to(shin, body)

        # Foot
        foot_scale = config["foot_scale"]
        bpy.ops.mesh.primitive_cube_add(
            size=0.01, location=[leg_x, -leg_thickness * 0.3, hip_z - leg_length * 2.0]
        )
        foot = bpy.context.active_object
        foot.name = f"{name}_Foot_{side}"
        foot.scale = [
            leg_thickness * 8 * foot_scale,
            leg_thickness * 15 * foot_scale,
            leg_thickness * 5,
        ]
        if subdivisions > 0:
            subsurf = foot.modifiers.new("Subdivide", "SUBSURF")
            subsurf.levels = 1
            subsurf.render_levels = 1
        _set_smooth_shading(foot)
        # Shoe material
        shoe_mat = _create_material(f"{name}_Shoe", [0.1, 0.1, 0.9, 1.0], roughness=0.6)
        _assign_material(foot, shoe_mat)
        _parent_to(foot, body)

    created_parts.append(f"{name}_Legs")

    # ========== Armature (optional) ==========
    has_armature = False
    if create_armature:
        try:
            # Create armature
            bpy.ops.object.armature_add(location=[0, 0, 0])
            armature_obj = bpy.context.active_object
            armature_obj.name = f"{name}_Armature"
            armature = armature_obj.data
            armature.name = f"{name}_Armature"

            # Enter edit mode to add bones
            bpy.ops.object.mode_set(mode="EDIT")

            # Root bone
            root_bone = armature.edit_bones[0]
            root_bone.name = "root"
            root_bone.head = (0, 0, 0)
            root_bone.tail = (0, 0, hip_z)

            # Spine
            spine = armature.edit_bones.new("spine")
            spine.head = (0, 0, hip_z)
            spine.tail = (0, 0, body_z)
            spine.parent = root_bone

            spine_001 = armature.edit_bones.new("spine.001")
            spine_001.head = (0, 0, body_z)
            spine_001.tail = (0, 0, shoulder_z)
            spine_001.parent = spine

            # Head
            head_bone = armature.edit_bones.new("head")
            head_bone.head = (0, 0, shoulder_z)
            head_bone.tail = (0, 0, head_z + head_radius)
            head_bone.parent = spine_001

            # Arm bones
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

            # Leg bones
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

            bpy.ops.object.mode_set(mode="OBJECT")

            _parent_to(armature_obj, root_empty)
            has_armature = True
            created_parts.append(f"{name}_Armature")

        except Exception:
            _ensure_object_mode()
            # Armature creation failure does not affect the rest
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
        },
    }


# ==================== Equipment Addition ====================


def handle_add_equipment(params: dict[str, Any]) -> dict[str, Any]:
    """Add sport equipment"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    equipment_type = params.get("equipment_type", "PADDLE")
    attach_to = params.get("attach_to", "auto")
    color = params.get("color")
    secondary_color = params.get("secondary_color")
    scale = params.get("scale", 1.0)

    # Find character root object
    root_obj = bpy.data.objects.get(f"{character_name}_Root")
    bpy.data.objects.get(f"{character_name}_Hand_R")

    # Auto-determine attachment position
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

    # Get attachment point location
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
        # Table tennis paddle
        paddle_color = color or [0.8, 0.1, 0.1]
        handle_color = secondary_color or [0.5, 0.3, 0.1]

        # Blade face
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.08 * scale, depth=0.01 * scale, location=attach_location
        )
        blade = bpy.context.active_object
        blade.name = f"{character_name}_Paddle_Blade"
        blade.scale[2] = 0.3  # Flat
        blade_mat = _create_material(
            f"{character_name}_PaddleRubber", paddle_color + [1.0], roughness=0.9
        )
        _assign_material(blade, blade_mat)

        # Handle
        handle_loc = list(attach_location)
        handle_loc[2] -= 0.1 * scale
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.015 * scale, depth=0.08 * scale, location=handle_loc
        )
        handle = bpy.context.active_object
        handle.name = f"{character_name}_Paddle_Handle"
        handle_mat = _create_material(
            f"{character_name}_PaddleHandle", handle_color + [1.0], roughness=0.6
        )
        _assign_material(handle, handle_mat)

        # Combine
        _parent_to(handle, blade)
        equip_obj = blade
        if parent_obj:
            _parent_to(blade, parent_obj)

    elif equipment_type == "BALL":
        # Table tennis ball
        ball_color = color or [1.0, 0.6, 0.0]  # Orange table tennis ball
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16, ring_count=12, radius=0.02 * scale, location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Ball"
        _set_smooth_shading(equip_obj)
        ball_mat = _create_material(f"{character_name}_Ball", ball_color + [1.0], roughness=0.3)
        _assign_material(equip_obj, ball_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "TABLE":
        # Table tennis table
        table_color = color or [0.0, 0.3, 0.5]  # Dark blue-green
        # Table surface
        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[0, 0, 0.76 * scale])
        table_top = bpy.context.active_object
        table_top.name = f"{character_name}_Table"
        table_top.scale = [1.525 * scale * 50, 0.7625 * scale * 50, 0.02 * scale * 50]
        table_mat = _create_material(f"{character_name}_Table", table_color + [1.0], roughness=0.4)
        _assign_material(table_top, table_mat)

        # White center line
        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[0, 0, 0.761 * scale])
        center_line = bpy.context.active_object
        center_line.name = f"{character_name}_TableLine"
        center_line.scale = [0.01 * 50, 0.76 * scale * 50, 0.005 * 50]
        line_mat = _create_material(
            f"{character_name}_TableLine", [1.0, 1.0, 1.0, 1.0], roughness=0.5
        )
        _assign_material(center_line, line_mat)
        _parent_to(center_line, table_top)

        equip_obj = table_top

    elif equipment_type == "NET":
        # Net
        net_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[0, 0, 0.91 * scale])
        net = bpy.context.active_object
        net.name = f"{character_name}_Net"
        net.scale = [0.01 * 50, 0.9125 * scale * 50, 0.1525 * scale * 50]
        net_mat = _create_material(f"{character_name}_Net", net_color + [1.0], roughness=0.8)
        net_mat.blend_method = "CLIP" if hasattr(net_mat, "blend_method") else None
        _assign_material(net, net_mat)
        equip_obj = net

    elif equipment_type.startswith("MEDAL_"):
        # Medal
        medal_colors = {
            "MEDAL_GOLD": [1.0, 0.85, 0.0],
            "MEDAL_SILVER": [0.8, 0.8, 0.85],
            "MEDAL_BRONZE": [0.8, 0.5, 0.2],
        }
        medal_color = color or medal_colors.get(equipment_type, [1.0, 0.85, 0.0])

        # Medal body
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.04 * scale, depth=0.005 * scale, location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_{equipment_type}"
        medal_mat = _create_material(
            f"{character_name}_{equipment_type}", medal_color + [1.0], metallic=0.9, roughness=0.2
        )
        _assign_material(equip_obj, medal_mat)

        # Ribbon
        ribbon_color = [0.0, 0.2, 0.8]  # Blue ribbon (Paris Olympics style)
        ribbon_loc = list(attach_location)
        ribbon_loc[2] += 0.06 * scale
        bpy.ops.mesh.primitive_cube_add(size=0.01, location=ribbon_loc)
        ribbon = bpy.context.active_object
        ribbon.name = f"{character_name}_{equipment_type}_Ribbon"
        ribbon.scale = [0.015 * scale * 50, 0.002 * 50, 0.05 * scale * 50]
        ribbon_mat = _create_material(
            f"{character_name}_Ribbon", ribbon_color + [1.0], roughness=0.7
        )
        _assign_material(ribbon, ribbon_mat)
        _parent_to(ribbon, equip_obj)

        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "WRISTBAND":
        # Wristband
        wb_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.025 * scale, minor_radius=0.008 * scale, location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Wristband"
        wb_mat = _create_material(f"{character_name}_Wristband", wb_color + [1.0], roughness=0.8)
        _assign_material(equip_obj, wb_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "HEADBAND":
        # Headband
        hb_color = color or [1.0, 0.1, 0.1]
        head_obj = bpy.data.objects.get(f"{character_name}_Head")
        head_radius = 0.25  # Default head radius
        if head_obj:
            head_radius = max(head_obj.dimensions) / 2
            attach_location = list(head_obj.location)
            attach_location[2] += head_radius * 0.3

        bpy.ops.mesh.primitive_torus_add(
            major_radius=head_radius * 1.05, minor_radius=0.01 * scale, location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Headband"
        hb_mat = _create_material(f"{character_name}_Headband", hb_color + [1.0], roughness=0.8)
        _assign_material(equip_obj, hb_mat)
        if head_obj:
            _parent_to(equip_obj, head_obj)

    elif equipment_type == "TROPHY":
        # Trophy
        trophy_color = color or [1.0, 0.85, 0.0]
        # Cup body
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24, radius=0.04 * scale, depth=0.12 * scale, location=attach_location
        )
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Trophy"
        trophy_mat = _create_material(
            f"{character_name}_Trophy", trophy_color + [1.0], metallic=0.95, roughness=0.15
        )
        _assign_material(equip_obj, trophy_mat)

        # Base
        base_loc = list(attach_location)
        base_loc[2] -= 0.07 * scale
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24, radius=0.03 * scale, depth=0.02 * scale, location=base_loc
        )
        base = bpy.context.active_object
        base.name = f"{character_name}_Trophy_Base"
        base_mat = _create_material(
            f"{character_name}_TrophyBase", [0.15, 0.1, 0.05, 1.0], roughness=0.4
        )
        _assign_material(base, base_mat)
        _parent_to(base, equip_obj)

        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    elif equipment_type == "TOWEL":
        # Towel
        towel_color = color or [1.0, 1.0, 1.0]
        bpy.ops.mesh.primitive_cube_add(size=0.01, location=attach_location)
        equip_obj = bpy.context.active_object
        equip_obj.name = f"{character_name}_Towel"
        equip_obj.scale = [0.3 * scale * 50, 0.002 * 50, 0.15 * scale * 50]
        towel_mat = _create_material(f"{character_name}_Towel", towel_color + [1.0], roughness=0.9)
        _assign_material(equip_obj, towel_mat)
        if parent_obj:
            _parent_to(equip_obj, parent_obj)

    if equip_obj is None:
        return {
            "success": False,
            "error": {
                "code": "UNKNOWN_EQUIPMENT",
                "message": f"Unknown equipment type: {equipment_type}",
            },
        }

    return {
        "success": True,
        "data": {
            "equipment_name": equip_obj.name,
            "equipment_type": equipment_type,
            "attached_to": attach_to,
        },
    }


# ==================== Sportswear ====================


def handle_create_uniform(params: dict[str, Any]) -> dict[str, Any]:
    """Create sportswear"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    team = params.get("team", "CHINA_NATIONAL")
    uniform_style = params.get("uniform_style", "MATCH_JERSEY")
    jersey_number = params.get("jersey_number", 20)
    player_name = params.get("player_name", "FAN ZHENDONG")
    params.get("brand", "Li-Ning")
    custom_primary = params.get("custom_primary_color")
    custom_secondary = params.get("custom_secondary_color")

    # Get team colors
    if team == "CLUB_CUSTOM" and custom_primary:
        colors = {
            "primary": custom_primary + [1.0] if len(custom_primary) == 3 else custom_primary,
            "secondary": (
                (custom_secondary or [1.0, 1.0, 1.0]) + [1.0]
                if custom_secondary and len(custom_secondary) == 3
                else (custom_secondary or [1.0, 1.0, 1.0, 1.0])
            ),
            "accent": [0.1, 0.1, 0.1, 1.0],
        }
    else:
        colors = TEAM_COLORS.get(team, TEAM_COLORS["CHINA_NATIONAL"])

    # Find character body
    body_obj = bpy.data.objects.get(f"{character_name}_Body")
    if not body_obj:
        return {
            "success": False,
            "error": {
                "code": "CHARACTER_NOT_FOUND",
                "message": f"Character not found: {character_name}",
            },
        }

    body_loc = list(body_obj.location)
    body_scale = list(body_obj.scale)
    created_items = []

    if uniform_style in ("MATCH_JERSEY", "TRAINING_WEAR"):
        # Jersey top
        jersey_color = colors["primary"]
        jersey_mat = _create_material(f"{character_name}_Jersey", jersey_color, roughness=0.7)

        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[body_loc[0], body_loc[1], body_loc[2]])
        jersey = bpy.context.active_object
        jersey.name = f"{character_name}_Jersey"
        jersey.scale = [body_scale[0] * 1.08, body_scale[1] * 1.08, body_scale[2] * 1.02]
        # Add subdivision for more natural clothing
        subsurf = jersey.modifiers.new("Smooth", "SUBSURF")
        subsurf.levels = 1
        subsurf.render_levels = 1
        _set_smooth_shading(jersey)
        _assign_material(jersey, jersey_mat)
        _parent_to(jersey, body_obj)
        created_items.append(jersey.name)

        # Shorts
        shorts_color = colors.get("accent", [0.1, 0.1, 0.1, 1.0])
        shorts_mat = _create_material(f"{character_name}_Shorts", shorts_color, roughness=0.7)

        # Find thigh position
        thigh_r = bpy.data.objects.get(f"{character_name}_Thigh_R")
        bpy.data.objects.get(f"{character_name}_Thigh_L")
        shorts_z = thigh_r.location[2] if thigh_r else body_loc[2] - body_scale[2] * 1.5

        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[body_loc[0], body_loc[1], shorts_z])
        shorts = bpy.context.active_object
        shorts.name = f"{character_name}_Shorts"
        shorts.scale = [body_scale[0] * 1.2, body_scale[1] * 1.1, body_scale[2] * 0.6]
        subsurf = shorts.modifiers.new("Smooth", "SUBSURF")
        subsurf.levels = 1
        subsurf.render_levels = 1
        _set_smooth_shading(shorts)
        _assign_material(shorts, shorts_mat)
        _parent_to(shorts, body_obj)
        created_items.append(shorts.name)

    elif uniform_style == "AWARD_CEREMONY":
        # Award ceremony outfit (white with red stripes jacket)
        jacket_mat = _create_material(
            f"{character_name}_AwardJacket", colors["primary"], roughness=0.6
        )

        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[body_loc[0], body_loc[1], body_loc[2]])
        jacket = bpy.context.active_object
        jacket.name = f"{character_name}_AwardJacket"
        jacket.scale = [body_scale[0] * 1.15, body_scale[1] * 1.15, body_scale[2] * 1.1]
        subsurf = jacket.modifiers.new("Smooth", "SUBSURF")
        subsurf.levels = 1
        _set_smooth_shading(jacket)
        _assign_material(jacket, jacket_mat)
        _parent_to(jacket, body_obj)
        created_items.append(jacket.name)

        # Sweatpants (white)
        pants_mat = _create_material(
            f"{character_name}_AwardPants", colors["primary"], roughness=0.6
        )
        thigh_r = bpy.data.objects.get(f"{character_name}_Thigh_R")
        pants_z = thigh_r.location[2] if thigh_r else body_loc[2] - body_scale[2] * 1.5

        bpy.ops.mesh.primitive_cube_add(size=0.01, location=[body_loc[0], body_loc[1], pants_z])
        pants = bpy.context.active_object
        pants.name = f"{character_name}_AwardPants"
        pants.scale = [body_scale[0] * 1.1, body_scale[1] * 1.05, body_scale[2] * 0.8]
        subsurf = pants.modifiers.new("Smooth", "SUBSURF")
        subsurf.levels = 1
        _set_smooth_shading(pants)
        _assign_material(pants, pants_mat)
        _parent_to(pants, body_obj)
        created_items.append(pants.name)

    elif uniform_style == "WARMUP_JACKET":
        # Warmup jacket
        jacket_mat = _create_material(
            f"{character_name}_WarmupJacket", colors["primary"], roughness=0.55
        )

        bpy.ops.mesh.primitive_cube_add(
            size=0.01, location=[body_loc[0], body_loc[1], body_loc[2] + body_scale[2] * 0.1]
        )
        jacket = bpy.context.active_object
        jacket.name = f"{character_name}_WarmupJacket"
        jacket.scale = [body_scale[0] * 1.2, body_scale[1] * 1.2, body_scale[2] * 1.15]
        subsurf = jacket.modifiers.new("Smooth", "SUBSURF")
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
        },
    }


# ==================== Sport Poses ====================


def handle_set_pose(params: dict[str, Any]) -> dict[str, Any]:
    """Set sport pose"""
    _ensure_object_mode()

    character_name = params.get("character_name", "")
    pose = params.get("pose", "READY_STANCE")
    intensity = params.get("intensity", 1.0)
    mirror = params.get("mirror", False)
    add_motion_trail = params.get("add_motion_trail", False)

    # Get pose data
    pose_data = SPORT_POSES.get(pose)
    if not pose_data:
        return {
            "success": False,
            "error": {"code": "UNKNOWN_POSE", "message": f"Unknown pose: {pose}"},
        }

    # Find armature
    armature_obj = bpy.data.objects.get(f"{character_name}_Armature")
    if not armature_obj:
        return {
            "success": False,
            "error": {
                "code": "NO_ARMATURE",
                "message": f"Character armature not found: {character_name}_Armature",
            },
        }

    # Enter Pose mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="POSE")

    applied_bones = []

    for bone_name, rotation in pose_data.items():
        if bone_name == "description":
            continue
        if not isinstance(rotation, tuple):
            continue

        # Mirror processing: swap L and R
        actual_bone_name = bone_name
        if mirror:
            if ".R" in bone_name:
                actual_bone_name = bone_name.replace(".R", ".L")
            elif ".L" in bone_name:
                actual_bone_name = bone_name.replace(".L", ".R")

        pose_bone = armature_obj.pose.bones.get(actual_bone_name)
        if pose_bone:
            # Apply rotation (with intensity)
            rx = math.radians(rotation[0] * intensity)
            ry = math.radians(rotation[1] * intensity)
            rz = math.radians(rotation[2] * intensity)

            pose_bone.rotation_mode = "XYZ"
            pose_bone.rotation_euler = (rx, ry, rz)
            applied_bones.append(actual_bone_name)

    bpy.ops.object.mode_set(mode="OBJECT")

    # Motion trail effect (optional)
    has_motion_trail = False
    if add_motion_trail and pose in (
        "FOREHAND_ATTACK",
        "BACKHAND_ATTACK",
        "FOREHAND_LOOP",
        "SERVE_HIT",
    ):
        # Create arc trail
        try:
            hand_obj = bpy.data.objects.get(f"{character_name}_Hand_R")
            if hand_obj:
                trail_points = []
                hand_loc = list(hand_obj.location)
                for i in range(5):
                    t = i / 4.0
                    trail_points.append(
                        (
                            hand_loc[0] + math.sin(t * math.pi) * 0.3,
                            hand_loc[1] - t * 0.2,
                            hand_loc[2] + math.cos(t * math.pi) * 0.1,
                        )
                    )

                curve_data = bpy.data.curves.new(f"{character_name}_MotionTrail", "CURVE")
                curve_data.dimensions = "3D"
                spline = curve_data.splines.new("BEZIER")
                spline.bezier_points.add(len(trail_points) - 1)
                for i, point in enumerate(trail_points):
                    spline.bezier_points[i].co = point

                trail_obj = bpy.data.objects.new(f"{character_name}_MotionTrail", curve_data)
                bpy.context.collection.objects.link(trail_obj)
                curve_data.bevel_depth = 0.005
                trail_mat = _create_material(
                    f"{character_name}_TrailMat", [1.0, 1.0, 1.0, 0.5], roughness=0.1
                )
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
        },
    }


# ==================== Reference Image Loading ====================


def handle_load_reference(params: dict[str, Any]) -> dict[str, Any]:
    """Load reference image"""
    _ensure_object_mode()

    image_path = params.get("image_path", "")
    view = params.get("view", "FRONT")
    opacity = params.get("opacity", 0.5)
    offset_x = params.get("offset_x", 0.0)
    offset_y = params.get("offset_y", 0.0)
    scale = params.get("scale", 1.0)

    # Check if file exists
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"File not found: {image_path}"},
        }

    # Load image
    try:
        image = bpy.data.images.load(image_path)
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LOAD_ERROR", "message": f"Failed to load image: {str(e)}"},
        }

    image_name = os.path.basename(image_path)

    # Create empty object as reference image carrier
    bpy.ops.object.empty_add(type="IMAGE", location=[offset_x, offset_y, 0])
    ref_obj = bpy.context.active_object
    ref_obj.name = f"Ref_{view}_{image_name}"
    ref_obj.data = image
    ref_obj.empty_display_size = scale
    ref_obj.empty_image_depth = "BACK"
    ref_obj.color[3] = opacity

    # Rotate based on view angle
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

    # Set as non-selectable (to avoid interfering with modeling)
    ref_obj.hide_select = True

    return {
        "success": True,
        "data": {
            "image_name": image_name,
            "object_name": ref_obj.name,
            "view": view,
            "opacity": opacity,
        },
    }


# ==================== Model Optimization ====================


def handle_optimize_model(params: dict[str, Any]) -> dict[str, Any]:
    """Optimize sport character model"""
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

    # Find all mesh objects of the character
    root_obj = bpy.data.objects.get(f"{character_name}_Root")
    if not root_obj:
        # Try to find objects with matching names
        matching_objs = [
            obj
            for obj in bpy.data.objects
            if obj.name.startswith(character_name) and obj.type == "MESH"
        ]
        if not matching_objs:
            return {
                "success": False,
                "error": {
                    "code": "CHARACTER_NOT_FOUND",
                    "message": f"Character not found: {character_name}",
                },
            }
    else:
        matching_objs = [
            obj
            for obj in bpy.data.objects
            if obj.name.startswith(character_name) and obj.type == "MESH"
        ]

    # Count original faces
    original_tris = 0
    for obj in matching_objs:
        if obj.type == "MESH":
            # Each quad is approximately 2 triangles
            original_tris += len(obj.data.polygons) * 2

    # Apply decimate modifier
    if original_tris > target_tris and target != "PRINT_3D":
        ratio = target_tris / max(original_tris, 1)
        for obj in matching_objs:
            if obj.type == "MESH" and len(obj.data.polygons) > 10:
                decimate = obj.modifiers.new("Decimate", "DECIMATE")
                decimate.ratio = max(0.1, ratio)

    # Cleanup: remove loose vertices
    for obj in matching_objs:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            try:
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.delete_loose()
                bpy.ops.object.mode_set(mode="OBJECT")
            except Exception:
                _ensure_object_mode()

    # Count final faces
    final_tris = 0
    for obj in matching_objs:
        if obj.type == "MESH":
            # Evaluate face count after modifiers
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            final_tris += len(eval_obj.data.polygons) * 2

    # LOD generation (optional)
    lod_count = 0
    if generate_lod:
        for level in range(1, lod_levels + 1):
            lod_ratio = 1.0 / (2**level)
            for obj in matching_objs:
                if obj.type == "MESH" and len(obj.data.polygons) > 20:
                    # Copy object
                    lod_obj = obj.copy()
                    lod_obj.data = obj.data.copy()
                    lod_obj.name = f"{obj.name}_LOD{level}"
                    bpy.context.collection.objects.link(lod_obj)

                    # Add decimate
                    decimate = lod_obj.modifiers.new(f"LOD{level}", "DECIMATE")
                    decimate.ratio = max(0.05, lod_ratio)

                    # Hide LOD objects
                    lod_obj.hide_viewport = True
                    lod_obj.hide_render = True
                    lod_count += 1

    # GLB export (optional)
    exported_path = None
    if export_glb:
        if not export_path:
            blend_path = bpy.data.filepath
            if blend_path:
                export_path = os.path.join(os.path.dirname(blend_path), f"{character_name}.glb")
            else:
                export_path = os.path.join(os.path.expanduser("~"), f"{character_name}.glb")

        try:
            # Select character objects
            bpy.ops.object.select_all(action="DESELECT")
            for obj in matching_objs:
                obj.select_set(True)
            # Also select armature
            armature = bpy.data.objects.get(f"{character_name}_Armature")
            if armature:
                armature.select_set(True)

            # Export GLB
            export_settings = {
                "filepath": export_path,
                "use_selection": True,
                "export_format": "GLB",
                "export_apply": True,
            }

            # Draco compression
            if apply_draco:
                export_settings["export_draco_mesh_compression_enable"] = True
                export_settings["export_draco_mesh_compression_level"] = 6

            bpy.ops.export_scene.gltf(**export_settings)
            exported_path = export_path

        except Exception:
            # Export failure does not affect other results
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
        },
    }


# ==================== Scene Setup ====================


def handle_setup_scene(params: dict[str, Any]) -> dict[str, Any]:
    """Set up sport scene"""
    _ensure_object_mode()

    scene_type = params.get("scene_type", "PORTRAIT")
    character_name = params.get("character_name")
    background_color = params.get("background_color")
    params.get("use_hdri", False)
    camera_distance = params.get("camera_distance", 3.0)
    render_engine = params.get("render_engine", "EEVEE")

    scene = bpy.context.scene
    lights_count = 0

    # Set render engine
    if render_engine == "CYCLES":
        scene.render.engine = "CYCLES"
    else:
        scene.render.engine = get_eevee_engine()

    # Set color management
    try:
        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "Medium Contrast"
    except Exception:
        pass

    # Delete default lights
    for obj in list(bpy.data.objects):
        if obj.type == "LIGHT" and obj.name in ("Light", "Lamp"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Background color
    if background_color:
        world = scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            scene.world = world
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs["Color"].default_value = (
                background_color + [1.0] if len(background_color) == 3 else background_color
            )

    # Set up lights based on scene type
    if scene_type == "PORTRAIT":
        # Three-point lighting: portrait display
        # Key light (warm, 45 degrees front-side)
        bpy.ops.object.light_add(type="AREA", location=(2, -2, 3))
        key_light = bpy.context.active_object
        key_light.name = "KeyLight"
        key_light.data.energy = 200
        key_light.data.color = (1.0, 0.95, 0.9)  # Warm tone
        key_light.data.size = 2
        key_light.rotation_euler = (math.radians(45), 0, math.radians(45))
        lights_count += 1

        # Fill light (cool, opposite side)
        bpy.ops.object.light_add(type="AREA", location=(-2, -1.5, 2))
        fill_light = bpy.context.active_object
        fill_light.name = "FillLight"
        fill_light.data.energy = 80
        fill_light.data.color = (0.9, 0.95, 1.0)  # Cool tone
        fill_light.data.size = 3
        fill_light.rotation_euler = (math.radians(30), 0, math.radians(-30))
        lights_count += 1

        # Rim light (back)
        bpy.ops.object.light_add(type="AREA", location=(0, 2, 2.5))
        rim_light = bpy.context.active_object
        rim_light.name = "RimLight"
        rim_light.data.energy = 150
        rim_light.data.color = (1.0, 1.0, 1.0)
        rim_light.data.size = 1
        rim_light.rotation_euler = (math.radians(60), 0, math.radians(180))
        lights_count += 1

    elif scene_type == "PRODUCT":
        # Product/figurine display lighting
        # Top ambient light
        bpy.ops.object.light_add(type="AREA", location=(0, 0, 4))
        top_light = bpy.context.active_object
        top_light.name = "TopLight"
        top_light.data.energy = 150
        top_light.data.size = 4
        top_light.rotation_euler = (0, 0, 0)
        lights_count += 1

        # Front-side light
        bpy.ops.object.light_add(type="AREA", location=(1.5, -2, 1.5))
        front_light = bpy.context.active_object
        front_light.name = "FrontLight"
        front_light.data.energy = 100
        front_light.data.color = (1.0, 0.98, 0.95)
        front_light.data.size = 2
        front_light.rotation_euler = (math.radians(30), 0, math.radians(30))
        lights_count += 1

        # Bottom fill light (product display specific)
        bpy.ops.object.light_add(type="AREA", location=(0, -1, -0.5))
        bottom_light = bpy.context.active_object
        bottom_light.name = "BottomFill"
        bottom_light.data.energy = 30
        bottom_light.data.size = 3
        bottom_light.rotation_euler = (math.radians(-60), 0, 0)
        lights_count += 1

        # Display base
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.05, location=(0, 0, -0.025))
        base = bpy.context.active_object
        base.name = "DisplayBase"
        base_mat = _create_material(
            "DisplayBase", [0.1, 0.1, 0.1, 1.0], metallic=0.3, roughness=0.2
        )
        _assign_material(base, base_mat)

    elif scene_type == "MATCH":
        # Match scene lighting (stadium overhead lights)
        for i, x_offset in enumerate([-2, 0, 2]):
            bpy.ops.object.light_add(type="AREA", location=(x_offset, 0, 5))
            light = bpy.context.active_object
            light.name = f"StadiumLight_{i}"
            light.data.energy = 300
            light.data.color = (1.0, 1.0, 0.98)
            light.data.size = 3
            lights_count += 1

        # Side fill light
        bpy.ops.object.light_add(type="AREA", location=(4, -3, 2))
        side_light = bpy.context.active_object
        side_light.name = "SideLight"
        side_light.data.energy = 80
        side_light.data.size = 4
        lights_count += 1

    elif scene_type == "AWARD_CEREMONY":
        # Award ceremony scene
        # Spotlight (award ceremony effect)
        bpy.ops.object.light_add(type="SPOT", location=(0, -3, 5))
        spot = bpy.context.active_object
        spot.name = "AwardSpotlight"
        spot.data.energy = 500
        spot.data.spot_size = math.radians(30)
        spot.data.color = (1.0, 0.95, 0.85)
        spot.rotation_euler = (math.radians(30), 0, 0)
        lights_count += 1

        # Ambient fill light
        bpy.ops.object.light_add(type="AREA", location=(2, -1, 3))
        fill = bpy.context.active_object
        fill.name = "AwardFill"
        fill.data.energy = 100
        fill.data.size = 3
        lights_count += 1

        # Podium
        for pos, h, color in [
            ((0, 0, 0), 0.3, [1.0, 0.85, 0.0, 1.0]),  # Gold medal position (center, highest)
            ((-0.6, 0, 0), 0.2, [0.75, 0.75, 0.8, 1.0]),  # Silver medal position
            ((0.6, 0, 0), 0.15, [0.7, 0.45, 0.2, 1.0]),  # Bronze medal position
        ]:
            bpy.ops.mesh.primitive_cube_add(size=0.01, location=(pos[0], pos[1], h / 2))
            podium = bpy.context.active_object
            podium.name = f"Podium_{pos[0]}"
            podium.scale = [0.25 * 50, 0.2 * 50, h / 2 * 50]
            podium_mat = _create_material(f"Podium_{pos[0]}", color, roughness=0.3)
            _assign_material(podium, podium_mat)

    elif scene_type == "TRAINING":
        # Training scene
        bpy.ops.object.light_add(type="AREA", location=(0, 0, 4))
        overhead = bpy.context.active_object
        overhead.name = "TrainingLight"
        overhead.data.energy = 200
        overhead.data.size = 5
        lights_count += 1

        bpy.ops.object.light_add(type="AREA", location=(3, -2, 2))
        side = bpy.context.active_object
        side.name = "TrainingSide"
        side.data.energy = 60
        side.data.size = 3
        lights_count += 1

    # Set up camera
    # Delete default camera
    for obj in list(bpy.data.objects):
        if obj.type == "CAMERA" and obj.name == "Camera":
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_height = 1.0 if scene_type in ("PORTRAIT", "PRODUCT") else 1.5
    bpy.ops.object.camera_add(
        location=(0, -camera_distance, cam_height), rotation=(math.radians(80), 0, 0)
    )
    camera = bpy.context.active_object
    camera.name = "SportCamera"
    scene.camera = camera

    # If character exists, camera tracks character
    if character_name:
        target_obj = bpy.data.objects.get(f"{character_name}_Root") or bpy.data.objects.get(
            f"{character_name}_Body"
        )
        if target_obj:
            constraint = camera.constraints.new("TRACK_TO")
            constraint.target = target_obj
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            constraint.up_axis = "UP_Y"

    return {
        "success": True,
        "data": {
            "scene_type": scene_type,
            "render_engine": render_engine,
            "lights_count": lights_count,
            "camera_distance": camera_distance,
        },
    }
