"""
Blender MCP Server - 主服务器模块

实现 MCP 协议，注册所有工具，处理请求和响应。

工具模块配置:
- 编辑 tools_config.py 中的 TOOL_PROFILE 来控制启用的工具数量
- "skill": ~31个工具 + 按需加载 (推荐)
- "minimal": ~30个工具 (仅核心功能)
- "focused": ~82个工具
- "standard": ~146个工具
- "full": ~319个工具 (所有功能)
"""

import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from blender_mcp.connection import BlenderConnection
from blender_mcp.tools_config import get_enabled_modules, MODULE_REGISTRY, TOOL_PROFILE

# 动态导入启用的工具模块
import importlib

logger = logging.getLogger(__name__)


class BlenderMCPServer:
    """Blender MCP 服务器
    
    负责：
    - 初始化 MCP 服务器
    - 注册所有工具
    - 管理 Blender 连接
    - 处理请求和响应
    """
    
    def __init__(
        self,
        blender_host: str = "127.0.0.1",
        blender_port: int = 9876,
        name: str = "blender_mcp"
    ):
        """初始化服务器
        
        Args:
            blender_host: Blender 插件服务器主机
            blender_port: Blender 插件服务器端口
            name: MCP 服务器名称
        """
        self.blender_host = blender_host
        self.blender_port = blender_port
        
        # 创建 MCP 服务器实例
        self.mcp = FastMCP(name)
        
        # Blender 连接（延迟初始化）
        self._connection: Optional[BlenderConnection] = None
        
        # Skill 管理器（延迟初始化，仅在 skill profile 下使用）
        self._skill_manager = None
        
        # 注册所有工具
        self._register_tools()
        
        logger.info(f"Blender MCP 服务器初始化完成: {name}")
    
    @property
    def skill_manager(self):
        """获取 Skill 管理器实例（仅 skill profile 下可用）"""
        if self._skill_manager is None:
            from blender_mcp.skill_manager import SkillManager
            self._skill_manager = SkillManager(self)
        return self._skill_manager
    
    @property
    def connection(self) -> BlenderConnection:
        """获取 Blender 连接实例"""
        if self._connection is None:
            self._connection = BlenderConnection(
                host=self.blender_host,
                port=self.blender_port
            )
        return self._connection
    
    def _register_tools(self) -> None:
        """注册启用的 MCP 工具模块
        
        根据 tools_config.py 中的 TOOL_PROFILE 设置动态加载模块。
        可以通过修改 TOOL_PROFILE 来控制工具数量：
        - "skill": ~31个工具 + 按需加载 (推荐)
        - "minimal": ~30个工具
        - "focused": ~82个工具
        - "standard": ~146个工具
        - "full": ~319个工具
        """
        enabled_modules = get_enabled_modules()
        loaded_count = 0
        
        logger.info(f"工具配置: {TOOL_PROFILE} (启用 {len(enabled_modules)} 个模块)")
        
        for module_name in enabled_modules:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"未知模块: {module_name}")
                continue
            
            register_func_name = MODULE_REGISTRY[module_name]
            
            try:
                # 动态导入模块
                tool_module = importlib.import_module(f"blender_mcp.tools.{module_name}")
                register_func = getattr(tool_module, register_func_name)
                
                # 调用注册函数
                register_func(self.mcp, self)
                loaded_count += 1
                logger.debug(f"已加载模块: {module_name}")
                
            except ImportError as e:
                logger.warning(f"无法导入模块 {module_name}: {e}")
            except AttributeError as e:
                logger.warning(f"模块 {module_name} 缺少注册函数 {register_func_name}: {e}")
            except Exception as e:
                logger.warning(f"加载模块 {module_name} 失败: {e}")
        
        logger.info(f"工具注册完成: 加载了 {loaded_count}/{len(enabled_modules)} 个模块")
    
    async def execute_command(
        self,
        category: str,
        action: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """执行 Blender 命令
        
        Args:
            category: 命令类别（如 scene, object, modeling 等）
            action: 具体操作
            params: 操作参数
            
        Returns:
            执行结果字典
        """
        try:
            # 确保连接
            if not self.connection.connected:
                await self.connection.connect()
            
            # 发送命令并等待响应
            result = await self.connection.send_command(category, action, params)
            
            return result
            
        except Exception as e:
            logger.error(f"命令执行失败: {category}.{action} - {e}")
            return {
                "success": False,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e)
                }
            }
    
    def run_stdio(self) -> None:
        """以 stdio 模式运行服务器（同步方法）"""
        logger.info("启动 stdio 传输")
        self.mcp.run(transport="stdio")
    
    def run_http(self, port: int = 8080) -> None:
        """以 HTTP 模式运行服务器（同步方法）
        
        Args:
            port: HTTP 服务端口
        """
        logger.info(f"启动 HTTP 传输，端口: {port}")
        # FastMCP 的 run() 不接收端口参数，需要通过 settings 注入
        self.mcp.settings.port = port
        self.mcp.run(transport="streamable-http")
    
    async def shutdown(self) -> None:
        """关闭服务器"""
        if self._connection:
            await self._connection.disconnect()
        logger.info("服务器已关闭")
