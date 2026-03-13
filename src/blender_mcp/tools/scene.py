"""
Scene Management Tools

Provides scene creation, listing, switching, deletion, and other features.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ResponseFormat(str, Enum):
    """Response format"""

    MARKDOWN = "markdown"
    JSON = "json"


class UnitSystem(str, Enum):
    """Unit system"""

    NONE = "NONE"
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


# ==================== Input Models ====================


class SceneCreateInput(BaseModel):
    """Create scene input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Scene name", min_length=1, max_length=100)
    copy_from: str | None = Field(default=None, description="Source scene name to copy from")


class SceneListInput(BaseModel):
    """List scenes input"""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format: markdown or json"
    )


class SceneGetInfoInput(BaseModel):
    """Get scene info input"""

    scene_name: str | None = Field(
        default=None, description="Scene name; returns current scene if empty"
    )


class SceneSwitchInput(BaseModel):
    """Switch scene input"""

    scene_name: str = Field(..., description="Name of the scene to switch to")


class SceneDeleteInput(BaseModel):
    """Delete scene input"""

    scene_name: str = Field(..., description="Name of the scene to delete")


class SceneSettingsInput(BaseModel):
    """Scene settings input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    scene_name: str | None = Field(default=None, description="Scene name")
    frame_start: int | None = Field(default=None, description="Start frame", ge=0)
    frame_end: int | None = Field(default=None, description="End frame", ge=1)
    fps: int | None = Field(default=None, description="Frame rate", ge=1, le=120)
    unit_system: UnitSystem | None = Field(default=None, description="Unit system")
    unit_scale: float | None = Field(default=None, description="Unit scale", gt=0)


# ==================== Tool Registration ====================


def register_scene_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register scene management tools"""

    @mcp.tool(
        name="blender_scene_create",
        annotations={
            "title": "Create Scene",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_scene_create(params: SceneCreateInput) -> str:
        """Create a new scene in Blender.

        Creates a new scene, optionally copied from an existing scene.

        Args:
            params: Contains scene name and optional copy source

        Returns:
            Creation result as JSON string
        """
        result = await server.execute_command(
            "scene", "create", {"name": params.name, "copy_from": params.copy_from}
        )

        if result.get("success"):
            return f"Successfully created scene '{params.name}'"
        else:
            error = result.get("error", {})
            return f"Failed to create scene: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_scene_list",
        annotations={
            "title": "List Scenes",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_scene_list(params: SceneListInput) -> str:
        """List all scenes in Blender.

        Returns a list of all scenes including name, object count, and other info.

        Args:
            params: Output format options

        Returns:
            Scene list (Markdown or JSON format)
        """
        result = await server.execute_command("scene", "list", {})

        if not result.get("success"):
            return f"Failed to get scene list: {result.get('error', {}).get('message', 'Unknown error')}"

        scenes = result.get("data", {}).get("scenes", [])

        if params.response_format == ResponseFormat.JSON:
            import json

            return json.dumps({"scenes": scenes, "total": len(scenes)}, indent=2)

        # Markdown format
        lines = ["# Blender Scene List", ""]
        lines.append(f"Total: {len(scenes)} scene(s)")
        lines.append("")

        for scene in scenes:
            active = " (current)" if scene.get("is_active") else ""
            lines.append(f"## {scene['name']}{active}")
            lines.append(f"- Object count: {scene.get('objects_count', 0)}")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_scene_get_info",
        annotations={
            "title": "Get Scene Info",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_scene_get_info(params: SceneGetInfoInput) -> str:
        """Get detailed information about a scene.

        Returns the scene's frame range, FPS, unit settings, and other detailed info.

        Args:
            params: Scene name (optional)

        Returns:
            Detailed scene information
        """
        result = await server.execute_command(
            "scene", "get_info", {"scene_name": params.scene_name}
        )

        if not result.get("success"):
            return f"Failed to get scene info: {result.get('error', {}).get('message', 'Unknown error')}"

        data = result.get("data", {})

        lines = [f"# Scene: {data.get('name', 'Unknown')}", ""]
        lines.append(
            f"- **Frame Range**: {data.get('frame_start', 1)} - {data.get('frame_end', 250)}"
        )
        lines.append(f"- **Current Frame**: {data.get('frame_current', 1)}")
        lines.append(f"- **Frame Rate**: {data.get('fps', 24)} FPS")
        lines.append(f"- **Object Count**: {data.get('objects_count', 0)}")
        lines.append(f"- **Unit System**: {data.get('unit_system', 'METRIC')}")
        lines.append(f"- **Unit Scale**: {data.get('unit_scale', 1.0)}")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_scene_switch",
        annotations={
            "title": "Switch Scene",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_scene_switch(params: SceneSwitchInput) -> str:
        """Switch to the specified scene.

        Args:
            params: Target scene name

        Returns:
            Switch result
        """
        result = await server.execute_command("scene", "switch", {"scene_name": params.scene_name})

        if result.get("success"):
            return f"Switched to scene '{params.scene_name}'"
        else:
            return (
                f"Failed to switch scene: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_scene_delete",
        annotations={
            "title": "Delete Scene",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_scene_delete(params: SceneDeleteInput) -> str:
        """Delete the specified scene.

        Note: Cannot delete the last remaining scene.

        Args:
            params: Name of the scene to delete

        Returns:
            Deletion result
        """
        result = await server.execute_command("scene", "delete", {"scene_name": params.scene_name})

        if result.get("success"):
            return f"Deleted scene '{params.scene_name}'"
        else:
            return (
                f"Failed to delete scene: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_scene_set_settings",
        annotations={
            "title": "Set Scene Settings",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_scene_set_settings(params: SceneSettingsInput) -> str:
        """Set scene settings.

        Can set frame range, frame rate, unit system, etc.

        Args:
            params: Scene settings parameters

        Returns:
            Settings result
        """
        settings = {}
        if params.frame_start is not None:
            settings["frame_start"] = params.frame_start
        if params.frame_end is not None:
            settings["frame_end"] = params.frame_end
        if params.fps is not None:
            settings["fps"] = params.fps
        if params.unit_system is not None:
            settings["unit_system"] = params.unit_system.value
        if params.unit_scale is not None:
            settings["unit_scale"] = params.unit_scale

        if not settings:
            return "No settings parameters specified"

        result = await server.execute_command(
            "scene", "set_settings", {"scene_name": params.scene_name, "settings": settings}
        )

        if result.get("success"):
            return "Scene settings updated"
        else:
            return f"Settings failed: {result.get('error', {}).get('message', 'Unknown error')}"
