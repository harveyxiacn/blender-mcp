"""
Grease Pencil / 2D Animation Tools

Provides Grease Pencil related MCP tools.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class GPencilCreateInput(BaseModel):
    """Create grease pencil object"""
    name: str = Field("GPencil", description="Object name")
    location: List[float] = Field([0, 0, 0], description="Location")
    stroke_depth_order: str = Field("3D", description="Depth order: 2D, 3D")


class GPencilLayerInput(BaseModel):
    """Layer operations"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    action: str = Field("ADD", description="Action: ADD, REMOVE, RENAME, MOVE")
    layer_name: str = Field("Layer", description="Layer name")
    new_name: Optional[str] = Field(None, description="New name (for renaming)")
    color: Optional[List[float]] = Field(None, description="Layer color")


class GPencilFrameInput(BaseModel):
    """Frame operations"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    layer_name: str = Field("Layer", description="Layer name")
    action: str = Field("ADD", description="Action: ADD, REMOVE, COPY, DUPLICATE")
    frame_number: int = Field(1, description="Frame number")
    target_frame: Optional[int] = Field(None, description="Target frame (for copying)")


class GPencilDrawInput(BaseModel):
    """Draw strokes"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    layer_name: str = Field("Layer", description="Layer name")
    points: List[List[float]] = Field(
        ...,
        description="Point list [[x,y,z,pressure,strength], ...]"
    )
    material_index: int = Field(0, description="Material index")
    line_width: int = Field(10, description="Line width")


class GPencilMaterialInput(BaseModel):
    """Grease pencil material"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    name: str = Field("GPMaterial", description="Material name")
    mode: str = Field("LINE", description="Mode: LINE, DOTS, BOX, FILL")
    stroke_color: List[float] = Field([0, 0, 0, 1], description="Stroke color")
    fill_color: Optional[List[float]] = Field(None, description="Fill color")


class GPencilModifierInput(BaseModel):
    """Grease pencil modifier"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    modifier_type: str = Field(
        "SMOOTH",
        description="Modifier type: SMOOTH, NOISE, THICKNESS, TINT, OFFSET, OPACITY, etc."
    )
    modifier_name: Optional[str] = Field(None, description="Modifier name")
    settings: Optional[Dict[str, Any]] = Field(None, description="Modifier settings")


class GPencilEffectInput(BaseModel):
    """Grease pencil effect"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    effect_type: str = Field(
        "BLUR",
        description="Effect type: BLUR, COLORIZE, FLIP, GLOW, LIGHT, PIXELATE, RIM, SHADOW, SWIRL, WAVE"
    )
    effect_name: Optional[str] = Field(None, description="Effect name")


class GPencilConvertInput(BaseModel):
    """Conversion"""
    gpencil_name: str = Field(..., description="Grease pencil object name")
    target_type: str = Field("CURVE", description="Target type: CURVE, MESH")
    keep_original: bool = Field(True, description="Keep original object")


# ============ Tool Registration ============

def register_grease_pencil_tools(mcp: FastMCP, server):
    """Register grease pencil tools"""

    @mcp.tool()
    async def blender_gpencil_create(
        name: str = "GPencil",
        location: List[float] = [0, 0, 0],
        stroke_depth_order: str = "3D"
    ) -> Dict[str, Any]:
        """
        Create a grease pencil object

        Args:
            name: Object name
            location: Location [x, y, z]
            stroke_depth_order: Depth order (2D or 3D)
        """
        params = GPencilCreateInput(
            name=name,
            location=location,
            stroke_depth_order=stroke_depth_order
        )
        return await server.send_command("gpencil", "create", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_layer(
        gpencil_name: str,
        action: str = "ADD",
        layer_name: str = "Layer",
        new_name: Optional[str] = None,
        color: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Grease pencil layer operations

        Args:
            gpencil_name: Grease pencil object name
            action: Action type (ADD, REMOVE, RENAME, MOVE)
            layer_name: Layer name
            new_name: New name (used when renaming)
            color: Layer color [R,G,B]
        """
        params = GPencilLayerInput(
            gpencil_name=gpencil_name,
            action=action,
            layer_name=layer_name,
            new_name=new_name,
            color=color
        )
        return await server.send_command("gpencil", "layer", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_frame(
        gpencil_name: str,
        layer_name: str = "Layer",
        action: str = "ADD",
        frame_number: int = 1,
        target_frame: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Grease pencil frame operations

        Args:
            gpencil_name: Grease pencil object name
            layer_name: Layer name
            action: Action type (ADD, REMOVE, COPY, DUPLICATE)
            frame_number: Frame number
            target_frame: Target frame (used when copying)
        """
        params = GPencilFrameInput(
            gpencil_name=gpencil_name,
            layer_name=layer_name,
            action=action,
            frame_number=frame_number,
            target_frame=target_frame
        )
        return await server.send_command("gpencil", "frame", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_draw(
        gpencil_name: str,
        layer_name: str,
        points: List[List[float]],
        material_index: int = 0,
        line_width: int = 10
    ) -> Dict[str, Any]:
        """
        Draw grease pencil strokes

        Args:
            gpencil_name: Grease pencil object name
            layer_name: Layer name
            points: Point list [[x,y,z,pressure,strength], ...]
            material_index: Material index
            line_width: Line width
        """
        params = GPencilDrawInput(
            gpencil_name=gpencil_name,
            layer_name=layer_name,
            points=points,
            material_index=material_index,
            line_width=line_width
        )
        return await server.send_command("gpencil", "draw", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_material(
        gpencil_name: str,
        name: str = "GPMaterial",
        mode: str = "LINE",
        stroke_color: List[float] = [0, 0, 0, 1],
        fill_color: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Create a grease pencil material

        Args:
            gpencil_name: Grease pencil object name
            name: Material name
            mode: Mode (LINE, DOTS, BOX, FILL)
            stroke_color: Stroke color [R,G,B,A]
            fill_color: Fill color [R,G,B,A]
        """
        params = GPencilMaterialInput(
            gpencil_name=gpencil_name,
            name=name,
            mode=mode,
            stroke_color=stroke_color,
            fill_color=fill_color
        )
        return await server.send_command("gpencil", "material", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_modifier(
        gpencil_name: str,
        modifier_type: str = "SMOOTH",
        modifier_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a grease pencil modifier

        Args:
            gpencil_name: Grease pencil object name
            modifier_type: Modifier type (SMOOTH, NOISE, THICKNESS, TINT, OFFSET, etc.)
            modifier_name: Modifier name
            settings: Modifier settings
        """
        params = GPencilModifierInput(
            gpencil_name=gpencil_name,
            modifier_type=modifier_type,
            modifier_name=modifier_name,
            settings=settings
        )
        return await server.send_command("gpencil", "modifier", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_effect(
        gpencil_name: str,
        effect_type: str = "BLUR",
        effect_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a grease pencil effect

        Args:
            gpencil_name: Grease pencil object name
            effect_type: Effect type (BLUR, GLOW, SHADOW, RIM, WAVE, etc.)
            effect_name: Effect name
        """
        params = GPencilEffectInput(
            gpencil_name=gpencil_name,
            effect_type=effect_type,
            effect_name=effect_name
        )
        return await server.send_command("gpencil", "effect", params.model_dump())

    @mcp.tool()
    async def blender_gpencil_convert(
        gpencil_name: str,
        target_type: str = "CURVE",
        keep_original: bool = True
    ) -> Dict[str, Any]:
        """
        Convert grease pencil to another type

        Args:
            gpencil_name: Grease pencil object name
            target_type: Target type (CURVE or MESH)
            keep_original: Whether to keep the original object
        """
        params = GPencilConvertInput(
            gpencil_name=gpencil_name,
            target_type=target_type,
            keep_original=keep_original
        )
        return await server.send_command("gpencil", "convert", params.model_dump())
