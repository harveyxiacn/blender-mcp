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
]
