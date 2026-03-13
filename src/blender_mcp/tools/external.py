"""
External Integration Tools

Provides MCP tools for integration with external tools (Unity, Unreal, etc.).
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class UnityExportInput(BaseModel):
    """Unity export"""

    filepath: str = Field(..., description="Export file path")
    objects: list[str] | None = Field(None, description="List of objects to export")
    apply_modifiers: bool = Field(True, description="Apply modifiers")
    apply_scale: bool = Field(True, description="Apply scale")
    export_animations: bool = Field(True, description="Export animations")
    bake_animation: bool = Field(False, description="Bake animations")


class UnrealExportInput(BaseModel):
    """Unreal export"""

    filepath: str = Field(..., description="Export file path")
    objects: list[str] | None = Field(None, description="List of objects to export")
    export_animations: bool = Field(True, description="Export animations")
    smoothing: str = Field("FACE", description="Smoothing type: FACE, EDGE, OFF")
    use_tspace: bool = Field(True, description="Use tangent space")


class GodotExportInput(BaseModel):
    """Godot export"""

    filepath: str = Field(..., description="Export file path")
    objects: list[str] | None = Field(None, description="List of objects to export")
    export_format: str = Field("GLTF", description="Export format: GLTF, GLB")


class BatchExportInput(BaseModel):
    """Batch export"""

    output_dir: str = Field(..., description="Output directory")
    format: str = Field("FBX", description="Format: FBX, GLTF, OBJ")
    separate_files: bool = Field(True, description="Export to separate files individually")
    objects: list[str] | None = Field(None, description="List of objects to export")


class CollectionExportInput(BaseModel):
    """Collection export"""

    collection_name: str = Field(..., description="Collection name")
    filepath: str = Field(..., description="Export file path")
    format: str = Field("FBX", description="Format: FBX, GLTF, OBJ")


# ============ Tool Registration ============


def register_external_tools(mcp: FastMCP, server) -> None:
    """Register external integration tools"""

    @mcp.tool()
    async def blender_unity_export(
        filepath: str,
        objects: list[str] | None = None,
        apply_modifiers: bool = True,
        apply_scale: bool = True,
        export_animations: bool = True,
        bake_animation: bool = False,
    ) -> dict[str, Any]:
        """
        Export optimized for Unity

        Args:
            filepath: Export file path (.fbx)
            objects: List of objects to export
            apply_modifiers: Apply modifiers
            apply_scale: Apply scale (Unity uses a different coordinate system)
            export_animations: Export animations
            bake_animation: Bake animations
        """
        params = UnityExportInput(
            filepath=filepath,
            objects=objects,
            apply_modifiers=apply_modifiers,
            apply_scale=apply_scale,
            export_animations=export_animations,
            bake_animation=bake_animation,
        )
        return await server.send_command("external", "unity_export", params.model_dump())

    @mcp.tool()
    async def blender_unreal_export(
        filepath: str,
        objects: list[str] | None = None,
        export_animations: bool = True,
        smoothing: str = "FACE",
        use_tspace: bool = True,
    ) -> dict[str, Any]:
        """
        Export optimized for Unreal Engine

        Args:
            filepath: Export file path (.fbx)
            objects: List of objects to export
            export_animations: Export animations
            smoothing: Smoothing type (FACE, EDGE, OFF)
            use_tspace: Use tangent space
        """
        params = UnrealExportInput(
            filepath=filepath,
            objects=objects,
            export_animations=export_animations,
            smoothing=smoothing,
            use_tspace=use_tspace,
        )
        return await server.send_command("external", "unreal_export", params.model_dump())

    @mcp.tool()
    async def blender_godot_export(
        filepath: str, objects: list[str] | None = None, export_format: str = "GLTF"
    ) -> dict[str, Any]:
        """
        Export optimized for Godot

        Args:
            filepath: Export file path
            objects: List of objects to export
            export_format: Export format (GLTF, GLB)
        """
        params = GodotExportInput(filepath=filepath, objects=objects, export_format=export_format)
        return await server.send_command("external", "godot_export", params.model_dump())

    # Note: blender_batch_export has been moved to batch.py to avoid duplicate registration

    @mcp.tool()
    async def blender_collection_export(
        collection_name: str, filepath: str, format: str = "FBX"
    ) -> dict[str, Any]:
        """
        Export an entire collection

        Args:
            collection_name: Collection name
            filepath: Export file path
            format: Export format (FBX, GLTF, OBJ)
        """
        params = CollectionExportInput(
            collection_name=collection_name, filepath=filepath, format=format
        )
        return await server.send_command("external", "collection_export", params.model_dump())
