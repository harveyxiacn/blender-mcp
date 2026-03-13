"""
Object Handler

Handles object-related commands.
"""

import fnmatch
from typing import Any

import bpy
import mathutils


def _create_mesh_primitive(obj_type: str, mp: dict[str, Any]) -> None:
    """Create a mesh primitive based on type and mesh_params"""
    if obj_type in ("SPHERE", "UV_SPHERE"):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=mp.get("segments", 32),
            ring_count=mp.get("ring_count", 16),
            radius=mp.get("radius", 1.0),
        )
    elif obj_type == "ICO_SPHERE":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=mp.get("subdivisions", 2),
            radius=mp.get("radius", 1.0),
        )
    elif obj_type == "CYLINDER":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=mp.get("vertices", 32),
            radius=mp.get("radius", 1.0),
            depth=mp.get("depth", 2.0),
            end_fill_type=mp.get("fill_type", "NGON"),
        )
    elif obj_type == "CONE":
        bpy.ops.mesh.primitive_cone_add(
            vertices=mp.get("vertices", 32),
            radius1=mp.get("radius1", 1.0),
            radius2=mp.get("radius2", 0.0),
            depth=mp.get("depth", 2.0),
            end_fill_type=mp.get("fill_type", "NGON"),
        )
    elif obj_type == "TORUS":
        bpy.ops.mesh.primitive_torus_add(
            major_segments=mp.get("major_segments", 48),
            minor_segments=mp.get("minor_segments", 12),
            major_radius=mp.get("major_radius", 1.0),
            minor_radius=mp.get("minor_radius", 0.25),
        )
    elif obj_type == "CIRCLE":
        bpy.ops.mesh.primitive_circle_add(
            vertices=mp.get("vertices", 32),
            radius=mp.get("radius", 1.0),
            fill_type=mp.get("fill_type", "NOTHING"),
        )
    elif obj_type == "GRID":
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=mp.get("x_subdivisions", 10),
            y_subdivisions=mp.get("y_subdivisions", 10),
            size=mp.get("size", 2.0),
        )
    elif obj_type == "CUBE":
        bpy.ops.mesh.primitive_cube_add(
            size=mp.get("size", 2.0),
        )
    elif obj_type == "PLANE":
        bpy.ops.mesh.primitive_plane_add(
            size=mp.get("size", 2.0),
        )
    elif obj_type == "MONKEY":
        bpy.ops.mesh.primitive_monkey_add()
    else:
        return False
    return True


def handle_create(params: dict[str, Any]) -> dict[str, Any]:
    """Create an object"""
    obj_type = params.get("type", "CUBE")
    name = params.get("name")
    location = params.get("location", [0, 0, 0])
    rotation = params.get("rotation", [0, 0, 0])
    scale = params.get("scale", [1, 1, 1])
    mp = params.get("mesh_params", {}) or {}

    # Create mesh object
    mesh_types = [
        "CUBE",
        "SPHERE",
        "UV_SPHERE",
        "ICO_SPHERE",
        "CYLINDER",
        "CONE",
        "TORUS",
        "PLANE",
        "CIRCLE",
        "GRID",
        "MONKEY",
    ]

    if obj_type in mesh_types:
        result = _create_mesh_primitive(obj_type, mp)
        if result is False:
            return {
                "success": False,
                "error": {"code": "INVALID_TYPE", "message": f"Unsupported mesh type: {obj_type}"},
            }
    elif obj_type == "EMPTY":
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    elif obj_type == "TEXT":
        bpy.ops.object.text_add(location=location)
    elif obj_type == "CAMERA":
        bpy.ops.object.camera_add(location=location)
    elif obj_type == "LIGHT":
        bpy.ops.object.light_add(type="POINT", location=location)
    elif obj_type == "ARMATURE":
        bpy.ops.object.armature_add(location=location)
    elif obj_type == "LATTICE":
        u_res = mp.get("u_resolution", 2)
        v_res = mp.get("v_resolution", 2)
        w_res = mp.get("w_resolution", 2)
        bpy.ops.object.add(type="LATTICE", location=location)
        lat = bpy.context.active_object.data
        lat.points_u = u_res
        lat.points_v = v_res
        lat.points_w = w_res
    else:
        return {
            "success": False,
            "error": {"code": "INVALID_TYPE", "message": f"Unsupported object type: {obj_type}"},
        }

    # Get the newly created object
    obj = bpy.context.active_object

    # Set transform
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale

    # Rename
    if name:
        obj.name = name

    return {
        "success": True,
        "data": {"object_name": obj.name, "object_type": obj.type, "location": list(obj.location)},
    }


def handle_delete(params: dict[str, Any]) -> dict[str, Any]:
    """Delete an object"""
    name = params.get("name")
    delete_data = params.get("delete_data", True)

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    # Save data reference
    data = obj.data if delete_data else None

    # Delete object
    bpy.data.objects.remove(obj, do_unlink=True)

    # Delete data
    if data:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)
        # Other types...

    return {"success": True, "data": {}}


def handle_duplicate(params: dict[str, Any]) -> dict[str, Any]:
    """Duplicate an object"""
    name = params.get("name")
    new_name = params.get("new_name")
    linked = params.get("linked", False)
    offset = params.get("offset", [0, 0, 0])

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    # Duplicate object
    if linked:
        new_obj = obj.copy()
    else:
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()

    # Set name
    if new_name:
        new_obj.name = new_name

    # Set position offset
    new_obj.location = (
        obj.location.x + offset[0],
        obj.location.y + offset[1],
        obj.location.z + offset[2],
    )

    # Link to scene
    bpy.context.collection.objects.link(new_obj)

    return {"success": True, "data": {"new_object_name": new_obj.name}}


def handle_transform(params: dict[str, Any]) -> dict[str, Any]:
    """Transform an object"""
    name = params.get("name")

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    # Absolute transform
    if "location" in params:
        obj.location = params["location"]
    if "rotation" in params:
        obj.rotation_euler = params["rotation"]
    if "scale" in params:
        obj.scale = params["scale"]

    # Incremental transform
    if "delta_location" in params:
        delta = params["delta_location"]
        obj.location = (
            obj.location.x + delta[0],
            obj.location.y + delta[1],
            obj.location.z + delta[2],
        )
    if "delta_rotation" in params:
        delta = params["delta_rotation"]
        obj.rotation_euler = (
            obj.rotation_euler.x + delta[0],
            obj.rotation_euler.y + delta[1],
            obj.rotation_euler.z + delta[2],
        )
    if "delta_scale" in params:
        delta = params["delta_scale"]
        obj.scale = (obj.scale.x + delta[0], obj.scale.y + delta[1], obj.scale.z + delta[2])

    return {
        "success": True,
        "data": {
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        },
    }


def handle_select(params: dict[str, Any]) -> dict[str, Any]:
    """Select objects"""
    names = params.get("names")
    pattern = params.get("pattern")
    deselect_all = params.get("deselect_all", True)
    set_active = params.get("set_active")

    # Deselect all
    if deselect_all:
        bpy.ops.object.select_all(action="DESELECT")

    selected_count = 0

    # Select by name
    if names:
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
                selected_count += 1

    # Select by pattern
    if pattern:
        for obj in bpy.data.objects:
            if fnmatch.fnmatch(obj.name, pattern):
                obj.select_set(True)
                selected_count += 1

    # Set active object
    if set_active:
        obj = bpy.data.objects.get(set_active)
        if obj:
            bpy.context.view_layer.objects.active = obj

    return {"success": True, "data": {"selected_count": selected_count}}


def handle_list(params: dict[str, Any]) -> dict[str, Any]:
    """List objects"""
    type_filter = params.get("type_filter")
    name_pattern = params.get("name_pattern")
    limit = params.get("limit", 50)

    objects = []

    for obj in bpy.data.objects:
        # Type filter
        if type_filter and obj.type != type_filter:
            continue

        # Name filter
        if name_pattern and not fnmatch.fnmatch(obj.name, name_pattern):
            continue

        objects.append(
            {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "visible": obj.visible_get(),
            }
        )

        if len(objects) >= limit:
            break

    return {"success": True, "data": {"objects": objects, "total": len(bpy.data.objects)}}


def handle_get_info(params: dict[str, Any]) -> dict[str, Any]:
    """Get object info"""
    name = params.get("name")
    include_mesh_stats = params.get("include_mesh_stats", True)
    include_modifiers = params.get("include_modifiers", True)
    include_materials = params.get("include_materials", True)

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
    }

    # Mesh statistics
    if include_mesh_stats and obj.type == "MESH" and obj.data:
        mesh = obj.data
        data["mesh_stats"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons),
        }

    # Modifiers
    if include_modifiers:
        data["modifiers"] = [mod.name for mod in obj.modifiers]

    # Materials
    if include_materials:
        data["materials"] = [
            slot.material.name if slot.material else None for slot in obj.material_slots
        ]

    return {"success": True, "data": data}


def handle_rename(params: dict[str, Any]) -> dict[str, Any]:
    """Rename an object"""
    name = params.get("name")
    new_name = params.get("new_name")

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    obj.name = new_name

    return {"success": True, "data": {"new_name": obj.name}}


def handle_set_parent(params: dict[str, Any]) -> dict[str, Any]:
    """Set parent-child relationship"""
    child_name = params.get("child_name")
    parent_name = params.get("parent_name")
    keep_transform = params.get("keep_transform", True)

    if not child_name:
        return {
            "success": False,
            "error": {
                "code": "MISSING_PARAM",
                "message": "child_name parameter is required",
            },
        }

    child = bpy.data.objects.get(child_name)
    if not child:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"Child object not found: {child_name}",
            },
        }

    if parent_name:
        parent = bpy.data.objects.get(parent_name)
        if not parent:
            return {
                "success": False,
                "error": {
                    "code": "OBJECT_NOT_FOUND",
                    "message": f"Parent object not found: {parent_name}",
                },
            }

        if keep_transform:
            child.parent = parent
            child.matrix_parent_inverse = parent.matrix_world.inverted()
        else:
            child.parent = parent
    else:
        child.parent = None

    return {"success": True, "data": {}}


def handle_join(params: dict[str, Any]) -> dict[str, Any]:
    """Join objects"""
    objects = params.get("objects", [])
    target = params.get("target")

    if len(objects) < 2:
        return {
            "success": False,
            "error": {
                "code": "INVALID_PARAMS",
                "message": "At least two objects are required to join",
            },
        }

    # Deselect all
    bpy.ops.object.select_all(action="DESELECT")

    # Select objects to join
    target_obj = None
    for name in objects:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.select_set(True)
            if target and name == target or target_obj is None:
                target_obj = obj

    if not target_obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": "No objects found to join"},
        }

    # Set active object
    bpy.context.view_layer.objects.active = target_obj

    # Join
    bpy.ops.object.join()

    return {"success": True, "data": {"result_object": bpy.context.active_object.name}}


def handle_set_origin(params: dict[str, Any]) -> dict[str, Any]:
    """Set object origin

    Args:
        params:
            - name: Object name
            - origin_type: Origin type
                - GEOMETRY: Origin to geometry center
                - CURSOR: Origin to 3D cursor
                - BOTTOM: Origin to bottom center (feet)
                - CENTER_OF_MASS: Origin to center of mass
                - CENTER_OF_VOLUME: Origin to center of volume
            - center: Geometry center calculation method (MEDIAN, BOUNDS)
    """
    name = params.get("name")
    origin_type = params.get("origin_type", "GEOMETRY")
    center = params.get("center", "MEDIAN")

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    # Save current selection and active object
    original_active = bpy.context.view_layer.objects.active
    original_selected = list(bpy.context.selected_objects)

    # Select target object
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        if origin_type == "GEOMETRY":
            # Origin to geometry center
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center=center)
        elif origin_type == "CURSOR":
            # Origin to 3D cursor
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        elif origin_type == "BOTTOM":
            # Origin to bottom center (for characters, feet)
            if obj.type == "MESH":
                # Get object bounding box
                bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                # Find lowest point
                min_z = min(v.z for v in bbox)
                # Calculate bottom center
                center_x = sum(v.x for v in bbox) / 8
                center_y = sum(v.y for v in bbox) / 8

                # Save current cursor position
                cursor_loc = bpy.context.scene.cursor.location.copy()

                # Move cursor to bottom center
                bpy.context.scene.cursor.location = (center_x, center_y, min_z)

                # Set origin to cursor
                bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

                # Restore cursor position
                bpy.context.scene.cursor.location = cursor_loc
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_TYPE",
                        "message": "BOTTOM origin type only supports mesh objects",
                    },
                }
        elif origin_type == "CENTER_OF_MASS":
            # Origin to center of mass (surface)
            bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="MEDIAN")
        elif origin_type == "CENTER_OF_VOLUME":
            # Origin to center of volume
            bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME", center="MEDIAN")
        else:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ORIGIN_TYPE",
                    "message": f"Unsupported origin type: {origin_type}",
                },
            }

        # Restore selection
        bpy.ops.object.select_all(action="DESELECT")
        for o in original_selected:
            if o:
                o.select_set(True)
        if original_active:
            bpy.context.view_layer.objects.active = original_active

        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "origin_type": origin_type,
                "new_origin": list(obj.location),
            },
        }
    except Exception as e:
        return {"success": False, "error": {"code": "SET_ORIGIN_ERROR", "message": str(e)}}


def handle_apply_transform(params: dict[str, Any]) -> dict[str, Any]:
    """Apply transform

    Args:
        params:
            - name: Object name
            - location: Apply location
            - rotation: Apply rotation
            - scale: Apply scale
    """
    name = params.get("name")
    apply_location = params.get("location", False)
    apply_rotation = params.get("rotation", False)
    apply_scale = params.get("scale", True)

    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"Object not found: {name}"},
        }

    # Select object
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.object.transform_apply(
            location=apply_location, rotation=apply_rotation, scale=apply_scale
        )

        return {"success": True, "data": {"object_name": obj.name}}
    except Exception as e:
        return {"success": False, "error": {"code": "APPLY_TRANSFORM_ERROR", "message": str(e)}}
