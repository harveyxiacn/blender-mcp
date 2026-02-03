"""
Blender MCP Addon - 插件入口

在 Blender 中启用 MCP 通信服务，接收并执行来自 MCP 服务器的命令。
"""

bl_info = {
    "name": "Blender MCP",
    "author": "Blender MCP Team",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Enable AI assistants to control Blender through MCP protocol",
    "category": "Interface",
    "doc_url": "https://github.com/your-username/blender-mcp",
    "tracker_url": "https://github.com/your-username/blender-mcp/issues",
}

import bpy
from bpy.props import IntProperty, BoolProperty, StringProperty

# 模块导入
from . import server
from . import operators
from . import panels


class BlenderMCPPreferences(bpy.types.AddonPreferences):
    """插件偏好设置"""
    bl_idname = __name__
    
    port: IntProperty(
        name="服务端口",
        description="MCP 通信服务端口",
        default=9876,
        min=1024,
        max=65535
    )
    
    auto_start: BoolProperty(
        name="自动启动",
        description="Blender 启动时自动启动 MCP 服务",
        default=True
    )
    
    log_level: StringProperty(
        name="日志级别",
        description="日志详细程度",
        default="INFO"
    )
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "port")
        layout.prop(self, "auto_start")
        layout.prop(self, "log_level")


# 所有需要注册的类
classes = [
    BlenderMCPPreferences,
]


def register():
    """注册插件"""
    # 注册类
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # 注册子模块
    operators.register()
    panels.register()
    
    # 自动启动服务
    prefs = bpy.context.preferences.addons.get(__name__)
    if prefs and prefs.preferences.auto_start:
        # 延迟启动，确保 Blender 完全初始化
        bpy.app.timers.register(
            lambda: _delayed_start(),
            first_interval=1.0
        )


def unregister():
    """注销插件"""
    # 停止服务
    server.stop_server()
    
    # 注销子模块
    panels.unregister()
    operators.unregister()
    
    # 注销类
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def _delayed_start():
    """延迟启动服务"""
    try:
        prefs = bpy.context.preferences.addons.get(__name__)
        if prefs:
            port = prefs.preferences.port
            server.start_server(port)
    except Exception as e:
        print(f"[MCP] 自动启动服务失败: {e}")
    return None  # 不重复执行


if __name__ == "__main__":
    register()
