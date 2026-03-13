"""
Physics simulation tools

Provides physics simulation features including cloth, rigid body, particle systems, etc.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class ClothAddInput(BaseModel):
    """Add cloth simulation input"""

    object_name: str = Field(..., description="Mesh object name")
    preset: str = Field(
        default="cotton", description="Cloth preset: cotton, silk, leather, denim, rubber"
    )
    pin_group: str | None = Field(default=None, description="Pin vertex group")
    collision_quality: int = Field(default=2, description="Collision quality", ge=1, le=10)


class RigidBodyAddInput(BaseModel):
    """Add rigid body input"""

    object_name: str = Field(..., description="Object name")
    body_type: str = Field(default="ACTIVE", description="Type: ACTIVE, PASSIVE")
    shape: str = Field(
        default="CONVEX_HULL",
        description="Collision shape: BOX, SPHERE, CAPSULE, CYLINDER, CONE, CONVEX_HULL, MESH",
    )
    mass: float = Field(default=1.0, description="Mass (kg)", ge=0)
    friction: float = Field(default=0.5, description="Friction", ge=0, le=1)
    bounciness: float = Field(default=0.0, description="Bounciness", ge=0, le=1)


class CollisionAddInput(BaseModel):
    """Add collision body input"""

    object_name: str = Field(..., description="Object name")
    damping: float = Field(default=0.0, description="Damping", ge=0, le=1)
    thickness: float = Field(default=0.02, description="Thickness", ge=0)
    friction: float = Field(default=0.0, description="Friction", ge=0, le=1)


class ParticleSystemInput(BaseModel):
    """Particle system input"""

    object_name: str = Field(..., description="Emitter object name")
    particle_type: str = Field(default="EMITTER", description="Type: EMITTER, HAIR")
    count: int = Field(default=1000, description="Particle count", ge=1, le=100000)
    lifetime: float = Field(default=50.0, description="Lifetime (frames)", ge=1)
    emit_from: str = Field(default="FACE", description="Emit from: VERT, FACE, VOLUME")
    velocity_normal: float = Field(default=1.0, description="Normal velocity")


class ForceFieldInput(BaseModel):
    """Force field input"""

    force_type: str = Field(
        default="WIND",
        description="Force field type: WIND, VORTEX, TURBULENCE, DRAG, FORCE, MAGNETIC",
    )
    location: list[float] | None = Field(default=None, description="Location")
    strength: float = Field(default=1.0, description="Strength")
    flow: float = Field(default=0.0, description="Flow")


class SoftBodyAddInput(BaseModel):
    """Add soft body input"""

    object_name: str = Field(..., description="Object name")
    mass: float = Field(default=1.0, description="Mass", ge=0)
    friction: float = Field(default=0.5, description="Friction", ge=0, le=1)
    goal_strength: float = Field(default=0.7, description="Goal strength", ge=0, le=1)


# ==================== Tool Registration ====================


def register_physics_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register physics simulation tools"""

    @mcp.tool(
        name="blender_physics_cloth_add",
        annotations={
            "title": "Add Cloth Simulation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_cloth_add(params: ClothAddInput) -> str:
        """Add cloth simulation to a mesh.

        Args:
            params: Object name, cloth preset, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "cloth_add",
            {
                "object_name": params.object_name,
                "preset": params.preset,
                "pin_group": params.pin_group,
                "collision_quality": params.collision_quality,
            },
        )

        if result.get("success"):
            return f"Successfully added {params.preset} cloth simulation to '{params.object_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_physics_rigid_body_add",
        annotations={
            "title": "Add Rigid Body",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_rigid_body_add(params: RigidBodyAddInput) -> str:
        """Add rigid body physics to an object.

        Args:
            params: Object name, type, mass, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "rigid_body_add",
            {
                "object_name": params.object_name,
                "body_type": params.body_type,
                "shape": params.shape,
                "mass": params.mass,
                "friction": params.friction,
                "bounciness": params.bounciness,
            },
        )

        if result.get("success"):
            return f"Successfully added {params.body_type} rigid body to '{params.object_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_physics_collision_add",
        annotations={
            "title": "Add Collision Body",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_collision_add(params: CollisionAddInput) -> str:
        """Add collision body to an object (for cloth/soft body collision).

        Args:
            params: Object name, damping, thickness, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "collision_add",
            {
                "object_name": params.object_name,
                "damping": params.damping,
                "thickness": params.thickness,
                "friction": params.friction,
            },
        )

        if result.get("success"):
            return f"Successfully added collision body to '{params.object_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_physics_particles_create",
        annotations={
            "title": "Create Particle System",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_particles_create(params: ParticleSystemInput) -> str:
        """Create a particle system.

        Args:
            params: Emitter, particle count, lifetime, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "particles_create",
            {
                "object_name": params.object_name,
                "particle_type": params.particle_type,
                "count": params.count,
                "lifetime": params.lifetime,
                "emit_from": params.emit_from,
                "velocity_normal": params.velocity_normal,
            },
        )

        if result.get("success"):
            return f"Successfully created particle system for '{params.object_name}' ({params.count} particles)"
        else:
            return f"Failed to create: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_physics_force_field_add",
        annotations={
            "title": "Add Force Field",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_force_field_add(params: ForceFieldInput) -> str:
        """Add a force field (wind, vortex, turbulence, etc.).

        Args:
            params: Force field type, location, strength, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "force_field_add",
            {
                "force_type": params.force_type,
                "location": params.location or [0, 0, 0],
                "strength": params.strength,
                "flow": params.flow,
            },
        )

        if result.get("success"):
            return f"Successfully created {params.force_type} force field"
        else:
            return f"Failed to create: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_physics_soft_body_add",
        annotations={
            "title": "Add Soft Body",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_physics_soft_body_add(params: SoftBodyAddInput) -> str:
        """Add soft body simulation to an object.

        Args:
            params: Object name, mass, friction, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "physics",
            "soft_body_add",
            {
                "object_name": params.object_name,
                "mass": params.mass,
                "friction": params.friction,
                "goal_strength": params.goal_strength,
            },
        )

        if result.get("success"):
            return f"Successfully added soft body simulation to '{params.object_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"
