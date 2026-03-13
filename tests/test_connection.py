"""Tests for BlenderConnection."""

import asyncio
import contextlib

import pytest

from blender_mcp.connection import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    BlenderConnection,
    BlenderConnectionError,
)


class TestBlenderConnectionInit:
    def test_defaults(self) -> None:
        conn = BlenderConnection()
        assert conn.host == DEFAULT_HOST
        assert conn.port == DEFAULT_PORT
        assert conn.auto_reconnect is True
        assert not conn.connected

    def test_custom_params(self) -> None:
        conn = BlenderConnection(host="10.0.0.1", port=1234, auto_reconnect=False)
        assert conn.host == "10.0.0.1"
        assert conn.port == 1234
        assert conn.auto_reconnect is False

    def test_stats_initial(self) -> None:
        conn = BlenderConnection()
        stats = conn.stats
        assert stats["connected"] is False
        assert stats["total_commands"] == 0
        assert stats["failed_commands"] == 0
        assert stats["reconnect_count"] == 0


class TestBlenderConnectionConnect:
    @pytest.mark.asyncio
    async def test_connect_refused(self) -> None:
        conn = BlenderConnection(port=19999, max_retries=1, auto_reconnect=False)
        with pytest.raises(BlenderConnectionError, match="Cannot connect"):
            await conn.connect()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self) -> None:
        conn = BlenderConnection()
        conn._connected = True
        await conn.connect()

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self) -> None:
        conn = BlenderConnection()
        await conn.disconnect()


class TestBlenderConnectionSendCommand:
    @pytest.mark.asyncio
    async def test_send_without_connection_raises(self) -> None:
        conn = BlenderConnection(port=19999, max_retries=1, auto_reconnect=False)
        with pytest.raises(BlenderConnectionError):
            await conn.send_command("scene", "list", {})

    @pytest.mark.asyncio
    async def test_stats_increment_on_send(self) -> None:
        conn = BlenderConnection(port=19999, max_retries=1, auto_reconnect=False)
        with contextlib.suppress(BlenderConnectionError):
            await conn.send_command("scene", "list", {})
        assert conn.stats["total_commands"] == 1


class TestHandleResponse:
    @pytest.mark.asyncio
    async def test_matching_response(self) -> None:
        conn = BlenderConnection()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        conn._pending_requests["test-id"] = future

        await conn._handle_response({"id": "test-id", "success": True, "data": {}})

        assert future.done()
        assert future.result() == {"id": "test-id", "success": True, "data": {}}

    @pytest.mark.asyncio
    async def test_unmatched_response(self) -> None:
        conn = BlenderConnection()
        await conn._handle_response({"id": "unknown-id", "success": True})
