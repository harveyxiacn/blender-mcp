"""
Operators module
"""

import bpy
from bpy.props import IntProperty

from .. import server


class MCP_OT_StartServer(bpy.types.Operator):
    """Start the MCP server"""

    bl_idname = "mcp.start_server"
    bl_label = "Start MCP Server"
    bl_description = "Start the MCP communication server"

    def execute(self, context):
        prefs = context.preferences.addons.get("blender_mcp_addon")
        port = prefs.preferences.port if prefs else 9876

        if server.start_server(port=port):
            self.report({"INFO"}, f"MCP server started on port: {port}")
        else:
            self.report({"ERROR"}, "Failed to start MCP server")

        return {"FINISHED"}


class MCP_OT_StopServer(bpy.types.Operator):
    """Stop the MCP server"""

    bl_idname = "mcp.stop_server"
    bl_label = "Stop MCP Server"
    bl_description = "Stop the MCP communication server"

    def execute(self, context):
        server.stop_server()
        self.report({"INFO"}, "MCP server stopped")
        return {"FINISHED"}


class MCP_OT_RestartServer(bpy.types.Operator):
    """Restart the MCP server"""

    bl_idname = "mcp.restart_server"
    bl_label = "Restart MCP Server"
    bl_description = "Restart the MCP communication server"

    def execute(self, context):
        server.stop_server()

        prefs = context.preferences.addons.get("blender_mcp_addon")
        port = prefs.preferences.port if prefs else 9876

        if server.start_server(port=port):
            self.report({"INFO"}, f"MCP server restarted on port: {port}")
        else:
            self.report({"ERROR"}, "Failed to restart MCP server")

        return {"FINISHED"}


class MCP_OT_HotReload(bpy.types.Operator):
    """Hot Reload - Update addon from source directory"""

    bl_idname = "mcp.hot_reload"
    bl_label = "Hot Reload"
    bl_description = "Update addon code from the development source directory and reload"

    def execute(self, context):
        # Import hot reload function
        from .. import hot_reload

        success, message = hot_reload()

        if success:
            self.report({"INFO"}, message)
        else:
            self.report({"ERROR"}, message)

        return {"FINISHED"}

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


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
