"""
Rigging tools

Provides armature creation, bone addition, IK setup, and related functionality.
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class RigType(str, Enum):
    """Rig type"""
    HUMAN = "HUMAN"
    QUADRUPED = "QUADRUPED"
    BIRD = "BIRD"
    BASIC = "BASIC"


# ==================== Input Models ====================

class ArmatureCreateInput(BaseModel):
    """Create armature input"""
    name: Optional[str] = Field(default="Armature", description="Armature name")
    location: Optional[List[float]] = Field(default=None, description="Location")


class BoneAddInput(BaseModel):
    """Add bone input"""
    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    head: List[float] = Field(..., description="Bone head position [x, y, z]")
    tail: List[float] = Field(..., description="Bone tail position [x, y, z]")
    parent: Optional[str] = Field(default=None, description="Parent bone name")
    use_connect: bool = Field(default=False, description="Connect to parent bone")


class ArmatureGenerateRigInput(BaseModel):
    """Generate rig input"""
    target_mesh: str = Field(..., description="Target mesh name")
    rig_type: RigType = Field(default=RigType.HUMAN, description="Rig type")
    auto_weights: bool = Field(default=True, description="Auto-calculate weights")


class IKSetupInput(BaseModel):
    """IK setup input"""
    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    target: str = Field(..., description="Target object or bone")
    chain_length: int = Field(default=2, description="IK chain length", ge=1, le=10)
    pole_target: Optional[str] = Field(default=None, description="Pole target")


class PoseSetInput(BaseModel):
    """Set pose input"""
    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    location: Optional[List[float]] = Field(default=None, description="Location")
    rotation: Optional[List[float]] = Field(default=None, description="Rotation (Euler angles)")
    rotation_mode: str = Field(default="XYZ", description="Rotation mode")


class WeightPaintInput(BaseModel):
    """Weight paint input"""
    mesh_name: str = Field(..., description="Mesh name")
    armature_name: str = Field(..., description="Armature name")
    auto_normalize: bool = Field(default=True, description="Auto-normalize weights")


class BindType(str, Enum):
    """Bind type"""
    AUTO = "AUTO"           # Auto weights (recommended)
    ENVELOPE = "ENVELOPE"   # Envelope weights
    EMPTY = "EMPTY"         # Bind only, no weights


class ArmatureBindInput(BaseModel):
    """Armature bind input"""
    mesh_name: str = Field(..., description="Mesh object name")
    armature_name: str = Field(..., description="Armature object name")
    bind_type: BindType = Field(
        default=BindType.AUTO,
        description="Bind type: AUTO (auto weights), ENVELOPE (envelope weights), EMPTY (bind only)"
    )
    preserve_volume: bool = Field(
        default=True,
        description="Preserve volume (prevents excessive deformation at joints)"
    )


class VertexGroupCreateInput(BaseModel):
    """Create vertex group input"""
    object_name: str = Field(..., description="Object name")
    group_name: str = Field(..., description="Vertex group name")
    vertex_indices: Optional[List[int]] = Field(default=None, description="Vertex index list")
    weight: float = Field(default=1.0, description="Weight value (0.0-1.0)", ge=0, le=1)


class VertexGroupAssignMode(str, Enum):
    """Vertex group assign mode"""
    REPLACE = "REPLACE"     # Replace
    ADD = "ADD"             # Add
    SUBTRACT = "SUBTRACT"   # Subtract


class VertexGroupAssignInput(BaseModel):
    """Assign vertices to vertex group input"""
    object_name: str = Field(..., description="Object name")
    group_name: str = Field(..., description="Vertex group name")
    vertex_indices: List[int] = Field(..., description="Vertex index list")
    weight: float = Field(default=1.0, description="Weight value (0.0-1.0)", ge=0, le=1)
    mode: VertexGroupAssignMode = Field(default=VertexGroupAssignMode.REPLACE, description="Assign mode")


class ConstraintType(str, Enum):
    """Constraint type"""
    IK = "IK"
    COPY_ROTATION = "COPY_ROTATION"
    COPY_LOCATION = "COPY_LOCATION"
    COPY_TRANSFORMS = "COPY_TRANSFORMS"
    LIMIT_ROTATION = "LIMIT_ROTATION"
    LIMIT_LOCATION = "LIMIT_LOCATION"
    DAMPED_TRACK = "DAMPED_TRACK"
    STRETCH_TO = "STRETCH_TO"
    FLOOR = "FLOOR"


class BoneConstraintAddInput(BaseModel):
    """Add bone constraint input"""
    armature_name: str = Field(..., description="Armature name")
    bone_name: str = Field(..., description="Bone name")
    constraint_type: ConstraintType = Field(..., description="Constraint type")
    settings: Optional[dict] = Field(default=None, description="Constraint settings")


# ==================== Tool Registration ====================

def register_rigging_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register rigging tools"""

    @mcp.tool(
        name="blender_armature_create",
        annotations={
            "title": "Create Armature",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_create(params: ArmatureCreateInput) -> str:
        """Create an armature object.

        Args:
            params: Armature name and location

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "rigging", "armature_create",
            {
                "name": params.name,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            name = result.get("data", {}).get("armature_name", params.name)
            return f"Successfully created armature '{name}'"
        else:
            return f"Failed to create armature: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_bone_add",
        annotations={
            "title": "Add Bone",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_bone_add(params: BoneAddInput) -> str:
        """Add a bone to an armature.

        Args:
            params: Armature name, bone name, position, parent

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "rigging", "bone_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "head": params.head,
                "tail": params.tail,
                "parent": params.parent,
                "use_connect": params.use_connect
            }
        )

        if result.get("success"):
            return f"Added bone '{params.bone_name}' to armature '{params.armature_name}'"
        else:
            return f"Failed to add bone: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_armature_generate_rig",
        annotations={
            "title": "Generate Character Rig",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_generate_rig(params: ArmatureGenerateRigInput) -> str:
        """Generate a complete character rig using Rigify.

        Supports human, quadruped, bird, and other rig types.

        Args:
            params: Target mesh, rig type, whether to auto-weight

        Returns:
            Generation result
        """
        result = await server.execute_command(
            "rigging", "generate_rig",
            {
                "target_mesh": params.target_mesh,
                "rig_type": params.rig_type.value,
                "auto_weights": params.auto_weights
            }
        )

        if result.get("success"):
            rig_names = {
                "HUMAN": "human",
                "QUADRUPED": "quadruped",
                "BIRD": "bird",
                "BASIC": "basic"
            }
            return f"Generated {rig_names.get(params.rig_type.value)} rig for '{params.target_mesh}'"
        else:
            return f"Failed to generate rig: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_ik_setup",
        annotations={
            "title": "Setup IK",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_ik_setup(params: IKSetupInput) -> str:
        """Set up Inverse Kinematics (IK) constraint.

        Args:
            params: Armature name, bone name, target, chain length

        Returns:
            Setup result
        """
        result = await server.execute_command(
            "rigging", "ik_setup",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "target": params.target,
                "chain_length": params.chain_length,
                "pole_target": params.pole_target
            }
        )

        if result.get("success"):
            return f"Set up IK constraint for bone '{params.bone_name}'"
        else:
            return f"Failed to set up IK: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_pose_set",
        annotations={
            "title": "Set Pose",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_pose_set(params: PoseSetInput) -> str:
        """Set bone pose.

        Args:
            params: Armature name, bone name, location, rotation

        Returns:
            Operation result
        """
        pose = {}
        if params.location is not None:
            pose["location"] = params.location
        if params.rotation is not None:
            pose["rotation"] = params.rotation
            pose["rotation_mode"] = params.rotation_mode

        if not pose:
            return "No pose parameters specified"

        result = await server.execute_command(
            "rigging", "pose_set",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                **pose
            }
        )

        if result.get("success"):
            return f"Set pose for bone '{params.bone_name}'"
        else:
            return f"Failed to set pose: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_weight_paint",
        annotations={
            "title": "Auto Weight Paint",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_weight_paint(params: WeightPaintInput) -> str:
        """Auto-calculate bone weights for a mesh.

        Args:
            params: Mesh name and armature name

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "rigging", "weight_paint",
            {
                "mesh_name": params.mesh_name,
                "armature_name": params.armature_name,
                "auto_normalize": params.auto_normalize
            }
        )

        if result.get("success"):
            return f"Calculated bone weights for '{params.mesh_name}'"
        else:
            return f"Weight paint failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_armature_bind",
        annotations={
            "title": "Armature Bind",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_bind(params: ArmatureBindInput) -> str:
        """Bind a mesh to an armature.

        Supports auto weights, envelope weights, or bind-only modes.

        Args:
            params: Mesh name, armature name, bind type

        Returns:
            Bind result
        """
        result = await server.execute_command(
            "rigging", "armature_bind",
            {
                "mesh_name": params.mesh_name,
                "armature_name": params.armature_name,
                "bind_type": params.bind_type.value,
                "preserve_volume": params.preserve_volume
            }
        )

        if result.get("success"):
            bind_names = {
                "AUTO": "auto weights",
                "ENVELOPE": "envelope weights",
                "EMPTY": "bind only"
            }
            return f"Bound '{params.mesh_name}' to '{params.armature_name}' ({bind_names.get(params.bind_type.value, params.bind_type.value)})"
        else:
            return f"Bind failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vertex_group_create",
        annotations={
            "title": "Create Vertex Group",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group_create(params: VertexGroupCreateInput) -> str:
        """Create a vertex group.

        Vertex groups are used for bone weights, material assignment, etc.

        Args:
            params: Object name, group name, vertex list

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "rigging", "vertex_group_create",
            {
                "object_name": params.object_name,
                "group_name": params.group_name,
                "vertex_indices": params.vertex_indices or [],
                "weight": params.weight
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Created vertex group '{data.get('group_name', params.group_name)}' (index: {data.get('group_index', 'N/A')})"
        else:
            return f"Failed to create vertex group: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vertex_group_assign",
        annotations={
            "title": "Assign Vertices to Vertex Group",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group_assign(params: VertexGroupAssignInput) -> str:
        """Assign vertices to a vertex group.

        Args:
            params: Object name, group name, vertex list, weight, mode

        Returns:
            Assignment result
        """
        result = await server.execute_command(
            "rigging", "vertex_group_assign",
            {
                "object_name": params.object_name,
                "group_name": params.group_name,
                "vertex_indices": params.vertex_indices,
                "weight": params.weight,
                "mode": params.mode.value
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Assigned {data.get('assigned_count', len(params.vertex_indices))} vertices to '{params.group_name}'"
        else:
            return f"Failed to assign vertices: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_bone_constraint_add",
        annotations={
            "title": "Add Bone Constraint",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_bone_constraint_add(params: BoneConstraintAddInput) -> str:
        """Add a constraint to a bone.

        Supports IK, Copy Rotation, Copy Location, and many other constraint types.

        Args:
            params: Armature name, bone name, constraint type, settings

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "rigging", "bone_constraint_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "constraint_type": params.constraint_type.value,
                "settings": params.settings or {}
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Added {params.constraint_type.value} constraint to bone '{params.bone_name}'"
        else:
            return f"Failed to add constraint: {result.get('error', {}).get('message', 'Unknown error')}"
