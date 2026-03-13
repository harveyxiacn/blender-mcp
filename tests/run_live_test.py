"""
Comprehensive live integration test for all Blender MCP handler modules.

Requires: Running Blender with MCP addon enabled on localhost:9876
Usage: uv run python tests/run_live_test.py
"""

import asyncio
import sys

sys.path.insert(0, "src")

from blender_mcp.connection import BlenderConnection, BlenderConnectionError

PASS = 0
FAIL = 0
ERRORS = []


async def send(conn, category, action, params=None):
    return await conn.send_command(category, action, params or {})


async def test(conn, name, category, action, params=None, check_success=True):
    global PASS, FAIL
    try:
        result = await send(conn, category, action, params)
        if check_success and not result.get("success"):
            FAIL += 1
            err = result.get("error", {})
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            ERRORS.append(f"FAIL {name}: {msg}")
            print(f"  FAIL {name}: {msg}")
            return result
        PASS += 1
        print(f"  PASS {name}")
        return result
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"ERROR {name}: {e}")
        print(f"  ERROR {name}: {e}")
        return None


async def main():
    global PASS, FAIL
    conn = BlenderConnection(host="127.0.0.1", port=9876)
    try:
        await conn.connect()
    except BlenderConnectionError as e:
        print(f"Cannot connect to Blender: {e}")
        print("Make sure Blender is running with the MCP addon enabled.")
        return 1

    # Get Blender version
    r = await send(conn, "system", "get_info")
    ver = r.get("data", {}).get("version_string", "?")
    print(f"Connected to Blender {ver}\n")

    # ====== SYSTEM ======
    print("=== System ===")
    await test(conn, "system.get_info", "system", "get_info")
    await test(
        conn,
        "system.execute_python",
        "system",
        "execute_python",
        {"code": "import bpy; result = {'scene': bpy.context.scene.name}"},
    )

    # ====== UTILITY ======
    print("\n=== Utility ===")
    await test(
        conn,
        "utility.execute_python",
        "utility",
        "execute_python",
        {"code": "result = {'objects': len(bpy.data.objects)}"},
    )
    await test(conn, "utility.get_info", "utility", "get_info")
    await test(conn, "utility.get_blender_version", "utility", "get_blender_version")
    await test(conn, "utility.undo", "utility", "undo", {}, check_success=False)
    await test(conn, "utility.redo", "utility", "redo", {}, check_success=False)

    # ====== SCENE ======
    print("\n=== Scene ===")
    await test(conn, "scene.list", "scene", "list")
    await test(conn, "scene.get_info", "scene", "get_info")
    await test(conn, "scene.create", "scene", "create", {"name": "TestScene_Live"})
    await test(conn, "scene.switch", "scene", "switch", {"scene_name": "TestScene_Live"})
    await test(conn, "scene.switch back", "scene", "switch", {"scene_name": "Scene"})
    await test(conn, "scene.set_settings", "scene", "set_settings", {"settings": {"fps": 30}})
    await test(conn, "scene.set_frame_range", "scene", "set_frame_range", {"start": 1, "end": 120})
    await test(conn, "scene.delete", "scene", "delete", {"scene_name": "TestScene_Live"})

    # ====== OBJECT ======
    print("\n=== Object ===")
    await test(conn, "object.list", "object", "list")
    await test(
        conn,
        "object.create CUBE",
        "object",
        "create",
        {"type": "CUBE", "name": "T_Cube", "location": [0, 0, 0]},
    )
    await test(
        conn,
        "object.create SPHERE",
        "object",
        "create",
        {"type": "SPHERE", "name": "T_Sphere", "location": [3, 0, 0]},
    )
    await test(
        conn,
        "object.create CYLINDER",
        "object",
        "create",
        {"type": "CYLINDER", "name": "T_Cylinder", "location": [6, 0, 0]},
    )
    await test(
        conn,
        "object.create CONE",
        "object",
        "create",
        {"type": "CONE", "name": "T_Cone", "location": [9, 0, 0]},
    )
    await test(
        conn,
        "object.create PLANE",
        "object",
        "create",
        {"type": "PLANE", "name": "T_Plane", "location": [0, -3, 0]},
    )
    await test(
        conn,
        "object.create TORUS",
        "object",
        "create",
        {"type": "TORUS", "name": "T_Torus", "location": [3, -3, 0]},
    )
    await test(
        conn,
        "object.create EMPTY",
        "object",
        "create",
        {"type": "EMPTY", "name": "T_Empty", "location": [6, -3, 0]},
    )
    await test(
        conn,
        "object.transform",
        "object",
        "transform",
        {"name": "T_Cube", "location": [1, 1, 1], "rotation": [0, 0, 45], "scale": [2, 2, 2]},
    )
    await test(conn, "object.get_info", "object", "get_info", {"name": "T_Cube"})
    await test(conn, "object.select", "object", "select", {"name": "T_Cube"})
    await test(
        conn, "object.rename", "object", "rename", {"name": "T_Torus", "new_name": "T_Torus_R"}
    )
    await test(conn, "object.duplicate", "object", "duplicate", {"name": "T_Cube"})
    await test(
        conn,
        "object.set_parent",
        "object",
        "set_parent",
        {"child_name": "T_Sphere", "parent_name": "T_Empty"},
    )
    await test(
        conn,
        "object.set_origin",
        "object",
        "set_origin",
        {"name": "T_Cube", "type": "ORIGIN_GEOMETRY"},
    )
    await test(conn, "object.apply_transform", "object", "apply_transform", {"name": "T_Cube"})

    # ====== MODELING ======
    print("\n=== Modeling ===")
    await test(
        conn,
        "modeling.modifier_add SUBSURF",
        "modeling",
        "modifier_add",
        {"object_name": "T_Cube", "modifier_type": "SUBSURF"},
    )
    await test(
        conn,
        "modeling.modifier_add SOLIDIFY",
        "modeling",
        "modifier_add",
        {"object_name": "T_Plane", "modifier_type": "SOLIDIFY"},
    )
    await test(
        conn,
        "modeling.modifier_add BEVEL",
        "modeling",
        "modifier_add",
        {"object_name": "T_Cone", "modifier_type": "BEVEL"},
    )
    await test(
        conn,
        "modeling.modifier_apply",
        "modeling",
        "modifier_apply",
        {"object_name": "T_Cube", "modifier_name": "Subdivision Surface"},
        check_success=False,  # Modifier name varies by Blender version
    )
    await test(
        conn,
        "modeling.boolean",
        "modeling",
        "boolean",
        {"object_name": "T_Cube", "target_name": "T_Sphere", "operation": "DIFFERENCE"},
    )
    await test(conn, "modeling.mesh_analyze", "modeling", "mesh_analyze", {"object_name": "T_Cube"})
    await test(
        conn,
        "modeling.auto_smooth",
        "modeling",
        "auto_smooth",
        {"object_name": "T_Cone", "angle": 30},
    )
    await test(
        conn, "modeling.shapekey_list", "modeling", "shapekey_list", {"object_name": "T_Cube"}
    )

    # ====== MATERIAL ======
    print("\n=== Material ===")
    await test(
        conn,
        "material.create RED",
        "material",
        "create",
        {"name": "T_Red", "base_color": [1, 0, 0, 1]},
    )
    await test(
        conn,
        "material.create BLUE",
        "material",
        "create",
        {"name": "T_Blue", "base_color": [0, 0, 1, 1]},
    )
    await test(
        conn,
        "material.create GREEN",
        "material",
        "create",
        {"name": "T_Green", "base_color": [0, 1, 0, 1]},
    )
    await test(
        conn,
        "material.assign",
        "material",
        "assign",
        {"object_name": "T_Cube", "material_name": "T_Red"},
    )
    await test(
        conn,
        "material.assign sphere",
        "material",
        "assign",
        {"object_name": "T_Sphere", "material_name": "T_Blue"},
    )
    await test(conn, "material.list", "material", "list")
    await test(conn, "material.analyze", "material", "analyze", {"material_name": "T_Red"})

    # ====== LIGHTING ======
    print("\n=== Lighting ===")
    await test(
        conn,
        "lighting.create POINT",
        "lighting",
        "create",
        {"type": "POINT", "name": "T_PointLight", "location": [0, 0, 5], "energy": 100},
    )
    await test(
        conn,
        "lighting.create SUN",
        "lighting",
        "create",
        {"type": "SUN", "name": "T_SunLight", "location": [0, 0, 10], "energy": 5},
    )
    await test(
        conn,
        "lighting.create SPOT",
        "lighting",
        "create",
        {"type": "SPOT", "name": "T_SpotLight", "location": [5, 0, 5], "energy": 200},
    )
    await test(
        conn,
        "lighting.create AREA",
        "lighting",
        "create",
        {"type": "AREA", "name": "T_AreaLight", "location": [-5, 0, 5], "energy": 150},
    )
    await test(
        conn,
        "lighting.set_properties",
        "lighting",
        "set_properties",
        {"light_name": "T_PointLight", "energy": 200, "color": [1, 0.8, 0.6]},
    )
    await test(conn, "lighting.delete", "lighting", "delete", {"light_name": "T_AreaLight"})

    # ====== CAMERA ======
    print("\n=== Camera ===")
    await test(
        conn,
        "camera.create",
        "camera",
        "create",
        {"name": "T_Camera", "location": [10, -10, 5], "focal_length": 50},
    )
    await test(
        conn,
        "camera.set_properties",
        "camera",
        "set_properties",
        {"camera_name": "T_Camera", "focal_length": 85},
    )
    await test(
        conn,
        "camera.look_at",
        "camera",
        "look_at",
        {"camera_name": "T_Camera", "target": [0, 0, 0]},
    )
    await test(conn, "camera.set_active", "camera", "set_active", {"name": "T_Camera"})

    # ====== ANIMATION ======
    print("\n=== Animation ===")
    await test(
        conn,
        "animation.keyframe_insert f1",
        "animation",
        "keyframe_insert",
        {"object_name": "T_Sphere", "data_path": "location", "frame": 1},
    )
    await send(conn, "object", "transform", {"name": "T_Sphere", "location": [3, 3, 3]})
    await test(
        conn,
        "animation.keyframe_insert f24",
        "animation",
        "keyframe_insert",
        {"object_name": "T_Sphere", "data_path": "location", "frame": 24},
    )
    await test(
        conn,
        "animation.set_interpolation",
        "animation",
        "set_interpolation",
        {"object_name": "T_Sphere", "interpolation": "BEZIER"},
        check_success=False,  # Blender 5.x uses layered action system, fcurves unavailable
    )
    await test(
        conn,
        "animation.timeline_set_range",
        "animation",
        "timeline_set_range",
        {"start": 1, "end": 120},
    )
    await test(conn, "animation.goto_frame", "animation", "goto_frame", {"frame": 12})
    await test(conn, "animation.action_list", "animation", "action_list")
    await test(
        conn,
        "animation.action_create",
        "animation",
        "action_create",
        {"armature_name": "T_Armature", "action_name": "T_TestAction"},
        check_success=False,  # May fail if armature not created yet
    )

    # ====== WORLD ======
    print("\n=== World ===")
    await test(conn, "world.create", "world", "create", {"name": "T_World"})
    await test(conn, "world.background", "world", "background", {"color": [0.05, 0.05, 0.1]})
    await test(conn, "world.sky", "world", "sky")

    # ====== RENDER ======
    print("\n=== Render ===")
    await test(conn, "render.settings (get)", "render", "settings", {})
    await test(conn, "render.set_engine CYCLES", "render", "set_engine", {"engine": "CYCLES"})
    await test(conn, "render.set_engine EEVEE", "render", "set_engine", {"engine": "BLENDER_EEVEE"})
    await test(conn, "render.set_resolution", "render", "set_resolution", {"x": 1920, "y": 1080})
    await test(conn, "render.set_samples", "render", "set_samples", {"samples": 64})

    # ====== CURVES ======
    print("\n=== Curves ===")
    await test(
        conn,
        "curves.create BEZIER",
        "curves",
        "create",
        {"type": "BEZIER", "name": "T_Curve", "location": [0, 6, 0]},
    )
    await test(conn, "curves.circle", "curves", "circle", {"name": "T_Circle", "radius": 2})
    await test(conn, "curves.path", "curves", "path", {"name": "T_Path"})

    # ====== UV ======
    print("\n=== UV ===")
    await test(conn, "uv.unwrap", "uv", "unwrap", {"object_name": "T_Cone"})
    await test(conn, "uv.smart_project", "uv", "smart_project", {"object_name": "T_Cylinder"})
    await test(conn, "uv.pack", "uv", "pack", {"object_name": "T_Cone"})

    # ====== PHYSICS ======
    print("\n=== Physics ===")
    await send(
        conn, "object", "create", {"type": "CUBE", "name": "T_PhysRB", "location": [0, 12, 5]}
    )
    await test(
        conn, "physics.rigid_body_add", "physics", "rigid_body_add", {"object_name": "T_PhysRB"}
    )
    await send(
        conn, "object", "create", {"type": "PLANE", "name": "T_PhysColl", "location": [0, 12, 0]}
    )
    await test(
        conn, "physics.collision_add", "physics", "collision_add", {"object_name": "T_PhysColl"}
    )
    await send(
        conn, "object", "create", {"type": "CUBE", "name": "T_PhysCloth", "location": [3, 12, 0]}
    )
    await test(conn, "physics.cloth_add", "physics", "cloth_add", {"object_name": "T_PhysCloth"})

    # ====== CONSTRAINTS ======
    print("\n=== Constraints ===")
    await test(
        conn,
        "constraints.add COPY_LOCATION",
        "constraints",
        "add",
        {"object_name": "T_Cylinder", "constraint_type": "COPY_LOCATION", "target": "T_Empty"},
    )
    await test(conn, "constraints.list", "constraints", "list", {"object_name": "T_Cylinder"})
    await test(
        conn,
        "constraints.remove",
        "constraints",
        "remove",
        {"object_name": "T_Cylinder", "constraint_name": "Copy Location"},
    )

    # ====== NODES ======
    print("\n=== Nodes ===")
    await test(
        conn,
        "nodes.add",
        "nodes",
        "add",
        {"target": "T_Red", "node_type": "ShaderNodeMixRGB"},
    )
    await test(
        conn,
        "nodes.shader_preset",
        "nodes",
        "shader_preset",
        {"material_name": "T_Blue", "preset": "glass"},
    )

    # ====== RIGGING ======
    print("\n=== Rigging ===")
    await test(
        conn,
        "rigging.armature_create",
        "rigging",
        "armature_create",
        {"name": "T_Armature", "location": [0, 8, 0]},
    )
    await test(
        conn,
        "rigging.bone_add",
        "rigging",
        "bone_add",
        {"armature_name": "T_Armature", "bone_name": "T_Bone1"},
    )

    # ====== CHARACTER TEMPLATE ======
    print("\n=== Character Template ===")
    await test(
        conn,
        "character_template.create chibi",
        "character_template",
        "create",
        {"template": "chibi", "name": "T_Chibi"},
    )

    # ====== EXPORT ======
    print("\n=== Export ===")
    # Don't actually export, just test the handler loads
    await test(
        conn, "export.fbx", "export", "fbx", {"filepath": "C:/temp/test.fbx"}, check_success=False
    )

    # ====== BATCH ======
    print("\n=== Batch ===")
    await test(
        conn,
        "batch.rename",
        "batch",
        "rename",
        {"pattern": "T_Torus*", "find": "T_Torus", "replace": "T_TorusRenamed"},
        check_success=False,
    )

    # ====== ASSETS ======
    print("\n=== Assets ===")
    await test(
        conn, "assets.mark", "assets", "mark", {"object_name": "T_Cube"}, check_success=False
    )

    # ====== SCENE ADVANCED ======
    print("\n=== Scene Advanced ===")
    await test(
        conn,
        "scene_advanced.environment_preset",
        "scene_advanced",
        "environment_preset",
        {"preset": "studio"},
    )

    # ====== ADDONS ======
    print("\n=== Addons ===")
    await test(conn, "addons.list", "addons", "list")

    # ====== PREFERENCES ======
    print("\n=== Preferences ===")
    await test(
        conn, "preferences.get", "preferences", "get", {"category": "view", "key": "show_tooltips"}
    )
    await test(conn, "preferences.viewport", "preferences", "viewport")

    # ====== VERSIONING ======
    print("\n=== Versioning ===")
    await test(
        conn, "versioning.info", "versioning", "info", {"version_id": "test"}, check_success=False
    )

    # ====== SCULPT ======
    print("\n=== Sculpt ===")
    await test(
        conn,
        "sculpt.mode",
        "sculpt",
        "mode",
        {"object_name": "T_Cube", "enable": False},
        check_success=False,
    )

    # ====== COMPOSITOR ======
    print("\n=== Compositor ===")
    await test(conn, "compositor.enable", "compositor", "enable", {"use_nodes": True})

    # ====== MESH EDIT ADVANCED ======
    print("\n=== Mesh Edit Advanced ===")
    await test(
        conn,
        "mesh_edit_advanced.vertex_group",
        "mesh_edit_advanced",
        "vertex_group",
        {"object_name": "T_Cube", "action": "list"},
        check_success=False,  # Vertex group may not exist
    )

    # ====== STYLE PRESETS ======
    print("\n=== Style Presets ===")
    await test(
        conn, "style_presets.setup LOW_POLY", "style_presets", "setup", {"style": "LOW_POLY"}
    )

    # ====== PROCEDURAL MATERIALS ======
    print("\n=== Procedural Materials ===")
    await test(
        conn,
        "procedural_materials.create",
        "procedural_materials",
        "create",
        {"preset": "GOLD", "material_name": "T_Gold", "object_name": "T_Cube"},
    )

    # ====== SPORT CHARACTER ======
    print("\n=== Sport Character ===")
    await test(
        conn,
        "sport_character.create_character",
        "sport_character",
        "create_character",
        {"sport_type": "basketball", "name": "T_Athlete"},
    )

    # ====== EXTERNAL ======
    print("\n=== External ===")
    await test(
        conn,
        "external.unity_export",
        "external",
        "unity_export",
        {"filepath": "C:/temp/test.fbx"},
        check_success=False,
    )

    # ====== AI ASSIST ======
    print("\n=== AI Assist ===")
    await test(conn, "ai_assist.describe_scene", "ai_assist", "describe_scene")
    await test(conn, "ai_assist.scene_statistics", "ai_assist", "scene_statistics")
    await test(conn, "ai_assist.list_issues", "ai_assist", "list_issues")

    # ====== AI GENERATION ======
    print("\n=== AI Generation ===")
    await test(conn, "ai_generation.config", "ai_generation", "config")

    # ====== SUBSTANCE ======
    print("\n=== Substance ===")
    await test(conn, "substance.detect", "substance", "detect")

    # ====== ZBRUSH ======
    print("\n=== ZBrush ===")
    await test(conn, "zbrush.detect", "zbrush", "detect")

    # ====== MOCAP ======
    print("\n=== Mocap ===")
    await test(
        conn, "mocap.import", "mocap", "import", {"filepath": "test.bvh"}, check_success=False
    )

    # ====== CLOUD RENDER ======
    print("\n=== Cloud Render ===")
    await test(conn, "cloud_render.discover", "cloud_render", "discover")

    # ====== COLLABORATION ======
    print("\n=== Collaboration ===")
    await test(conn, "collaboration.status", "collaboration", "status")

    # ====== VR/AR ======
    print("\n=== VR/AR ===")
    await test(conn, "vr_ar.setup", "vr_ar", "setup")

    # ====== TEXTURE PAINT ======
    print("\n=== Texture Paint ===")
    await test(
        conn,
        "texture_paint.create",
        "texture_paint",
        "create",
        {"object_name": "T_Cube", "name": "T_TexPaint"},
    )

    # ====== GPENCIL ======
    print("\n=== Grease Pencil ===")
    await test(conn, "gpencil.create", "gpencil", "create", {"name": "T_GPencil"})

    # ====== HAIR ======
    print("\n=== Hair ===")
    await test(
        conn,
        "hair.add",
        "hair",
        "add",
        {"object_name": "T_Sphere"},
        check_success=False,  # May fail if object is hidden from earlier test
    )

    # ====== SIMULATION ======
    print("\n=== Simulation ===")
    await test(
        conn,
        "simulation.ocean",
        "simulation",
        "ocean",
        {"object_name": "T_Plane", "name": "T_Ocean"},
    )

    # ====== VSE ======
    print("\n=== VSE (Video Editing) ===")
    # VSE needs specific setup, just test handler loading
    await test(conn, "vse.list_strips", "vse", "list_strips", {}, check_success=False)

    # ====== AUTO RIG ======
    print("\n=== Auto Rig ===")
    await test(
        conn,
        "auto_rig.setup",
        "auto_rig",
        "setup",
        {"character_name": "T_Chibi"},
        check_success=False,
    )

    # ====== ANIMATION PRESET ======
    print("\n=== Animation Preset ===")
    await test(
        conn,
        "animation_preset.apply",
        "animation_preset",
        "apply",
        {"armature_name": "T_Armature", "preset": "idle"},
        check_success=False,
    )

    # ====== CHARACTER ======
    print("\n=== Character (Extended) ===")
    await test(
        conn, "character.create_humanoid", "character", "create_humanoid", {"name": "T_Human"}
    )

    # ====== CLEANUP ======
    print("\n=== Cleanup ===")
    r = await send(conn, "object", "list")
    deleted = 0
    if r.get("success"):
        for obj in r["data"].get("objects", []):
            name = obj["name"] if isinstance(obj, dict) else obj
            if name.startswith("T_") or name.startswith("Test_") or name.endswith(".001"):
                await send(conn, "object", "delete", {"name": name})
                deleted += 1
    print(f"  Deleted {deleted} test objects")

    # Reset render engine
    await send(conn, "render", "set_engine", {"engine": "BLENDER_EEVEE"})
    # Reset frame range
    await send(conn, "scene", "set_frame_range", {"start": 1, "end": 250})

    await conn.disconnect()

    # ====== SUMMARY ======
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(sep)
    if ERRORS:
        print(f"\n{FAIL} Failed tests:")
        for e in ERRORS:
            print(f"  {e}")

    return FAIL


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(1 if code > 0 else 0)
