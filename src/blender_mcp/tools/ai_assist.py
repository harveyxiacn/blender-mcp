"""
AI辅助工具

提供AI辅助功能的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class DescribeSceneInput(BaseModel):
    """描述场景"""
    detail_level: str = Field("medium", description="详细程度: low, medium, high")
    include_materials: bool = Field(True, description="包含材质信息")
    include_animations: bool = Field(True, description="包含动画信息")


class AnalyzeObjectInput(BaseModel):
    """分析对象"""
    object_name: str = Field(..., description="对象名称")
    include_modifiers: bool = Field(True, description="包含修改器信息")
    include_topology: bool = Field(True, description="包含拓扑信息")


class SuggestOptimizationInput(BaseModel):
    """优化建议"""
    target: str = Field("performance", description="目标: performance, quality, memory")


class AutoMaterialInput(BaseModel):
    """自动材质"""
    object_name: str = Field(..., description="对象名称")
    description: str = Field(..., description="材质描述")
    style: str = Field("realistic", description="风格: realistic, cartoon, stylized")


class SceneStatisticsInput(BaseModel):
    """场景统计"""
    include_hidden: bool = Field(False, description="包含隐藏对象")


# ============ 工具注册 ============

def register_ai_assist_tools(mcp: FastMCP, server):
    """注册AI辅助工具"""
    
    @mcp.tool()
    async def blender_ai_describe_scene(
        detail_level: str = "medium",
        include_materials: bool = True,
        include_animations: bool = True
    ) -> Dict[str, Any]:
        """
        获取当前场景的详细描述
        
        Args:
            detail_level: 详细程度 (low, medium, high)
            include_materials: 是否包含材质信息
            include_animations: 是否包含动画信息
        """
        params = DescribeSceneInput(
            detail_level=detail_level,
            include_materials=include_materials,
            include_animations=include_animations
        )
        return await server.send_command("ai_assist", "describe_scene", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_analyze_object(
        object_name: str,
        include_modifiers: bool = True,
        include_topology: bool = True
    ) -> Dict[str, Any]:
        """
        分析指定对象
        
        Args:
            object_name: 对象名称
            include_modifiers: 包含修改器信息
            include_topology: 包含拓扑信息
        """
        params = AnalyzeObjectInput(
            object_name=object_name,
            include_modifiers=include_modifiers,
            include_topology=include_topology
        )
        return await server.send_command("ai_assist", "analyze_object", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_suggest_optimization(
        target: str = "performance"
    ) -> Dict[str, Any]:
        """
        获取场景优化建议
        
        Args:
            target: 优化目标 (performance, quality, memory)
        """
        params = SuggestOptimizationInput(target=target)
        return await server.send_command("ai_assist", "suggest_optimization", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_auto_material(
        object_name: str,
        description: str,
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """
        根据描述自动创建材质
        
        Args:
            object_name: 对象名称
            description: 材质描述（如"金属表面"、"木纹"等）
            style: 风格 (realistic, cartoon, stylized)
        """
        params = AutoMaterialInput(
            object_name=object_name,
            description=description,
            style=style
        )
        return await server.send_command("ai_assist", "auto_material", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_scene_statistics(
        include_hidden: bool = False
    ) -> Dict[str, Any]:
        """
        获取场景统计信息
        
        Args:
            include_hidden: 是否包含隐藏对象
        """
        params = SceneStatisticsInput(include_hidden=include_hidden)
        return await server.send_command("ai_assist", "scene_statistics", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_list_issues() -> Dict[str, Any]:
        """
        检测场景中的潜在问题
        """
        return await server.send_command("ai_assist", "list_issues", {})
