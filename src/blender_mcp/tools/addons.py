"""
Addon Management Tools

MCP tools for managing Blender addons.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class AddonEnableInput(BaseModel):
    """Enable addon"""

    addon_name: str = Field(..., description="Addon module name")


class AddonDisableInput(BaseModel):
    """Disable addon"""

    addon_name: str = Field(..., description="Addon module name")


class AddonInstallInput(BaseModel):
    """Install addon"""

    filepath: str = Field(..., description="Addon file path (.py or .zip)")
    overwrite: bool = Field(True, description="Overwrite existing addon")
    enable: bool = Field(True, description="Enable after installation")


class AddonInfoInput(BaseModel):
    """Get addon info"""

    addon_name: str = Field(..., description="Addon module name")


# ============ Tool Registration ============


def register_addon_tools(mcp: FastMCP, server) -> None:
    """Register addon management tools"""

    @mcp.tool()
    async def blender_addon_list() -> dict[str, Any]:
        """
        List all installed addons

        Returns:
            List of installed addons with their enabled status
        """
        return await server.send_command("addons", "list", {})

    @mcp.tool()
    async def blender_addon_enable(addon_name: str) -> dict[str, Any]:
        """
        Enable an addon

        Args:
            addon_name: Addon module name
        """
        params = AddonEnableInput(addon_name=addon_name)
        return await server.send_command("addons", "enable", params.model_dump())

    @mcp.tool()
    async def blender_addon_disable(addon_name: str) -> dict[str, Any]:
        """
        Disable an addon

        Args:
            addon_name: Addon module name
        """
        params = AddonDisableInput(addon_name=addon_name)
        return await server.send_command("addons", "disable", params.model_dump())

    @mcp.tool()
    async def blender_addon_install(
        filepath: str, overwrite: bool = True, enable: bool = True
    ) -> dict[str, Any]:
        """
        Install an addon

        Args:
            filepath: Addon file path (.py or .zip)
            overwrite: Overwrite existing addon
            enable: Enable after installation
        """
        params = AddonInstallInput(filepath=filepath, overwrite=overwrite, enable=enable)
        return await server.send_command("addons", "install", params.model_dump())

    @mcp.tool()
    async def blender_addon_info(addon_name: str) -> dict[str, Any]:
        """
        Get detailed addon information

        Args:
            addon_name: Addon module name
        """
        params = AddonInfoInput(addon_name=addon_name)
        return await server.send_command("addons", "info", params.model_dump())
