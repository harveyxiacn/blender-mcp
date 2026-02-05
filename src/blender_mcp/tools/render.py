"""
渲染工具

提供渲染设置和渲染功能。
"""

from typing import TYPE_CHECKING, Optional
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class RenderEngine(str, Enum):
    """渲染引擎"""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    EEVEE_NEXT = "BLENDER_EEVEE_NEXT"
    WORKBENCH = "BLENDER_WORKBENCH"


class FileFormat(str, Enum):
    """文件格式"""
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    EXR = "OPEN_EXR"
    BMP = "BMP"


# ==================== 输入模型 ====================

class RenderSettingsInput(BaseModel):
    """渲染设置输入"""
    engine: Optional[RenderEngine] = Field(default=None, description="渲染引擎")
    resolution_x: Optional[int] = Field(default=None, description="水平分辨率", ge=1, le=16384)
    resolution_y: Optional[int] = Field(default=None, description="垂直分辨率", ge=1, le=16384)
    resolution_percentage: Optional[int] = Field(default=None, description="分辨率百分比", ge=1, le=100)
    samples: Optional[int] = Field(default=None, description="采样数", ge=1, le=16384)
    use_denoising: Optional[bool] = Field(default=None, description="使用降噪")
    file_format: Optional[FileFormat] = Field(default=None, description="输出格式")
    output_path: Optional[str] = Field(default=None, description="输出路径")


class RenderImageInput(BaseModel):
    """渲染图像输入"""
    output_path: Optional[str] = Field(default=None, description="输出路径")
    frame: Optional[int] = Field(default=None, description="渲染帧")
    camera: Optional[str] = Field(default=None, description="相机名称")
    write_still: bool = Field(default=True, description="保存图像")


class RenderAnimationInput(BaseModel):
    """渲染动画输入"""
    output_path: str = Field(..., description="输出目录")
    frame_start: Optional[int] = Field(default=None, description="起始帧")
    frame_end: Optional[int] = Field(default=None, description="结束帧")
    frame_step: int = Field(default=1, description="帧步长", ge=1)


class RenderPreviewInput(BaseModel):
    """渲染预览输入"""
    resolution_percentage: int = Field(default=50, description="分辨率百分比", ge=1, le=100)
    samples: int = Field(default=32, description="采样数", ge=1, le=256)


class ViewType(str, Enum):
    """视图类型"""
    PERSP = "PERSP"     # 透视
    FRONT = "FRONT"     # 前视图
    BACK = "BACK"       # 后视图
    LEFT = "LEFT"       # 左视图
    RIGHT = "RIGHT"     # 右视图
    TOP = "TOP"         # 顶视图
    BOTTOM = "BOTTOM"   # 底视图


class GetViewportScreenshotInput(BaseModel):
    """获取视口截图输入"""
    output_path: Optional[str] = Field(default=None, description="输出路径（不提供则使用临时目录）")
    width: int = Field(default=800, description="截图宽度", ge=64, le=4096)
    height: int = Field(default=600, description="截图高度", ge=64, le=4096)
    view_type: Optional[ViewType] = Field(default=None, description="视图类型")
    return_base64: bool = Field(default=False, description="是否返回base64编码的图片数据")


# ==================== 工具注册 ====================

def register_render_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册渲染工具"""
    
    @mcp.tool(
        name="blender_render_settings",
        annotations={
            "title": "设置渲染参数",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_render_settings(params: RenderSettingsInput) -> str:
        """设置渲染参数。
        
        可以设置渲染引擎、分辨率、采样数等。
        
        Args:
            params: 渲染设置
            
        Returns:
            设置结果
        """
        settings = {}
        if params.engine is not None:
            settings["engine"] = params.engine.value
        if params.resolution_x is not None:
            settings["resolution_x"] = params.resolution_x
        if params.resolution_y is not None:
            settings["resolution_y"] = params.resolution_y
        if params.resolution_percentage is not None:
            settings["resolution_percentage"] = params.resolution_percentage
        if params.samples is not None:
            settings["samples"] = params.samples
        if params.use_denoising is not None:
            settings["use_denoising"] = params.use_denoising
        if params.file_format is not None:
            settings["file_format"] = params.file_format.value
        if params.output_path is not None:
            settings["output_path"] = params.output_path
        
        if not settings:
            return "没有指定任何设置"
        
        result = await server.execute_command(
            "render", "settings",
            settings
        )
        
        if result.get("success"):
            return f"渲染设置已更新"
        else:
            return f"设置渲染参数失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_render_image",
        annotations={
            "title": "渲染静态图像",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_render_image(params: RenderImageInput) -> str:
        """渲染静态图像。
        
        Args:
            params: 输出路径、帧号、相机
            
        Returns:
            渲染结果
        """
        result = await server.execute_command(
            "render", "image",
            {
                "output_path": params.output_path,
                "frame": params.frame,
                "camera": params.camera,
                "write_still": params.write_still
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            output = data.get("output_path", params.output_path or "默认路径")
            time = data.get("render_time", "未知")
            return f"渲染完成，输出: {output}，耗时: {time}秒"
        else:
            return f"渲染失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_render_animation",
        annotations={
            "title": "渲染动画",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_render_animation(params: RenderAnimationInput) -> str:
        """渲染动画序列。
        
        Args:
            params: 输出目录、帧范围
            
        Returns:
            渲染结果
        """
        result = await server.execute_command(
            "render", "animation",
            {
                "output_path": params.output_path,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
                "frame_step": params.frame_step
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            frames = data.get("frames_rendered", "未知")
            return f"动画渲染完成，共 {frames} 帧，输出到: {params.output_path}"
        else:
            return f"渲染动画失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_render_preview",
        annotations={
            "title": "渲染预览",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_render_preview(params: RenderPreviewInput) -> str:
        """快速渲染预览图。
        
        使用较低的分辨率和采样数进行快速预览。
        
        Args:
            params: 分辨率百分比和采样数
            
        Returns:
            预览结果
        """
        result = await server.execute_command(
            "render", "preview",
            {
                "resolution_percentage": params.resolution_percentage,
                "samples": params.samples
            }
        )
        
        if result.get("success"):
            return f"预览渲染完成"
        else:
            return f"预览渲染失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_get_viewport_screenshot",
        annotations={
            "title": "获取视口截图",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_get_viewport_screenshot(params: GetViewportScreenshotInput) -> str:
        """获取当前3D视口的截图。
        
        使用OpenGL渲染捕获视口画面，用于调试和预览。
        
        Args:
            params: 输出路径、尺寸、视图类型
            
        Returns:
            截图文件路径信息
        """
        result = await server.execute_command(
            "render", "get_viewport_screenshot",
            {
                "output_path": params.output_path,
                "width": params.width,
                "height": params.height,
                "view_type": params.view_type.value if params.view_type else None,
                "return_base64": params.return_base64
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            lines = ["视口截图已保存"]
            lines.append(f"- 路径: {data.get('output_path', 'N/A')}")
            lines.append(f"- 尺寸: {data.get('width', 0)}x{data.get('height', 0)}")
            lines.append(f"- 文件大小: {data.get('file_size', 0)} 字节")
            
            if params.return_base64 and data.get('base64'):
                lines.append(f"- Base64 数据已包含在响应中")
            
            return "\n".join(lines)
        else:
            return f"截图失败: {result.get('error', {}).get('message', '未知错误')}"
