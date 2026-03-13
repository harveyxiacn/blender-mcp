"""
Sachi (幸) high-detail toon character build script for Blender MCP.
Run after AAA_v2_kirito.py and AAA_v2_asuna.py in the same scene.
"""

import math

import bmesh
import bpy


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col:
        return col
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def toon_mat(name, rgb, shadow=(0.55, 0.5, 0.6), rp=0.42, rim=0.25):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (980, 0)

    diff = nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (*rgb, 1.0)
    diff.location = (-380, 120)

    s2r = nodes.new("ShaderNodeShaderToRGB")
    s2r.location = (-170, 120)
    links.new(diff.outputs["BSDF"], s2r.inputs["Shader"])

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (60, 120)
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (
        rgb[0] * shadow[0],
        rgb[1] * shadow[1],
        rgb[2] * shadow[2],
        1.0,
    )
    ramp.color_ramp.elements[1].color = (*rgb, 1.0)
    ramp.color_ramp.elements[1].position = rp
    links.new(s2r.outputs["Color"], ramp.inputs["Fac"])

    fres = nodes.new("ShaderNodeFresnel")
    fres.inputs["IOR"].default_value = 1.45
    fres.location = (-170, -170)

    rr = nodes.new("ShaderNodeValToRGB")
    rr.location = (60, -170)
    rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    rr.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    rr.color_ramp.elements[1].position = 0.78
    links.new(fres.outputs["Fac"], rr.inputs["Fac"])

    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "ADD"
    mix.inputs["Fac"].default_value = rim
    mix.location = (300, 0)
    links.new(ramp.outputs["Color"], mix.inputs[1])
    links.new(rr.outputs["Color"], mix.inputs[2])

    em = nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    em.location = (560, 0)
    links.new(mix.outputs["Color"], em.inputs["Color"])
    links.new(em.outputs["Emission"], out.inputs["Surface"])

    return mat


def ensure_materials() -> None:
    toon_mat("M_Skin", (0.94, 0.80, 0.70), rim=0.2)
    toon_mat("M_EyeWhite", (0.95, 0.95, 0.95), rim=0.05)
    toon_mat("M_EyeBlack", (0.015, 0.015, 0.02), rim=0.0)
    toon_mat("M_SachiBlue", (0.18, 0.24, 0.50), rim=0.24)
    toon_mat("M_SachiLightBlue", (0.66, 0.81, 0.95), rim=0.16)
    toon_mat("M_SachiHair", (0.08, 0.10, 0.24), rim=0.34)
    toon_mat("M_SachiEye", (0.33, 0.62, 0.76), rim=0.12)
    toon_mat("M_SachiBoot", (0.10, 0.11, 0.13), rim=0.08)

    if "M_EyeHighlight" not in bpy.data.materials:
        hl = bpy.data.materials.new("M_EyeHighlight")
        hl.use_nodes = True
        nodes = hl.node_tree.nodes
        links = hl.node_tree.links
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        out.location = (300, 0)
        em = nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        em.inputs["Strength"].default_value = 3.0
        em.location = (120, 0)
        links.new(em.outputs["Emission"], out.inputs["Surface"])


def loft(name, profiles, ns=16, cap_top=False, cap_bot=False):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []

    for z, rx, ry, ox, oy in profiles:
        ring = []
        for i in range(ns):
            a = 2.0 * math.pi * i / ns
            x = ox + rx * math.cos(a)
            y = oy + ry * math.sin(a)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)

    for r in range(len(rings) - 1):
        for i in range(ns):
            v1 = rings[r][i]
            v2 = rings[r][(i + 1) % ns]
            v3 = rings[r + 1][(i + 1) % ns]
            v4 = rings[r + 1][i]
            bm.faces.new([v1, v4, v3, v2])

    if cap_bot and rings:
        bm.faces.new(rings[0])
    if cap_top and rings:
        bm.faces.new(list(reversed(rings[-1])))

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def setup(obj, mat_name, col_name="Characters", ss=2, outline=0.003) -> None:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    col = ensure_collection(col_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

    if ss > 0:
        mod = obj.modifiers.new("SS", "SUBSURF")
        mod.levels = ss
        mod.render_levels = ss

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)

    outline_mat = bpy.data.materials.get("M_Outline")
    if outline > 0 and outline_mat:
        om = obj.modifiers.new("Outline", "SOLIDIFY")
        om.thickness = outline
        om.offset = -1
        om.use_flip_normals = True
        om.material_offset = len(obj.data.materials)
        obj.data.materials.append(outline_mat)


def hair_strip(name, loc, rot_deg, length, base_w, tip_w, mat="M_SachiHair", thickness=0.008, ns=6):
    profiles = [
        (0.0, base_w, thickness, 0.0, 0.0),
        (length * 0.3, base_w * 0.86, thickness * 0.9, 0.0, 0.0),
        (length * 0.6, base_w * 0.60, thickness * 0.7, 0.0, 0.0),
        (length * 0.85, base_w * 0.30, thickness * 0.4, 0.0, 0.0),
        (length, tip_w * 0.25, thickness * 0.1, 0.0, 0.0),
    ]
    h = loft(name, profiles, ns=ns, cap_top=True, cap_bot=True)
    h.location = loc
    h.rotation_euler = tuple(math.radians(v) for v in rot_deg)
    setup(h, mat, ss=1, outline=0.0025)
    return h


# --- Build ---
for c in ("Characters", "Weapons", "Environment", "Lighting"):
    ensure_collection(c)
ensure_materials()

sx = 2.8
print("\n[Sachi] Building...")

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=28, ring_count=18, radius=0.108, location=(sx, 0, 1.54)
)
head = bpy.context.active_object
head.name = "SA_Head"
head.scale = (1.0, 0.90, 1.08)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < -0.02:
        f = max(0.0, (-0.02 - v.co.z) / 0.09)
        v.co.x *= 1.0 - f * 0.45
        v.co.y *= 1.0 - f * 0.35
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(head, "M_Skin", ss=2, outline=0.0035)

for side, sgn in (("L", 1), ("R", -1)):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=14, ring_count=10, radius=0.028, location=(sx + sgn * 0.036, -0.086, 1.545)
    )
    ew = bpy.context.active_object
    ew.name = f"SA_EyeW{side}"
    ew.scale = (1.0, 0.52, 1.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(ew, "M_EyeWhite", ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=0.020, location=(sx + sgn * 0.036, -0.100, 1.542)
    )
    iris = bpy.context.active_object
    iris.name = f"SA_Iris{side}"
    iris.scale = (1.0, 0.55, 1.25)
    bpy.ops.object.transform_apply(scale=True)
    setup(iris, "M_SachiEye", ss=1, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6, radius=0.008, location=(sx + sgn * 0.036, -0.112, 1.541)
    )
    pupil = bpy.context.active_object
    pupil.name = f"SA_Pupil{side}"
    pupil.scale = (1.0, 0.6, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    setup(pupil, "M_EyeBlack", ss=0, outline=0)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6, radius=0.007, location=(sx + sgn * 0.045, -0.116, 1.557)
    )
    hl = bpy.context.active_object
    hl.name = f"SA_HL{side}"
    setup(hl, "M_EyeHighlight", ss=0, outline=0)

for side, sgn in (("L", 1), ("R", -1)):
    bpy.ops.mesh.primitive_cube_add(size=0.008, location=(sx + sgn * 0.036, -0.099, 1.575))
    brow = bpy.context.active_object
    brow.name = f"SA_Brow{side}"
    brow.scale = (2.8, 0.3, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    setup(brow, "M_SachiHair", ss=1, outline=0)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8, ring_count=6, radius=0.006, location=(sx, -0.108, 1.514)
)
nose = bpy.context.active_object
nose.name = "SA_Nose"
nose.scale = (0.5, 0.5, 0.8)
bpy.ops.object.transform_apply(scale=True)
setup(nose, "M_Skin", ss=1, outline=0)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=20, ring_count=14, radius=0.120, location=(sx, 0.008, 1.59)
)
hb = bpy.context.active_object
hb.name = "SA_HairBase"
hb.scale = (1.04, 0.98, 1.02)
bpy.ops.object.transform_apply(scale=True)
setup(hb, "M_SachiHair", ss=1, outline=0.003)

for i, (dx, dy, dz, rot, ln, bw) in enumerate(
    [
        (-0.045, -0.102, 1.64, (82, 0, 12), 0.09, 0.026),
        (-0.012, -0.108, 1.64, (84, 0, 3), 0.10, 0.025),
        (0.018, -0.108, 1.64, (84, 0, -4), 0.10, 0.024),
        (0.050, -0.100, 1.63, (80, 0, -12), 0.09, 0.026),
    ]
):
    hair_strip(f"SA_Bang{i}", (sx + dx, dy, dz), rot, ln, bw, 0.004)

for side, sgn in (("L", 1), ("R", -1)):
    for j, z in enumerate((1.60, 1.55, 1.50)):
        hair_strip(
            f"SA_Side{side}{j}",
            (sx + sgn * 0.090, -0.01, z),
            (88, sgn * 12, sgn * (26 + j * 4)),
            0.16 - j * 0.02,
            0.020 - j * 0.002,
            0.003,
        )

back = loft(
    "SA_BackHair",
    [
        (1.60, 0.11, 0.040, sx, 0.070),
        (1.52, 0.12, 0.045, sx, 0.075),
        (1.44, 0.115, 0.040, sx, 0.070),
        (1.38, 0.10, 0.035, sx, 0.060),
    ],
    ns=14,
    cap_bot=True,
)
setup(back, "M_SachiHair", ss=1, outline=0.003)

torso = loft(
    "SA_Torso",
    [
        (0.72, 0.12, 0.082, sx, 0),
        (0.80, 0.126, 0.086, sx, 0),
        (0.90, 0.132, 0.090, sx, 0),
        (1.00, 0.137, 0.093, sx, 0),
        (1.10, 0.140, 0.095, sx, 0),
        (1.18, 0.132, 0.090, sx, 0),
        (1.28, 0.085, 0.064, sx, 0),
        (1.34, 0.045, 0.042, sx, 0),
    ],
    ns=18,
)
setup(torso, "M_Skin", ss=2, outline=0.0025)

vest = loft(
    "SA_Vest",
    [
        (0.80, 0.126, 0.058, sx, -0.045),
        (0.92, 0.132, 0.062, sx, -0.050),
        (1.05, 0.137, 0.064, sx, -0.052),
        (1.16, 0.130, 0.060, sx, -0.048),
    ],
    ns=18,
)
setup(vest, "M_SachiBlue", ss=1, outline=0.003)

vest_trim = loft(
    "SA_VestTrim",
    [
        (0.84, 0.133, 0.064, sx, -0.050),
        (0.98, 0.140, 0.068, sx, -0.054),
        (1.10, 0.134, 0.064, sx, -0.050),
    ],
    ns=18,
)
setup(vest_trim, "M_SachiLightBlue", ss=0, outline=0)

for side, sgn in (("L", 1), ("R", -1)):
    arm = loft(
        f"SA_Arm{side}",
        [
            (1.26, 0.037, 0.034, sx + sgn * 0.14, 0),
            (1.18, 0.032, 0.030, sx + sgn * 0.18, 0),
            (1.08, 0.028, 0.026, sx + sgn * 0.21, 0),
            (0.98, 0.025, 0.023, sx + sgn * 0.23, 0),
            (0.90, 0.023, 0.021, sx + sgn * 0.24, 0),
        ],
        ns=12,
    )
    setup(arm, "M_FabricWhite", ss=1, outline=0.002)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10, ring_count=8, radius=0.021, location=(sx + sgn * 0.24, 0.0, 0.86)
    )
    hand = bpy.context.active_object
    hand.name = f"SA_Hand{side}"
    hand.scale = (0.86, 0.5, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    setup(hand, "M_Skin", ss=1, outline=0)

for side, sgn in (("L", 1), ("R", -1)):
    leg = loft(
        f"SA_Leg{side}",
        [
            (0.72, 0.052, 0.046, sx + sgn * 0.055, 0),
            (0.62, 0.048, 0.043, sx + sgn * 0.058, 0),
            (0.50, 0.042, 0.037, sx + sgn * 0.060, 0),
            (0.38, 0.036, 0.032, sx + sgn * 0.060, 0),
            (0.26, 0.031, 0.028, sx + sgn * 0.060, 0),
            (0.15, 0.028, 0.025, sx + sgn * 0.060, 0),
        ],
        ns=12,
    )
    setup(leg, "M_Skin", ss=1, outline=0.002)

    boot = loft(
        f"SA_Boot{side}",
        [
            (0.32, 0.040, 0.034, sx + sgn * 0.060, 0),
            (0.24, 0.042, 0.036, sx + sgn * 0.060, 0),
            (0.16, 0.044, 0.040, sx + sgn * 0.060, -0.002),
            (0.08, 0.046, 0.050, sx + sgn * 0.060, -0.010),
            (0.03, 0.043, 0.052, sx + sgn * 0.060, -0.014),
        ],
        ns=12,
        cap_bot=True,
    )
    setup(boot, "M_SachiBoot", ss=1, outline=0.0025)

skirt = loft(
    "SA_Skirt",
    [
        (0.80, 0.11, 0.080, sx, 0),
        (0.74, 0.13, 0.095, sx, 0),
        (0.68, 0.15, 0.110, sx, 0),
        (0.62, 0.17, 0.125, sx, 0),
        (0.58, 0.18, 0.135, sx, 0),
    ],
    ns=18,
)
setup(skirt, "M_SachiLightBlue", ss=1, outline=0.0025)

shorts = loft(
    "SA_Shorts",
    [
        (0.74, 0.10, 0.070, sx, 0),
        (0.68, 0.11, 0.075, sx, 0),
        (0.62, 0.11, 0.075, sx, 0),
    ],
    ns=16,
)
setup(shorts, "M_SachiBlue", ss=1, outline=0.0015)

belt = loft(
    "SA_Belt",
    [
        (0.79, 0.12, 0.082, sx, 0),
        (0.81, 0.123, 0.084, sx, 0),
        (0.83, 0.120, 0.082, sx, 0),
    ],
    ns=16,
)
setup(belt, "M_EyeBlack", ss=1, outline=0)

print("✓ Sachi complete")
