# 更新日志

Blender MCP 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased] - 2026-03-13

### 新增

- **全面的实时集成测试套件**
  - `tests/run_live_test.py`: 121个测试覆盖所有50+处理器类别，针对实时Blender实例
  - `tests/create_style_scenes.py`: 264条命令演示，创建3个完整场景（3A游戏、动漫、像素风格）
  - 测试覆盖：场景、对象、建模、材质、灯光、相机、动画、渲染、曲线、UV、物理、约束、节点、骨骼、角色模板、导出、批处理、资产、风格预设、程序化材质、运动角色、世界环境、合成器、雕刻、油笔、毛发、模拟等

### 变更

- **Blender 5.x 兼容性修复（50+处理器文件）**
  - 修复EEVEE引擎名称：`BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE`，增加版本感知兼容层（`handlers/compat.py`）
  - 修复`bpy.data.objects.get(None)`崩溃问题（Blender 5.x抛出异常而非返回None）
  - 修复`Action.fcurves`移除问题（5.x使用分层动作系统）
  - 修复`ClothSettings.collision_settings`属性位置变更
  - 修复`bpy_prop_collection.__contains__`类型检查
  - 曲线创建添加默认控制点
  - 偏好设置处理器增加None键处理
  - Black格式化151个文件

### 修复

- **CI流水线全绿**
  - 修复6696个ruff lint错误（自动修复 + addon/examples/tests按文件忽略规则）
  - 修复141个black格式化问题
  - 修复414个mypy类型错误（放宽addon代码配置，TYPE_CHECKING导入）
  - 从pytest收集中排除实时测试文件（需要运行Blender实例）
  - 移除已弃用的ruff规则（ANN101, ANN102）

## [Unreleased] - 2026-03-04

### 新增

- **自动化生产线工具（Pipeline）**
  - 新增 `blender_pipeline_generate_character`：角色模板 + 发型/服装/配饰 + 自动绑定 + 风格应用
  - 新增 `blender_pipeline_generate_prop`：道具创建 + 风格 + 程序化材质 + 自动 UV
  - 新增 `blender_pipeline_assemble_scene`：环境/地面/灯光/相机/渲染参数一键组装

- **质量审计工具（Quality Audit）**
  - 新增 `blender_quality_audit_topology`：拓扑审计（N-gon、非流形、松散点）
  - 新增 `blender_quality_audit_uv`：UV 审计（利用率、拉伸、重叠）
  - 新增 `blender_quality_audit_performance`：性能预算审计（三角面、估算 draw call）
  - 新增 `blender_quality_audit_full`：拓扑 + UV + 性能综合评分与等级输出

- **自动化 Skill 组**
  - 新增 `automation` Skill，组合 `pipeline`、`quality_audit`、`style_presets`、`procedural_materials`
  - 支持从“自动生成”到“自动验收”的闭环工作流

- **拓扑节点辅助工具**
  - 新增 `addon/blender_mcp_addon/handlers/node_utils.py`
  - 提供共享的 `find_principled_bsdf()`，用于材质节点安全查找

- **测试覆盖扩展**
  - 新增连接、配置、工具配置、Skill 管理器、Server 兼容别名、工具导出、Principled BSDF 回归等测试
  - 测试总数从 27 项扩展到 34 项

- **连接状态工具**
  - 新增 `blender_connection_status`，可查询 MCP 与 Blender 的连接状态、重连次数、失败命令数、待处理请求等诊断信息

- **统一配置模块**
  - 新增 `src/blender_mcp/config.py`
  - 支持通过环境变量配置主机、端口、超时、重连与日志级别等运行参数

### 变更

- **SkillManager 兼容性升级**
  - 适配新版 FastMCP 工具管理方式，修复动态激活/停用 Skill 时的工具快照与卸载逻辑

- **工具配置扩展**
  - `tools_config.py` 新增 `AUTOMATION_MODULES`
  - `focused`、`standard`、`full` Profile 现已纳入 `pipeline` 和 `quality_audit`

- **工具导出与注册完善**
  - `pipeline` 与 `quality_audit` 接入模块注册表与 `tools.__all__` 导出

- **Blender 5.0.1 集成验证**
  - 回归测试通过：`test_comprehensive.py` 133/133、`test_all_tools.py` 23/23
  - 自动化流程实测通过：角色/道具/场景流水线 + 全量质量审计

- **连接层稳定性增强**
  - `BlenderConnection` 增加自动重连与心跳机制
  - 命令发送失败时支持重连后重试
  - 扩大读取缓冲区并增强 UTF-8 解码容错
  - 新增连接统计信息（总命令数、失败数、重连次数等）

- **Addon 主线程等待机制优化**
  - 使用 `threading.Event.wait()` 替代 `sleep` 轮询等待，降低 CPU 空转

- **CLI 默认配置来源统一**
  - `__main__.py` 与 `server.py` 默认参数改为从统一配置模块读取

### 修复

- **Principled BSDF 递归缺陷**
  - 修复 `ai_generation`、`character_template`、`substance`、`vr_ar`、`zbrush` 中的递归调用错误
  - 统一改为使用共享 helper，避免运行时崩溃风险

- **Server 向后兼容**
  - 为 `BlenderMCPServer` 增加 `send_command()` 别名，兼容仍在调用旧接口的工具模块

- **Pipeline 工具注册与参数兼容**
  - 修复 `pipeline/quality_audit` 在 FastMCP 下的注册错误
  - 改进相机激活参数兼容（同时传递 `camera_name` 与 `name`）

- **Addon 启动参数问题**
  - 修复 `start_server()` 未正确传递 `host` 参数的问题

- **Python 执行安全性**
  - 为 `execute_python` 增加空代码校验、代码大小限制与危险模式拦截

## [0.2.0] - 2026-02-11

### 新增

- **Skill 系统（动态工具加载）**
  - `SkillManager` 按需激活/停用工具组
  - 3 个元工具：`blender_list_skills`、`blender_activate_skill`、`blender_deactivate_skill`
  - 11 个 Skill 组覆盖全部 200+ 工具
  - `tools/list_changed` MCP 通知，客户端自动刷新
  - 激活时返回工作流指引
  - 新增 `"skill"` 工具 Profile（推荐，~31 个启动工具）

- **高级网格编辑**（5 个工具）
  - `blender_mesh_edit_advanced` — 内嵌、桥接、旋转、切刀、填充、对称化等
  - `blender_mesh_edge_mark` — 折痕、锐边、缝合、倒角权重
  - `blender_mesh_select_by_trait` — 非流形、松散、边界等
  - `blender_vertex_group` — 顶点组管理
  - `blender_vertex_color` — 顶点颜色绘制

- **风格预设**（3 个工具）
  - `blender_style_setup` — 一键风格配置（像素风→3A，8 种预设）
  - `blender_outline_effect` — 描边（Solidify/Freestyle/Grease Pencil）
  - `blender_bake_maps` — 高低模烘焙工作流

- **程序化材质**（2 个工具）
  - `blender_procedural_material` — 8 大类 67 种预设
  - `blender_material_wear` — 磨损效果（边缘磨损、划痕、锈蚀、灰尘等）

- **增强对象创建**
  - `mesh_params` 支持参数化网格创建（段数、半径、深度等）
  - 所有网格基本体的完整参数控制

- **扩展修改器支持**
  - 45 种修改器类型（从 12 种扩展）
  - 新增：螺旋、线框、焊接、重建网格、构建、多级精度、铸型、曲线、晶格等

### 变更

- 默认 `TOOL_PROFILE` 从 `"focused"` 改为 `"skill"`
- 启动工具数从 ~100 减少到 ~31（减少 69%）

## [0.1.0] - 2026-01-15

### 新增

- 首次发布
- 基于 FastMCP 框架的 MCP 服务器
- Blender 插件（TCP 服务器）
- 核心工具模块：场景、对象、建模、材质、灯光、相机、动画、渲染、实用工具、导出
- 扩展模块：角色模板、骨骼绑定、自动绑定、物理、约束、节点、合成器、雕刻、纹理绘制、批处理、资产、动画预设、世界环境、版本控制、AI 生成、VR/AR、Substance、ZBrush、云渲染、协作、培训
- 多 IDE 支持：Cursor、Windsurf、Claude Desktop
- 插件热更新开发功能
- 工具 Profile：minimal、focused、standard、full
