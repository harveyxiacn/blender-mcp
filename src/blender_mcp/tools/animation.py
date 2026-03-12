"""
Animation Tools

Provides keyframe animation and timeline control features.
"""

from typing import TYPE_CHECKING, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class InterpolationType(str, Enum):
    """Interpolation type"""
    CONSTANT = "CONSTANT"
    LINEAR = "LINEAR"
    BEZIER = "BEZIER"
    SINE = "SINE"
    QUAD = "QUAD"
    CUBIC = "CUBIC"
    QUART = "QUART"
    QUINT = "QUINT"
    EXPO = "EXPO"
    CIRC = "CIRC"
    BACK = "BACK"
    BOUNCE = "BOUNCE"
    ELASTIC = "ELASTIC"


# ==================== Input Models ====================

class KeyframeInsertInput(BaseModel):
    """Insert keyframe input"""
    object_name: str = Field(..., description="Object name")
    data_path: str = Field(..., description="Data path (e.g. location, rotation_euler, scale)")
    frame: Optional[int] = Field(default=None, description="Frame number, uses current frame if empty")
    value: Optional[Any] = Field(default=None, description="Property value")


class KeyframeDeleteInput(BaseModel):
    """Delete keyframe input"""
    object_name: str = Field(..., description="Object name")
    data_path: str = Field(..., description="Data path")
    frame: Optional[int] = Field(default=None, description="Frame number")


class AnimationSetInterpolationInput(BaseModel):
    """Set interpolation type input"""
    object_name: str = Field(..., description="Object name")
    interpolation: InterpolationType = Field(..., description="Interpolation type")


class TimelineSetRangeInput(BaseModel):
    """Set timeline range input"""
    frame_start: Optional[int] = Field(default=None, description="Start frame", ge=0)
    frame_end: Optional[int] = Field(default=None, description="End frame", ge=1)
    frame_current: Optional[int] = Field(default=None, description="Current frame", ge=0)


class TimelineGotoFrameInput(BaseModel):
    """Go to frame input"""
    frame: int = Field(..., description="Target frame", ge=0)


class AnimationBakeInput(BaseModel):
    """Bake animation input"""
    object_name: str = Field(..., description="Object name")
    frame_start: Optional[int] = Field(default=None, description="Start frame")
    frame_end: Optional[int] = Field(default=None, description="End frame")
    step: int = Field(default=1, description="Frame step", ge=1)
    bake_location: bool = Field(default=True, description="Bake location")
    bake_rotation: bool = Field(default=True, description="Bake rotation")
    bake_scale: bool = Field(default=True, description="Bake scale")


class ActionCreateInput(BaseModel):
    """Create action input"""
    armature_name: str = Field(..., description="Armature name")
    action_name: str = Field(default="Action", description="Action name")
    fake_user: bool = Field(default=True, description="Set fake user (prevent cleanup)")


class BoneKeyframe(BaseModel):
    """Bone keyframe data"""
    frame: int = Field(..., description="Frame number")
    bone: str = Field(..., description="Bone name")
    location: Optional[list] = Field(default=None, description="Location [x, y, z]")
    rotation: Optional[list] = Field(default=None, description="Euler rotation [x, y, z]")
    rotation_quaternion: Optional[list] = Field(default=None, description="Quaternion rotation [w, x, y, z]")
    scale: Optional[list] = Field(default=None, description="Scale [x, y, z]")


class ActionCreateFromPosesInput(BaseModel):
    """Create action from poses input"""
    armature_name: str = Field(..., description="Armature name")
    action_name: str = Field(default="Action", description="Action name")
    keyframes: list = Field(..., description="Keyframe data list [{frame, bone, location, rotation, scale}, ...]")
    fake_user: bool = Field(default=True, description="Set fake user")


class ActionListInput(BaseModel):
    """List actions input"""
    armature_name: Optional[str] = Field(default=None, description="Armature name (optional)")


class ActionAssignInput(BaseModel):
    """Assign action input"""
    armature_name: str = Field(..., description="Armature name")
    action_name: str = Field(..., description="Action name")


class NLAPushActionInput(BaseModel):
    """Push action to NLA input"""
    armature_name: str = Field(..., description="Armature name")
    action_name: Optional[str] = Field(default=None, description="Action name (uses current action if empty)")
    track_name: str = Field(default="NLATrack", description="NLA track name")
    start_frame: int = Field(default=1, description="Start frame")


# ==================== Tool Registration ====================

def register_animation_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register animation tools"""

    @mcp.tool(
        name="blender_keyframe_insert",
        annotations={
            "title": "Insert Keyframe",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_keyframe_insert(params: KeyframeInsertInput) -> str:
        """Insert a keyframe.

        Insert a keyframe for the specified property of an object.

        Common data paths:
        - location: Position
        - rotation_euler: Euler rotation
        - scale: Scale
        - location[0]: X position

        Args:
            params: Object name, data path, frame number, value

        Returns:
            Insertion result
        """
        result = await server.execute_command(
            "animation", "keyframe_insert",
            {
                "object_name": params.object_name,
                "data_path": params.data_path,
                "frame": params.frame,
                "value": params.value
            }
        )

        if result.get("success"):
            frame = params.frame or result.get("data", {}).get("frame", "current")
            return f"Inserted keyframe for '{params.object_name}' {params.data_path} at frame {frame}"
        else:
            return f"Failed to insert keyframe: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_keyframe_delete",
        annotations={
            "title": "Delete Keyframe",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_keyframe_delete(params: KeyframeDeleteInput) -> str:
        """Delete a keyframe.

        Args:
            params: Object name, data path, frame number

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "animation", "keyframe_delete",
            {
                "object_name": params.object_name,
                "data_path": params.data_path,
                "frame": params.frame
            }
        )

        if result.get("success"):
            return f"Keyframe deleted"
        else:
            return f"Failed to delete keyframe: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_animation_set_interpolation",
        annotations={
            "title": "Set Interpolation Type",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_animation_set_interpolation(params: AnimationSetInterpolationInput) -> str:
        """Set the interpolation type for keyframes.

        Supported interpolation types include: constant, linear, bezier, easing, etc.

        Args:
            params: Object name and interpolation type

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "animation", "set_interpolation",
            {
                "object_name": params.object_name,
                "interpolation": params.interpolation.value
            }
        )

        if result.get("success"):
            return f"Set interpolation type for '{params.object_name}' to {params.interpolation.value}"
        else:
            return f"Failed to set interpolation: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_timeline_set_range",
        annotations={
            "title": "Set Timeline Range",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_timeline_set_range(params: TimelineSetRangeInput) -> str:
        """Set the timeline range.

        Can set start frame, end frame, and current frame.

        Args:
            params: Frame range settings

        Returns:
            Setting result
        """
        settings = {}
        if params.frame_start is not None:
            settings["frame_start"] = params.frame_start
        if params.frame_end is not None:
            settings["frame_end"] = params.frame_end
        if params.frame_current is not None:
            settings["frame_current"] = params.frame_current

        if not settings:
            return "No settings specified"

        result = await server.execute_command(
            "animation", "timeline_set_range",
            settings
        )

        if result.get("success"):
            return f"Timeline range updated"
        else:
            return f"Failed to set timeline: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_timeline_goto_frame",
        annotations={
            "title": "Go to Frame",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_timeline_goto_frame(params: TimelineGotoFrameInput) -> str:
        """Go to the specified frame.

        Args:
            params: Target frame number

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "animation", "goto_frame",
            {"frame": params.frame}
        )

        if result.get("success"):
            return f"Jumped to frame {params.frame}"
        else:
            return f"Failed to jump: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_animation_bake",
        annotations={
            "title": "Bake Animation",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_animation_bake(params: AnimationBakeInput) -> str:
        """Bake animation.

        Convert constraints, drivers, etc. into keyframe animation.

        Args:
            params: Bake parameters

        Returns:
            Bake result
        """
        result = await server.execute_command(
            "animation", "bake",
            {
                "object_name": params.object_name,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
                "step": params.step,
                "bake_location": params.bake_location,
                "bake_rotation": params.bake_rotation,
                "bake_scale": params.bake_scale
            }
        )

        if result.get("success"):
            return f"Baked animation for '{params.object_name}'"
        else:
            return f"Failed to bake animation: {result.get('error', {}).get('message', 'unknown error')}"

    # ==================== Animation Action Tools ====================

    @mcp.tool(
        name="blender_action_create",
        annotations={
            "title": "Create Animation Action",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_action_create(params: ActionCreateInput) -> str:
        """Create a new animation action.

        An action is a set of keyframe data that can be reused across different armatures.

        Args:
            params: Armature name, action name

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "animation", "action_create",
            {
                "armature_name": params.armature_name,
                "action_name": params.action_name,
                "fake_user": params.fake_user
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Created action '{data.get('action_name', params.action_name)}' and assigned to '{params.armature_name}'"
        else:
            return f"Failed to create action: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_action_create_from_poses",
        annotations={
            "title": "Create Action from Poses",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_action_create_from_poses(params: ActionCreateFromPosesInput) -> str:
        """Batch create animation keyframes from a list of poses.

        Used to quickly create animation sequences such as idle, attack, jump actions.

        Keyframe format:
        [{
            "frame": frame number,
            "bone": "bone name",
            "location": [x, y, z],      # optional
            "rotation": [x, y, z],       # Euler angles, optional
            "rotation_quaternion": [w, x, y, z],  # quaternion, optional
            "scale": [x, y, z]           # optional
        }, ...]

        Args:
            params: Armature name, action name, keyframe list

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "animation", "action_create_from_poses",
            {
                "armature_name": params.armature_name,
                "action_name": params.action_name,
                "keyframes": params.keyframes,
                "fake_user": params.fake_user
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            bones = data.get("bones_animated", [])
            return f"Created action '{data.get('action_name', params.action_name)}' with {data.get('keyframe_count', 0)} keyframes, bones: {', '.join(bones) if bones else 'N/A'}"
        else:
            return f"Failed to create action: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_action_list",
        annotations={
            "title": "List Animation Actions",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_action_list(params: ActionListInput) -> str:
        """List all animation actions.

        Args:
            params: Optional armature name filter

        Returns:
            Action list
        """
        result = await server.execute_command(
            "animation", "action_list",
            {"armature_name": params.armature_name}
        )

        if result.get("success"):
            data = result.get("data", {})
            actions = data.get("actions", [])

            if not actions:
                return "No actions found"

            lines = ["# Animation Action List", ""]
            for action in actions:
                status = "📌" if action.get("fake_user") else "  "
                lines.append(f"{status} **{action['name']}** (frames: {action['frame_start']:.0f}-{action['frame_end']:.0f})")

            return "\n".join(lines)
        else:
            return f"Failed to get action list: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_action_assign",
        annotations={
            "title": "Assign Animation Action",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_action_assign(params: ActionAssignInput) -> str:
        """Assign an animation action to an armature.

        Args:
            params: Armature name, action name

        Returns:
            Assignment result
        """
        result = await server.execute_command(
            "animation", "action_assign",
            {
                "armature_name": params.armature_name,
                "action_name": params.action_name
            }
        )

        if result.get("success"):
            return f"Assigned action '{params.action_name}' to '{params.armature_name}'"
        else:
            return f"Failed to assign action: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_nla_push_action",
        annotations={
            "title": "Push Action to NLA",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_nla_push_action(params: NLAPushActionInput) -> str:
        """Push an action to an NLA track.

        NLA (Non-Linear Animation) allows blending and sequencing multiple actions.

        Args:
            params: Armature name, action name, track name, start frame

        Returns:
            Push result
        """
        result = await server.execute_command(
            "animation", "nla_push_action",
            {
                "armature_name": params.armature_name,
                "action_name": params.action_name,
                "track_name": params.track_name,
                "start_frame": params.start_frame
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Pushed action '{data.get('action_name', 'N/A')}' to NLA track '{data.get('track_name', params.track_name)}'"
        else:
            return f"Failed to push action: {result.get('error', {}).get('message', 'unknown error')}"
