"""
Auto Rigging Tools

Provides automatic bone creation, weight painting, IK/FK setup, and more.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class AutoRigSetupInput(BaseModel):
    """Auto rig setup input"""

    character_name: str = Field(..., description="Character name prefix")
    rig_type: str = Field(
        default="humanoid", description="Rig type: humanoid, quadruped, bird, simple"
    )
    auto_weight: bool = Field(default=True, description="Automatic weight painting")
    symmetric: bool = Field(default=True, description="Symmetric bones")


class BoneAddInput(BaseModel):
    """Add bone input"""

    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    head: list[float] = Field(..., description="Bone head position")
    tail: list[float] = Field(..., description="Bone tail position")
    parent_bone: str | None = Field(default=None, description="Parent bone name")
    connect: bool = Field(default=False, description="Connect to parent bone")


class IKSetupInput(BaseModel):
    """IK setup input"""

    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone to add IK to")
    chain_length: int = Field(default=2, description="IK chain length")
    target_name: str | None = Field(default=None, description="IK target object")
    pole_target: str | None = Field(default=None, description="Pole target")


class WeightPaintInput(BaseModel):
    """Weight paint input"""

    object_name: str = Field(..., description="Mesh object name")
    armature_name: str = Field(..., description="Armature name")
    method: str = Field(default="automatic", description="Method: automatic, envelope, nearest")


class PoseApplyInput(BaseModel):
    """Apply pose input"""

    armature_name: str = Field(..., description="Armature name")
    pose_name: str = Field(default="t_pose", description="Pose: t_pose, a_pose, rest, action_pose")


class RigConstraintInput(BaseModel):
    """Bone constraint input"""

    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    constraint_type: str = Field(
        default="COPY_ROTATION",
        description="Constraint type: COPY_ROTATION, COPY_LOCATION, LIMIT_ROTATION, DAMPED_TRACK",
    )
    target_armature: str | None = Field(default=None, description="Target armature")
    target_bone: str | None = Field(default=None, description="Target bone")


# ==================== Tool Registration ====================


def register_auto_rig_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register auto rigging tools"""

    @mcp.tool(
        name="blender_rig_auto_setup",
        annotations={
            "title": "Auto Create Rig",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_rig_auto_setup(params: AutoRigSetupInput) -> str:
        """Automatically create a bone system for a character.

        Automatically creates an appropriate bone structure based on the character mesh.

        Args:
            params: Character name, rig type, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "auto_rig",
            "setup",
            {
                "character_name": params.character_name,
                "rig_type": params.rig_type,
                "auto_weight": params.auto_weight,
                "symmetric": params.symmetric,
            },
        )

        if result.get("success"):
            bones = result.get("data", {}).get("bones_created", 0)
            return f"Successfully created {params.rig_type} rig for '{params.character_name}' with {bones} bones"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_rig_bone_add",
        annotations={
            "title": "Add Bone",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_rig_bone_add(params: BoneAddInput) -> str:
        """Manually add a bone.

        Args:
            params: Armature, bone name, position, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "auto_rig",
            "bone_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "head": params.head,
                "tail": params.tail,
                "parent_bone": params.parent_bone,
                "connect": params.connect,
            },
        )

        if result.get("success"):
            return f"Successfully added bone '{params.bone_name}'"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_rig_ik_setup",
        annotations={
            "title": "Setup IK",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_rig_ik_setup(params: IKSetupInput) -> str:
        """Set up Inverse Kinematics (IK) for a bone.

        Args:
            params: Armature, bone, chain length, etc.

        Returns:
            Setup result
        """
        result = await server.execute_command(
            "auto_rig",
            "ik_setup",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "chain_length": params.chain_length,
                "target_name": params.target_name,
                "pole_target": params.pole_target,
            },
        )

        if result.get("success"):
            return f"Successfully set up IK for '{params.bone_name}' (chain length: {params.chain_length})"
        else:
            return f"Setup failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_rig_weight_paint",
        annotations={
            "title": "Auto Weight Paint",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_rig_weight_paint(params: WeightPaintInput) -> str:
        """Perform automatic weight painting for a mesh object.

        Args:
            params: Mesh object, armature, method

        Returns:
            Painting result
        """
        result = await server.execute_command(
            "auto_rig",
            "weight_paint",
            {
                "object_name": params.object_name,
                "armature_name": params.armature_name,
                "method": params.method,
            },
        )

        if result.get("success"):
            return (
                f"Successfully performed {params.method} weight painting for '{params.object_name}'"
            )
        else:
            return (
                f"Weight painting failed: {result.get('error', {}).get('message', 'unknown error')}"
            )

    @mcp.tool(
        name="blender_rig_pose_apply",
        annotations={
            "title": "Apply Preset Pose",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_rig_pose_apply(params: PoseApplyInput) -> str:
        """Apply a preset pose to an armature.

        Args:
            params: Armature name, pose type

        Returns:
            Application result
        """
        result = await server.execute_command(
            "auto_rig",
            "pose_apply",
            {"armature_name": params.armature_name, "pose_name": params.pose_name},
        )

        if result.get("success"):
            return f"Successfully applied {params.pose_name} pose"
        else:
            return f"Application failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_rig_constraint_add",
        annotations={
            "title": "Add Bone Constraint",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_rig_constraint_add(params: RigConstraintInput) -> str:
        """Add a constraint to a bone.

        Args:
            params: Armature, bone, constraint type, etc.

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "auto_rig",
            "constraint_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "constraint_type": params.constraint_type,
                "target_armature": params.target_armature,
                "target_bone": params.target_bone,
            },
        )

        if result.get("success"):
            return f"Successfully added {params.constraint_type} constraint to '{params.bone_name}'"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"
