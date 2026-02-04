"""
Blender MCP Server - 主服务器模块

实现 MCP 协议，注册所有工具，处理请求和响应。
"""

import asyncio
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from blender_mcp.connection import BlenderConnection
from blender_mcp.tools import (
    register_scene_tools,
    register_object_tools,
    register_modeling_tools,
    register_material_tools,
    register_lighting_tools,
    register_camera_tools,
    register_animation_tools,
    register_character_tools,
    register_rigging_tools,
    register_render_tools,
    register_utility_tools,
    register_export_tools,
    register_character_template_tools,
    register_auto_rig_tools,
    register_animation_preset_tools,
    register_physics_tools,
    register_scene_advanced_tools,
    register_batch_tools,
    register_curve_tools,
    register_uv_tools,
    register_node_tools,
    register_compositor_tools,
    register_video_editing_tools,
    register_sculpting_tools,
    register_texture_painting_tools,
    register_grease_pencil_tools,
    register_simulation_tools,
    register_hair_tools,
    register_asset_tools,
    register_addon_tools,
    register_world_tools,
    register_constraint_tools,
    register_mocap_tools,
    register_preferences_tools,
    register_external_tools,
    register_ai_assist_tools,
    register_versioning_tools,
    register_ai_generation_tools,
    register_vr_ar_tools,
    register_substance_tools,
    register_zbrush_tools,
    register_cloud_render_tools,
    register_collaboration_tools,
)

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
        
        # 注册所有工具
        self._register_tools()
        
        logger.info(f"Blender MCP 服务器初始化完成: {name}")
    
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
        """注册所有 MCP 工具"""
        # 场景管理工具
        register_scene_tools(self.mcp, self)
        
        # 对象操作工具
        register_object_tools(self.mcp, self)
        
        # 建模工具
        register_modeling_tools(self.mcp, self)
        
        # 材质工具
        register_material_tools(self.mcp, self)
        
        # 灯光工具
        register_lighting_tools(self.mcp, self)
        
        # 相机工具
        register_camera_tools(self.mcp, self)
        
        # 动画工具
        register_animation_tools(self.mcp, self)
        
        # 角色系统工具
        register_character_tools(self.mcp, self)
        
        # 骨骼绑定工具
        register_rigging_tools(self.mcp, self)
        
        # 渲染工具
        register_render_tools(self.mcp, self)
        
        # 实用工具
        register_utility_tools(self.mcp, self)
        
        # 导出工具
        register_export_tools(self.mcp, self)
        
        # 角色模板工具
        register_character_template_tools(self.mcp, self)
        
        # 自动骨骼绑定工具
        register_auto_rig_tools(self.mcp, self)
        
        # 预设动画工具
        register_animation_preset_tools(self.mcp, self)
        
        # 物理模拟工具
        register_physics_tools(self.mcp, self)
        
        # 场景增强工具
        register_scene_advanced_tools(self.mcp, self)
        
        # 批量处理工具
        register_batch_tools(self.mcp, self)
        
        # 曲线建模工具
        register_curve_tools(self.mcp, self)
        
        # UV映射工具
        register_uv_tools(self.mcp, self)
        
        # 节点系统工具
        register_node_tools(self.mcp, self)
        
        # 合成器工具
        register_compositor_tools(self.mcp, self)
        
        # 视频编辑工具
        register_video_editing_tools(self.mcp, self)
        
        # 雕刻工具
        register_sculpting_tools(self.mcp, self)
        
        # 纹理绘制工具
        register_texture_painting_tools(self.mcp, self)
        
        # 油笔/2D动画工具
        register_grease_pencil_tools(self.mcp, self)
        
        # 高级模拟工具（流体、烟雾、海洋）
        register_simulation_tools(self.mcp, self)
        
        # 毛发系统工具
        register_hair_tools(self.mcp, self)
        
        # 资产管理工具
        register_asset_tools(self.mcp, self)
        
        # 插件管理工具
        register_addon_tools(self.mcp, self)
        
        # 世界/环境工具
        register_world_tools(self.mcp, self)
        
        # 约束系统工具
        register_constraint_tools(self.mcp, self)
        
        # 动作捕捉工具
        register_mocap_tools(self.mcp, self)
        
        # 偏好设置工具
        register_preferences_tools(self.mcp, self)
        
        # 外部集成工具
        register_external_tools(self.mcp, self)
        
        # AI辅助工具
        register_ai_assist_tools(self.mcp, self)
        
        # 版本控制工具
        register_versioning_tools(self.mcp, self)
        
        # AI生成工具
        register_ai_generation_tools(self.mcp, self)
        
        # VR/AR工具
        register_vr_ar_tools(self.mcp, self)
        
        # Substance连接工具
        register_substance_tools(self.mcp, self)
        
        # ZBrush连接工具
        register_zbrush_tools(self.mcp, self)
        
        # 云渲染工具
        register_cloud_render_tools(self.mcp, self)
        
        # 协作工具
        register_collaboration_tools(self.mcp, self)
        
        logger.info("所有工具注册完成")
    
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
        self.mcp.run(transport="streamable-http")
    
    async def shutdown(self) -> None:
        """关闭服务器"""
        if self._connection:
            await self._connection.disconnect()
        logger.info("服务器已关闭")
