"""
Blender MCP - High-Level Compound Tools

One-call workflow tools that chain multiple operations for maximum user satisfaction.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

from mcp.server.fastmcp import FastMCP


class LightingStyle(str, Enum):
    """Lighting style presets"""

    STUDIO = "studio"
    DRAMATIC = "dramatic"
    SOFT = "soft"
    OUTDOOR = "outdoor"


class SceneStyle(str, Enum):
    """Scene setup style presets"""

    STUDIO = "studio"
    OUTDOOR = "outdoor"
    DRAMATIC = "dramatic"
    MINIMAL = "minimal"


class RotationAxis(str, Enum):
    """Rotation axis"""

    X = "X"
    Y = "Y"
    Z = "Z"


class QuickProductShotInput(BaseModel):
    """Product shot input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    target_object: str | None = Field(
        default=None, description="Object name to focus on (uses active object if omitted)"
    )
    style: LightingStyle = Field(default=LightingStyle.STUDIO, description="Lighting style")
    background_color: list[float] | None = Field(
        default=None, description="Background RGB values [0-1, 0-1, 0-1]"
    )
    render_width: int = Field(default=1920, description="Render width in pixels", ge=320, le=7680)
    render_height: int = Field(default=1080, description="Render height in pixels", ge=240, le=4320)

    @field_validator("background_color")
    @classmethod
    def validate_color(cls, v: list[float] | None) -> list[float] | None:
        if v is not None:
            if len(v) != 3:
                raise ValueError("Color must have 3 components [R, G, B]")
            for c in v:
                if not 0.0 <= c <= 1.0:
                    raise ValueError("Color components must be between 0.0 and 1.0")
        return v


class QuickTurntableInput(BaseModel):
    """Turntable animation input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    target_object: str | None = Field(
        default=None, description="Object to animate (uses active object if omitted)"
    )
    frames: int = Field(
        default=120, description="Total frames for full 360 rotation", ge=24, le=1000
    )
    axis: RotationAxis = Field(default=RotationAxis.Z, description="Rotation axis")


class QuickSceneSetupInput(BaseModel):
    """Scene setup input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    style: SceneStyle = Field(default=SceneStyle.STUDIO, description="Scene style preset")
    clear_scene: bool = Field(default=False, description="Remove existing objects first")


def register_quick_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    """Register quick compound tools"""

    @mcp.tool(
        name="blender_quick_product_shot",
        annotations={
            "title": "Quick Product Shot Setup",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_quick_product_shot(params: QuickProductShotInput) -> str:
        """Set up a complete product visualization in one call: 3-point lighting,
        camera aimed at target, backdrop plane, and render settings.

        Example: Set up a studio product shot for 'MyModel' with dramatic lighting.
        """
        result = await server.execute_command(
            "quick",
            "product_shot",
            {
                "target_object": params.target_object,
                "style": params.style.value,
                "background_color": params.background_color,
                "render_width": params.render_width,
                "render_height": params.render_height,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            created = data.get("created_objects", [])
            target = data.get("target", "active object")
            return (
                f"Product shot setup complete for '{target}'.\n"
                f"Style: {params.style.value}\n"
                f"Created: {', '.join(created)}\n"
                f"Render: {params.render_width}x{params.render_height}\n"
                f"Scene is ready to render."
            )
        else:
            error = result.get("error", {})
            suggestion = error.get("suggestion", "")
            msg = f"Product shot setup failed: {error.get('message', 'Unknown error')}"
            if suggestion:
                msg += f"\nSuggestion: {suggestion}"
            return msg

    @mcp.tool(
        name="blender_quick_turntable",
        annotations={
            "title": "Quick Turntable Animation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_quick_turntable(params: QuickTurntableInput) -> str:
        """Create a turntable (360 rotation) animation for an object in one call.

        Example: Create a 120-frame turntable around the Z axis for 'Sculpture'.
        """
        result = await server.execute_command(
            "quick",
            "turntable",
            {
                "target_object": params.target_object,
                "frames": params.frames,
                "axis": params.axis.value,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            target = data.get("target", "active object")
            pivot = data.get("pivot_empty", "")
            return (
                f"Turntable animation created for '{target}'.\n"
                f"Frames: 1-{params.frames} (full 360 on {params.axis.value} axis)\n"
                f"Pivot empty: {pivot}\n"
                f"Press Play or render animation to see the result."
            )
        else:
            error = result.get("error", {})
            suggestion = error.get("suggestion", "")
            msg = f"Turntable setup failed: {error.get('message', 'Unknown error')}"
            if suggestion:
                msg += f"\nSuggestion: {suggestion}"
            return msg

    @mcp.tool(
        name="blender_quick_scene_setup",
        annotations={
            "title": "Quick Scene Setup",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_quick_scene_setup(params: QuickSceneSetupInput) -> str:
        """One-click scene setup with lighting and camera for a given style.
        Styles: studio (neutral grey, 3-point), outdoor (sun + sky), dramatic (high contrast),
        minimal (single key light).

        Example: Set up a studio scene with default lighting for general modeling work.
        """
        result = await server.execute_command(
            "quick",
            "scene_setup",
            {
                "style": params.style.value,
                "clear_scene": params.clear_scene,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            created = data.get("created_objects", [])
            return (
                f"Scene setup complete ({params.style.value} style).\n"
                f"Created: {', '.join(created)}\n"
                f"Scene is ready for modeling."
            )
        else:
            error = result.get("error", {})
            return f"Scene setup failed: {error.get('message', 'Unknown error')}"
