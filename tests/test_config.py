"""Tests for config module."""

import os
from unittest.mock import patch


def test_default_values() -> None:
    from blender_mcp import config

    assert os.environ.get("BLENDER_MCP_HOST", "127.0.0.1") == config.BLENDER_HOST
    assert isinstance(config.BLENDER_PORT, int)
    assert isinstance(config.COMMAND_TIMEOUT, float)


def test_env_override() -> None:
    env = {
        "BLENDER_MCP_HOST": "192.168.1.100",
        "BLENDER_MCP_PORT": "5555",
        "BLENDER_MCP_TIMEOUT": "60.0",
        "BLENDER_MCP_AUTO_RECONNECT": "false",
    }
    with patch.dict(os.environ, env):
        import importlib

        from blender_mcp import config

        importlib.reload(config)

        assert config.BLENDER_HOST == "192.168.1.100"
        assert config.BLENDER_PORT == 5555
        assert config.COMMAND_TIMEOUT == 60.0
        assert config.AUTO_RECONNECT is False

    importlib.reload(config)
