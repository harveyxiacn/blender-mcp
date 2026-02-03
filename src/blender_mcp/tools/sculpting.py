"""
雕刻工具

提供数字雕刻相关的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class SculptModeInput(BaseModel):
    """进入/退出雕刻模式"""
    object_name: str = Field(..., description="对象名称")
    enable: bool = Field(True, description="是否进入雕刻模式")


class SculptBrushInput(BaseModel):
    """设置雕刻笔刷"""
    brush_type: str = Field(
        "DRAW",
        description="笔刷类型: DRAW, CLAY, CLAY_STRIPS, INFLATE, BLOB, CREASE, SMOOTH, FLATTEN, FILL, SCRAPE, PINCH, GRAB, SNAKE_HOOK, THUMB, NUDGE, ROTATE, MASK, DRAW_FACE_SETS"
    )
    radius: float = Field(50.0, description="笔刷半径")
    strength: float = Field(0.5, description="笔刷强度 (0-1)")
    auto_smooth: float = Field(0.0, description="自动平滑 (0-1)")


class SculptStrokeInput(BaseModel):
    """执行雕刻笔触"""
    object_name: str = Field(..., description="对象名称")
    stroke_points: List[List[float]] = Field(
        ...,
        description="笔触点列表 [[x,y,z,pressure], ...]"
    )
    brush_type: Optional[str] = Field(None, description="笔刷类型")


class SculptRemeshInput(BaseModel):
    """重新网格化"""
    object_name: str = Field(..., description="对象名称")
    mode: str = Field("VOXEL", description="模式: VOXEL, QUAD")
    voxel_size: float = Field(0.1, description="体素大小")
    smooth_normals: bool = Field(True, description="平滑法线")


class SculptMultiresInput(BaseModel):
    """多分辨率细分"""
    object_name: str = Field(..., description="对象名称")
    levels: int = Field(2, description="细分级别")
    sculpt_level: Optional[int] = Field(None, description="雕刻级别")


class SculptMaskInput(BaseModel):
    """蒙版操作"""
    object_name: str = Field(..., description="对象名称")
    action: str = Field("CLEAR", description="操作: CLEAR, INVERT, SMOOTH, EXPAND, CONTRACT")


class SculptSymmetryInput(BaseModel):
    """设置对称"""
    use_x: bool = Field(True, description="X轴对称")
    use_y: bool = Field(False, description="Y轴对称")
    use_z: bool = Field(False, description="Z轴对称")


class SculptDyntopoInput(BaseModel):
    """动态拓扑"""
    object_name: str = Field(..., description="对象名称")
    enable: bool = Field(True, description="启用动态拓扑")
    detail_size: float = Field(12.0, description="细节大小")
    detail_type: str = Field("RELATIVE", description="细节类型: RELATIVE, CONSTANT, BRUSH")


# ============ 工具注册 ============

def register_sculpting_tools(mcp: FastMCP, server):
    """注册雕刻工具"""
    
    @mcp.tool()
    async def blender_sculpt_mode(
        object_name: str,
        enable: bool = True
    ) -> Dict[str, Any]:
        """
        进入或退出雕刻模式
        
        Args:
            object_name: 要雕刻的对象名称
            enable: True进入雕刻模式，False退出
        """
        params = SculptModeInput(
            object_name=object_name,
            enable=enable
        )
        return await server.send_command("sculpt", "mode", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_set_brush(
        brush_type: str = "DRAW",
        radius: float = 50.0,
        strength: float = 0.5,
        auto_smooth: float = 0.0
    ) -> Dict[str, Any]:
        """
        设置雕刻笔刷
        
        Args:
            brush_type: 笔刷类型 (DRAW, CLAY, CLAY_STRIPS, INFLATE, SMOOTH, GRAB等)
            radius: 笔刷半径
            strength: 笔刷强度 (0-1)
            auto_smooth: 自动平滑值 (0-1)
        """
        params = SculptBrushInput(
            brush_type=brush_type,
            radius=radius,
            strength=strength,
            auto_smooth=auto_smooth
        )
        return await server.send_command("sculpt", "set_brush", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_stroke(
        object_name: str,
        stroke_points: List[List[float]],
        brush_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行雕刻笔触
        
        Args:
            object_name: 对象名称
            stroke_points: 笔触点列表 [[x,y,z,pressure], ...]
            brush_type: 可选的笔刷类型
        """
        params = SculptStrokeInput(
            object_name=object_name,
            stroke_points=stroke_points,
            brush_type=brush_type
        )
        return await server.send_command("sculpt", "stroke", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_remesh(
        object_name: str,
        mode: str = "VOXEL",
        voxel_size: float = 0.1,
        smooth_normals: bool = True
    ) -> Dict[str, Any]:
        """
        重新网格化对象
        
        Args:
            object_name: 对象名称
            mode: 重网格模式 (VOXEL或QUAD)
            voxel_size: 体素大小
            smooth_normals: 是否平滑法线
        """
        params = SculptRemeshInput(
            object_name=object_name,
            mode=mode,
            voxel_size=voxel_size,
            smooth_normals=smooth_normals
        )
        return await server.send_command("sculpt", "remesh", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_multires(
        object_name: str,
        levels: int = 2,
        sculpt_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        添加多分辨率修改器
        
        Args:
            object_name: 对象名称
            levels: 细分级别
            sculpt_level: 雕刻级别
        """
        params = SculptMultiresInput(
            object_name=object_name,
            levels=levels,
            sculpt_level=sculpt_level
        )
        return await server.send_command("sculpt", "multires", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_mask(
        object_name: str,
        action: str = "CLEAR"
    ) -> Dict[str, Any]:
        """
        雕刻蒙版操作
        
        Args:
            object_name: 对象名称
            action: 操作类型 (CLEAR, INVERT, SMOOTH, EXPAND, CONTRACT)
        """
        params = SculptMaskInput(
            object_name=object_name,
            action=action
        )
        return await server.send_command("sculpt", "mask", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_symmetry(
        use_x: bool = True,
        use_y: bool = False,
        use_z: bool = False
    ) -> Dict[str, Any]:
        """
        设置雕刻对称
        
        Args:
            use_x: X轴对称
            use_y: Y轴对称
            use_z: Z轴对称
        """
        params = SculptSymmetryInput(
            use_x=use_x,
            use_y=use_y,
            use_z=use_z
        )
        return await server.send_command("sculpt", "symmetry", params.model_dump())
    
    @mcp.tool()
    async def blender_sculpt_dyntopo(
        object_name: str,
        enable: bool = True,
        detail_size: float = 12.0,
        detail_type: str = "RELATIVE"
    ) -> Dict[str, Any]:
        """
        启用动态拓扑
        
        Args:
            object_name: 对象名称
            enable: 是否启用
            detail_size: 细节大小
            detail_type: 细节类型 (RELATIVE, CONSTANT, BRUSH)
        """
        params = SculptDyntopoInput(
            object_name=object_name,
            enable=enable,
            detail_size=detail_size,
            detail_type=detail_type
        )
        return await server.send_command("sculpt", "dyntopo", params.model_dump())
