"""
Render tools

Provides render settings and rendering functionality.
"""

from typing import TYPE_CHECKING, Optional
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class RenderEngine(str, Enum):
    """Render engine"""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    EEVEE_NEXT = "BLENDER_EEVEE_NEXT"
    WORKBENCH = "BLENDER_WORKBENCH"


class FileFormat(str, Enum):
    """File format"""
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    EXR = "OPEN_EXR"
    BMP = "BMP"


# ==================== Input Models ====================

class RenderSettingsInput(BaseModel):
    """Render settings input"""
    engine: Optional[RenderEngine] = Field(default=None, description="Render engine")
    resolution_x: Optional[int] = Field(default=None, description="Horizontal resolution", ge=1, le=16384)
    resolution_y: Optional[int] = Field(default=None, description="Vertical resolution", ge=1, le=16384)
    resolution_percentage: Optional[int] = Field(default=None, description="Resolution percentage", ge=1, le=100)
    samples: Optional[int] = Field(default=None, description="Sample count", ge=1, le=16384)
    use_denoising: Optional[bool] = Field(default=None, description="Use denoising")
    file_format: Optional[FileFormat] = Field(default=None, description="Output format")
    output_path: Optional[str] = Field(default=None, description="Output path")


class RenderImageInput(BaseModel):
    """Render image input"""
    output_path: Optional[str] = Field(default=None, description="Output path")
    frame: Optional[int] = Field(default=None, description="Render frame")
    camera: Optional[str] = Field(default=None, description="Camera name")
    write_still: bool = Field(default=True, description="Save image")


class RenderAnimationInput(BaseModel):
    """Render animation input"""
    output_path: str = Field(..., description="Output directory")
    frame_start: Optional[int] = Field(default=None, description="Start frame")
    frame_end: Optional[int] = Field(default=None, description="End frame")
    frame_step: int = Field(default=1, description="Frame step", ge=1)


class RenderPreviewInput(BaseModel):
    """Render preview input"""
    resolution_percentage: int = Field(default=50, description="Resolution percentage", ge=1, le=100)
    samples: int = Field(default=32, description="Sample count", ge=1, le=256)


class ViewType(str, Enum):
    """View type"""
    PERSP = "PERSP"     # Perspective
    FRONT = "FRONT"     # Front view
    BACK = "BACK"       # Back view
    LEFT = "LEFT"       # Left view
    RIGHT = "RIGHT"     # Right view
    TOP = "TOP"         # Top view
    BOTTOM = "BOTTOM"   # Bottom view


class GetViewportScreenshotInput(BaseModel):
    """Get viewport screenshot input"""
    output_path: Optional[str] = Field(default=None, description="Output path (uses temp directory if not provided)")
    width: int = Field(default=800, description="Screenshot width", ge=64, le=4096)
    height: int = Field(default=600, description="Screenshot height", ge=64, le=4096)
    view_type: Optional[ViewType] = Field(default=None, description="View type")
    return_base64: bool = Field(default=False, description="Whether to return base64-encoded image data")


# ==================== Tool Registration ====================

def register_render_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register render tools"""

    @mcp.tool(
        name="blender_render_settings",
        annotations={
            "title": "Set Render Parameters",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_render_settings(params: RenderSettingsInput) -> str:
        """Set render parameters.

        Can set render engine, resolution, sample count, etc.

        Args:
            params: Render settings

        Returns:
            Settings result
        """
        settings = {}
        if params.engine is not None:
            settings["engine"] = params.engine.value
        if params.resolution_x is not None:
            settings["resolution_x"] = params.resolution_x
        if params.resolution_y is not None:
            settings["resolution_y"] = params.resolution_y
        if params.resolution_percentage is not None:
            settings["resolution_percentage"] = params.resolution_percentage
        if params.samples is not None:
            settings["samples"] = params.samples
        if params.use_denoising is not None:
            settings["use_denoising"] = params.use_denoising
        if params.file_format is not None:
            settings["file_format"] = params.file_format.value
        if params.output_path is not None:
            settings["output_path"] = params.output_path

        if not settings:
            return "No settings specified"

        result = await server.execute_command(
            "render", "settings",
            settings
        )

        if result.get("success"):
            return f"Render settings updated"
        else:
            return f"Failed to set render parameters: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_render_image",
        annotations={
            "title": "Render Still Image",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_render_image(params: RenderImageInput) -> str:
        """Render a still image.

        Args:
            params: Output path, frame number, camera

        Returns:
            Render result
        """
        result = await server.execute_command(
            "render", "image",
            {
                "output_path": params.output_path,
                "frame": params.frame,
                "camera": params.camera,
                "write_still": params.write_still
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            output = data.get("output_path", params.output_path or "default path")
            time = data.get("render_time", "unknown")
            return f"Render complete, output: {output}, time: {time}s"
        else:
            return f"Render failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_render_animation",
        annotations={
            "title": "Render Animation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_render_animation(params: RenderAnimationInput) -> str:
        """Render an animation sequence.

        Args:
            params: Output directory, frame range

        Returns:
            Render result
        """
        result = await server.execute_command(
            "render", "animation",
            {
                "output_path": params.output_path,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
                "frame_step": params.frame_step
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            frames = data.get("frames_rendered", "unknown")
            return f"Animation render complete, {frames} frames total, output to: {params.output_path}"
        else:
            return f"Animation render failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_render_preview",
        annotations={
            "title": "Render Preview",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_render_preview(params: RenderPreviewInput) -> str:
        """Quick render preview.

        Uses lower resolution and sample count for a fast preview.

        Args:
            params: Resolution percentage and sample count

        Returns:
            Preview result
        """
        result = await server.execute_command(
            "render", "preview",
            {
                "resolution_percentage": params.resolution_percentage,
                "samples": params.samples
            }
        )

        if result.get("success"):
            return f"Preview render complete"
        else:
            return f"Preview render failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_get_viewport_screenshot",
        annotations={
            "title": "Get Viewport Screenshot",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_get_viewport_screenshot(params: GetViewportScreenshotInput) -> str:
        """Get a screenshot of the current 3D viewport.

        Uses OpenGL rendering to capture the viewport for debugging and preview.

        Args:
            params: Output path, dimensions, view type

        Returns:
            Screenshot file path information
        """
        result = await server.execute_command(
            "render", "get_viewport_screenshot",
            {
                "output_path": params.output_path,
                "width": params.width,
                "height": params.height,
                "view_type": params.view_type.value if params.view_type else None,
                "return_base64": params.return_base64
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            lines = ["Viewport screenshot saved"]
            lines.append(f"- Path: {data.get('output_path', 'N/A')}")
            lines.append(f"- Dimensions: {data.get('width', 0)}x{data.get('height', 0)}")
            lines.append(f"- File size: {data.get('file_size', 0)} bytes")

            if params.return_base64 and data.get('base64'):
                lines.append(f"- Base64 data included in response")

            return "\n".join(lines)
        else:
            return f"Screenshot failed: {result.get('error', {}).get('message', 'Unknown error')}"
