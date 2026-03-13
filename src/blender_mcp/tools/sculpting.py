"""
Sculpting tools

Provides MCP tools for digital sculpting.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class SculptModeInput(BaseModel):
    """Enter/exit sculpt mode"""

    object_name: str = Field(..., description="Object name")
    enable: bool = Field(True, description="Whether to enter sculpt mode")


class SculptBrushInput(BaseModel):
    """Set sculpt brush"""

    brush_type: str = Field(
        "DRAW",
        description="Brush type: DRAW, CLAY, CLAY_STRIPS, INFLATE, BLOB, CREASE, SMOOTH, FLATTEN, FILL, SCRAPE, PINCH, GRAB, SNAKE_HOOK, THUMB, NUDGE, ROTATE, MASK, DRAW_FACE_SETS",
    )
    radius: float = Field(50.0, description="Brush radius")
    strength: float = Field(0.5, description="Brush strength (0-1)")
    auto_smooth: float = Field(0.0, description="Auto smooth (0-1)")


class SculptStrokeInput(BaseModel):
    """Execute sculpt stroke"""

    object_name: str = Field(..., description="Object name")
    stroke_points: list[list[float]] = Field(
        ..., description="Stroke point list [[x,y,z,pressure], ...]"
    )
    brush_type: str | None = Field(None, description="Brush type")


class SculptRemeshInput(BaseModel):
    """Remesh"""

    object_name: str = Field(..., description="Object name")
    mode: str = Field("VOXEL", description="Mode: VOXEL, QUAD")
    voxel_size: float = Field(0.1, description="Voxel size")
    smooth_normals: bool = Field(True, description="Smooth normals")


class SculptMultiresInput(BaseModel):
    """Multiresolution subdivision"""

    object_name: str = Field(..., description="Object name")
    levels: int = Field(2, description="Subdivision levels")
    sculpt_level: int | None = Field(None, description="Sculpt level")


class SculptMaskInput(BaseModel):
    """Mask operation"""

    object_name: str = Field(..., description="Object name")
    action: str = Field("CLEAR", description="Action: CLEAR, INVERT, SMOOTH, EXPAND, CONTRACT")


class SculptSymmetryInput(BaseModel):
    """Set symmetry"""

    use_x: bool = Field(True, description="X axis symmetry")
    use_y: bool = Field(False, description="Y axis symmetry")
    use_z: bool = Field(False, description="Z axis symmetry")


class SculptDyntopoInput(BaseModel):
    """Dynamic topology"""

    object_name: str = Field(..., description="Object name")
    enable: bool = Field(True, description="Enable dynamic topology")
    detail_size: float = Field(12.0, description="Detail size")
    detail_type: str = Field("RELATIVE", description="Detail type: RELATIVE, CONSTANT, BRUSH")


# ============ Tool Registration ============


def register_sculpting_tools(mcp: FastMCP, server) -> None:
    """Register sculpting tools"""

    @mcp.tool()
    async def blender_sculpt_mode(object_name: str, enable: bool = True) -> dict[str, Any]:
        """
        Enter or exit sculpt mode

        Args:
            object_name: Name of the object to sculpt
            enable: True to enter sculpt mode, False to exit
        """
        params = SculptModeInput(object_name=object_name, enable=enable)
        return await server.send_command("sculpt", "mode", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_set_brush(
        brush_type: str = "DRAW",
        radius: float = 50.0,
        strength: float = 0.5,
        auto_smooth: float = 0.0,
    ) -> dict[str, Any]:
        """
        Set sculpt brush

        Args:
            brush_type: Brush type (DRAW, CLAY, CLAY_STRIPS, INFLATE, SMOOTH, GRAB, etc.)
            radius: Brush radius
            strength: Brush strength (0-1)
            auto_smooth: Auto smooth value (0-1)
        """
        params = SculptBrushInput(
            brush_type=brush_type, radius=radius, strength=strength, auto_smooth=auto_smooth
        )
        return await server.send_command("sculpt", "set_brush", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_stroke(
        object_name: str, stroke_points: list[list[float]], brush_type: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a sculpt stroke

        Args:
            object_name: Object name
            stroke_points: Stroke point list [[x,y,z,pressure], ...]
            brush_type: Optional brush type
        """
        params = SculptStrokeInput(
            object_name=object_name, stroke_points=stroke_points, brush_type=brush_type
        )
        return await server.send_command("sculpt", "stroke", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_remesh(
        object_name: str, mode: str = "VOXEL", voxel_size: float = 0.1, smooth_normals: bool = True
    ) -> dict[str, Any]:
        """
        Remesh the object

        Args:
            object_name: Object name
            mode: Remesh mode (VOXEL or QUAD)
            voxel_size: Voxel size
            smooth_normals: Whether to smooth normals
        """
        params = SculptRemeshInput(
            object_name=object_name, mode=mode, voxel_size=voxel_size, smooth_normals=smooth_normals
        )
        return await server.send_command("sculpt", "remesh", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_multires(
        object_name: str, levels: int = 2, sculpt_level: int | None = None
    ) -> dict[str, Any]:
        """
        Add multiresolution modifier

        Args:
            object_name: Object name
            levels: Subdivision levels
            sculpt_level: Sculpt level
        """
        params = SculptMultiresInput(
            object_name=object_name, levels=levels, sculpt_level=sculpt_level
        )
        return await server.send_command("sculpt", "multires", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_mask(object_name: str, action: str = "CLEAR") -> dict[str, Any]:
        """
        Sculpt mask operation

        Args:
            object_name: Object name
            action: Action type (CLEAR, INVERT, SMOOTH, EXPAND, CONTRACT)
        """
        params = SculptMaskInput(object_name=object_name, action=action)
        return await server.send_command("sculpt", "mask", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_symmetry(
        use_x: bool = True, use_y: bool = False, use_z: bool = False
    ) -> dict[str, Any]:
        """
        Set sculpt symmetry

        Args:
            use_x: X axis symmetry
            use_y: Y axis symmetry
            use_z: Z axis symmetry
        """
        params = SculptSymmetryInput(use_x=use_x, use_y=use_y, use_z=use_z)
        return await server.send_command("sculpt", "symmetry", params.model_dump())

    @mcp.tool()
    async def blender_sculpt_dyntopo(
        object_name: str,
        enable: bool = True,
        detail_size: float = 12.0,
        detail_type: str = "RELATIVE",
    ) -> dict[str, Any]:
        """
        Enable dynamic topology

        Args:
            object_name: Object name
            enable: Whether to enable
            detail_size: Detail size
            detail_type: Detail type (RELATIVE, CONSTANT, BRUSH)
        """
        params = SculptDyntopoInput(
            object_name=object_name, enable=enable, detail_size=detail_size, detail_type=detail_type
        )
        return await server.send_command("sculpt", "dyntopo", params.model_dump())
