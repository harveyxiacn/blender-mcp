# Blender MCP Quick Start Guide

## Introduction

Get started with Blender MCP in 5 minutes. Control Blender through natural language conversations with AI.

## Prerequisites

- Blender 4.0+ installed ([download](https://www.blender.org/download/)), 5.0+ recommended
- Python 3.10+
- An MCP-compatible IDE (Cursor, Windsurf, etc.)

## Installation

### 1. Install the MCP Server

```bash
# Using uv (recommended)
uv pip install blender-mcp

# Or using pip
pip install blender-mcp
```

### 2. Install the Blender Addon

```bash
# Auto-install
python -m blender_mcp install-addon

# Or build manually
python build_addon.py
# Then in Blender: Edit → Preferences → Add-ons → Install → select dist/blender_mcp_addon.zip
```

### 3. Configure Your IDE

**Cursor** — create `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/blender-mcp", "blender-mcp"]
    }
  }
}
```

**Windsurf** — add via MCP settings panel, same command and args.

### 4. Launch Blender

Open Blender, find the "MCP" panel in the sidebar (N key), confirm the server status shows "Running".

## Your First Session

Send this to the AI assistant in your IDE:

```
Create a simple scene in Blender:
1. Delete the default cube
2. Create a sphere
3. Add a red metallic material to the sphere
4. Add a point light to illuminate the scene
```

The AI will automatically call Blender MCP tools to execute each step.

## Skill System (On-Demand Tool Loading)

Blender MCP uses a **Skill system** to manage 200+ tools efficiently. On startup, only ~31 core tools are loaded. Additional tools are loaded on demand.

```
AI: list_skills()                    → See 11 available skill groups
AI: activate_skill("modeling")       → Load 38 modeling tools
AI: (perform modeling tasks)
AI: deactivate_skill("modeling")     → Unload to free context
AI: activate_skill("materials")      → Load 17 material tools
```

### Available Skills

| Skill | Tools | Description |
|-------|-------|-------------|
| modeling | ~38 | Mesh editing, modifiers, curves, UV mapping |
| materials | ~17 | Standard & procedural materials (67 presets), wear effects |
| style | ~8 | Pixel→AAA style presets, outlines, baking |
| character | ~23 | Character templates, rigging, auto-rig |
| animation | ~17 | Keyframes, animation presets, timeline |
| scene_setup | ~18 | Lighting, camera, world, render settings |
| physics | ~18 | Rigid body, cloth, fluid, constraints |
| batch_assets | ~11 | Batch operations, asset management |
| advanced_3d | ~32 | Nodes, compositor, sculpting, texture painting |
| sport_character | ~7 | Sport character modeling |
| training | ~11 | Interactive Blender learning courses |

## Common Examples

### Create Objects
```
Create a cylinder at position (2, 0, 0) in Blender
```

### Modify Materials
```
Change Cube's material to a blue glass effect
```

### Create Animation
```
Create a bouncing animation for Sphere, lasting 60 frames
```

### Render Setup
```
Set render resolution to 1920x1080, use Cycles engine, render an image
```

## Troubleshooting

### Can't connect to Blender?
1. Ensure Blender is running
2. MCP addon is enabled
3. Server status shows "Running"

### Command execution failed?
1. Check Blender's system console for errors
2. Check IDE terminal for MCP server logs

### Enable verbose logging
```bash
python -m blender_mcp --log-level DEBUG
```

## Next Steps

- [Installation Guide](./INSTALLATION.md) — Detailed setup instructions
- [Architecture](./ARCHITECTURE.md) — System design and internals
- [API Reference](./API_REFERENCE.md) — Complete tool documentation
- [Tutorials](./TUTORIALS.md) — Step-by-step project guides
- [Skill System Guide](./MCP_SKILL_SYSTEM_GUIDE.md) — Dynamic tool loading
- [Contributing](./CONTRIBUTING.md) — How to contribute
