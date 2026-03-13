"""
Utility Tools

Provides utility features such as script execution, screenshots, and file operations.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class ExecutePythonInput(BaseModel):
    """Execute Python code input"""

    code: str = Field(..., description="Python code")
    timeout: int = Field(default=30, description="Timeout in seconds", ge=1, le=300)


class ViewportScreenshotInput(BaseModel):
    """Viewport screenshot input"""

    output_path: str | None = Field(default=None, description="Output path")
    width: int = Field(default=800, description="Image width", ge=100, le=4096)
    height: int = Field(default=600, description="Image height", ge=100, le=4096)


class FileSaveInput(BaseModel):
    """Save file input"""

    filepath: str | None = Field(default=None, description="File path")
    compress: bool = Field(default=True, description="Compress file")


class FileOpenInput(BaseModel):
    """Open file input"""

    filepath: str = Field(..., description="File path")
    load_ui: bool = Field(default=False, description="Load UI layout")


class GetBlenderInfoInput(BaseModel):
    """Get Blender info input"""

    pass


class ConnectionStatusInput(BaseModel):
    """Connection status query input"""

    pass


class UndoInput(BaseModel):
    """Undo input"""

    steps: int = Field(default=1, description="Number of undo steps", ge=1, le=100)


class RedoInput(BaseModel):
    """Redo input"""

    steps: int = Field(default=1, description="Number of redo steps", ge=1, le=100)


# ==================== Tool Registration ====================


def register_utility_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register utility tools"""

    @mcp.tool(
        name="blender_execute_python",
        annotations={
            "title": "Execute Python Code",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_execute_python(params: ExecutePythonInput) -> str:
        """Execute Python code in Blender.

        Note: Use with caution as this may modify the scene or perform dangerous operations.

        Args:
            params: Python code and timeout

        Returns:
            Execution result
        """
        result = await server.execute_command(
            "utility", "execute_python", {"code": params.code, "timeout": params.timeout}
        )

        if result.get("success"):
            output = result.get("data", {}).get("output", "")
            return (
                f"Code executed successfully\n{output}" if output else "Code executed successfully"
            )
        else:
            return f"Execution failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_get_viewport_screenshot",
        annotations={
            "title": "Get Viewport Screenshot",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_get_viewport_screenshot(params: ViewportScreenshotInput) -> str:
        """Get a screenshot of the current viewport.

        Args:
            params: Output path and dimensions

        Returns:
            Screenshot path
        """
        result = await server.execute_command(
            "utility",
            "viewport_screenshot",
            {"output_path": params.output_path, "width": params.width, "height": params.height},
        )

        if result.get("success"):
            path = result.get("data", {}).get("output_path", "temporary file")
            return f"Viewport screenshot saved: {path}"
        else:
            return f"Screenshot failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_file_save",
        annotations={
            "title": "Save File",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_file_save(params: FileSaveInput) -> str:
        """Save the Blender file.

        Args:
            params: File path and compression options

        Returns:
            Save result
        """
        result = await server.execute_command(
            "utility", "file_save", {"filepath": params.filepath, "compress": params.compress}
        )

        if result.get("success"):
            path = result.get("data", {}).get("filepath", params.filepath or "current file")
            return f"File saved: {path}"
        else:
            return f"Save failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_file_open",
        annotations={
            "title": "Open File",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_file_open(params: FileOpenInput) -> str:
        """Open a Blender file.

        Note: This will replace the current scene; unsaved changes will be lost.

        Args:
            params: File path

        Returns:
            Open result
        """
        result = await server.execute_command(
            "utility", "file_open", {"filepath": params.filepath, "load_ui": params.load_ui}
        )

        if result.get("success"):
            return f"File opened: {params.filepath}"
        else:
            return f"Failed to open file: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_get_info",
        annotations={
            "title": "Get Blender Info",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_get_info(params: GetBlenderInfoInput) -> str:
        """Get Blender version and status information.

        Returns:
            Blender info
        """
        result = await server.execute_command("utility", "get_info", {})

        if result.get("success"):
            data = result.get("data", {})
            lines = ["# Blender Info", ""]
            lines.append(f"- **Version**: {data.get('version', 'Unknown')}")
            lines.append(f"- **Version String**: {data.get('version_string', 'Unknown')}")
            lines.append(f"- **Current File**: {data.get('filepath', 'Unsaved')}")
            lines.append(f"- **Current Scene**: {data.get('scene', 'Unknown')}")
            lines.append(f"- **Object Count**: {data.get('objects_count', 0)}")
            return "\n".join(lines)
        else:
            return f"Failed to get info: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_undo",
        annotations={
            "title": "Undo",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_undo(params: UndoInput) -> str:
        """Undo operations.

        Args:
            params: Number of undo steps

        Returns:
            Undo result
        """
        result = await server.execute_command("utility", "undo", {"steps": params.steps})

        if result.get("success"):
            return f"Undone {params.steps} step(s)"
        else:
            return f"Undo failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_redo",
        annotations={
            "title": "Redo",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_redo(params: RedoInput) -> str:
        """Redo operations.

        Args:
            params: Number of redo steps

        Returns:
            Redo result
        """
        result = await server.execute_command("utility", "redo", {"steps": params.steps})

        if result.get("success"):
            return f"Redone {params.steps} step(s)"
        else:
            return f"Redo failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_connection_status",
        annotations={
            "title": "Query Connection Status",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_connection_status(params: ConnectionStatusInput) -> str:
        """Query the current connection status and statistics with Blender.

        Can be used to diagnose connection issues and confirm whether Blender is online.

        Returns:
            Connection status information
        """
        conn = server.connection
        stats = conn.stats

        lines = ["# Blender Connection Status", ""]
        lines.append(f"- **Status**: {'Connected' if stats['connected'] else 'Disconnected'}")
        lines.append(f"- **Address**: {stats['host']}:{stats['port']}")
        lines.append(f"- **Total Commands**: {stats['total_commands']}")
        lines.append(f"- **Failed Commands**: {stats['failed_commands']}")
        lines.append(f"- **Reconnection Count**: {stats['reconnect_count']}")
        lines.append(f"- **Pending Requests**: {stats['pending_requests']}")

        if stats["connected"]:
            try:
                info = await conn.get_blender_info()
                lines.append("")
                lines.append("## Blender Info")
                lines.append(f"- **Version**: {info.get('version_string', 'Unknown')}")
                lines.append(f"- **Scene**: {info.get('scene', 'Unknown')}")
                lines.append(f"- **Object Count**: {info.get('objects_count', 0)}")
            except Exception:
                lines.append("\n*Unable to get detailed Blender info*")

        return "\n".join(lines)
