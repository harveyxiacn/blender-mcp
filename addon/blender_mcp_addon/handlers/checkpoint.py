"""
Checkpoint handler - Named save/restore points.

Runs inside Blender with full bpy access.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from typing import Any

import bpy


def _checkpoint_dir() -> str:
    """Get or create the checkpoint directory."""
    d = os.path.join(tempfile.gettempdir(), "blender_mcp_checkpoints")
    os.makedirs(d, exist_ok=True)
    return d


def _meta_path(name: str) -> str:
    """Path to the metadata JSON for a checkpoint."""
    return os.path.join(_checkpoint_dir(), f"{name}.meta.json")


def _blend_path(name: str) -> str:
    """Path to the .blend file for a checkpoint."""
    return os.path.join(_checkpoint_dir(), f"{name}.blend")


def _sanitize_name(name: str) -> str:
    """Sanitize checkpoint name to be filesystem-safe."""
    # Allow alphanumeric, underscore, hyphen, dot
    return "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in name)


def handle_save(params: dict[str, Any]) -> dict[str, Any]:
    """Save a named checkpoint."""
    raw_name = params.get("name", "")
    description = params.get("description", "")

    if not raw_name:
        return {
            "success": False,
            "error": {"code": "MISSING_PARAM", "message": "Checkpoint name is required."},
        }

    name = _sanitize_name(raw_name)
    blend_path = _blend_path(name)
    meta_path = _meta_path(name)

    try:
        scene = bpy.context.scene
        object_count = len(scene.objects)

        # Save .blend copy
        bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)

        # Save metadata
        meta = {
            "name": raw_name,
            "sanitized_name": name,
            "description": description or "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "object_count": object_count,
            "scene_name": scene.name,
            "blend_path": blend_path,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return {
            "success": True,
            "data": {
                "name": raw_name,
                "path": blend_path,
                "object_count": object_count,
                "timestamp": meta["timestamp"],
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHECKPOINT_SAVE_ERROR", "message": str(e)},
        }


def handle_restore(params: dict[str, Any]) -> dict[str, Any]:
    """Restore a previously saved checkpoint."""
    raw_name = params.get("name", "")

    if not raw_name:
        return {
            "success": False,
            "error": {"code": "MISSING_PARAM", "message": "Checkpoint name is required."},
        }

    name = _sanitize_name(raw_name)
    blend_path = _blend_path(name)
    meta_path = _meta_path(name)

    if not os.path.exists(blend_path):
        return {
            "success": False,
            "error": {
                "code": "CHECKPOINT_NOT_FOUND",
                "message": f"Checkpoint '{raw_name}' not found.",
                "suggestion": "Use 'blender_checkpoint_list' to see available checkpoints.",
            },
        }

    try:
        bpy.ops.wm.open_mainfile(filepath=blend_path)

        # Read metadata
        object_count = len(bpy.context.scene.objects)
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)

        return {
            "success": True,
            "data": {
                "name": raw_name,
                "object_count": object_count,
                "restored_from": meta.get("timestamp", "unknown"),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHECKPOINT_RESTORE_ERROR", "message": str(e)},
        }


def handle_list(params: dict[str, Any]) -> dict[str, Any]:
    """List all saved checkpoints."""
    try:
        cp_dir = _checkpoint_dir()
        checkpoints = []

        for fname in sorted(os.listdir(cp_dir)):
            if fname.endswith(".meta.json"):
                meta_path = os.path.join(cp_dir, fname)
                try:
                    with open(meta_path, encoding="utf-8") as f:
                        meta = json.load(f)
                    # Verify .blend file still exists
                    if os.path.exists(meta.get("blend_path", "")):
                        checkpoints.append(
                            {
                                "name": meta.get("name", fname),
                                "description": meta.get("description", ""),
                                "timestamp": meta.get("timestamp", ""),
                                "object_count": meta.get("object_count", 0),
                                "scene_name": meta.get("scene_name", ""),
                            }
                        )
                except (json.JSONDecodeError, OSError):
                    continue

        return {"success": True, "data": {"checkpoints": checkpoints}}

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHECKPOINT_LIST_ERROR", "message": str(e)},
        }


def handle_delete(params: dict[str, Any]) -> dict[str, Any]:
    """Delete a checkpoint."""
    raw_name = params.get("name", "")

    if not raw_name:
        return {
            "success": False,
            "error": {"code": "MISSING_PARAM", "message": "Checkpoint name is required."},
        }

    name = _sanitize_name(raw_name)
    blend_path = _blend_path(name)
    meta_path = _meta_path(name)

    if not os.path.exists(blend_path) and not os.path.exists(meta_path):
        return {
            "success": False,
            "error": {
                "code": "CHECKPOINT_NOT_FOUND",
                "message": f"Checkpoint '{raw_name}' not found.",
                "suggestion": "Use 'blender_checkpoint_list' to see available checkpoints.",
            },
        }

    try:
        if os.path.exists(blend_path):
            os.remove(blend_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)

        return {"success": True, "data": {"name": raw_name, "deleted": True}}

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHECKPOINT_DELETE_ERROR", "message": str(e)},
        }
