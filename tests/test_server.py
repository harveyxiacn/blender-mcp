"""Tests for BlenderMCPServer compatibility helpers."""

from unittest.mock import AsyncMock

import pytest

from blender_mcp.server import BlenderMCPServer


@pytest.mark.asyncio
async def test_send_command_alias_calls_execute_command() -> None:
    server = BlenderMCPServer.__new__(BlenderMCPServer)
    server.execute_command = AsyncMock(return_value={"success": True, "data": {"ok": 1}})

    result = await BlenderMCPServer.send_command(server, "scene", "list", {"limit": 1})

    assert result == {"success": True, "data": {"ok": 1}}
    server.execute_command.assert_awaited_once_with("scene", "list", {"limit": 1})
