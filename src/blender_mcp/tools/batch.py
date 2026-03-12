"""
Batch Processing Tools

Provides batch material application, transformation, renaming, export, and more.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class BatchMaterialInput(BaseModel):
    """Batch apply material input"""
    pattern: str = Field(..., description="Object name pattern (supports wildcard *)")
    material_name: str = Field(..., description="Material name")
    replace_existing: bool = Field(default=True, description="Replace existing materials")


class BatchTransformInput(BaseModel):
    """Batch transform input"""
    pattern: str = Field(..., description="Object name pattern")
    location_offset: Optional[List[float]] = Field(default=None, description="Location offset")
    rotation_offset: Optional[List[float]] = Field(default=None, description="Rotation offset")
    scale_factor: Optional[List[float]] = Field(default=None, description="Scale factor")


class BatchRenameInput(BaseModel):
    """Batch rename input"""
    pattern: str = Field(..., description="Object name pattern")
    new_name: str = Field(..., description="New name prefix")
    numbering: bool = Field(default=True, description="Add numbering")
    start_number: int = Field(default=1, description="Start number")


class BatchDeleteInput(BaseModel):
    """Batch delete input"""
    pattern: str = Field(..., description="Object name pattern")
    delete_data: bool = Field(default=True, description="Delete associated data")


class BatchExportInput(BaseModel):
    """Batch export input"""
    pattern: str = Field(..., description="Object name pattern")
    export_path: str = Field(..., description="Export directory path")
    format: str = Field(default="fbx", description="Format: fbx, obj, gltf")
    individual_files: bool = Field(default=True, description="Individual file per object")


class BatchModifierInput(BaseModel):
    """Batch add modifier input"""
    pattern: str = Field(..., description="Object name pattern")
    modifier_type: str = Field(..., description="Modifier type: SUBSURF, BEVEL, SOLIDIFY, MIRROR")
    settings: Optional[dict] = Field(default=None, description="Modifier settings")


class BatchParentInput(BaseModel):
    """Batch set parent input"""
    pattern: str = Field(..., description="Child object name pattern")
    parent_name: str = Field(..., description="Parent object name")
    keep_transform: bool = Field(default=True, description="Keep transform")


# ==================== Tool Registration ====================

def register_batch_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register batch processing tools"""

    @mcp.tool(
        name="blender_batch_apply_material",
        annotations={
            "title": "Batch Apply Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_apply_material(params: BatchMaterialInput) -> str:
        """Batch apply material to matching objects.

        Args:
            params: Object pattern, material name, etc.

        Returns:
            Application result
        """
        result = await server.execute_command(
            "batch", "apply_material",
            {
                "pattern": params.pattern,
                "material_name": params.material_name,
                "replace_existing": params.replace_existing
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("objects_affected", 0)
            return f"Successfully applied material '{params.material_name}' to {count} objects"
        else:
            return f"Application failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_transform",
        annotations={
            "title": "Batch Transform",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_transform(params: BatchTransformInput) -> str:
        """Batch transform matching objects.

        Args:
            params: Object pattern, location/rotation/scale offsets

        Returns:
            Transform result
        """
        result = await server.execute_command(
            "batch", "transform",
            {
                "pattern": params.pattern,
                "location_offset": params.location_offset,
                "rotation_offset": params.rotation_offset,
                "scale_factor": params.scale_factor
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("objects_affected", 0)
            return f"Successfully transformed {count} objects"
        else:
            return f"Transform failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_rename",
        annotations={
            "title": "Batch Rename",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_batch_rename(params: BatchRenameInput) -> str:
        """Batch rename matching objects.

        Args:
            params: Object pattern, new name, numbering, etc.

        Returns:
            Rename result
        """
        result = await server.execute_command(
            "batch", "rename",
            {
                "pattern": params.pattern,
                "new_name": params.new_name,
                "numbering": params.numbering,
                "start_number": params.start_number
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("objects_renamed", 0)
            return f"Successfully renamed {count} objects"
        else:
            return f"Rename failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_delete",
        annotations={
            "title": "Batch Delete",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_delete(params: BatchDeleteInput) -> str:
        """Batch delete matching objects.

        Args:
            params: Object pattern, whether to delete data

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "batch", "delete",
            {
                "pattern": params.pattern,
                "delete_data": params.delete_data
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("objects_deleted", 0)
            return f"Successfully deleted {count} objects"
        else:
            return f"Deletion failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_export",
        annotations={
            "title": "Batch Export",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_batch_export(params: BatchExportInput) -> str:
        """Batch export matching objects.

        Args:
            params: Object pattern, export path, format, etc.

        Returns:
            Export result
        """
        result = await server.execute_command(
            "batch", "export",
            {
                "pattern": params.pattern,
                "export_path": params.export_path,
                "format": params.format,
                "individual_files": params.individual_files
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("files_exported", 0)
            return f"Successfully exported {count} files to '{params.export_path}'"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_add_modifier",
        annotations={
            "title": "Batch Add Modifier",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_batch_add_modifier(params: BatchModifierInput) -> str:
        """Batch add modifiers to matching objects.

        Args:
            params: Object pattern, modifier type, settings

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "batch", "add_modifier",
            {
                "pattern": params.pattern,
                "modifier_type": params.modifier_type,
                "settings": params.settings or {}
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("modifiers_added", 0)
            return f"Successfully added {params.modifier_type} modifier to {count} objects"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_batch_set_parent",
        annotations={
            "title": "Batch Set Parent",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_set_parent(params: BatchParentInput) -> str:
        """Batch set parent for matching objects.

        Args:
            params: Child object pattern, parent object name

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "batch", "set_parent",
            {
                "pattern": params.pattern,
                "parent_name": params.parent_name,
                "keep_transform": params.keep_transform
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("objects_parented", 0)
            return f"Successfully set {count} objects as children of '{params.parent_name}'"
        else:
            return f"Setting failed: {result.get('error', {}).get('message', 'unknown error')}"
