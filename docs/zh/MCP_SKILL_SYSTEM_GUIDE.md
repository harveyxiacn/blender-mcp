# MCP Skill System — 按需加载工具的通用实现指南

> **适用场景**: 任何拥有大量工具（>30个）的 MCP Server  
> **核心收益**: 启动时减少 60-80% 的工具 schema 开销，节省 AI Context Window  
> **验证状态**: 已在 Blender MCP 项目中实测通过（`focused` Profile 108 工具 → `skill` Profile 32 启动工具 + 按需加载）

---

## 1. 问题背景

### 为什么需要 Skill 系统？

MCP Server 注册的每个工具（Tool）都会以 JSON Schema 形式发送给 AI 客户端。当工具数量庞大时：

| 工具数量 | 估算 Schema Token 消耗 | 问题 |
|----------|------------------------|------|
| 30 个 | ~5-8K tokens | ✅ 可接受 |
| 80 个 | ~15-25K tokens | ⚠️ 挤压可用上下文 |
| 200+ 个 | ~40-60K tokens | ❌ 严重浪费，AI 选择准确率下降 |

**Skill 系统解决方案**: 启动时只注册核心工具 + 几个元工具（meta-tools），AI 根据任务按需加载/卸载工具组。

```
传统模式:  启动 → 注册全部 108 个 focused 工具 → AI 面对 108 个选择
Skill 模式: 启动 → 注册 32 个启动工具 → AI 按需加载 → 用完卸载
```

---

## 2. 技术可行性

### 2.1 MCP 协议支持

MCP 协议原生支持动态工具变更：

```
Server → Client: notifications/tools/list_changed
Client 收到后: 重新调用 tools/list → 获取最新工具列表
```

**协议类型定义**（`mcp.types`）:
```python
class ToolListChangedNotification:
    method: Literal["notifications/tools/list_changed"]
    params: NotificationParams | None = None
```

### 2.2 FastMCP SDK 支持

FastMCP（Python MCP SDK）提供了完整的运行时工具管理 API：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

# ✅ 运行时动态添加工具
mcp.add_tool(my_function, name="tool_name", description="...")

# ✅ 运行时动态移除工具
mcp.remove_tool("tool_name")

# ✅ 在工具处理函数中发送通知（通过 Context）
@mcp.tool()
async def activate_skill(name: str, ctx: Context) -> str:
    mcp.add_tool(...)
    await ctx.session.send_tool_list_changed()  # 通知客户端
```

**内部实现**: `ToolManager._tools` 是一个 `dict[str, Tool]`，add/remove 就是字典操作，运行时安全。

### 2.3 客户端兼容性

| 客户端 | tools/list_changed 支持 | 备注 |
|--------|------------------------|------|
| Windsurf | ✅ 已验证 | 收到通知后自动刷新工具列表 |
| Cursor | ✅ 预期支持 | 基于 MCP 标准协议 |
| Claude Desktop | ✅ 预期支持 | Anthropic 官方客户端 |
| 自定义客户端 | ⚠️ 需实现 | 需监听 `notifications/tools/list_changed` |

---

## 3. 架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────┐
│                 MCP Client (AI)              │
│                                              │
│  1. list_skills()         → 查看可用 Skill    │
│  2. activate_skill("X")   → 加载工具组        │
│  3. 使用新加载的工具完成任务                    │
│  4. deactivate_skill("X") → 卸载工具组        │
└──────────────────┬──────────────────────────┘
                   │ MCP Protocol
┌──────────────────▼──────────────────────────┐
│              MCP Server                      │
│                                              │
│  启动时注册:                                  │
│  ├── 核心工具 (始终可用)                       │
│  └── Skill 元工具 (3个):                      │
│      ├── list_skills                         │
│      ├── activate_skill                      │
│      └── deactivate_skill                    │
│                                              │
│  动态注册/移除:                               │
│  ├── Skill A 工具组 (按需)                    │
│  ├── Skill B 工具组 (按需)                    │
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

### 3.2 核心组件

| 组件 | 职责 | 关键 API |
|------|------|----------|
| **SkillManager** | 管理 Skill 生命周期、跟踪激活状态 | `activate()`, `deactivate()`, `is_active()` |
| **SkillInfo** | Skill 元数据（描述、模块列表、工作流指引） | 数据类 |
| **Skill 元工具** | 暴露给 AI 的 MCP 工具接口 | `list_skills`, `activate_skill`, `deactivate_skill` |
| **工具模块** | 按 Skill 分组的工具代码 | 每个模块一个 `register_xxx_tools()` 函数 |

---

## 4. 实现步骤

### 步骤 1：定义 Skill 元数据

```python
# skill_manager.py
from dataclasses import dataclass, field

@dataclass
class SkillInfo:
    """Skill 元数据"""
    name: str                    # Skill 唯一标识
    description: str             # AI 可读的描述
    modules: list[str]           # 对应的工具模块名列表
    workflow_guide: str = ""     # 工作流指引文本（激活时返回给 AI）
    estimated_tools: int = 0     # 预估工具数量
    tags: list[str] = field(default_factory=list)  # 搜索标签
```

### 步骤 2：建立 Skill 注册表

将工具模块按功能分组，每组成为一个 Skill：

```python
SKILL_DEFINITIONS: dict[str, SkillInfo] = {
    "modeling": SkillInfo(
        name="modeling",
        description="3D建模工具 - 网格编辑、修改器、曲线",
        modules=["modeling", "curves", "uv_mapping"],
        estimated_tools=38,
        workflow_guide="""
## Modeling 工作流指引
1. 创建基础几何体 → 添加修改器 → 应用
2. 曲线建模: 创建路径 → 添加 Curve 修改器
...
""",
    ),
    "materials": SkillInfo(
        name="materials",
        description="材质系统 - PBR材质、程序化材质",
        modules=["material", "procedural_materials"],
        estimated_tools=17,
        workflow_guide="...",
    ),
    # ... 更多 Skills
}
```

**分组原则**:
- **按功能域分组**: 建模、材质、动画、渲染等
- **每组 5-40 个工具**: 太少不值得独立，太多失去按需加载意义
- **依赖关系**: 相互依赖的工具放在同一 Skill 中

### 步骤 3：实现 SkillManager

```python
class SkillManager:
    def __init__(self, server):
        self.server = server
        self._active_skills: dict[str, list[str]] = {}  # skill_name → [tool_names]
    
    def activate_skill(self, skill_name: str) -> tuple[bool, str, list[str]]:
        """激活 Skill，动态注册工具"""
        skill_info = SKILL_DEFINITIONS[skill_name]
        registered_tools = []
        
        for module_name in skill_info.modules:
            # 记录注册前的工具列表
            before = set(t.name for t in server.mcp._tool_manager.list_tools())
            
            # 动态导入并注册模块
            tool_module = importlib.import_module(f"mypackage.tools.{module_name}")
            register_func = getattr(tool_module, f"register_{module_name}_tools")
            register_func(server.mcp, server)
            
            # 计算新增工具
            after = set(t.name for t in server.mcp._tool_manager.list_tools())
            registered_tools.extend(after - before)
        
        self._active_skills[skill_name] = registered_tools
        return True, f"Activated {skill_name}", registered_tools
    
    def deactivate_skill(self, skill_name: str) -> tuple[bool, str]:
        """停用 Skill，移除工具"""
        for tool_name in self._active_skills[skill_name]:
            self.server.mcp.remove_tool(tool_name)
        del self._active_skills[skill_name]
        return True, f"Deactivated {skill_name}"
```

### 步骤 4：实现 Skill MCP 元工具

```python
# tools/skills.py
from mcp.server.fastmcp import FastMCP, Context

def register_skill_tools(mcp: FastMCP, server) -> None:
    
    @mcp.tool()
    async def list_skills() -> str:
        """List all available skills and their activation status.
        
        Skills are groups of tools that can be loaded on demand.
        Start here to discover what capabilities are available.
        """
        return server.skill_manager.get_status_summary()
    
    @mcp.tool()
    async def activate_skill(skill_name: str, ctx: Context) -> str:
        """Activate a skill to dynamically load its tool group.
        
        This registers new MCP tools that become available for immediate use.
        Each skill provides a set of related tools and a workflow guide.
        
        Args:
            skill_name: Name of the skill to activate
        """
        success, message, tools = server.skill_manager.activate_skill(skill_name)
        
        if success:
            # 🔑 关键：通知客户端工具列表已变更
            await ctx.session.send_tool_list_changed()
        
        # 返回工作流指引
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

### 步骤 5：配置启动 Profile

```python
# tools_config.py

TOOL_PROFILE = "skill"  # 推荐

# 核心工具 - 启动时始终加载
CORE_MODULES = ["scene", "object", "utility", "export"]

# Skill 模式 - 核心 + 元工具
SKILL_MODULES = CORE_MODULES + ["skills"]

def get_enabled_modules():
    if TOOL_PROFILE == "skill":
        return SKILL_MODULES       # ~32 个工具
    elif TOOL_PROFILE == "full":
        return ALL_MODULES          # ~300 个工具
```

### 步骤 6：Server 集成

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
    
    def _register_tools(self):
        for module_name in get_enabled_modules():
            # 动态导入并注册模块
            tool_module = importlib.import_module(f"mypackage.tools.{module_name}")
            register_func = getattr(tool_module, MODULE_REGISTRY[module_name])
            register_func(self.mcp, self)
```

---

## 5. 工具模块组织规范

### 5.1 目录结构

```
src/mypackage/
├── server.py              # MCP Server 主类
├── skill_manager.py       # Skill 管理器 + Skill 定义
├── tools_config.py        # Profile 配置
├── tools/
│   ├── __init__.py        # 导出所有 register 函数
│   ├── skills.py          # Skill 元工具 (list/activate/deactivate)
│   ├── core_module_a.py   # 核心工具模块 (始终加载)
│   ├── core_module_b.py   # 核心工具模块 (始终加载)
│   ├── skill_module_x.py  # Skill 工具模块 (按需加载)
│   ├── skill_module_y.py  # Skill 工具模块 (按需加载)
│   └── ...
```

### 5.2 工具模块模板

每个工具模块遵循统一模式：

```python
# tools/my_module.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

class MyInput(BaseModel):
    param: str = Field(..., description="参数描述")

def register_my_module_tools(mcp: FastMCP, server) -> None:
    """注册 my_module 工具组"""
    
    @mcp.tool()
    async def my_tool(params: MyInput) -> str:
        """Tool description for AI to understand."""
        result = await server.execute_command("category", "action", params.model_dump())
        return format_result(result)
```

### 5.3 MODULE_REGISTRY 映射

```python
MODULE_REGISTRY = {
    "core_a": "register_core_a_tools",
    "core_b": "register_core_b_tools",
    "skill_x": "register_skill_x_tools",
    "skill_y": "register_skill_y_tools",
    "skills": "register_skill_tools",  # Skill 元工具
}
```

---

## 6. 工作流指引设计

工作流指引是 Skill 系统的**差异化优势**——不只是加载工具，还告诉 AI 如何组合使用。

### 6.1 指引结构模板

```markdown
## [Skill Name] 工作流指引

### 常用工作流:
1. **场景A**: 工具1 → 工具2 → 工具3
2. **场景B**: 工具4 → 工具5

### 关键参数:
- 参数X: 推荐值范围
- 参数Y: 常用选项列表

### 提示:
- 最佳实践建议
- 常见错误规避
```

### 6.2 指引内容原则

- **简洁**: 200-400 字，不超过 500 字
- **可操作**: 写具体工具名和参数，不写抽象概念
- **场景驱动**: 按"我要做XX"组织，而非按工具列表
- **包含 fallback**: 提示 AI 复杂操作可通过 `execute_python` 实现

---

## 7. 最佳实践

### 7.1 Skill 划分原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **功能内聚** | 同一工作流的工具放一起 | 建模+曲线+UV = "modeling" Skill |
| **大小适中** | 每个 Skill 5-40 个工具 | 太小→频繁切换；太大→失去意义 |
| **独立可用** | Skill 之间无强依赖 | 激活 "animation" 不需要先激活 "modeling" |
| **命名直观** | AI 能从名字猜到功能 | "materials" 而非 "group_b" |

### 7.2 核心工具选择标准

启动时始终加载的核心工具应满足：

1. **高频使用** — 几乎每个任务都需要
2. **基础操作** — 查看、列表、基本CRUD
3. **万能后备** — 如 `execute_python`/`execute_script` 可覆盖未加载的功能
4. **总数控制** — 核心工具不超过 30 个

### 7.3 多 Skill 并行激活

```python
# AI 可以同时激活多个 Skill
activate_skill("modeling")    # +38 工具
activate_skill("materials")   # +17 工具
# 此时共 32 + 38 + 17 = 87 个工具

# 用完后逐个卸载
deactivate_skill("modeling")
deactivate_skill("materials")
```

### 7.4 防重复注册

`SkillManager.activate_skill()` 应检查 Skill 是否已激活，避免重复注册：

```python
if skill_name in self._active_skills:
    return False, f"Skill '{skill_name}' is already active", existing_tools
```

FastMCP 的 `ToolManager.add_tool()` 也会检查重复并跳过（`warn_on_duplicate_tools`）。

### 7.5 错误处理

```python
def activate_skill(self, skill_name):
    if skill_name not in SKILL_DEFINITIONS:
        available = ", ".join(SKILL_DEFINITIONS.keys())
        return False, f"Unknown skill: {skill_name}. Available: {available}", []
```

---

## 8. 效果量化

### Blender MCP 实测数据

| 指标 | 传统模式 (focused) | Skill 模式 | 改善 |
|------|-------------------|------------|------|
| 启动工具数 | 108 | 32 | **-70%** |
| 估算 Schema Tokens | ~20K | ~6K | **-70%** |
| 工具选择准确率 | 一般 | 高 | AI 面对更少选项 |
| 功能完整性 | 100% | 100% | 按需加载不丢功能 |

### 典型工作流 Token 消耗对比

```
传统: 始终 20K tokens 工具 schema
Skill: 6K (核心) + 按需加载的 Skill schema

场景: "创建一个带材质的角色"
  传统: 20K (全量 schema)
  Skill: 6K + 8K (modeling) + 4K (materials) = 18K
         但任务完成后卸载, 后续对话恢复 6K
```

---

## 9. 适用场景判断

### 适合使用 Skill 系统

- ✅ 工具总数 > 30 个
- ✅ 工具可按功能域分组
- ✅ 不同任务使用不同工具子集
- ✅ Context Window 是瓶颈

### 不适合使用 Skill 系统

- ❌ 工具总数 < 20 个（直接全量加载）
- ❌ 所有工具每次都需要（无法分组）
- ❌ 客户端不支持 `tools/list_changed`（工具仍注册但 AI 不知道）

### 替代方案

如果 Skill 系统不适合，还可以考虑：

1. **复合工具**: 将多个小工具合并为参数化的大工具（如本项目的 10 个复合工具替代 58 个原子工具）
2. **execute_script 兜底**: 保留一个万能脚本执行工具，复杂操作通过脚本实现
3. **静态 Profile**: 预设几个工具集（minimal/standard/full），启动时选择

---

## 10. 快速 Checklist

在你的 MCP Server 中实现 Skill 系统的检查清单：

- [ ] 确认 MCP SDK 版本支持 `add_tool()` / `remove_tool()` / `send_tool_list_changed()`
- [ ] 将工具按功能域分组，定义 Skill 元数据
- [ ] 确定核心工具集（始终加载，≤30 个）
- [ ] 实现 `SkillManager` 类（activate/deactivate/状态查询）
- [ ] 实现 3 个 Skill 元工具（list/activate/deactivate）
- [ ] 为每个 Skill 编写工作流指引文本
- [ ] 添加 "skill" Profile 到配置文件
- [ ] Server 类添加 `skill_manager` 属性
- [ ] 测试完整流程：list → activate → 使用工具 → deactivate
- [ ] 验证客户端响应 `tools/list_changed` 通知

---

## 附录 A：关键 API 速查

```python
# FastMCP 动态工具管理
mcp.add_tool(fn, name="...", description="...")   # 运行时添加
mcp.remove_tool("tool_name")                      # 运行时移除

# 工具列表变更通知（在工具处理函数内）
@mcp.tool()
async def my_tool(ctx: Context):
    await ctx.session.send_tool_list_changed()

# ToolManager 内部（dict 操作）
mcp._tool_manager._tools: dict[str, Tool]         # 工具存储
mcp._tool_manager.list_tools() -> list[Tool]       # 列出工具
mcp._tool_manager.add_tool(fn, ...) -> Tool        # 添加
mcp._tool_manager.remove_tool(name)                # 移除
```

## 附录 B：故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 激活 Skill 后 AI 看不到新工具 | 客户端未响应 `tools_changed` | activate 返回值包含工具列表，AI 可直接使用 |
| 重复激活报错 | 未检查已激活状态 | `if skill in _active_skills: return` |
| 卸载后工具仍可调用 | `remove_tool` 未执行 | 检查 SkillManager 是否正确跟踪 tool_names |
| 服务器重启后 Skill 状态丢失 | `_active_skills` 在内存中 | 设计上预期行为，重启后回到核心工具集 |

## 附录 C：项目实际文件参考

以 Blender MCP 为例，以下文件构成了完整的 Skill 系统实现：

```
src/blender_mcp/
├── server.py              # 添加 skill_manager 属性
├── skill_manager.py       # SkillManager + 12 个 SKILL_DEFINITIONS
├── tools_config.py        # "skill" Profile, SKILL_MODULES
├── tools/
│   ├── __init__.py        # 注册 skills 模块
│   ├── skills.py          # 3 个元工具: list/activate/deactivate
│   ├── scene.py           # [核心] 场景管理
│   ├── object.py          # [核心] 对象操作
│   ├── utility.py         # [核心] 实用工具(含 execute_python)
│   ├── export.py          # [核心] 导出
│   ├── modeling.py        # [Skill: modeling] 建模工具
│   ├── curves.py          # [Skill: modeling] 曲线工具
│   ├── uv_mapping.py      # [Skill: modeling] UV 映射
│   ├── material.py        # [Skill: materials] 材质系统
│   ├── animation.py       # [Skill: animation] 动画工具
│   └── ...                # 更多 Skill 模块
```
