# Blender MCP Architecture

## Overview

Blender MCP implements the [Model Context Protocol](https://modelcontextprotocol.io/) to bridge AI assistants and Blender. It consists of two main components: an **MCP Server** (Python) and a **Blender Addon** (Python/Blender API).

```
┌──────────────┐     MCP Protocol      ┌──────────────┐    Socket/TCP    ┌──────────┐
│   AI IDE     │ ◄──── stdio ────────► │  MCP Server  │ ◄────────────► │  Blender │
│ (Cursor,     │   tools/list          │  (FastMCP)   │   JSON-RPC     │  Addon   │
│  Windsurf)   │   tools/call          │              │                │          │
└──────────────┘                        └──────────────┘                └──────────┘
```

## System Architecture

### Component Diagram

```
blender-mcp/
├── src/blender_mcp/          # MCP Server (runs as a separate process)
│   ├── server.py             # BlenderMCPServer — main entry point
│   ├── connection.py         # BlenderConnection — TCP socket to Blender
│   ├── skill_manager.py      # SkillManager — dynamic tool loading
│   ├── tools_config.py       # Profile-based tool configuration
│   └── tools/                # MCP tool definitions (grouped by module)
│       ├── scene.py          # Scene management tools
│       ├── object.py         # Object CRUD tools
│       ├── modeling.py       # Mesh editing & modifiers
│       ├── material.py       # Material system
│       ├── skills.py         # Skill meta-tools (list/activate/deactivate)
│       └── ...               # 25+ tool modules
│
├── addon/blender_mcp_addon/  # Blender Addon (runs inside Blender)
│   ├── __init__.py           # Addon registration
│   ├── server.py             # TCP server (listens for MCP commands)
│   ├── executor.py           # Command dispatcher
│   ├── handlers/             # Command handlers (execute Blender API calls)
│   │   ├── scene.py
│   │   ├── object.py
│   │   ├── modeling.py
│   │   └── ...
│   ├── operators/            # Blender operators
│   ├── panels/               # UI panels
│   └── utils/                # Utilities
```

### Data Flow

```
User → AI IDE → MCP Server → Blender Addon → Blender API → Result
                                                              ↓
User ← AI IDE ← MCP Server ← Blender Addon ← JSON Response ←┘
```

1. **User** sends natural language request to AI in IDE
2. **AI** selects appropriate MCP tool(s) and calls them
3. **MCP Server** receives tool call, formats command, sends to Blender via TCP
4. **Blender Addon** receives command, dispatches to handler, executes Blender Python API
5. **Result** flows back through the chain as JSON

## MCP Server

### BlenderMCPServer

The main server class (`server.py`) manages:

- **FastMCP instance** — Handles MCP protocol (stdio transport)
- **BlenderConnection** — TCP socket to Blender addon (lazy initialization)
- **SkillManager** — Dynamic tool loading/unloading (lazy initialization)
- **Tool registration** — Loads tool modules based on configured profile

```python
class BlenderMCPServer:
    def __init__(self, name="Blender MCP", blender_host="127.0.0.1", blender_port=9876):
        self.mcp = FastMCP(name)
        self._connection = None      # Lazy: BlenderConnection
        self._skill_manager = None   # Lazy: SkillManager
        self._register_tools()       # Load tools based on TOOL_PROFILE
```

### Tool Modules

Each tool module follows a consistent pattern:

```python
# tools/example.py
from pydantic import BaseModel, Field

class ExampleInput(BaseModel):
    name: str = Field(..., description="Object name")

def register_example_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    @mcp.tool()
    async def blender_example_action(params: ExampleInput) -> str:
        result = await server.execute_command("category", "action", params.model_dump())
        return format_result(result)
```

### Tool Configuration (Profiles)

`tools_config.py` defines which modules are loaded at startup:

| Profile | Modules | Tools | Use Case |
|---------|---------|-------|----------|
| `skill` | 5 (core + skills) | ~31 | Recommended: on-demand loading |
| `minimal` | 4 (core only) | ~28 | Minimum viable set |
| `focused` | 12 | ~82 | Static, curated set |
| `standard` | 20 | ~146 | Most features |
| `full` | 26+ | ~319 | Everything |

## Skill System (Dynamic Tool Loading)

The Skill system reduces initial context window usage by loading tools on demand.

### Architecture

```
Startup: Load CORE_MODULES + skills module → ~31 tools
         ├── scene (6 tools)
         ├── object (12 tools)
         ├── utility (7 tools)
         ├── export (3 tools)
         └── skills (3 meta-tools)

Runtime: AI calls activate_skill("modeling")
         → SkillManager dynamically imports modeling/curves/uv_mapping modules
         → FastMCP.add_tool() registers each tool
         → Server sends tools/list_changed notification
         → Client refreshes tool list
         → AI now has +38 modeling tools available

         AI calls deactivate_skill("modeling")
         → FastMCP.remove_tool() for each registered tool
         → Server sends tools/list_changed notification
         → Tools removed, context freed
```

### Skill Definitions

11 skill groups covering all functionality:

| Skill | Tools | Modules |
|-------|-------|---------|
| modeling | ~38 | modeling, curves, uv_mapping |
| materials | ~17 | material, procedural_materials |
| style | ~8 | style_presets, mesh_edit_advanced |
| character | ~23 | character_templates, rigging, auto_rig |
| animation | ~17 | animation, animation_presets |
| scene_setup | ~18 | lighting, camera, world, render |
| physics | ~18 | physics, constraints |
| batch_assets | ~11 | batch, assets |
| advanced_3d | ~32 | nodes, compositor, sculpting, texture_painting |
| sport_character | ~7 | sport_character |
| training | ~11 | training |

### Key APIs Used

```python
# Dynamic tool management (FastMCP)
mcp.add_tool(fn, name="...", description="...")
mcp.remove_tool("tool_name")

# Client notification (MCP Protocol)
await ctx.session.send_tool_list_changed()
```

## Blender Addon

### TCP Server

The addon runs a TCP server inside Blender (default port 9876) that:

1. Listens for JSON-RPC commands from the MCP server
2. Dispatches commands to the appropriate handler
3. Returns JSON results

### Command Dispatcher

`executor.py` routes commands by category:

```python
HANDLER_MAP = {
    "scene": scene_handler,
    "object": object_handler,
    "modeling": modeling_handler,
    "material": material_handler,
    # ... more handlers
}
```

### Handlers

Each handler executes Blender Python API calls:

```python
# handlers/object.py
def handle(action: str, params: dict) -> dict:
    if action == "create":
        return _create_object(params)
    elif action == "delete":
        return _delete_object(params)
    # ...
```

## Communication Protocol

### MCP Server ↔ Blender Addon

JSON-RPC over TCP socket:

```json
// Request (MCP Server → Blender)
{
    "category": "object",
    "action": "create",
    "params": {"type": "CUBE", "name": "MyCube", "location": [0, 0, 0]}
}

// Response (Blender → MCP Server)
{
    "success": true,
    "result": "Created CUBE 'MyCube' at [0, 0, 0]"
}
```

### MCP Server ↔ AI IDE

Standard MCP protocol over stdio:

- `tools/list` — List available tools
- `tools/call` — Execute a tool
- `notifications/tools/list_changed` — Dynamic tool updates

## Design Decisions

### Composite Tools over Atomic Tools

10 composite tools replace 58 atomic tools to prevent AI tool selection confusion:

```
Before: create_cube, create_sphere, create_cylinder, ... (20 tools)
After:  blender_object_create(type="CUBE|SPHERE|CYLINDER|...") (1 tool)
```

### Lazy Initialization

Both `BlenderConnection` and `SkillManager` use lazy initialization to avoid startup overhead and circular imports.

### Profile-Based Loading

Multiple profiles allow the same codebase to serve different use cases without code changes — just a config switch.

## Extension Guide

### Adding a New Tool Module

1. Create `src/blender_mcp/tools/my_module.py` with `register_my_module_tools(mcp, server)`
2. Create `addon/blender_mcp_addon/handlers/my_module.py` with `handle(action, params)`
3. Register in `tools_config.py` → `MODULE_REGISTRY`
4. Register handler in `addon/blender_mcp_addon/executor.py`
5. Add to appropriate profile or skill definition

### Adding a New Skill

Edit `skill_manager.py` → `SKILL_DEFINITIONS`:

```python
"my_skill": SkillInfo(
    name="my_skill",
    description="Description for AI to understand",
    modules=["my_module_a", "my_module_b"],
    estimated_tools=15,
    workflow_guide="## My Skill Workflow\n...",
),
```
