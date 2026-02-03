"""
面板模块
"""

import bpy

from .. import server


class MCP_PT_MainPanel(bpy.types.Panel):
    """MCP 主面板"""
    bl_label = "Blender MCP"
    bl_idname = "MCP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MCP'
    
    def draw(self, context):
        layout = self.layout
        
        # 服务状态
        box = layout.box()
        row = box.row()
        row.label(text="服务状态:")
        
        if server.is_running():
            row.label(text="运行中", icon='PLAY')
            box.label(text=f"端口: {server.get_port()}")
        else:
            row.label(text="已停止", icon='PAUSE')
        
        # 控制按钮
        layout.separator()
        
        if server.is_running():
            layout.operator("mcp.stop_server", text="停止服务", icon='CANCEL')
            layout.operator("mcp.restart_server", text="重启服务", icon='FILE_REFRESH')
        else:
            layout.operator("mcp.start_server", text="启动服务", icon='PLAY')
        
        # 信息
        layout.separator()
        box = layout.box()
        box.label(text="使用说明:", icon='INFO')
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. 启动 MCP 服务")
        col.label(text="2. 在 IDE 中配置 MCP")
        col.label(text="3. 通过 AI 助手控制 Blender")


class MCP_PT_InfoPanel(bpy.types.Panel):
    """MCP 信息面板"""
    bl_label = "场景信息"
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
        col.label(text=f"场景: {scene.name}")
        col.label(text=f"对象: {len(scene.objects)}")
        col.label(text=f"帧范围: {scene.frame_start} - {scene.frame_end}")
        col.label(text=f"当前帧: {scene.frame_current}")


classes = [
    MCP_PT_MainPanel,
    MCP_PT_InfoPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
