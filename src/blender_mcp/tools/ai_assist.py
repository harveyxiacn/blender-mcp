"""
AI Assist Tools

MCP tools providing AI-assisted features.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class DescribeSceneInput(BaseModel):
    """Describe scene"""

    detail_level: str = Field("medium", description="Detail level: low, medium, high")
    include_materials: bool = Field(True, description="Include material information")
    include_animations: bool = Field(True, description="Include animation information")


class AnalyzeObjectInput(BaseModel):
    """Analyze object"""

    object_name: str = Field(..., description="Object name")
    include_modifiers: bool = Field(True, description="Include modifier information")
    include_topology: bool = Field(True, description="Include topology information")


class SuggestOptimizationInput(BaseModel):
    """Optimization suggestions"""

    target: str = Field("performance", description="Target: performance, quality, memory")


class AutoMaterialInput(BaseModel):
    """Auto material"""

    object_name: str = Field(..., description="Object name")
    description: str = Field(..., description="Material description")
    style: str = Field("realistic", description="Style: realistic, cartoon, stylized")


class SceneStatisticsInput(BaseModel):
    """Scene statistics"""

    include_hidden: bool = Field(False, description="Include hidden objects")


# ============ Tool Registration ============


def register_ai_assist_tools(mcp: FastMCP, server) -> None:
    """Register AI assist tools"""

    @mcp.tool()
    async def blender_ai_describe_scene(
        detail_level: str = "medium",
        include_materials: bool = True,
        include_animations: bool = True,
    ) -> dict[str, Any]:
        """
        Get a detailed description of the current scene

        Args:
            detail_level: Detail level (low, medium, high)
            include_materials: Whether to include material information
            include_animations: Whether to include animation information
        """
        params = DescribeSceneInput(
            detail_level=detail_level,
            include_materials=include_materials,
            include_animations=include_animations,
        )
        return await server.send_command("ai_assist", "describe_scene", params.model_dump())

    @mcp.tool()
    async def blender_ai_analyze_object(
        object_name: str, include_modifiers: bool = True, include_topology: bool = True
    ) -> dict[str, Any]:
        """
        Analyze a specified object

        Args:
            object_name: Object name
            include_modifiers: Include modifier information
            include_topology: Include topology information
        """
        params = AnalyzeObjectInput(
            object_name=object_name,
            include_modifiers=include_modifiers,
            include_topology=include_topology,
        )
        return await server.send_command("ai_assist", "analyze_object", params.model_dump())

    @mcp.tool()
    async def blender_ai_suggest_optimization(target: str = "performance") -> dict[str, Any]:
        """
        Get scene optimization suggestions

        Args:
            target: Optimization target (performance, quality, memory)
        """
        params = SuggestOptimizationInput(target=target)
        return await server.send_command("ai_assist", "suggest_optimization", params.model_dump())

    @mcp.tool()
    async def blender_ai_auto_material(
        object_name: str, description: str, style: str = "realistic"
    ) -> dict[str, Any]:
        """
        Automatically create a material based on description

        Args:
            object_name: Object name
            description: Material description (e.g. "metal surface", "wood grain")
            style: Style (realistic, cartoon, stylized)
        """
        params = AutoMaterialInput(object_name=object_name, description=description, style=style)
        return await server.send_command("ai_assist", "auto_material", params.model_dump())

    @mcp.tool()
    async def blender_ai_scene_statistics(include_hidden: bool = False) -> dict[str, Any]:
        """
        Get scene statistics

        Args:
            include_hidden: Whether to include hidden objects
        """
        params = SceneStatisticsInput(include_hidden=include_hidden)
        return await server.send_command("ai_assist", "scene_statistics", params.model_dump())

    @mcp.tool()
    async def blender_ai_list_issues() -> dict[str, Any]:
        """
        Detect potential issues in the scene
        """
        return await server.send_command("ai_assist", "list_issues", {})
