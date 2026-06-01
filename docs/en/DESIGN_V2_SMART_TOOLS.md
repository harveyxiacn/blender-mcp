# Design Document: Blender MCP Smart Tools v2

**Date:** 2026-03-17
**Status:** Implementation Ready

## Overview

This document describes 5 new feature areas that transform Blender MCP from a "bag of tools" into an intelligent Blender copilot. Each feature is designed to follow existing project patterns exactly.

---

## Feature 1: Viewport Snapshot (`snapshot`)

### Motivation
Multimodal AI clients (Claude, GPT-4o) can analyze images. A viewport screenshot lets the AI **see** the scene and give visual feedback — the single most impactful feature for user satisfaction.

### MCP Tools
| Tool | Description | ReadOnly |
|------|-------------|----------|
| `blender_snapshot_viewport` | Capture the 3D viewport to a PNG file and return the path | Yes |
| `blender_snapshot_render_preview` | Quick render at reduced resolution and return path | Yes |

### Addon Handler: `handlers/snapshot.py`
- `handle_viewport(params)` — Uses `bpy.ops.screen.screenshot_area()` or `gpu` offscreen rendering to capture the active 3D viewport.
- `handle_render_preview(params)` — Temporarily overrides render resolution to `params.width` (default 512), renders, saves to temp file, restores settings.

### Parameters
```python
class SnapshotViewportInput(BaseModel):
    width: int = Field(default=800, description="Image width in pixels", ge=64, le=3840)
    height: int = Field(default=600, description="Image height in pixels", ge=64, le=2160)
    output_path: str | None = Field(default=None, description="Output file path (auto-generated if omitted)")

class SnapshotRenderPreviewInput(BaseModel):
    width: int = Field(default=512, description="Preview render width", ge=64, le=1920)
    samples: int = Field(default=16, description="Render samples (lower=faster)", ge=1, le=128)
    output_path: str | None = Field(default=None, description="Output file path")
```

### Response
```json
{"success": true, "data": {"path": "/tmp/blender_snapshot_20260317_143022.png", "width": 800, "height": 600}}
```

---

## Feature 2: Scene Describe & Hierarchy (`describe`)

### Motivation
AI assistants need to **understand** the current scene before giving advice. Currently they must call multiple tools and piece together the picture. A single `describe` tool returns a structured summary.

### MCP Tools
| Tool | Description | ReadOnly |
|------|-------------|----------|
| `blender_describe_scene` | Return a structured summary of the entire scene | Yes |
| `blender_describe_hierarchy` | Return the full parent-child object tree | Yes |
| `blender_describe_object` | Deep inspection of a single object (topology, materials, modifiers, constraints) | Yes |

### Addon Handler: `handlers/describe.py`
- `handle_scene(params)` — Iterates `bpy.data.objects`, `bpy.data.materials`, `bpy.data.lights`, `bpy.data.cameras`, collects counts and names, render settings, frame range.
- `handle_hierarchy(params)` — Builds parent-child tree from `obj.parent` relationships, returns as nested dict or indented text.
- `handle_object(params)` — For a given object: mesh stats (verts/edges/faces/ngons), material slots, modifier stack, constraints, parent chain, bounding box.

### Response Example (scene)
```json
{
  "success": true,
  "data": {
    "scene_name": "Scene",
    "object_count": 12,
    "objects_by_type": {"MESH": 8, "LIGHT": 2, "CAMERA": 1, "EMPTY": 1},
    "materials": ["Metal.001", "Wood.002"],
    "lights": [{"name": "Sun", "type": "SUN", "energy": 5.0}],
    "camera": {"name": "Camera", "lens": 50.0},
    "render": {"engine": "CYCLES", "resolution": [1920, 1080], "samples": 128},
    "frame_range": [1, 250],
    "summary": "Scene has 12 objects (8 meshes, 2 lights, 1 camera, 1 empty), 2 materials, rendering with Cycles at 1920x1080."
  }
}
```

---

## Feature 3: Checkpoint Save/Restore (`checkpoint`)

### Motivation
When the AI makes a bad change, there's no structured rollback. Named checkpoints provide undo safety net, dramatically improving user trust.

### MCP Tools
| Tool | Description | ReadOnly |
|------|-------------|----------|
| `blender_checkpoint_save` | Save a named checkpoint (file-based snapshot) | No |
| `blender_checkpoint_restore` | Restore a previously saved checkpoint | No |
| `blender_checkpoint_list` | List all available checkpoints | Yes |
| `blender_checkpoint_delete` | Delete a checkpoint | No |

### Addon Handler: `handlers/checkpoint.py`
- `handle_save(params)` — Calls `bpy.ops.wm.save_as_mainfile(filepath=checkpoint_path, copy=True)` to save a .blend copy to a `_mcp_checkpoints/` temp directory. Records metadata (name, timestamp, object count).
- `handle_restore(params)` — Calls `bpy.ops.wm.open_mainfile(filepath=checkpoint_path)` to restore.
- `handle_list(params)` — Scans checkpoint directory, returns list with metadata.
- `handle_delete(params)` — Removes checkpoint file.

### Parameters
```python
class CheckpointSaveInput(BaseModel):
    name: str = Field(..., description="Checkpoint name", min_length=1, max_length=100)
    description: str | None = Field(default=None, description="Optional description of scene state")

class CheckpointRestoreInput(BaseModel):
    name: str = Field(..., description="Checkpoint name to restore")
```

---

## Feature 4: Rich Error Suggestions (`error_suggestions`)

### Motivation
Errors currently return raw messages. Adding a `suggestion` field turns failures into guided next-steps, reducing user frustration.

### Implementation Approach
This is NOT a new tool module. Instead, it's a **utility module** that enhances the addon executor.

### Addon: `handlers/error_suggestions.py`
A mapping of error patterns to suggestion strings:

```python
SUGGESTIONS = {
    "OBJECT_NOT_FOUND": "Use 'blender_describe_scene' to list all objects in the scene.",
    "MATERIAL_NOT_FOUND": "Use 'blender_describe_scene' to see available materials.",
    "MODIFIER_ERROR": "Check that the target object is a mesh. Use 'blender_describe_object' to inspect it.",
    "INVALID_ENUM": "Check the API reference for valid enum values.",
    "CONNECTION_LOST": "Ensure Blender is running and the MCP addon is enabled.",
    ...
}

def enrich_error(result: dict) -> dict:
    """Add suggestion field to error responses."""
    if not result.get("success") and "error" in result:
        code = result["error"].get("code", "")
        result["error"]["suggestion"] = SUGGESTIONS.get(code, "Try 'blender_describe_scene' to understand the current scene state.")
    return result
```

### Integration Point
In `executor.py`, wrap the return of `execute()` with `enrich_error()`.

---

## Feature 5: High-Level Compound Tools (`quick`)

### Motivation
Users want to say "set up a product shot" and have it just work. Compound tools chain multiple operations into single high-value actions.

### MCP Tools
| Tool | Description | ReadOnly |
|------|-------------|----------|
| `blender_quick_product_shot` | Set up complete product visualization (3-point lighting, camera, background) | No |
| `blender_quick_turntable` | Create a turntable animation for an object | No |
| `blender_quick_scene_setup` | One-click scene setup with lighting and camera for a given style | No |

### Addon Handler: `handlers/quick.py`

**`handle_product_shot(params)`**:
1. Clear default objects (optional)
2. Create backdrop plane (scaled, with matte material)
3. Create 3-point lighting (key, fill, rim lights)
4. Position camera looking at target object
5. Set render settings (transparent background option)
6. Return summary of created objects

**`handle_turntable(params)`**:
1. Create empty at object's origin
2. Parent object to empty (keep transform)
3. Add keyframes: empty rotation Z from 0 to 360 over `frames` count
4. Set frame range
5. Return animation summary

**`handle_scene_setup(params)`**:
1. Accept a `style` parameter (studio, outdoor, dramatic, minimal)
2. Create appropriate lighting rig
3. Position camera
4. Set world background
5. Configure render settings for the style

### Parameters
```python
class QuickProductShotInput(BaseModel):
    target_object: str | None = Field(default=None, description="Object name to focus on (uses active object if omitted)")
    style: str = Field(default="studio", description="Lighting style: studio, dramatic, soft, outdoor")
    background_color: list[float] | None = Field(default=None, description="Background RGB [0-1, 0-1, 0-1]")
    render_width: int = Field(default=1920, description="Render width")
    render_height: int = Field(default=1080, description="Render height")

class QuickTurntableInput(BaseModel):
    target_object: str | None = Field(default=None, description="Object to animate")
    frames: int = Field(default=120, description="Total frames for full rotation", ge=24, le=1000)
    axis: str = Field(default="Z", description="Rotation axis: X, Y, or Z")

class QuickSceneSetupInput(BaseModel):
    style: str = Field(default="studio", description="Scene style: studio, outdoor, dramatic, minimal")
    clear_scene: bool = Field(default=False, description="Remove existing objects first")
```

---

## File Inventory

### New MCP Tool Modules (`src/blender_mcp/tools/`)
| File | Register Function | Tools |
|------|-------------------|-------|
| `snapshot.py` | `register_snapshot_tools` | 2 |
| `describe.py` | `register_describe_tools` | 3 |
| `checkpoint.py` | `register_checkpoint_tools` | 4 |
| `quick.py` | `register_quick_tools` | 3 |

### New Addon Handlers (`addon/blender_mcp_addon/handlers/`)
| File | Actions |
|------|---------|
| `snapshot.py` | `handle_viewport`, `handle_render_preview` |
| `describe.py` | `handle_scene`, `handle_hierarchy`, `handle_object` |
| `checkpoint.py` | `handle_save`, `handle_restore`, `handle_list`, `handle_delete` |
| `quick.py` | `handle_product_shot`, `handle_turntable`, `handle_scene_setup` |
| `error_suggestions.py` | `enrich_error()` utility (not a handler) |

### Modified Files
| File | Change |
|------|--------|
| `src/blender_mcp/tools_config.py` | Add 4 modules to `MODULE_REGISTRY` and profiles |
| `addon/blender_mcp_addon/handlers/__init__.py` | Add 4 entries to `HANDLER_MODULES` |
| `addon/blender_mcp_addon/executor.py` | Integrate `enrich_error()` in `execute()` return path |
| `tests/test_parity.py` | Verify new modules (automatic via existing test) |

### New Test Files
| File | Purpose |
|------|---------|
| `tests/test_new_tools.py` | Unit tests for new tool module imports and registration |
| `tests/run_demo.py` | Live demo script that creates scenes using all new features |

---

## Demo Scenes

The `tests/run_demo.py` script will create these demo scenes in Blender:

1. **Product Shot Demo** — Creates a monkey head with metallic material, uses `quick_product_shot` to set up studio lighting and camera, captures viewport snapshot.

2. **Turntable Demo** — Creates a torus with glass material, uses `quick_turntable` for 120-frame spin animation.

3. **Scene Describe Demo** — Builds a multi-object scene, then calls `describe_scene`, `describe_hierarchy`, and `describe_object` to show the full readout.

4. **Checkpoint Demo** — Creates objects, saves checkpoint, makes destructive changes, restores checkpoint to prove rollback works.
