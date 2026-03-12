"""
Export Tools

Provides model and animation export features, supporting Unity, Web, and other platforms.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class ExportFBXInput(BaseModel):
    """FBX export input"""
    filepath: str = Field(..., description="Export file path (.fbx)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    apply_modifiers: bool = Field(default=True, description="Apply modifiers")
    include_animation: bool = Field(default=True, description="Include animation")
    bake_animation: bool = Field(default=False, description="Bake animation")
    use_mesh_modifiers: bool = Field(default=True, description="Apply mesh modifiers")
    use_armature_deform_only: bool = Field(default=False, description="Armature deform only")
    add_leaf_bones: bool = Field(default=False, description="Add leaf bones (not needed for Unity)")
    primary_bone_axis: str = Field(default="Y", description="Primary bone axis")
    secondary_bone_axis: str = Field(default="X", description="Secondary bone axis")
    apply_scale: str = Field(default="FBX_SCALE_ALL", description="Scale apply method")


class ExportGLTFInput(BaseModel):
    """glTF export input"""
    filepath: str = Field(..., description="Export file path (.glb or .gltf)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    include_animation: bool = Field(default=True, description="Include animation")
    export_format: str = Field(default="GLB", description="Format: GLB or GLTF_SEPARATE")
    export_textures: bool = Field(default=True, description="Export textures")
    export_draco: bool = Field(default=False, description="Draco compression")


class ExportOBJInput(BaseModel):
    """OBJ export input"""
    filepath: str = Field(..., description="Export file path (.obj)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    apply_modifiers: bool = Field(default=True, description="Apply modifiers")
    export_materials: bool = Field(default=True, description="Export materials")


class ExportUnityPackageInput(BaseModel):
    """Unity package export input"""
    filepath: str = Field(..., description="Export file path")
    objects: Optional[List[str]] = Field(default=None, description="List of objects to export")
    include_animations: bool = Field(default=True, description="Include animations")
    setup_humanoid: bool = Field(default=False, description="Set up as Humanoid type")
    generate_lod: bool = Field(default=False, description="Generate LOD")


# ==================== Tool Registration ====================

def register_export_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register export tools"""

    @mcp.tool(
        name="blender_export_fbx",
        annotations={
            "title": "Export FBX",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_fbx(params: ExportFBXInput) -> str:
        """Export as FBX format (suitable for Unity, Unreal, etc.).

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export", "fbx",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "include_animation": params.include_animation,
                "bake_animation": params.bake_animation,
                "use_mesh_modifiers": params.use_mesh_modifiers,
                "use_armature_deform_only": params.use_armature_deform_only,
                "add_leaf_bones": params.add_leaf_bones,
                "primary_bone_axis": params.primary_bone_axis,
                "secondary_bone_axis": params.secondary_bone_axis,
                "apply_scale": params.apply_scale
            }
        )

        if result.get("success"):
            return f"Successfully exported FBX to: {params.filepath}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_export_gltf",
        annotations={
            "title": "Export glTF",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_gltf(params: ExportGLTFInput) -> str:
        """Export as glTF format (suitable for Web, Three.js, etc.).

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export", "gltf",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "include_animation": params.include_animation,
                "export_format": params.export_format,
                "export_textures": params.export_textures,
                "export_draco": params.export_draco
            }
        )

        if result.get("success"):
            return f"Successfully exported glTF to: {params.filepath}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_export_obj",
        annotations={
            "title": "Export OBJ",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_obj(params: ExportOBJInput) -> str:
        """Export as OBJ format.

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export", "obj",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "export_materials": params.export_materials
            }
        )

        if result.get("success"):
            return f"Successfully exported OBJ to: {params.filepath}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"
