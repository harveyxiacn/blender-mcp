"""
场景管理工具

提供场景创建、列表、切换、删除等功能。
"""

from typing import TYPE_CHECKING, Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ResponseFormat(str, Enum):
    """响应格式"""
    MARKDOWN = "markdown"
    JSON = "json"


class UnitSystem(str, Enum):
    """单位系统"""
    NONE = "NONE"
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


# ==================== 输入模型 ====================

class SceneCreateInput(BaseModel):
    """创建场景输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="场景名称", min_length=1, max_length=100)
    copy_from: Optional[str] = Field(default=None, description="复制来源场景名称")


class SceneListInput(BaseModel):
    """列出场景输入"""
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式: markdown 或 json"
    )


class SceneGetInfoInput(BaseModel):
    """获取场景信息输入"""
    scene_name: Optional[str] = Field(
        default=None,
        description="场景名称，为空则返回当前场景"
    )


class SceneSwitchInput(BaseModel):
    """切换场景输入"""
    scene_name: str = Field(..., description="要切换到的场景名称")


class SceneDeleteInput(BaseModel):
    """删除场景输入"""
    scene_name: str = Field(..., description="要删除的场景名称")


class SceneSettingsInput(BaseModel):
    """场景设置输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    scene_name: Optional[str] = Field(default=None, description="场景名称")
    frame_start: Optional[int] = Field(default=None, description="起始帧", ge=0)
    frame_end: Optional[int] = Field(default=None, description="结束帧", ge=1)
    fps: Optional[int] = Field(default=None, description="帧率", ge=1, le=120)
    unit_system: Optional[UnitSystem] = Field(default=None, description="单位系统")
    unit_scale: Optional[float] = Field(default=None, description="单位缩放", gt=0)


# ==================== 工具注册 ====================

def register_scene_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册场景管理工具"""
    
    @mcp.tool(
        name="blender_scene_create",
        annotations={
            "title": "创建场景",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_create(params: SceneCreateInput) -> str:
        """在 Blender 中创建新场景。
        
        创建一个新的场景，可以选择从现有场景复制。
        
        Args:
            params: 包含场景名称和可选的复制来源
            
        Returns:
            创建结果的 JSON 字符串
        """
        result = await server.execute_command(
            "scene", "create",
            {"name": params.name, "copy_from": params.copy_from}
        )
        
        if result.get("success"):
            return f"成功创建场景 '{params.name}'"
        else:
            error = result.get("error", {})
            return f"创建场景失败: {error.get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_list",
        annotations={
            "title": "列出场景",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_list(params: SceneListInput) -> str:
        """列出 Blender 中的所有场景。
        
        返回所有场景的列表，包括名称、对象数量等信息。
        
        Args:
            params: 输出格式选项
            
        Returns:
            场景列表（Markdown 或 JSON 格式）
        """
        result = await server.execute_command("scene", "list", {})
        
        if not result.get("success"):
            return f"获取场景列表失败: {result.get('error', {}).get('message', '未知错误')}"
        
        scenes = result.get("data", {}).get("scenes", [])
        
        if params.response_format == ResponseFormat.JSON:
            import json
            return json.dumps({"scenes": scenes, "total": len(scenes)}, indent=2)
        
        # Markdown 格式
        lines = ["# Blender 场景列表", ""]
        lines.append(f"共 {len(scenes)} 个场景")
        lines.append("")
        
        for scene in scenes:
            active = " (当前)" if scene.get("is_active") else ""
            lines.append(f"## {scene['name']}{active}")
            lines.append(f"- 对象数量: {scene.get('objects_count', 0)}")
            lines.append("")
        
        return "\n".join(lines)
    
    @mcp.tool(
        name="blender_scene_get_info",
        annotations={
            "title": "获取场景信息",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_get_info(params: SceneGetInfoInput) -> str:
        """获取场景的详细信息。
        
        返回场景的帧范围、FPS、单位设置等详细信息。
        
        Args:
            params: 场景名称（可选）
            
        Returns:
            场景详细信息
        """
        result = await server.execute_command(
            "scene", "get_info",
            {"scene_name": params.scene_name}
        )
        
        if not result.get("success"):
            return f"获取场景信息失败: {result.get('error', {}).get('message', '未知错误')}"
        
        data = result.get("data", {})
        
        lines = [f"# 场景: {data.get('name', '未知')}", ""]
        lines.append(f"- **帧范围**: {data.get('frame_start', 1)} - {data.get('frame_end', 250)}")
        lines.append(f"- **当前帧**: {data.get('frame_current', 1)}")
        lines.append(f"- **帧率**: {data.get('fps', 24)} FPS")
        lines.append(f"- **对象数量**: {data.get('objects_count', 0)}")
        lines.append(f"- **单位系统**: {data.get('unit_system', 'METRIC')}")
        lines.append(f"- **单位缩放**: {data.get('unit_scale', 1.0)}")
        
        return "\n".join(lines)
    
    @mcp.tool(
        name="blender_scene_switch",
        annotations={
            "title": "切换场景",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_switch(params: SceneSwitchInput) -> str:
        """切换到指定场景。
        
        Args:
            params: 目标场景名称
            
        Returns:
            切换结果
        """
        result = await server.execute_command(
            "scene", "switch",
            {"scene_name": params.scene_name}
        )
        
        if result.get("success"):
            return f"已切换到场景 '{params.scene_name}'"
        else:
            return f"切换场景失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_delete",
        annotations={
            "title": "删除场景",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_delete(params: SceneDeleteInput) -> str:
        """删除指定场景。
        
        注意：不能删除最后一个场景。
        
        Args:
            params: 要删除的场景名称
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "scene", "delete",
            {"scene_name": params.scene_name}
        )
        
        if result.get("success"):
            return f"已删除场景 '{params.scene_name}'"
        else:
            return f"删除场景失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_set_settings",
        annotations={
            "title": "设置场景参数",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_set_settings(params: SceneSettingsInput) -> str:
        """设置场景参数。
        
        可以设置帧范围、帧率、单位系统等。
        
        Args:
            params: 场景设置参数
            
        Returns:
            设置结果
        """
        settings = {}
        if params.frame_start is not None:
            settings["frame_start"] = params.frame_start
        if params.frame_end is not None:
            settings["frame_end"] = params.frame_end
        if params.fps is not None:
            settings["fps"] = params.fps
        if params.unit_system is not None:
            settings["unit_system"] = params.unit_system.value
        if params.unit_scale is not None:
            settings["unit_scale"] = params.unit_scale
        
        if not settings:
            return "没有指定任何设置参数"
        
        result = await server.execute_command(
            "scene", "set_settings",
            {"scene_name": params.scene_name, "settings": settings}
        )
        
        if result.get("success"):
            return f"场景设置已更新"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
