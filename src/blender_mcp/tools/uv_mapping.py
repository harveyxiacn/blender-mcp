"""
UV映射工具

提供UV展开、投影、编辑等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class UVUnwrapInput(BaseModel):
    """UV展开输入"""
    object_name: str = Field(..., description="对象名称")
    method: str = Field(
        default="ANGLE_BASED",
        description="展开方法: ANGLE_BASED, CONFORMAL"
    )
    fill_holes: bool = Field(default=True, description="填充空洞")
    correct_aspect: bool = Field(default=True, description="修正宽高比")


class UVProjectInput(BaseModel):
    """UV投影输入"""
    object_name: str = Field(..., description="对象名称")
    projection_type: str = Field(
        default="CUBE",
        description="投影类型: CUBE, CYLINDER, SPHERE, VIEW"
    )
    scale_to_bounds: bool = Field(default=True, description="缩放到边界")


class UVSmartProjectInput(BaseModel):
    """智能UV投影输入"""
    object_name: str = Field(..., description="对象名称")
    angle_limit: float = Field(default=66.0, description="角度限制 (度)", ge=0, le=89)
    island_margin: float = Field(default=0.0, description="岛屿边距", ge=0, le=1)
    area_weight: float = Field(default=0.0, description="面积权重", ge=0, le=1)


class UVPackInput(BaseModel):
    """UV打包输入"""
    object_name: str = Field(..., description="对象名称")
    margin: float = Field(default=0.001, description="边距", ge=0, le=1)
    rotate: bool = Field(default=True, description="允许旋转")


class UVSeamInput(BaseModel):
    """UV接缝输入"""
    object_name: str = Field(..., description="对象名称")
    action: str = Field(default="mark", description="操作: mark, clear")
    edge_indices: Optional[List[int]] = Field(default=None, description="边索引列表")
    from_sharp: bool = Field(default=False, description="从锐边标记")


class UVTransformInput(BaseModel):
    """UV变换输入"""
    object_name: str = Field(..., description="对象名称")
    translate: Optional[List[float]] = Field(default=None, description="平移 [U, V]")
    rotate: Optional[float] = Field(default=None, description="旋转 (度)")
    scale: Optional[List[float]] = Field(default=None, description="缩放 [U, V]")


# ==================== 工具注册 ====================

def register_uv_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册UV映射工具"""
    
    @mcp.tool(
        name="blender_uv_unwrap",
        annotations={
            "title": "UV展开",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_unwrap(params: UVUnwrapInput) -> str:
        """自动UV展开。
        
        Args:
            params: 对象名称、展开方法等
            
        Returns:
            展开结果
        """
        result = await server.execute_command(
            "uv", "unwrap",
            {
                "object_name": params.object_name,
                "method": params.method,
                "fill_holes": params.fill_holes,
                "correct_aspect": params.correct_aspect
            }
        )
        
        if result.get("success"):
            return f"成功展开 '{params.object_name}' 的UV"
        else:
            return f"展开失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_project",
        annotations={
            "title": "UV投影",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_project(params: UVProjectInput) -> str:
        """投影UV映射（立方体、圆柱、球面）。
        
        Args:
            params: 对象名称、投影类型
            
        Returns:
            投影结果
        """
        result = await server.execute_command(
            "uv", "project",
            {
                "object_name": params.object_name,
                "projection_type": params.projection_type,
                "scale_to_bounds": params.scale_to_bounds
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 应用 {params.projection_type} 投影"
        else:
            return f"投影失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_smart_project",
        annotations={
            "title": "智能UV投影",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_smart_project(params: UVSmartProjectInput) -> str:
        """智能UV投影（自动分割岛屿）。
        
        Args:
            params: 对象名称、角度限制、边距
            
        Returns:
            投影结果
        """
        result = await server.execute_command(
            "uv", "smart_project",
            {
                "object_name": params.object_name,
                "angle_limit": params.angle_limit,
                "island_margin": params.island_margin,
                "area_weight": params.area_weight
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 应用智能UV投影"
        else:
            return f"投影失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_pack",
        annotations={
            "title": "UV打包",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_uv_pack(params: UVPackInput) -> str:
        """优化UV岛屿排布。
        
        Args:
            params: 对象名称、边距、是否旋转
            
        Returns:
            打包结果
        """
        result = await server.execute_command(
            "uv", "pack",
            {
                "object_name": params.object_name,
                "margin": params.margin,
                "rotate": params.rotate
            }
        )
        
        if result.get("success"):
            return f"成功打包 '{params.object_name}' 的UV"
        else:
            return f"打包失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_seam",
        annotations={
            "title": "UV接缝",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_uv_seam(params: UVSeamInput) -> str:
        """标记或清除UV接缝。
        
        Args:
            params: 对象名称、操作类型
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "uv", "seam",
            {
                "object_name": params.object_name,
                "action": params.action,
                "edge_indices": params.edge_indices,
                "from_sharp": params.from_sharp
            }
        )
        
        if result.get("success"):
            return f"成功{params.action} UV接缝"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_transform",
        annotations={
            "title": "UV变换",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_uv_transform(params: UVTransformInput) -> str:
        """变换UV坐标。
        
        Args:
            params: 对象名称、平移、旋转、缩放
            
        Returns:
            变换结果
        """
        result = await server.execute_command(
            "uv", "transform",
            {
                "object_name": params.object_name,
                "translate": params.translate,
                "rotate": params.rotate,
                "scale": params.scale
            }
        )
        
        if result.get("success"):
            return f"成功变换 '{params.object_name}' 的UV"
        else:
            return f"变换失败: {result.get('error', {}).get('message', '未知错误')}"
