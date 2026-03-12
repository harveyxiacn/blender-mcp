"""
Blender MCP Unified Configuration

Centralized management of all configurable constants, with environment variable overrides.
"""

import os

BLENDER_HOST = os.environ.get("BLENDER_MCP_HOST", "127.0.0.1")
BLENDER_PORT = int(os.environ.get("BLENDER_MCP_PORT", "9876"))

MCP_HTTP_PORT = int(os.environ.get("BLENDER_MCP_HTTP_PORT", "8080"))

COMMAND_TIMEOUT = float(os.environ.get("BLENDER_MCP_TIMEOUT", "30.0"))
MAX_RETRIES = int(os.environ.get("BLENDER_MCP_MAX_RETRIES", "3"))
AUTO_RECONNECT = os.environ.get("BLENDER_MCP_AUTO_RECONNECT", "true").lower() in ("true", "1", "yes")
HEARTBEAT_INTERVAL = float(os.environ.get("BLENDER_MCP_HEARTBEAT_INTERVAL", "15.0"))

EXEC_MAX_CODE_SIZE = int(os.environ.get("BLENDER_MCP_MAX_CODE_SIZE", "100000"))

LOG_LEVEL = os.environ.get("BLENDER_MCP_LOG_LEVEL", "INFO").upper()
