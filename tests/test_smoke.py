"""Basic smoke tests for blender-mcp core modules."""

from unittest.mock import patch

from blender_mcp.server import BlenderMCPServer
from blender_mcp.tools_config import get_enabled_modules


def test_enabled_modules_not_empty() -> None:
    """Configured profile should always load at least one module."""
    enabled = get_enabled_modules()
    assert enabled


def test_run_http_applies_port_to_fastmcp_settings() -> None:
    """run_http should forward the provided port into FastMCP settings."""
    server = BlenderMCPServer()
    with patch.object(server.mcp, "run", return_value=None) as mocked_run:
        server.run_http(9123)

    assert server.mcp.settings.port == 9123
    mocked_run.assert_called_once_with(transport="streamable-http")
