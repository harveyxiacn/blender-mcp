"""
World/Environment Handler

Handles Blender world and environment settings commands.
"""

import os
from typing import Any

import bpy

from .compat import is_eevee_engine


def _ensure_world():
    """Ensure an active world exists"""
    if not bpy.context.scene.world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    return bpy.context.scene.world


def handle_create(params: dict[str, Any]) -> dict[str, Any]:
    """Create a new world"""
    name = params.get("name", "World")
    use_nodes = params.get("use_nodes", True)

    try:
        world = bpy.data.worlds.new(name)
        world.use_nodes = use_nodes

        # Set as the current scene's world
        bpy.context.scene.world = world

        return {"success": True, "data": {"world_name": world.name, "use_nodes": use_nodes}}

    except Exception as e:
        return {"success": False, "error": {"code": "WORLD_CREATE_ERROR", "message": str(e)}}


def handle_background(params: dict[str, Any]) -> dict[str, Any]:
    """Set world background"""
    color = params.get("color")
    strength = params.get("strength", 1.0)
    use_sky_texture = params.get("use_sky_texture", False)

    try:
        world = _ensure_world()
        world.use_nodes = True

        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create output node
        output = nodes.new("ShaderNodeOutputWorld")
        output.location = (300, 0)

        # Create background node
        background = nodes.new("ShaderNodeBackground")
        background.location = (0, 0)
        background.inputs["Strength"].default_value = strength

        if color:
            background.inputs["Color"].default_value = (
                color[:3] + [1.0] if len(color) == 3 else color[:4]
            )

        if use_sky_texture:
            # Add sky texture
            sky = nodes.new("ShaderNodeTexSky")
            sky.location = (-300, 0)
            links.new(sky.outputs["Color"], background.inputs["Color"])

        links.new(background.outputs["Background"], output.inputs["Surface"])

        return {
            "success": True,
            "data": {"world_name": world.name, "color": color, "strength": strength},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "BACKGROUND_ERROR", "message": str(e)}}


def handle_hdri(params: dict[str, Any]) -> dict[str, Any]:
    """Set up HDRI environment"""
    hdri_path = params.get("hdri_path")
    strength = params.get("strength", 1.0)
    rotation = params.get("rotation", 0.0)

    if not os.path.exists(hdri_path):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"HDRI file not found: {hdri_path}"},
        }

    try:
        world = _ensure_world()
        world.use_nodes = True

        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create nodes
        output = nodes.new("ShaderNodeOutputWorld")
        output.location = (300, 0)

        background = nodes.new("ShaderNodeBackground")
        background.location = (0, 0)
        background.inputs["Strength"].default_value = strength

        env_tex = nodes.new("ShaderNodeTexEnvironment")
        env_tex.location = (-300, 0)

        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (-500, 0)
        mapping.inputs["Rotation"].default_value[2] = rotation

        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = (-700, 0)

        # Load HDRI
        image = bpy.data.images.load(hdri_path)
        env_tex.image = image

        # Connect nodes
        links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], env_tex.inputs["Vector"])
        links.new(env_tex.outputs["Color"], background.inputs["Color"])
        links.new(background.outputs["Background"], output.inputs["Surface"])

        return {
            "success": True,
            "data": {"world_name": world.name, "hdri": hdri_path, "strength": strength},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "HDRI_ERROR", "message": str(e)}}


def handle_sky(params: dict[str, Any]) -> dict[str, Any]:
    """Set up procedural sky"""
    sky_type = params.get("sky_type", "HOSEK_WILKIE")
    sun_elevation = params.get("sun_elevation", 0.785)
    sun_rotation = params.get("sun_rotation", 0.0)
    params.get("air_density", 1.0)
    params.get("dust_density", 0.0)
    params.get("ozone_density", 1.0)

    try:
        world = _ensure_world()
        world.use_nodes = True

        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create nodes
        output = nodes.new("ShaderNodeOutputWorld")
        output.location = (300, 0)

        background = nodes.new("ShaderNodeBackground")
        background.location = (0, 0)

        sky = nodes.new("ShaderNodeTexSky")
        sky.location = (-300, 0)

        # Blender 5.0 sky_type: SINGLE_SCATTERING, MULTIPLE_SCATTERING, PREETHAM, HOSEK_WILKIE
        # Map the old NISHITA to the new types
        type_map = {
            "NISHITA": "HOSEK_WILKIE",
            "PREETHAM": "PREETHAM",
            "HOSEK_WILKIE": "HOSEK_WILKIE",
            "SINGLE_SCATTERING": "SINGLE_SCATTERING",
            "MULTIPLE_SCATTERING": "MULTIPLE_SCATTERING",
        }
        actual_type = type_map.get(sky_type, "HOSEK_WILKIE")
        sky.sky_type = actual_type

        # Set sun direction
        if hasattr(sky, "sun_elevation"):
            sky.sun_elevation = sun_elevation
        if hasattr(sky, "sun_rotation"):
            sky.sun_rotation = sun_rotation
        if hasattr(sky, "sun_direction"):
            import math

            sky.sun_direction[0] = math.cos(sun_elevation) * math.sin(sun_rotation)
            sky.sun_direction[1] = math.cos(sun_elevation) * math.cos(sun_rotation)
            sky.sun_direction[2] = math.sin(sun_elevation)

        # Connect nodes
        links.new(sky.outputs["Color"], background.inputs["Color"])
        links.new(background.outputs["Background"], output.inputs["Surface"])

        return {"success": True, "data": {"world_name": world.name, "sky_type": actual_type}}

    except Exception as e:
        return {"success": False, "error": {"code": "SKY_ERROR", "message": str(e)}}


def handle_fog(params: dict[str, Any]) -> dict[str, Any]:
    """Set up volumetric fog"""
    use_fog = params.get("use_fog", True)
    density = params.get("density", 0.01)
    color = params.get("color", [0.5, 0.6, 0.7])
    anisotropy = params.get("anisotropy", 0.0)

    try:
        world = _ensure_world()
        world.use_nodes = True

        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Find the output node
        output = None
        for node in nodes:
            if node.type == "OUTPUT_WORLD":
                output = node
                break

        if not output:
            output = nodes.new("ShaderNodeOutputWorld")
            output.location = (300, 0)

        if use_fog:
            # Create volume scatter node
            volume = nodes.new("ShaderNodeVolumeScatter")
            volume.location = (0, -200)
            volume.inputs["Color"].default_value = color[:3] + [1.0]
            volume.inputs["Density"].default_value = density
            volume.inputs["Anisotropy"].default_value = anisotropy

            links.new(volume.outputs["Volume"], output.inputs["Volume"])
        else:
            # Disconnect volume links
            for link in output.inputs["Volume"].links:
                links.remove(link)

        return {"success": True, "data": {"use_fog": use_fog, "density": density}}

    except Exception as e:
        return {"success": False, "error": {"code": "FOG_ERROR", "message": str(e)}}


def handle_ambient_occlusion(params: dict[str, Any]) -> dict[str, Any]:
    """Set up ambient occlusion"""
    use_ao = params.get("use_ao", True)
    distance = params.get("distance", 1.0)
    factor = params.get("factor", 1.0)

    try:
        world = _ensure_world()
        scene = bpy.context.scene

        # Blender 5.0+ AO settings location changed
        # EEVEE Next
        if is_eevee_engine(scene.render.engine):
            if hasattr(scene.eevee, "use_gtao"):
                scene.eevee.use_gtao = use_ao
                scene.eevee.gtao_distance = distance
                scene.eevee.gtao_factor = factor
            elif hasattr(scene.eevee, "use_raytracing"):
                # EEVEE Next may use ray-traced AO
                pass

        # Cycles - AO implemented via world nodes
        elif scene.render.engine == "CYCLES":
            # In Cycles, AO is typically implemented via shader nodes
            # or through render passes
            if hasattr(scene, "cycles"):
                scene.cycles.use_fast_gi = use_ao

        # Try old API as fallback
        try:
            if hasattr(world.light_settings, "use_ambient_occlusion"):
                world.light_settings.use_ambient_occlusion = use_ao
                world.light_settings.ao_factor = factor
                world.light_settings.distance = distance
        except:
            pass

        return {
            "success": True,
            "data": {
                "use_ao": use_ao,
                "distance": distance,
                "factor": factor,
                "note": "AO settings applied where supported",
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "AO_ERROR", "message": str(e)}}
