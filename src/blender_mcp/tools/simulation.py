"""
Advanced simulation tools

Provides MCP tools for fluid, smoke, ocean, and other advanced simulations.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class FluidDomainInput(BaseModel):
    """Fluid domain settings"""

    object_name: str = Field(..., description="Object name")
    domain_type: str = Field("LIQUID", description="Domain type: LIQUID, GAS")
    resolution: int = Field(64, description="Resolution")
    use_adaptive_domain: bool = Field(False, description="Adaptive domain")


class FluidFlowInput(BaseModel):
    """Fluid inflow/outflow"""

    object_name: str = Field(..., description="Object name")
    flow_type: str = Field("INFLOW", description="Type: INFLOW, OUTFLOW, GEOMETRY")
    flow_behavior: str = Field("GEOMETRY", description="Behavior: INFLOW, OUTFLOW, GEOMETRY")
    use_initial_velocity: bool = Field(False, description="Use initial velocity")
    velocity: list[float] = Field([0, 0, 0], description="Velocity [x, y, z]")


class FluidEffectorInput(BaseModel):
    """Fluid effector"""

    object_name: str = Field(..., description="Object name")
    effector_type: str = Field("COLLISION", description="Type: COLLISION, GUIDE")


class SmokeDomainInput(BaseModel):
    """Smoke/fire domain"""

    object_name: str = Field(..., description="Object name")
    smoke_type: str = Field("SMOKE", description="Type: SMOKE, FIRE, BOTH")
    resolution: int = Field(32, description="Resolution")
    use_high_resolution: bool = Field(False, description="High resolution")


class SmokeFlowInput(BaseModel):
    """Smoke flow emitter"""

    object_name: str = Field(..., description="Object name")
    flow_type: str = Field("SMOKE", description="Type: SMOKE, FIRE, BOTH")
    temperature: float = Field(1.0, description="Temperature")
    density: float = Field(1.0, description="Density")
    smoke_color: list[float] = Field([1, 1, 1], description="Smoke color")


class OceanModifierInput(BaseModel):
    """Ocean modifier"""

    object_name: str = Field(..., description="Object name")
    resolution: int = Field(7, description="Resolution (2^n)")
    spatial_size: int = Field(50, description="Spatial size")
    wave_scale: float = Field(1.0, description="Wave scale")
    choppiness: float = Field(1.0, description="Choppiness")
    wind_velocity: float = Field(30.0, description="Wind velocity")
    use_foam: bool = Field(False, description="Use foam")


class DynamicPaintCanvasInput(BaseModel):
    """Dynamic paint canvas"""

    object_name: str = Field(..., description="Object name")
    surface_type: str = Field("PAINT", description="Type: PAINT, DISPLACE, WAVE, WEIGHT")
    use_dissolve: bool = Field(False, description="Use dissolve")
    dissolve_speed: int = Field(80, description="Dissolve speed")


class DynamicPaintBrushInput(BaseModel):
    """Dynamic paint brush"""

    object_name: str = Field(..., description="Object name")
    paint_color: list[float] = Field([1, 0, 0], description="Paint color")
    paint_alpha: float = Field(1.0, description="Alpha")


class SimulationBakeInput(BaseModel):
    """Bake simulation"""

    object_name: str = Field(..., description="Domain object name")
    frame_start: int = Field(1, description="Start frame")
    frame_end: int = Field(250, description="End frame")


# ============ Tool Registration ============


def register_simulation_tools(mcp: FastMCP, server) -> None:
    """Register advanced simulation tools"""

    @mcp.tool()
    async def blender_sim_fluid_domain(
        object_name: str,
        domain_type: str = "LIQUID",
        resolution: int = 64,
        use_adaptive_domain: bool = False,
    ) -> dict[str, Any]:
        """
        Set up fluid domain

        Args:
            object_name: Domain object name (usually a bounding box)
            domain_type: Domain type (LIQUID or GAS)
            resolution: Simulation resolution
            use_adaptive_domain: Whether to use adaptive domain
        """
        params = FluidDomainInput(
            object_name=object_name,
            domain_type=domain_type,
            resolution=resolution,
            use_adaptive_domain=use_adaptive_domain,
        )
        return await server.send_command("simulation", "fluid_domain", params.model_dump())

    @mcp.tool()
    async def blender_sim_fluid_flow(
        object_name: str,
        flow_type: str = "INFLOW",
        flow_behavior: str = "GEOMETRY",
        use_initial_velocity: bool = False,
        velocity: list[float] = None,
    ) -> dict[str, Any]:
        """
        Set up fluid inflow/outflow

        Args:
            object_name: Fluid source object name
            flow_type: Flow type (INFLOW, OUTFLOW, GEOMETRY)
            flow_behavior: Flow behavior
            use_initial_velocity: Use initial velocity
            velocity: Velocity vector [x, y, z]
        """
        if velocity is None:
            velocity = [0, 0, 0]
        params = FluidFlowInput(
            object_name=object_name,
            flow_type=flow_type,
            flow_behavior=flow_behavior,
            use_initial_velocity=use_initial_velocity,
            velocity=velocity,
        )
        return await server.send_command("simulation", "fluid_flow", params.model_dump())

    @mcp.tool()
    async def blender_sim_fluid_effector(
        object_name: str, effector_type: str = "COLLISION"
    ) -> dict[str, Any]:
        """
        Set up fluid effector (collision body)

        Args:
            object_name: Effector object name
            effector_type: Effector type (COLLISION, GUIDE)
        """
        params = FluidEffectorInput(object_name=object_name, effector_type=effector_type)
        return await server.send_command("simulation", "fluid_effector", params.model_dump())

    @mcp.tool()
    async def blender_sim_smoke_domain(
        object_name: str,
        smoke_type: str = "SMOKE",
        resolution: int = 32,
        use_high_resolution: bool = False,
    ) -> dict[str, Any]:
        """
        Set up smoke/fire domain

        Args:
            object_name: Domain object name
            smoke_type: Type (SMOKE, FIRE, BOTH)
            resolution: Base resolution
            use_high_resolution: Use high resolution
        """
        params = SmokeDomainInput(
            object_name=object_name,
            smoke_type=smoke_type,
            resolution=resolution,
            use_high_resolution=use_high_resolution,
        )
        return await server.send_command("simulation", "smoke_domain", params.model_dump())

    @mcp.tool()
    async def blender_sim_smoke_flow(
        object_name: str,
        flow_type: str = "SMOKE",
        temperature: float = 1.0,
        density: float = 1.0,
        smoke_color: list[float] = None,
    ) -> dict[str, Any]:
        """
        Set up smoke/fire emitter

        Args:
            object_name: Emitter object name
            flow_type: Flow type (SMOKE, FIRE, BOTH)
            temperature: Temperature
            density: Density
            smoke_color: Smoke color [R, G, B]
        """
        if smoke_color is None:
            smoke_color = [1, 1, 1]
        params = SmokeFlowInput(
            object_name=object_name,
            flow_type=flow_type,
            temperature=temperature,
            density=density,
            smoke_color=smoke_color,
        )
        return await server.send_command("simulation", "smoke_flow", params.model_dump())

    @mcp.tool()
    async def blender_sim_ocean(
        object_name: str,
        resolution: int = 7,
        spatial_size: int = 50,
        wave_scale: float = 1.0,
        choppiness: float = 1.0,
        wind_velocity: float = 30.0,
        use_foam: bool = False,
    ) -> dict[str, Any]:
        """
        Add ocean modifier

        Args:
            object_name: Object name (usually a plane)
            resolution: Resolution (2^n)
            spatial_size: Spatial size
            wave_scale: Wave scale
            choppiness: Choppiness
            wind_velocity: Wind velocity
            use_foam: Whether to generate foam
        """
        params = OceanModifierInput(
            object_name=object_name,
            resolution=resolution,
            spatial_size=spatial_size,
            wave_scale=wave_scale,
            choppiness=choppiness,
            wind_velocity=wind_velocity,
            use_foam=use_foam,
        )
        return await server.send_command("simulation", "ocean", params.model_dump())

    @mcp.tool()
    async def blender_sim_dynamic_paint_canvas(
        object_name: str,
        surface_type: str = "PAINT",
        use_dissolve: bool = False,
        dissolve_speed: int = 80,
    ) -> dict[str, Any]:
        """
        Set up dynamic paint canvas

        Args:
            object_name: Canvas object name
            surface_type: Surface type (PAINT, DISPLACE, WAVE, WEIGHT)
            use_dissolve: Use dissolve effect
            dissolve_speed: Dissolve speed
        """
        params = DynamicPaintCanvasInput(
            object_name=object_name,
            surface_type=surface_type,
            use_dissolve=use_dissolve,
            dissolve_speed=dissolve_speed,
        )
        return await server.send_command("simulation", "dynamic_paint_canvas", params.model_dump())

    @mcp.tool()
    async def blender_sim_dynamic_paint_brush(
        object_name: str, paint_color: list[float] = None, paint_alpha: float = 1.0
    ) -> dict[str, Any]:
        """
        Set up dynamic paint brush

        Args:
            object_name: Brush object name
            paint_color: Paint color [R, G, B]
            paint_alpha: Alpha
        """
        if paint_color is None:
            paint_color = [1, 0, 0]
        params = DynamicPaintBrushInput(
            object_name=object_name, paint_color=paint_color, paint_alpha=paint_alpha
        )
        return await server.send_command("simulation", "dynamic_paint_brush", params.model_dump())

    @mcp.tool()
    async def blender_sim_bake(
        object_name: str, frame_start: int = 1, frame_end: int = 250
    ) -> dict[str, Any]:
        """
        Bake simulation

        Args:
            object_name: Domain object name
            frame_start: Start frame
            frame_end: End frame
        """
        params = SimulationBakeInput(
            object_name=object_name, frame_start=frame_start, frame_end=frame_end
        )
        return await server.send_command("simulation", "bake", params.model_dump())
