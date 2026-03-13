"""
Real-time collaboration handler

Handles simplified scene synchronization collaboration commands.
Note: This is a simplified implementation that only supports basic object-level synchronization.
"""

from datetime import datetime
from typing import Any

import bpy

# Collaboration session state
COLLAB_SESSION = {
    "active": False,
    "role": None,  # "host" or "client"
    "session_name": None,
    "host": None,
    "port": 9877,
    "username": None,
    "users": [],
    "locked_objects": {},  # object_name -> username
    "chat_history": [],
    "last_sync": None,
}


def _get_scene_state() -> dict:
    """Get current scene state"""
    state = {"objects": [], "timestamp": datetime.now().isoformat()}

    for obj in bpy.context.scene.objects:
        obj_state = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "visible": obj.visible_get(),
            "parent": obj.parent.name if obj.parent else None,
        }

        # Material info
        if hasattr(obj.data, "materials") and obj.data.materials:
            obj_state["materials"] = [m.name if m else None for m in obj.data.materials]

        state["objects"].append(obj_state)

    return state


def _apply_scene_state(state: dict) -> None:
    """Apply scene state"""
    for obj_state in state.get("objects", []):
        obj = bpy.data.objects.get(obj_state["name"])
        if obj:
            obj.location = obj_state["location"]
            obj.rotation_euler = obj_state["rotation"]
            obj.scale = obj_state["scale"]


def handle_host(params: dict[str, Any]) -> dict[str, Any]:
    """Start collaboration session"""
    session_name = params.get("session_name")
    port = params.get("port", 9877)
    password = params.get("password")

    try:
        global COLLAB_SESSION

        if COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {
                    "code": "SESSION_ACTIVE",
                    "message": "A collaboration session is already active",
                },
            }

        COLLAB_SESSION["active"] = True
        COLLAB_SESSION["role"] = "host"
        COLLAB_SESSION["session_name"] = session_name
        COLLAB_SESSION["port"] = port
        COLLAB_SESSION["username"] = "Host"
        COLLAB_SESSION["users"] = [
            {"username": "Host", "role": "host", "joined": datetime.now().isoformat()}
        ]
        COLLAB_SESSION["locked_objects"] = {}
        COLLAB_SESSION["chat_history"] = []

        # Get initial scene state
        initial_state = _get_scene_state()
        COLLAB_SESSION["last_sync"] = initial_state["timestamp"]

        return {
            "success": True,
            "data": {
                "session_name": session_name,
                "port": port,
                "role": "host",
                "password_protected": bool(password),
                "note": "Collaboration session started. Other users can join via blender_collab_join.",
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "HOST_ERROR", "message": str(e)}}


def handle_join(params: dict[str, Any]) -> dict[str, Any]:
    """Join collaboration session"""
    host = params.get("host")
    port = params.get("port", 9877)
    params.get("password")
    username = params.get("username", "Guest")

    try:
        global COLLAB_SESSION

        if COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {
                    "code": "SESSION_ACTIVE",
                    "message": "A collaboration session is already active",
                },
            }

        COLLAB_SESSION["active"] = True
        COLLAB_SESSION["role"] = "client"
        COLLAB_SESSION["host"] = host
        COLLAB_SESSION["port"] = port
        COLLAB_SESSION["username"] = username
        COLLAB_SESSION["users"] = [
            {"username": username, "role": "client", "joined": datetime.now().isoformat()}
        ]

        return {
            "success": True,
            "data": {
                "host": host,
                "port": port,
                "username": username,
                "role": "client",
                "note": "Simplified collaboration mode: use blender_collab_sync to manually sync scene",
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "JOIN_ERROR", "message": str(e)}}


def handle_leave(params: dict[str, Any]) -> dict[str, Any]:
    """Leave collaboration session"""
    try:
        global COLLAB_SESSION

        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "No active collaboration session"},
            }

        old_session = COLLAB_SESSION.copy()

        COLLAB_SESSION = {
            "active": False,
            "role": None,
            "session_name": None,
            "host": None,
            "port": 9877,
            "username": None,
            "users": [],
            "locked_objects": {},
            "chat_history": [],
            "last_sync": None,
        }

        return {
            "success": True,
            "data": {"left_session": old_session["session_name"], "role": old_session["role"]},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "LEAVE_ERROR", "message": str(e)}}


def handle_sync(params: dict[str, Any]) -> dict[str, Any]:
    """Synchronize scene state"""
    try:
        global COLLAB_SESSION

        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "No active collaboration session"},
            }

        # Get current scene state
        state = _get_scene_state()
        COLLAB_SESSION["last_sync"] = state["timestamp"]

        return {
            "success": True,
            "data": {
                "timestamp": state["timestamp"],
                "objects_count": len(state["objects"]),
                "state": state,
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "SYNC_ERROR", "message": str(e)}}


def handle_lock(params: dict[str, Any]) -> dict[str, Any]:
    """Lock objects"""
    object_names = params.get("object_names", [])

    try:
        global COLLAB_SESSION

        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "No active collaboration session"},
            }

        locked = []
        already_locked = []

        for name in object_names:
            obj = bpy.data.objects.get(name)
            if not obj:
                continue

            if name in COLLAB_SESSION["locked_objects"]:
                if COLLAB_SESSION["locked_objects"][name] != COLLAB_SESSION["username"]:
                    already_locked.append(
                        {"name": name, "locked_by": COLLAB_SESSION["locked_objects"][name]}
                    )
                    continue

            COLLAB_SESSION["locked_objects"][name] = COLLAB_SESSION["username"]

            # Add visual marker
            obj["collab_locked"] = True
            obj["collab_locked_by"] = COLLAB_SESSION["username"]

            locked.append(name)

        return {
            "success": True,
            "data": {
                "locked": locked,
                "already_locked": already_locked,
                "user": COLLAB_SESSION["username"],
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "LOCK_ERROR", "message": str(e)}}


def handle_unlock(params: dict[str, Any]) -> dict[str, Any]:
    """Unlock objects"""
    object_names = params.get("object_names", [])

    try:
        global COLLAB_SESSION

        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "No active collaboration session"},
            }

        unlocked = []
        not_allowed = []

        for name in object_names:
            if name not in COLLAB_SESSION["locked_objects"]:
                continue

            # Can only unlock objects locked by self (or host can unlock all)
            if (
                COLLAB_SESSION["locked_objects"][name] != COLLAB_SESSION["username"]
                and COLLAB_SESSION["role"] != "host"
            ):
                not_allowed.append(name)
                continue

            del COLLAB_SESSION["locked_objects"][name]

            # Remove visual marker
            obj = bpy.data.objects.get(name)
            if obj:
                if "collab_locked" in obj:
                    del obj["collab_locked"]
                if "collab_locked_by" in obj:
                    del obj["collab_locked_by"]

            unlocked.append(name)

        return {"success": True, "data": {"unlocked": unlocked, "not_allowed": not_allowed}}

    except Exception as e:
        return {"success": False, "error": {"code": "UNLOCK_ERROR", "message": str(e)}}


def handle_chat(params: dict[str, Any]) -> dict[str, Any]:
    """Send message"""
    message = params.get("message", "")

    try:
        global COLLAB_SESSION

        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "No active collaboration session"},
            }

        chat_entry = {
            "username": COLLAB_SESSION["username"],
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        COLLAB_SESSION["chat_history"].append(chat_entry)

        # Limit chat history length
        if len(COLLAB_SESSION["chat_history"]) > 100:
            COLLAB_SESSION["chat_history"] = COLLAB_SESSION["chat_history"][-100:]

        return {"success": True, "data": chat_entry}

    except Exception as e:
        return {"success": False, "error": {"code": "CHAT_ERROR", "message": str(e)}}


def handle_status(params: dict[str, Any]) -> dict[str, Any]:
    """Get collaboration status"""
    try:
        global COLLAB_SESSION

        return {
            "success": True,
            "data": {
                "active": COLLAB_SESSION["active"],
                "role": COLLAB_SESSION["role"],
                "session_name": COLLAB_SESSION["session_name"],
                "host": COLLAB_SESSION["host"],
                "port": COLLAB_SESSION["port"],
                "username": COLLAB_SESSION["username"],
                "users_count": len(COLLAB_SESSION["users"]),
                "locked_objects_count": len(COLLAB_SESSION["locked_objects"]),
                "last_sync": COLLAB_SESSION["last_sync"],
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "STATUS_ERROR", "message": str(e)}}


def handle_users(params: dict[str, Any]) -> dict[str, Any]:
    """List users"""
    try:
        global COLLAB_SESSION

        return {
            "success": True,
            "data": {
                "users": COLLAB_SESSION["users"],
                "locked_objects": COLLAB_SESSION["locked_objects"],
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "USERS_ERROR", "message": str(e)}}
