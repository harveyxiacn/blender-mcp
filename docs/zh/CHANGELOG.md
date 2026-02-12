# 更新日志

Blender MCP 的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

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
