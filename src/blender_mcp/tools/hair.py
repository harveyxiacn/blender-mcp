"""
Hair System Tools

Provides MCP tools for hair creation and editing.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class HairSystemInput(BaseModel):
    """Add hair system"""

    object_name: str = Field(..., description="Object name")
    name: str = Field("Hair", description="Hair system name")
    hair_length: float = Field(0.1, description="Hair length")
    hair_count: int = Field(1000, description="Hair count")
    segments: int = Field(5, description="Hair segments")


class HairSettingsInput(BaseModel):
    """Hair settings"""

    object_name: str = Field(..., description="Object name")
    system_name: str | None = Field(None, description="Hair system name")
    hair_length: float | None = Field(None, description="Hair length")
    root_radius: float | None = Field(None, description="Root radius")
    tip_radius: float | None = Field(None, description="Tip radius")
    random_length: float | None = Field(None, description="Random length")
    random_rotation: float | None = Field(None, description="Random rotation")


class HairDynamicsInput(BaseModel):
    """Hair dynamics"""

    object_name: str = Field(..., description="Object name")
    enable: bool = Field(True, description="Enable dynamics")
    stiffness: float = Field(0.5, description="Stiffness")
    damping: float = Field(0.1, description="Damping")
    gravity: float = Field(1.0, description="Gravity influence")


class HairMaterialInput(BaseModel):
    """Hair material"""

    object_name: str = Field(..., description="Object name")
    color: list[float] = Field([0.1, 0.05, 0.02, 1.0], description="Color")
    roughness: float = Field(0.4, description="Roughness")
    use_hair_bsdf: bool = Field(True, description="Use Hair BSDF")


class HairChildrenInput(BaseModel):
    """Hair children"""

    object_name: str = Field(..., description="Object name")
    child_type: str = Field("INTERPOLATED", description="Type: NONE, SIMPLE, INTERPOLATED")
    child_count: int = Field(10, description="Child count")
    clump: float = Field(0.0, description="Clumping")
    roughness: float = Field(0.0, description="Roughness")


class HairGroomInput(BaseModel):
    """Hair grooming"""

    object_name: str = Field(..., description="Object name")
    action: str = Field("COMB", description="Action: COMB, CUT, LENGTH, PUFF, SMOOTH")
    strength: float = Field(0.5, description="Strength")


# ============ Tool Registration ============


def register_hair_tools(mcp: FastMCP, server) -> None:
    """Register hair tools"""

    @mcp.tool()
    async def blender_hair_add(
        object_name: str,
        name: str = "Hair",
        hair_length: float = 0.1,
        hair_count: int = 1000,
        segments: int = 5,
    ) -> dict[str, Any]:
        """
        Add a hair system

        Args:
            object_name: Target object name
            name: Hair system name
            hair_length: Hair length
            hair_count: Hair count
            segments: Segments per hair strand
        """
        params = HairSystemInput(
            object_name=object_name,
            name=name,
            hair_length=hair_length,
            hair_count=hair_count,
            segments=segments,
        )
        return await server.send_command("hair", "add", params.model_dump())

    @mcp.tool()
    async def blender_hair_settings(
        object_name: str,
        system_name: str | None = None,
        hair_length: float | None = None,
        root_radius: float | None = None,
        tip_radius: float | None = None,
        random_length: float | None = None,
        random_rotation: float | None = None,
    ) -> dict[str, Any]:
        """
        Set hair properties

        Args:
            object_name: Object name
            system_name: Hair system name
            hair_length: Hair length
            root_radius: Root radius
            tip_radius: Tip radius
            random_length: Length randomness
            random_rotation: Rotation randomness
        """
        params = HairSettingsInput(
            object_name=object_name,
            system_name=system_name,
            hair_length=hair_length,
            root_radius=root_radius,
            tip_radius=tip_radius,
            random_length=random_length,
            random_rotation=random_rotation,
        )
        return await server.send_command("hair", "settings", params.model_dump())

    @mcp.tool()
    async def blender_hair_dynamics(
        object_name: str,
        enable: bool = True,
        stiffness: float = 0.5,
        damping: float = 0.1,
        gravity: float = 1.0,
    ) -> dict[str, Any]:
        """
        Set hair dynamics

        Args:
            object_name: Object name
            enable: Enable dynamics
            stiffness: Stiffness (0-1)
            damping: Damping (0-1)
            gravity: Gravity influence
        """
        params = HairDynamicsInput(
            object_name=object_name,
            enable=enable,
            stiffness=stiffness,
            damping=damping,
            gravity=gravity,
        )
        return await server.send_command("hair", "dynamics", params.model_dump())

    @mcp.tool()
    async def blender_hair_material(
        object_name: str,
        color: list[float] = None,
        roughness: float = 0.4,
        use_hair_bsdf: bool = True,
    ) -> dict[str, Any]:
        """
        Set hair material

        Args:
            object_name: Object name
            color: Hair color [R, G, B, A]
            roughness: Roughness
            use_hair_bsdf: Use Hair BSDF shader
        """
        if color is None:
            color = [0.1, 0.05, 0.02, 1.0]
        params = HairMaterialInput(
            object_name=object_name, color=color, roughness=roughness, use_hair_bsdf=use_hair_bsdf
        )
        return await server.send_command("hair", "material", params.model_dump())

    @mcp.tool()
    async def blender_hair_children(
        object_name: str,
        child_type: str = "INTERPOLATED",
        child_count: int = 10,
        clump: float = 0.0,
        roughness: float = 0.0,
    ) -> dict[str, Any]:
        """
        Set hair children

        Args:
            object_name: Object name
            child_type: Child type (NONE, SIMPLE, INTERPOLATED)
            child_count: Child count
            clump: Clumping
            roughness: Child roughness
        """
        params = HairChildrenInput(
            object_name=object_name,
            child_type=child_type,
            child_count=child_count,
            clump=clump,
            roughness=roughness,
        )
        return await server.send_command("hair", "children", params.model_dump())

    @mcp.tool()
    async def blender_hair_groom(
        object_name: str, action: str = "COMB", strength: float = 0.5
    ) -> dict[str, Any]:
        """
        Hair grooming operations

        Args:
            object_name: Object name
            action: Grooming action (COMB, CUT, LENGTH, PUFF, SMOOTH)
            strength: Action strength
        """
        params = HairGroomInput(object_name=object_name, action=action, strength=strength)
        return await server.send_command("hair", "groom", params.model_dump())
