#!/usr/bin/env python
"""
刀剑神域 (Sword Art Online) 同人角色 Demo

基于 examples/刀剑神域/scripts/AAA_v2_*.py 的 toon 着色模式,
通过 MCP 连接在 Blender 中创建桐人(Kirito)、亚丝娜(Asuna)、克莱因(Klein) 的同人模型。

Usage:
    python tests/build_sao_demo.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from blender_mcp.connection import BlenderConnection

PASS = 0
FAIL = 0


async def send(conn, category, action, params=None):
    return await conn.send_command(category, action, params or {})


async def test(conn, name, category, action, params=None, check_success=True):
    global PASS, FAIL
    try:
        result = await send(conn, category, action, params)
        if check_success and not result.get("success"):
            FAIL += 1
            err = result.get("error", {})
            print(f"  FAIL {name}: {err.get('message', str(err))}")
            return result
        PASS += 1
        print(f"  PASS {name}")
        return result
    except Exception as e:
        FAIL += 1
        print(f"  ERROR {name}: {e}")
        return {"success": False}


async def run_py(conn, name, code):
    """Execute Python code in Blender via MCP.

    Uses the utility handler which captures stdout.
    Code should set 'result' variable and we append print(result) automatically.
    """
    # Append print(result) so the utility handler captures it as output
    full_code = code.rstrip() + "\nprint(result)"
    return await test(conn, name, "utility", "execute_python", {"code": full_code})


# ============================================================
# 材质系统 (Toon Material System)
# ============================================================

MATERIAL_SETUP_CODE = '''
import bpy, math

# ---------- toon_mat ----------
def toon_mat(name, rgb, shadow=(0.55, 0.50, 0.60), rp=0.42, rim=0.3, spec=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    N = mat.node_tree.nodes
    L = mat.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial"); out.location = (1200,0)
    diff = N.new("ShaderNodeBsdfDiffuse"); diff.inputs["Color"].default_value = (*rgb,1); diff.location = (-400,100)
    s2r = N.new("ShaderNodeShaderToRGB"); s2r.location = (-200,100)
    L.new(diff.outputs["BSDF"], s2r.inputs["Shader"])
    ramp = N.new("ShaderNodeValToRGB"); ramp.location = (0,100)
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (rgb[0]*shadow[0], rgb[1]*shadow[1], rgb[2]*shadow[2], 1)
    ramp.color_ramp.elements[1].color = (*rgb, 1)
    ramp.color_ramp.elements[1].position = rp
    L.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    fres = N.new("ShaderNodeFresnel"); fres.inputs["IOR"].default_value = 1.45; fres.location = (-200,-200)
    rr = N.new("ShaderNodeValToRGB"); rr.location = (0,-200)
    rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (0,0,0,1)
    rr.color_ramp.elements[1].color = (1,1,1,1)
    rr.color_ramp.elements[1].position = 0.75
    L.new(fres.outputs["Fac"], rr.inputs["Fac"])
    mix = N.new("ShaderNodeMixRGB"); mix.blend_type = "ADD"; mix.inputs["Fac"].default_value = rim; mix.location = (400,0)
    L.new(ramp.outputs["Color"], mix.inputs[1])
    L.new(rr.outputs["Color"], mix.inputs[2])
    fi = mix
    if spec:
        gl = N.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.3; gl.location = (-400,-400)
        sr2 = N.new("ShaderNodeShaderToRGB"); sr2.location = (-200,-400)
        L.new(gl.outputs["BSDF"], sr2.inputs["Shader"])
        sramp = N.new("ShaderNodeValToRGB"); sramp.location = (0,-400)
        sramp.color_ramp.interpolation = "CONSTANT"
        sramp.color_ramp.elements[0].color = (0,0,0,1)
        sramp.color_ramp.elements[1].color = (1,1,1,1)
        sramp.color_ramp.elements[1].position = 0.9
        L.new(sr2.outputs["Color"], sramp.inputs["Fac"])
        sa = N.new("ShaderNodeMixRGB"); sa.blend_type = "ADD"; sa.inputs["Fac"].default_value = 0.15; sa.location = (600,0)
        L.new(mix.outputs["Color"], sa.inputs[1])
        L.new(sramp.outputs["Color"], sa.inputs[2])
        fi = sa
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0; em.location = (900,0)
    L.new(fi.outputs["Color"], em.inputs["Color"])
    L.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat

def metal_mat(name, rgb):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    N = mat.node_tree.nodes; L = mat.node_tree.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); out.location = (800,0)
    gl = N.new("ShaderNodeBsdfGlossy"); gl.inputs["Color"].default_value = (*rgb,1); gl.inputs["Roughness"].default_value = 0.12; gl.location = (-300,0)
    s2r = N.new("ShaderNodeShaderToRGB"); s2r.location = (-100,0)
    L.new(gl.outputs["BSDF"], s2r.inputs["Shader"])
    ramp = N.new("ShaderNodeValToRGB"); ramp.location = (100,0)
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (rgb[0]*0.25, rgb[1]*0.25, rgb[2]*0.3, 1)
    ramp.color_ramp.elements[1].color = (*rgb, 1)
    ramp.color_ramp.elements[1].position = 0.35
    hl = ramp.color_ramp.elements.new(0.88)
    hl.color = (min(1,rgb[0]+0.35), min(1,rgb[1]+0.35), min(1,rgb[2]+0.35), 1)
    L.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0; em.location = (400,0)
    L.new(ramp.outputs["Color"], em.inputs["Color"])
    L.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat

# Outline material
om = bpy.data.materials.new("M_Outline")
om.use_nodes = True; om.use_backface_culling = True
ns = om.node_tree.nodes; ls = om.node_tree.links; ns.clear()
o = ns.new("ShaderNodeOutputMaterial"); o.location = (300,0)
e = ns.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.01,0.01,0.02,1); e.inputs["Strength"].default_value = 0; e.location = (100,0)
ls.new(e.outputs["Emission"], o.inputs["Surface"])

# Eye highlight material
eh = bpy.data.materials.new("M_EyeHighlight")
eh.use_nodes = True
ns = eh.node_tree.nodes; ls = eh.node_tree.links; ns.clear()
o = ns.new("ShaderNodeOutputMaterial"); o.location = (300,0)
e = ns.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1,1,1,1); e.inputs["Strength"].default_value = 3.0; e.location = (100,0)
ls.new(e.outputs["Emission"], o.inputs["Surface"])

# ---------- All SAO Character Materials ----------
# Shared
toon_mat("M_Skin", (0.94, 0.80, 0.70), rim=0.2)
toon_mat("M_EyeBlack", (0.015, 0.015, 0.02))
toon_mat("M_EyeWhite", (0.95, 0.95, 0.95))

# Kirito
toon_mat("M_KiritoBlack", (0.030, 0.030, 0.035), shadow=(0.5,0.5,0.5), rim=0.4)
toon_mat("M_KiritoHair", (0.025, 0.025, 0.04), shadow=(0.4,0.4,0.5), rim=0.5, spec=True)
toon_mat("M_KiritoBelt", (0.22, 0.12, 0.06), rim=0.15)
toon_mat("M_KiritoEye", (0.12, 0.12, 0.15), shadow=(0.4,0.4,0.4))
metal_mat("M_KiritoSilver", (0.78, 0.78, 0.80))
toon_mat("M_KiritoTrim", (0.70, 0.70, 0.72), shadow=(0.5,0.5,0.5), rim=0.2)

# Asuna
toon_mat("M_AsunaWhite", (0.95, 0.95, 0.93), rim=0.25, spec=True)
toon_mat("M_AsunaRed", (0.78, 0.18, 0.18), rim=0.3)
toon_mat("M_AsunaHair", (0.76, 0.44, 0.18), shadow=(0.5,0.45,0.5), rim=0.35, spec=True)
toon_mat("M_AsunaEye", (0.52, 0.38, 0.06))
metal_mat("M_AsunaGold", (0.82, 0.68, 0.20))

# Klein
toon_mat("M_KleinRed", (0.70, 0.24, 0.16), rim=0.3)
toon_mat("M_KleinHair", (0.70, 0.24, 0.16), shadow=(0.45,0.4,0.45), rim=0.4)
toon_mat("M_KleinCream", (0.90, 0.85, 0.76))
toon_mat("M_KleinBrown", (0.28, 0.18, 0.12))
toon_mat("M_SkinTan", (0.72, 0.52, 0.38), rim=0.2)

# Weapons
metal_mat("M_Elucidator", (0.025, 0.025, 0.03))
metal_mat("M_LambentLight", (0.90, 0.90, 0.93))

result = f"Created {len(bpy.data.materials)} materials"
'''

# ============================================================
# 工具函数 (Helper functions injected into Blender)
# ============================================================

HELPER_FUNCS_CODE = '''
import bpy, bmesh, math

def loft(name, profiles, ns=16, cap_top=False, cap_bot=False):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for z, rx, ry, ox, oy in profiles:
        ring = []
        for i in range(ns):
            a = 2*math.pi*i/ns
            x = ox + rx*math.cos(a)
            y = oy + ry*math.sin(a)
            ring.append(bm.verts.new((x,y,z)))
        rings.append(ring)
    for r in range(len(rings)-1):
        for i in range(ns):
            v1, v2 = rings[r][i], rings[r][(i+1)%ns]
            v3, v4 = rings[r+1][(i+1)%ns], rings[r+1][i]
            bm.faces.new([v1,v4,v3,v2])
    if cap_bot and rings:
        bm.faces.new(rings[0])
    if cap_top and rings:
        bm.faces.new(list(reversed(rings[-1])))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def setup(obj, mat_name, ss=2, outline=0.004):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if ss > 0:
        m = obj.modifiers.new("SS", "SUBSURF")
        m.levels = ss; m.render_levels = ss
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    if outline > 0:
        om = bpy.data.materials.get("M_Outline")
        if om:
            m = obj.modifiers.new("Outline", "SOLIDIFY")
            m.thickness = outline; m.offset = -1; m.use_flip_normals = True
            m.material_offset = len(obj.data.materials)
            obj.data.materials.append(om)

def hair_strip(name, loc, rot_deg, length, base_w, tip_w, mat_name="M_KiritoHair", thickness=0.012, ns=6):
    profiles = [
        (0, base_w, thickness, 0, 0),
        (length*0.25, base_w*0.85, thickness*0.9, 0, 0),
        (length*0.5, base_w*0.6, thickness*0.7, 0, 0),
        (length*0.75, base_w*0.35, thickness*0.5, 0, 0),
        (length*0.9, tip_w*1.5, thickness*0.3, 0, 0),
        (length, tip_w*0.3, thickness*0.1, 0, 0),
    ]
    obj = loft(name, profiles, ns=ns, cap_top=True, cap_bot=True)
    obj.location = loc
    obj.rotation_euler = tuple(math.radians(d) for d in rot_deg)
    setup(obj, mat_name, ss=1, outline=0.003)
    return obj

# Store in driver namespace for reuse
bpy.app.driver_namespace["loft"] = loft
bpy.app.driver_namespace["setup"] = setup
bpy.app.driver_namespace["hair_strip"] = hair_strip

result = "Helper functions registered"
'''

# ============================================================
# 桐人 (Kirito) - Black Swordsman
# ============================================================

KIRITO_CODE = '''
import bpy, bmesh, math
loft = bpy.app.driver_namespace["loft"]
setup = bpy.app.driver_namespace["setup"]
hair_strip = bpy.app.driver_namespace["hair_strip"]

kx = -1.2  # Kirito X position

# === Head ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.115, location=(kx, 0, 1.58))
head = bpy.context.active_object
head.name = "K_Head"
head.scale = (1.0, 0.85, 1.06)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < -0.02:
        f = max(0, (-0.02 - v.co.z)/0.08)
        v.co.x *= 1.0 - f*0.5
        v.co.y *= 1.0 - f*0.4
    if v.co.y > 0.02:
        v.co.y *= 0.88
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(head, "M_Skin", outline=0.004)

# === Eyes ===
for side, sx in [("L", -0.04), ("R", 0.04)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.028, location=(kx+sx, -0.088, 1.59))
    eye = bpy.context.active_object
    eye.name = f"K_Eye_{side}"
    eye.scale = (0.75, 0.38, 1.0)
    setup(eye, "M_KiritoEye", ss=1, outline=0)
    # Pupil
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.014, location=(kx+sx, -0.10, 1.59))
    pupil = bpy.context.active_object
    pupil.name = f"K_Pupil_{side}"
    setup(pupil, "M_EyeBlack", ss=1, outline=0)
    # Highlight
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.006, location=(kx+sx+0.008, -0.105, 1.60))
    hl = bpy.context.active_object
    hl.name = f"K_Highlight_{side}"
    setup(hl, "M_EyeHighlight", ss=0, outline=0)

# === Body (torso) ===
profiles_body = [
    (0, 0.12, 0.08, 0, 0),
    (0.08, 0.15, 0.10, 0, 0),
    (0.22, 0.16, 0.10, 0, 0),
    (0.38, 0.14, 0.09, 0, 0),
    (0.45, 0.11, 0.08, 0, 0),
]
body = loft("K_Body", profiles_body, ns=16, cap_top=True, cap_bot=True)
body.location = (kx, 0, 1.0)
setup(body, "M_KiritoBlack", ss=2, outline=0.004)

# === Legs ===
for side, sx in [("L", -0.06), ("R", 0.06)]:
    profs = [
        (0, 0.05, 0.05, 0, 0),
        (0.18, 0.048, 0.048, 0, 0),
        (0.42, 0.04, 0.04, 0, 0),
        (0.55, 0.038, 0.042, 0, 0),
    ]
    leg = loft(f"K_Leg_{side}", profs, ns=12, cap_top=True, cap_bot=True)
    leg.location = (kx+sx, 0, 0.45)
    setup(leg, "M_KiritoBlack", ss=1, outline=0.004)
    # Boot
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(kx+sx, -0.01, 0.05))
    boot = bpy.context.active_object
    boot.name = f"K_Boot_{side}"
    boot.scale = (0.7, 1.2, 0.6)
    setup(boot, "M_KiritoBlack", ss=1, outline=0.003)

# === Arms ===
for side, sx, rot in [("L", -0.22, 12), ("R", 0.22, -12)]:
    profs = [
        (0, 0.035, 0.035, 0, 0),
        (0.15, 0.033, 0.033, 0, 0),
        (0.30, 0.028, 0.028, 0, 0),
        (0.40, 0.024, 0.024, 0, 0),
    ]
    arm = loft(f"K_Arm_{side}", profs, ns=10, cap_top=True, cap_bot=True)
    arm.location = (kx+sx, 0, 1.35)
    arm.rotation_euler = (0, 0, math.radians(rot))
    setup(arm, "M_KiritoBlack", ss=1, outline=0.003)
    # Hand
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.022, location=(kx+sx*1.5, 0, 0.95))
    hand = bpy.context.active_object
    hand.name = f"K_Hand_{side}"
    hand.scale = (0.8, 0.6, 1.0)
    setup(hand, "M_Skin", ss=1, outline=0.002)

# === Coat (long black coat with trim) ===
coat_profs = [
    (0, 0.18, 0.12, 0, 0),
    (0.15, 0.20, 0.12, 0, 0),
    (0.40, 0.22, 0.11, 0, 0.01),
    (0.65, 0.25, 0.10, 0, 0.02),
    (0.85, 0.24, 0.08, 0, 0.03),
]
coat = loft("K_Coat", coat_profs, ns=20, cap_top=True, cap_bot=True)
coat.location = (kx, 0, 0.35)
setup(coat, "M_KiritoBlack", ss=2, outline=0.005)

# === Belt cross ===
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(kx, -0.11, 1.25))
belt1 = bpy.context.active_object
belt1.name = "K_Belt1"
belt1.scale = (6, 0.8, 1)
belt1.rotation_euler = (0, 0, math.radians(25))
setup(belt1, "M_KiritoBelt", ss=0, outline=0)
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(kx, -0.11, 1.25))
belt2 = bpy.context.active_object
belt2.name = "K_Belt2"
belt2.scale = (6, 0.8, 1)
belt2.rotation_euler = (0, 0, math.radians(-25))
setup(belt2, "M_KiritoBelt", ss=0, outline=0)

# === Hair (spiky black) ===
# Main top spikes
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,   0.02,  1.70, -10, 0,  0,    0.12, 0.035),
    (0.04, 0.01, 1.71, -15, 0,  20,   0.11, 0.030),
    (-0.04,0.01, 1.71, -15, 0, -20,   0.11, 0.030),
    (0.07, 0,    1.68, -10, 0,  40,   0.10, 0.028),
    (-0.07,0,    1.68, -10, 0, -40,   0.10, 0.028),
    (0.03, 0.04, 1.69, -30, 0,  10,   0.09, 0.025),
    (-0.03,0.04, 1.69, -30, 0, -10,   0.09, 0.025),
]):
    hair_strip(f"K_Hair_Top_{i}", (kx+ox, oy, oz), (rx,ry,rz), l, bw, 0.005)

# Back hair
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    0.06, 1.62, 160, 0,  0,   0.14, 0.04),
    (0.05, 0.06, 1.60, 155, 0,  15,  0.13, 0.035),
    (-0.05,0.06, 1.60, 155, 0, -15,  0.13, 0.035),
    (0.08, 0.05, 1.58, 150, 0,  30,  0.11, 0.030),
    (-0.08,0.05, 1.58, 150, 0, -30,  0.11, 0.030),
]):
    hair_strip(f"K_Hair_Back_{i}", (kx+ox, oy, oz), (rx,ry,rz), l, bw, 0.005)

# Bangs
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    -0.08, 1.66, 70, 0,  0,   0.10, 0.035),
    (0.04, -0.08, 1.66, 65, 0,  15,  0.09, 0.030),
    (-0.04,-0.08, 1.66, 65, 0, -15,  0.09, 0.030),
    (0.07, -0.06, 1.64, 55, 0,  30,  0.08, 0.025),
    (-0.07,-0.06, 1.64, 55, 0, -30,  0.08, 0.025),
]):
    hair_strip(f"K_Hair_Bang_{i}", (kx+ox, oy, oz), (rx,ry,rz), l, bw, 0.005)

result = "Kirito complete"
'''

# ============================================================
# 亚丝娜 (Asuna) - Knight of Blood
# ============================================================

ASUNA_CODE = '''
import bpy, bmesh, math
loft = bpy.app.driver_namespace["loft"]
setup = bpy.app.driver_namespace["setup"]
hair_strip = bpy.app.driver_namespace["hair_strip"]

ax = 0.0  # Asuna position (center)

# === Head ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.115, location=(ax, 0, 1.58))
head = bpy.context.active_object
head.name = "A_Head"
head.scale = (1.0, 0.88, 1.08)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < -0.02:
        f = max(0, (-0.02 - v.co.z)/0.08)
        v.co.x *= 1.0 - f*0.48
        v.co.y *= 1.0 - f*0.38
    if v.co.y > 0.02:
        v.co.y *= 0.88
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(head, "M_Skin", outline=0.004)

# === Eyes (amber, larger & rounder) ===
for side, sx in [("L", -0.04), ("R", 0.04)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.032, location=(ax+sx, -0.090, 1.59))
    eye = bpy.context.active_object
    eye.name = f"A_Eye_{side}"
    eye.scale = (0.75, 0.38, 1.05)
    setup(eye, "M_AsunaEye", ss=1, outline=0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.015, location=(ax+sx, -0.103, 1.59))
    pupil = bpy.context.active_object
    pupil.name = f"A_Pupil_{side}"
    setup(pupil, "M_EyeBlack", ss=1, outline=0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.007, location=(ax+sx+0.008, -0.108, 1.605))
    hl = bpy.context.active_object
    hl.name = f"A_Highlight_{side}"
    setup(hl, "M_EyeHighlight", ss=0, outline=0)

# === Body - white chest armor with red cross ===
body_profs = [
    (0, 0.11, 0.08, 0, 0),
    (0.06, 0.14, 0.09, 0, 0),
    (0.20, 0.15, 0.09, 0, 0),
    (0.36, 0.13, 0.085, 0, 0),
    (0.42, 0.10, 0.07, 0, 0),
]
body = loft("A_Body", body_profs, ns=16, cap_top=True, cap_bot=True)
body.location = (ax, 0, 1.02)
setup(body, "M_AsunaWhite", ss=2, outline=0.004)

# === Red cross emblem on chest ===
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(ax, -0.095, 1.25))
cross_h = bpy.context.active_object
cross_h.name = "A_Cross_H"
cross_h.scale = (4.0, 0.5, 1.0)
setup(cross_h, "M_AsunaRed", ss=0, outline=0)
bpy.ops.mesh.primitive_cube_add(size=0.01, location=(ax, -0.095, 1.25))
cross_v = bpy.context.active_object
cross_v.name = "A_Cross_V"
cross_v.scale = (1.0, 0.5, 4.0)
setup(cross_v, "M_AsunaRed", ss=0, outline=0)

# === Red pleated skirt ===
skirt_profs = [
    (0, 0.12, 0.09, 0, 0),
    (0.05, 0.16, 0.10, 0, 0),
    (0.12, 0.20, 0.12, 0, 0),
    (0.20, 0.22, 0.13, 0, 0.01),
]
skirt = loft("A_Skirt", skirt_profs, ns=20, cap_top=True, cap_bot=True)
skirt.location = (ax, 0, 0.78)
setup(skirt, "M_AsunaRed", ss=2, outline=0.004)

# === Legs ===
for side, sx in [("L", -0.055), ("R", 0.055)]:
    profs = [
        (0, 0.045, 0.045, 0, 0),
        (0.20, 0.043, 0.043, 0, 0),
        (0.42, 0.036, 0.036, 0, 0),
        (0.55, 0.034, 0.038, 0, 0),
    ]
    leg = loft(f"A_Leg_{side}", profs, ns=12, cap_top=True, cap_bot=True)
    leg.location = (ax+sx, 0, 0.23)
    setup(leg, "M_Skin", ss=1, outline=0.003)
    # White knee-high boots
    boot_profs = [
        (0, 0.042, 0.048, 0, 0),
        (0.12, 0.040, 0.042, 0, 0),
        (0.28, 0.038, 0.040, 0, 0),
        (0.35, 0.036, 0.044, 0, 0),
    ]
    boot = loft(f"A_Boot_{side}", boot_profs, ns=12, cap_top=True, cap_bot=True)
    boot.location = (ax+sx, 0, 0.0)
    setup(boot, "M_AsunaWhite", ss=1, outline=0.003)

# === Arms (white sleeves) ===
for side, sx, rot in [("L", -0.20, 15), ("R", 0.20, -15)]:
    profs = [
        (0, 0.032, 0.032, 0, 0),
        (0.14, 0.030, 0.030, 0, 0),
        (0.28, 0.026, 0.026, 0, 0),
        (0.38, 0.022, 0.022, 0, 0),
    ]
    arm = loft(f"A_Arm_{side}", profs, ns=10, cap_top=True, cap_bot=True)
    arm.location = (ax+sx, 0, 1.35)
    arm.rotation_euler = (0, 0, math.radians(rot))
    setup(arm, "M_AsunaWhite", ss=1, outline=0.003)
    # Hand
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.020, location=(ax+sx*1.5, 0, 0.97))
    hand = bpy.context.active_object
    hand.name = f"A_Hand_{side}"
    hand.scale = (0.8, 0.6, 1.0)
    setup(hand, "M_Skin", ss=1, outline=0.002)

# === Shoulder armor (red) ===
for side, sx in [("L", -0.17), ("R", 0.17)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.045, location=(ax+sx, 0, 1.44))
    sp = bpy.context.active_object
    sp.name = f"A_Shoulder_{side}"
    sp.scale = (1.0, 0.8, 0.7)
    setup(sp, "M_AsunaRed", ss=1, outline=0.003)

# === Gold belt ===
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.012, location=(ax, 0, 1.02))
belt = bpy.context.active_object
belt.name = "A_GoldBelt"
belt.scale = (1.0, 0.8, 0.3)
setup(belt, "M_AsunaGold", ss=1, outline=0)

# === Hair (long orange-brown, past waist) ===
# Top volume
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    0.02,  1.70, -5,  0,  0,   0.10, 0.04),
    (0.04, 0.01,  1.70, -8,  0,  15,  0.09, 0.035),
    (-0.04,0.01,  1.70, -8,  0, -15,  0.09, 0.035),
    (0.07, 0,     1.67, -5,  0,  30,  0.08, 0.030),
    (-0.07,0,     1.67, -5,  0, -30,  0.08, 0.030),
]):
    hair_strip(f"A_Hair_Top_{i}", (ax+ox, oy, oz), (rx,ry,rz), l, bw, 0.005, mat_name="M_AsunaHair")

# Long back hair (past waist)
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    0.07,  1.62, 170, 0,  0,   0.55, 0.05),
    (0.05, 0.07,  1.60, 165, 0,  10,  0.52, 0.045),
    (-0.05,0.07,  1.60, 165, 0, -10,  0.52, 0.045),
    (0.09, 0.06,  1.56, 160, 0,  20,  0.48, 0.040),
    (-0.09,0.06,  1.56, 160, 0, -20,  0.48, 0.040),
    (0.03, 0.08,  1.58, 168, 0,  5,   0.50, 0.042),
    (-0.03,0.08,  1.58, 168, 0, -5,   0.50, 0.042),
]):
    hair_strip(f"A_Hair_Back_{i}", (ax+ox, oy, oz), (rx,ry,rz), l, bw, 0.006, mat_name="M_AsunaHair")

# Bangs
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    -0.08, 1.67, 70, 0,  0,   0.08, 0.03),
    (0.035,-0.08, 1.67, 65, 0,  12,  0.07, 0.028),
    (-0.035,-0.08,1.67, 65, 0, -12,  0.07, 0.028),
    (0.06, -0.07, 1.65, 55, 0,  25,  0.06, 0.024),
    (-0.06,-0.07, 1.65, 55, 0, -25,  0.06, 0.024),
]):
    hair_strip(f"A_Hair_Bang_{i}", (ax+ox, oy, oz), (rx,ry,rz), l, bw, 0.005, mat_name="M_AsunaHair")

# White headband
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.008, location=(ax, 0, 1.68))
hband = bpy.context.active_object
hband.name = "A_Headband"
hband.scale = (1.0, 0.85, 1.0)
hband.rotation_euler = (math.radians(15), 0, 0)
setup(hband, "M_AsunaWhite", ss=1, outline=0)

result = "Asuna complete"
'''

# ============================================================
# 克莱因 (Klein)
# ============================================================

KLEIN_CODE = '''
import bpy, bmesh, math
loft = bpy.app.driver_namespace["loft"]
setup = bpy.app.driver_namespace["setup"]
hair_strip = bpy.app.driver_namespace["hair_strip"]

kx = 1.2  # Klein position (right)

# === Head (slightly wider, more masculine) ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.12, location=(kx, 0, 1.56))
head = bpy.context.active_object
head.name = "KL_Head"
head.scale = (1.05, 0.88, 1.02)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(head.data)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.co.z < -0.02:
        f = max(0, (-0.02 - v.co.z)/0.08)
        v.co.x *= 1.0 - f*0.45
        v.co.y *= 1.0 - f*0.35
bmesh.update_edit_mesh(head.data)
bpy.ops.object.mode_set(mode="OBJECT")
setup(head, "M_SkinTan", outline=0.004)

# === Eyes (narrower, more masculine) ===
for side, sx in [("L", -0.042), ("R", 0.042)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.025, location=(kx+sx, -0.092, 1.57))
    eye = bpy.context.active_object
    eye.name = f"KL_Eye_{side}"
    eye.scale = (0.8, 0.35, 0.85)
    setup(eye, "M_KiritoEye", ss=1, outline=0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.012, location=(kx+sx, -0.103, 1.57))
    pupil = bpy.context.active_object
    pupil.name = f"KL_Pupil_{side}"
    setup(pupil, "M_EyeBlack", ss=1, outline=0)

# === Body (broader, red/cream armor) ===
body_profs = [
    (0, 0.14, 0.09, 0, 0),
    (0.08, 0.17, 0.11, 0, 0),
    (0.24, 0.18, 0.11, 0, 0),
    (0.40, 0.15, 0.10, 0, 0),
    (0.48, 0.12, 0.08, 0, 0),
]
body = loft("KL_Body", body_profs, ns=16, cap_top=True, cap_bot=True)
body.location = (kx, 0, 0.98)
setup(body, "M_KleinRed", ss=2, outline=0.004)

# === Cream undershirt visible at collar ===
bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.06, location=(kx, 0, 1.44))
collar = bpy.context.active_object
collar.name = "KL_Collar"
collar.scale = (1.0, 0.8, 1.0)
setup(collar, "M_KleinCream", ss=1, outline=0)

# === Legs ===
for side, sx in [("L", -0.07), ("R", 0.07)]:
    profs = [
        (0, 0.055, 0.055, 0, 0),
        (0.20, 0.052, 0.052, 0, 0),
        (0.42, 0.042, 0.042, 0, 0),
        (0.55, 0.040, 0.045, 0, 0),
    ]
    leg = loft(f"KL_Leg_{side}", profs, ns=12, cap_top=True, cap_bot=True)
    leg.location = (kx+sx, 0, 0.42)
    setup(leg, "M_KleinBrown", ss=1, outline=0.004)
    # Boots
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(kx+sx, -0.01, 0.05))
    boot = bpy.context.active_object
    boot.name = f"KL_Boot_{side}"
    boot.scale = (0.75, 1.2, 0.65)
    setup(boot, "M_KleinBrown", ss=1, outline=0.003)

# === Arms ===
for side, sx, rot in [("L", -0.24, 10), ("R", 0.24, -10)]:
    profs = [
        (0, 0.038, 0.038, 0, 0),
        (0.16, 0.035, 0.035, 0, 0),
        (0.32, 0.030, 0.030, 0, 0),
        (0.42, 0.026, 0.026, 0, 0),
    ]
    arm = loft(f"KL_Arm_{side}", profs, ns=10, cap_top=True, cap_bot=True)
    arm.location = (kx+sx, 0, 1.33)
    arm.rotation_euler = (0, 0, math.radians(rot))
    setup(arm, "M_KleinRed", ss=1, outline=0.003)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.024, location=(kx+sx*1.5, 0, 0.92))
    hand = bpy.context.active_object
    hand.name = f"KL_Hand_{side}"
    hand.scale = (0.85, 0.65, 1.0)
    setup(hand, "M_SkinTan", ss=1, outline=0.002)

# === Spiky red hair ===
for i, (ox, oy, oz, rx, ry, rz, l, bw) in enumerate([
    (0,    0.02,  1.68, -15, 0,  0,   0.11, 0.035),
    (0.05, 0.01,  1.69, -20, 0,  25,  0.10, 0.032),
    (-0.05,0.01,  1.69, -20, 0, -25,  0.10, 0.032),
    (0.08, 0,     1.66, -12, 0,  45,  0.09, 0.028),
    (-0.08,0,     1.66, -12, 0, -45,  0.09, 0.028),
    (0.03, 0.04,  1.67, -35, 0,  12,  0.08, 0.025),
    (-0.03,0.04,  1.67, -35, 0, -12,  0.08, 0.025),
    (0,    0.05,  1.64, 155, 0,  0,   0.10, 0.035),
    (0.04, 0.05,  1.62, 150, 0,  15,  0.09, 0.030),
    (-0.04,0.05,  1.62, 150, 0, -15,  0.09, 0.030),
]):
    hair_strip(f"KL_Hair_{i}", (kx+ox, oy, oz), (rx,ry,rz), l, bw, 0.005, mat_name="M_KleinHair")

# Bandana
bpy.ops.mesh.primitive_torus_add(major_radius=0.125, minor_radius=0.01, location=(kx, 0, 1.64))
band = bpy.context.active_object
band.name = "KL_Bandana"
band.scale = (1.0, 0.88, 0.5)
setup(band, "M_KleinRed", ss=1, outline=0)

result = "Klein complete"
'''

# ============================================================
# 场景灯光和摄像机
# ============================================================

SCENE_SETUP_CODE = '''
import bpy, math

# --- EEVEE anime render settings ---
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "RenderSettings") and "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# World background (soft gradient)
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.15, 0.18, 0.28, 1.0)
    bg.inputs["Strength"].default_value = 0.8

# --- Anime 3-point lighting ---
# Key Light (warm sun)
bpy.ops.object.light_add(type="SUN", location=(5, -5, 10))
kl = bpy.context.active_object
kl.name = "SAO_KeyLight"
kl.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
kl.data.energy = 3.5
kl.data.color = (1.0, 0.95, 0.88)

# Fill Light (cool blue)
bpy.ops.object.light_add(type="SUN", location=(-5, -3, 5))
fl = bpy.context.active_object
fl.name = "SAO_FillLight"
fl.rotation_euler = (math.radians(65), math.radians(-30), math.radians(-20))
fl.data.energy = 1.2
fl.data.color = (0.82, 0.88, 1.0)

# Rim Light (bright white backlight)
bpy.ops.object.light_add(type="SUN", location=(0, 5, 8))
rl = bpy.context.active_object
rl.name = "SAO_RimLight"
rl.rotation_euler = (math.radians(-30), 0, math.radians(180))
rl.data.energy = 2.0

# --- Camera ---
bpy.ops.object.camera_add(location=(0, -4.5, 1.3))
cam = bpy.context.active_object
cam.name = "SAO_Camera"
cam.data.lens = 65
# Point at center of characters
from mathutils import Vector
direction = Vector((0, 0, 1.2)) - cam.location
rot_quat = direction.to_track_quat("-Z", "Y")
cam.rotation_euler = rot_quat.to_euler()
scene.camera = cam

# Set frame range
scene.frame_start = 1
scene.frame_end = 250

result = "Scene setup complete"
'''

# ============================================================
# Ground plane
# ============================================================

GROUND_CODE = '''
import bpy

# Simple ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "SAO_Ground"

# Ground material (dark blue-grey)
mat = bpy.data.materials.new("M_Ground")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.08, 0.10, 0.15, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
ground.data.materials.append(mat)

result = "Ground created"
'''


async def main():
    global PASS, FAIL

    print("=" * 60)
    print("刀剑神域 (Sword Art Online) 同人角色构建")
    print("=" * 60)
    print("Connecting to Blender...")

    conn = BlenderConnection(host="127.0.0.1", port=9876)
    await conn.connect()
    print("Connected!\n")

    start = time.time()

    # Step 1: Create new scene
    print("--- Step 1: 创建新场景 ---")
    await test(conn, "scene.create", "scene", "create", {"name": "SAO_FanArt"})
    await test(conn, "scene.switch", "scene", "switch", {"scene_name": "SAO_FanArt"})

    # Clear default objects
    await run_py(conn, "clear_defaults", '''
import bpy
for obj in list(bpy.data.objects):
    if obj.users_scene and bpy.context.scene.name in [s.name for s in obj.users_scene]:
        bpy.data.objects.remove(obj, do_unlink=True)
result = "Scene cleared"
''')

    # Step 2: Material system
    print("\n--- Step 2: 创建 Toon 着色材质系统 ---")
    await run_py(conn, "materials.setup", MATERIAL_SETUP_CODE)

    # Step 3: Helper functions
    print("\n--- Step 3: 注册辅助函数 ---")
    await run_py(conn, "helpers.register", HELPER_FUNCS_CODE)

    # Step 4: Build Kirito
    print("\n--- Step 4: 构建 桐人 (Kirito) - 黑色剑士 ---")
    await run_py(conn, "kirito.build", KIRITO_CODE)

    # Step 5: Build Asuna
    print("\n--- Step 5: 构建 亚丝娜 (Asuna) - 血盟骑士团 ---")
    await run_py(conn, "asuna.build", ASUNA_CODE)

    # Step 6: Build Klein
    print("\n--- Step 6: 构建 克莱因 (Klein) - 风林火山 ---")
    await run_py(conn, "klein.build", KLEIN_CODE)

    # Step 7: Ground
    print("\n--- Step 7: 地面 ---")
    await run_py(conn, "ground.create", GROUND_CODE)

    # Step 8: Scene setup (lighting, camera, render)
    print("\n--- Step 8: 灯光/摄像机/渲染设置 ---")
    await run_py(conn, "scene.lighting", SCENE_SETUP_CODE)

    # Step 9: Save checkpoint
    print("\n--- Step 9: 保存检查点 ---")
    await test(conn, "checkpoint.save", "checkpoint", "save", {
        "name": "sao_fan_art_complete",
        "description": "SAO fan art with Kirito, Asuna, Klein - toon shaded"
    })

    # Step 10: Describe scene
    print("\n--- Step 10: 场景描述 ---")
    result = await test(conn, "describe.scene", "describe", "scene", {"format": "markdown"})
    if result.get("success"):
        summary = result.get("data", {}).get("summary", "")
        for line in summary.split("\n")[:25]:
            print(f"  | {line}")

    # Step 11: Hierarchy
    result = await test(conn, "describe.hierarchy", "describe", "hierarchy", {"format": "markdown"})
    if result.get("success"):
        tree = result.get("data", {}).get("tree", "")
        for line in tree.split("\n")[:30]:
            print(f"  | {line}")

    # Step 12: Take snapshots
    print("\n--- Step 11: 截图 ---")
    result = await test(conn, "snapshot.viewport", "snapshot", "viewport", {"width": 1920, "height": 1080})
    if result.get("success"):
        print(f"  视口截图: {result.get('data', {}).get('path', '?')}")

    result = await test(conn, "snapshot.render", "snapshot", "render_preview", {"width": 960, "samples": 32})
    if result.get("success"):
        print(f"  渲染预览: {result.get('data', {}).get('path', '?')}")

    elapsed = time.time() - start
    await conn.disconnect()

    print("\n" + "=" * 60)
    print(f"构建完成: {PASS}/{PASS+FAIL} 通过, {FAIL} 失败 ({elapsed:.1f}s)")
    print("=" * 60)
    print("\n场景 'SAO_FanArt' 已保留在 Blender 中:")
    print("  - 桐人 (Kirito)  位置: x=-1.2  黑色剑士装束")
    print("  - 亚丝娜 (Asuna) 位置: x=0.0   血盟骑士团铠甲")
    print("  - 克莱因 (Klein)  位置: x=1.2   风林火山战士")
    print("\n按 小键盘0 切换摄像机视角, F12 渲染")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
