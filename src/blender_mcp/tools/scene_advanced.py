"""
Scene enhancement tools

Provides environment presets, procedural generation, HDRI setup, and related functionality.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class EnvironmentPresetInput(BaseModel):
    """Environment preset input"""
    preset: str = Field(
        default="studio",
        description="Preset: studio, outdoor_day, outdoor_night, sunset, indoor, stadium, space"
    )
    intensity: float = Field(default=1.0, description="Environment light intensity", ge=0)


class ScatterObjectsInput(BaseModel):
    """Scatter objects input"""
    source_object: str = Field(..., description="Source object name")
    target_surface: str = Field(..., description="Target surface name")
    count: int = Field(default=100, description="Scatter count", ge=1, le=10000)
    seed: int = Field(default=0, description="Random seed")
    scale_min: float = Field(default=0.8, description="Minimum scale", ge=0.1)
    scale_max: float = Field(default=1.2, description="Maximum scale", ge=0.1)
    rotation_random: bool = Field(default=True, description="Random rotation")
    align_to_normal: bool = Field(default=True, description="Align to normal")


class ArrayGenerateInput(BaseModel):
    """Array generation input"""
    object_name: str = Field(..., description="Object name")
    count_x: int = Field(default=1, description="X direction count", ge=1)
    count_y: int = Field(default=1, description="Y direction count", ge=1)
    count_z: int = Field(default=1, description="Z direction count", ge=1)
    offset_x: float = Field(default=2.0, description="X direction offset")
    offset_y: float = Field(default=2.0, description="Y direction offset")
    offset_z: float = Field(default=2.0, description="Z direction offset")


class HDRISetupInput(BaseModel):
    """HDRI setup input"""
    hdri_path: Optional[str] = Field(default=None, description="HDRI file path")
    rotation: float = Field(default=0.0, description="Rotation angle (degrees)")
    strength: float = Field(default=1.0, description="Strength", ge=0)
    use_background: bool = Field(default=True, description="Use as background")


class GroundPlaneInput(BaseModel):
    """Ground plane input"""
    size: float = Field(default=100.0, description="Size", ge=1)
    material_preset: str = Field(
        default="concrete",
        description="Material preset: concrete, grass, wood, marble, sand, water"
    )
    location: Optional[List[float]] = Field(default=None, description="Location")


class SkySetupInput(BaseModel):
    """Sky setup input"""
    sky_type: str = Field(
        default="hosek_wilkie",
        description="Sky type: hosek_wilkie, preetham, nishita"
    )
    sun_elevation: float = Field(default=45.0, description="Sun elevation (degrees)", ge=-90, le=90)
    sun_rotation: float = Field(default=0.0, description="Sun azimuth (degrees)")
    turbidity: float = Field(default=2.0, description="Turbidity", ge=1, le=10)


class FogAddInput(BaseModel):
    """Add fog effect input"""
    density: float = Field(default=0.1, description="Density", ge=0)
    color: Optional[List[float]] = Field(default=None, description="Color RGB")
    height: float = Field(default=0.0, description="Fog height")
    falloff: float = Field(default=1.0, description="Falloff", ge=0)


# ==================== Tool Registration ====================

def register_scene_advanced_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register scene enhancement tools"""

    @mcp.tool(
        name="blender_scene_environment_preset",
        annotations={
            "title": "Apply Environment Preset",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_environment_preset(params: EnvironmentPresetInput) -> str:
        """Apply an environment preset.

        Available presets:
        - studio: Studio lighting
        - outdoor_day: Outdoor daytime
        - outdoor_night: Outdoor nighttime
        - sunset: Sunset
        - indoor: Indoor
        - stadium: Stadium
        - space: Space

        Args:
            params: Preset type, intensity

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "scene_advanced", "environment_preset",
            {
                "preset": params.preset,
                "intensity": params.intensity
            }
        )

        if result.get("success"):
            return f"Successfully applied {params.preset} environment preset"
        else:
            return f"Failed to apply: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_scatter",
        annotations={
            "title": "Scatter Objects",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_scatter(params: ScatterObjectsInput) -> str:
        """Scatter objects on a surface (grass, trees, rocks, etc.).

        Args:
            params: Source object, target surface, count, etc.

        Returns:
            Scatter result
        """
        result = await server.execute_command(
            "scene_advanced", "scatter",
            {
                "source_object": params.source_object,
                "target_surface": params.target_surface,
                "count": params.count,
                "seed": params.seed,
                "scale_min": params.scale_min,
                "scale_max": params.scale_max,
                "rotation_random": params.rotation_random,
                "align_to_normal": params.align_to_normal
            }
        )

        if result.get("success"):
            created = result.get("data", {}).get("instances_created", 0)
            return f"Successfully scattered {created} instances of '{params.source_object}'"
        else:
            return f"Scatter failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_array_generate",
        annotations={
            "title": "Array Generation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_array_generate(params: ArrayGenerateInput) -> str:
        """Generate an object array (buildings, seats, etc.).

        Args:
            params: Object, count and offset per direction

        Returns:
            Generation result
        """
        result = await server.execute_command(
            "scene_advanced", "array_generate",
            {
                "object_name": params.object_name,
                "count_x": params.count_x,
                "count_y": params.count_y,
                "count_z": params.count_z,
                "offset_x": params.offset_x,
                "offset_y": params.offset_y,
                "offset_z": params.offset_z
            }
        )

        if result.get("success"):
            total = params.count_x * params.count_y * params.count_z
            return f"Successfully generated array of {total} objects"
        else:
            return f"Generation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_ground_plane",
        annotations={
            "title": "Create Ground Plane",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_ground_plane(params: GroundPlaneInput) -> str:
        """Create a ground plane with material.

        Args:
            params: Size, material preset, location

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "scene_advanced", "ground_plane",
            {
                "size": params.size,
                "material_preset": params.material_preset,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            return f"Successfully created {params.material_preset} material ground plane ({params.size}m)"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_sky_setup",
        annotations={
            "title": "Setup Sky",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_sky_setup(params: SkySetupInput) -> str:
        """Set up procedural sky.

        Args:
            params: Sky type, sun position, etc.

        Returns:
            Setup result
        """
        result = await server.execute_command(
            "scene_advanced", "sky_setup",
            {
                "sky_type": params.sky_type,
                "sun_elevation": params.sun_elevation,
                "sun_rotation": params.sun_rotation,
                "turbidity": params.turbidity
            }
        )

        if result.get("success"):
            return f"Successfully set up {params.sky_type} sky"
        else:
            return f"Setup failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_fog_add",
        annotations={
            "title": "Add Fog Effect",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_fog_add(params: FogAddInput) -> str:
        """Add volumetric fog effect.

        Args:
            params: Density, color, height, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "scene_advanced", "fog_add",
            {
                "density": params.density,
                "color": params.color or [0.8, 0.9, 1.0],
                "height": params.height,
                "falloff": params.falloff
            }
        )

        if result.get("success"):
            return f"Successfully added fog effect (density: {params.density})"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"
