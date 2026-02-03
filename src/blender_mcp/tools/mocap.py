"""
动作捕捉工具

提供动作捕捉数据导入和处理的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class MocapImportInput(BaseModel):
    """导入动捕数据"""
    filepath: str = Field(..., description="动捕文件路径 (.bvh, .fbx)")
    target_armature: Optional[str] = Field(None, description="目标骨架名称")
    scale: float = Field(1.0, description="缩放比例")
    frame_start: int = Field(1, description="开始帧")
    use_fps_scale: bool = Field(False, description="使用FPS缩放")


class MocapRetargetInput(BaseModel):
    """重定向动作"""
    source_armature: str = Field(..., description="源骨架名称")
    target_armature: str = Field(..., description="目标骨架名称")
    bone_mapping: Optional[Dict[str, str]] = Field(None, description="骨骼映射")


class MocapCleanInput(BaseModel):
    """清理动作数据"""
    armature_name: str = Field(..., description="骨架名称")
    action_name: Optional[str] = Field(None, description="动作名称")
    threshold: float = Field(0.001, description="清理阈值")
    remove_noise: bool = Field(True, description="移除噪点")


class MocapBlendInput(BaseModel):
    """混合动作"""
    armature_name: str = Field(..., description="骨架名称")
    action1: str = Field(..., description="动作1名称")
    action2: str = Field(..., description="动作2名称")
    blend_factor: float = Field(0.5, description="混合因子 (0-1)")
    output_name: str = Field("BlendedAction", description="输出动作名称")


class MocapBakeInput(BaseModel):
    """烘焙动作"""
    armature_name: str = Field(..., description="骨架名称")
    frame_start: int = Field(1, description="开始帧")
    frame_end: int = Field(250, description="结束帧")
    only_selected: bool = Field(False, description="只烘焙选中的骨骼")
    visual_keying: bool = Field(True, description="视觉关键帧")


# ============ 工具注册 ============

def register_mocap_tools(mcp: FastMCP, server):
    """注册动作捕捉工具"""
    
    @mcp.tool()
    async def blender_mocap_import(
        filepath: str,
        target_armature: Optional[str] = None,
        scale: float = 1.0,
        frame_start: int = 1,
        use_fps_scale: bool = False
    ) -> Dict[str, Any]:
        """
        导入动作捕捉数据
        
        Args:
            filepath: 动捕文件路径 (.bvh, .fbx)
            target_armature: 目标骨架名称
            scale: 缩放比例
            frame_start: 开始帧
            use_fps_scale: 使用FPS缩放
        """
        params = MocapImportInput(
            filepath=filepath,
            target_armature=target_armature,
            scale=scale,
            frame_start=frame_start,
            use_fps_scale=use_fps_scale
        )
        return await server.send_command("mocap", "import", params.model_dump())
    
    @mcp.tool()
    async def blender_mocap_retarget(
        source_armature: str,
        target_armature: str,
        bone_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        重定向动作到另一个骨架
        
        Args:
            source_armature: 源骨架名称
            target_armature: 目标骨架名称
            bone_mapping: 骨骼名称映射字典
        """
        params = MocapRetargetInput(
            source_armature=source_armature,
            target_armature=target_armature,
            bone_mapping=bone_mapping
        )
        return await server.send_command("mocap", "retarget", params.model_dump())
    
    @mcp.tool()
    async def blender_mocap_clean(
        armature_name: str,
        action_name: Optional[str] = None,
        threshold: float = 0.001,
        remove_noise: bool = True
    ) -> Dict[str, Any]:
        """
        清理动作数据噪点
        
        Args:
            armature_name: 骨架名称
            action_name: 动作名称（为空则使用当前动作）
            threshold: 清理阈值
            remove_noise: 移除噪点
        """
        params = MocapCleanInput(
            armature_name=armature_name,
            action_name=action_name,
            threshold=threshold,
            remove_noise=remove_noise
        )
        return await server.send_command("mocap", "clean", params.model_dump())
    
    @mcp.tool()
    async def blender_mocap_blend(
        armature_name: str,
        action1: str,
        action2: str,
        blend_factor: float = 0.5,
        output_name: str = "BlendedAction"
    ) -> Dict[str, Any]:
        """
        混合两个动作
        
        Args:
            armature_name: 骨架名称
            action1: 第一个动作名称
            action2: 第二个动作名称
            blend_factor: 混合因子 (0=全action1, 1=全action2)
            output_name: 输出动作名称
        """
        params = MocapBlendInput(
            armature_name=armature_name,
            action1=action1,
            action2=action2,
            blend_factor=blend_factor,
            output_name=output_name
        )
        return await server.send_command("mocap", "blend", params.model_dump())
    
    @mcp.tool()
    async def blender_mocap_bake(
        armature_name: str,
        frame_start: int = 1,
        frame_end: int = 250,
        only_selected: bool = False,
        visual_keying: bool = True
    ) -> Dict[str, Any]:
        """
        烘焙动作到关键帧
        
        Args:
            armature_name: 骨架名称
            frame_start: 开始帧
            frame_end: 结束帧
            only_selected: 只烘焙选中的骨骼
            visual_keying: 使用视觉关键帧
        """
        params = MocapBakeInput(
            armature_name=armature_name,
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=only_selected,
            visual_keying=visual_keying
        )
        return await server.send_command("mocap", "bake", params.model_dump())
