"""
Texture Painting Tools

Provides texture painting related MCP tools.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class TexturePaintModeInput(BaseModel):
    """Enter/exit texture paint mode"""

    object_name: str = Field(..., description="Object name")
    enable: bool = Field(True, description="Whether to enter texture paint mode")


class TextureCreateInput(BaseModel):
    """Create a new texture"""

    name: str = Field(..., description="Texture name")
    width: int = Field(1024, description="Width")
    height: int = Field(1024, description="Height")
    color: list[float] = Field([0.0, 0.0, 0.0, 1.0], description="Initial color [R,G,B,A]")
    alpha: bool = Field(True, description="Whether to include alpha channel")
    float_buffer: bool = Field(False, description="Whether to use 32-bit float")


class TexturePaintBrushInput(BaseModel):
    """Set paint brush"""

    brush_type: str = Field(
        "DRAW", description="Brush type: DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK"
    )
    color: list[float] = Field([1.0, 1.0, 1.0], description="Color [R,G,B]")
    radius: float = Field(50.0, description="Brush radius")
    strength: float = Field(1.0, description="Brush strength (0-1)")
    blend: str = Field("MIX", description="Blend mode: MIX, ADD, SUBTRACT, MULTIPLY, etc.")


class TexturePaintStrokeInput(BaseModel):
    """Execute a paint stroke"""

    object_name: str = Field(..., description="Object name")
    uv_points: list[list[float]] = Field(
        ..., description="UV coordinate point list [[u,v,pressure], ...]"
    )
    color: list[float] | None = Field(None, description="Color [R,G,B]")


class TexturePaintFillInput(BaseModel):
    """Fill with color"""

    object_name: str = Field(..., description="Object name")
    color: list[float] = Field([1.0, 1.0, 1.0, 1.0], description="Fill color [R,G,B,A]")
    texture_slot: int = Field(0, description="Texture slot index")


class TextureBakeInput(BaseModel):
    """Bake texture"""

    object_name: str = Field(..., description="Object name")
    bake_type: str = Field(
        "DIFFUSE",
        description="Bake type: DIFFUSE, AO, SHADOW, NORMAL, UV, EMIT, ENVIRONMENT, COMBINED",
    )
    width: int = Field(1024, description="Output width")
    height: int = Field(1024, description="Output height")
    margin: int = Field(16, description="Margin extension")
    output_path: str | None = Field(None, description="Output path")


class TextureSlotInput(BaseModel):
    """Texture slot management"""

    object_name: str = Field(..., description="Object name")
    action: str = Field("ADD", description="Action: ADD, REMOVE, SELECT")
    texture_name: str | None = Field(None, description="Texture name")
    slot_index: int = Field(0, description="Slot index")


class TextureSaveInput(BaseModel):
    """Save texture"""

    texture_name: str = Field(..., description="Texture name")
    filepath: str = Field(..., description="Save path")
    file_format: str = Field("PNG", description="File format: PNG, JPEG, TIFF, BMP, OPEN_EXR")


# ============ Tool Registration ============


def register_texture_painting_tools(mcp: FastMCP, server) -> None:
    """Register texture painting tools"""

    @mcp.tool()
    async def blender_texture_paint_mode(object_name: str, enable: bool = True) -> dict[str, Any]:
        """
        Enter or exit texture paint mode

        Args:
            object_name: Name of the object to paint
            enable: True to enter texture paint mode, False to exit
        """
        params = TexturePaintModeInput(object_name=object_name, enable=enable)
        return await server.send_command("texture_paint", "mode", params.model_dump())

    @mcp.tool()
    async def blender_texture_create(
        name: str,
        width: int = 1024,
        height: int = 1024,
        color: list[float] = None,
        alpha: bool = True,
        float_buffer: bool = False,
    ) -> dict[str, Any]:
        """
        Create a new texture

        Args:
            name: Texture name
            width: Width (pixels)
            height: Height (pixels)
            color: Initial color [R,G,B,A]
            alpha: Whether to include alpha channel
            float_buffer: Whether to use 32-bit float precision
        """
        if color is None:
            color = [0.0, 0.0, 0.0, 1.0]
        params = TextureCreateInput(
            name=name,
            width=width,
            height=height,
            color=color,
            alpha=alpha,
            float_buffer=float_buffer,
        )
        return await server.send_command("texture_paint", "create", params.model_dump())

    @mcp.tool()
    async def blender_texture_paint_set_brush(
        brush_type: str = "DRAW",
        color: list[float] = None,
        radius: float = 50.0,
        strength: float = 1.0,
        blend: str = "MIX",
    ) -> dict[str, Any]:
        """
        Set texture paint brush

        Args:
            brush_type: Brush type (DRAW, SOFTEN, SMEAR, CLONE, FILL, MASK)
            color: Paint color [R,G,B]
            radius: Brush radius
            strength: Brush strength (0-1)
            blend: Blend mode (MIX, ADD, SUBTRACT, MULTIPLY, etc.)
        """
        if color is None:
            color = [1.0, 1.0, 1.0]
        params = TexturePaintBrushInput(
            brush_type=brush_type, color=color, radius=radius, strength=strength, blend=blend
        )
        return await server.send_command("texture_paint", "set_brush", params.model_dump())

    @mcp.tool()
    async def blender_texture_paint_stroke(
        object_name: str, uv_points: list[list[float]], color: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Execute a texture paint stroke

        Args:
            object_name: Object name
            uv_points: UV coordinate point list [[u,v,pressure], ...]
            color: Optional paint color [R,G,B]
        """
        params = TexturePaintStrokeInput(object_name=object_name, uv_points=uv_points, color=color)
        return await server.send_command("texture_paint", "stroke", params.model_dump())

    @mcp.tool()
    async def blender_texture_paint_fill(
        object_name: str, color: list[float] = None, texture_slot: int = 0
    ) -> dict[str, Any]:
        """
        Fill texture with color

        Args:
            object_name: Object name
            color: Fill color [R,G,B,A]
            texture_slot: Texture slot index
        """
        if color is None:
            color = [1.0, 1.0, 1.0, 1.0]
        params = TexturePaintFillInput(
            object_name=object_name, color=color, texture_slot=texture_slot
        )
        return await server.send_command("texture_paint", "fill", params.model_dump())

    @mcp.tool()
    async def blender_texture_bake(
        object_name: str,
        bake_type: str = "DIFFUSE",
        width: int = 1024,
        height: int = 1024,
        margin: int = 16,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Bake texture

        Args:
            object_name: Object name
            bake_type: Bake type (DIFFUSE, AO, SHADOW, NORMAL, UV, EMIT, COMBINED)
            width: Output width
            height: Output height
            margin: Margin extension pixels
            output_path: Output file path
        """
        params = TextureBakeInput(
            object_name=object_name,
            bake_type=bake_type,
            width=width,
            height=height,
            margin=margin,
            output_path=output_path,
        )
        return await server.send_command("texture_paint", "bake", params.model_dump())

    @mcp.tool()
    async def blender_texture_slot(
        object_name: str, action: str = "ADD", texture_name: str | None = None, slot_index: int = 0
    ) -> dict[str, Any]:
        """
        Manage texture slots

        Args:
            object_name: Object name
            action: Action type (ADD, REMOVE, SELECT)
            texture_name: Texture name
            slot_index: Slot index
        """
        params = TextureSlotInput(
            object_name=object_name, action=action, texture_name=texture_name, slot_index=slot_index
        )
        return await server.send_command("texture_paint", "slot", params.model_dump())

    @mcp.tool()
    async def blender_texture_save(
        texture_name: str, filepath: str, file_format: str = "PNG"
    ) -> dict[str, Any]:
        """
        Save texture to file

        Args:
            texture_name: Texture name
            filepath: Save path
            file_format: File format (PNG, JPEG, TIFF, BMP, OPEN_EXR)
        """
        params = TextureSaveInput(
            texture_name=texture_name, filepath=filepath, file_format=file_format
        )
        return await server.send_command("texture_paint", "save", params.model_dump())
