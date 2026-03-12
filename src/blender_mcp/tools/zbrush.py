"""
ZBrush Connection Tools

Provides MCP tools for ZBrush integration.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class ZBrushExportInput(BaseModel):
    """Export to ZBrush"""
    object_name: str = Field(..., description="Object name")
    filepath: Optional[str] = Field(None, description="Export path (uses GoZ if empty)")
    subdivisions: int = Field(0, description="Subdivision level")


class ZBrushImportInput(BaseModel):
    """Import from ZBrush"""
    filepath: Optional[str] = Field(None, description="File path (imports from GoZ if empty)")
    import_polypaint: bool = Field(True, description="Import vertex colors")
    import_mask: bool = Field(True, description="Import mask")


class ZBrushMapsInput(BaseModel):
    """Import ZBrush maps"""
    displacement_path: Optional[str] = Field(None, description="Displacement map path")
    normal_path: Optional[str] = Field(None, description="Normal map path")
    polypaint_path: Optional[str] = Field(None, description="Polypaint map path")
    object_name: str = Field(..., description="Target object")


class ZBrushDecimateInput(BaseModel):
    """Export decimated model"""
    object_name: str = Field(..., description="Object name")
    target_faces: int = Field(10000, description="Target face count")
    filepath: str = Field(..., description="Export path")


# ============ Tool Registration ============

def register_zbrush_tools(mcp: FastMCP, server):
    """Register ZBrush connection tools"""

    @mcp.tool()
    async def blender_zbrush_export(
        object_name: str,
        filepath: Optional[str] = None,
        subdivisions: int = 0
    ) -> Dict[str, Any]:
        """
        Export model to ZBrush

        Args:
            object_name: Object name
            filepath: Export path (uses GoZ protocol if empty)
            subdivisions: Subdivision level
        """
        params = ZBrushExportInput(
            object_name=object_name,
            filepath=filepath,
            subdivisions=subdivisions
        )
        return await server.send_command("zbrush", "export", params.model_dump())

    @mcp.tool()
    async def blender_zbrush_import(
        filepath: Optional[str] = None,
        import_polypaint: bool = True,
        import_mask: bool = True
    ) -> Dict[str, Any]:
        """
        Import model from ZBrush

        Args:
            filepath: File path (imports from GoZ if empty)
            import_polypaint: Import vertex colors
            import_mask: Import mask
        """
        params = ZBrushImportInput(
            filepath=filepath,
            import_polypaint=import_polypaint,
            import_mask=import_mask
        )
        return await server.send_command("zbrush", "import", params.model_dump())

    @mcp.tool()
    async def blender_zbrush_goz_send(
        object_name: str
    ) -> Dict[str, Any]:
        """
        Send to ZBrush via GoZ

        Args:
            object_name: Object name
        """
        return await server.send_command("zbrush", "goz_send", {
            "object_name": object_name
        })

    @mcp.tool()
    async def blender_zbrush_goz_receive() -> Dict[str, Any]:
        """
        Receive ZBrush model from GoZ
        """
        return await server.send_command("zbrush", "goz_receive", {})

    @mcp.tool()
    async def blender_zbrush_maps(
        object_name: str,
        displacement_path: Optional[str] = None,
        normal_path: Optional[str] = None,
        polypaint_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import maps exported from ZBrush

        Args:
            object_name: Target object name
            displacement_path: Displacement map path
            normal_path: Normal map path
            polypaint_path: Polypaint map path
        """
        params = ZBrushMapsInput(
            object_name=object_name,
            displacement_path=displacement_path,
            normal_path=normal_path,
            polypaint_path=polypaint_path
        )
        return await server.send_command("zbrush", "maps", params.model_dump())

    @mcp.tool()
    async def blender_zbrush_decimate_export(
        object_name: str,
        target_faces: int = 10000,
        filepath: str = ""
    ) -> Dict[str, Any]:
        """
        Export decimated model for ZBrush projection

        Args:
            object_name: Object name
            target_faces: Target face count
            filepath: Export path
        """
        params = ZBrushDecimateInput(
            object_name=object_name,
            target_faces=target_faces,
            filepath=filepath
        )
        return await server.send_command("zbrush", "decimate_export", params.model_dump())

    @mcp.tool()
    async def blender_zbrush_detect() -> Dict[str, Any]:
        """
        Detect ZBrush installation and GoZ configuration
        """
        return await server.send_command("zbrush", "detect", {})
