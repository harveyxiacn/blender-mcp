"""
纹理绘制工具

提供纹理绘制相关的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class TexturePaintModeInput(BaseModel):
    """进入/退出纹理绘制模式"""
    object_name: str = Field(..., description="对象名称")
    enable: bool = Field(True, description="是否进入纹理绘制模式")


class TextureCreateInput(BaseModel):
    """创建新纹理"""
    name: str = Field(..., description="纹理名称")
    width: int = Field(1024, description="宽度")
    height: int = Field(1024, description="高度")
    color: List[float] = Field([0.0, 0.0, 0.0, 1.0], description="初始颜色 [R,G,B,A]")
    alpha: bool = Field(True, description="是否有Alpha通道")
    float_buffer: bool = Field(False, description="是否使用32位浮点")


class TexturePaintBrushInput(BaseModel):
    """设置绘制笔刷"""
    brush_type: str = Field("DRAW", description="笔刷类型: DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK")
    color: List[float] = Field([1.0, 1.0, 1.0], description="颜色 [R,G,B]")
    radius: float = Field(50.0, description="笔刷半径")
    strength: float = Field(1.0, description="笔刷强度 (0-1)")
    blend: str = Field("MIX", description="混合模式: MIX, ADD, SUBTRACT, MULTIPLY, etc.")


class TexturePaintStrokeInput(BaseModel):
    """执行绘制笔触"""
    object_name: str = Field(..., description="对象名称")
    uv_points: List[List[float]] = Field(
        ...,
        description="UV坐标点列表 [[u,v,pressure], ...]"
    )
    color: Optional[List[float]] = Field(None, description="颜色 [R,G,B]")


class TexturePaintFillInput(BaseModel):
    """填充颜色"""
    object_name: str = Field(..., description="对象名称")
    color: List[float] = Field([1.0, 1.0, 1.0, 1.0], description="填充颜色 [R,G,B,A]")
    texture_slot: int = Field(0, description="纹理槽索引")


class TextureBakeInput(BaseModel):
    """烘焙纹理"""
    object_name: str = Field(..., description="对象名称")
    bake_type: str = Field(
        "DIFFUSE",
        description="烘焙类型: DIFFUSE, AO, SHADOW, NORMAL, UV, EMIT, ENVIRONMENT, COMBINED"
    )
    width: int = Field(1024, description="输出宽度")
    height: int = Field(1024, description="输出高度")
    margin: int = Field(16, description="边缘扩展")
    output_path: Optional[str] = Field(None, description="输出路径")


class TextureSlotInput(BaseModel):
    """纹理槽管理"""
    object_name: str = Field(..., description="对象名称")
    action: str = Field("ADD", description="操作: ADD, REMOVE, SELECT")
    texture_name: Optional[str] = Field(None, description="纹理名称")
    slot_index: int = Field(0, description="槽索引")


class TextureSaveInput(BaseModel):
    """保存纹理"""
    texture_name: str = Field(..., description="纹理名称")
    filepath: str = Field(..., description="保存路径")
    file_format: str = Field("PNG", description="文件格式: PNG, JPEG, TIFF, BMP, OPEN_EXR")


# ============ 工具注册 ============

def register_texture_painting_tools(mcp: FastMCP, server):
    """注册纹理绘制工具"""
    
    @mcp.tool()
    async def blender_texture_paint_mode(
        object_name: str,
        enable: bool = True
    ) -> Dict[str, Any]:
        """
        进入或退出纹理绘制模式
        
        Args:
            object_name: 要绘制的对象名称
            enable: True进入纹理绘制模式，False退出
        """
        params = TexturePaintModeInput(
            object_name=object_name,
            enable=enable
        )
        return await server.send_command("texture_paint", "mode", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_create(
        name: str,
        width: int = 1024,
        height: int = 1024,
        color: List[float] = [0.0, 0.0, 0.0, 1.0],
        alpha: bool = True,
        float_buffer: bool = False
    ) -> Dict[str, Any]:
        """
        创建新纹理
        
        Args:
            name: 纹理名称
            width: 宽度（像素）
            height: 高度（像素）
            color: 初始颜色 [R,G,B,A]
            alpha: 是否有Alpha通道
            float_buffer: 是否使用32位浮点精度
        """
        params = TextureCreateInput(
            name=name,
            width=width,
            height=height,
            color=color,
            alpha=alpha,
            float_buffer=float_buffer
        )
        return await server.send_command("texture_paint", "create", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_paint_set_brush(
        brush_type: str = "DRAW",
        color: List[float] = [1.0, 1.0, 1.0],
        radius: float = 50.0,
        strength: float = 1.0,
        blend: str = "MIX"
    ) -> Dict[str, Any]:
        """
        设置纹理绘制笔刷
        
        Args:
            brush_type: 笔刷类型 (DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK)
            color: 绘制颜色 [R,G,B]
            radius: 笔刷半径
            strength: 笔刷强度 (0-1)
            blend: 混合模式 (MIX, ADD, SUBTRACT, MULTIPLY等)
        """
        params = TexturePaintBrushInput(
            brush_type=brush_type,
            color=color,
            radius=radius,
            strength=strength,
            blend=blend
        )
        return await server.send_command("texture_paint", "set_brush", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_paint_stroke(
        object_name: str,
        uv_points: List[List[float]],
        color: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        执行纹理绘制笔触
        
        Args:
            object_name: 对象名称
            uv_points: UV坐标点列表 [[u,v,pressure], ...]
            color: 可选的绘制颜色 [R,G,B]
        """
        params = TexturePaintStrokeInput(
            object_name=object_name,
            uv_points=uv_points,
            color=color
        )
        return await server.send_command("texture_paint", "stroke", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_paint_fill(
        object_name: str,
        color: List[float] = [1.0, 1.0, 1.0, 1.0],
        texture_slot: int = 0
    ) -> Dict[str, Any]:
        """
        填充纹理颜色
        
        Args:
            object_name: 对象名称
            color: 填充颜色 [R,G,B,A]
            texture_slot: 纹理槽索引
        """
        params = TexturePaintFillInput(
            object_name=object_name,
            color=color,
            texture_slot=texture_slot
        )
        return await server.send_command("texture_paint", "fill", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_bake(
        object_name: str,
        bake_type: str = "DIFFUSE",
        width: int = 1024,
        height: int = 1024,
        margin: int = 16,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        烘焙纹理
        
        Args:
            object_name: 对象名称
            bake_type: 烘焙类型 (DIFFUSE, AO, SHADOW, NORMAL, UV, EMIT, COMBINED)
            width: 输出宽度
            height: 输出高度
            margin: 边缘扩展像素
            output_path: 输出文件路径
        """
        params = TextureBakeInput(
            object_name=object_name,
            bake_type=bake_type,
            width=width,
            height=height,
            margin=margin,
            output_path=output_path
        )
        return await server.send_command("texture_paint", "bake", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_slot(
        object_name: str,
        action: str = "ADD",
        texture_name: Optional[str] = None,
        slot_index: int = 0
    ) -> Dict[str, Any]:
        """
        管理纹理槽
        
        Args:
            object_name: 对象名称
            action: 操作类型 (ADD, REMOVE, SELECT)
            texture_name: 纹理名称
            slot_index: 槽索引
        """
        params = TextureSlotInput(
            object_name=object_name,
            action=action,
            texture_name=texture_name,
            slot_index=slot_index
        )
        return await server.send_command("texture_paint", "slot", params.model_dump())
    
    @mcp.tool()
    async def blender_texture_save(
        texture_name: str,
        filepath: str,
        file_format: str = "PNG"
    ) -> Dict[str, Any]:
        """
        保存纹理到文件
        
        Args:
            texture_name: 纹理名称
            filepath: 保存路径
            file_format: 文件格式 (PNG, JPEG, TIFF, BMP, OPEN_EXR)
        """
        params = TextureSaveInput(
            texture_name=texture_name,
            filepath=filepath,
            file_format=file_format
        )
        return await server.send_command("texture_paint", "save", params.model_dump())
