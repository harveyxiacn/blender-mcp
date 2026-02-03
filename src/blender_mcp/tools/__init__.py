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
from blender_mcp.tools.sculpting import register_sculpting_tools
from blender_mcp.tools.texture_painting import register_texture_painting_tools
from blender_mcp.tools.grease_pencil import register_grease_pencil_tools
from blender_mcp.tools.simulation import register_simulation_tools
from blender_mcp.tools.hair import register_hair_tools
from blender_mcp.tools.assets import register_asset_tools
from blender_mcp.tools.addons import register_addon_tools
from blender_mcp.tools.world import register_world_tools
from blender_mcp.tools.constraints import register_constraint_tools
from blender_mcp.tools.mocap import register_mocap_tools
from blender_mcp.tools.preferences import register_preferences_tools
from blender_mcp.tools.external import register_external_tools
from blender_mcp.tools.ai_assist import register_ai_assist_tools
from blender_mcp.tools.versioning import register_versioning_tools
from blender_mcp.tools.ai_generation import register_ai_generation_tools
from blender_mcp.tools.vr_ar import register_vr_ar_tools
from blender_mcp.tools.substance import register_substance_tools
from blender_mcp.tools.zbrush import register_zbrush_tools
from blender_mcp.tools.cloud_render import register_cloud_render_tools
from blender_mcp.tools.collaboration import register_collaboration_tools

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
    "register_sculpting_tools",
    "register_texture_painting_tools",
    "register_grease_pencil_tools",
    "register_simulation_tools",
    "register_hair_tools",
    "register_asset_tools",
    "register_addon_tools",
    "register_world_tools",
    "register_constraint_tools",
    "register_mocap_tools",
    "register_preferences_tools",
    "register_external_tools",
    "register_ai_assist_tools",
    "register_versioning_tools",
    "register_ai_generation_tools",
    "register_vr_ar_tools",
    "register_substance_tools",
    "register_zbrush_tools",
    "register_cloud_render_tools",
    "register_collaboration_tools",
]
