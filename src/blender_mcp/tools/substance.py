"""
Substance Connection Tools

Provides MCP tools for integration with Substance Painter.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class SubstanceExportInput(BaseModel):
    """Export to Substance"""
    object_name: str = Field(..., description="Object name")
    filepath: str = Field(..., description="Export file path")
    format: str = Field("FBX", description="Format: FBX, OBJ")
    export_uvs: bool = Field(True, description="Export UVs")
    triangulate: bool = Field(True, description="Triangulate mesh")


class SubstanceImportInput(BaseModel):
    """Import Substance textures"""
    texture_folder: str = Field(..., description="Texture folder path")
    object_name: str = Field(..., description="Target object name")
    naming_convention: str = Field("substance", description="Naming convention: substance, custom")


class SubstanceLinkInput(BaseModel):
    """Establish live link"""
    project_path: str = Field(..., description="Substance project path (.spp)")
    watch_interval: float = Field(2.0, description="Watch interval in seconds")


class SubstanceBakeInput(BaseModel):
    """Request texture baking"""
    high_poly: str = Field(..., description="High-poly object name")
    low_poly: str = Field(..., description="Low-poly object name")
    output_folder: str = Field(..., description="Output folder path")
    maps: List[str] = Field(["normal", "ao", "curvature"], description="Map types to bake")
    resolution: int = Field(2048, description="Texture resolution")


# ============ Tool Registration ============

def register_substance_tools(mcp: FastMCP, server):
    """Register Substance connection tools."""

    @mcp.tool()
    async def blender_substance_export(
        object_name: str,
        filepath: str,
        format: str = "FBX",
        export_uvs: bool = True,
        triangulate: bool = True
    ) -> Dict[str, Any]:
        """
        Export model to Substance Painter.

        Args:
            object_name: Object name
            filepath: Export file path
            format: Export format (FBX, OBJ)
            export_uvs: Whether to export UVs
            triangulate: Whether to triangulate the mesh
        """
        params = SubstanceExportInput(
            object_name=object_name,
            filepath=filepath,
            format=format,
            export_uvs=export_uvs,
            triangulate=triangulate
        )
        return await server.send_command("substance", "export", params.model_dump())

    @mcp.tool()
    async def blender_substance_import(
        texture_folder: str,
        object_name: str,
        naming_convention: str = "substance"
    ) -> Dict[str, Any]:
        """
        Import textures exported from Substance Painter.

        Args:
            texture_folder: Path to the texture folder
            object_name: Target object name
            naming_convention: Naming convention (substance, custom)
        """
        params = SubstanceImportInput(
            texture_folder=texture_folder,
            object_name=object_name,
            naming_convention=naming_convention
        )
        return await server.send_command("substance", "import", params.model_dump())

    @mcp.tool()
    async def blender_substance_link(
        project_path: str,
        watch_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        Establish a live link with Substance Painter.

        Args:
            project_path: Substance project path (.spp)
            watch_interval: Watch interval in seconds
        """
        params = SubstanceLinkInput(
            project_path=project_path,
            watch_interval=watch_interval
        )
        return await server.send_command("substance", "link", params.model_dump())

    @mcp.tool()
    async def blender_substance_unlink() -> Dict[str, Any]:
        """
        Disconnect the Substance Painter live link.
        """
        return await server.send_command("substance", "unlink", {})

    @mcp.tool()
    async def blender_substance_bake(
        high_poly: str,
        low_poly: str,
        output_folder: str,
        maps: List[str] = ["normal", "ao", "curvature"],
        resolution: int = 2048
    ) -> Dict[str, Any]:
        """
        Prepare and export models for Substance baking.

        Args:
            high_poly: High-poly object name
            low_poly: Low-poly object name
            output_folder: Output folder path
            maps: Map types to bake
            resolution: Texture resolution
        """
        params = SubstanceBakeInput(
            high_poly=high_poly,
            low_poly=low_poly,
            output_folder=output_folder,
            maps=maps,
            resolution=resolution
        )
        return await server.send_command("substance", "bake", params.model_dump())

    @mcp.tool()
    async def blender_substance_detect() -> Dict[str, Any]:
        """
        Detect Substance Painter installation.
        """
        return await server.send_command("substance", "detect", {})
