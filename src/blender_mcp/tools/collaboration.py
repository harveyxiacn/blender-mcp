"""
Real-time Collaboration Tools

MCP tools providing simplified scene synchronization and collaboration features.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class CollabHostInput(BaseModel):
    """Start collaboration session"""
    session_name: str = Field(..., description="Session name")
    port: int = Field(9877, description="Port")
    password: Optional[str] = Field(None, description="Password (optional)")


class CollabJoinInput(BaseModel):
    """Join collaboration session"""
    host: str = Field(..., description="Host address")
    port: int = Field(9877, description="Port")
    password: Optional[str] = Field(None, description="Password")
    username: str = Field("Guest", description="Username")


class CollabLockInput(BaseModel):
    """Lock objects"""
    object_names: List[str] = Field(..., description="Object name list")


class CollabChatInput(BaseModel):
    """Send message"""
    message: str = Field(..., description="Message content")


# ============ Tool Registration ============

def register_collaboration_tools(mcp: FastMCP, server):
    """Register collaboration tools"""

    @mcp.tool()
    async def blender_collab_host(
        session_name: str,
        port: int = 9877,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a collaboration session as host

        Args:
            session_name: Session name
            port: Port number
            password: Access password (optional)
        """
        params = CollabHostInput(
            session_name=session_name,
            port=port,
            password=password
        )
        return await server.send_command("collaboration", "host", params.model_dump())

    @mcp.tool()
    async def blender_collab_join(
        host: str,
        port: int = 9877,
        password: Optional[str] = None,
        username: str = "Guest"
    ) -> Dict[str, Any]:
        """
        Join a collaboration session

        Args:
            host: Host address
            port: Port number
            password: Password
            username: Username
        """
        params = CollabJoinInput(
            host=host,
            port=port,
            password=password,
            username=username
        )
        return await server.send_command("collaboration", "join", params.model_dump())

    @mcp.tool()
    async def blender_collab_leave() -> Dict[str, Any]:
        """
        Leave the collaboration session
        """
        return await server.send_command("collaboration", "leave", {})

    @mcp.tool()
    async def blender_collab_sync() -> Dict[str, Any]:
        """
        Synchronize scene state
        """
        return await server.send_command("collaboration", "sync", {})

    @mcp.tool()
    async def blender_collab_lock(
        object_names: List[str]
    ) -> Dict[str, Any]:
        """
        Lock objects (prevent other users from editing)

        Args:
            object_names: List of object names to lock
        """
        params = CollabLockInput(object_names=object_names)
        return await server.send_command("collaboration", "lock", params.model_dump())

    @mcp.tool()
    async def blender_collab_unlock(
        object_names: List[str]
    ) -> Dict[str, Any]:
        """
        Unlock objects

        Args:
            object_names: List of object names to unlock
        """
        return await server.send_command("collaboration", "unlock", {
            "object_names": object_names
        })

    @mcp.tool()
    async def blender_collab_chat(
        message: str
    ) -> Dict[str, Any]:
        """
        Send a collaboration message

        Args:
            message: Message content
        """
        params = CollabChatInput(message=message)
        return await server.send_command("collaboration", "chat", params.model_dump())

    @mcp.tool()
    async def blender_collab_status() -> Dict[str, Any]:
        """
        Get collaboration status
        """
        return await server.send_command("collaboration", "status", {})

    @mcp.tool()
    async def blender_collab_users() -> Dict[str, Any]:
        """
        List current collaboration users
        """
        return await server.send_command("collaboration", "users", {})
