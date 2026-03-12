"""
Blender MCP Server - Main Server Module

Implements the MCP protocol, registers all tools, and handles requests and responses.

Tool module configuration:
- Edit TOOL_PROFILE in tools_config.py to control the number of enabled tools
- "skill": ~31 tools + on-demand loading (recommended)
- "minimal": ~30 tools (core functionality only)
- "focused": ~82 tools
- "standard": ~146 tools
- "full": ~319 tools (all features)
"""

import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from blender_mcp.connection import BlenderConnection
from blender_mcp.tools_config import get_enabled_modules, MODULE_REGISTRY, TOOL_PROFILE
from blender_mcp import config

# Dynamically import enabled tool modules
import importlib

logger = logging.getLogger(__name__)


class BlenderMCPServer:
    """Blender MCP Server

    Responsible for:
    - Initializing the MCP server
    - Registering all tools
    - Managing the Blender connection
    - Handling requests and responses
    """
    
    def __init__(
        self,
        blender_host: str = config.BLENDER_HOST,
        blender_port: int = config.BLENDER_PORT,
        name: str = "blender_mcp"
    ):
        """Initialize the server

        Args:
            blender_host: Blender addon server host
            blender_port: Blender addon server port
            name: MCP server name
        """
        self.blender_host = blender_host
        self.blender_port = blender_port
        
        # Create MCP server instance
        self.mcp = FastMCP(name)

        # Blender connection (lazy initialization)
        self._connection: Optional[BlenderConnection] = None

        # Skill manager (lazy initialization, only used in skill profile)
        self._skill_manager = None

        # Register all tools
        self._register_tools()

        logger.info(f"Blender MCP server initialized: {name}")
    
    @property
    def skill_manager(self):
        """Get the skill manager instance (only available in skill profile)"""
        if self._skill_manager is None:
            from blender_mcp.skill_manager import SkillManager
            self._skill_manager = SkillManager(self)
        return self._skill_manager
    
    @property
    def connection(self) -> BlenderConnection:
        """Get the Blender connection instance"""
        if self._connection is None:
            self._connection = BlenderConnection(
                host=self.blender_host,
                port=self.blender_port
            )
        return self._connection
    
    def _register_tools(self) -> None:
        """Register enabled MCP tool modules

        Dynamically loads modules based on the TOOL_PROFILE setting in tools_config.py.
        Control the number of tools by modifying TOOL_PROFILE:
        - "skill": ~31 tools + on-demand loading (recommended)
        - "minimal": ~30 tools
        - "focused": ~82 tools
        - "standard": ~146 tools
        - "full": ~319 tools
        """
        enabled_modules = get_enabled_modules()
        loaded_count = 0
        
        logger.info(f"Tool profile: {TOOL_PROFILE} ({len(enabled_modules)} modules enabled)")
        
        for module_name in enabled_modules:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Unknown module: {module_name}")
                continue
            
            register_func_name = MODULE_REGISTRY[module_name]
            
            try:
                # Dynamically import module
                tool_module = importlib.import_module(f"blender_mcp.tools.{module_name}")
                register_func = getattr(tool_module, register_func_name)

                # Call register function
                register_func(self.mcp, self)
                loaded_count += 1
                logger.debug(f"Loaded module: {module_name}")

            except ImportError as e:
                logger.warning(f"Cannot import module {module_name}: {e}")
            except AttributeError as e:
                logger.warning(f"Module {module_name} missing register function {register_func_name}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load module {module_name}: {e}")

        logger.info(f"Tool registration complete: loaded {loaded_count}/{len(enabled_modules)} modules")
    
    async def execute_command(
        self,
        category: str,
        action: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a Blender command

        Args:
            category: Command category (e.g. scene, object, modeling, etc.)
            action: Specific operation
            params: Operation parameters

        Returns:
            Result dictionary
        """
        try:
            # Ensure connection
            if not self.connection.connected:
                await self.connection.connect()

            # Send command and wait for response
            result = await self.connection.send_command(category, action, params)

            return result

        except Exception as e:
            logger.error(f"Command execution failed: {category}.{action} - {e}")
            return {
                "success": False,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e)
                }
            }

    async def send_command(
        self,
        category: str,
        action: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """Backward-compatible alias for tool modules using send_command()."""
        return await self.execute_command(category, action, params)
    
    def run_stdio(self) -> None:
        """Run the server in stdio mode (synchronous method)"""
        logger.info("Starting stdio transport")
        self.mcp.run(transport="stdio")

    def run_http(self, port: int = 8080) -> None:
        """Run the server in HTTP mode (synchronous method)

        Args:
            port: HTTP server port
        """
        logger.info(f"Starting HTTP transport on port: {port}")
        # FastMCP's run() does not accept a port parameter; inject via settings
        self.mcp.settings.port = port
        self.mcp.run(transport="streamable-http")

    async def shutdown(self) -> None:
        """Shut down the server"""
        if self._connection:
            await self._connection.disconnect()
        logger.info("Server shut down")
