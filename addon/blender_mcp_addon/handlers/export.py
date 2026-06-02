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

    fbx_kwargs = {
        "filepath": filepath,
        "use_selection": params.get("selected_only", False),
        "global_scale": params.get("global_scale", 1.0),
        "apply_unit_scale": apply_unit_scale,
        "apply_scale_options": params.get("apply_scale", "FBX_SCALE_ALL"),
        "use_space_transform": use_space_transform,
        "bake_space_transform": bake_space_transform,
        "axis_forward": axis_forward,
        "axis_up": axis_up,
        "mesh_smooth_type": mesh_smooth_type,
        "use_mesh_modifiers": params.get("use_mesh_modifiers", True),
        "use_armature_deform_only": params.get("use_armature_deform_only", False),
        "add_leaf_bones": params.get("add_leaf_bones", False),
        "primary_bone_axis": params.get("primary_bone_axis", "Y"),
        "secondary_bone_axis": params.get("secondary_bone_axis", "X"),
        "bake_anim": params.get("include_animation", True),
        "bake_anim_use_all_actions": params.get("bake_animation", False),
        "path_mode": params.get("path_mode", "AUTO"),
    }
    if object_types_set:
        fbx_kwargs["object_types"] = object_types_set

    # --- Zero-Transform contract guard (see UNITY_QUEST_EXPORT.md) ---
    # Under bake_space_transform, a non-zero object .location is carried into
    # the FBX node => the prop imports into Unity offset by metres, NOT at
    # (0,0,0). Auto-zero each exported object's .location for the export and
    # restore it after; warn (do not auto-apply) on unapplied rotation/scale,
    # which also bakes into the mesh.
    zero_tx = params.get("zero_transform_for_export", True)
    use_selection = params.get("selected_only", False)
    if use_selection:
        targets = list(bpy.context.selected_objects)
    else:
        targets = list(bpy.context.scene.objects)

    warnings = []
    saved_locations = {}
    eps = 1e-6
    for o in targets:
        if o.type not in {"MESH", "EMPTY", "ARMATURE", "CURVE", "SURFACE", "FONT"}:
            continue
        rot = tuple(o.rotation_euler)
        scl = tuple(o.scale)
        if any(abs(a) > 1e-5 for a in rot) or any(abs(a - 1.0) > 1e-5 for a in scl):
            warnings.append(
                f"{o.name}: unapplied rotation/scale will bake into the FBX "
                f"(rotation={[round(a, 4) for a in rot]}, scale={[round(a, 4) for a in scl]})"
            )
        if zero_tx and bake_space_transform and any(abs(a) > eps for a in o.location):
            saved_locations[o.name] = tuple(o.location)
            o.location = (0.0, 0.0, 0.0)

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
                "zeroed_for_export": list(saved_locations.keys()),
                "warnings": warnings,
            },
        }
    except Exception as e:
        return {"success": False, "error": {"code": "EXPORT_ERROR", "message": str(e)}}
    finally:
        for nm, loc in saved_locations.items():
            ob = bpy.data.objects.get(nm)
            if ob is not None:
                ob.location = loc


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


def handle_verify_fbx(params: dict[str, Any]) -> dict[str, Any]:
    """Re-import an exported FBX and assert game-engine readiness.

    Imports the file into the current .blend (then removes the imported
    datablocks), and checks the contract a modeling agent cares about:
    world origin at (0,0,0), triangle budget, one-object-per-file, material
    count, emissive slots. Returns pass/fail so an agent can self-verify each
    export instead of doing 45-file post-hoc QA. See UNITY_QUEST_EXPORT.md.
    """
    filepath = params.get("filepath")
    if not filepath or not os.path.exists(filepath):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"FBX not found: {filepath}"},
        }

    tri_budget = params.get("tri_budget")
    expect_origin = params.get("expect_origin", True)
    expect_single = params.get("expect_single_object", True)
    origin_eps = params.get("origin_epsilon", 1e-4)

    before_obj = {o.name for o in bpy.data.objects}
    before_mesh = {m.name for m in bpy.data.meshes}
    before_mat = {m.name for m in bpy.data.materials}
    before_img = {i.name for i in bpy.data.images}

    try:
        bpy.ops.import_scene.fbx(filepath=filepath)
    except Exception as e:
        return {"success": False, "error": {"code": "IMPORT_ERROR", "message": str(e)}}

    new_objs = [o for o in bpy.data.objects if o.name not in before_obj]
    meshes = [o for o in new_objs if o.type == "MESH"]

    objects_report = []
    total_tris = 0
    for o in meshes:
        wt = o.matrix_world.translation
        tcount = sum(len(p.vertices) - 2 for p in o.data.polygons)
        total_tris += tcount
        mats = [s.material.name for s in o.material_slots if s.material]
        emissive = []
        for s in o.material_slots:
            m = s.material
            if not m or not m.use_nodes:
                continue
            for n in m.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    es = n.inputs.get("Emission Strength")
                    if es is not None and es.default_value > 1e-4:
                        emissive.append(m.name)
        objects_report.append(
            {
                "name": o.name,
                "world_origin": [round(v, 5) for v in wt],
                "triangles": tcount,
                "materials": mats,
                "emissive_materials": emissive,
            }
        )

    failures = []
    if expect_single and len(meshes) != 1:
        failures.append(f"expected 1 mesh object, found {len(meshes)}")
    if expect_origin:
        for r in objects_report:
            if any(abs(v) > origin_eps for v in r["world_origin"]):
                failures.append(f"{r['name']} world origin {r['world_origin']} != (0,0,0)")
    if tri_budget is not None and total_tris > tri_budget:
        failures.append(f"triangles {total_tris} > budget {tri_budget}")

    # Clean up everything the import created so verification has no side effects.
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in [mm for mm in bpy.data.meshes if mm.name not in before_mesh]:
        bpy.data.meshes.remove(m)
    for m in [mm for mm in bpy.data.materials if mm.name not in before_mat]:
        bpy.data.materials.remove(m)
    for im in [ii for ii in bpy.data.images if ii.name not in before_img]:
        try:
            bpy.data.images.remove(im)
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "filepath": filepath,
            "passed": len(failures) == 0,
            "failures": failures,
            "object_count": len(meshes),
            "total_triangles": total_tris,
            "objects": objects_report,
        },
    }
