"""
Lighting Tools

Provides light creation and configuration functionality.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class LightType(str, Enum):
    """Light type"""

    POINT = "POINT"  # Point light
    SUN = "SUN"  # Sun light
    SPOT = "SPOT"  # Spot light
    AREA = "AREA"  # Area light


# ==================== Input Models ====================


class LightCreateInput(BaseModel):
    """Create light input"""

    type: LightType = Field(..., description="Light type")
    name: str | None = Field(default=None, description="Light name")
    location: list[float] | None = Field(default=None, description="Location [x, y, z]")
    rotation: list[float] | None = Field(default=None, description="Rotation [x, y, z]")
    color: list[float] | None = Field(default=None, description="RGB color")
    energy: float = Field(default=1000.0, description="Energy/intensity (watts)", ge=0)
    radius: float = Field(default=0.25, description="Light radius", ge=0)

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is not None and len(v) != 3:
            raise ValueError("Color must contain 3 components (RGB)")
        return v


class LightSetPropertiesInput(BaseModel):
    """Set light properties input"""

    light_name: str = Field(..., description="Light name")
    color: list[float] | None = Field(default=None, description="RGB color")
    energy: float | None = Field(default=None, description="Energy", ge=0)
    radius: float | None = Field(default=None, description="Radius", ge=0)
    spot_size: float | None = Field(default=None, description="Spot light angle (radians)", ge=0)
    spot_blend: float | None = Field(
        default=None, description="Spot light edge softness", ge=0, le=1
    )
    shadow_soft_size: float | None = Field(default=None, description="Shadow softness", ge=0)
    use_shadow: bool | None = Field(default=None, description="Whether to cast shadows")


class LightDeleteInput(BaseModel):
    """Delete light input"""

    light_name: str = Field(..., description="Light name")


class HDRISetupInput(BaseModel):
    """HDRI setup input"""

    hdri_path: str = Field(..., description="HDRI file path")
    strength: float = Field(default=1.0, description="Environment light strength", ge=0)
    rotation: float = Field(default=0.0, description="Rotation angle (radians)")


# ==================== Tool Registration ====================


def register_lighting_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register lighting tools"""

    @mcp.tool(
        name="blender_light_create",
        annotations={
            "title": "Create Light",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_light_create(params: LightCreateInput) -> str:
        """Create a light.

        Supports point light, sun light, spot light, and area light.

        Args:
            params: Light type and properties

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "lighting",
            "create",
            {
                "type": params.type.value,
                "name": params.name,
                "location": params.location or [0, 0, 5],
                "rotation": params.rotation or [0, 0, 0],
                "color": params.color or [1, 1, 1],
                "energy": params.energy,
                "radius": params.radius,
            },
        )

        if result.get("success"):
            name = result.get("data", {}).get("light_name", params.name or params.type.value)
            light_names = {
                "POINT": "Point Light",
                "SUN": "Sun Light",
                "SPOT": "Spot Light",
                "AREA": "Area Light",
            }
            return f"Successfully created {light_names.get(params.type.value, params.type.value)} '{name}', energy: {params.energy}W"
        else:
            return (
                f"Failed to create light: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_light_set_properties",
        annotations={
            "title": "Set Light Properties",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_light_set_properties(params: LightSetPropertiesInput) -> str:
        """Set light properties.

        Can set color, energy, shadow, and other properties.

        Args:
            params: Light name and properties to set

        Returns:
            Setting result
        """
        properties = {}
        if params.color is not None:
            properties["color"] = params.color
        if params.energy is not None:
            properties["energy"] = params.energy
        if params.radius is not None:
            properties["radius"] = params.radius
        if params.spot_size is not None:
            properties["spot_size"] = params.spot_size
        if params.spot_blend is not None:
            properties["spot_blend"] = params.spot_blend
        if params.shadow_soft_size is not None:
            properties["shadow_soft_size"] = params.shadow_soft_size
        if params.use_shadow is not None:
            properties["use_shadow"] = params.use_shadow

        if not properties:
            return "No properties specified"

        result = await server.execute_command(
            "lighting",
            "set_properties",
            {"light_name": params.light_name, "properties": properties},
        )

        if result.get("success"):
            return f"Light '{params.light_name}' properties updated"
        else:
            return f"Failed to set light properties: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_light_delete",
        annotations={
            "title": "Delete Light",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_light_delete(params: LightDeleteInput) -> str:
        """Delete a light.

        Args:
            params: Light name

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "lighting", "delete", {"light_name": params.light_name}
        )

        if result.get("success"):
            return f"Deleted light '{params.light_name}'"
        else:
            return (
                f"Failed to delete light: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_hdri_setup",
        annotations={
            "title": "Set Up HDRI Environment Light",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_hdri_setup(params: HDRISetupInput) -> str:
        """Set up HDRI environment lighting.

        Load an HDRI image as the scene's environment lighting.

        Args:
            params: HDRI file path and settings

        Returns:
            Setup result
        """
        result = await server.execute_command(
            "lighting",
            "hdri_setup",
            {
                "hdri_path": params.hdri_path,
                "strength": params.strength,
                "rotation": params.rotation,
            },
        )

        if result.get("success"):
            return f"HDRI environment lighting set up, strength: {params.strength}"
        else:
            return (
                f"Failed to set up HDRI: {result.get('error', {}).get('message', 'Unknown error')}"
            )
