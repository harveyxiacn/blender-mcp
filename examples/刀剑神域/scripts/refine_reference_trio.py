"""
Reference-driven refinement pass for SAO trio (Kirito, Asuna, Sachi).
Run after AAA_v2_kirito.py + AAA_v2_asuna.py + AAA_v2_sachi.py.
"""

import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

BASE_DIR = Path(r"E:\Projects\blender-mcp\examples\刀剑神域")


def iter_meshes(prefix):
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name.startswith(prefix):
            yield obj


def world_bbox(objs):
    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    count = 0
    for obj in objs:
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            min_v.x = min(min_v.x, w.x)
            min_v.y = min(min_v.y, w.y)
            min_v.z = min(min_v.z, w.z)
            max_v.x = max(max_v.x, w.x)
            max_v.y = max(max_v.y, w.y)
            max_v.z = max(max_v.z, w.z)
            count += 1
    if count == 0:
        return None
    return min_v, max_v


def scale_move_character(prefix, target_height, target_x) -> None:
    objs = list(iter_meshes(prefix))
    bb = world_bbox(objs)
    if not bb:
        return

    min_v, max_v = bb
    cur_h = max_v.z - min_v.z
    if cur_h < 1e-5:
        return

    s = target_height / cur_h

    # Scale around world origin; most assets are authored in mesh coordinates.
    for obj in objs:
        obj.scale = (obj.scale.x * s, obj.scale.y * s, obj.scale.z * s)
        obj.location = obj.location * s

    min_v2, max_v2 = world_bbox(objs)
    cx = (min_v2.x + max_v2.x) * 0.5
    dz = -min_v2.z
    dx = target_x - cx

    for obj in objs:
        obj.location.x += dx
        obj.location.z += dz


def taper_mesh_xy(obj, top_scale=1.0, bottom_scale=1.0) -> None:
    if obj.type != "MESH":
        return

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    if not bm.verts:
        bm.free()
        return

    min_z = min(v.co.z for v in bm.verts)
    max_z = max(v.co.z for v in bm.verts)
    span = max(1e-6, max_z - min_z)

    for v in bm.verts:
        t = (v.co.z - min_z) / span
        s = bottom_scale * (1.0 - t) + top_scale * t
        v.co.x *= s
        v.co.y *= s

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def recalc_normals_all() -> None:
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()


def set_auto_smooth_all(angle_deg=35.0) -> None:
    angle = math.radians(angle_deg)
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        mesh = obj.data
        if hasattr(mesh, "use_auto_smooth"):
            mesh.use_auto_smooth = True
        if hasattr(mesh, "auto_smooth_angle"):
            mesh.auto_smooth_angle = angle


def scale_if_exists(name, sx=1.0, sy=1.0, sz=1.0) -> None:
    obj = bpy.data.objects.get(name)
    if not obj:
        return
    obj.scale.x *= sx
    obj.scale.y *= sy
    obj.scale.z *= sz


def add_reference_images() -> None:
    ref_col = bpy.data.collections.get("SAO_Refs")
    if not ref_col:
        ref_col = bpy.data.collections.new("SAO_Refs")
        bpy.context.scene.collection.children.link(ref_col)

    refs = [
        ("REF_Kirito", BASE_DIR / "桐人.jpg", -2.1),
        ("REF_Asuna", BASE_DIR / "亚丝娜.jpg", 0.0),
        ("REF_Sachi", BASE_DIR / "幸.png", 2.1),
    ]

    for name, path, x in refs:
        if not path.exists():
            continue

        obj = bpy.data.objects.get(name)
        if obj is None:
            bpy.ops.object.empty_image_add(location=(x, -1.8, 1.0))
            obj = bpy.context.active_object
            obj.name = name
            obj.empty_display_type = "IMAGE"
            obj.data = bpy.data.images.load(str(path), check_existing=True)
            obj.empty_image_depth = "BACK"
            obj.empty_image_side = "FRONT"
            obj.empty_display_size = 1.65
            obj.rotation_euler = (math.radians(90), 0.0, 0.0)

        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        ref_col.objects.link(obj)


def refine_material_colors() -> None:
    # Lift very dark values so silhouettes retain anime detail under toon lighting.
    remap = {
        "M_KiritoBlack": (0.08, 0.09, 0.12),
        "M_KiritoHair": (0.07, 0.08, 0.12),
        "M_AsunaHair": (0.78, 0.47, 0.24),
        "M_AsunaRed": (0.82, 0.24, 0.27),
        "M_SachiHair": (0.11, 0.14, 0.30),
        "M_SachiBlue": (0.22, 0.29, 0.58),
        "M_SachiLightBlue": (0.70, 0.84, 0.96),
    }

    for name, rgb in remap.items():
        mat = bpy.data.materials.get(name)
        if not mat or not mat.use_nodes:
            continue
        nodes = mat.node_tree.nodes
        for n in nodes:
            if n.type == "BSDF_DIFFUSE":
                n.inputs["Color"].default_value = (*rgb, 1.0)


def setup_lighting_camera_world() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = False

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.87, 0.89, 0.94, 1.0)
        bg.inputs[1].default_value = 0.9

    # Keep existing lights but normalize energies.
    for obj in bpy.data.objects:
        if obj.type != "LIGHT":
            continue
        if obj.name == "KeyLight":
            obj.data.energy = 4.0
        elif obj.name == "FillLight":
            obj.data.energy = 1.6
        elif obj.name == "RimLight":
            obj.data.energy = 2.4

    cam = bpy.data.objects.get("MainCamera")
    if cam is None:
        bpy.ops.object.camera_add(location=(0.0, -7.5, 1.45))
        cam = bpy.context.active_object
        cam.name = "MainCamera"
    cam.location = (0.0, -7.5, 1.45)
    cam.rotation_euler = (math.radians(82), 0.0, 0.0)
    cam.data.lens = 58
    scene.camera = cam


def hide_noise_objects() -> None:
    # Keep trio and their swords; hide helper/noise if present.
    keep_prefix = (
        "K_",
        "A_",
        "SA_",
        "E_",
        "LL_",
        "MainCamera",
        "KeyLight",
        "FillLight",
        "RimLight",
    )
    for obj in bpy.data.objects:
        if obj.name.startswith("REF_"):
            obj.hide_render = True
            continue
        if obj.name in ("Camera",):
            obj.hide_render = True
            continue
        if any(obj.name.startswith(p) for p in keep_prefix if p.endswith("_")) or obj.name in (
            "MainCamera",
            "KeyLight",
            "FillLight",
            "RimLight",
        ):
            obj.hide_render = False
        else:
            # Keep scene clean for character turntable output.
            if obj.type in {"MESH", "EMPTY"}:
                obj.hide_render = True


def run() -> None:
    # 1) Add refs for alignment.
    add_reference_images()

    # 2) Normalize character heights and placement based on reference sheets.
    scale_move_character("K_", target_height=1.72, target_x=-2.0)
    scale_move_character("A_", target_height=1.68, target_x=0.0)
    scale_move_character("SA_", target_height=1.58, target_x=2.0)

    # 3) Silhouette refinements from reference sheets.
    for name, top, bot in [
        ("K_Coat", 0.84, 1.10),
        ("A_SkirtOuter", 0.86, 1.14),
        ("A_SkirtInner", 0.90, 1.08),
        ("SA_Skirt", 0.92, 1.08),
        ("SA_Vest", 0.94, 1.03),
    ]:
        obj = bpy.data.objects.get(name)
        if obj:
            taper_mesh_xy(obj, top_scale=top, bottom_scale=bot)

    # Head/eye/hair proportional refinements.
    scale_if_exists("K_Head", 1.02, 0.98, 1.04)
    scale_if_exists("A_Head", 1.00, 0.98, 1.03)
    scale_if_exists("SA_Head", 1.02, 0.98, 1.02)

    for nm in ["K_EyeWL", "K_EyeWR", "K_IrisL", "K_IrisR"]:
        scale_if_exists(nm, 1.12, 1.0, 1.10)
    for nm in ["A_EyeWL", "A_EyeWR", "A_IrisL", "A_IrisR"]:
        scale_if_exists(nm, 1.06, 1.0, 1.05)
    for nm in ["SA_EyeWL", "SA_EyeWR", "SA_IrisL", "SA_IrisR"]:
        scale_if_exists(nm, 1.12, 1.0, 1.08)

    scale_if_exists("K_HairBase", 1.08, 1.02, 1.06)
    scale_if_exists("A_HairBase", 1.04, 1.00, 1.04)
    scale_if_exists("SA_HairBase", 1.06, 1.02, 1.05)

    # 4) Shading hygiene.
    recalc_normals_all()
    set_auto_smooth_all(angle_deg=36.0)
    refine_material_colors()

    # 5) Render setup and cleanup.
    setup_lighting_camera_world()
    hide_noise_objects()

    print("Reference refinement pass done.")


run()
