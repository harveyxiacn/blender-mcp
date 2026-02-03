"""
实时协作工具

提供简化的场景同步协作功能的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class CollabHostInput(BaseModel):
    """启动协作会话"""
    session_name: str = Field(..., description="会话名称")
    port: int = Field(9877, description="端口")
    password: Optional[str] = Field(None, description="密码（可选）")


class CollabJoinInput(BaseModel):
    """加入协作会话"""
    host: str = Field(..., description="主机地址")
    port: int = Field(9877, description="端口")
    password: Optional[str] = Field(None, description="密码")
    username: str = Field("Guest", description="用户名")


class CollabLockInput(BaseModel):
    """锁定对象"""
    object_names: List[str] = Field(..., description="对象名称列表")


class CollabChatInput(BaseModel):
    """发送消息"""
    message: str = Field(..., description="消息内容")


# ============ 工具注册 ============

def register_collaboration_tools(mcp: FastMCP, server):
    """注册协作工具"""
    
    @mcp.tool()
    async def blender_collab_host(
        session_name: str,
        port: int = 9877,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        作为主机启动协作会话
        
        Args:
            session_name: 会话名称
            port: 端口号
            password: 访问密码（可选）
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
        加入协作会话
        
        Args:
            host: 主机地址
            port: 端口号
            password: 密码
            username: 用户名
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
        离开协作会话
        """
        return await server.send_command("collaboration", "leave", {})
    
    @mcp.tool()
    async def blender_collab_sync() -> Dict[str, Any]:
        """
        同步场景状态
        """
        return await server.send_command("collaboration", "sync", {})
    
    @mcp.tool()
    async def blender_collab_lock(
        object_names: List[str]
    ) -> Dict[str, Any]:
        """
        锁定对象（防止其他用户编辑）
        
        Args:
            object_names: 要锁定的对象名称列表
        """
        params = CollabLockInput(object_names=object_names)
        return await server.send_command("collaboration", "lock", params.model_dump())
    
    @mcp.tool()
    async def blender_collab_unlock(
        object_names: List[str]
    ) -> Dict[str, Any]:
        """
        解锁对象
        
        Args:
            object_names: 要解锁的对象名称列表
        """
        return await server.send_command("collaboration", "unlock", {
            "object_names": object_names
        })
    
    @mcp.tool()
    async def blender_collab_chat(
        message: str
    ) -> Dict[str, Any]:
        """
        发送协作消息
        
        Args:
            message: 消息内容
        """
        params = CollabChatInput(message=message)
        return await server.send_command("collaboration", "chat", params.model_dump())
    
    @mcp.tool()
    async def blender_collab_status() -> Dict[str, Any]:
        """
        获取协作状态
        """
        return await server.send_command("collaboration", "status", {})
    
    @mcp.tool()
    async def blender_collab_users() -> Dict[str, Any]:
        """
        列出当前协作用户
        """
        return await server.send_command("collaboration", "users", {})
