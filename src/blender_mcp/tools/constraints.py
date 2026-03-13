"""
Constraint System Tools

MCP tools for Blender object and bone constraints.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class ConstraintAddInput(BaseModel):
    """Add constraint"""

    object_name: str = Field(..., description="Object name")
    constraint_type: str = Field(..., description="Constraint type")
    name: str | None = Field(None, description="Constraint name")
    target: str | None = Field(None, description="Target object")
    subtarget: str | None = Field(None, description="Subtarget (bone name)")


class ConstraintRemoveInput(BaseModel):
    """Remove constraint"""

    object_name: str = Field(..., description="Object name")
    constraint_name: str = Field(..., description="Constraint name")


class ConstraintCopyLocationInput(BaseModel):
    """Copy location constraint"""

    object_name: str = Field(..., description="Object name")
    target: str = Field(..., description="Target object")
    subtarget: str | None = Field(None, description="Subtarget bone")
    use_x: bool = Field(True, description="X axis")
    use_y: bool = Field(True, description="Y axis")
    use_z: bool = Field(True, description="Z axis")
    influence: float = Field(1.0, description="Influence")


class ConstraintCopyRotationInput(BaseModel):
    """Copy rotation constraint"""

    object_name: str = Field(..., description="Object name")
    target: str = Field(..., description="Target object")
    subtarget: str | None = Field(None, description="Subtarget bone")
    use_x: bool = Field(True, description="X axis")
    use_y: bool = Field(True, description="Y axis")
    use_z: bool = Field(True, description="Z axis")
    influence: float = Field(1.0, description="Influence")


class ConstraintCopyScaleInput(BaseModel):
    """Copy scale constraint"""

    object_name: str = Field(..., description="Object name")
    target: str = Field(..., description="Target object")
    subtarget: str | None = Field(None, description="Subtarget bone")
    use_x: bool = Field(True, description="X axis")
    use_y: bool = Field(True, description="Y axis")
    use_z: bool = Field(True, description="Z axis")
    influence: float = Field(1.0, description="Influence")


class ConstraintTrackToInput(BaseModel):
    """Track to constraint"""

    object_name: str = Field(..., description="Object name")
    target: str = Field(..., description="Target object")
    subtarget: str | None = Field(None, description="Subtarget bone")
    track_axis: str = Field("TRACK_NEGATIVE_Z", description="Track axis")
    up_axis: str = Field("UP_Y", description="Up axis")
    influence: float = Field(1.0, description="Influence")


class ConstraintLimitInput(BaseModel):
    """Limit constraint"""

    object_name: str = Field(..., description="Object name")
    limit_type: str = Field("LOCATION", description="Limit type: LOCATION, ROTATION, SCALE")
    min_x: float | None = Field(None, description="X minimum")
    max_x: float | None = Field(None, description="X maximum")
    min_y: float | None = Field(None, description="Y minimum")
    max_y: float | None = Field(None, description="Y maximum")
    min_z: float | None = Field(None, description="Z minimum")
    max_z: float | None = Field(None, description="Z maximum")


class ConstraintIKInput(BaseModel):
    """IK constraint (Inverse Kinematics)"""

    object_name: str = Field(..., description="Armature object name")
    bone_name: str = Field(..., description="Bone name")
    target: str | None = Field(None, description="Target object")
    subtarget: str | None = Field(None, description="Target bone")
    pole_target: str | None = Field(None, description="Pole target object")
    pole_subtarget: str | None = Field(None, description="Pole target bone")
    chain_count: int = Field(2, description="Chain length")
    influence: float = Field(1.0, description="Influence")


class ConstraintParentInput(BaseModel):
    """Child of constraint"""

    object_name: str = Field(..., description="Object name")
    target: str = Field(..., description="Target object")
    subtarget: str | None = Field(None, description="Subtarget bone")
    influence: float = Field(1.0, description="Influence")


# ============ Tool Registration ============


def register_constraint_tools(mcp: FastMCP, server) -> None:
    """Register constraint tools"""

    @mcp.tool()
    async def blender_constraint_add(
        object_name: str,
        constraint_type: str,
        name: str | None = None,
        target: str | None = None,
        subtarget: str | None = None,
    ) -> dict[str, Any]:
        """
        Add a constraint

        Args:
            object_name: Object name
            constraint_type: Constraint type (COPY_LOCATION, COPY_ROTATION, TRACK_TO, IK, etc.)
            name: Constraint name
            target: Target object
            subtarget: Subtarget (bone name)
        """
        params = ConstraintAddInput(
            object_name=object_name,
            constraint_type=constraint_type,
            name=name,
            target=target,
            subtarget=subtarget,
        )
        return await server.send_command("constraints", "add", params.model_dump())

    @mcp.tool()
    async def blender_constraint_remove(object_name: str, constraint_name: str) -> dict[str, Any]:
        """
        Remove a constraint

        Args:
            object_name: Object name
            constraint_name: Constraint name
        """
        params = ConstraintRemoveInput(object_name=object_name, constraint_name=constraint_name)
        return await server.send_command("constraints", "remove", params.model_dump())

    @mcp.tool()
    async def blender_constraint_copy_location(
        object_name: str,
        target: str,
        subtarget: str | None = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Add a copy location constraint

        Args:
            object_name: Object name
            target: Target object
            subtarget: Subtarget bone
            use_x/y/z: Whether to affect each axis
            influence: Influence (0-1)
        """
        params = ConstraintCopyLocationInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence,
        )
        return await server.send_command("constraints", "copy_location", params.model_dump())

    @mcp.tool()
    async def blender_constraint_copy_rotation(
        object_name: str,
        target: str,
        subtarget: str | None = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Add a copy rotation constraint

        Args:
            object_name: Object name
            target: Target object
            subtarget: Subtarget bone
            use_x/y/z: Whether to affect each axis
            influence: Influence (0-1)
        """
        params = ConstraintCopyRotationInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence,
        )
        return await server.send_command("constraints", "copy_rotation", params.model_dump())

    @mcp.tool()
    async def blender_constraint_copy_scale(
        object_name: str,
        target: str,
        subtarget: str | None = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Add a copy scale constraint

        Args:
            object_name: Object name
            target: Target object
            subtarget: Subtarget bone
            use_x/y/z: Whether to affect each axis
            influence: Influence (0-1)
        """
        params = ConstraintCopyScaleInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence,
        )
        return await server.send_command("constraints", "copy_scale", params.model_dump())

    @mcp.tool()
    async def blender_constraint_track_to(
        object_name: str,
        target: str,
        subtarget: str | None = None,
        track_axis: str = "TRACK_NEGATIVE_Z",
        up_axis: str = "UP_Y",
        influence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Add a track to constraint

        Args:
            object_name: Object name
            target: Target object
            subtarget: Subtarget bone
            track_axis: Track axis (TRACK_X, TRACK_Y, TRACK_Z, TRACK_NEGATIVE_X/Y/Z)
            up_axis: Up axis (UP_X, UP_Y, UP_Z)
            influence: Influence (0-1)
        """
        params = ConstraintTrackToInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            track_axis=track_axis,
            up_axis=up_axis,
            influence=influence,
        )
        return await server.send_command("constraints", "track_to", params.model_dump())

    @mcp.tool()
    async def blender_constraint_limit(
        object_name: str,
        limit_type: str = "LOCATION",
        min_x: float | None = None,
        max_x: float | None = None,
        min_y: float | None = None,
        max_y: float | None = None,
        min_z: float | None = None,
        max_z: float | None = None,
    ) -> dict[str, Any]:
        """
        Add a limit constraint

        Args:
            object_name: Object name
            limit_type: Limit type (LOCATION, ROTATION, SCALE)
            min_x/max_x: X axis range
            min_y/max_y: Y axis range
            min_z/max_z: Z axis range
        """
        params = ConstraintLimitInput(
            object_name=object_name,
            limit_type=limit_type,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            min_z=min_z,
            max_z=max_z,
        )
        return await server.send_command("constraints", "limit", params.model_dump())

    @mcp.tool()
    async def blender_constraint_ik(
        object_name: str,
        bone_name: str,
        target: str | None = None,
        subtarget: str | None = None,
        pole_target: str | None = None,
        pole_subtarget: str | None = None,
        chain_count: int = 2,
        influence: float = 1.0,
    ) -> dict[str, Any]:
        """
        Add an IK constraint (Inverse Kinematics)

        Args:
            object_name: Armature object name
            bone_name: Bone name
            target: Target object
            subtarget: Target bone
            pole_target: Pole target object
            pole_subtarget: Pole target bone
            chain_count: Chain length
            influence: Influence (0-1)
        """
        params = ConstraintIKInput(
            object_name=object_name,
            bone_name=bone_name,
            target=target,
            subtarget=subtarget,
            pole_target=pole_target,
            pole_subtarget=pole_subtarget,
            chain_count=chain_count,
            influence=influence,
        )
        return await server.send_command("constraints", "ik", params.model_dump())

    @mcp.tool()
    async def blender_constraint_parent(
        object_name: str, target: str, subtarget: str | None = None, influence: float = 1.0
    ) -> dict[str, Any]:
        """
        Add a child of constraint

        Args:
            object_name: Object name
            target: Target object
            subtarget: Subtarget bone
            influence: Influence (0-1)
        """
        params = ConstraintParentInput(
            object_name=object_name, target=target, subtarget=subtarget, influence=influence
        )
        return await server.send_command("constraints", "parent", params.model_dump())

    @mcp.tool()
    async def blender_constraint_list(object_name: str) -> dict[str, Any]:
        """
        List all constraints on an object

        Args:
            object_name: Object name
        """
        return await server.send_command("constraints", "list", {"object_name": object_name})
