# Blender MCP API Reference

## Overview

This document describes all tools provided by Blender MCP. Tools are exposed via the MCP protocol and can be used from any MCP-compatible IDE.

Status note (2026-03-10): the repository now contains 51 tool modules and 359 total tool registrations. This reference remains strongest for the stable/core tool families. Newer modules such as `training`, `sport_character`, `style_presets`, `procedural_materials`, and the experimental automation surface should be cross-checked with source and the project review until this reference is expanded.

## Tool Naming Convention

All tool names follow this pattern:
```
blender_{category}_{action}
```

Examples:
- `blender_object_create` — Create an object
- `blender_scene_list` — List scenes
- `blender_modifier_add` — Add a modifier

## Skill System

With the `"skill"` profile (default), only **core tools** are loaded at startup. Use skill meta-tools to load additional tool groups on demand.

### Skill Meta-Tools (Always Available)

| Tool | Description |
|------|-------------|
| `blender_list_skills` | List all 12 skill groups and their activation status |
| `blender_activate_skill` | Load a skill's tool group dynamically |
| `blender_deactivate_skill` | Unload a skill's tools to free context |

---

## Core Tools (Always Loaded)

### 1. Scene Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `blender_scene_create` | Create a new scene | `name`, `copy_from` |
| `blender_scene_list` | List all scenes | `response_format` |
| `blender_scene_get_info` | Get scene details | `scene_name` |
| `blender_scene_set_settings` | Set scene settings | `fps`, `frame_start`, `frame_end`, `unit_system` |
| `blender_scene_switch` | Switch active scene | `scene_name` |
| `blender_scene_delete` | Delete a scene | `scene_name` |

### 2. Object Operations

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `blender_object_create` | Create mesh primitives | `type` (CUBE/SPHERE/CYLINDER/...), `name`, `location`, `rotation`, `scale`, `mesh_params` |
| `blender_object_delete` | Delete an object | `name` |
| `blender_object_transform` | Transform (move/rotate/scale) | `name`, `location`, `rotation`, `scale`, `delta_*` |
| `blender_object_get_info` | Get object details | `name`, `include_materials`, `include_modifiers` |
| `blender_object_list` | List scene objects | `type_filter`, `name_pattern`, `limit` |
| `blender_object_select` | Select objects | `names`, `pattern`, `set_active` |
| `blender_object_duplicate` | Duplicate an object | `name`, `new_name`, `linked`, `offset` |
| `blender_object_join` | Join multiple objects | `objects`, `target` |
| `blender_object_parent` | Set parent-child relationship | `child_name`, `parent_name` |
| `blender_object_rename` | Rename an object | `name`, `new_name` |
| `blender_object_set_origin` | Set object origin | `name`, `origin_type` (GEOMETRY/CURSOR/BOTTOM) |
| `blender_object_apply_transform` | Apply transforms | `name`, `location`, `rotation`, `scale` |

#### Object Types for `blender_object_create`

```
CUBE, SPHERE, UV_SPHERE, ICO_SPHERE, CYLINDER, CONE, TORUS,
PLANE, CIRCLE, GRID, MONKEY, BEZIER, NURBS_CURVE, NURBS_CIRCLE,
PATH, TEXT, EMPTY, ARMATURE, LATTICE, CAMERA, LIGHT
```

#### mesh_params Examples

```json
{"segments": 32, "ring_count": 16, "radius": 1.0}       // UV_SPHERE
{"vertices": 32, "radius": 1.0, "depth": 2.0}            // CYLINDER
{"major_segments": 48, "minor_segments": 12}              // TORUS
{"subdivisions": 2, "radius": 1.0}                        // ICO_SPHERE
```

### 3. Utility Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `blender_execute_python` | Execute Python code in Blender | `code`, `timeout` |
| `blender_get_viewport_screenshot` | Capture viewport screenshot | `width`, `height`, `output_path` |
| `blender_get_info` | Get Blender version & status | — |
| `blender_file_save` | Save .blend file | `filepath`, `compress` |
| `blender_file_open` | Open .blend file | `filepath`, `load_ui` |
| `blender_undo` | Undo | `steps` |
| `blender_redo` | Redo | `steps` |

### 4. Export Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `blender_export_gltf` | Export as glTF/GLB | `filepath`, `export_format`, `include_animation` |
| `blender_export_fbx` | Export as FBX | `filepath`, `apply_modifiers`, `include_animation` |
| `blender_export_obj` | Export as OBJ | `filepath`, `apply_modifiers`, `export_materials` |

---

## Skill-Loaded Tools

The following tools become available after activating their respective skills.

### Skill: modeling (~38 tools)

**Activate**: `blender_activate_skill("modeling")`

Includes mesh editing, modifiers, curves, and UV mapping tools.

| Category | Key Tools |
|----------|-----------|
| Mesh Editing | `blender_mesh_extrude`, `blender_mesh_bevel`, `blender_mesh_subdivide`, `blender_mesh_select`, `blender_mesh_edit_mode` |
| Modifiers | `blender_modifier_add` (45 types), `blender_modifier_apply`, `blender_modifier_remove` |
| Boolean | `blender_boolean_operation` |
| Shape Keys | `blender_shapekey_create`, `blender_shapekey_edit`, `blender_shapekey_list` |
| Curves | `blender_curve_create`, `blender_curve_extrude`, `blender_curve_to_mesh`, `blender_curve_spiral` |
| UV Mapping | `blender_uv_unwrap`, `blender_uv_smart_project`, `blender_uv_project`, `blender_uv_pack` |

#### Modifier Types (45)

```
SUBDIVISION, MIRROR, ARRAY, SOLIDIFY, BEVEL, BOOLEAN, DECIMATE,
SMOOTH, SHRINKWRAP, SIMPLE_DEFORM, SCREW, WIREFRAME, WELD,
REMESH, BUILD, MULTIRES, CAST, CURVE, LATTICE, SKIN,
CLOTH, COLLISION, PARTICLE_SYSTEM, ARMATURE, ...
```

### Skill: materials (~17 tools)

**Activate**: `blender_activate_skill("materials")`

| Category | Key Tools |
|----------|-----------|
| Standard | `blender_material_create`, `blender_material_assign`, `blender_material_edit` |
| Procedural | `blender_procedural_material` (67 presets: metal/wood/stone/fabric/nature/skin/effect/toon) |
| Wear Effects | `blender_material_wear` (edge_wear/scratches/rust/dirt/dust/moss/paint_chip) |

### Skill: style (~8 tools)

**Activate**: `blender_activate_skill("style")`

| Category | Key Tools |
|----------|-----------|
| Style Setup | `blender_style_setup` (PIXEL/LOW_POLY/STYLIZED/TOON/HAND_PAINTED/SEMI_REALISTIC/PBR_REALISTIC/AAA) |
| Outlines | `blender_outline_effect` (SOLIDIFY/FREESTYLE/GREASE_PENCIL) |
| Baking | `blender_bake_maps` (NORMAL/AO/CURVATURE/DIFFUSE/ROUGHNESS/COMBINED) |
| Advanced Mesh | `blender_mesh_edit_advanced`, `blender_mesh_edge_mark`, `blender_mesh_select_by_trait`, `blender_vertex_group`, `blender_vertex_color` |

### Skill: character (~23 tools)

**Activate**: `blender_activate_skill("character")`

Character templates, bone rigging, auto-rigging tools.

### Skill: animation (~17 tools)

**Activate**: `blender_activate_skill("animation")`

Keyframe insertion, animation presets, timeline management.

### Skill: scene_setup (~18 tools)

**Activate**: `blender_activate_skill("scene_setup")`

Lighting (point/sun/spot/area), camera control, world environment, render settings.

### Skill: physics (~18 tools)

**Activate**: `blender_activate_skill("physics")`

Rigid body, cloth, fluid simulation, constraints.

### Skill: batch_assets (~11 tools)

**Activate**: `blender_activate_skill("batch_assets")`

Batch operations, asset library management.

### Skill: advanced_3d (~32 tools)

**Activate**: `blender_activate_skill("advanced_3d")`

Shader nodes, compositor, sculpting, texture painting.

### Skill: sport_character (~7 tools)

**Activate**: `blender_activate_skill("sport_character")`

Sport character modeling and equipment.

### Skill: training (~11 tools)

**Activate**: `blender_activate_skill("training")`

Interactive Blender learning courses and project-based tutorials.

---

## Error Handling

All tools return results in this format:

**Success**:
```json
{
  "success": true,
  "result": "Created CUBE 'MyCube' at [0, 0, 0]"
}
```

**Error**:
```json
{
  "success": false,
  "error": "Object 'NonExistent' not found"
}
```

## Universal Fallback

`blender_execute_python` can execute any Blender Python API call. Use it for operations not covered by dedicated tools:

```python
import bpy
obj = bpy.data.objects['Cube']
obj.modifiers.new('MyMod', 'SUBSURF')
obj.modifiers['MyMod'].levels = 3
```
