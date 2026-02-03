"""
视频编辑工具

提供视频剪辑、效果、渲染等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class VSEAddStripInput(BaseModel):
    """添加条带输入"""
    strip_type: str = Field(
        default="MOVIE",
        description="条带类型: MOVIE, IMAGE, SOUND, SCENE, COLOR, TEXT"
    )
    filepath: Optional[str] = Field(default=None, description="文件路径 (视频/图像/音频)")
    channel: int = Field(default=1, description="通道", ge=1, le=128)
    start_frame: int = Field(default=1, description="起始帧")
    # 特定类型参数
    text: Optional[str] = Field(default=None, description="文本内容 (TEXT类型)")
    color: Optional[List[float]] = Field(default=None, description="颜色 RGBA (COLOR类型)")
    scene_name: Optional[str] = Field(default=None, description="场景名称 (SCENE类型)")


class VSECutInput(BaseModel):
    """剪切条带输入"""
    channel: int = Field(..., description="通道")
    frame: int = Field(..., description="剪切帧")
    cut_type: str = Field(default="SOFT", description="剪切类型: SOFT, HARD")


class VSETransformInput(BaseModel):
    """变换条带输入"""
    strip_name: str = Field(..., description="条带名称")
    position: Optional[List[float]] = Field(default=None, description="位置 [x, y]")
    scale: Optional[List[float]] = Field(default=None, description="缩放 [x, y]")
    rotation: Optional[float] = Field(default=None, description="旋转角度")
    opacity: Optional[float] = Field(default=None, description="不透明度", ge=0, le=1)


class VSEEffectInput(BaseModel):
    """添加效果输入"""
    effect_type: str = Field(
        default="CROSS",
        description="效果类型: CROSS, ADD, SUBTRACT, MULTIPLY, GAMMA_CROSS, WIPE, TRANSFORM, SPEED, GLOW"
    )
    channel: int = Field(default=1, description="通道")
    start_frame: int = Field(default=1, description="起始帧")
    end_frame: int = Field(default=30, description="结束帧")
    seq1_name: Optional[str] = Field(default=None, description="第一个序列名称")
    seq2_name: Optional[str] = Field(default=None, description="第二个序列名称")


class VSETextInput(BaseModel):
    """文本条带输入"""
    text: str = Field(..., description="文本内容")
    channel: int = Field(default=1, description="通道")
    start_frame: int = Field(default=1, description="起始帧")
    duration: int = Field(default=100, description="持续帧数")
    font_size: float = Field(default=60.0, description="字体大小")
    color: Optional[List[float]] = Field(default=None, description="颜色 RGBA")
    location: Optional[List[float]] = Field(default=None, description="位置 [x, y]")


class VSERenderInput(BaseModel):
    """渲染视频输入"""
    output_path: str = Field(..., description="输出路径")
    format: str = Field(default="MPEG4", description="格式: MPEG4, AVI, QUICKTIME")
    codec: str = Field(default="H264", description="编解码器: H264, MPEG4, PNG")
    quality: int = Field(default=90, description="质量", ge=1, le=100)


# ==================== 工具注册 ====================

def register_video_editing_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册视频编辑工具"""
    
    @mcp.tool(
        name="blender_vse_add_strip",
        annotations={
            "title": "添加视频条带",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_vse_add_strip(params: VSEAddStripInput) -> str:
        """在视频序列编辑器中添加条带。
        
        支持类型:
        - MOVIE: 视频文件
        - IMAGE: 图像序列
        - SOUND: 音频文件
        - SCENE: Blender场景
        - COLOR: 纯色条带
        - TEXT: 文本条带
        
        Args:
            params: 条带类型、文件路径、通道等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "vse", "add_strip",
            {
                "strip_type": params.strip_type,
                "filepath": params.filepath,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "text": params.text,
                "color": params.color,
                "scene_name": params.scene_name
            }
        )
        
        if result.get("success"):
            name = result.get("data", {}).get("strip_name", "")
            return f"成功添加条带 '{name}'"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vse_cut",
        annotations={
            "title": "剪切条带",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_cut(params: VSECutInput) -> str:
        """在指定帧剪切条带。
        
        Args:
            params: 通道、帧位置、剪切类型
            
        Returns:
            剪切结果
        """
        result = await server.execute_command(
            "vse", "cut",
            {
                "channel": params.channel,
                "frame": params.frame,
                "cut_type": params.cut_type
            }
        )
        
        if result.get("success"):
            return f"成功在帧 {params.frame} 剪切"
        else:
            return f"剪切失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vse_transform",
        annotations={
            "title": "变换条带",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_vse_transform(params: VSETransformInput) -> str:
        """变换视频条带（位置、缩放、旋转、透明度）。
        
        Args:
            params: 条带名称、位置、缩放等
            
        Returns:
            变换结果
        """
        result = await server.execute_command(
            "vse", "transform",
            {
                "strip_name": params.strip_name,
                "position": params.position,
                "scale": params.scale,
                "rotation": params.rotation,
                "opacity": params.opacity
            }
        )
        
        if result.get("success"):
            return f"成功变换条带 '{params.strip_name}'"
        else:
            return f"变换失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vse_add_effect",
        annotations={
            "title": "添加视频效果",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_add_effect(params: VSEEffectInput) -> str:
        """添加视频效果（转场、叠加等）。
        
        Args:
            params: 效果类型、通道、帧范围
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "vse", "add_effect",
            {
                "effect_type": params.effect_type,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "end_frame": params.end_frame,
                "seq1_name": params.seq1_name,
                "seq2_name": params.seq2_name
            }
        )
        
        if result.get("success"):
            return f"成功添加 {params.effect_type} 效果"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vse_add_text",
        annotations={
            "title": "添加文本",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_add_text(params: VSETextInput) -> str:
        """添加文本条带。
        
        Args:
            params: 文本内容、字体大小、颜色等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "vse", "add_text",
            {
                "text": params.text,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "duration": params.duration,
                "font_size": params.font_size,
                "color": params.color,
                "location": params.location
            }
        )
        
        if result.get("success"):
            return f"成功添加文本 '{params.text}'"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vse_render",
        annotations={
            "title": "渲染视频",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_vse_render(params: VSERenderInput) -> str:
        """渲染视频序列。
        
        Args:
            params: 输出路径、格式、编码等
            
        Returns:
            渲染结果
        """
        result = await server.execute_command(
            "vse", "render",
            {
                "output_path": params.output_path,
                "format": params.format,
                "codec": params.codec,
                "quality": params.quality
            }
        )
        
        if result.get("success"):
            return f"视频渲染完成: {params.output_path}"
        else:
            return f"渲染失败: {result.get('error', {}).get('message', '未知错误')}"
