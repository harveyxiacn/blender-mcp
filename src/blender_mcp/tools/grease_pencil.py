"""
油笔/2D动画工具

提供油笔（Grease Pencil）相关的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class GPencilCreateInput(BaseModel):
    """创建油笔对象"""
    name: str = Field("GPencil", description="对象名称")
    location: List[float] = Field([0, 0, 0], description="位置")
    stroke_depth_order: str = Field("3D", description="深度顺序: 2D, 3D")


class GPencilLayerInput(BaseModel):
    """图层操作"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    action: str = Field("ADD", description="操作: ADD, REMOVE, RENAME, MOVE")
    layer_name: str = Field("Layer", description="图层名称")
    new_name: Optional[str] = Field(None, description="新名称（重命名时）")
    color: Optional[List[float]] = Field(None, description="图层颜色")


class GPencilFrameInput(BaseModel):
    """帧操作"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    layer_name: str = Field("Layer", description="图层名称")
    action: str = Field("ADD", description="操作: ADD, REMOVE, COPY, DUPLICATE")
    frame_number: int = Field(1, description="帧号")
    target_frame: Optional[int] = Field(None, description="目标帧（复制时）")


class GPencilDrawInput(BaseModel):
    """绘制笔触"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    layer_name: str = Field("Layer", description="图层名称")
    points: List[List[float]] = Field(
        ...,
        description="点列表 [[x,y,z,pressure,strength], ...]"
    )
    material_index: int = Field(0, description="材质索引")
    line_width: int = Field(10, description="线宽")


class GPencilMaterialInput(BaseModel):
    """油笔材质"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    name: str = Field("GPMaterial", description="材质名称")
    mode: str = Field("LINE", description="模式: LINE, DOTS, BOX, FILL")
    stroke_color: List[float] = Field([0, 0, 0, 1], description="笔触颜色")
    fill_color: Optional[List[float]] = Field(None, description="填充颜色")


class GPencilModifierInput(BaseModel):
    """油笔修改器"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    modifier_type: str = Field(
        "SMOOTH",
        description="修改器类型: SMOOTH, NOISE, THICKNESS, TINT, OFFSET, OPACITY, etc."
    )
    modifier_name: Optional[str] = Field(None, description="修改器名称")
    settings: Optional[Dict[str, Any]] = Field(None, description="修改器设置")


class GPencilEffectInput(BaseModel):
    """油笔特效"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    effect_type: str = Field(
        "BLUR",
        description="特效类型: BLUR, COLORIZE, FLIP, GLOW, LIGHT, PIXELATE, RIM, SHADOW, SWIRL, WAVE"
    )
    effect_name: Optional[str] = Field(None, description="特效名称")


class GPencilConvertInput(BaseModel):
    """转换"""
    gpencil_name: str = Field(..., description="油笔对象名称")
    target_type: str = Field("CURVE", description="目标类型: CURVE, MESH")
    keep_original: bool = Field(True, description="保留原对象")


# ============ 工具注册 ============

def register_grease_pencil_tools(mcp: FastMCP, server):
    """注册油笔工具"""
    
    @mcp.tool()
    async def blender_gpencil_create(
        name: str = "GPencil",
        location: List[float] = [0, 0, 0],
        stroke_depth_order: str = "3D"
    ) -> Dict[str, Any]:
        """
        创建油笔对象
        
        Args:
            name: 对象名称
            location: 位置 [x, y, z]
            stroke_depth_order: 深度顺序 (2D或3D)
        """
        params = GPencilCreateInput(
            name=name,
            location=location,
            stroke_depth_order=stroke_depth_order
        )
        return await server.send_command("gpencil", "create", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_layer(
        gpencil_name: str,
        action: str = "ADD",
        layer_name: str = "Layer",
        new_name: Optional[str] = None,
        color: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        油笔图层操作
        
        Args:
            gpencil_name: 油笔对象名称
            action: 操作类型 (ADD, REMOVE, RENAME, MOVE)
            layer_name: 图层名称
            new_name: 新名称（重命名时使用）
            color: 图层颜色 [R,G,B]
        """
        params = GPencilLayerInput(
            gpencil_name=gpencil_name,
            action=action,
            layer_name=layer_name,
            new_name=new_name,
            color=color
        )
        return await server.send_command("gpencil", "layer", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_frame(
        gpencil_name: str,
        layer_name: str = "Layer",
        action: str = "ADD",
        frame_number: int = 1,
        target_frame: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        油笔帧操作
        
        Args:
            gpencil_name: 油笔对象名称
            layer_name: 图层名称
            action: 操作类型 (ADD, REMOVE, COPY, DUPLICATE)
            frame_number: 帧号
            target_frame: 目标帧（复制时使用）
        """
        params = GPencilFrameInput(
            gpencil_name=gpencil_name,
            layer_name=layer_name,
            action=action,
            frame_number=frame_number,
            target_frame=target_frame
        )
        return await server.send_command("gpencil", "frame", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_draw(
        gpencil_name: str,
        layer_name: str,
        points: List[List[float]],
        material_index: int = 0,
        line_width: int = 10
    ) -> Dict[str, Any]:
        """
        绘制油笔笔触
        
        Args:
            gpencil_name: 油笔对象名称
            layer_name: 图层名称
            points: 点列表 [[x,y,z,pressure,strength], ...]
            material_index: 材质索引
            line_width: 线宽
        """
        params = GPencilDrawInput(
            gpencil_name=gpencil_name,
            layer_name=layer_name,
            points=points,
            material_index=material_index,
            line_width=line_width
        )
        return await server.send_command("gpencil", "draw", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_material(
        gpencil_name: str,
        name: str = "GPMaterial",
        mode: str = "LINE",
        stroke_color: List[float] = [0, 0, 0, 1],
        fill_color: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        创建油笔材质
        
        Args:
            gpencil_name: 油笔对象名称
            name: 材质名称
            mode: 模式 (LINE, DOTS, BOX, FILL)
            stroke_color: 笔触颜色 [R,G,B,A]
            fill_color: 填充颜色 [R,G,B,A]
        """
        params = GPencilMaterialInput(
            gpencil_name=gpencil_name,
            name=name,
            mode=mode,
            stroke_color=stroke_color,
            fill_color=fill_color
        )
        return await server.send_command("gpencil", "material", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_modifier(
        gpencil_name: str,
        modifier_type: str = "SMOOTH",
        modifier_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        添加油笔修改器
        
        Args:
            gpencil_name: 油笔对象名称
            modifier_type: 修改器类型 (SMOOTH, NOISE, THICKNESS, TINT, OFFSET等)
            modifier_name: 修改器名称
            settings: 修改器设置
        """
        params = GPencilModifierInput(
            gpencil_name=gpencil_name,
            modifier_type=modifier_type,
            modifier_name=modifier_name,
            settings=settings
        )
        return await server.send_command("gpencil", "modifier", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_effect(
        gpencil_name: str,
        effect_type: str = "BLUR",
        effect_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加油笔特效
        
        Args:
            gpencil_name: 油笔对象名称
            effect_type: 特效类型 (BLUR, GLOW, SHADOW, RIM, WAVE等)
            effect_name: 特效名称
        """
        params = GPencilEffectInput(
            gpencil_name=gpencil_name,
            effect_type=effect_type,
            effect_name=effect_name
        )
        return await server.send_command("gpencil", "effect", params.model_dump())
    
    @mcp.tool()
    async def blender_gpencil_convert(
        gpencil_name: str,
        target_type: str = "CURVE",
        keep_original: bool = True
    ) -> Dict[str, Any]:
        """
        转换油笔为其他类型
        
        Args:
            gpencil_name: 油笔对象名称
            target_type: 目标类型 (CURVE或MESH)
            keep_original: 是否保留原对象
        """
        params = GPencilConvertInput(
            gpencil_name=gpencil_name,
            target_type=target_type,
            keep_original=keep_original
        )
        return await server.send_command("gpencil", "convert", params.model_dump())
