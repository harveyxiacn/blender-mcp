"""
Version Control Tools

Provides MCP tools for Blender scene version management.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class VersionSaveInput(BaseModel):
    """Save version"""

    name: str | None = Field(None, description="Version name")
    description: str = Field("", description="Version description")
    create_thumbnail: bool = Field(True, description="Generate thumbnail")


class VersionRestoreInput(BaseModel):
    """Restore version"""

    version_id: str = Field(..., description="Version ID")
    create_backup: bool = Field(True, description="Create backup before restoring")


class VersionCompareInput(BaseModel):
    """Compare versions"""

    version_id_1: str = Field(..., description="Version 1 ID")
    version_id_2: str = Field(..., description="Version 2 ID")


class VersionBranchInput(BaseModel):
    """Create branch"""

    branch_name: str = Field(..., description="Branch name")
    from_version: str | None = Field(None, description="Create from specified version")


class VersionMergeInput(BaseModel):
    """Merge branch"""

    source_branch: str = Field(..., description="Source branch")
    target_branch: str = Field("main", description="Target branch")
    strategy: str = Field("theirs", description="Merge strategy: theirs, ours, manual")


class VersionDeleteInput(BaseModel):
    """Delete version"""

    version_id: str = Field(..., description="Version ID")
    force: bool = Field(False, description="Force delete")


# ============ Tool Registration ============


def register_versioning_tools(mcp: FastMCP, server) -> None:
    """Register version control tools"""

    @mcp.tool()
    async def blender_version_init(project_path: str | None = None) -> dict[str, Any]:
        """
        Initialize the version control system

        Args:
            project_path: Project path (uses current file directory if empty)
        """
        return await server.send_command("versioning", "init", {"project_path": project_path})

    @mcp.tool()
    async def blender_version_save(
        name: str | None = None, description: str = "", create_thumbnail: bool = True
    ) -> dict[str, Any]:
        """
        Save current scene as a new version

        Args:
            name: Version name (auto-generated if empty)
            description: Version description
            create_thumbnail: Whether to generate a thumbnail
        """
        params = VersionSaveInput(
            name=name, description=description, create_thumbnail=create_thumbnail
        )
        return await server.send_command("versioning", "save", params.model_dump())

    @mcp.tool()
    async def blender_version_list(branch: str = "main", limit: int = 20) -> dict[str, Any]:
        """
        List all versions

        Args:
            branch: Branch name
            limit: Return count limit
        """
        return await server.send_command("versioning", "list", {"branch": branch, "limit": limit})

    @mcp.tool()
    async def blender_version_restore(
        version_id: str, create_backup: bool = True
    ) -> dict[str, Any]:
        """
        Restore to a specified version

        Args:
            version_id: Version ID
            create_backup: Whether to create a backup of current state before restoring
        """
        params = VersionRestoreInput(version_id=version_id, create_backup=create_backup)
        return await server.send_command("versioning", "restore", params.model_dump())

    @mcp.tool()
    async def blender_version_compare(version_id_1: str, version_id_2: str) -> dict[str, Any]:
        """
        Compare differences between two versions

        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
        """
        params = VersionCompareInput(version_id_1=version_id_1, version_id_2=version_id_2)
        return await server.send_command("versioning", "compare", params.model_dump())

    @mcp.tool()
    async def blender_version_branch(
        branch_name: str, from_version: str | None = None
    ) -> dict[str, Any]:
        """
        Create a new branch

        Args:
            branch_name: Branch name
            from_version: Create from specified version (uses current version if empty)
        """
        params = VersionBranchInput(branch_name=branch_name, from_version=from_version)
        return await server.send_command("versioning", "branch", params.model_dump())

    @mcp.tool()
    async def blender_version_branches() -> dict[str, Any]:
        """
        List all branches
        """
        return await server.send_command("versioning", "branches", {})

    @mcp.tool()
    async def blender_version_switch_branch(branch_name: str) -> dict[str, Any]:
        """
        Switch to a specified branch

        Args:
            branch_name: Branch name
        """
        return await server.send_command(
            "versioning", "switch_branch", {"branch_name": branch_name}
        )

    @mcp.tool()
    async def blender_version_delete(version_id: str, force: bool = False) -> dict[str, Any]:
        """
        Delete a specified version

        Args:
            version_id: Version ID
            force: Force delete
        """
        params = VersionDeleteInput(version_id=version_id, force=force)
        return await server.send_command("versioning", "delete", params.model_dump())

    @mcp.tool()
    async def blender_version_info(version_id: str) -> dict[str, Any]:
        """
        Get detailed version information

        Args:
            version_id: Version ID
        """
        return await server.send_command("versioning", "info", {"version_id": version_id})
