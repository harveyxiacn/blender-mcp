"""
Preferences tools

Provides MCP tools for Blender preferences management.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class PrefGetInput(BaseModel):
    """Get preference input"""

    category: str = Field(..., description="Preference category")
    key: str = Field(..., description="Preference key")


class PrefSetInput(BaseModel):
    """Set preference input"""

    category: str = Field(..., description="Preference category")
    key: str = Field(..., description="Preference key")
    value: Any = Field(..., description="Preference value")


class PrefThemeInput(BaseModel):
    """Theme settings input"""

    preset: str | None = Field(None, description="Preset theme name")
    custom_colors: dict[str, list[float]] | None = Field(None, description="Custom colors")


class PrefViewportInput(BaseModel):
    """Viewport settings input"""

    show_gizmo: bool | None = Field(None, description="Show gizmos")
    show_floor: bool | None = Field(None, description="Show floor grid")
    show_axis_x: bool | None = Field(None, description="Show X axis")
    show_axis_y: bool | None = Field(None, description="Show Y axis")
    show_axis_z: bool | None = Field(None, description="Show Z axis")
    clip_start: float | None = Field(None, description="Near clipping distance")
    clip_end: float | None = Field(None, description="Far clipping distance")


class PrefSystemInput(BaseModel):
    """System settings input"""

    memory_cache_limit: int | None = Field(None, description="Memory cache limit (MB)")
    undo_steps: int | None = Field(None, description="Undo steps")
    use_gpu_subdivision: bool | None = Field(None, description="GPU subdivision")


# ============ Tool Registration ============


def register_preferences_tools(mcp: FastMCP, server) -> None:
    """Register preferences tools"""

    @mcp.tool()
    async def blender_pref_get(category: str, key: str) -> dict[str, Any]:
        """
        Get Blender preference settings

        Args:
            category: Preference category (view, system, edit, input, etc.)
            key: Preference key name
        """
        params = PrefGetInput(category=category, key=key)
        return await server.send_command("preferences", "get", params.model_dump())

    @mcp.tool()
    async def blender_pref_set(category: str, key: str, value: Any) -> dict[str, Any]:
        """
        Set Blender preference

        Args:
            category: Preference category (view, system, edit, input, etc.)
            key: Preference key name
            value: Preference value
        """
        params = PrefSetInput(category=category, key=key, value=value)
        return await server.send_command("preferences", "set", params.model_dump())

    @mcp.tool()
    async def blender_pref_theme(
        preset: str | None = None, custom_colors: dict[str, list[float]] | None = None
    ) -> dict[str, Any]:
        """
        Set theme

        Args:
            preset: Preset theme name (Dark, Light, etc.)
            custom_colors: Custom color dictionary
        """
        params = PrefThemeInput(preset=preset, custom_colors=custom_colors)
        return await server.send_command("preferences", "theme", params.model_dump())

    @mcp.tool()
    async def blender_pref_viewport(
        show_gizmo: bool | None = None,
        show_floor: bool | None = None,
        show_axis_x: bool | None = None,
        show_axis_y: bool | None = None,
        show_axis_z: bool | None = None,
        clip_start: float | None = None,
        clip_end: float | None = None,
    ) -> dict[str, Any]:
        """
        Set viewport preferences

        Args:
            show_gizmo: Show gizmos
            show_floor: Show floor grid
            show_axis_x/y/z: Show coordinate axes
            clip_start: Near clipping distance
            clip_end: Far clipping distance
        """
        params = PrefViewportInput(
            show_gizmo=show_gizmo,
            show_floor=show_floor,
            show_axis_x=show_axis_x,
            show_axis_y=show_axis_y,
            show_axis_z=show_axis_z,
            clip_start=clip_start,
            clip_end=clip_end,
        )
        return await server.send_command("preferences", "viewport", params.model_dump())

    @mcp.tool()
    async def blender_pref_system(
        memory_cache_limit: int | None = None,
        undo_steps: int | None = None,
        use_gpu_subdivision: bool | None = None,
    ) -> dict[str, Any]:
        """
        Set system preferences

        Args:
            memory_cache_limit: Memory cache limit (MB)
            undo_steps: Undo steps
            use_gpu_subdivision: Use GPU subdivision
        """
        params = PrefSystemInput(
            memory_cache_limit=memory_cache_limit,
            undo_steps=undo_steps,
            use_gpu_subdivision=use_gpu_subdivision,
        )
        return await server.send_command("preferences", "system", params.model_dump())

    @mcp.tool()
    async def blender_pref_save() -> dict[str, Any]:
        """
        Save preferences
        """
        return await server.send_command("preferences", "save", {})

    @mcp.tool()
    async def blender_pref_load_factory() -> dict[str, Any]:
        """
        Load factory settings
        """
        return await server.send_command("preferences", "load_factory", {})
