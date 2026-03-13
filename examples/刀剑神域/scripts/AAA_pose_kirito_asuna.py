"""
Add weapons, battle poses, and keyframed actions for Kirito + Asuna.

Prerequisite:
1. Run AAA_v2_kirito.py
2. Run AAA_v2_asuna.py
"""

import math

import bpy
from mathutils import Euler, Vector

OUTPUT_BLEND = r"E:\Projects\blender-mcp\examples\sao_kirito_asuna_action.blend"
OUTPUT_STILL = r"E:\Projects\blender-mcp\examples\sao_kirito_asuna_action_f24.png"


def require_object(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required object missing: {name}")
    return obj


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


def assign_material(obj: bpy.types.Object, mat_name: str) -> None:
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def apply_transform(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def ensure_kirito_weapon(parts_col: bpy.types.Collection) -> list[str]:
    part_names = [
        "K_Elucidator_Blade",
        "K_Elucidator_Guard",
        "K_Elucidator_Grip",
        "K_Elucidator_Pommel",
    ]
    if all(bpy.data.objects.get(n) for n in part_names):
        return part_names

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.46))
    blade = bpy.context.active_object
    blade.name = "K_Elucidator_Blade"
    blade.scale = (0.014, 0.004, 0.42)
    apply_transform(blade)
    assign_material(blade, "M_Elucidator")
    move_to_collection(blade, parts_col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.07))
    guard = bpy.context.active_object
    guard.name = "K_Elucidator_Guard"
    guard.scale = (0.060, 0.015, 0.010)
    apply_transform(guard)
    assign_material(guard, "M_MetalDark")
    move_to_collection(guard, parts_col)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.010, depth=0.16, location=(0.0, 0.0, -0.02))
    grip = bpy.context.active_object
    grip.name = "K_Elucidator_Grip"
    assign_material(grip, "M_KiritoBelt")
    move_to_collection(grip, parts_col)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.013, location=(0.0, 0.0, -0.12)
    )
    pommel = bpy.context.active_object
    pommel.name = "K_Elucidator_Pommel"
    assign_material(pommel, "M_MetalDark")
    move_to_collection(pommel, parts_col)

    return part_names


def attach_weapon_to_hand(
    root_name: str,
    hand_name: str,
    part_names: list[str],
    root_local_loc: tuple[float, float, float],
    root_local_rot_deg: tuple[float, float, float],
    parts_col: bpy.types.Collection,
) -> bpy.types.Object:
    hand = require_object(hand_name)
    root = bpy.data.objects.get(root_name)
    if root is None:
        root = bpy.data.objects.new(root_name, None)
        root.empty_display_type = "PLAIN_AXES"
        bpy.context.scene.collection.objects.link(root)
    move_to_collection(root, parts_col)

    root.parent = hand
    root.matrix_parent_inverse = hand.matrix_world.inverted()
    root.location = root_local_loc
    root.rotation_euler = tuple(math.radians(v) for v in root_local_rot_deg)

    for name in part_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
        if "Blade" in name:
            obj.location = (0.0, 0.0, 0.50)
            obj.rotation_euler = (0.0, 0.0, 0.0)
        elif "Guard" in name:
            obj.location = (0.0, 0.0, 0.08)
            obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        elif "Grip" in name:
            obj.location = (0.0, 0.0, -0.02)
            obj.rotation_euler = (0.0, 0.0, 0.0)
        elif "Pommel" in name:
            obj.location = (0.0, 0.0, -0.12)
            obj.rotation_euler = (0.0, 0.0, 0.0)
        move_to_collection(obj, parts_col)

    return root


def collect_targets(names: list[str]) -> dict[str, bpy.types.Object]:
    targets: dict[str, bpy.types.Object] = {}
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            targets[name] = obj
    return targets


def base_transforms(targets: dict[str, bpy.types.Object]) -> dict[str, tuple[Vector, Euler]]:
    data: dict[str, tuple[Vector, Euler]] = {}
    for name, obj in targets.items():
        data[name] = (obj.location.copy(), obj.rotation_euler.copy())
    return data


def apply_pose(
    frame: int,
    targets: dict[str, bpy.types.Object],
    base: dict[str, tuple[Vector, Euler]],
    deltas: dict[str, dict[str, tuple[float, float, float]]],
) -> None:
    bpy.context.scene.frame_set(frame)
    for name, obj in targets.items():
        base_loc, base_rot = base[name]
        obj.location = base_loc.copy()
        obj.rotation_euler = base_rot.copy()

        delta = deltas.get(name)
        if delta is not None:
            loc_delta = delta.get("loc")
            if loc_delta is not None:
                obj.location = base_loc + Vector(loc_delta)
            rot_delta = delta.get("rot")
            if rot_delta is not None:
                obj.rotation_euler = (
                    base_rot.x + math.radians(rot_delta[0]),
                    base_rot.y + math.radians(rot_delta[1]),
                    base_rot.z + math.radians(rot_delta[2]),
                )

        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def smooth_animation(targets: dict[str, bpy.types.Object]) -> None:
    for obj in targets.values():
        ad = obj.animation_data
        if ad is None or ad.action is None:
            continue
        action = ad.action
        if not hasattr(action, "fcurves"):
            # Blender 5+ may store animation channels in layered actions.
            continue
        for fc in action.fcurves:
            for key in fc.keyframe_points:
                key.interpolation = "BEZIER"
                key.handle_left_type = "AUTO_CLAMPED"
                key.handle_right_type = "AUTO_CLAMPED"


def main() -> None:
    required = [
        "K_Torso",
        "K_ArmL",
        "K_ArmR",
        "K_HandL",
        "K_HandR",
        "K_LegL",
        "K_LegR",
        "K_BootL",
        "K_BootR",
        "A_Torso",
        "A_ArmL",
        "A_ArmR",
        "A_HandL",
        "A_HandR",
        "A_LegL",
        "A_LegR",
        "A_BootL",
        "A_BootR",
    ]
    for obj_name in required:
        require_object(obj_name)

    parts_col = ensure_collection("Weapons")

    k_parts = ensure_kirito_weapon(parts_col)
    k_root = attach_weapon_to_hand(
        root_name="K_WeaponRoot",
        hand_name="K_HandR",
        part_names=k_parts,
        root_local_loc=(0.0, 0.0, -0.03),
        root_local_rot_deg=(95.0, 5.0, -8.0),
        parts_col=parts_col,
    )

    a_parts = [
        n
        for n in ["LL_Blade", "LL_Guard", "LL_Grip", "LL_Pommel"]
        if bpy.data.objects.get(n) is not None
    ]
    if not a_parts:
        raise RuntimeError(
            "Asuna weapon parts not found (LL_Blade / LL_Guard / LL_Grip / LL_Pommel)"
        )
    a_root = attach_weapon_to_hand(
        root_name="A_WeaponRoot",
        hand_name="A_HandR",
        part_names=a_parts,
        root_local_loc=(0.0, 0.0, -0.02),
        root_local_rot_deg=(80.0, -2.0, 10.0),
        parts_col=parts_col,
    )

    targets = collect_targets(
        [
            "K_Torso",
            "K_ArmL",
            "K_ArmR",
            "K_HandL",
            "K_HandR",
            "K_LegL",
            "K_LegR",
            "K_BootL",
            "K_BootR",
            "A_Torso",
            "A_ArmL",
            "A_ArmR",
            "A_HandL",
            "A_HandR",
            "A_LegL",
            "A_LegR",
            "A_BootL",
            "A_BootR",
            "A_LongHair",
            "A_SkirtOuter",
            "A_SkirtInner",
            k_root.name,
            a_root.name,
        ]
    )
    base = base_transforms(targets)

    pose_1 = {
        "K_Torso": {"rot": (0.0, 0.0, 10.0)},
        "K_ArmR": {"rot": (-35.0, 0.0, -42.0)},
        "K_HandR": {"rot": (-20.0, 15.0, -8.0)},
        "K_ArmL": {"rot": (-18.0, 0.0, 30.0)},
        "K_HandL": {"rot": (0.0, 0.0, 15.0)},
        "K_LegL": {"rot": (6.0, 0.0, 6.0)},
        "K_LegR": {"rot": (-4.0, 0.0, -6.0)},
        "K_BootL": {"rot": (-3.0, 0.0, 2.0)},
        "K_BootR": {"rot": (2.0, 0.0, -2.0)},
        "K_WeaponRoot": {"rot": (80.0, 0.0, 6.0)},
        "A_Torso": {"rot": (0.0, 0.0, -10.0)},
        "A_ArmR": {"rot": (-25.0, 0.0, 28.0)},
        "A_HandR": {"rot": (-12.0, 0.0, 10.0)},
        "A_ArmL": {"rot": (-12.0, 0.0, -30.0)},
        "A_HandL": {"rot": (5.0, 0.0, -10.0)},
        "A_LegR": {"rot": (5.0, 0.0, -5.0)},
        "A_LegL": {"rot": (-3.0, 0.0, 7.0)},
        "A_BootR": {"rot": (-2.0, 0.0, -3.0)},
        "A_BootL": {"rot": (2.0, 0.0, 3.0)},
        "A_WeaponRoot": {"rot": (72.0, 0.0, -10.0)},
    }

    pose_2 = {
        "K_Torso": {"loc": (-0.02, 0.03, 0.0), "rot": (0.0, 0.0, 18.0)},
        "K_ArmR": {"rot": (-70.0, 10.0, -80.0)},
        "K_HandR": {"rot": (-30.0, 25.0, -25.0)},
        "K_ArmL": {"rot": (-25.0, -5.0, 18.0)},
        "K_LegL": {"rot": (12.0, 0.0, 4.0)},
        "K_LegR": {"rot": (-8.0, 0.0, -10.0)},
        "K_WeaponRoot": {"rot": (120.0, 0.0, -18.0)},
        "A_Torso": {"loc": (0.01, 0.02, 0.0), "rot": (0.0, 0.0, -5.0)},
        "A_ArmR": {"rot": (-45.0, 0.0, 14.0)},
        "A_HandR": {"rot": (-18.0, 0.0, 20.0)},
        "A_ArmL": {"rot": (-6.0, 0.0, -38.0)},
        "A_LegR": {"rot": (10.0, 0.0, -4.0)},
        "A_LegL": {"rot": (-4.0, 0.0, 8.0)},
        "A_WeaponRoot": {"rot": (86.0, 0.0, 8.0)},
    }

    pose_3 = {
        "K_Torso": {"loc": (0.03, 0.08, 0.0), "rot": (0.0, 0.0, -4.0)},
        "K_ArmR": {"rot": (-18.0, -5.0, 35.0)},
        "K_HandR": {"rot": (18.0, -5.0, 20.0)},
        "K_ArmL": {"rot": (-10.0, 0.0, 50.0)},
        "K_LegL": {"rot": (-4.0, 0.0, 12.0)},
        "K_LegR": {"rot": (14.0, 0.0, -12.0)},
        "K_WeaponRoot": {"rot": (48.0, 0.0, 35.0)},
        "A_Torso": {"loc": (-0.02, 0.07, 0.0), "rot": (0.0, 0.0, -14.0)},
        "A_ArmR": {"rot": (-8.0, 0.0, 58.0)},
        "A_HandR": {"rot": (20.0, 0.0, 28.0)},
        "A_ArmL": {"rot": (-16.0, 0.0, -20.0)},
        "A_LegR": {"rot": (-2.0, 0.0, -12.0)},
        "A_LegL": {"rot": (12.0, 0.0, 10.0)},
        "A_WeaponRoot": {"rot": (96.0, 0.0, 26.0)},
        "A_LongHair": {"rot": (6.0, 0.0, 0.0)},
        "A_SkirtOuter": {"rot": (-4.0, 0.0, 0.0)},
        "A_SkirtInner": {"rot": (-4.0, 0.0, 0.0)},
    }

    pose_4 = {
        "K_Torso": {"loc": (0.01, 0.02, 0.0), "rot": (0.0, 0.0, 8.0)},
        "K_ArmR": {"rot": (-28.0, 0.0, -20.0)},
        "K_HandR": {"rot": (-8.0, 5.0, -3.0)},
        "K_ArmL": {"rot": (-14.0, 0.0, 26.0)},
        "K_LegL": {"rot": (3.0, 0.0, 4.0)},
        "K_LegR": {"rot": (-2.0, 0.0, -4.0)},
        "K_WeaponRoot": {"rot": (76.0, 0.0, 4.0)},
        "A_Torso": {"loc": (0.0, 0.02, 0.0), "rot": (0.0, 0.0, -8.0)},
        "A_ArmR": {"rot": (-20.0, 0.0, 24.0)},
        "A_HandR": {"rot": (-8.0, 0.0, 8.0)},
        "A_ArmL": {"rot": (-9.0, 0.0, -28.0)},
        "A_LegR": {"rot": (4.0, 0.0, -4.0)},
        "A_LegL": {"rot": (-2.0, 0.0, 5.0)},
        "A_WeaponRoot": {"rot": (70.0, 0.0, -6.0)},
    }

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 48
    scene.render.fps = 24

    apply_pose(1, targets, base, pose_1)
    apply_pose(12, targets, base, pose_2)
    apply_pose(24, targets, base, pose_3)
    apply_pose(36, targets, base, pose_4)
    apply_pose(48, targets, base, pose_1)
    smooth_animation(targets)

    cam = bpy.data.objects.get("MainCamera")
    if cam is not None:
        cam.location = Vector((0.52, -4.20, 1.22))
        cam.rotation_euler = (math.radians(84.0), 0.0, math.radians(2.0))
        cam.keyframe_insert(data_path="location", frame=1)
        cam.keyframe_insert(data_path="rotation_euler", frame=1)

        cam.location = Vector((0.55, -3.95, 1.24))
        cam.rotation_euler = (math.radians(83.0), 0.0, math.radians(4.0))
        cam.keyframe_insert(data_path="location", frame=24)
        cam.keyframe_insert(data_path="rotation_euler", frame=24)

        cam.location = Vector((0.52, -4.20, 1.22))
        cam.rotation_euler = (math.radians(84.0), 0.0, math.radians(2.0))
        cam.keyframe_insert(data_path="location", frame=48)
        cam.keyframe_insert(data_path="rotation_euler", frame=48)

    scene.frame_set(24)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = OUTPUT_STILL
    bpy.ops.render.render(write_still=True)

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print(f"Saved blend: {OUTPUT_BLEND}")
    print(f"Saved still: {OUTPUT_STILL}")
    print(f"Total objects: {len(bpy.data.objects)}")


if __name__ == "__main__":
    main()
