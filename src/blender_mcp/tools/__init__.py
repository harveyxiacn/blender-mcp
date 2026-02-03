"""
Blender MCP 工具模块

提供所有 MCP 工具的注册函数。
"""

from blender_mcp.tools.scene import register_scene_tools
from blender_mcp.tools.object import register_object_tools
from blender_mcp.tools.modeling import register_modeling_tools
from blender_mcp.tools.material import register_material_tools
from blender_mcp.tools.lighting import register_lighting_tools
from blender_mcp.tools.camera import register_camera_tools
from blender_mcp.tools.animation import register_animation_tools
from blender_mcp.tools.character import register_character_tools
from blender_mcp.tools.rigging import register_rigging_tools
from blender_mcp.tools.render import register_render_tools
from blender_mcp.tools.utility import register_utility_tools
from blender_mcp.tools.export import register_export_tools
from blender_mcp.tools.character_templates import register_character_template_tools
from blender_mcp.tools.auto_rig import register_auto_rig_tools
from blender_mcp.tools.animation_presets import register_animation_preset_tools
from blender_mcp.tools.physics import register_physics_tools
from blender_mcp.tools.scene_advanced import register_scene_advanced_tools
from blender_mcp.tools.batch import register_batch_tools
from blender_mcp.tools.curves import register_curve_tools
from blender_mcp.tools.uv_mapping import register_uv_tools
from blender_mcp.tools.nodes import register_node_tools
from blender_mcp.tools.compositor import register_compositor_tools
from blender_mcp.tools.video_editing import register_video_editing_tools

__all__ = [
    "register_scene_tools",
    "register_object_tools",
    "register_modeling_tools",
    "register_material_tools",
    "register_lighting_tools",
    "register_camera_tools",
    "register_animation_tools",
    "register_character_tools",
    "register_rigging_tools",
    "register_render_tools",
    "register_utility_tools",
    "register_export_tools",
    "register_character_template_tools",
    "register_auto_rig_tools",
    "register_animation_preset_tools",
    "register_physics_tools",
    "register_scene_advanced_tools",
    "register_batch_tools",
    "register_curve_tools",
    "register_uv_tools",
    "register_node_tools",
    "register_compositor_tools",
    "register_video_editing_tools",
]
