"""
Command handler module

Each handler is responsible for processing a specific category of commands.
Uses lazy loading to avoid circular imports and startup failures.
"""

import importlib
import logging

logger = logging.getLogger(__name__)

# Mapping of handler module names to file names
HANDLER_MODULES = {
    "scene": "scene",
    "object": "object",
    "modeling": "modeling",
    "material": "material",
    "lighting": "lighting",
    "camera": "camera",
    "animation": "animation",
    "character": "character",
    "rigging": "rigging",
    "render": "render",
    "utility": "utility",
    "export": "export",
    "character_template": "character_template",
    "auto_rig": "auto_rig",
    "animation_preset": "animation_preset",
    "physics": "physics",
    "scene_advanced": "scene_advanced",
    "batch": "batch",
    "curves": "curves",
    "uv": "uv",
    "nodes": "nodes",
    "compositor": "compositor",
    "vse": "vse",
    "sculpt": "sculpt",
    "texture_paint": "texture_paint",
    "gpencil": "gpencil",
    "simulation": "simulation",
    "hair": "hair",
    "assets": "assets",
    "addons": "addons",
    "world": "world",
    "constraints": "constraints",
    "mocap": "mocap",
    "preferences": "preferences",
    "external": "external",
    "ai_assist": "ai_assist",
    "versioning": "versioning",
    "ai_generation": "ai_generation",
    "vr_ar": "vr_ar",
    "substance": "substance",
    "zbrush": "zbrush",
    "cloud_render": "cloud_render",
    "collaboration": "collaboration",
    "training": "training",
    "sport_character": "sport_character",
    "mesh_edit_advanced": "mesh_edit_advanced",
    "style_presets": "style_presets",
    "procedural_materials": "procedural_materials",
}

# Lazy loading cache
_loaded_handlers = {}


def get_handler(name: str):
    """Lazily load and retrieve a handler module

    Args:
        name: Handler name (e.g. "scene", "object", "modeling", etc.)

    Returns:
        The handler module, or None on failure
    """
    if name in _loaded_handlers:
        return _loaded_handlers[name]
    
    module_file = HANDLER_MODULES.get(name)
    if not module_file:
        logger.warning(f"Unknown handler: {name}")
        return None
    
    try:
        mod = importlib.import_module(f".{module_file}", package=__name__)
        _loaded_handlers[name] = mod
        return mod
    except Exception as e:
        logger.error(f"Failed to load handler '{name}': {e}")
        return None


__all__ = ["HANDLER_MODULES", "get_handler"]
