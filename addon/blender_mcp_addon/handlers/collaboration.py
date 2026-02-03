"""
实时协作处理器

处理简化的场景同步协作命令。
注意：这是一个简化的实现，仅支持基本的对象级别同步。
"""

from typing import Any, Dict, List
import bpy
import json
from datetime import datetime


# 协作会话状态
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
    "last_sync": None
}


def _get_scene_state() -> Dict:
    """获取当前场景状态"""
    state = {
        "objects": [],
        "timestamp": datetime.now().isoformat()
    }
    
    for obj in bpy.context.scene.objects:
        obj_state = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "visible": obj.visible_get(),
            "parent": obj.parent.name if obj.parent else None
        }
        
        # 材质信息
        if hasattr(obj.data, 'materials') and obj.data.materials:
            obj_state["materials"] = [m.name if m else None for m in obj.data.materials]
        
        state["objects"].append(obj_state)
    
    return state


def _apply_scene_state(state: Dict):
    """应用场景状态"""
    for obj_state in state.get("objects", []):
        obj = bpy.data.objects.get(obj_state["name"])
        if obj:
            obj.location = obj_state["location"]
            obj.rotation_euler = obj_state["rotation"]
            obj.scale = obj_state["scale"]


def handle_host(params: Dict[str, Any]) -> Dict[str, Any]:
    """启动协作会话"""
    session_name = params.get("session_name")
    port = params.get("port", 9877)
    password = params.get("password")
    
    try:
        global COLLAB_SESSION
        
        if COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "SESSION_ACTIVE", "message": "已有活动的协作会话"}
            }
        
        COLLAB_SESSION["active"] = True
        COLLAB_SESSION["role"] = "host"
        COLLAB_SESSION["session_name"] = session_name
        COLLAB_SESSION["port"] = port
        COLLAB_SESSION["username"] = "Host"
        COLLAB_SESSION["users"] = [{"username": "Host", "role": "host", "joined": datetime.now().isoformat()}]
        COLLAB_SESSION["locked_objects"] = {}
        COLLAB_SESSION["chat_history"] = []
        
        # 获取初始场景状态
        initial_state = _get_scene_state()
        COLLAB_SESSION["last_sync"] = initial_state["timestamp"]
        
        return {
            "success": True,
            "data": {
                "session_name": session_name,
                "port": port,
                "role": "host",
                "password_protected": bool(password),
                "note": "协作会话已启动。其他用户可以通过 blender_collab_join 加入。"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "HOST_ERROR", "message": str(e)}
        }


def handle_join(params: Dict[str, Any]) -> Dict[str, Any]:
    """加入协作会话"""
    host = params.get("host")
    port = params.get("port", 9877)
    password = params.get("password")
    username = params.get("username", "Guest")
    
    try:
        global COLLAB_SESSION
        
        if COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "SESSION_ACTIVE", "message": "已有活动的协作会话"}
            }
        
        COLLAB_SESSION["active"] = True
        COLLAB_SESSION["role"] = "client"
        COLLAB_SESSION["host"] = host
        COLLAB_SESSION["port"] = port
        COLLAB_SESSION["username"] = username
        COLLAB_SESSION["users"] = [{"username": username, "role": "client", "joined": datetime.now().isoformat()}]
        
        return {
            "success": True,
            "data": {
                "host": host,
                "port": port,
                "username": username,
                "role": "client",
                "note": "简化协作模式：使用 blender_collab_sync 手动同步场景"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "JOIN_ERROR", "message": str(e)}
        }


def handle_leave(params: Dict[str, Any]) -> Dict[str, Any]:
    """离开协作会话"""
    try:
        global COLLAB_SESSION
        
        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "没有活动的协作会话"}
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
            "last_sync": None
        }
        
        return {
            "success": True,
            "data": {
                "left_session": old_session["session_name"],
                "role": old_session["role"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LEAVE_ERROR", "message": str(e)}
        }


def handle_sync(params: Dict[str, Any]) -> Dict[str, Any]:
    """同步场景状态"""
    try:
        global COLLAB_SESSION
        
        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "没有活动的协作会话"}
            }
        
        # 获取当前场景状态
        state = _get_scene_state()
        COLLAB_SESSION["last_sync"] = state["timestamp"]
        
        return {
            "success": True,
            "data": {
                "timestamp": state["timestamp"],
                "objects_count": len(state["objects"]),
                "state": state
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SYNC_ERROR", "message": str(e)}
        }


def handle_lock(params: Dict[str, Any]) -> Dict[str, Any]:
    """锁定对象"""
    object_names = params.get("object_names", [])
    
    try:
        global COLLAB_SESSION
        
        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "没有活动的协作会话"}
            }
        
        locked = []
        already_locked = []
        
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if not obj:
                continue
            
            if name in COLLAB_SESSION["locked_objects"]:
                if COLLAB_SESSION["locked_objects"][name] != COLLAB_SESSION["username"]:
                    already_locked.append({
                        "name": name,
                        "locked_by": COLLAB_SESSION["locked_objects"][name]
                    })
                    continue
            
            COLLAB_SESSION["locked_objects"][name] = COLLAB_SESSION["username"]
            
            # 添加视觉标记
            obj["collab_locked"] = True
            obj["collab_locked_by"] = COLLAB_SESSION["username"]
            
            locked.append(name)
        
        return {
            "success": True,
            "data": {
                "locked": locked,
                "already_locked": already_locked,
                "user": COLLAB_SESSION["username"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LOCK_ERROR", "message": str(e)}
        }


def handle_unlock(params: Dict[str, Any]) -> Dict[str, Any]:
    """解锁对象"""
    object_names = params.get("object_names", [])
    
    try:
        global COLLAB_SESSION
        
        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "没有活动的协作会话"}
            }
        
        unlocked = []
        not_allowed = []
        
        for name in object_names:
            if name not in COLLAB_SESSION["locked_objects"]:
                continue
            
            # 只能解锁自己锁定的对象（或主机可以解锁所有）
            if COLLAB_SESSION["locked_objects"][name] != COLLAB_SESSION["username"] and COLLAB_SESSION["role"] != "host":
                not_allowed.append(name)
                continue
            
            del COLLAB_SESSION["locked_objects"][name]
            
            # 移除视觉标记
            obj = bpy.data.objects.get(name)
            if obj:
                if "collab_locked" in obj:
                    del obj["collab_locked"]
                if "collab_locked_by" in obj:
                    del obj["collab_locked_by"]
            
            unlocked.append(name)
        
        return {
            "success": True,
            "data": {
                "unlocked": unlocked,
                "not_allowed": not_allowed
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "UNLOCK_ERROR", "message": str(e)}
        }


def handle_chat(params: Dict[str, Any]) -> Dict[str, Any]:
    """发送消息"""
    message = params.get("message", "")
    
    try:
        global COLLAB_SESSION
        
        if not COLLAB_SESSION["active"]:
            return {
                "success": False,
                "error": {"code": "NO_SESSION", "message": "没有活动的协作会话"}
            }
        
        chat_entry = {
            "username": COLLAB_SESSION["username"],
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        COLLAB_SESSION["chat_history"].append(chat_entry)
        
        # 限制聊天历史长度
        if len(COLLAB_SESSION["chat_history"]) > 100:
            COLLAB_SESSION["chat_history"] = COLLAB_SESSION["chat_history"][-100:]
        
        return {
            "success": True,
            "data": chat_entry
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHAT_ERROR", "message": str(e)}
        }


def handle_status(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取协作状态"""
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
                "last_sync": COLLAB_SESSION["last_sync"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "STATUS_ERROR", "message": str(e)}
        }


def handle_users(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出用户"""
    try:
        global COLLAB_SESSION
        
        return {
            "success": True,
            "data": {
                "users": COLLAB_SESSION["users"],
                "locked_objects": COLLAB_SESSION["locked_objects"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "USERS_ERROR", "message": str(e)}
        }
