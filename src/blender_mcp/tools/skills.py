"""
Skill 管理工具

提供按需加载/卸载工具组的 MCP 工具:
- list_skills: 列出所有可用 Skill 及状态
- activate_skill: 激活 Skill, 动态加载工具组
- deactivate_skill: 停用 Skill, 移除工具组
"""

import asyncio
import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

logger = logging.getLogger(__name__)


# ==================== 输入模型 ====================

class ActivateSkillInput(BaseModel):
    """激活 Skill 输入"""
    skill_name: str = Field(
        ...,
        description="Skill name to activate. Use list_skills to see available options."
    )


class DeactivateSkillInput(BaseModel):
    """停用 Skill 输入"""
    skill_name: str = Field(
        ...,
        description="Skill name to deactivate."
    )


# 去抖：保存上一个待发送的通知任务，新的到来时取消旧的
_pending_notify_task: asyncio.Task | None = None


def _schedule_notify(ctx: Context) -> None:
    """去抖发送 tools/list_changed 通知
    
    关键设计：
    1. 不在 tool handler 内部 await，响应先返回客户端
    2. 每次调度新通知时取消之前未发送的通知（去抖）
    3. 连续 8 次 activate/deactivate 只会发送最后 1 个通知
    4. 延迟 0.5 秒确保响应已被客户端读取
    """
    global _pending_notify_task
    
    # 取消之前未完成的通知任务
    if _pending_notify_task and not _pending_notify_task.done():
        _pending_notify_task.cancel()
    
    async def _delayed_notify():
        await asyncio.sleep(0.5)
        try:
            await asyncio.wait_for(
                ctx.session.send_tool_list_changed(),
                timeout=3.0
            )
        except asyncio.CancelledError:
            pass  # 被新通知取消，正常行为
        except Exception as e:
            logger.debug(f"tool_list_changed notification skipped: {e}")
    
    try:
        _pending_notify_task = asyncio.get_event_loop().create_task(_delayed_notify())
    except Exception:
        pass


# ==================== 注册函数 ====================

def register_skill_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册 Skill 管理工具"""
    
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
        
        # 延迟发送通知（响应先返回，避免 stdio 死锁）
        _schedule_notify(ctx)
        
        # 获取工作流指引
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
        
        # 延迟发送通知
        _schedule_notify(ctx)
        
        return f"✅ {message}"
