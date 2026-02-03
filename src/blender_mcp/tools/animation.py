"""
动画工具

提供关键帧动画和时间线控制功能。
"""

from typing import TYPE_CHECKING, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class InterpolationType(str, Enum):
    """插值类型"""
    CONSTANT = "CONSTANT"
    LINEAR = "LINEAR"
    BEZIER = "BEZIER"
    SINE = "SINE"
    QUAD = "QUAD"
    CUBIC = "CUBIC"
    QUART = "QUART"
    QUINT = "QUINT"
    EXPO = "EXPO"
    CIRC = "CIRC"
    BACK = "BACK"
    BOUNCE = "BOUNCE"
    ELASTIC = "ELASTIC"


# ==================== 输入模型 ====================

class KeyframeInsertInput(BaseModel):
    """插入关键帧输入"""
    object_name: str = Field(..., description="对象名称")
    data_path: str = Field(..., description="数据路径（如 location, rotation_euler, scale）")
    frame: Optional[int] = Field(default=None, description="帧编号，为空则使用当前帧")
    value: Optional[Any] = Field(default=None, description="属性值")


class KeyframeDeleteInput(BaseModel):
    """删除关键帧输入"""
    object_name: str = Field(..., description="对象名称")
    data_path: str = Field(..., description="数据路径")
    frame: Optional[int] = Field(default=None, description="帧编号")


class AnimationSetInterpolationInput(BaseModel):
    """设置插值类型输入"""
    object_name: str = Field(..., description="对象名称")
    interpolation: InterpolationType = Field(..., description="插值类型")


class TimelineSetRangeInput(BaseModel):
    """设置时间线范围输入"""
    frame_start: Optional[int] = Field(default=None, description="起始帧", ge=0)
    frame_end: Optional[int] = Field(default=None, description="结束帧", ge=1)
    frame_current: Optional[int] = Field(default=None, description="当前帧", ge=0)


class TimelineGotoFrameInput(BaseModel):
    """跳转到帧输入"""
    frame: int = Field(..., description="目标帧", ge=0)


class AnimationBakeInput(BaseModel):
    """烘焙动画输入"""
    object_name: str = Field(..., description="对象名称")
    frame_start: Optional[int] = Field(default=None, description="起始帧")
    frame_end: Optional[int] = Field(default=None, description="结束帧")
    step: int = Field(default=1, description="帧步长", ge=1)
    bake_location: bool = Field(default=True, description="烘焙位置")
    bake_rotation: bool = Field(default=True, description="烘焙旋转")
    bake_scale: bool = Field(default=True, description="烘焙缩放")


# ==================== 工具注册 ====================

def register_animation_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册动画工具"""
    
    @mcp.tool(
        name="blender_keyframe_insert",
        annotations={
            "title": "插入关键帧",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_keyframe_insert(params: KeyframeInsertInput) -> str:
        """插入关键帧。
        
        为对象的指定属性插入关键帧。
        
        常用数据路径：
        - location: 位置
        - rotation_euler: 欧拉旋转
        - scale: 缩放
        - location[0]: X 位置
        
        Args:
            params: 对象名称、数据路径、帧号、值
            
        Returns:
            插入结果
        """
        result = await server.execute_command(
            "animation", "keyframe_insert",
            {
                "object_name": params.object_name,
                "data_path": params.data_path,
                "frame": params.frame,
                "value": params.value
            }
        )
        
        if result.get("success"):
            frame = params.frame or result.get("data", {}).get("frame", "当前")
            return f"已在第 {frame} 帧为 '{params.object_name}' 的 {params.data_path} 插入关键帧"
        else:
            return f"插入关键帧失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_keyframe_delete",
        annotations={
            "title": "删除关键帧",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_keyframe_delete(params: KeyframeDeleteInput) -> str:
        """删除关键帧。
        
        Args:
            params: 对象名称、数据路径、帧号
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "animation", "keyframe_delete",
            {
                "object_name": params.object_name,
                "data_path": params.data_path,
                "frame": params.frame
            }
        )
        
        if result.get("success"):
            return f"已删除关键帧"
        else:
            return f"删除关键帧失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_animation_set_interpolation",
        annotations={
            "title": "设置插值类型",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_animation_set_interpolation(params: AnimationSetInterpolationInput) -> str:
        """设置关键帧的插值类型。
        
        支持的插值类型包括：常量、线性、贝塞尔、缓动等。
        
        Args:
            params: 对象名称和插值类型
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "animation", "set_interpolation",
            {
                "object_name": params.object_name,
                "interpolation": params.interpolation.value
            }
        )
        
        if result.get("success"):
            return f"已将 '{params.object_name}' 的插值类型设为 {params.interpolation.value}"
        else:
            return f"设置插值失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_timeline_set_range",
        annotations={
            "title": "设置时间线范围",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_timeline_set_range(params: TimelineSetRangeInput) -> str:
        """设置时间线范围。
        
        可以设置起始帧、结束帧和当前帧。
        
        Args:
            params: 帧范围设置
            
        Returns:
            设置结果
        """
        settings = {}
        if params.frame_start is not None:
            settings["frame_start"] = params.frame_start
        if params.frame_end is not None:
            settings["frame_end"] = params.frame_end
        if params.frame_current is not None:
            settings["frame_current"] = params.frame_current
        
        if not settings:
            return "没有指定任何设置"
        
        result = await server.execute_command(
            "animation", "timeline_set_range",
            settings
        )
        
        if result.get("success"):
            return f"时间线范围已更新"
        else:
            return f"设置时间线失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_timeline_goto_frame",
        annotations={
            "title": "跳转到帧",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_timeline_goto_frame(params: TimelineGotoFrameInput) -> str:
        """跳转到指定帧。
        
        Args:
            params: 目标帧号
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "animation", "goto_frame",
            {"frame": params.frame}
        )
        
        if result.get("success"):
            return f"已跳转到第 {params.frame} 帧"
        else:
            return f"跳转失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_animation_bake",
        annotations={
            "title": "烘焙动画",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_animation_bake(params: AnimationBakeInput) -> str:
        """烘焙动画。
        
        将约束、驱动器等转换为关键帧动画。
        
        Args:
            params: 烘焙参数
            
        Returns:
            烘焙结果
        """
        result = await server.execute_command(
            "animation", "bake",
            {
                "object_name": params.object_name,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
                "step": params.step,
                "bake_location": params.bake_location,
                "bake_rotation": params.bake_rotation,
                "bake_scale": params.bake_scale
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.object_name}' 烘焙动画"
        else:
            return f"烘焙动画失败: {result.get('error', {}).get('message', '未知错误')}"
