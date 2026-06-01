"""
Snapshot handler - Viewport capture and render preview.

Runs inside Blender with full bpy access.
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Any

import bpy


def _default_path(prefix: str = "blender_snapshot") -> str:
    """Generate a timestamped temp file path."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(tempfile.gettempdir(), f"{prefix}_{ts}.png")


def handle_viewport(params: dict[str, Any]) -> dict[str, Any]:
    """Capture the active 3D viewport to a PNG file."""
    width = params.get("width", 800)
    height = params.get("height", 600)
    output_path = params.get("output_path") or _default_path("blender_viewport")

    try:
        # Find a 3D viewport area
        target_area = None
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    target_area = area
                    break
            if target_area:
                break

        if not target_area:
            return {
                "success": False,
                "error": {
                    "code": "NO_VIEWPORT",
                    "message": "No 3D viewport found. Ensure a 3D View area is open in Blender.",
                },
            }

        # Use offscreen rendering via gpu module for headless-safe capture
        import gpu
        from gpu_extras.presets import draw_texture_2d

        space = target_area.spaces[0]

        # Temporarily override region dimensions are not directly settable,
        # so we use the viewport render approach via bpy.ops with context override.
        region = None
        for r in target_area.regions:
            if r.type == "WINDOW":
                region = r
                break

        if not region:
            return {
                "success": False,
                "error": {
                    "code": "NO_REGION",
                    "message": "No WINDOW region found in 3D viewport.",
                },
            }

        # Use render-based viewport capture for reliability
        scene = bpy.context.scene
        old_res_x = scene.render.resolution_x
        old_res_y = scene.render.resolution_y
        old_pct = scene.render.resolution_percentage
        old_path = scene.render.filepath
        old_format = scene.render.image_settings.file_format

        try:
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.resolution_percentage = 100
            scene.render.filepath = output_path
            scene.render.image_settings.file_format = "PNG"

            # Use OpenGL render (viewport render)
            override = bpy.context.copy()
            override["area"] = target_area
            override["region"] = region
            override["space_data"] = space

            # Try with_context approach (Blender 3.2+)
            if hasattr(bpy.context, "temp_override"):
                with bpy.context.temp_override(**override):
                    bpy.ops.render.opengl(write_still=True)
            else:
                bpy.ops.render.opengl(override, write_still=True)

            return {
                "success": True,
                "data": {
                    "path": output_path,
                    "width": width,
                    "height": height,
                },
            }
        finally:
            scene.render.resolution_x = old_res_x
            scene.render.resolution_y = old_res_y
            scene.render.resolution_percentage = old_pct
            scene.render.filepath = old_path
            scene.render.image_settings.file_format = old_format

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SNAPSHOT_ERROR", "message": str(e)},
        }


def handle_render_preview(params: dict[str, Any]) -> dict[str, Any]:
    """Quick render at reduced resolution."""
    width = params.get("width", 512)
    samples = params.get("samples", 16)
    output_path = params.get("output_path") or _default_path("blender_render_preview")

    try:
        scene = bpy.context.scene

        # Save current settings
        old_res_x = scene.render.resolution_x
        old_res_y = scene.render.resolution_y
        old_pct = scene.render.resolution_percentage
        old_path = scene.render.filepath
        old_format = scene.render.image_settings.file_format

        # Save engine-specific sample settings
        old_samples = None
        engine = scene.render.engine
        if engine == "CYCLES":
            old_samples = scene.cycles.samples
            scene.cycles.samples = samples
        elif engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            if hasattr(scene.eevee, "taa_render_samples"):
                old_samples = scene.eevee.taa_render_samples
                scene.eevee.taa_render_samples = samples

        # Calculate height maintaining aspect ratio
        if old_res_x > 0:
            aspect = old_res_y / old_res_x
            height = int(width * aspect)
        else:
            height = width

        try:
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.resolution_percentage = 100
            scene.render.filepath = output_path
            scene.render.image_settings.file_format = "PNG"

            bpy.ops.render.render(write_still=True)

            return {
                "success": True,
                "data": {
                    "path": output_path,
                    "width": width,
                    "height": height,
                    "samples": samples,
                    "engine": engine,
                },
            }
        finally:
            scene.render.resolution_x = old_res_x
            scene.render.resolution_y = old_res_y
            scene.render.resolution_percentage = old_pct
            scene.render.filepath = old_path
            scene.render.image_settings.file_format = old_format

            if engine == "CYCLES" and old_samples is not None:
                scene.cycles.samples = old_samples
            elif engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
                if old_samples is not None and hasattr(scene.eevee, "taa_render_samples"):
                    scene.eevee.taa_render_samples = old_samples

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "RENDER_PREVIEW_ERROR", "message": str(e)},
        }
