"""
Addon management handler

Handles Blender addon management commands.
"""

from typing import Any

import addon_utils
import bpy


def handle_list(params: dict[str, Any]) -> dict[str, Any]:
    """List all addons"""
    try:
        addons = []

        for mod in addon_utils.modules():
            name = mod.__name__
            bl_info = getattr(mod, "bl_info", {})

            # Check if enabled
            is_enabled = addon_utils.check(name)[0]

            addons.append(
                {
                    "name": name,
                    "bl_name": bl_info.get("name", name),
                    "version": bl_info.get("version", (0, 0, 0)),
                    "author": bl_info.get("author", "Unknown"),
                    "description": bl_info.get("description", ""),
                    "category": bl_info.get("category", ""),
                    "enabled": is_enabled,
                }
            )

        return {"success": True, "data": {"addons": addons, "total": len(addons)}}

    except Exception as e:
        return {"success": False, "error": {"code": "LIST_ERROR", "message": str(e)}}


def handle_enable(params: dict[str, Any]) -> dict[str, Any]:
    """Enable an addon"""
    addon_name = params.get("addon_name")

    try:
        bpy.ops.preferences.addon_enable(module=addon_name)

        return {"success": True, "data": {"addon_name": addon_name, "enabled": True}}

    except Exception as e:
        return {"success": False, "error": {"code": "ENABLE_ERROR", "message": str(e)}}


def handle_disable(params: dict[str, Any]) -> dict[str, Any]:
    """Disable an addon"""
    addon_name = params.get("addon_name")

    try:
        bpy.ops.preferences.addon_disable(module=addon_name)

        return {"success": True, "data": {"addon_name": addon_name, "enabled": False}}

    except Exception as e:
        return {"success": False, "error": {"code": "DISABLE_ERROR", "message": str(e)}}


def handle_install(params: dict[str, Any]) -> dict[str, Any]:
    """Install an addon"""
    filepath = params.get("filepath")
    overwrite = params.get("overwrite", True)
    enable = params.get("enable", True)

    try:
        bpy.ops.preferences.addon_install(filepath=filepath, overwrite=overwrite)

        # Get the installed addon name
        import os

        addon_name = os.path.splitext(os.path.basename(filepath))[0]

        if enable:
            bpy.ops.preferences.addon_enable(module=addon_name)

        return {
            "success": True,
            "data": {"addon_name": addon_name, "installed": True, "enabled": enable},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "INSTALL_ERROR", "message": str(e)}}


def handle_info(params: dict[str, Any]) -> dict[str, Any]:
    """Get detailed addon information"""
    addon_name = params.get("addon_name")

    try:
        for mod in addon_utils.modules():
            if mod.__name__ == addon_name:
                bl_info = getattr(mod, "bl_info", {})
                is_enabled = addon_utils.check(addon_name)[0]

                return {
                    "success": True,
                    "data": {
                        "name": addon_name,
                        "bl_name": bl_info.get("name", addon_name),
                        "version": bl_info.get("version", (0, 0, 0)),
                        "blender": bl_info.get("blender", (0, 0, 0)),
                        "author": bl_info.get("author", "Unknown"),
                        "description": bl_info.get("description", ""),
                        "location": bl_info.get("location", ""),
                        "warning": bl_info.get("warning", ""),
                        "doc_url": bl_info.get("doc_url", ""),
                        "tracker_url": bl_info.get("tracker_url", ""),
                        "support": bl_info.get("support", ""),
                        "category": bl_info.get("category", ""),
                        "enabled": is_enabled,
                    },
                }

        return {
            "success": False,
            "error": {"code": "NOT_FOUND", "message": f"Addon not found: {addon_name}"},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "INFO_ERROR", "message": str(e)}}
