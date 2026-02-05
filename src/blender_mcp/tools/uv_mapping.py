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


# ==================== 生产标准优化输入模型 ====================

from enum import Enum


class TextureResolution(str, Enum):
    """纹理分辨率"""
    RES_256 = "256"
    RES_512 = "512"
    RES_1024 = "1024"
    RES_2048 = "2048"
    RES_4096 = "4096"


class UVAnalyzeInput(BaseModel):
    """UV分析输入"""
    object_name: str = Field(..., description="对象名称")
    texture_resolution: TextureResolution = Field(
        default=TextureResolution.RES_1024,
        description="目标纹理分辨率（用于计算像素密度）"
    )


class UVOptimizeInput(BaseModel):
    """UV优化输入"""
    object_name: str = Field(..., description="对象名称")
    target_margin: float = Field(default=0.01, description="目标边距", ge=0, le=0.1)
    straighten_uvs: bool = Field(default=True, description="尝试矫正UV")
    minimize_stretch: bool = Field(default=True, description="最小化拉伸")
    pack_efficiently: bool = Field(default=True, description="高效打包")


class UVDensityInput(BaseModel):
    """UV密度标准化输入"""
    object_name: str = Field(..., description="对象名称")
    target_density: Optional[float] = Field(
        default=None,
        description="目标密度（像素/单位），None则使用平均密度"
    )
    texture_resolution: TextureResolution = Field(
        default=TextureResolution.RES_1024,
        description="目标纹理分辨率"
    )


class TextureAtlasCreateInput(BaseModel):
    """创建纹理图集输入"""
    object_names: List[str] = Field(..., description="对象名称列表")
    atlas_name: str = Field(default="TextureAtlas", description="图集名称")
    resolution: TextureResolution = Field(
        default=TextureResolution.RES_2048,
        description="图集分辨率"
    )
    margin: float = Field(default=0.01, description="UV岛屿边距", ge=0, le=0.1)


class UVAutoSeamInput(BaseModel):
    """自动接缝输入"""
    object_name: str = Field(..., description="对象名称")
    angle_threshold: float = Field(default=30.0, description="角度阈值（度）", ge=0, le=90)
    use_hard_edges: bool = Field(default=True, description="使用硬边作为接缝")
    optimize_for_deformation: bool = Field(default=False, description="优化变形区域")


class UVGridCheckInput(BaseModel):
    """UV棋盘格检查输入"""
    object_name: str = Field(..., description="对象名称")
    grid_size: int = Field(default=8, description="棋盘格数量", ge=2, le=64)


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
    
    # ==================== 生产标准优化工具 ====================
    
    @mcp.tool(
        name="blender_uv_analyze",
        annotations={
            "title": "UV质量分析",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_uv_analyze(params: UVAnalyzeInput) -> str:
        """分析UV映射质量。
        
        检查UV质量指标：
        - 拉伸/变形程度
        - 岛屿数量和分布
        - UV空间利用率
        - 像素密度一致性
        - 重叠检测
        
        Args:
            params: 对象名称和目标纹理分辨率
            
        Returns:
            详细的UV分析报告
        """
        result = await server.execute_command(
            "uv", "analyze",
            {
                "object_name": params.object_name,
                "texture_resolution": int(params.texture_resolution.value)
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"# UV分析报告: {params.object_name}", ""]
            
            # 基础统计
            lines.append("## 基础统计")
            lines.append(f"- UV层数量: {data.get('uv_layer_count', 'N/A')}")
            lines.append(f"- 岛屿数量: {data.get('island_count', 'N/A')}")
            lines.append(f"- UV空间利用率: {data.get('space_usage', 0):.1f}%")
            lines.append("")
            
            # 质量指标
            lines.append("## 质量指标")
            lines.append(f"- 平均拉伸度: {data.get('avg_stretch', 0):.3f}")
            lines.append(f"- 最大拉伸度: {data.get('max_stretch', 0):.3f}")
            lines.append(f"- 重叠面数: {data.get('overlapping_faces', 0)}")
            lines.append("")
            
            # 像素密度
            density = data.get("pixel_density", {})
            lines.append("## 像素密度（基于 {}x{} 纹理）".format(
                params.texture_resolution.value, params.texture_resolution.value
            ))
            lines.append(f"- 平均密度: {density.get('average', 0):.1f} 像素/单位")
            lines.append(f"- 最小密度: {density.get('min', 0):.1f} 像素/单位")
            lines.append(f"- 最大密度: {density.get('max', 0):.1f} 像素/单位")
            lines.append(f"- 密度变化: {density.get('variance', 0):.1f}%")
            lines.append("")
            
            # 问题和建议
            issues = data.get("issues", [])
            if issues:
                lines.append("## ⚠️ 发现的问题")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")
            
            # 评分
            score = data.get("quality_score", 0)
            lines.append(f"## UV质量评分: {score}/100")
            
            return "\n".join(lines)
        else:
            return f"分析失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_optimize",
        annotations={
            "title": "优化UV布局",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_optimize(params: UVOptimizeInput) -> str:
        """优化UV布局以符合生产标准。
        
        自动执行以下优化：
        - 最小化UV拉伸
        - 高效打包UV岛屿
        - 优化UV空间利用率
        - 设置适当的岛屿边距
        
        Args:
            params: 对象名称和优化选项
            
        Returns:
            优化结果
        """
        result = await server.execute_command(
            "uv", "optimize",
            {
                "object_name": params.object_name,
                "target_margin": params.target_margin,
                "straighten_uvs": params.straighten_uvs,
                "minimize_stretch": params.minimize_stretch,
                "pack_efficiently": params.pack_efficiently
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"UV优化完成: {params.object_name}", ""]
            lines.append(f"- 空间利用率: {data.get('old_usage', 0):.1f}% → {data.get('new_usage', 0):.1f}%")
            lines.append(f"- 平均拉伸度: {data.get('old_stretch', 0):.3f} → {data.get('new_stretch', 0):.3f}")
            
            return "\n".join(lines)
        else:
            return f"优化失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_density_normalize",
        annotations={
            "title": "标准化UV密度",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_density_normalize(params: UVDensityInput) -> str:
        """标准化UV像素密度。
        
        确保所有UV岛屿具有一致的像素密度，这对于：
        - 游戏资产质量一致性至关重要
        - 避免纹理模糊或过于清晰的区域
        - 符合游戏引擎LOD要求
        
        Args:
            params: 对象名称和目标密度设置
            
        Returns:
            标准化结果
        """
        result = await server.execute_command(
            "uv", "density_normalize",
            {
                "object_name": params.object_name,
                "target_density": params.target_density,
                "texture_resolution": int(params.texture_resolution.value)
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"UV密度标准化完成: {params.object_name}", ""]
            lines.append(f"- 目标密度: {data.get('target_density', 0):.1f} 像素/单位")
            lines.append(f"- 调整的岛屿数: {data.get('adjusted_islands', 0)}")
            
            return "\n".join(lines)
        else:
            return f"标准化失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_texture_atlas_create",
        annotations={
            "title": "创建纹理图集",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_texture_atlas_create(params: TextureAtlasCreateInput) -> str:
        """为多个对象创建纹理图集（Texture Atlas）。
        
        将多个对象的UV合并到单一纹理空间中，这对于：
        - 减少Draw Call，提升渲染性能
        - 移动端游戏优化
        - 批量渲染静态场景
        
        Args:
            params: 对象列表、图集名称和设置
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "uv", "create_atlas",
            {
                "object_names": params.object_names,
                "atlas_name": params.atlas_name,
                "resolution": int(params.resolution.value),
                "margin": params.margin
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"纹理图集创建成功: {params.atlas_name}", ""]
            lines.append(f"- 分辨率: {params.resolution.value}x{params.resolution.value}")
            lines.append(f"- 包含对象数: {len(params.object_names)}")
            lines.append(f"- UV空间利用率: {data.get('space_usage', 0):.1f}%")
            
            return "\n".join(lines)
        else:
            return f"创建图集失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_auto_seam",
        annotations={
            "title": "自动UV接缝",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_uv_auto_seam(params: UVAutoSeamInput) -> str:
        """智能自动标记UV接缝。
        
        基于几何特征自动生成最优接缝：
        - 基于角度阈值检测硬边
        - 考虑模型拓扑结构
        - 可选择针对变形优化（角色动画）
        
        Args:
            params: 对象名称和接缝选项
            
        Returns:
            接缝标记结果
        """
        result = await server.execute_command(
            "uv", "auto_seam",
            {
                "object_name": params.object_name,
                "angle_threshold": params.angle_threshold,
                "use_hard_edges": params.use_hard_edges,
                "optimize_for_deformation": params.optimize_for_deformation
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"自动接缝完成: {params.object_name}", ""]
            lines.append(f"- 标记的接缝边数: {data.get('seam_count', 0)}")
            lines.append(f"- 预计岛屿数: {data.get('estimated_islands', 0)}")
            
            return "\n".join(lines)
        else:
            return f"自动接缝失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_uv_grid_check",
        annotations={
            "title": "UV棋盘格检查",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_uv_grid_check(params: UVGridCheckInput) -> str:
        """应用棋盘格纹理检查UV质量。
        
        创建并应用棋盘格材质，用于直观检查：
        - UV拉伸和变形
        - 像素密度一致性
        - 接缝位置
        
        Args:
            params: 对象名称和棋盘格参数
            
        Returns:
            检查结果
        """
        result = await server.execute_command(
            "uv", "grid_check",
            {
                "object_name": params.object_name,
                "grid_size": params.grid_size
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已为 '{params.object_name}' 应用棋盘格检查材质 '{data.get('material_name', 'UV_Checker')}'"
        else:
            return f"检查失败: {result.get('error', {}).get('message', '未知错误')}"
