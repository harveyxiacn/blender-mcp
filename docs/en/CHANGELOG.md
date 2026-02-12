# Changelog

All notable changes to Blender MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-02-11

### Added

- **Skill System (Dynamic Tool Loading)**
  - `SkillManager` for on-demand tool group activation/deactivation
  - 3 meta-tools: `blender_list_skills`, `blender_activate_skill`, `blender_deactivate_skill`
  - 11 skill groups covering all 200+ tools
  - `tools/list_changed` MCP notification for client-side refresh
  - Workflow guides returned on skill activation
  - New `"skill"` tool profile (recommended, ~31 startup tools)

- **Advanced Mesh Editing** (5 tools)
  - `blender_mesh_edit_advanced` — inset, bridge, spin, knife, fill, symmetrize, etc.
  - `blender_mesh_edge_mark` — crease, sharp, seam, bevel weight
  - `blender_mesh_select_by_trait` — non-manifold, loose, boundary, etc.
  - `blender_vertex_group` — vertex group management
  - `blender_vertex_color` — vertex color painting

- **Style Presets** (3 tools)
  - `blender_style_setup` — one-click style config (Pixel → AAA, 8 presets)
  - `blender_outline_effect` — outline via Solidify/Freestyle/Grease Pencil
  - `blender_bake_maps` — high-to-low poly baking workflow

- **Procedural Materials** (2 tools)
  - `blender_procedural_material` — 67 presets across 8 categories
  - `blender_material_wear` — wear effects (edge wear, scratches, rust, dirt, etc.)

- **Enhanced Object Creation**
  - `mesh_params` support for parametric mesh creation (segments, radius, depth, etc.)
  - Full control for all mesh primitive types

- **Expanded Modifier Support**
  - 45 modifier types (up from 12)
  - Added: Screw, Wireframe, Weld, Remesh, Build, Multires, Cast, Curve, Lattice, and more

### Changed

- Default `TOOL_PROFILE` changed from `"focused"` to `"skill"`
- Startup tool count reduced from ~100 to ~31 (69% reduction)

## [0.1.0] - 2026-01-15

### Added

- Initial release
- MCP Server with FastMCP framework
- Blender Addon with TCP server
- Core tool modules: scene, object, modeling, material, lighting, camera, animation, render, utility, export
- Extended modules: character templates, rigging, auto-rig, physics, constraints, nodes, compositor, sculpting, texture painting, batch, assets, animation presets, world, versioning, AI generation, VR/AR, Substance, ZBrush, cloud render, collaboration, training
- Multi-IDE support: Cursor, Windsurf, Claude Desktop
- Hot reload for addon development
- Tool profiles: minimal, focused, standard, full
