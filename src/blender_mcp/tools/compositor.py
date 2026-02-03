"""
合成器工具

提供后期合成、颜色校正、特效等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class CompositorEnableInput(BaseModel):
    """启用合成器输入"""
    enable: bool = Field(default=True, description="是否启用")
    use_backdrop: bool = Field(default=True, description="使用背景板预览")


class CompositorPresetInput(BaseModel):
    """合成器预设输入"""
    preset: str = Field(
        default="color_correction",
        description="预设: color_correction, bloom, vignette, blur, sharpen, film_grain, chromatic_aberration"
    )
    intensity: float = Field(default=1.0, description="效果强度", ge=0, le=2)


class CompositorColorBalanceInput(BaseModel):
    """颜色平衡输入"""
    shadows: Optional[List[float]] = Field(default=None, description="阴影颜色 RGB")
    midtones: Optional[List[float]] = Field(default=None, description="中间调颜色 RGB")
    highlights: Optional[List[float]] = Field(default=None, description="高光颜色 RGB")


class CompositorBlurInput(BaseModel):
    """模糊输入"""
    blur_type: str = Field(default="FAST_GAUSS", description="类型: FLAT, TENT, QUAD, CUBIC, GAUSS, FAST_GAUSS")
    size_x: float = Field(default=10.0, description="X方向大小", ge=0)
    size_y: float = Field(default=10.0, description="Y方向大小", ge=0)


class RenderLayerInput(BaseModel):
    """渲染层输入"""
    layer_name: str = Field(default="ViewLayer", description="视图层名称")
    use_pass_combined: bool = Field(default=True, description="组合通道")
    use_pass_z: bool = Field(default=False, description="Z深度通道")
    use_pass_normal: bool = Field(default=False, description="法线通道")
    use_pass_ao: bool = Field(default=False, description="环境光遮蔽通道")


# ==================== 工具注册 ====================

def register_compositor_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册合成器工具"""
    
    @mcp.tool(
        name="blender_compositor_enable",
        annotations={
            "title": "启用合成器",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_compositor_enable(params: CompositorEnableInput) -> str:
        """启用或禁用合成器。
        
        Args:
            params: 是否启用、是否使用背景板
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "compositor", "enable",
            {
                "enable": params.enable,
                "use_backdrop": params.use_backdrop
            }
        )
        
        if result.get("success"):
            status = "启用" if params.enable else "禁用"
            return f"成功{status}合成器"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_compositor_preset",
        annotations={
            "title": "应用合成器预设",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_compositor_preset(params: CompositorPresetInput) -> str:
        """应用合成器效果预设。
        
        可用预设:
        - color_correction: 颜色校正
        - bloom: 辉光效果
        - vignette: 暗角
        - blur: 模糊
        - sharpen: 锐化
        - film_grain: 胶片颗粒
        - chromatic_aberration: 色差
        
        Args:
            params: 预设类型、强度
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "compositor", "preset",
            {
                "preset": params.preset,
                "intensity": params.intensity
            }
        )
        
        if result.get("success"):
            return f"成功应用 {params.preset} 效果"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_compositor_color_balance",
        annotations={
            "title": "颜色平衡",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_compositor_color_balance(params: CompositorColorBalanceInput) -> str:
        """调整颜色平衡。
        
        Args:
            params: 阴影、中间调、高光颜色
            
        Returns:
            调整结果
        """
        result = await server.execute_command(
            "compositor", "color_balance",
            {
                "shadows": params.shadows,
                "midtones": params.midtones,
                "highlights": params.highlights
            }
        )
        
        if result.get("success"):
            return f"成功调整颜色平衡"
        else:
            return f"调整失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_compositor_blur",
        annotations={
            "title": "添加模糊",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_compositor_blur(params: CompositorBlurInput) -> str:
        """添加模糊效果。
        
        Args:
            params: 模糊类型、大小
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "compositor", "blur",
            {
                "blur_type": params.blur_type,
                "size_x": params.size_x,
                "size_y": params.size_y
            }
        )
        
        if result.get("success"):
            return f"成功添加模糊效果"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_render_layer_setup",
        annotations={
            "title": "设置渲染层",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_render_layer_setup(params: RenderLayerInput) -> str:
        """设置渲染层通道。
        
        Args:
            params: 各种通道开关
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "compositor", "render_layer",
            {
                "layer_name": params.layer_name,
                "use_pass_combined": params.use_pass_combined,
                "use_pass_z": params.use_pass_z,
                "use_pass_normal": params.use_pass_normal,
                "use_pass_ao": params.use_pass_ao
            }
        )
        
        if result.get("success"):
            return f"成功设置渲染层 '{params.layer_name}'"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
