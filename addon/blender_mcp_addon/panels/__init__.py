"""
Panels module
"""

import bpy

from .. import server


class MCP_PT_MainPanel(bpy.types.Panel):
    """MCP Main Panel"""
    bl_label = "Blender MCP"
    bl_idname = "MCP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MCP'
    
    def draw(self, context):
        layout = self.layout
        
        # Server status
        box = layout.box()
        row = box.row()
        row.label(text="Server Status:")
        
        if server.is_running():
            row.label(text="Running", icon='PLAY')
            box.label(text=f"Port: {server.get_port()}")
        else:
            row.label(text="Stopped", icon='PAUSE')
        
        # Control buttons
        layout.separator()
        
        if server.is_running():
            layout.operator("mcp.stop_server", text="Stop Server", icon='CANCEL')
            layout.operator("mcp.restart_server", text="Restart Server", icon='FILE_REFRESH')
        else:
            layout.operator("mcp.start_server", text="Start Server", icon='PLAY')
        
        # Instructions
        layout.separator()
        box = layout.box()
        box.label(text="Instructions:", icon='INFO')
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. Start the MCP server")
        col.label(text="2. Configure MCP in your IDE")
        col.label(text="3. Control Blender via AI assistant")


class MCP_PT_DevPanel(bpy.types.Panel):
    """MCP Developer Panel"""
    bl_label = "Developer Tools"
    bl_idname = "MCP_PT_dev_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MCP'
    bl_parent_id = "MCP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when a dev source path is configured
        prefs = context.preferences.addons.get("blender_mcp_addon")
        return prefs and prefs.preferences.dev_source_path
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons.get("blender_mcp_addon")
        
        if prefs and prefs.preferences.dev_source_path:
            # Display source path
            box = layout.box()
            box.label(text="Source Directory:", icon='FILE_FOLDER')
            col = box.column(align=True)
            col.scale_y = 0.8
            # Wrap long paths across lines
            path = prefs.preferences.dev_source_path
            col.label(text=path if len(path) < 40 else f"...{path[-37:]}")
            
            # Hot reload button
            layout.separator()
            layout.operator("mcp.hot_reload", text="Hot Reload", icon='FILE_REFRESH')
            
            # Tip
            layout.separator()
            col = layout.column(align=True)
            col.scale_y = 0.7
            col.label(text="Tip: Click Hot Reload after editing source code")
            col.label(text="Changes apply without restarting Blender")


class MCP_PT_InfoPanel(bpy.types.Panel):
    """MCP Info Panel"""
    bl_label = "Scene Info"
    bl_idname = "MCP_PT_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MCP'
    bl_parent_id = "MCP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        col.label(text=f"Scene: {scene.name}")
        col.label(text=f"Objects: {len(scene.objects)}")
        col.label(text=f"Frame Range: {scene.frame_start} - {scene.frame_end}")
        col.label(text=f"Current Frame: {scene.frame_current}")


classes = [
    MCP_PT_MainPanel,
    MCP_PT_InfoPanel,
    MCP_PT_DevPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
