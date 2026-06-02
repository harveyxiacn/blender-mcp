# Unity / Quest VR Export Workflow

How to export Blender models from this MCP server so they drop into a Unity URP
project (e.g. a Meta Quest title) with a **zeroed Transform**, correct axis,
correct scale, and a mobile-safe triangle budget.

This mirrors the requirements in
`AmblyopiaThreatment6.5/docs/blender_model_spec_zh.md` §1, and is what the
`amblyopia_build/` pipeline uses.

---

## 1. The one call you need

For **non-rigged props / environments**:

```python
blender_export_fbx(
    filepath="<UnityProject>/Assets/Models/.../PROP_Name.fbx",
    selected_only=True,          # export just the selected object(s)
    unity_static_preset=True,    # <-- the important flag
)
```

`unity_static_preset=True` sets, under the hood:

| Setting | Value | Why |
|---|---|---|
| `axis_forward` | `-Z` | Unity importer convention |
| `axis_up` | `Y` | Unity is Y-up; Blender is Z-up |
| `use_space_transform` | `True` | convert spaces on export |
| `bake_space_transform` | `True` | **bakes the axis conversion into the mesh** so Unity shows Transform = (0,0,0) with no residual -90° X rotation |
| `mesh_smooth_type` | `FACE` | export smoothing groups |
| `object_types` | `{MESH, EMPTY}` | don't export cameras/lights |
| `apply_unit_scale` | `True` | 1 Blender unit = 1 m = 1 Unity unit |

All of these are also individually overridable as named params if you need to.

> On the **Unity import side**, also tick **Bake Axis Conversion** on the model
> importer and set **Scale Factor = 1**. With both sides set, the object imports
> at Position (0,0,0) Rotation (0,0,0) Scale (1,1,1).

For **rigged characters**, do **not** bake the space transform:

```python
blender_export_fbx(
    filepath=...,
    selected_only=True,
    unity_static_preset=False,
    primary_bone_axis="Y", secondary_bone_axis="X",
    add_leaf_bones=False,
)
```

---

## 2. Pre-export checklist (do this in Blender first)

1. **Metric, unit scale 1.0** — `scene.unit_settings.system='METRIC'`,
   `scale_length=1.0`.
2. **Apply all transforms** — scale = (1,1,1), rotation = (0,0,0). Bake any
   per-part rotations into the mesh before export (e.g. join, then
   `transform_apply`).
3. **Set the origin** per use:
   - floor-standing props (seat, sofa, table, trophy) → **bottom-centre** (Z=0)
   - wall props (screen frame, picture, window) → **geometric centre**
   - balls / targets / orbs → **geometric centre**
   - Tool: `blender_set_origin(name=..., origin_type="BOTTOM" | "GEOMETRY")`.
4. **Front faces -Y** in Blender (= +Z forward in Unity).
5. **One object per file**, named like the file (PascalCase / spec prefix).

---

## 3. Triangle budgets (Quest 3, 90 Hz, stylized low-poly)

Verify with:

```python
blender_get_object_info(name="PROP_Name", include_mesh_stats=True)
# -> data.mesh_stats.triangles
```

Typical budgets (per the Amblyopia spec — adjust per project):

| Category | Tri budget / item |
|---|---|
| Environment shell (floor/walls/ceiling per theme) | ≤ 8 000 |
| Hero prop (main seat, sofa, planet, hero crater) | ≤ 2 500 |
| Standard prop (table, lamp, shelf, plant, window, frame) | ≤ 800 |
| Instanceable small prop (audience seat, panel, book, rock, orb, brick) | ≤ 400 |
| Game target / brick / paddle | ≤ 600 |
| Reward (trophy, medal, badge) | ≤ 1 500 |

Style: stylized low-poly, flat shading, **low Unity smoothness** (≈ 0.12) =
**high Blender roughness** (≈ 0.85). Prefer one shared material per kit; put
emissive areas (glow points, neon, lampshades, windows) on their own material
slot. Avoid high-contrast noise textures on anything that enters a dichoptic
mask region.

---

## 4. Recommended per-model loop

A robust pipeline for each model — drive Blender via `blender_execute_python`
(or the socket protocol directly):

1. Build the multi-part mesh (primitives + modifiers).
2. Join into one object; apply **all** transforms.
3. Set the origin (bottom-centre for floor props, centre for wall props).
4. Verify the triangle budget via
   `blender_get_object_info(name=..., include_mesh_stats=True)`.
5. Export with `blender_export_fbx(filepath=..., selected_only=True, unity_static_preset=True)`.
6. Save a `.blend` source for later re-editing.

Batching this loop over a model list lets you regenerate a whole kit
deterministically from a spec.
