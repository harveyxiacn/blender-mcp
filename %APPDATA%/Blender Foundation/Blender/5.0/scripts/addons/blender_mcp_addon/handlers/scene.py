"""
场景处理器

处理场景相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建场景"""
    name = params.get("name", "Scene")
    copy_from = params.get("copy_from")
    
    if copy_from:
        # 从现有场景复制
        source = bpy.data.scenes.get(copy_from)
        if not source:
            return {
                "success": False,
                "error": {
                    "code": "SCENE_NOT_FOUND",
                    "message": f"源场景不存在: {copy_from}"
                }
            }
        scene = source.copy()
        scene.name = name
    else:
        # 创建新场景
        scene = bpy.data.scenes.new(name)
    
    return {
        "success": True,
        "data": {
            "scene_name": scene.name
        }
    }


def handle_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出场景"""
    scenes = []
    active_scene = bpy.context.scene
    
    for scene in bpy.data.scenes:
        scenes.append({
            "name": scene.name,
            "objects_count": len(scene.objects),
            "is_active": scene == active_scene
        })
    
    return {
        "success": True,
        "data": {
            "scenes": scenes,
            "total": len(scenes)
        }
    }


def handle_get_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取场景信息"""
    scene_name = params.get("scene_name")
    
    if scene_name:
        scene = bpy.data.scenes.get(scene_name)
        if not scene:
            return {
                "success": False,
                "error": {
                    "code": "SCENE_NOT_FOUND",
                    "message": f"场景不存在: {scene_name}"
                }
            }
    else:
        scene = bpy.context.scene
    
    return {
        "success": True,
        "data": {
            "name": scene.name,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "frame_current": scene.frame_current,
            "fps": scene.render.fps,
            "objects_count": len(scene.objects),
            "unit_system": scene.unit_settings.system,
            "unit_scale": scene.unit_settings.scale_length
        }
    }


def handle_switch(params: Dict[str, Any]) -> Dict[str, Any]:
    """切换场景"""
    scene_name = params.get("scene_name")
    
    scene = bpy.data.scenes.get(scene_name)
    if not scene:
        return {
            "success": False,
            "error": {
                "code": "SCENE_NOT_FOUND",
                "message": f"场景不存在: {scene_name}"
            }
        }
    
    bpy.context.window.scene = scene
    
    return {
        "success": True,
        "data": {
            "scene_name": scene.name
        }
    }


def handle_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除场景"""
    scene_name = params.get("scene_name")
    
    if len(bpy.data.scenes) <= 1:
        return {
            "success": False,
            "error": {
                "code": "CANNOT_DELETE_LAST_SCENE",
                "message": "不能删除最后一个场景"
            }
        }
    
    scene = bpy.data.scenes.get(scene_name)
    if not scene:
        return {
            "success": False,
            "error": {
                "code": "SCENE_NOT_FOUND",
                "message": f"场景不存在: {scene_name}"
            }
        }
    
    bpy.data.scenes.remove(scene)
    
    return {
        "success": True,
        "data": {}
    }


def handle_set_settings(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置场景参数"""
    scene_name = params.get("scene_name")
    settings = params.get("settings", {})
    
    if scene_name:
        scene = bpy.data.scenes.get(scene_name)
        if not scene:
            return {
                "success": False,
                "error": {
                    "code": "SCENE_NOT_FOUND",
                    "message": f"场景不存在: {scene_name}"
                }
            }
    else:
        scene = bpy.context.scene
    
    # 应用设置
    if "frame_start" in settings:
        scene.frame_start = settings["frame_start"]
    if "frame_end" in settings:
        scene.frame_end = settings["frame_end"]
    if "fps" in settings:
        scene.render.fps = settings["fps"]
    if "unit_system" in settings:
        scene.unit_settings.system = settings["unit_system"]
    if "unit_scale" in settings:
        scene.unit_settings.scale_length = settings["unit_scale"]
    
    return {
        "success": True,
        "data": {
            "scene_name": scene.name
        }
    }
