"""
Blender 培训系统 MCP 工具

提供通过 MCP 协议访问培训系统的工具接口。
支持课程浏览、练习执行、进度管理。
"""

import sys
import os
from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

# 添加项目根目录到路径以导入 blender_training
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ============================================================
# 输入模型定义
# ============================================================

class TrainingOverviewInput(BaseModel):
    """获取培训概览"""
    pass


class ListStagesInput(BaseModel):
    """列出培训阶段"""
    pass


class ListModulesInput(BaseModel):
    """列出模块"""
    stage_id: str = Field(description="阶段ID，如 S1, S2, S3, S4, S5, S6")


class ListExercisesInput(BaseModel):
    """列出练习"""
    module_id: str = Field(description="模块ID，如 S1M1, S2M1 等")


class ExerciseDetailInput(BaseModel):
    """获取练习详情"""
    exercise_id: str = Field(description="练习ID，如 S1M1E1, S2M1E1 等")


class StartExerciseInput(BaseModel):
    """开始练习"""
    exercise_id: str = Field(description="练习ID")


class NextStepInput(BaseModel):
    """进入下一步"""
    exercise_id: str = Field(description="练习ID")


class CompleteExerciseInput(BaseModel):
    """完成练习"""
    exercise_id: str = Field(description="练习ID")


class ProjectExercisesInput(BaseModel):
    """查看项目专属练习"""
    project: str = Field(description="项目标签: penglai(蓬莱九章) 或 fanzhendong(Q版樊振东)")


class ResetProgressInput(BaseModel):
    """重置进度"""
    confirm: bool = Field(default=False, description="确认重置（true=确认）")


class RunExerciseCommandInput(BaseModel):
    """执行练习中的 MCP 命令"""
    exercise_id: str = Field(description="练习ID")
    command_index: int = Field(default=0, description="命令索引（从0开始）")


# ============================================================
# 工具注册
# ============================================================

def register_training_tools(mcp: FastMCP, server: "BlenderMCPServer"):
    """注册培训系统工具"""

    # 延迟初始化 - 避免在 Skill 激活时阻塞
    _runner_cache = {}

    def _get_runner():
        if "instance" not in _runner_cache:
            from blender_training.runner import TrainingRunner
            _runner_cache["instance"] = TrainingRunner()
        return _runner_cache["instance"]

    # 兼容旧引用
    class _LazyRunner:
        def __getattr__(self, name):
            return getattr(_get_runner(), name)

    runner = _LazyRunner()

    @mcp.tool(
        name="blender_training_overview",
        description="获取 Blender 培训系统概览。显示课程体系结构、学习进度和统计信息。"
                    "培训基于8本专业书籍，融入蓬莱九章和Q版樊振东项目实战。"
    )
    async def training_overview(params: TrainingOverviewInput) -> str:
        overview = runner.get_overview()
        lines = [
            "# Blender 3D 大师培训系统",
            "",
            f"**版本**: {overview['version']}",
            f"**课程阶段**: {overview['stages']} 个",
            f"**课程模块**: {overview['modules']} 个",
            f"**练习总数**: {overview['exercises']} 个",
            "",
            "## 学习进度",
            f"- 完成率: {overview['progress']['completion_rate']}",
            f"- 已完成: {overview['progress']['completed']}/{overview['progress']['total']}",
            f"- 当前阶段: {overview['progress']['current_stage']}",
            f"- 当前模块: {overview['progress']['current_module']}",
            "",
            "## 课程结构",
        ]
        for s in overview["stages_detail"]:
            lines.append(f"- **{s['id']}** {s['title']} ({s['modules']}模块, {s['exercises']}练习)")

        lines.extend([
            "",
            "## 项目实战",
            "- **蓬莱九章**: NPR国风3渲2游戏场景（迷雾森林关卡）",
            "- **Q版樊振东**: 巴黎奥运乒乓球Q版角色场景",
            "",
            "💡 使用 `blender_training_list_stages` 查看所有阶段详情",
        ])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_stages",
        description="列出培训系统的所有阶段。每个阶段包含多个模块，从基础到专家逐步进阶。"
    )
    async def training_list_stages(params: ListStagesInput) -> str:
        stages = runner.list_stages()
        lines = ["# 培训阶段列表", ""]
        for s in stages:
            marker = "▶" if s["is_current"] else "○"
            lines.append(f"{marker} **{s['id']}** {s['title']}")
            lines.append(f"  {s['description']}")
            lines.append(f"  模块: {s['modules']} | 进度: {s['progress']}")
            lines.append("")
        lines.append("💡 使用 `blender_training_list_modules(stage_id)` 查看模块详情")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_modules",
        description="列出指定阶段的所有课程模块。每个模块包含学习目标和多个练习。"
    )
    async def training_list_modules(params: ListModulesInput) -> str:
        modules = runner.list_modules(params.stage_id)
        if not modules:
            return f"未找到阶段 {params.stage_id}"
        lines = [f"# 阶段 {params.stage_id} 的课程模块", ""]
        for m in modules:
            marker = "▶" if m["is_current"] else "○"
            lines.append(f"{marker} **{m['id']}** {m['title']} [{m['difficulty']}]")
            lines.append(f"  {m['description']}")
            lines.append(f"  练习: {m['completed']}/{m['exercises']} 完成")
            lines.append(f"  学习目标:")
            for obj in m["objectives"]:
                lines.append(f"    - {obj}")
            lines.append("")
        lines.append("💡 使用 `blender_training_list_exercises(module_id)` 查看练习列表")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_exercises",
        description="列出指定模块的所有练习。每个练习包含分步骤指导。"
    )
    async def training_list_exercises(params: ListExercisesInput) -> str:
        exercises = runner.list_exercises(params.module_id)
        if not exercises:
            return f"未找到模块 {params.module_id}"
        lines = [f"# 模块 {params.module_id} 的练习列表", ""]
        for ex in exercises:
            status_icon = {"not_started": "⬜", "in_progress": "🔄", "completed": "✅", "skipped": "⏭"}.get(ex["status"], "⬜")
            tag = f" [{ex['project_tag']}]" if ex["project_tag"] else ""
            lines.append(f"{status_icon} **{ex['id']}** {ex['title']}{tag}")
            lines.append(f"  {ex['description']}")
            lines.append(f"  难度: {ex['difficulty']} | 预计: {ex['time_estimate']} | 步骤: {ex['total_steps']}")
            lines.append("")
        lines.append("💡 使用 `blender_training_exercise_detail(exercise_id)` 查看练习详情")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_exercise_detail",
        description="获取练习的完整详情，包括步骤指导、MCP命令、预期结果和提示。"
    )
    async def training_exercise_detail(params: ExerciseDetailInput) -> str:
        detail = runner.get_exercise_detail(params.exercise_id)
        if not detail:
            return f"未找到练习 {params.exercise_id}"
        lines = [
            f"# 练习: {detail['title']}",
            "",
            f"**ID**: {detail['id']}",
            f"**难度**: {detail['difficulty']}",
            f"**分类**: {detail['category']}",
            f"**预计时间**: {detail['time_estimate']}",
            f"**状态**: {detail['status']}",
        ]
        if detail["project_tag"]:
            tag_name = {"penglai": "蓬莱九章", "fanzhendong": "Q版樊振东"}.get(detail["project_tag"], detail["project_tag"])
            lines.append(f"**项目**: {tag_name}")
        lines.extend(["", f"## 说明", detail["description"], "", "## 步骤"])
        for step in detail["steps"]:
            lines.append(f"  {step['index']}. {step['instruction']}")
        if detail["expected_objects"]:
            lines.extend(["", "## 预期对象"])
            for obj in detail["expected_objects"]:
                lines.append(f"  - `{obj}`")
        if detail["tips"]:
            lines.extend(["", "## 提示"])
            for tip in detail["tips"]:
                lines.append(f"  💡 {tip}")
        if detail["mcp_commands"]:
            lines.extend(["", "## 可用 MCP 命令"])
            for i, cmd in enumerate(detail["mcp_commands"]):
                lines.append(f"  [{i}] `{cmd.get('tool', '')}` → {cmd.get('params', {})}")
        lines.extend(["", "💡 使用 `blender_training_start_exercise` 开始练习"])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_start_exercise",
        description="开始一个练习。返回第一步指导和可用的MCP命令。"
    )
    async def training_start_exercise(params: StartExerciseInput) -> str:
        result = runner.start_exercise(params.exercise_id)
        if not result["success"]:
            return f"错误: {result['error']}"
        lines = [
            f"# 开始练习: {result['exercise']}",
            "",
            f"共 {result['total_steps']} 个步骤",
            "",
            f"## 第 1 步",
            result["first_step"],
        ]
        if result.get("tips"):
            lines.extend(["", "## 提示"])
            for tip in result["tips"]:
                lines.append(f"  💡 {tip}")
        if result.get("mcp_commands"):
            lines.extend(["", "## 参考 MCP 命令"])
            cmd = result["mcp_commands"][0]
            lines.append(f"  `{cmd.get('tool', '')}` → {cmd.get('params', {})}")
        lines.extend(["", "💡 使用 `blender_training_next_step` 进入下一步"])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_next_step",
        description="进入练习的下一步。完成当前步骤后调用此工具获取下一步指导。"
    )
    async def training_next_step(params: NextStepInput) -> str:
        result = runner.next_step(params.exercise_id)
        if not result["success"]:
            return f"错误: {result['error']}"
        if result.get("completed"):
            return f"🎉 {result['message']}\n\n总进度: {result['progress']}"
        lines = [
            f"## 第 {result['step']} 步（共 {result['total_steps']} 步）",
            "",
            result["instruction"],
        ]
        if result.get("mcp_command"):
            cmd = result["mcp_command"]
            lines.extend(["", "参考命令:", f"  `{cmd.get('tool', '')}` → {cmd.get('params', {})}"])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_complete_exercise",
        description="标记练习为已完成。"
    )
    async def training_complete_exercise(params: CompleteExerciseInput) -> str:
        result = runner.complete_exercise(params.exercise_id)
        if not result["success"]:
            return f"错误: {result['error']}"
        return f"✅ {result['message']}\n完成率: {result['completion_rate']}"

    @mcp.tool(
        name="blender_training_project_exercises",
        description="查看指定项目的所有练习。支持 penglai（蓬莱九章）和 fanzhendong（Q版樊振东）两个项目。"
    )
    async def training_project_exercises(params: ProjectExercisesInput) -> str:
        exercises = runner.list_project_exercises(params.project)
        if not exercises:
            return f"未找到项目 {params.project} 的练习"
        project_name = {"penglai": "蓬莱九章", "fanzhendong": "Q版樊振东"}.get(params.project, params.project)
        lines = [f"# {project_name} 专项练习", ""]
        for ex in exercises:
            status_icon = {"not_started": "⬜", "in_progress": "🔄", "completed": "✅"}.get(ex["status"], "⬜")
            lines.append(f"{status_icon} **{ex['id']}** {ex['title']} [{ex['difficulty']}] ~{ex['time_estimate']}")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_run_command",
        description="执行练习中预定义的MCP命令。直接在Blender中执行操作，帮助学员理解工具用法。"
    )
    async def training_run_command(params: RunExerciseCommandInput) -> str:
        detail = runner.get_exercise_detail(params.exercise_id)
        if not detail:
            return f"未找到练习 {params.exercise_id}"

        commands = detail.get("mcp_commands", [])
        if params.command_index >= len(commands):
            return f"命令索引 {params.command_index} 超出范围（共 {len(commands)} 个命令）"

        cmd = commands[params.command_index]
        tool_name = cmd.get("tool", "")
        tool_params = cmd.get("params", {})

        # 通过 MCP server 执行实际命令
        # 解析工具名称到 category 和 action
        parts = tool_name.replace("blender_", "").split("_", 1)
        if len(parts) == 2:
            category, action = parts
        else:
            category = parts[0]
            action = "execute"

        try:
            result = await server.execute_command(category, action, tool_params)
            return f"✅ 命令执行成功\n工具: {tool_name}\n结果: {result}"
        except Exception as e:
            return f"⚠️ 命令执行失败: {str(e)}\n工具: {tool_name}\n参数: {tool_params}\n\n你可以手动执行此命令进行练习。"

    @mcp.tool(
        name="blender_training_reset",
        description="重置所有培训进度。需要 confirm=true 确认。"
    )
    async def training_reset(params: ResetProgressInput) -> str:
        if not params.confirm:
            return "⚠️ 重置将清除所有进度。请设置 confirm=true 确认重置。"
        result = runner.reset_progress()
        return f"{'✅' if result['success'] else '❌'} {result['message']}"
