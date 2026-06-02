"""
Export Handler

Handles export commands for various formats.
"""

import os
from typing import Any

import bpy


def handle_fbx(params: dict[str, Any]) -> dict[str, Any]:
    """Export FBX.

    Supports full axis/transform control for engine-correct output. When
    ``unity_static_preset`` is true, applies the settings recommended for
    static Unity props (see blender_model_spec_zh.md §1.4): bakes the space
    transform so meshes import with a zeroed Transform (no residual -90deg X
    rotation), face smoothing, and Mesh/Empty object types only. Granular
    params still override the preset when explicitly provided.
    """
    filepath = params.get("filepath")

    if not filepath:
        return {
            "success": False,
            "error": {"code": "MISSING_FILEPATH", "message": "Export filepath is required"},
        }

    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Ensure correct file extension
    if not filepath.lower().endswith(".fbx"):
        filepath += ".fbx"

    unity_preset = params.get("unity_static_preset", False)

    # Axis / transform defaults. -Z forward + Y up matches Unity's importer;
    # these are also Blender's FBX defaults so behaviour is unchanged unless
    # overridden.
    axis_forward = params.get("axis_forward", "-Z")
    axis_up = params.get("axis_up", "Y")
    use_space_transform = params.get("use_space_transform", True)
    apply_unit_scale = params.get("apply_unit_scale", True)

    # Preset-driven defaults (only used when caller did not set them).
    bake_space_transform = params.get("bake_space_transform", True if unity_preset else False)
    mesh_smooth_type = params.get("mesh_smooth_type", "FACE" if unity_preset else "OFF")

    object_types = params.get("object_types")
    if object_types is None and unity_preset:
        object_types = ["MESH", "EMPTY"]
    object_types_set = set(object_types) if object_types else None

    fbx_kwargs = dict(
        filepath=filepath,
        use_selection=params.get("selected_only", False),
        global_scale=params.get("global_scale", 1.0),
        apply_unit_scale=apply_unit_scale,
        apply_scale_options=params.get("apply_scale", "FBX_SCALE_ALL"),
        use_space_transform=use_space_transform,
        bake_space_transform=bake_space_transform,
        axis_forward=axis_forward,
        axis_up=axis_up,
        mesh_smooth_type=mesh_smooth_type,
        use_mesh_modifiers=params.get("use_mesh_modifiers", True),
        use_armature_deform_only=params.get("use_armature_deform_only", False),
        add_leaf_bones=params.get("add_leaf_bones", False),
        primary_bone_axis=params.get("primary_bone_axis", "Y"),
        secondary_bone_axis=params.get("secondary_bone_axis", "X"),
        bake_anim=params.get("include_animation", True),
        bake_anim_use_all_actions=params.get("bake_animation", False),
        path_mode=params.get("path_mode", "AUTO"),
    )
    if object_types_set:
        fbx_kwargs["object_types"] = object_types_set

    try:
        bpy.ops.export_scene.fbx(**fbx_kwargs)

        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "unity_static_preset": unity_preset,
                "axis_forward": axis_forward,
                "axis_up": axis_up,
                "bake_space_transform": bake_space_transform,
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "EXPORT_ERROR", "message": str(e)}}


def handle_gltf(params: dict[str, Any]) -> dict[str, Any]:
    """Export glTF"""
    filepath = params.get("filepath")

    if not filepath:
        return {
            "success": False,
            "error": {"code": "MISSING_FILEPATH", "message": "Export filepath is required"},
        }

    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    export_format = params.get("export_format", "GLB")

    # Ensure correct file extension
    if export_format == "GLB" and not filepath.lower().endswith(".glb"):
        filepath += ".glb"
    elif export_format == "GLTF_SEPARATE" and not filepath.lower().endswith(".gltf"):
        filepath += ".gltf"

    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=params.get("selected_only", False),
            export_format=export_format,
            export_animations=params.get("include_animation", True),
            export_image_format="AUTO" if params.get("export_textures", True) else "NONE",
            export_draco_mesh_compression_enable=params.get("export_draco", False),
        )

        return {"success": True, "data": {"filepath": filepath}}

    except Exception as e:
        return {"success": False, "error": {"code": "EXPORT_ERROR", "message": str(e)}}


def handle_obj(params: dict[str, Any]) -> dict[str, Any]:
    """Export OBJ"""
    filepath = params.get("filepath")

    if not filepath:
        return {
            "success": False,
            "error": {"code": "MISSING_FILEPATH", "message": "Export filepath is required"},
        }

    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Ensure correct file extension
    if not filepath.lower().endswith(".obj"):
        filepath += ".obj"

    try:
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=params.get("selected_only", False),
            apply_modifiers=params.get("apply_modifiers", True),
            export_materials=params.get("export_materials", True),
        )

        return {"success": True, "data": {"filepath": filepath}}

    except Exception as e:
        return {"success": False, "error": {"code": "EXPORT_ERROR", "message": str(e)}}
