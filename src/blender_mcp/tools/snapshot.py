"""
Blender MCP - Viewport Snapshot Tools

Capture viewport screenshots and render previews for multimodal AI analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

from mcp.server.fastmcp import FastMCP


class SnapshotViewportInput(BaseModel):
    """Viewport snapshot input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    width: int = Field(default=800, description="Image width in pixels", ge=64, le=3840)
    height: int = Field(default=600, description="Image height in pixels", ge=64, le=2160)
    output_path: str | None = Field(
        default=None, description="Output file path (auto-generated if omitted)"
    )


class SnapshotRenderPreviewInput(BaseModel):
    """Render preview input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    width: int = Field(default=512, description="Preview render width", ge=64, le=1920)
    samples: int = Field(default=16, description="Render samples (lower=faster)", ge=1, le=128)
    output_path: str | None = Field(
        default=None, description="Output file path (auto-generated if omitted)"
    )


def register_snapshot_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    """Register snapshot tools"""

    @mcp.tool(
        name="blender_snapshot_viewport",
        annotations={
            "title": "Capture Viewport Snapshot",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_snapshot_viewport(params: SnapshotViewportInput) -> str:
        """Capture the 3D viewport as a PNG image. Returns the file path for multimodal AI analysis.

        Example: Capture an 800x600 screenshot of the current viewport to see the scene layout.
        """
        result = await server.execute_command(
            "snapshot",
            "viewport",
            {
                "width": params.width,
                "height": params.height,
                "output_path": params.output_path,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            path = data.get("path", "unknown")
            w = data.get("width", params.width)
            h = data.get("height", params.height)
            return (
                f"Viewport snapshot saved: {path}\n"
                f"Resolution: {w}x{h}\n"
                f"Use this image path with a multimodal AI to analyze the scene visually."
            )
        else:
            error = result.get("error", {})
            return f"Snapshot failed: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_snapshot_render_preview",
        annotations={
            "title": "Quick Render Preview",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_snapshot_render_preview(params: SnapshotRenderPreviewInput) -> str:
        """Quick render at reduced resolution for preview. Returns the file path.

        Example: Render a 512px wide preview with 16 samples to check lighting and materials.
        """
        result = await server.execute_command(
            "snapshot",
            "render_preview",
            {
                "width": params.width,
                "samples": params.samples,
                "output_path": params.output_path,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            path = data.get("path", "unknown")
            w = data.get("width", params.width)
            h = data.get("height", "auto")
            return (
                f"Render preview saved: {path}\n"
                f"Resolution: {w}x{h}, Samples: {params.samples}\n"
                f"Use this image path to analyze materials, lighting, and composition."
            )
        else:
            error = result.get("error", {})
            return f"Render preview failed: {error.get('message', 'Unknown error')}"
