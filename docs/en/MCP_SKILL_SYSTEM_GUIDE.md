# MCP Skill System — On-Demand Tool Loading Guide

> **Applicable to**: Any MCP Server with 30+ tools  
> **Core benefit**: Reduce tool schema overhead by 60-80% at startup, saving AI Context Window  
> **Verified**: Tested in Blender MCP (100 tools → 31 startup + on-demand loading)

---

## 1. Problem Background

### Why Do You Need a Skill System?

Every tool registered by an MCP Server is sent to the AI client as a JSON Schema. When tool count grows large:

| Tool Count | Estimated Schema Tokens | Issue |
|------------|------------------------|-------|
| 30 | ~5-8K tokens | ✅ Acceptable |
| 80 | ~15-25K tokens | ⚠️ Squeezes available context |
| 200+ | ~40-60K tokens | ❌ Wasteful, AI selection accuracy drops |

**Skill system solution**: Register only core tools + a few meta-tools at startup. AI loads/unloads tool groups on demand.

```
Traditional: Startup → Register all 100 tools → AI faces 100 choices
Skill mode:  Startup → Register 31 core tools → AI loads on demand → Unloads when done
```

---

## 2. Technical Feasibility

### 2.1 MCP Protocol Support

The MCP protocol natively supports dynamic tool changes:

```
Server → Client: notifications/tools/list_changed
Client receives → Re-calls tools/list → Gets updated tool list
```

### 2.2 FastMCP SDK Support

FastMCP (Python MCP SDK) provides complete runtime tool management APIs:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

# ✅ Add tools at runtime
mcp.add_tool(my_function, name="tool_name", description="...")

# ✅ Remove tools at runtime
mcp.remove_tool("tool_name")

# ✅ Notify client from within a tool handler (via Context)
@mcp.tool()
async def activate_skill(name: str, ctx: Context) -> str:
    mcp.add_tool(...)
    await ctx.session.send_tool_list_changed()
```

**Internal implementation**: `ToolManager._tools` is a `dict[str, Tool]` — add/remove are dictionary operations, runtime-safe.

### 2.3 Client Compatibility

| Client | tools/list_changed | Notes |
|--------|-------------------|-------|
| Windsurf | ✅ Verified | Auto-refreshes tool list on notification |
| Cursor | ✅ Expected | Based on MCP standard protocol |
| Claude Desktop | ✅ Expected | Anthropic's official client |
| Custom clients | ⚠️ Must implement | Need to listen for `notifications/tools/list_changed` |

---

## 3. Architecture Design

### 3.1 Overall Architecture

```
┌─────────────────────────────────────────────┐
│                 MCP Client (AI)              │
│                                              │
│  1. list_skills()         → View skills      │
│  2. activate_skill("X")   → Load tool group  │
│  3. Use newly loaded tools                   │
│  4. deactivate_skill("X") → Unload tools     │
└──────────────────┬──────────────────────────┘
                   │ MCP Protocol
┌──────────────────▼──────────────────────────┐
│              MCP Server                      │
│                                              │
│  Registered at startup:                      │
│  ├── Core tools (always available)           │
│  └── Skill meta-tools (3):                   │
│      ├── list_skills                         │
│      ├── activate_skill                      │
│      └── deactivate_skill                    │
│                                              │
│  Dynamically registered/removed:             │
│  ├── Skill A tool group (on demand)          │
│  ├── Skill B tool group (on demand)          │
│  └── ...                                     │
│                                              │
│  ┌──────────────┐  ┌─────────────────────┐   │
│  │ SkillManager │  │ FastMCP ToolManager │   │
│  │              │──│ add_tool()          │   │
│  │ activate()   │  │ remove_tool()       │   │
│  │ deactivate() │  │ list_tools()        │   │
│  └──────────────┘  └─────────────────────┘   │
└──────────────────────────────────────────────┘
```

### 3.2 Core Components

| Component | Responsibility | Key API |
|-----------|---------------|---------|
| **SkillManager** | Manage skill lifecycle, track active state | `activate()`, `deactivate()`, `is_active()` |
| **SkillInfo** | Skill metadata (description, modules, workflow guide) | Dataclass |
| **Skill meta-tools** | MCP tool interface exposed to AI | `list_skills`, `activate_skill`, `deactivate_skill` |
| **Tool modules** | Tool code grouped by skill | Each module has a `register_xxx_tools()` function |

---

## 4. Implementation Steps

### Step 1: Define Skill Metadata

```python
# skill_manager.py
from dataclasses import dataclass, field

@dataclass
class SkillInfo:
    name: str                    # Unique skill identifier
    description: str             # AI-readable description
    modules: list[str]           # Corresponding tool module names
    workflow_guide: str = ""     # Workflow text (returned on activation)
    estimated_tools: int = 0     # Estimated tool count
    tags: list[str] = field(default_factory=list)
```

### Step 2: Build Skill Registry

Group tool modules by functional domain:

```python
SKILL_DEFINITIONS: dict[str, SkillInfo] = {
    "modeling": SkillInfo(
        name="modeling",
        description="3D modeling tools - mesh editing, modifiers, curves",
        modules=["modeling", "curves", "uv_mapping"],
        estimated_tools=38,
        workflow_guide="""
## Modeling Workflow Guide
1. Create base geometry → Add modifiers → Apply
2. Curve modeling: Create path → Add Curve modifier
""",
    ),
    # ... more skills
}
```

**Grouping principles**:
- **Functional cohesion**: Tools from the same workflow go together
- **5-40 tools per skill**: Too few = not worth isolating; too many = defeats the purpose
- **Independent**: Skills should not depend on each other
- **Intuitive naming**: AI should guess functionality from the name

### Step 3: Implement SkillManager

```python
class SkillManager:
    def __init__(self, server):
        self.server = server
        self._active_skills: dict[str, list[str]] = {}  # skill_name → [tool_names]
    
    def activate_skill(self, skill_name: str) -> tuple[bool, str, list[str]]:
        skill_info = SKILL_DEFINITIONS[skill_name]
        registered_tools = []
        
        for module_name in skill_info.modules:
            before = set(t.name for t in server.mcp._tool_manager.list_tools())
            
            tool_module = importlib.import_module(f"mypackage.tools.{module_name}")
            register_func = getattr(tool_module, f"register_{module_name}_tools")
            register_func(server.mcp, server)
            
            after = set(t.name for t in server.mcp._tool_manager.list_tools())
            registered_tools.extend(after - before)
        
        self._active_skills[skill_name] = registered_tools
        return True, f"Activated {skill_name}", registered_tools
    
    def deactivate_skill(self, skill_name: str) -> tuple[bool, str]:
        for tool_name in self._active_skills[skill_name]:
            self.server.mcp.remove_tool(tool_name)
        del self._active_skills[skill_name]
        return True, f"Deactivated {skill_name}"
```

### Step 4: Implement Skill MCP Meta-Tools

```python
# tools/skills.py
from mcp.server.fastmcp import FastMCP, Context

def register_skill_tools(mcp: FastMCP, server) -> None:
    
    @mcp.tool()
    async def list_skills() -> str:
        """List all available skills and their activation status."""
        return server.skill_manager.get_status_summary()
    
    @mcp.tool()
    async def activate_skill(skill_name: str, ctx: Context) -> str:
        """Activate a skill to dynamically load its tool group."""
        success, message, tools = server.skill_manager.activate_skill(skill_name)
        if success:
            await ctx.session.send_tool_list_changed()  # Key: notify client
        workflow = SKILL_DEFINITIONS[skill_name].workflow_guide
        return f"{message}\n\nRegistered: {', '.join(tools)}\n\n{workflow}"
    
    @mcp.tool()
    async def deactivate_skill(skill_name: str, ctx: Context) -> str:
        """Deactivate a skill, removing its tools to free up context."""
        success, message = server.skill_manager.deactivate_skill(skill_name)
        if success:
            await ctx.session.send_tool_list_changed()
        return message
```

### Step 5: Configure Startup Profile

```python
# tools_config.py
TOOL_PROFILE = "skill"  # Recommended

CORE_MODULES = ["scene", "object", "utility", "export"]
SKILL_MODULES = CORE_MODULES + ["skills"]

def get_enabled_modules():
    if TOOL_PROFILE == "skill":
        return SKILL_MODULES       # ~31 tools
    elif TOOL_PROFILE == "full":
        return ALL_MODULES          # ~300 tools
```

### Step 6: Server Integration

```python
# server.py
class MyMCPServer:
    def __init__(self):
        self.mcp = FastMCP("my-server")
        self._skill_manager = None
        self._register_tools()
    
    @property
    def skill_manager(self):
        if self._skill_manager is None:
            from mypackage.skill_manager import SkillManager
            self._skill_manager = SkillManager(self)
        return self._skill_manager
```

---

## 5. Best Practices

### Core Tool Selection

Startup core tools should be:
1. **High frequency** — Needed for almost every task
2. **Basic operations** — View, list, basic CRUD
3. **Universal fallback** — e.g., `execute_python`/`execute_script`
4. **Count limit** — No more than 30 core tools

### Multiple Skills in Parallel

```python
activate_skill("modeling")    # +38 tools
activate_skill("materials")   # +17 tools
# Now: 31 + 38 + 17 = 86 tools

deactivate_skill("modeling")
deactivate_skill("materials")
# Back to 31
```

### Workflow Guides

Each skill should include a concise workflow guide (200-400 words) that tells the AI:
- Common workflows with specific tool names
- Key parameters and recommended values
- Tips and fallback options

---

## 6. Measured Results

### Blender MCP Test Data

| Metric | Traditional (focused) | Skill Mode | Improvement |
|--------|----------------------|------------|-------------|
| Startup tools | 100 | 31 | **-69%** |
| Schema tokens | ~20K | ~6K | **-70%** |
| Tool selection accuracy | Average | High | Fewer choices |
| Feature completeness | 100% | 100% | No loss |

---

## 7. When to Use

### Good Fit
- ✅ 30+ tools total
- ✅ Tools group naturally by domain
- ✅ Different tasks use different tool subsets
- ✅ Context window is a bottleneck

### Not a Good Fit
- ❌ Fewer than 20 tools (just load them all)
- ❌ All tools needed every time
- ❌ Client doesn't support `tools/list_changed`

### Alternatives
1. **Composite tools**: Merge small tools into parameterized larger ones
2. **Script fallback**: Keep a universal `execute_script` tool
3. **Static profiles**: Preset tool sets chosen at startup

---

## Quick Checklist

- [ ] Confirm MCP SDK supports `add_tool()` / `remove_tool()` / `send_tool_list_changed()`
- [ ] Group tools by domain, define skill metadata
- [ ] Identify core tool set (always loaded, ≤30)
- [ ] Implement `SkillManager` class
- [ ] Implement 3 skill meta-tools (list/activate/deactivate)
- [ ] Write workflow guide for each skill
- [ ] Add `"skill"` profile to config
- [ ] Add `skill_manager` property to server class
- [ ] Test full flow: list → activate → use tools → deactivate
- [ ] Verify client responds to `tools/list_changed`
