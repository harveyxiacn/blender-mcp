"""
曲线建模工具

提供曲线创建、编辑、转换等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class CurveCreateInput(BaseModel):
    """创建曲线输入"""
    curve_type: str = Field(
        default="BEZIER",
        description="曲线类型: BEZIER, NURBS, POLY"
    )
    name: str = Field(default="Curve", description="曲线名称")
    points: List[List[float]] = Field(..., description="控制点列表 [[x,y,z], ...]")
    cyclic: bool = Field(default=False, description="闭合曲线")
    location: Optional[List[float]] = Field(default=None, description="位置")


class CurveCircleInput(BaseModel):
    """创建圆形曲线输入"""
    name: str = Field(default="Circle", description="名称")
    radius: float = Field(default=1.0, description="半径", ge=0.001)
    location: Optional[List[float]] = Field(default=None, description="位置")
    fill_mode: str = Field(default="NONE", description="填充: NONE, FRONT, BACK, BOTH")


class CurvePathInput(BaseModel):
    """创建路径曲线输入"""
    name: str = Field(default="Path", description="名称")
    length: float = Field(default=4.0, description="长度", ge=0.1)
    points_count: int = Field(default=5, description="点数", ge=2)
    location: Optional[List[float]] = Field(default=None, description="位置")


class CurveSpiralInput(BaseModel):
    """创建螺旋曲线输入"""
    name: str = Field(default="Spiral", description="名称")
    turns: float = Field(default=2.0, description="圈数", ge=0.1)
    radius: float = Field(default=1.0, description="半径", ge=0.001)
    height: float = Field(default=2.0, description="高度")
    location: Optional[List[float]] = Field(default=None, description="位置")


class CurveToMeshInput(BaseModel):
    """曲线转网格输入"""
    curve_name: str = Field(..., description="曲线名称")
    resolution: int = Field(default=12, description="分辨率", ge=1, le=64)
    keep_original: bool = Field(default=False, description="保留原曲线")


class CurveExtrudeInput(BaseModel):
    """曲线挤出输入"""
    curve_name: str = Field(..., description="曲线名称")
    depth: float = Field(default=0.1, description="挤出深度", ge=0)
    bevel_depth: float = Field(default=0.0, description="倒角深度", ge=0)
    bevel_resolution: int = Field(default=0, description="倒角分辨率", ge=0)


class CurveProfileInput(BaseModel):
    """沿曲线挤出轮廓输入"""
    path_curve: str = Field(..., description="路径曲线名称")
    profile_curve: str = Field(..., description="轮廓曲线名称")
    name: str = Field(default="Sweep", description="结果名称")


class CurveTextInput(BaseModel):
    """创建文本曲线输入"""
    text: str = Field(..., description="文本内容")
    name: str = Field(default="Text", description="名称")
    font_size: float = Field(default=1.0, description="字体大小", ge=0.01)
    extrude: float = Field(default=0.0, description="挤出深度", ge=0)
    location: Optional[List[float]] = Field(default=None, description="位置")


# ==================== 工具注册 ====================

def register_curve_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册曲线建模工具"""
    
    @mcp.tool(
        name="blender_curve_create",
        annotations={
            "title": "创建曲线",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_create(params: CurveCreateInput) -> str:
        """从控制点创建曲线。
        
        Args:
            params: 曲线类型、控制点、是否闭合等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "curves", "create",
            {
                "curve_type": params.curve_type,
                "name": params.name,
                "points": params.points,
                "cyclic": params.cyclic,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            return f"成功创建 {params.curve_type} 曲线 '{params.name}' ({len(params.points)} 个点)"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_circle",
        annotations={
            "title": "创建圆形曲线",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_circle(params: CurveCircleInput) -> str:
        """创建圆形曲线。
        
        Args:
            params: 半径、位置、填充模式
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "curves", "circle",
            {
                "name": params.name,
                "radius": params.radius,
                "location": params.location or [0, 0, 0],
                "fill_mode": params.fill_mode
            }
        )
        
        if result.get("success"):
            return f"成功创建圆形曲线 '{params.name}' (半径: {params.radius})"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_path",
        annotations={
            "title": "创建路径曲线",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_path(params: CurvePathInput) -> str:
        """创建路径曲线（用于动画）。
        
        Args:
            params: 长度、点数、位置
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "curves", "path",
            {
                "name": params.name,
                "length": params.length,
                "points_count": params.points_count,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            return f"成功创建路径曲线 '{params.name}'"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_spiral",
        annotations={
            "title": "创建螺旋曲线",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_spiral(params: CurveSpiralInput) -> str:
        """创建螺旋曲线。
        
        Args:
            params: 圈数、半径、高度
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "curves", "spiral",
            {
                "name": params.name,
                "turns": params.turns,
                "radius": params.radius,
                "height": params.height,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            return f"成功创建螺旋曲线 '{params.name}' ({params.turns} 圈)"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_to_mesh",
        annotations={
            "title": "曲线转网格",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_to_mesh(params: CurveToMeshInput) -> str:
        """将曲线转换为网格。
        
        Args:
            params: 曲线名称、分辨率
            
        Returns:
            转换结果
        """
        result = await server.execute_command(
            "curves", "to_mesh",
            {
                "curve_name": params.curve_name,
                "resolution": params.resolution,
                "keep_original": params.keep_original
            }
        )
        
        if result.get("success"):
            mesh_name = result.get("data", {}).get("mesh_name", "")
            return f"成功将曲线转换为网格 '{mesh_name}'"
        else:
            return f"转换失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_extrude",
        annotations={
            "title": "曲线挤出",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_curve_extrude(params: CurveExtrudeInput) -> str:
        """设置曲线的挤出和倒角。
        
        Args:
            params: 曲线名称、深度、倒角
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "curves", "extrude",
            {
                "curve_name": params.curve_name,
                "depth": params.depth,
                "bevel_depth": params.bevel_depth,
                "bevel_resolution": params.bevel_resolution
            }
        )
        
        if result.get("success"):
            return f"成功设置曲线挤出"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_curve_text",
        annotations={
            "title": "创建文本曲线",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_text(params: CurveTextInput) -> str:
        """创建3D文本。
        
        Args:
            params: 文本内容、字体大小、挤出深度
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "curves", "text",
            {
                "text": params.text,
                "name": params.name,
                "font_size": params.font_size,
                "extrude": params.extrude,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            return f"成功创建文本 '{params.text}'"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
