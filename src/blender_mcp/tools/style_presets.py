"""
Style Preset Tools

One-click configuration of complete rendering/material/modeling environments
from pixel art to AAA quality. Consolidates multiple tool calls into a single
high-level style setup tool.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ModelingStyle(str, Enum):
    """Modeling style"""

    PIXEL = "PIXEL"
    LOW_POLY = "LOW_POLY"
    STYLIZED = "STYLIZED"
    TOON = "TOON"
    HAND_PAINTED = "HAND_PAINTED"
    SEMI_REALISTIC = "SEMI_REALISTIC"
    PBR_REALISTIC = "PBR_REALISTIC"
    AAA = "AAA"


class OutlineMethod(str, Enum):
    """Outline method"""

    SOLIDIFY = "SOLIDIFY"
    FREESTYLE = "FREESTYLE"
    GREASE_PENCIL = "GREASE_PENCIL"


class StyleSetupInput(BaseModel):
    """Style setup input"""

    style: ModelingStyle = Field(
        ...,
        description="Modeling style: "
        "PIXEL (pixel/voxel, Flat Shading + pixel textures), "
        "LOW_POLY (low polygon, Flat Shading + solid/vertex color), "
        "STYLIZED (stylized, gradient + simple textures), "
        "TOON (cartoon/cel-shaded, Cel Shading + outlines), "
        "HAND_PAINTED (hand-painted, Diffuse-Only textures), "
        "SEMI_REALISTIC (semi-realistic, simplified PBR), "
        "PBR_REALISTIC (PBR realistic, full PBR pipeline), "
        "AAA (AAA/cinematic, high-poly sculpt + full texture set)",
    )
    apply_to_scene: bool = Field(
        default=True, description="Whether to apply to scene render settings"
    )
    apply_to_objects: list[str] | None = Field(
        default=None, description="Apply to specified objects (empty = scene only)"
    )


class OutlineSetupInput(BaseModel):
    """Outline effect setup input"""

    object_name: str = Field(..., description="Object name")
    method: OutlineMethod = Field(
        default=OutlineMethod.SOLIDIFY,
        description="Outline method: SOLIDIFY (solidify + flipped normals, most versatile), FREESTYLE (render lines, Cycles/EEVEE only), GREASE_PENCIL (grease pencil outline)",
    )
    thickness: float = Field(default=0.02, description="Outline thickness", gt=0)
    color: list[float] | None = Field(
        default=None, description="Outline color [R,G,B] (default: black)"
    )


class BakeWorkflowInput(BaseModel):
    """Bake workflow input"""

    high_poly: str = Field(..., description="High-poly object name")
    low_poly: str = Field(..., description="Low-poly object name")
    maps: list[str] = Field(
        default=["NORMAL", "AO"],
        description="Map types to bake: NORMAL, AO (ambient occlusion), CURVATURE, DIFFUSE, ROUGHNESS, COMBINED",
    )
    resolution: int = Field(default=2048, description="Texture resolution", ge=256, le=8192)
    cage_extrusion: float = Field(default=0.1, description="Cage extrusion distance", ge=0.001)
    output_dir: str | None = Field(
        default=None, description="Output directory (empty = same as .blend file)"
    )
    margin: int = Field(default=16, description="Edge margin in pixels", ge=0, le=64)


# ==================== Tool Registration ====================


def register_style_preset_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register style preset tools."""

    @mcp.tool(
        name="blender_style_setup",
        annotations={
            "title": "Style Environment Setup",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_style_setup(params: StyleSetupInput) -> str:
        """One-click modeling style environment configuration.

        Automatically configures the following based on the selected style (pixel to AAA):
        - Render engine and settings
        - Default material mode
        - Shading mode (Flat/Smooth)
        - Texture filtering (Nearest/Linear)
        - Recommended modeling parameters

        This is the first step before starting any style-specific modeling.

        Args:
            params: Style type and application scope

        Returns:
            Configuration results and modeling tips
        """
        result = await server.execute_command(
            "style_presets",
            "setup",
            {
                "style": params.style.value,
                "apply_to_scene": params.apply_to_scene,
                "apply_to_objects": params.apply_to_objects or [],
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            style_names = {
                "PIXEL": "Pixel/Voxel",
                "LOW_POLY": "Low Poly",
                "STYLIZED": "Stylized",
                "TOON": "Toon/Cel-Shaded",
                "HAND_PAINTED": "Hand-Painted",
                "SEMI_REALISTIC": "Semi-Realistic",
                "PBR_REALISTIC": "PBR Realistic",
                "AAA": "AAA/Cinematic",
            }
            tips = data.get("tips", "")
            settings = data.get("settings_applied", {})
            extra = data.get("extra_applied", [])
            lines = [
                f"# {style_names.get(params.style.value, params.style.value)} Style Environment Configured",
                "",
                "## Applied Settings",
            ]
            for k, v in settings.items():
                lines.append(f"- **{k}**: {v}")
            if extra:
                lines.append("")
                lines.append("## Additional Configuration")
                for item in extra:
                    lines.append(f"- {item}")
            if tips:
                lines.append("")
                lines.append("## Modeling Tips")
                lines.append(tips)
            return "\n".join(lines)
        else:
            return f"Style setup failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_outline_effect",
        annotations={
            "title": "Outline Effect",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_outline_effect(params: OutlineSetupInput) -> str:
        """Add outline effect to an object.

        Supports three methods:
        - SOLIDIFY: Solidify + flipped normals (most versatile, ideal for toon/stylized)
        - FREESTYLE: Blender render lines (visible only at render time)
        - GREASE_PENCIL: Grease pencil outline (visible in real-time)

        Args:
            params: Object name, method, thickness, color

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "style_presets",
            "outline",
            {
                "object_name": params.object_name,
                "method": params.method.value,
                "thickness": params.thickness,
                "color": params.color or [0, 0, 0],
            },
        )

        if result.get("success"):
            method_names = {
                "SOLIDIFY": "Solidify Flip",
                "FREESTYLE": "Freestyle",
                "GREASE_PENCIL": "Grease Pencil",
            }
            return f"Added {method_names.get(params.method.value, params.method.value)} outline effect, thickness: {params.thickness}"
        else:
            return (
                f"Failed to add outline: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_bake_maps",
        annotations={
            "title": "Bake Texture Maps",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_bake_maps(params: BakeWorkflowInput) -> str:
        """Bake texture maps from high-poly to low-poly (normal/AO/curvature etc.).

        A core step for AAA and PBR-realistic workflows. Automatically handles:
        - Selecting high-poly and low-poly objects
        - Creating bake image texture nodes
        - Setting bake parameters
        - Executing the bake
        - Saving textures

        Requires the Cycles render engine.

        Args:
            params: High-poly name, low-poly name, map types, resolution

        Returns:
            Bake results
        """
        result = await server.execute_command(
            "style_presets",
            "bake_maps",
            {
                "high_poly": params.high_poly,
                "low_poly": params.low_poly,
                "maps": params.maps,
                "resolution": params.resolution,
                "cage_extrusion": params.cage_extrusion,
                "output_dir": params.output_dir,
                "margin": params.margin,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            baked = data.get("baked_maps", [])
            lines = ["# Bake Complete", ""]
            for m in baked:
                lines.append(f"- **{m.get('type', '?')}**: {m.get('path', 'saved')}")
            return "\n".join(lines)
        else:
            return f"Bake failed: {result.get('error', {}).get('message', 'Unknown error')}"
