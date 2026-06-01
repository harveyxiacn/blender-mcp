"""
Describe handler - Scene understanding and inspection.

Runs inside Blender with full bpy access.
"""

from __future__ import annotations

from typing import Any

import bpy


def handle_scene(params: dict[str, Any]) -> dict[str, Any]:
    """Return a structured summary of the current scene."""
    fmt = params.get("format", "markdown")

    try:
        scene = bpy.context.scene

        # Count objects by type
        objects_by_type: dict[str, int] = {}
        all_objects: list[dict[str, Any]] = []
        for obj in scene.objects:
            obj_type = obj.type
            objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1
            all_objects.append({"name": obj.name, "type": obj_type})

        # Materials
        materials = [mat.name for mat in bpy.data.materials if mat.users > 0]

        # Lights
        lights = []
        for obj in scene.objects:
            if obj.type == "LIGHT" and obj.data:
                light_data: dict[str, Any] = {
                    "name": obj.name,
                    "type": obj.data.type,
                    "energy": round(obj.data.energy, 2),
                }
                if hasattr(obj.data, "color"):
                    light_data["color"] = [round(c, 3) for c in obj.data.color[:3]]
                lights.append(light_data)

        # Camera
        camera_info = None
        if scene.camera and scene.camera.data:
            cam = scene.camera.data
            camera_info = {
                "name": scene.camera.name,
                "lens": round(cam.lens, 1),
                "type": cam.type,
            }

        # Render settings
        render_info = {
            "engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "resolution_percentage": scene.render.resolution_percentage,
        }
        if scene.render.engine == "CYCLES":
            render_info["samples"] = scene.cycles.samples
        elif hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
            render_info["samples"] = scene.eevee.taa_render_samples

        # Frame range
        frame_range = [scene.frame_start, scene.frame_end]
        frame_current = scene.frame_current

        data = {
            "scene_name": scene.name,
            "object_count": len(scene.objects),
            "objects_by_type": objects_by_type,
            "objects": all_objects,
            "materials": materials,
            "lights": lights,
            "camera": camera_info,
            "render": render_info,
            "frame_range": frame_range,
            "frame_current": frame_current,
        }

        if fmt == "markdown":
            lines = [f"# Scene: {scene.name}", ""]

            # Object summary
            type_parts = [f"{count} {t.lower()}" for t, count in sorted(objects_by_type.items())]
            lines.append(f"**Objects:** {len(scene.objects)} total ({', '.join(type_parts)})")
            lines.append("")

            # Object list
            if all_objects:
                lines.append("**Object list:**")
                for obj_info in all_objects:
                    lines.append(f"  - {obj_info['name']} ({obj_info['type']})")
                lines.append("")

            # Materials
            if materials:
                lines.append(f"**Materials ({len(materials)}):** {', '.join(materials)}")
                lines.append("")

            # Lights
            if lights:
                lines.append("**Lights:**")
                for lt in lights:
                    lines.append(f"  - {lt['name']}: {lt['type']}, energy={lt['energy']}")
                lines.append("")

            # Camera
            if camera_info:
                lines.append(
                    f"**Camera:** {camera_info['name']} "
                    f"({camera_info['type']}, {camera_info['lens']}mm)"
                )
            else:
                lines.append("**Camera:** None set")
            lines.append("")

            # Render
            res = render_info["resolution"]
            lines.append(
                f"**Render:** {render_info['engine']} at "
                f"{res[0]}x{res[1]} ({render_info['resolution_percentage']}%)"
            )
            if "samples" in render_info:
                lines.append(f"**Samples:** {render_info['samples']}")
            lines.append("")

            # Frame
            lines.append(
                f"**Frames:** {frame_range[0]}-{frame_range[1]} "
                f"(current: {frame_current})"
            )

            data["summary"] = "\n".join(lines)

        return {"success": True, "data": data}

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DESCRIBE_SCENE_ERROR", "message": str(e)},
        }


def handle_hierarchy(params: dict[str, Any]) -> dict[str, Any]:
    """Return the full parent-child object tree."""
    fmt = params.get("format", "markdown")

    try:
        scene = bpy.context.scene

        # Build tree
        children_map: dict[str, list[str]] = {}
        root_objects: list[str] = []

        for obj in scene.objects:
            if obj.parent is None:
                root_objects.append(obj.name)
            else:
                parent_name = obj.parent.name
                if parent_name not in children_map:
                    children_map[parent_name] = []
                children_map[parent_name].append(obj.name)

        root_objects.sort()
        for k in children_map:
            children_map[k].sort()

        def build_tree_dict(name: str) -> dict[str, Any]:
            obj = bpy.data.objects.get(name)
            node: dict[str, Any] = {
                "name": name,
                "type": obj.type if obj else "UNKNOWN",
            }
            kids = children_map.get(name, [])
            if kids:
                node["children"] = [build_tree_dict(child) for child in kids]
            return node

        tree = [build_tree_dict(name) for name in root_objects]

        data: dict[str, Any] = {"roots": tree, "total_objects": len(scene.objects)}

        if fmt == "markdown":

            def tree_text(name: str, indent: int = 0) -> list[str]:
                obj = bpy.data.objects.get(name)
                obj_type = obj.type if obj else "?"
                prefix = "  " * indent + ("|- " if indent > 0 else "")
                lines = [f"{prefix}{name} [{obj_type}]"]
                for child in children_map.get(name, []):
                    lines.extend(tree_text(child, indent + 1))
                return lines

            text_lines = [f"Scene hierarchy ({len(scene.objects)} objects):", ""]
            for root in root_objects:
                text_lines.extend(tree_text(root))
            data["tree"] = "\n".join(text_lines)

        return {"success": True, "data": data}

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DESCRIBE_HIERARCHY_ERROR", "message": str(e)},
        }


def handle_object(params: dict[str, Any]) -> dict[str, Any]:
    """Deep inspection of a single object."""
    name = params.get("name", "")
    fmt = params.get("format", "markdown")

    if not name:
        return {
            "success": False,
            "error": {
                "code": "MISSING_PARAM",
                "message": "Object name is required.",
            },
        }

    obj = bpy.data.objects.get(name)
    if not obj:
        # Find close matches
        all_names = [o.name for o in bpy.data.objects]
        suggestions = [n for n in all_names if name.lower() in n.lower()][:5]
        msg = f"Object '{name}' not found."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions)}?"
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": msg,
                "suggestion": "Use 'blender_describe_scene' to list all objects in the scene.",
            },
        }

    try:
        data: dict[str, Any] = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation": [round(v, 4) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
            "visible": obj.visible_get(),
        }

        # Parent chain
        parent_chain = []
        p = obj.parent
        while p:
            parent_chain.append(p.name)
            p = p.parent
        data["parent_chain"] = parent_chain

        # Children
        data["children"] = [c.name for c in obj.children]

        # Mesh-specific stats
        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            data["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }
            # Count ngons (faces with >4 verts)
            ngons = sum(1 for p in mesh.polygons if len(p.vertices) > 4)
            tris = sum(1 for p in mesh.polygons if len(p.vertices) == 3)
            quads = sum(1 for p in mesh.polygons if len(p.vertices) == 4)
            data["mesh"]["triangles"] = tris
            data["mesh"]["quads"] = quads
            data["mesh"]["ngons"] = ngons

        # Bounding box
        if obj.bound_box:
            bb = [list(v) for v in obj.bound_box]
            mins = [min(v[i] for v in bb) for i in range(3)]
            maxs = [max(v[i] for v in bb) for i in range(3)]
            dims = [round(maxs[i] - mins[i], 4) for i in range(3)]
            data["bounding_box"] = {
                "min": [round(v, 4) for v in mins],
                "max": [round(v, 4) for v in maxs],
                "dimensions": dims,
            }

        # Material slots
        data["materials"] = []
        for slot in obj.material_slots:
            mat_info: dict[str, Any] = {"name": slot.material.name if slot.material else None}
            data["materials"].append(mat_info)

        # Modifiers
        data["modifiers"] = []
        for mod in obj.modifiers:
            data["modifiers"].append({"name": mod.name, "type": mod.type, "show_viewport": mod.show_viewport})

        # Constraints
        data["constraints"] = []
        for con in obj.constraints:
            data["constraints"].append({"name": con.name, "type": con.type, "enabled": con.enabled})

        # Markdown summary
        if fmt == "markdown":
            lines = [f"# Object: {obj.name} [{obj.type}]", ""]
            lines.append(
                f"**Location:** ({data['location'][0]}, {data['location'][1]}, {data['location'][2]})"
            )
            lines.append(
                f"**Scale:** ({data['scale'][0]}, {data['scale'][1]}, {data['scale'][2]})"
            )
            lines.append(f"**Visible:** {data['visible']}")
            lines.append("")

            if parent_chain:
                lines.append(f"**Parent chain:** {' > '.join(reversed(parent_chain))} > {obj.name}")
            if data["children"]:
                lines.append(f"**Children:** {', '.join(data['children'])}")
            lines.append("")

            if "mesh" in data:
                m = data["mesh"]
                lines.append(
                    f"**Mesh:** {m['vertices']} verts, {m['edges']} edges, "
                    f"{m['polygons']} faces ({m['triangles']} tris, {m['quads']} quads, {m['ngons']} ngons)"
                )
                lines.append("")

            if "bounding_box" in data:
                bb = data["bounding_box"]
                lines.append(
                    f"**Bounding box:** {bb['dimensions'][0]} x {bb['dimensions'][1]} x {bb['dimensions'][2]}"
                )
                lines.append("")

            if data["materials"]:
                mat_names = [m["name"] or "(empty slot)" for m in data["materials"]]
                lines.append(f"**Materials ({len(data['materials'])}):** {', '.join(mat_names)}")
                lines.append("")

            if data["modifiers"]:
                lines.append("**Modifiers:**")
                for mod in data["modifiers"]:
                    vis = "visible" if mod["show_viewport"] else "hidden"
                    lines.append(f"  - {mod['name']} ({mod['type']}, {vis})")
                lines.append("")

            if data["constraints"]:
                lines.append("**Constraints:**")
                for con in data["constraints"]:
                    en = "enabled" if con["enabled"] else "disabled"
                    lines.append(f"  - {con['name']} ({con['type']}, {en})")

            data["summary"] = "\n".join(lines)

        return {"success": True, "data": data}

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DESCRIBE_OBJECT_ERROR", "message": str(e)},
        }
