"""
Build rigged, fully movable Kirito + Asuna models from the AAA meshes.

Run after:
1) AAA_v2_kirito.py
2) AAA_v2_asuna.py
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


OUT_BLEND = Path(r"E:\Projects\blender-mcp\examples\sao_kirito_asuna_rigged.blend")
OUT_PREVIEW = Path(r"E:\Projects\blender-mcp\examples\sao_kirito_asuna_rigged_preview.png")
OUT_PREVIEW_NEUTRAL = Path(r"E:\Projects\blender-mcp\examples\sao_kirito_asuna_rigged_preview_f1.png")


def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def move_to_collection(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    for user_col in list(obj.users_collection):
        user_col.objects.unlink(obj)
    if col.objects.get(obj.name) is None:
        col.objects.link(obj)


def bbox_world(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    for c in obj.bound_box:
        w = obj.matrix_world @ Vector(c)
        min_v.x = min(min_v.x, w.x)
        min_v.y = min(min_v.y, w.y)
        min_v.z = min(min_v.z, w.z)
        max_v.x = max(max_v.x, w.x)
        max_v.y = max(max_v.y, w.y)
        max_v.z = max(max_v.z, w.z)
    return min_v, max_v


def bbox_center(min_v: Vector, max_v: Vector) -> Vector:
    return (min_v + max_v) * 0.5


def point_lerp(a: Vector, b: Vector, t: float) -> Vector:
    return a + (b - a) * t


def deselect_all() -> None:
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


def create_bridge_cylinder(name: str, p0: Vector, p1: Vector, radius: float, material: bpy.types.Material | None) -> bpy.types.Object:
    direction = p1 - p0
    depth = max(0.01, direction.length)
    mid = (p0 + p1) * 0.5

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=mid)
    cyl = bpy.context.view_layer.objects.active
    if cyl is None:
        raise RuntimeError("Failed to create bridge cylinder.")
    cyl.name = name

    if direction.length > 1e-6:
        q = direction.normalized().to_track_quat("Z", "Y")
        cyl.rotation_mode = "QUATERNION"
        cyl.rotation_quaternion = q
        cyl.rotation_mode = "XYZ"

    if material is not None:
        if cyl.data.materials:
            cyl.data.materials[0] = material
        else:
            cyl.data.materials.append(material)
    return cyl


def fuse_connectors(target_mesh: bpy.types.Object, connectors: list[bpy.types.Object]) -> None:
    bpy.context.view_layer.objects.active = target_mesh
    for i, con in enumerate(connectors):
        if con is None:
            continue
        mod = target_mesh.modifiers.new(name=f"Fuse_{i}", type="BOOLEAN")
        mod.operation = "UNION"
        mod.solver = "MANIFOLD"
        mod.object = con
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(con, do_unlink=True)


def join_character_mesh(
    prefix: str,
    torso_name: str,
    arm_l_name: str,
    arm_r_name: str,
    leg_l_name: str,
    leg_r_name: str,
    out_name: str,
) -> bpy.types.Object:
    torso_src = bpy.data.objects.get(torso_name)
    arm_l_src = bpy.data.objects.get(arm_l_name)
    arm_r_src = bpy.data.objects.get(arm_r_name)
    leg_l_src = bpy.data.objects.get(leg_l_name)
    leg_r_src = bpy.data.objects.get(leg_r_name)
    if not all([torso_src, arm_l_src, arm_r_src, leg_l_src, leg_r_src]):
        raise RuntimeError(f"Missing source joints for {prefix}")

    tmin, tmax = bbox_world(torso_src)
    amin_l, amax_l = bbox_world(arm_l_src)
    amin_r, amax_r = bbox_world(arm_r_src)
    lmin_l, lmax_l = bbox_world(leg_l_src)
    lmin_r, lmax_r = bbox_world(leg_r_src)
    tc = bbox_center(tmin, tmax)
    h = max(0.5, tmax.z - tmin.z)

    # Shoulder/hip bridge points in world space (before join).
    shoulder_z = tmin.z + (tmax.z - tmin.z) * 0.72
    hip_z = tmin.z + (tmax.z - tmin.z) * 0.42
    p_torso_sh_l = Vector((tmax.x, tc.y, shoulder_z))
    p_torso_sh_r = Vector((tmin.x, tc.y, shoulder_z))
    p_arm_l = Vector((amin_l.x, (amin_l.y + amax_l.y) * 0.5, point_lerp(amin_l, amax_l, 0.82).z))
    p_arm_r = Vector((amax_r.x, (amin_r.y + amax_r.y) * 0.5, point_lerp(amin_r, amax_r, 0.82).z))

    meshes = [
        o for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith(prefix) and not o.name.startswith(("LL_", "K_Elucidator"))
    ]
    if not meshes:
        raise RuntimeError(f"No meshes found for prefix: {prefix}")

    torso = bpy.data.objects.get(torso_name)
    if torso is None or torso.type != "MESH":
        raise RuntimeError(f"Torso mesh not found: {torso_name}")

    deselect_all()
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()

    merged = bpy.context.view_layer.objects.active
    if merged is None:
        raise RuntimeError(f"Join failed for {prefix}")
    merged.name = out_name

    # Cleanup and unify split parts into one continuous deformable shell.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0015)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Add bridge connectors and fuse them, keeping original materials intact.
    # Use torso first material for connectors so visual seams are less obvious.
    mat = merged.data.materials[0] if merged.data.materials else None
    radius_sh = h * 0.035
    radius_hip = h * 0.040
    connectors = [
        create_bridge_cylinder(f"{prefix}Bridge_ShL", p_torso_sh_l, p_arm_l, radius_sh, mat),
        create_bridge_cylinder(f"{prefix}Bridge_ShR", p_torso_sh_r, p_arm_r, radius_sh, mat),
    ]
    fuse_connectors(merged, connectors)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0022)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.shade_smooth()
    return merged


def create_basic_humanoid_rig(name: str, mesh_obj: bpy.types.Object) -> bpy.types.Object:
    min_v, max_v = bbox_world(mesh_obj)
    h = max(0.5, max_v.z - min_v.z)
    cx = (min_v.x + max_v.x) * 0.5
    cy = (min_v.y + max_v.y) * 0.5

    pelvis_z = min_v.z + h * 0.50
    chest_z = min_v.z + h * 0.68
    neck_z = min_v.z + h * 0.81
    head_z = min_v.z + h * 0.88
    head_top_z = min_v.z + h * 0.98
    knee_z = min_v.z + h * 0.23
    ankle_z = min_v.z + h * 0.07

    shoulder_span = h * 0.12
    elbow_x = shoulder_span + h * 0.13
    hand_x = elbow_x + h * 0.11
    hip_span = h * 0.06
    foot_len = h * 0.07

    arm_data = bpy.data.armatures.new(f"{name}_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    eb = arm_data.edit_bones
    if eb.get("Bone"):
        eb.remove(eb["Bone"])

    root = eb.new("root")
    root.head = (cx, cy, min_v.z)
    root.tail = (cx, cy, min_v.z + h * 0.06)

    pelvis = eb.new("pelvis")
    pelvis.head = (cx, cy, pelvis_z - h * 0.02)
    pelvis.tail = (cx, cy, pelvis_z + h * 0.03)
    pelvis.parent = root

    spine = eb.new("spine")
    spine.head = pelvis.tail
    spine.tail = (cx, cy, chest_z - h * 0.05)
    spine.parent = pelvis
    spine.use_connect = True

    chest = eb.new("chest")
    chest.head = spine.tail
    chest.tail = (cx, cy, chest_z)
    chest.parent = spine
    chest.use_connect = True

    neck = eb.new("neck")
    neck.head = chest.tail
    neck.tail = (cx, cy, neck_z)
    neck.parent = chest
    neck.use_connect = True

    head = eb.new("head")
    head.head = neck.tail
    head.tail = (cx, cy, head_top_z)
    head.parent = neck
    head.use_connect = True

    for side, sx in (("L", 1.0), ("R", -1.0)):
        clav = eb.new(f"clavicle.{side}")
        clav.head = chest.tail
        clav.tail = (cx + sx * shoulder_span, cy, chest_z)
        clav.parent = chest

        upper = eb.new(f"upper_arm.{side}")
        upper.head = clav.tail
        upper.tail = (cx + sx * elbow_x, cy, chest_z - h * 0.04)
        upper.parent = clav
        upper.use_connect = True

        fore = eb.new(f"forearm.{side}")
        fore.head = upper.tail
        fore.tail = (cx + sx * hand_x, cy, chest_z - h * 0.10)
        fore.parent = upper
        fore.use_connect = True

        hand = eb.new(f"hand.{side}")
        hand.head = fore.tail
        hand.tail = (cx + sx * (hand_x + h * 0.04), cy, chest_z - h * 0.12)
        hand.parent = fore
        hand.use_connect = True

        thigh = eb.new(f"thigh.{side}")
        thigh.head = (cx + sx * hip_span, cy, pelvis_z)
        thigh.tail = (cx + sx * hip_span, cy, knee_z)
        thigh.parent = pelvis

        shin = eb.new(f"shin.{side}")
        shin.head = thigh.tail
        shin.tail = (cx + sx * hip_span, cy, ankle_z)
        shin.parent = thigh
        shin.use_connect = True

        foot = eb.new(f"foot.{side}")
        foot.head = shin.tail
        foot.tail = (cx + sx * (hip_span + foot_len), cy - h * 0.02, ankle_z - h * 0.01)
        foot.parent = shin
        foot.use_connect = True

    bpy.ops.object.mode_set(mode="OBJECT")
    arm_obj.select_set(False)
    return arm_obj


def bind_mesh_to_rig(mesh_obj: bpy.types.Object, arm_obj: bpy.types.Object) -> None:
    # Deterministic binding: armature modifier + procedural weights.
    # This avoids Bone Heat failures on non-manifold anime meshes.
    for vg in list(mesh_obj.vertex_groups):
        mesh_obj.vertex_groups.remove(vg)

    deform_bones = [b for b in arm_obj.data.bones if b.use_deform and b.name != "root"]
    groups = {b.name: mesh_obj.vertex_groups.new(name=b.name) for b in deform_bones}

    inv_arm = arm_obj.matrix_world.inverted()
    bone_segments = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in deform_bones]

    for v in mesh_obj.data.vertices:
        p = inv_arm @ (mesh_obj.matrix_world @ v.co)
        dists: list[tuple[float, str]] = []
        for bn, h, t in bone_segments:
            d = point_segment_distance(p, h, t)
            dists.append((d, bn))
        dists.sort(key=lambda it: it[0])
        chosen = dists[:4]
        raw = []
        for d, bn in chosen:
            raw.append((bn, 1.0 / ((d + 1e-4) ** 2)))
        s = sum(w for _, w in raw) or 1.0
        for bn, w in raw:
            groups[bn].add([v.index], w / s, "REPLACE")

    for mod in list(mesh_obj.modifiers):
        if mod.type == "ARMATURE":
            mesh_obj.modifiers.remove(mod)
    arm_mod = mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    arm_mod.object = arm_obj
    if hasattr(arm_mod, "use_deform_preserve_volume"):
        arm_mod.use_deform_preserve_volume = True

    mesh_obj.parent = arm_obj


def point_segment_distance(p: Vector, a: Vector, b: Vector) -> float:
    ab = b - a
    l2 = ab.length_squared
    if l2 < 1e-12:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
    q = a + ab * t
    return (p - q).length


def ensure_kirito_weapon() -> list[bpy.types.Object]:
    objs = [bpy.data.objects.get(n) for n in ("K_Elucidator_Blade", "K_Elucidator_Guard", "K_Elucidator_Grip", "K_Elucidator_Pommel")]
    if all(objs):
        return [o for o in objs if o is not None]

    created = []
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.10, -0.18, 0.96))
    blade = bpy.context.view_layer.objects.active
    blade.name = "K_Elucidator_Blade"
    blade.scale = (0.016, 0.005, 0.44)
    created.append(blade)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.10, -0.18, 0.55))
    guard = bpy.context.view_layer.objects.active
    guard.name = "K_Elucidator_Guard"
    guard.scale = (0.070, 0.018, 0.012)
    created.append(guard)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=0.16, location=(0.10, -0.18, 0.45))
    grip = bpy.context.view_layer.objects.active
    grip.name = "K_Elucidator_Grip"
    created.append(grip)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.014, location=(0.10, -0.18, 0.36))
    pommel = bpy.context.view_layer.objects.active
    pommel.name = "K_Elucidator_Pommel"
    created.append(pommel)

    for obj in created:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    return created


def parent_weapon_to_bone(weapon_objs: list[bpy.types.Object], arm_obj: bpy.types.Object, bone_name: str) -> None:
    for obj in weapon_objs:
        if obj is None:
            continue
        mw = obj.matrix_world.copy()
        obj.parent = arm_obj
        obj.parent_type = "BONE"
        obj.parent_bone = bone_name
        obj.matrix_world = mw


def add_simple_action(arm_obj: bpy.types.Object, name: str) -> None:
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 36
    scene.render.fps = 24

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")
    pb = arm_obj.pose.bones
    for b in pb:
        b.rotation_mode = "XYZ"

    def key_pose(frame: int, edits: dict[str, tuple[float, float, float]]) -> None:
        scene.frame_set(frame)
        for bone in pb:
            bone.location = (0.0, 0.0, 0.0)
            bone.rotation_euler = (0.0, 0.0, 0.0)
        for bone_name, (rx, ry, rz) in edits.items():
            b = pb.get(bone_name)
            if b is None:
                continue
            b.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        for bone in pb:
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    if "Kirito" in name:
        key_pose(1, {"upper_arm.R": (-12, 0, -18), "forearm.R": (-20, 0, -20), "upper_arm.L": (-8, 0, 10)})
        key_pose(18, {"upper_arm.R": (-48, 5, -60), "forearm.R": (-35, 5, -30), "upper_arm.L": (-12, 0, 20), "spine": (0, 0, 10)})
        key_pose(36, {"upper_arm.R": (-12, 0, -18), "forearm.R": (-20, 0, -20), "upper_arm.L": (-8, 0, 10)})
    else:
        key_pose(1, {"upper_arm.R": (-10, 0, 24), "forearm.R": (-18, 0, 22), "upper_arm.L": (8, 0, -12)})
        key_pose(18, {"upper_arm.R": (-42, 0, 50), "forearm.R": (-30, 0, 28), "upper_arm.L": (16, 0, -22), "spine": (0, 0, -8)})
        key_pose(36, {"upper_arm.R": (-10, 0, 24), "forearm.R": (-18, 0, 22), "upper_arm.L": (8, 0, -12)})

    bpy.ops.object.mode_set(mode="OBJECT")


def setup_camera_render_preview() -> None:
    scene = bpy.context.scene
    cam = bpy.data.objects.get("MainCamera")
    if cam is None:
        bpy.ops.object.camera_add(location=(0.5, -5.0, 1.4))
        cam = bpy.context.view_layer.objects.active
        cam.name = "MainCamera"

    cam.location = (0.5, -5.3, 1.45)
    cam.rotation_euler = (math.radians(83.0), 0.0, 0.0)
    cam.data.lens = 62
    scene.camera = cam

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.88, 0.90, 0.95, 1.0)
        bg.inputs[1].default_value = 1.0

    scene.frame_set(18)
    scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    scene.frame_set(1)
    scene.render.filepath = str(OUT_PREVIEW_NEUTRAL)
    bpy.ops.render.render(write_still=True)


def run() -> None:
    scene = bpy.context.scene
    scene.frame_set(1)

    rig_col = ensure_collection("Rigged")

    kirito_mesh = join_character_mesh(
        "K_",
        "K_Torso",
        "K_ArmL",
        "K_ArmR",
        "K_LegL",
        "K_LegR",
        "CHR_Kirito_Mesh",
    )
    asuna_mesh = join_character_mesh(
        "A_",
        "A_Torso",
        "A_ArmL",
        "A_ArmR",
        "A_LegL",
        "A_LegR",
        "CHR_Asuna_Mesh",
    )
    move_to_collection(kirito_mesh, rig_col)
    move_to_collection(asuna_mesh, rig_col)

    kirito_rig = create_basic_humanoid_rig("CHR_Kirito_Rig", kirito_mesh)
    asuna_rig = create_basic_humanoid_rig("CHR_Asuna_Rig", asuna_mesh)
    move_to_collection(kirito_rig, rig_col)
    move_to_collection(asuna_rig, rig_col)

    bind_mesh_to_rig(kirito_mesh, kirito_rig)
    bind_mesh_to_rig(asuna_mesh, asuna_rig)

    # Weapons -> hand.R bones
    k_weapons = ensure_kirito_weapon()
    a_weapons = [bpy.data.objects.get(n) for n in ("LL_Blade", "LL_Guard", "LL_Grip", "LL_Pommel") if bpy.data.objects.get(n) is not None]
    parent_weapon_to_bone(k_weapons, kirito_rig, "hand.R")
    parent_weapon_to_bone(a_weapons, asuna_rig, "hand.R")
    for w in k_weapons + a_weapons:
        if w is not None:
            move_to_collection(w, rig_col)

    add_simple_action(kirito_rig, "KiritoAttack")
    add_simple_action(asuna_rig, "AsunaThrust")

    setup_camera_render_preview()

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    print(f"Saved rigged blend: {OUT_BLEND}")
    print(f"Saved preview: {OUT_PREVIEW}")
    print(f"Saved preview f1: {OUT_PREVIEW_NEUTRAL}")
    print(f"Objects: {len(bpy.data.objects)}")
    print("Rigged meshes: CHR_Kirito_Mesh, CHR_Asuna_Mesh")
    print("Armatures: CHR_Kirito_Rig, CHR_Asuna_Rig")


if __name__ == "__main__":
    run()
