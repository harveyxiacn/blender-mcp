# Blender MCP 架构设计

## 概述

Blender MCP 实现了 [Model Context Protocol](https://modelcontextprotocol.io/)，在 AI 助手和 Blender 之间架起桥梁。由两个主要组件构成：**MCP 服务器**（Python）和 **Blender 插件**（Python/Blender API）。

```
┌──────────────┐     MCP 协议          ┌──────────────┐    Socket/TCP    ┌──────────┐
│   AI IDE     │ ◄──── stdio ────────► │  MCP 服务器  │ ◄────────────► │  Blender │
│ (Cursor,     │   tools/list          │  (FastMCP)   │   JSON-RPC     │  插件    │
│  Windsurf)   │   tools/call          │              │                │          │
└──────────────┘                        └──────────────┘                └──────────┘
```

## 系统架构

### 组件图

```
blender-mcp/
├── src/blender_mcp/          # MCP 服务器（作为独立进程运行）
│   ├── server.py             # BlenderMCPServer — 主入口
│   ├── connection.py         # BlenderConnection — 到 Blender 的 TCP 连接
│   ├── skill_manager.py      # SkillManager — 动态工具加载
│   ├── tools_config.py       # 基于 Profile 的工具配置
│   └── tools/                # MCP 工具定义（按模块分组）
│       ├── scene.py          # 场景管理工具
│       ├── object.py         # 对象 CRUD 工具
│       ├── modeling.py       # 网格编辑与修改器
│       ├── material.py       # 材质系统
│       ├── skills.py         # Skill 元工具（list/activate/deactivate）
│       └── ...               # 25+ 工具模块
│
├── addon/blender_mcp_addon/  # Blender 插件（在 Blender 内运行）
│   ├── __init__.py           # 插件注册
│   ├── server.py             # TCP 服务器（监听 MCP 命令）
│   ├── executor.py           # 命令调度器
│   ├── handlers/             # 命令处理器（执行 Blender API 调用）
│   │   ├── scene.py
│   │   ├── object.py
│   │   ├── modeling.py
│   │   └── ...
│   ├── operators/            # Blender 操作符
│   ├── panels/               # UI 面板
│   └── utils/                # 工具函数
```

### 数据流

```
用户 → AI IDE → MCP 服务器 → Blender 插件 → Blender API → 结果
                                                            ↓
用户 ← AI IDE ← MCP 服务器 ← Blender 插件 ← JSON 响应 ←────┘
```

1. **用户** 在 IDE 中向 AI 发送自然语言请求
2. **AI** 选择合适的 MCP 工具并调用
3. **MCP 服务器** 接收工具调用，格式化命令，通过 TCP 发送到 Blender
4. **Blender 插件** 接收命令，分发到处理器，执行 Blender Python API
5. **结果** 通过链路返回为 JSON

## MCP 服务器

### BlenderMCPServer

主服务器类（`server.py`）管理：

- **FastMCP 实例** — 处理 MCP 协议（stdio 传输）
- **BlenderConnection** — 到 Blender 插件的 TCP 连接（延迟初始化）
- **SkillManager** — 动态工具加载/卸载（延迟初始化）
- **工具注册** — 根据配置的 Profile 加载工具模块

```python
class BlenderMCPServer:
    def __init__(self, name="Blender MCP", blender_host="127.0.0.1", blender_port=9876):
        self.mcp = FastMCP(name)
        self._connection = None      # 延迟：BlenderConnection
        self._skill_manager = None   # 延迟：SkillManager
        self._register_tools()       # 根据 TOOL_PROFILE 加载工具
```

### 工具模块

每个工具模块遵循一致的模式：

```python
# tools/example.py
from pydantic import BaseModel, Field

class ExampleInput(BaseModel):
    name: str = Field(..., description="对象名称")

def register_example_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    @mcp.tool()
    async def blender_example_action(params: ExampleInput) -> str:
        result = await server.execute_command("category", "action", params.model_dump())
        return format_result(result)
```

### 工具配置（Profiles）

`tools_config.py` 定义启动时加载哪些模块：

| Profile | 模块数 | 工具数 | 适用场景 |
|---------|--------|--------|---------|
| `skill` | 5（核心 + skills） | ~31 | 推荐：按需加载 |
| `minimal` | 4（仅核心） | ~28 | 最小可用集 |
| `focused` | 12 | ~82 | 静态精选集 |
| `standard` | 20 | ~146 | 大部分功能 |
| `full` | 26+ | ~319 | 所有功能 |

## Skill 系统（动态工具加载）

Skill 系统通过按需加载工具来减少初始 Context Window 占用。

### 架构

```
启动时：加载 CORE_MODULES + skills 模块 → ~31 个工具
         ├── scene（6 个工具）
         ├── object（12 个工具）
         ├── utility（7 个工具）
         ├── export（3 个工具）
         └── skills（3 个元工具）

运行时：AI 调用 activate_skill("modeling")
         → SkillManager 动态导入 modeling/curves/uv_mapping 模块
         → FastMCP.add_tool() 注册每个工具
         → 服务器发送 tools/list_changed 通知
         → 客户端刷新工具列表
         → AI 现在有 +38 个建模工具可用

         AI 调用 deactivate_skill("modeling")
         → FastMCP.remove_tool() 移除每个已注册的工具
         → 服务器发送 tools/list_changed 通知
         → 工具被移除，上下文释放
```

### Skill 定义

11 个 Skill 组覆盖所有功能：

| Skill | 工具数 | 模块 |
|-------|--------|------|
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

### 关键 API

```python
# 动态工具管理（FastMCP）
mcp.add_tool(fn, name="...", description="...")
mcp.remove_tool("tool_name")

# 客户端通知（MCP 协议）
await ctx.session.send_tool_list_changed()
```

## Blender 插件

### TCP 服务器

插件在 Blender 内运行 TCP 服务器（默认端口 9876）：

1. 监听来自 MCP 服务器的 JSON-RPC 命令
2. 将命令分发到对应的处理器
3. 返回 JSON 结果

### 命令调度器

`executor.py` 按类别路由命令：

```python
HANDLER_MAP = {
    "scene": scene_handler,
    "object": object_handler,
    "modeling": modeling_handler,
    "material": material_handler,
    # ... 更多处理器
}
```

### 处理器

每个处理器执行 Blender Python API 调用：

```python
# handlers/object.py
def handle(action: str, params: dict) -> dict:
    if action == "create":
        return _create_object(params)
    elif action == "delete":
        return _delete_object(params)
    # ...
```

## 通信协议

### MCP 服务器 ↔ Blender 插件

基于 TCP socket 的 JSON-RPC：

```json
// 请求（MCP 服务器 → Blender）
{
    "category": "object",
    "action": "create",
    "params": {"type": "CUBE", "name": "MyCube", "location": [0, 0, 0]}
}

// 响应（Blender → MCP 服务器）
{
    "success": true,
    "result": "Created CUBE 'MyCube' at [0, 0, 0]"
}
```

### MCP 服务器 ↔ AI IDE

标准 MCP 协议，通过 stdio：

- `tools/list` — 列出可用工具
- `tools/call` — 执行工具
- `notifications/tools/list_changed` — 动态工具更新

## 设计决策

### 复合工具替代原子工具

10 个复合工具替代了 58 个原子工具，防止 AI 工具选择混乱：

```
之前：create_cube, create_sphere, create_cylinder, ...（20 个工具）
之后：blender_object_create(type="CUBE|SPHERE|CYLINDER|...")（1 个工具）
```

### 延迟初始化

`BlenderConnection` 和 `SkillManager` 均使用延迟初始化，避免启动开销和循环导入。

### 基于 Profile 的加载

多个 Profile 允许同一代码库服务不同场景——只需修改配置，无需改代码。

## 扩展指南

### 添加新工具模块

1. 创建 `src/blender_mcp/tools/my_module.py`，包含 `register_my_module_tools(mcp, server)`
2. 创建 `addon/blender_mcp_addon/handlers/my_module.py`，包含 `handle(action, params)`
3. 在 `tools_config.py` → `MODULE_REGISTRY` 中注册
4. 在 `addon/blender_mcp_addon/executor.py` 中注册处理器
5. 添加到合适的 Profile 或 Skill 定义

### 添加新 Skill

编辑 `skill_manager.py` → `SKILL_DEFINITIONS`：

```python
"my_skill": SkillInfo(
    name="my_skill",
    description="AI 可理解的描述",
    modules=["my_module_a", "my_module_b"],
    estimated_tools=15,
    workflow_guide="## My Skill 工作流\n...",
),
```
