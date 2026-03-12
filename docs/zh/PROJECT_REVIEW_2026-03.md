# Blender MCP 项目审查报告

日期：2026-03-10

## 审查范围

本次检查覆盖：

- `README.md` 与核心文档
- `src/blender_mcp/*`
- `addon/blender_mcp_addon/*`
- `tests/*`
- 基于源码的工具/Profile/Skill 盘点

## 当前快照

- `src/blender_mcp/tools` 下 51 个工具模块
- 源码中共 359 个工具注册
- 12 个 Skill 分组
- 6 个 Profile：`minimal`、`skill`、`focused`、`standard`、`extended`、`full`
- 默认 `skill` Profile 启动面为 32 个工具

## 关键发现

### 1. automation 存在执行层断层

严重级别：高

- `pipeline` 与 `quality_audit` 已注册在 `src/blender_mcp/tools_config.py`
- 它们也会通过 `focused`、`standard`、`full` 以及 `automation` Skill 对外暴露
- 但 `addon/blender_mcp_addon/handlers/__init__.py` 里并没有这两个类别的映射

影响：

- MCP 客户端可能看得到这些工具
- 但执行时仍可能在插件分发层报未知类别错误

建议：

- 要么立刻补齐插件 handler
- 要么在执行层对齐之前，把这两个模块从稳定 Profile 中移除，或明确标记为实验性

### 2. 文档漂移已经影响判断

严重级别：中

本次更新前，核心文档仍然把项目描述为大约：

- 200+ 工具
- 26 个模块
- 11 个 Skill
- `skill` 启动约 31 个工具

而当前代码规模已经明显超过这些数字，路线图里也仍有一部分“已实现功能”被写成未来计划。

### 3. 环境可迁移性较弱

严重级别：中

当前本地 `.venv/pyvenv.cfg` 记录的是绝对解释器路径。仓库一旦在不同机器之间直接拷贝，`uv run` 或 `.venv\Scripts\python.exe` 可能在项目代码启动前就失效。

建议：

- 在文档里明确写出恢复方式
- 在交付/迁移流程中避免直接传递带机器绑定的虚拟环境状态

### 4. 测试没有覆盖服务端/插件端一致性

严重级别：中

现有测试覆盖了配置、导出、Skill 元数据和部分服务端行为，但没有断言“所有公开执行类别都能在插件侧找到对应 handler 路由”。

建议：

- 增加服务端类别与插件 handler 注册表的对齐测试
- 至少为 automation 模块补一个专门回归测试

### 5. 根目录遗留测试文件默认不会被 pytest 执行

严重级别：低

`pyproject.toml` 将 pytest 的默认路径指向 `tests/`，而仓库根目录仍保留多份旧的 `test_*.py` 文件。它们不会进入默认测试集。

建议：

- 要么迁移到 `tests/`
- 要么明确标注为手工脚本/历史测试

## 优化建议

### 1. 从源码自动生成盘点文档

- 工具数量从装饰器生成
- Profile 数量从 `tools_config.py` 生成
- Skill 清单从 `skill_manager.py` 生成
- 通过 CI 产出工具清单，避免未来再次出现数字漂移

### 2. 引入稳定/实验性能力标记

- 在插件执行层未补齐之前，将 automation 相关模块放到显式开关后面
- 在文档和工具描述里同步展示稳定性状态

### 3. 为长耗时操作加入任务控制

当前插件侧主要依赖“主线程执行 + 超时等待”的请求模型。对渲染、烘焙、导出、审计这类任务，更合适的是显式任务队列。

建议增加：

- 任务 ID
- 进度上报
- 取消机制
- 结构化耗时与错误遥测

### 4. 收紧发布检查清单

- 服务端类别与插件类别一致
- Profile 数量自动刷新
- 文档盘点自动刷新
- 至少对 `skill`、`focused`、`full` 做 smoke test

## 新功能建议

### 1. 审计到自动修复闭环

把 `quality_audit` 的结果转成后续修复动作：

- 修复导出命名
- 补齐缺失 UV
- 降低超预算网格
- 按目标平台套用发布预设

### 2. 资产构建配方

增加声明式 recipe / manifest：

- 角色 recipe
- 道具 recipe
- 场景 recipe
- 导出 recipe

这样可以提高批量生产与 AI 自动流程的可重复性。

### 3. 面向目标平台的导出校验

为以下目标增加导出前验证器：

- web
- mobile
- desktop
- hero / AAA

校验维度可包括三角面、材质槽、贴图预算、命名规范和导出格式策略。

### 4. Review 交接包

输出一个场景审查包，包含：

- 视口截图
- 审计摘要
- 导出摘要
- 与上一版资产的可选差异信息

## 建议执行顺序

1. 先补齐 `pipeline` 与 `quality_audit` 的插件 handler
2. 再补服务端/插件端一致性测试
3. 然后把工具/Profile/Skill 盘点文档自动化
4. 再建设长耗时任务的队列与进度机制
5. 最后在此基础上追加审计到自动修复能力
