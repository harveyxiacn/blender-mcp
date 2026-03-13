"""
Blender version compatibility helpers.

Provides portable detection of engine names and other identifiers
that changed across Blender versions.
"""

import bpy


def get_eevee_engine() -> str:
    """Return the correct EEVEE render-engine identifier for the running Blender.

    * Blender 4.2+ (including 5.x): ``"BLENDER_EEVEE"``
    * Blender 4.0 - 4.1:            ``"BLENDER_EEVEE_NEXT"``
    * Blender 3.x and earlier:       ``"BLENDER_EEVEE"``
    """
    if bpy.app.version >= (4, 0, 0) and bpy.app.version < (4, 2, 0):
        return "BLENDER_EEVEE_NEXT"
    return "BLENDER_EEVEE"


def normalize_engine_name(engine: str) -> str:
    """Translate an engine name so it is valid for the running Blender.

    Accepts both ``BLENDER_EEVEE`` and ``BLENDER_EEVEE_NEXT`` and converts
    to whichever one the current Blender actually supports.  Non-EEVEE
    engine names are returned unchanged.
    """
    if engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        return get_eevee_engine()
    return engine


def is_eevee_engine(engine: str) -> bool:
    """Return True if *engine* refers to any variant of the EEVEE renderer."""
    return engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT")
