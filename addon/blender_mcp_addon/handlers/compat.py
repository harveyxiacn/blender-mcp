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


def ensure_object_mode() -> None:
    """Force OBJECT mode if Blender is in any edit/pose/sculpt mode.

    Guarded heavily: ``bpy.ops.object.mode_set`` can hard-crash Blender when
    invoked from the addon server context without a valid active object, so we
    only call it when there is an active object and we are confident a switch
    is required.
    """
    try:
        if bpy.context.mode == "OBJECT":
            return
        active = bpy.context.view_layer.objects.active
        if active is None:
            return
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass


def select_only(obj: "bpy.types.Object") -> bool:
    """Deselect everything and select+activate *obj* (Blender 5.x safe).

    Links *obj* to the scene master collection if it is not in the active view
    layer, deselects all via the data API (no bpy.ops), then selects and
    activates *obj*. Every bpy call is guarded so a single bad object can never
    take down the whole operation.

    Returns True on success, False if the object could not be made selectable.
    """
    try:
        view_layer = bpy.context.view_layer
    except Exception:
        return False

    # Ensure the object is actually in the active view layer; if not, link it
    # to the scene master collection (always part of the view layer).
    if obj.name not in view_layer.objects:
        try:
            bpy.context.scene.collection.objects.link(obj)
        except Exception:
            return False
        if obj.name not in view_layer.objects:
            return False

    # Deselect everything via the data API (context-independent).
    try:
        for o in view_layer.objects:
            if o.select_get():
                o.select_set(False)
    except Exception:
        pass

    try:
        obj.select_set(True)
        view_layer.objects.active = obj
    except Exception:
        return False
    return True
