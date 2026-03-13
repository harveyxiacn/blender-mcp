"""
Blender Training System MCP Tools

Provides tool interfaces for accessing the training system via MCP protocol.
Supports course browsing, exercise execution, and progress management.
"""

import os
import sys
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

# Add project root to path to import blender_training
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ============================================================
# Input Model Definitions
# ============================================================


class TrainingOverviewInput(BaseModel):
    """Get training overview"""

    pass


class ListStagesInput(BaseModel):
    """List training stages"""

    pass


class ListModulesInput(BaseModel):
    """List modules"""

    stage_id: str = Field(description="Stage ID, e.g. S1, S2, S3, S4, S5, S6")


class ListExercisesInput(BaseModel):
    """List exercises"""

    module_id: str = Field(description="Module ID, e.g. S1M1, S2M1, etc.")


class ExerciseDetailInput(BaseModel):
    """Get exercise details"""

    exercise_id: str = Field(description="Exercise ID, e.g. S1M1E1, S2M1E1, etc.")


class StartExerciseInput(BaseModel):
    """Start an exercise"""

    exercise_id: str = Field(description="Exercise ID")


class NextStepInput(BaseModel):
    """Proceed to next step"""

    exercise_id: str = Field(description="Exercise ID")


class CompleteExerciseInput(BaseModel):
    """Complete an exercise"""

    exercise_id: str = Field(description="Exercise ID")


class ProjectExercisesInput(BaseModel):
    """View project-specific exercises"""

    project: str = Field(
        description="Project tag: penglai (Penglai Nine Chapters) or fanzhendong (Chibi Fan Zhendong)"
    )


class ResetProgressInput(BaseModel):
    """Reset progress"""

    confirm: bool = Field(default=False, description="Confirm reset (true=confirm)")


class RunExerciseCommandInput(BaseModel):
    """Execute an MCP command from an exercise"""

    exercise_id: str = Field(description="Exercise ID")
    command_index: int = Field(default=0, description="Command index (starting from 0)")


# ============================================================
# Tool Registration
# ============================================================


def register_training_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register training system tools"""

    # Lazy initialization - avoid blocking during Skill activation
    _runner_cache = {}

    def _get_runner() -> Any:
        if "instance" not in _runner_cache:
            from blender_training.runner import TrainingRunner

            _runner_cache["instance"] = TrainingRunner()
        return _runner_cache["instance"]

    # Backward compatibility wrapper
    class _LazyRunner:
        def __getattr__(self, name: str) -> Any:
            return getattr(_get_runner(), name)

    runner = _LazyRunner()

    @mcp.tool(
        name="blender_training_overview",
        description="Get an overview of the Blender training system. Displays course structure, learning progress, and statistics. "
        "Training is based on 8 professional books, incorporating Penglai Nine Chapters and Chibi Fan Zhendong project practice.",
    )
    async def training_overview(params: TrainingOverviewInput) -> str:
        overview = runner.get_overview()
        lines = [
            "# Blender 3D Master Training System",
            "",
            f"**Version**: {overview['version']}",
            f"**Course Stages**: {overview['stages']}",
            f"**Course Modules**: {overview['modules']}",
            f"**Total Exercises**: {overview['exercises']}",
            "",
            "## Learning Progress",
            f"- Completion Rate: {overview['progress']['completion_rate']}",
            f"- Completed: {overview['progress']['completed']}/{overview['progress']['total']}",
            f"- Current Stage: {overview['progress']['current_stage']}",
            f"- Current Module: {overview['progress']['current_module']}",
            "",
            "## Course Structure",
        ]
        for s in overview["stages_detail"]:
            lines.append(
                f"- **{s['id']}** {s['title']} ({s['modules']} modules, {s['exercises']} exercises)"
            )

        lines.extend(
            [
                "",
                "## Project Practice",
                "- **Penglai Nine Chapters**: NPR Chinese-style cel-shaded game scene (Misty Forest level)",
                "- **Chibi Fan Zhendong**: Paris Olympics table tennis chibi character scene",
                "",
                "Use `blender_training_list_stages` to view all stage details",
            ]
        )
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_stages",
        description="List all stages of the training system. Each stage contains multiple modules, progressing from beginner to expert.",
    )
    async def training_list_stages(params: ListStagesInput) -> str:
        stages = runner.list_stages()
        lines = ["# Training Stage List", ""]
        for s in stages:
            marker = "▶" if s["is_current"] else "○"
            lines.append(f"{marker} **{s['id']}** {s['title']}")
            lines.append(f"  {s['description']}")
            lines.append(f"  Modules: {s['modules']} | Progress: {s['progress']}")
            lines.append("")
        lines.append("Use `blender_training_list_modules(stage_id)` to view module details")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_modules",
        description="List all course modules for a specified stage. Each module contains learning objectives and multiple exercises.",
    )
    async def training_list_modules(params: ListModulesInput) -> str:
        modules = runner.list_modules(params.stage_id)
        if not modules:
            return f"Stage {params.stage_id} not found"
        lines = [f"# Course Modules for Stage {params.stage_id}", ""]
        for m in modules:
            marker = "▶" if m["is_current"] else "○"
            lines.append(f"{marker} **{m['id']}** {m['title']} [{m['difficulty']}]")
            lines.append(f"  {m['description']}")
            lines.append(f"  Exercises: {m['completed']}/{m['exercises']} completed")
            lines.append("  Learning Objectives:")
            for obj in m["objectives"]:
                lines.append(f"    - {obj}")
            lines.append("")
        lines.append("Use `blender_training_list_exercises(module_id)` to view exercise list")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_list_exercises",
        description="List all exercises for a specified module. Each exercise includes step-by-step guidance.",
    )
    async def training_list_exercises(params: ListExercisesInput) -> str:
        exercises = runner.list_exercises(params.module_id)
        if not exercises:
            return f"Module {params.module_id} not found"
        lines = [f"# Exercise List for Module {params.module_id}", ""]
        for ex in exercises:
            status_icon = {
                "not_started": "⬜",
                "in_progress": "🔄",
                "completed": "✅",
                "skipped": "⏭",
            }.get(ex["status"], "⬜")
            tag = f" [{ex['project_tag']}]" if ex["project_tag"] else ""
            lines.append(f"{status_icon} **{ex['id']}** {ex['title']}{tag}")
            lines.append(f"  {ex['description']}")
            lines.append(
                f"  Difficulty: {ex['difficulty']} | Estimated: {ex['time_estimate']} | Steps: {ex['total_steps']}"
            )
            lines.append("")
        lines.append("Use `blender_training_exercise_detail(exercise_id)` to view exercise details")
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_exercise_detail",
        description="Get full details of an exercise, including step guidance, MCP commands, expected results, and tips.",
    )
    async def training_exercise_detail(params: ExerciseDetailInput) -> str:
        detail = runner.get_exercise_detail(params.exercise_id)
        if not detail:
            return f"Exercise {params.exercise_id} not found"
        lines = [
            f"# Exercise: {detail['title']}",
            "",
            f"**ID**: {detail['id']}",
            f"**Difficulty**: {detail['difficulty']}",
            f"**Category**: {detail['category']}",
            f"**Estimated Time**: {detail['time_estimate']}",
            f"**Status**: {detail['status']}",
        ]
        if detail["project_tag"]:
            tag_name = {
                "penglai": "Penglai Nine Chapters",
                "fanzhendong": "Chibi Fan Zhendong",
            }.get(detail["project_tag"], detail["project_tag"])
            lines.append(f"**Project**: {tag_name}")
        lines.extend(["", "## Description", detail["description"], "", "## Steps"])
        for step in detail["steps"]:
            lines.append(f"  {step['index']}. {step['instruction']}")
        if detail["expected_objects"]:
            lines.extend(["", "## Expected Objects"])
            for obj in detail["expected_objects"]:
                lines.append(f"  - `{obj}`")
        if detail["tips"]:
            lines.extend(["", "## Tips"])
            for tip in detail["tips"]:
                lines.append(f"  {tip}")
        if detail["mcp_commands"]:
            lines.extend(["", "## Available MCP Commands"])
            for i, cmd in enumerate(detail["mcp_commands"]):
                lines.append(f"  [{i}] `{cmd.get('tool', '')}` → {cmd.get('params', {})}")
        lines.extend(["", "Use `blender_training_start_exercise` to start the exercise"])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_start_exercise",
        description="Start an exercise. Returns first step guidance and available MCP commands.",
    )
    async def training_start_exercise(params: StartExerciseInput) -> str:
        result = runner.start_exercise(params.exercise_id)
        if not result["success"]:
            return f"Error: {result['error']}"
        lines = [
            f"# Starting Exercise: {result['exercise']}",
            "",
            f"Total {result['total_steps']} steps",
            "",
            "## Step 1",
            result["first_step"],
        ]
        if result.get("tips"):
            lines.extend(["", "## Tips"])
            for tip in result["tips"]:
                lines.append(f"  {tip}")
        if result.get("mcp_commands"):
            lines.extend(["", "## Reference MCP Commands"])
            cmd = result["mcp_commands"][0]
            lines.append(f"  `{cmd.get('tool', '')}` → {cmd.get('params', {})}")
        lines.extend(["", "Use `blender_training_next_step` to proceed to the next step"])
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_next_step",
        description="Proceed to the next step of an exercise. Call this tool after completing the current step to get next step guidance.",
    )
    async def training_next_step(params: NextStepInput) -> str:
        result = runner.next_step(params.exercise_id)
        if not result["success"]:
            return f"Error: {result['error']}"
        if result.get("completed"):
            return f"{result['message']}\n\nOverall Progress: {result['progress']}"
        lines = [
            f"## Step {result['step']} of {result['total_steps']}",
            "",
            result["instruction"],
        ]
        if result.get("mcp_command"):
            cmd = result["mcp_command"]
            lines.extend(
                ["", "Reference Command:", f"  `{cmd.get('tool', '')}` → {cmd.get('params', {})}"]
            )
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_complete_exercise", description="Mark an exercise as completed."
    )
    async def training_complete_exercise(params: CompleteExerciseInput) -> str:
        result = runner.complete_exercise(params.exercise_id)
        if not result["success"]:
            return f"Error: {result['error']}"
        return f"{result['message']}\nCompletion Rate: {result['completion_rate']}"

    @mcp.tool(
        name="blender_training_project_exercises",
        description="View all exercises for a specified project. Supports penglai (Penglai Nine Chapters) and fanzhendong (Chibi Fan Zhendong) projects.",
    )
    async def training_project_exercises(params: ProjectExercisesInput) -> str:
        exercises = runner.list_project_exercises(params.project)
        if not exercises:
            return f"No exercises found for project {params.project}"
        project_name = {
            "penglai": "Penglai Nine Chapters",
            "fanzhendong": "Chibi Fan Zhendong",
        }.get(params.project, params.project)
        lines = [f"# {project_name} Project Exercises", ""]
        for ex in exercises:
            status_icon = {"not_started": "⬜", "in_progress": "🔄", "completed": "✅"}.get(
                ex["status"], "⬜"
            )
            lines.append(
                f"{status_icon} **{ex['id']}** {ex['title']} [{ex['difficulty']}] ~{ex['time_estimate']}"
            )
        return "\n".join(lines)

    @mcp.tool(
        name="blender_training_run_command",
        description="Execute a predefined MCP command from an exercise. Directly performs operations in Blender to help learners understand tool usage.",
    )
    async def training_run_command(params: RunExerciseCommandInput) -> str:
        detail = runner.get_exercise_detail(params.exercise_id)
        if not detail:
            return f"Exercise {params.exercise_id} not found"

        commands = detail.get("mcp_commands", [])
        if params.command_index >= len(commands):
            return f"Command index {params.command_index} out of range (total {len(commands)} commands)"

        cmd = commands[params.command_index]
        tool_name = cmd.get("tool", "")
        tool_params = cmd.get("params", {})

        # Execute actual command via MCP server
        # Parse tool name into category and action
        parts = tool_name.replace("blender_", "").split("_", 1)
        if len(parts) == 2:
            category, action = parts
        else:
            category = parts[0]
            action = "execute"

        try:
            result = await server.execute_command(category, action, tool_params)
            return f"Command executed successfully\nTool: {tool_name}\nResult: {result}"
        except Exception as e:
            return f"Command execution failed: {str(e)}\nTool: {tool_name}\nParams: {tool_params}\n\nYou can manually execute this command for practice."

    @mcp.tool(
        name="blender_training_reset",
        description="Reset all training progress. Requires confirm=true to confirm.",
    )
    async def training_reset(params: ResetProgressInput) -> str:
        if not params.confirm:
            return "Reset will clear all progress. Please set confirm=true to confirm the reset."
        result = runner.reset_progress()
        return f"{result['message']}"
