"""
命令处理器模块

每个处理器负责处理特定类别的命令。
"""

from . import scene as scene_handler
from . import object as object_handler
from . import modeling as modeling_handler
from . import material as material_handler
from . import lighting as lighting_handler
from . import camera as camera_handler
from . import animation as animation_handler
from . import character as character_handler
from . import rigging as rigging_handler
from . import render as render_handler
from . import utility as utility_handler
from . import export as export_handler
from . import character_template as character_template_handler
from . import auto_rig as auto_rig_handler
from . import animation_preset as animation_preset_handler
from . import physics as physics_handler
from . import scene_advanced as scene_advanced_handler
from . import batch as batch_handler
from . import curves as curves_handler
from . import uv as uv_handler
from . import nodes as nodes_handler
from . import compositor as compositor_handler
from . import vse as vse_handler
from . import sculpt as sculpt_handler
from . import texture_paint as texture_paint_handler
from . import gpencil as gpencil_handler

__all__ = [
    "scene_handler",
    "object_handler",
    "modeling_handler",
    "material_handler",
    "lighting_handler",
    "camera_handler",
    "animation_handler",
    "character_handler",
    "rigging_handler",
    "render_handler",
    "utility_handler",
    "export_handler",
    "character_template_handler",
    "auto_rig_handler",
    "animation_preset_handler",
    "physics_handler",
    "scene_advanced_handler",
    "batch_handler",
    "curves_handler",
    "uv_handler",
    "nodes_handler",
    "compositor_handler",
    "vse_handler",
    "sculpt_handler",
    "texture_paint_handler",
    "gpencil_handler",
]
