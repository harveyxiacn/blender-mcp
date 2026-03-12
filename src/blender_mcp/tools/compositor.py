"""
Compositor Tools

Provides post-processing compositing, color correction, effects, and more.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class CompositorEnableInput(BaseModel):
    """Enable compositor input"""
    enable: bool = Field(default=True, description="Whether to enable")
    use_backdrop: bool = Field(default=True, description="Use backdrop preview")


class CompositorPresetInput(BaseModel):
    """Compositor preset input"""
    preset: str = Field(
        default="color_correction",
        description="Preset: color_correction, bloom, vignette, blur, sharpen, film_grain, chromatic_aberration"
    )
    intensity: float = Field(default=1.0, description="Effect intensity", ge=0, le=2)


class CompositorColorBalanceInput(BaseModel):
    """Color balance input"""
    shadows: Optional[List[float]] = Field(default=None, description="Shadow color RGB")
    midtones: Optional[List[float]] = Field(default=None, description="Midtone color RGB")
    highlights: Optional[List[float]] = Field(default=None, description="Highlight color RGB")


class CompositorBlurInput(BaseModel):
    """Blur input"""
    blur_type: str = Field(default="FAST_GAUSS", description="Type: FLAT, TENT, QUAD, CUBIC, GAUSS, FAST_GAUSS")
    size_x: float = Field(default=10.0, description="X direction size", ge=0)
    size_y: float = Field(default=10.0, description="Y direction size", ge=0)


class RenderLayerInput(BaseModel):
    """Render layer input"""
    layer_name: str = Field(default="ViewLayer", description="View layer name")
    use_pass_combined: bool = Field(default=True, description="Combined pass")
    use_pass_z: bool = Field(default=False, description="Z depth pass")
    use_pass_normal: bool = Field(default=False, description="Normal pass")
    use_pass_ao: bool = Field(default=False, description="Ambient occlusion pass")


# ==================== Tool Registration ====================

def register_compositor_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register compositor tools"""

    @mcp.tool(
        name="blender_compositor_enable",
        annotations={
            "title": "Enable Compositor",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_compositor_enable(params: CompositorEnableInput) -> str:
        """Enable or disable the compositor.

        Args:
            params: Whether to enable, whether to use backdrop

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "compositor", "enable",
            {
                "enable": params.enable,
                "use_backdrop": params.use_backdrop
            }
        )

        if result.get("success"):
            status = "enabled" if params.enable else "disabled"
            return f"Successfully {status} compositor"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_compositor_preset",
        annotations={
            "title": "Apply Compositor Preset",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_compositor_preset(params: CompositorPresetInput) -> str:
        """Apply a compositor effect preset.

        Available presets:
        - color_correction: Color correction
        - bloom: Bloom effect
        - vignette: Vignette
        - blur: Blur
        - sharpen: Sharpen
        - film_grain: Film grain
        - chromatic_aberration: Chromatic aberration

        Args:
            params: Preset type, intensity

        Returns:
            Application result
        """
        result = await server.execute_command(
            "compositor", "preset",
            {
                "preset": params.preset,
                "intensity": params.intensity
            }
        )

        if result.get("success"):
            return f"Successfully applied {params.preset} effect"
        else:
            return f"Application failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_compositor_color_balance",
        annotations={
            "title": "Color Balance",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_compositor_color_balance(params: CompositorColorBalanceInput) -> str:
        """Adjust color balance.

        Args:
            params: Shadow, midtone, highlight colors

        Returns:
            Adjustment result
        """
        result = await server.execute_command(
            "compositor", "color_balance",
            {
                "shadows": params.shadows,
                "midtones": params.midtones,
                "highlights": params.highlights
            }
        )

        if result.get("success"):
            return f"Successfully adjusted color balance"
        else:
            return f"Adjustment failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_compositor_blur",
        annotations={
            "title": "Add Blur",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_compositor_blur(params: CompositorBlurInput) -> str:
        """Add a blur effect.

        Args:
            params: Blur type, size

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "compositor", "blur",
            {
                "blur_type": params.blur_type,
                "size_x": params.size_x,
                "size_y": params.size_y
            }
        )

        if result.get("success"):
            return f"Successfully added blur effect"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_render_layer_setup",
        annotations={
            "title": "Setup Render Layer",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_render_layer_setup(params: RenderLayerInput) -> str:
        """Set up render layer passes.

        Args:
            params: Various pass toggles

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "compositor", "render_layer",
            {
                "layer_name": params.layer_name,
                "use_pass_combined": params.use_pass_combined,
                "use_pass_z": params.use_pass_z,
                "use_pass_normal": params.use_pass_normal,
                "use_pass_ao": params.use_pass_ao
            }
        )

        if result.get("success"):
            return f"Successfully set up render layer '{params.layer_name}'"
        else:
            return f"Setup failed: {result.get('error', {}).get('message', 'unknown error')}"
