"""
Quick compound handler - High-level one-call workflows.

Runs inside Blender with full bpy access.
"""

from __future__ import annotations

import math
from typing import Any

import bpy


def _clear_default_objects() -> list[str]:
    """Remove default Cube, Camera, Light if present."""
    removed = []
    for name in ("Cube", "Camera", "Light"):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed.append(name)
    return removed


def _get_target_object(name: str | None) -> Any:
    """Get target object by name or use active object."""
    if name:
        obj = bpy.data.objects.get(name)
        return obj
    return bpy.context.view_layer.objects.active


def _create_material(name: str, color: tuple, metallic: float = 0.0, roughness: float = 0.5) -> Any:
    """Create a simple Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def handle_product_shot(params: dict[str, Any]) -> dict[str, Any]:
    """Set up complete product visualization: lighting, camera, backdrop."""
    target_name = params.get("target_object")
    style = params.get("style", "studio")
    bg_color = params.get("background_color", [0.8, 0.8, 0.8])
    render_w = params.get("render_width", 1920)
    render_h = params.get("render_height", 1080)

    try:
        target = _get_target_object(target_name)
        if not target:
            all_names = [o.name for o in bpy.context.scene.objects if o.type == "MESH"]
            return {
                "success": False,
                "error": {
                    "code": "OBJECT_NOT_FOUND",
                    "message": f"Target object '{target_name}' not found."
                    if target_name
                    else "No active object. Specify target_object.",
                    "suggestion": f"Available mesh objects: {', '.join(all_names[:10])}"
                    if all_names
                    else "Create an object first with blender_object_create.",
                },
            }

        created: list[str] = []

        # Calculate target bounds for placement
        dims = target.dimensions
        max_dim = max(dims) if max(dims) > 0 else 2.0
        center = target.location.copy()

        # --- Backdrop plane ---
        bpy.ops.mesh.primitive_plane_add(
            size=max_dim * 10,
            location=(center.x, center.y, center.z - dims.z / 2),
        )
        backdrop = bpy.context.active_object
        backdrop.name = "MCP_Backdrop"
        backdrop_mat = _create_material("MCP_Backdrop_Mat", tuple(bg_color), metallic=0.0, roughness=0.9)
        backdrop.data.materials.append(backdrop_mat)
        created.append(backdrop.name)

        # --- 3-Point Lighting ---
        cam_dist = max_dim * 3.0

        # Lighting configs per style
        light_configs = {
            "studio": [
                {"name": "MCP_Key", "type": "AREA", "energy": 200, "pos": (cam_dist, -cam_dist * 0.5, cam_dist * 0.8), "size": max_dim * 2},
                {"name": "MCP_Fill", "type": "AREA", "energy": 80, "pos": (-cam_dist * 0.8, -cam_dist * 0.3, cam_dist * 0.5), "size": max_dim * 3},
                {"name": "MCP_Rim", "type": "AREA", "energy": 150, "pos": (-cam_dist * 0.5, cam_dist, cam_dist * 0.6), "size": max_dim * 1.5},
            ],
            "dramatic": [
                {"name": "MCP_Key", "type": "SPOT", "energy": 500, "pos": (cam_dist, -cam_dist * 0.3, cam_dist), "size": max_dim},
                {"name": "MCP_Rim", "type": "AREA", "energy": 200, "pos": (-cam_dist, cam_dist * 0.5, cam_dist * 0.3), "size": max_dim * 2},
            ],
            "soft": [
                {"name": "MCP_Key", "type": "AREA", "energy": 100, "pos": (cam_dist * 0.5, -cam_dist, cam_dist), "size": max_dim * 4},
                {"name": "MCP_Fill", "type": "AREA", "energy": 60, "pos": (-cam_dist, 0, cam_dist * 0.5), "size": max_dim * 4},
                {"name": "MCP_Rim", "type": "AREA", "energy": 40, "pos": (0, cam_dist, cam_dist * 0.3), "size": max_dim * 3},
            ],
            "outdoor": [
                {"name": "MCP_Sun", "type": "SUN", "energy": 5, "pos": (cam_dist, -cam_dist, cam_dist * 2), "size": 0},
                {"name": "MCP_Fill", "type": "AREA", "energy": 30, "pos": (-cam_dist, cam_dist * 0.5, cam_dist * 0.3), "size": max_dim * 5},
            ],
        }

        lights = light_configs.get(style, light_configs["studio"])
        for lc in lights:
            light_data = bpy.data.lights.new(name=lc["name"], type=lc["type"])
            light_data.energy = lc["energy"]
            if lc["type"] == "AREA" and lc["size"] > 0:
                light_data.size = lc["size"]
            light_obj = bpy.data.objects.new(name=lc["name"], object_data=light_data)
            bpy.context.scene.collection.objects.link(light_obj)
            light_obj.location = lc["pos"]

            # Point light at target
            direction = center - light_obj.location
            rot_quat = direction.to_track_quat("-Z", "Y")
            light_obj.rotation_euler = rot_quat.to_euler()
            created.append(light_obj.name)

        # --- Camera ---
        cam_data = bpy.data.cameras.new(name="MCP_Camera")
        cam_data.lens = 85  # Portrait lens for product shots
        cam_obj = bpy.data.objects.new(name="MCP_Camera", object_data=cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)

        # Position camera at 30 degree angle
        angle = math.radians(30)
        cam_obj.location = (
            center.x + cam_dist * math.cos(angle),
            center.y - cam_dist * math.sin(angle) * 1.5,
            center.z + cam_dist * 0.6,
        )

        # Point camera at target
        direction = center - cam_obj.location
        rot_quat = direction.to_track_quat("-Z", "Y")
        cam_obj.rotation_euler = rot_quat.to_euler()

        bpy.context.scene.camera = cam_obj
        created.append(cam_obj.name)

        # --- Render settings ---
        scene = bpy.context.scene
        scene.render.resolution_x = render_w
        scene.render.resolution_y = render_h
        scene.render.resolution_percentage = 100

        return {
            "success": True,
            "data": {
                "target": target.name,
                "style": style,
                "created_objects": created,
                "render_resolution": [render_w, render_h],
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PRODUCT_SHOT_ERROR", "message": str(e)},
        }


def handle_turntable(params: dict[str, Any]) -> dict[str, Any]:
    """Create a turntable animation for an object."""
    target_name = params.get("target_object")
    frames = params.get("frames", 120)
    axis = params.get("axis", "Z")

    try:
        target = _get_target_object(target_name)
        if not target:
            all_names = [o.name for o in bpy.context.scene.objects if o.type == "MESH"]
            return {
                "success": False,
                "error": {
                    "code": "OBJECT_NOT_FOUND",
                    "message": f"Target object '{target_name}' not found."
                    if target_name
                    else "No active object. Specify target_object.",
                    "suggestion": f"Available mesh objects: {', '.join(all_names[:10])}"
                    if all_names
                    else "Create an object first with blender_object_create.",
                },
            }

        scene = bpy.context.scene

        # Create pivot empty at target's location
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=target.location)
        pivot = bpy.context.active_object
        pivot.name = f"MCP_Turntable_{target.name}"

        # Parent target to pivot (keep transform)
        target.select_set(True)
        pivot.select_set(True)
        bpy.context.view_layer.objects.active = pivot
        bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

        # Clear selection
        bpy.ops.object.select_all(action="DESELECT")
        pivot.select_set(True)
        bpy.context.view_layer.objects.active = pivot

        # Determine rotation channel index
        axis_map = {"X": 0, "Y": 1, "Z": 2}
        axis_idx = axis_map.get(axis.upper(), 2)

        # Set frame range
        scene.frame_start = 1
        scene.frame_end = frames
        scene.frame_current = 1

        # Keyframe at frame 1: rotation = 0
        pivot.rotation_euler[axis_idx] = 0.0
        pivot.keyframe_insert(data_path="rotation_euler", index=axis_idx, frame=1)

        # Keyframe at last frame + 1: rotation = 2*pi (for seamless loop, we go to frames+1)
        pivot.rotation_euler[axis_idx] = math.radians(360)
        pivot.keyframe_insert(data_path="rotation_euler", index=axis_idx, frame=frames + 1)

        # Set interpolation to linear for smooth rotation
        # In Blender 5.0+, Action.fcurves was removed in favor of layered action system
        if pivot.animation_data and pivot.animation_data.action:
            action = pivot.animation_data.action
            if hasattr(action, "fcurves"):
                try:
                    for fcurve in action.fcurves:
                        if fcurve.data_path == "rotation_euler" and fcurve.array_index == axis_idx:
                            for kp in fcurve.keyframe_points:
                                kp.interpolation = "LINEAR"
                except Exception:
                    pass  # Gracefully skip if fcurves access fails

        return {
            "success": True,
            "data": {
                "target": target.name,
                "pivot_empty": pivot.name,
                "frames": frames,
                "axis": axis.upper(),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "TURNTABLE_ERROR", "message": str(e)},
        }


def handle_scene_setup(params: dict[str, Any]) -> dict[str, Any]:
    """One-click scene setup with lighting and camera."""
    style = params.get("style", "studio")
    clear_scene = params.get("clear_scene", False)

    try:
        scene = bpy.context.scene
        created: list[str] = []

        # Clear if requested
        if clear_scene:
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False)

        # Style configurations
        configs = {
            "studio": {
                "world_color": (0.05, 0.05, 0.05),
                "lights": [
                    {"name": "MCP_Key", "type": "AREA", "energy": 200, "pos": (4, -3, 5), "size": 3},
                    {"name": "MCP_Fill", "type": "AREA", "energy": 80, "pos": (-3, -2, 3), "size": 4},
                    {"name": "MCP_Rim", "type": "AREA", "energy": 150, "pos": (-2, 4, 3), "size": 2},
                ],
                "camera": {"pos": (5, -5, 4), "lens": 50},
            },
            "outdoor": {
                "world_color": (0.3, 0.5, 0.8),
                "lights": [
                    {"name": "MCP_Sun", "type": "SUN", "energy": 5, "pos": (5, -5, 10), "size": 0},
                    {"name": "MCP_Bounce", "type": "AREA", "energy": 20, "pos": (-3, 2, 1), "size": 5},
                ],
                "camera": {"pos": (6, -6, 3), "lens": 35},
            },
            "dramatic": {
                "world_color": (0.01, 0.01, 0.01),
                "lights": [
                    {"name": "MCP_Key", "type": "SPOT", "energy": 500, "pos": (4, -1, 5), "size": 1},
                    {"name": "MCP_Rim", "type": "AREA", "energy": 200, "pos": (-3, 3, 2), "size": 2},
                ],
                "camera": {"pos": (4, -4, 3), "lens": 85},
            },
            "minimal": {
                "world_color": (0.9, 0.9, 0.9),
                "lights": [
                    {"name": "MCP_Key", "type": "AREA", "energy": 150, "pos": (3, -3, 5), "size": 5},
                ],
                "camera": {"pos": (5, -5, 3), "lens": 50},
            },
        }

        cfg = configs.get(style, configs["studio"])

        # --- World background ---
        world = bpy.data.worlds.get("World")
        if not world:
            world = bpy.data.worlds.new("World")
        scene.world = world
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            wc = cfg["world_color"]
            bg_node.inputs["Color"].default_value = (wc[0], wc[1], wc[2], 1.0)

        # --- Lights ---
        for lc in cfg["lights"]:
            light_data = bpy.data.lights.new(name=lc["name"], type=lc["type"])
            light_data.energy = lc["energy"]
            if lc["type"] == "AREA" and lc["size"] > 0:
                light_data.size = lc["size"]
            light_obj = bpy.data.objects.new(name=lc["name"], object_data=light_data)
            scene.collection.objects.link(light_obj)
            light_obj.location = lc["pos"]

            # Point toward origin
            from mathutils import Vector

            direction = Vector((0, 0, 0)) - light_obj.location
            rot_quat = direction.to_track_quat("-Z", "Y")
            light_obj.rotation_euler = rot_quat.to_euler()
            created.append(light_obj.name)

        # --- Camera ---
        cam_cfg = cfg["camera"]
        cam_data = bpy.data.cameras.new(name="MCP_Camera")
        cam_data.lens = cam_cfg["lens"]
        cam_obj = bpy.data.objects.new(name="MCP_Camera", object_data=cam_data)
        scene.collection.objects.link(cam_obj)
        cam_obj.location = cam_cfg["pos"]

        from mathutils import Vector

        direction = Vector((0, 0, 0)) - cam_obj.location
        rot_quat = direction.to_track_quat("-Z", "Y")
        cam_obj.rotation_euler = rot_quat.to_euler()

        scene.camera = cam_obj
        created.append(cam_obj.name)

        # --- Render settings ---
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100

        return {
            "success": True,
            "data": {
                "style": style,
                "created_objects": created,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SCENE_SETUP_ERROR", "message": str(e)},
        }
