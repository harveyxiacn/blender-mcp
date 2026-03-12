"""
World/Environment Tools

Provides MCP tools for Blender world and environment settings.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class WorldCreateInput(BaseModel):
    """Create world"""
    name: str = Field("World", description="World name")
    use_nodes: bool = Field(True, description="Use nodes")


class WorldBackgroundInput(BaseModel):
    """Set background"""
    color: Optional[List[float]] = Field(None, description="Background color [R, G, B]")
    strength: float = Field(1.0, description="Strength")
    use_sky_texture: bool = Field(False, description="Use sky texture")


class WorldHDRIInput(BaseModel):
    """Set HDRI environment"""
    hdri_path: str = Field(..., description="HDRI file path")
    strength: float = Field(1.0, description="Strength")
    rotation: float = Field(0.0, description="Rotation angle (radians)")


class WorldSkyInput(BaseModel):
    """Set procedural sky"""
    sky_type: str = Field("NISHITA", description="Sky type: PREETHAM, HOSEK_WILKIE, NISHITA")
    sun_elevation: float = Field(0.785, description="Sun elevation (radians)")
    sun_rotation: float = Field(0.0, description="Sun rotation (radians)")
    air_density: float = Field(1.0, description="Air density")
    dust_density: float = Field(0.0, description="Dust density")
    ozone_density: float = Field(1.0, description="Ozone density")


class WorldFogInput(BaseModel):
    """Set volumetric fog"""
    use_fog: bool = Field(True, description="Enable fog")
    density: float = Field(0.01, description="Density")
    color: List[float] = Field([0.5, 0.6, 0.7], description="Color")
    anisotropy: float = Field(0.0, description="Anisotropy")


class WorldAmbientOcclusionInput(BaseModel):
    """Set ambient occlusion"""
    use_ao: bool = Field(True, description="Enable AO")
    distance: float = Field(1.0, description="Distance")
    factor: float = Field(1.0, description="Factor")


# ============ Tool Registration ============

def register_world_tools(mcp: FastMCP, server):
    """Register world/environment tools"""

    @mcp.tool()
    async def blender_world_create(
        name: str = "World",
        use_nodes: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new world

        Args:
            name: World name
            use_nodes: Whether to use nodes
        """
        params = WorldCreateInput(name=name, use_nodes=use_nodes)
        return await server.send_command("world", "create", params.model_dump())

    @mcp.tool()
    async def blender_world_background(
        color: Optional[List[float]] = None,
        strength: float = 1.0,
        use_sky_texture: bool = False
    ) -> Dict[str, Any]:
        """
        Set world background

        Args:
            color: Background color [R, G, B]
            strength: Strength
            use_sky_texture: Use sky texture
        """
        params = WorldBackgroundInput(
            color=color,
            strength=strength,
            use_sky_texture=use_sky_texture
        )
        return await server.send_command("world", "background", params.model_dump())

    @mcp.tool()
    async def blender_world_hdri(
        hdri_path: str,
        strength: float = 1.0,
        rotation: float = 0.0
    ) -> Dict[str, Any]:
        """
        Set HDRI environment map

        Args:
            hdri_path: HDRI file path
            strength: Environment light strength
            rotation: Rotation angle (radians)
        """
        params = WorldHDRIInput(
            hdri_path=hdri_path,
            strength=strength,
            rotation=rotation
        )
        return await server.send_command("world", "hdri", params.model_dump())

    @mcp.tool()
    async def blender_world_sky(
        sky_type: str = "NISHITA",
        sun_elevation: float = 0.785,
        sun_rotation: float = 0.0,
        air_density: float = 1.0,
        dust_density: float = 0.0,
        ozone_density: float = 1.0
    ) -> Dict[str, Any]:
        """
        Set procedural sky

        Args:
            sky_type: Sky type (PREETHAM, HOSEK_WILKIE, NISHITA)
            sun_elevation: Sun elevation (radians)
            sun_rotation: Sun rotation (radians)
            air_density: Air density
            dust_density: Dust density
            ozone_density: Ozone density
        """
        params = WorldSkyInput(
            sky_type=sky_type,
            sun_elevation=sun_elevation,
            sun_rotation=sun_rotation,
            air_density=air_density,
            dust_density=dust_density,
            ozone_density=ozone_density
        )
        return await server.send_command("world", "sky", params.model_dump())

    @mcp.tool()
    async def blender_world_fog(
        use_fog: bool = True,
        density: float = 0.01,
        color: List[float] = [0.5, 0.6, 0.7],
        anisotropy: float = 0.0
    ) -> Dict[str, Any]:
        """
        Set volumetric fog

        Args:
            use_fog: Enable fog
            density: Fog density
            color: Fog color [R, G, B]
            anisotropy: Anisotropy
        """
        params = WorldFogInput(
            use_fog=use_fog,
            density=density,
            color=color,
            anisotropy=anisotropy
        )
        return await server.send_command("world", "fog", params.model_dump())

    @mcp.tool()
    async def blender_world_ambient_occlusion(
        use_ao: bool = True,
        distance: float = 1.0,
        factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Set ambient occlusion

        Args:
            use_ao: Enable ambient occlusion
            distance: AO distance
            factor: AO factor
        """
        params = WorldAmbientOcclusionInput(
            use_ao=use_ao,
            distance=distance,
            factor=factor
        )
        return await server.send_command("world", "ambient_occlusion", params.model_dump())
