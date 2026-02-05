"""
操作符模块
"""

import bpy
from bpy.props import IntProperty

from .. import server


class MCP_OT_StartServer(bpy.types.Operator):
    """启动 MCP 服务器"""
    bl_idname = "mcp.start_server"
    bl_label = "启动 MCP 服务器"
    bl_description = "启动 MCP 通信服务器"
    
    def execute(self, context):
        prefs = context.preferences.addons.get("blender_mcp_addon")
        port = prefs.preferences.port if prefs else 9876
        
        if server.start_server(port):
            self.report({'INFO'}, f"MCP 服务器已启动，端口: {port}")
        else:
            self.report({'ERROR'}, "MCP 服务器启动失败")
        
        return {'FINISHED'}


class MCP_OT_StopServer(bpy.types.Operator):
    """停止 MCP 服务器"""
    bl_idname = "mcp.stop_server"
    bl_label = "停止 MCP 服务器"
    bl_description = "停止 MCP 通信服务器"
    
    def execute(self, context):
        server.stop_server()
        self.report({'INFO'}, "MCP 服务器已停止")
        return {'FINISHED'}


class MCP_OT_RestartServer(bpy.types.Operator):
    """重启 MCP 服务器"""
    bl_idname = "mcp.restart_server"
    bl_label = "重启 MCP 服务器"
    bl_description = "重启 MCP 通信服务器"
    
    def execute(self, context):
        server.stop_server()
        
        prefs = context.preferences.addons.get("blender_mcp_addon")
        port = prefs.preferences.port if prefs else 9876
        
        if server.start_server(port):
            self.report({'INFO'}, f"MCP 服务器已重启，端口: {port}")
        else:
            self.report({'ERROR'}, "MCP 服务器重启失败")
        
        return {'FINISHED'}


class MCP_OT_HotReload(bpy.types.Operator):
    """热更新 - 从源代码目录更新addon"""
    bl_idname = "mcp.hot_reload"
    bl_label = "热更新"
    bl_description = "从开发源代码目录更新addon代码并重新加载"
    
    def execute(self, context):
        # 导入热更新函数
        from .. import hot_reload
        
        success, message = hot_reload()
        
        if success:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
        
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons.get("blender_mcp_addon")
        return prefs and prefs.preferences.dev_source_path


classes = [
    MCP_OT_StartServer,
    MCP_OT_StopServer,
    MCP_OT_RestartServer,
    MCP_OT_HotReload,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
