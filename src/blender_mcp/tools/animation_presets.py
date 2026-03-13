"""
Preset Animation Tools

Provides preset animation library, action management, NLA editing, and more.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class AnimationPresetApplyInput(BaseModel):
    """Apply preset animation input"""

    armature_name: str = Field(..., description="Armature name")
    preset: str = Field(
        default="idle",
        description="""Preset animation category:
        Basic actions: idle, idle_combat, walk, run, sprint, jump, double_jump, land, dodge_roll, dodge_back
        Combat actions: attack, attack_combo_1, attack_combo_2, attack_combo_3, attack_heavy, attack_spin, attack_uppercut, block, parry, hit_light, hit_heavy, knockdown, getup, death
        Skill actions: cast_spell, cast_fireball, cast_heal, charge_power, release_power
        Social actions: wave, celebrate, dance, sit, bow, salute, point
        Interaction actions: pickup, use_item, open_chest""",
    )
    speed: float = Field(default=1.0, description="Animation speed multiplier", ge=0.1, le=5.0)
    loop: bool = Field(default=True, description="Whether to loop")


class ActionCreateInput(BaseModel):
    """Create action input"""

    action_name: str = Field(..., description="Action name")
    armature_name: str | None = Field(default=None, description="Associated armature")
    frame_start: int = Field(default=1, description="Start frame")
    frame_end: int = Field(default=60, description="End frame")


class ActionLibraryAddInput(BaseModel):
    """Add to action library input"""

    action_name: str = Field(..., description="Action name")
    tags: list[str] | None = Field(default=None, description="Tags")
    category: str = Field(default="general", description="Category")


class NLAStripAddInput(BaseModel):
    """Add NLA strip input"""

    object_name: str = Field(..., description="Object name")
    action_name: str = Field(..., description="Action name")
    track_name: str = Field(default="NlaTrack", description="Track name")
    start_frame: int = Field(default=1, description="Start frame")
    blend_type: str = Field(
        default="REPLACE", description="Blend type: REPLACE, ADD, SUBTRACT, MULTIPLY"
    )
    scale: float = Field(default=1.0, description="Time scale")


class PathAnimationInput(BaseModel):
    """Path animation input"""

    object_name: str = Field(..., description="Object name")
    path_name: str = Field(..., description="Path curve name")
    duration: int = Field(default=100, description="Animation duration in frames")
    follow_rotation: bool = Field(default=True, description="Follow path rotation")


class AnimationBakeInput(BaseModel):
    """Bake animation input"""

    object_name: str = Field(..., description="Object name")
    frame_start: int = Field(default=1, description="Start frame")
    frame_end: int = Field(default=250, description="End frame")
    bake_types: list[str] = Field(
        default=["LOCATION", "ROTATION", "SCALE"], description="Bake types"
    )
    clear_constraints: bool = Field(default=False, description="Clear constraints after baking")


# ==================== Tool Registration ====================


def register_animation_preset_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register preset animation tools"""

    @mcp.tool(
        name="blender_animation_preset_apply",
        annotations={
            "title": "Apply Preset Animation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_animation_preset_apply(params: AnimationPresetApplyInput) -> str:
        """Apply a preset animation to an armature.

        Available presets:
        - idle: Idle breathing animation
        - walk: Walk cycle
        - run: Run cycle
        - jump: Jump
        - wave: Wave
        - celebrate: Celebrate
        - attack: Attack
        - dance: Dance
        - sit: Sit down
        - bow: Bow

        Args:
            params: Armature name, preset type, speed, etc.

        Returns:
            Application result
        """
        result = await server.execute_command(
            "animation_preset",
            "apply",
            {
                "armature_name": params.armature_name,
                "preset": params.preset,
                "speed": params.speed,
                "loop": params.loop,
            },
        )

        if result.get("success"):
            return f"Successfully applied {params.preset} animation to '{params.armature_name}'"
        else:
            return f"Application failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_action_create",
        annotations={
            "title": "Create Action",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_action_create(params: ActionCreateInput) -> str:
        """Create a new action.

        Args:
            params: Action name, frame range, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "animation_preset",
            "action_create",
            {
                "action_name": params.action_name,
                "armature_name": params.armature_name,
                "frame_start": params.frame_start,
                "frame_end": params.frame_end,
            },
        )

        if result.get("success"):
            return f"Successfully created action '{params.action_name}'"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_nla_strip_add",
        annotations={
            "title": "Add NLA Strip",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_nla_strip_add(params: NLAStripAddInput) -> str:
        """Add an NLA strip for animation blending.

        Args:
            params: Object, action, track, etc.

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "animation_preset",
            "nla_add",
            {
                "object_name": params.object_name,
                "action_name": params.action_name,
                "track_name": params.track_name,
                "start_frame": params.start_frame,
                "blend_type": params.blend_type,
                "scale": params.scale,
            },
        )

        if result.get("success"):
            return "Successfully added NLA strip"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_animation_follow_path",
        annotations={
            "title": "Path Animation",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_animation_follow_path(params: PathAnimationInput) -> str:
        """Make an object follow a path.

        Args:
            params: Object, path, duration, etc.

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "animation_preset",
            "follow_path",
            {
                "object_name": params.object_name,
                "path_name": params.path_name,
                "duration": params.duration,
                "follow_rotation": params.follow_rotation,
            },
        )

        if result.get("success"):
            return f"Successfully set '{params.object_name}' to follow '{params.path_name}'"
        else:
            return f"Setting failed: {result.get('error', {}).get('message', 'unknown error')}"

    # Note: blender_animation_bake has been moved to animation.py to avoid duplicate registration
