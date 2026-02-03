"""
预设动画工具

提供预设动画库、动作管理、NLA编辑等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class AnimationPresetApplyInput(BaseModel):
    """应用预设动画输入"""
    armature_name: str = Field(..., description="骨架名称")
    preset: str = Field(
        default="idle",
        description="预设动画: idle, walk, run, jump, wave, celebrate, attack, dance, sit, bow"
    )
    speed: float = Field(default=1.0, description="动画速度倍率", ge=0.1, le=5.0)
    loop: bool = Field(default=True, description="是否循环")


class ActionCreateInput(BaseModel):
    """创建动作输入"""
    action_name: str = Field(..., description="动作名称")
    armature_name: Optional[str] = Field(default=None, description="关联的骨架")
    frame_start: int = Field(default=1, description="起始帧")
    frame_end: int = Field(default=60, description="结束帧")


class ActionLibraryAddInput(BaseModel):
    """添加到动作库输入"""
    action_name: str = Field(..., description="动作名称")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    category: str = Field(default="general", description="分类")


class NLAStripAddInput(BaseModel):
    """添加NLA条带输入"""
    object_name: str = Field(..., description="对象名称")
    action_name: str = Field(..., description="动作名称")
    track_name: str = Field(default="NlaTrack", description="轨道名称")
    start_frame: int = Field(default=1, description="起始帧")
    blend_type: str = Field(default="REPLACE", description="混合类型: REPLACE, ADD, SUBTRACT, MULTIPLY")
    scale: float = Field(default=1.0, description="时间缩放")


class PathAnimationInput(BaseModel):
    """路径动画输入"""
    object_name: str = Field(..., description="对象名称")
    path_name: str = Field(..., description="路径曲线名称")
    duration: int = Field(default=100, description="动画持续帧数")
    follow_rotation: bool = Field(default=True, description="跟随路径旋转")


class AnimationBakeInput(BaseModel):
    """烘焙动画输入"""
    object_name: str = Field(..., description="对象名称")
    frame_start: int = Field(default=1, description="起始帧")
    frame_end: int = Field(default=250, description="结束帧")
    bake_types: List[str] = Field(
        default=["LOCATION", "ROTATION", "SCALE"],
        description="烘焙类型"
    )
    clear_constraints: bool = Field(default=False, description="烘焙后清除约束")


# ==================== 工具注册 ====================

def register_animation_preset_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册预设动画工具"""
    
    @mcp.tool(
        name="blender_animation_preset_apply",
        annotations={
            "title": "应用预设动画",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_animation_preset_apply(params: AnimationPresetApplyInput) -> str:
        """应用预设动画到骨架。
        
        可用预设:
        - idle: 待机呼吸动画
        - walk: 行走循环
        - run: 跑步循环
        - jump: 跳跃
        - wave: 挥手
        - celebrate: 庆祝
        - attack: 攻击
        - dance: 跳舞
        - sit: 坐下
        - bow: 鞠躬
        
        Args:
            params: 骨架名称、预设类型、速度等
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "animation_preset", "apply",
            {
                "armature_name": params.armature_name,
                "preset": params.preset,
                "speed": params.speed,
                "loop": params.loop
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.armature_name}' 应用 {params.preset} 动画"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_action_create",
        annotations={
            "title": "创建动作",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_action_create(params: ActionCreateInput) -> str:
        """创建新的动作。
        
        Args:
            params: 动作名称、帧范围等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "animation_preset", "action_create",
            {
                "action_name": params.action_name,
                "armature_name": params.armature_name,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end
            }
        )
        
        if result.get("success"):
            return f"成功创建动作 '{params.action_name}'"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_nla_strip_add",
        annotations={
            "title": "添加NLA条带",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_nla_strip_add(params: NLAStripAddInput) -> str:
        """添加NLA条带用于动画混合。
        
        Args:
            params: 对象、动作、轨道等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "animation_preset", "nla_add",
            {
                "object_name": params.object_name,
                "action_name": params.action_name,
                "track_name": params.track_name,
                "start_frame": params.start_frame,
                "blend_type": params.blend_type,
                "scale": params.scale
            }
        )
        
        if result.get("success"):
            return f"成功添加 NLA 条带"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_animation_follow_path",
        annotations={
            "title": "路径动画",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_animation_follow_path(params: PathAnimationInput) -> str:
        """让对象沿路径移动。
        
        Args:
            params: 对象、路径、持续时间等
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "animation_preset", "follow_path",
            {
                "object_name": params.object_name,
                "path_name": params.path_name,
                "duration": params.duration,
                "follow_rotation": params.follow_rotation
            }
        )
        
        if result.get("success"):
            return f"成功设置 '{params.object_name}' 沿 '{params.path_name}' 移动"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_animation_bake",
        annotations={
            "title": "烘焙动画",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_animation_bake(params: AnimationBakeInput) -> str:
        """烘焙动画到关键帧。
        
        将约束和程序化动画转换为实际关键帧。
        
        Args:
            params: 对象、帧范围、烘焙类型等
            
        Returns:
            烘焙结果
        """
        result = await server.execute_command(
            "animation_preset", "bake",
            {
                "object_name": params.object_name,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
                "bake_types": params.bake_types,
                "clear_constraints": params.clear_constraints
            }
        )
        
        if result.get("success"):
            frames = params.frame_end - params.frame_start + 1
            return f"成功烘焙 '{params.object_name}' 的动画 ({frames} 帧)"
        else:
            return f"烘焙失败: {result.get('error', {}).get('message', '未知错误')}"
