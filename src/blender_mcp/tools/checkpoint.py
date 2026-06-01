"""
Blender MCP - Checkpoint Save/Restore Tools

Named save-points for undo safety net, enabling structured rollback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

from mcp.server.fastmcp import FastMCP


class CheckpointSaveInput(BaseModel):
    """Checkpoint save input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Checkpoint name", min_length=1, max_length=100)
    description: str | None = Field(
        default=None, description="Optional description of the scene state"
    )


class CheckpointRestoreInput(BaseModel):
    """Checkpoint restore input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Checkpoint name to restore", min_length=1, max_length=100)


class CheckpointDeleteInput(BaseModel):
    """Checkpoint delete input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Checkpoint name to delete", min_length=1, max_length=100)


def register_checkpoint_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    """Register checkpoint tools"""

    @mcp.tool(
        name="blender_checkpoint_save",
        annotations={
            "title": "Save Checkpoint",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_checkpoint_save(params: CheckpointSaveInput) -> str:
        """Save a named checkpoint of the current scene state. Use before risky operations
        so you can restore if something goes wrong.

        Example: Save checkpoint 'before_rigging' before applying an armature.
        """
        result = await server.execute_command(
            "checkpoint",
            "save",
            {"name": params.name, "description": params.description},
        )

        if result.get("success"):
            data = result.get("data", {})
            path = data.get("path", "")
            obj_count = data.get("object_count", "?")
            return (
                f"Checkpoint '{params.name}' saved successfully.\n"
                f"Objects in scene: {obj_count}\n"
                f"File: {path}"
            )
        else:
            error = result.get("error", {})
            return f"Checkpoint save failed: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_checkpoint_restore",
        annotations={
            "title": "Restore Checkpoint",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_checkpoint_restore(params: CheckpointRestoreInput) -> str:
        """Restore a previously saved checkpoint. WARNING: This replaces the current scene entirely.

        Example: Restore checkpoint 'before_rigging' to undo the armature changes.
        """
        result = await server.execute_command(
            "checkpoint", "restore", {"name": params.name}
        )

        if result.get("success"):
            data = result.get("data", {})
            obj_count = data.get("object_count", "?")
            return (
                f"Checkpoint '{params.name}' restored successfully.\n"
                f"Objects in scene: {obj_count}"
            )
        else:
            error = result.get("error", {})
            suggestion = error.get("suggestion", "")
            msg = f"Checkpoint restore failed: {error.get('message', 'Unknown error')}"
            if suggestion:
                msg += f"\nSuggestion: {suggestion}"
            return msg

    @mcp.tool(
        name="blender_checkpoint_list",
        annotations={
            "title": "List Checkpoints",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_checkpoint_list() -> str:
        """List all saved checkpoints with their names, timestamps, and descriptions.

        Example: List checkpoints to see available restore points.
        """
        result = await server.execute_command("checkpoint", "list", {})

        if result.get("success"):
            data = result.get("data", {})
            checkpoints = data.get("checkpoints", [])
            if not checkpoints:
                return "No checkpoints saved yet. Use blender_checkpoint_save to create one."

            lines = ["Available checkpoints:"]
            for cp in checkpoints:
                desc = f" - {cp['description']}" if cp.get("description") else ""
                lines.append(
                    f"  - {cp['name']} (saved: {cp.get('timestamp', '?')}, "
                    f"objects: {cp.get('object_count', '?')}){desc}"
                )
            return "\n".join(lines)
        else:
            error = result.get("error", {})
            return f"List checkpoints failed: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_checkpoint_delete",
        annotations={
            "title": "Delete Checkpoint",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_checkpoint_delete(params: CheckpointDeleteInput) -> str:
        """Delete a saved checkpoint to free disk space.

        Example: Delete checkpoint 'old_backup' that is no longer needed.
        """
        result = await server.execute_command(
            "checkpoint", "delete", {"name": params.name}
        )

        if result.get("success"):
            return f"Checkpoint '{params.name}' deleted."
        else:
            error = result.get("error", {})
            return f"Delete checkpoint failed: {error.get('message', 'Unknown error')}"
