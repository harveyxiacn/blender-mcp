"""
Skill management tools

Provides MCP tools for on-demand loading/unloading of tool groups:
- list_skills: List all available skills and their status
- activate_skill: Activate a skill, dynamically loading its tool group
- deactivate_skill: Deactivate a skill, removing its tool group
"""

import asyncio
import contextlib
import logging
from typing import TYPE_CHECKING

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

logger = logging.getLogger(__name__)


# ==================== Input Models ====================


class ActivateSkillInput(BaseModel):
    """Activate skill input"""

    skill_name: str = Field(
        ..., description="Skill name to activate. Use list_skills to see available options."
    )


class DeactivateSkillInput(BaseModel):
    """Deactivate skill input"""

    skill_name: str = Field(..., description="Skill name to deactivate.")


# Debounce: keep track of the last pending notification task, cancel old one when new arrives
_pending_notify_task: asyncio.Task | None = None


def _schedule_notify(ctx: Context) -> None:
    """Debounced tools/list_changed notification

    Key design:
    1. Do not await inside the tool handler, let the response return to client first
    2. Cancel previously unsent notification each time a new one is scheduled (debounce)
    3. 8 consecutive activate/deactivate calls will only send 1 final notification
    4. 0.5 second delay ensures the response has been read by the client
    """
    global _pending_notify_task

    # Cancel previously unfinished notification task
    if _pending_notify_task and not _pending_notify_task.done():
        _pending_notify_task.cancel()

    async def _delayed_notify() -> None:
        await asyncio.sleep(0.5)
        try:
            await asyncio.wait_for(ctx.session.send_tool_list_changed(), timeout=3.0)
        except asyncio.CancelledError:
            pass  # Cancelled by new notification, normal behavior
        except Exception as e:
            logger.debug(f"tool_list_changed notification skipped: {e}")

    with contextlib.suppress(Exception):
        _pending_notify_task = asyncio.get_event_loop().create_task(_delayed_notify())


# ==================== Registration Function ====================


def register_skill_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register skill management tools"""

    @mcp.tool()
    async def blender_list_skills() -> str:
        """List all available skills and their activation status.

        Skills are groups of tools that can be loaded on demand.
        Start here to discover what capabilities are available, then use
        activate_skill to load the tools you need.

        Returns a summary of all skills with their descriptions,
        tool counts, and current activation status.
        """
        return server.skill_manager.get_status_summary()

    @mcp.tool()
    async def blender_activate_skill(skill_name: str, ctx: Context) -> str:
        """Activate a skill to dynamically load its tool group.

        This registers new MCP tools that become available for immediate use.
        Each skill provides a set of related tools and a workflow guide.

        Use list_skills first to see available skills.

        Args:
            skill_name: Name of the skill to activate (e.g., 'modeling', 'materials', 'animation')
        """
        success, message, tool_names = server.skill_manager.activate_skill(skill_name)

        if not success:
            return f"⚠️ {message}"

        # Send notification with delay (response returns first, avoiding stdio deadlock)
        _schedule_notify(ctx)

        # Get workflow guide
        from blender_mcp.skill_manager import SKILL_DEFINITIONS

        skill_info = SKILL_DEFINITIONS.get(skill_name)
        workflow = skill_info.workflow_guide if skill_info else ""

        result = (
            f"✅ {message}\n\n"
            f"**Registered tools:** {', '.join(sorted(tool_names))}\n\n"
            f"✅ Client notified of tool list change\n\n"
            f"---\n{workflow}"
        )
        return result

    @mcp.tool()
    async def blender_deactivate_skill(skill_name: str, ctx: Context) -> str:
        """Deactivate a skill, removing its tools to free up context.

        Use this when you no longer need a skill's tools, especially
        before activating a different skill group.

        Args:
            skill_name: Name of the skill to deactivate
        """
        success, message = server.skill_manager.deactivate_skill(skill_name)

        if not success:
            return f"⚠️ {message}"

        # Send notification with delay
        _schedule_notify(ctx)

        return f"✅ {message}"
