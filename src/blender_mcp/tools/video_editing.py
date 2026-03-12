"""
Video Editing Tools

Provides video clipping, effects, rendering, and related functionality.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class VSEAddStripInput(BaseModel):
    """Add strip input"""
    strip_type: str = Field(
        default="MOVIE",
        description="Strip type: MOVIE, IMAGE, SOUND, SCENE, COLOR, TEXT"
    )
    filepath: Optional[str] = Field(default=None, description="File path (video/image/audio)")
    channel: int = Field(default=1, description="Channel", ge=1, le=128)
    start_frame: int = Field(default=1, description="Start frame")
    # Type-specific parameters
    text: Optional[str] = Field(default=None, description="Text content (TEXT type)")
    color: Optional[List[float]] = Field(default=None, description="Color RGBA (COLOR type)")
    scene_name: Optional[str] = Field(default=None, description="Scene name (SCENE type)")


class VSECutInput(BaseModel):
    """Cut strip input"""
    channel: int = Field(..., description="Channel")
    frame: int = Field(..., description="Cut frame")
    cut_type: str = Field(default="SOFT", description="Cut type: SOFT, HARD")


class VSETransformInput(BaseModel):
    """Transform strip input"""
    strip_name: str = Field(..., description="Strip name")
    position: Optional[List[float]] = Field(default=None, description="Position [x, y]")
    scale: Optional[List[float]] = Field(default=None, description="Scale [x, y]")
    rotation: Optional[float] = Field(default=None, description="Rotation angle")
    opacity: Optional[float] = Field(default=None, description="Opacity", ge=0, le=1)


class VSEEffectInput(BaseModel):
    """Add effect input"""
    effect_type: str = Field(
        default="CROSS",
        description="Effect type: CROSS, ADD, SUBTRACT, MULTIPLY, GAMMA_CROSS, WIPE, TRANSFORM, SPEED, GLOW"
    )
    channel: int = Field(default=1, description="Channel")
    start_frame: int = Field(default=1, description="Start frame")
    end_frame: int = Field(default=30, description="End frame")
    seq1_name: Optional[str] = Field(default=None, description="First sequence name")
    seq2_name: Optional[str] = Field(default=None, description="Second sequence name")


class VSETextInput(BaseModel):
    """Text strip input"""
    text: str = Field(..., description="Text content")
    channel: int = Field(default=1, description="Channel")
    start_frame: int = Field(default=1, description="Start frame")
    duration: int = Field(default=100, description="Duration in frames")
    font_size: float = Field(default=60.0, description="Font size")
    color: Optional[List[float]] = Field(default=None, description="Color RGBA")
    location: Optional[List[float]] = Field(default=None, description="Location [x, y]")


class VSERenderInput(BaseModel):
    """Render video input"""
    output_path: str = Field(..., description="Output path")
    format: str = Field(default="MPEG4", description="Format: MPEG4, AVI, QUICKTIME")
    codec: str = Field(default="H264", description="Codec: H264, MPEG4, PNG")
    quality: int = Field(default=90, description="Quality", ge=1, le=100)


# ==================== Tool Registration ====================

def register_video_editing_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register video editing tools"""

    @mcp.tool(
        name="blender_vse_add_strip",
        annotations={
            "title": "Add Video Strip",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_vse_add_strip(params: VSEAddStripInput) -> str:
        """Add a strip in the Video Sequence Editor.

        Supported types:
        - MOVIE: Video file
        - IMAGE: Image sequence
        - SOUND: Audio file
        - SCENE: Blender scene
        - COLOR: Solid color strip
        - TEXT: Text strip

        Args:
            params: Strip type, file path, channel, etc.

        Returns:
            Add result
        """
        result = await server.execute_command(
            "vse", "add_strip",
            {
                "strip_type": params.strip_type,
                "filepath": params.filepath,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "text": params.text,
                "color": params.color,
                "scene_name": params.scene_name
            }
        )

        if result.get("success"):
            name = result.get("data", {}).get("strip_name", "")
            return f"Successfully added strip '{name}'"
        else:
            return f"Add failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vse_cut",
        annotations={
            "title": "Cut Strip",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_cut(params: VSECutInput) -> str:
        """Cut a strip at a specified frame.

        Args:
            params: Channel, frame position, cut type

        Returns:
            Cut result
        """
        result = await server.execute_command(
            "vse", "cut",
            {
                "channel": params.channel,
                "frame": params.frame,
                "cut_type": params.cut_type
            }
        )

        if result.get("success"):
            return f"Successfully cut at frame {params.frame}"
        else:
            return f"Cut failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vse_transform",
        annotations={
            "title": "Transform Strip",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_vse_transform(params: VSETransformInput) -> str:
        """Transform a video strip (position, scale, rotation, opacity).

        Args:
            params: Strip name, position, scale, etc.

        Returns:
            Transform result
        """
        result = await server.execute_command(
            "vse", "transform",
            {
                "strip_name": params.strip_name,
                "position": params.position,
                "scale": params.scale,
                "rotation": params.rotation,
                "opacity": params.opacity
            }
        )

        if result.get("success"):
            return f"Successfully transformed strip '{params.strip_name}'"
        else:
            return f"Transform failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vse_add_effect",
        annotations={
            "title": "Add Video Effect",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_add_effect(params: VSEEffectInput) -> str:
        """Add a video effect (transition, overlay, etc.).

        Args:
            params: Effect type, channel, frame range

        Returns:
            Add result
        """
        result = await server.execute_command(
            "vse", "add_effect",
            {
                "effect_type": params.effect_type,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "end_frame": params.end_frame,
                "seq1_name": params.seq1_name,
                "seq2_name": params.seq2_name
            }
        )

        if result.get("success"):
            return f"Successfully added {params.effect_type} effect"
        else:
            return f"Add failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vse_add_text",
        annotations={
            "title": "Add Text",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vse_add_text(params: VSETextInput) -> str:
        """Add a text strip.

        Args:
            params: Text content, font size, color, etc.

        Returns:
            Add result
        """
        result = await server.execute_command(
            "vse", "add_text",
            {
                "text": params.text,
                "channel": params.channel,
                "start_frame": params.start_frame,
                "duration": params.duration,
                "font_size": params.font_size,
                "color": params.color,
                "location": params.location
            }
        )

        if result.get("success"):
            return f"Successfully added text '{params.text}'"
        else:
            return f"Add failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vse_render",
        annotations={
            "title": "Render Video",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_vse_render(params: VSERenderInput) -> str:
        """Render the video sequence.

        Args:
            params: Output path, format, codec, etc.

        Returns:
            Render result
        """
        result = await server.execute_command(
            "vse", "render",
            {
                "output_path": params.output_path,
                "format": params.format,
                "codec": params.codec,
                "quality": params.quality
            }
        )

        if result.get("success"):
            return f"Video rendering complete: {params.output_path}"
        else:
            return f"Render failed: {result.get('error', {}).get('message', 'Unknown error')}"
