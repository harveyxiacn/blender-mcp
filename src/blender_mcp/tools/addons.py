"""
插件管理工具

提供Blender插件管理的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class AddonEnableInput(BaseModel):
    """启用插件"""
    addon_name: str = Field(..., description="插件模块名称")


class AddonDisableInput(BaseModel):
    """禁用插件"""
    addon_name: str = Field(..., description="插件模块名称")


class AddonInstallInput(BaseModel):
    """安装插件"""
    filepath: str = Field(..., description="插件文件路径 (.py 或 .zip)")
    overwrite: bool = Field(True, description="覆盖已有插件")
    enable: bool = Field(True, description="安装后启用")


class AddonInfoInput(BaseModel):
    """获取插件信息"""
    addon_name: str = Field(..., description="插件模块名称")


# ============ 工具注册 ============

def register_addon_tools(mcp: FastMCP, server):
    """注册插件管理工具"""
    
    @mcp.tool()
    async def blender_addon_list() -> Dict[str, Any]:
        """
        列出所有已安装的插件
        
        Returns:
            已安装插件列表，包含启用状态
        """
        return await server.send_command("addons", "list", {})
    
    @mcp.tool()
    async def blender_addon_enable(
        addon_name: str
    ) -> Dict[str, Any]:
        """
        启用插件
        
        Args:
            addon_name: 插件模块名称
        """
        params = AddonEnableInput(addon_name=addon_name)
        return await server.send_command("addons", "enable", params.model_dump())
    
    @mcp.tool()
    async def blender_addon_disable(
        addon_name: str
    ) -> Dict[str, Any]:
        """
        禁用插件
        
        Args:
            addon_name: 插件模块名称
        """
        params = AddonDisableInput(addon_name=addon_name)
        return await server.send_command("addons", "disable", params.model_dump())
    
    @mcp.tool()
    async def blender_addon_install(
        filepath: str,
        overwrite: bool = True,
        enable: bool = True
    ) -> Dict[str, Any]:
        """
        安装插件
        
        Args:
            filepath: 插件文件路径 (.py 或 .zip)
            overwrite: 覆盖已有插件
            enable: 安装后启用
        """
        params = AddonInstallInput(
            filepath=filepath,
            overwrite=overwrite,
            enable=enable
        )
        return await server.send_command("addons", "install", params.model_dump())
    
    @mcp.tool()
    async def blender_addon_info(
        addon_name: str
    ) -> Dict[str, Any]:
        """
        获取插件详细信息
        
        Args:
            addon_name: 插件模块名称
        """
        params = AddonInfoInput(addon_name=addon_name)
        return await server.send_command("addons", "info", params.model_dump())
