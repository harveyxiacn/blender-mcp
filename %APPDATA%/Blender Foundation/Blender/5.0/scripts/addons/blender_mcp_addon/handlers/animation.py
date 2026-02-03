"""
动画处理器

处理动画相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_keyframe_insert(params: Dict[str, Any]) -> Dict[str, Any]:
    """插入关键帧"""
    object_name = params.get("object_name")
    data_path = params.get("data_path")
    frame = params.get("frame")
    value = params.get("value")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    # 如果指定了帧，跳转到该帧
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    else:
        frame = bpy.context.scene.frame_current
    
    # 如果指定了值，设置属性值
    if value is not None:
        try:
            # 解析数据路径
            if "[" in data_path:
                # 处理索引，如 location[0]
                base_path, index = data_path.rsplit("[", 1)
                index = int(index.rstrip("]"))
                current = getattr(obj, base_path)
                current[index] = value
            else:
                setattr(obj, data_path, value)
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "SET_VALUE_ERROR",
                    "message": f"设置属性值失败: {e}"
                }
            }
    
    # 插入关键帧
    try:
        obj.keyframe_insert(data_path=data_path, frame=frame)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "KEYFRAME_INSERT_ERROR",
                "message": f"插入关键帧失败: {e}"
            }
        }
    
    return {
        "success": True,
        "data": {
            "frame": frame
        }
    }


def handle_keyframe_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除关键帧"""
    object_name = params.get("object_name")
    data_path = params.get("data_path")
    frame = params.get("frame")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    
    try:
        obj.keyframe_delete(data_path=data_path)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "KEYFRAME_DELETE_ERROR",
                "message": f"删除关键帧失败: {e}"
            }
        }
    
    return {
        "success": True,
        "data": {}
    }


def handle_set_interpolation(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置插值类型"""
    object_name = params.get("object_name")
    interpolation = params.get("interpolation", "BEZIER")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if not obj.animation_data or not obj.animation_data.action:
        return {
            "success": False,
            "error": {
                "code": "NO_ANIMATION",
                "message": "对象没有动画数据"
            }
        }
    
    # 设置所有关键帧的插值类型
    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = interpolation
    
    return {
        "success": True,
        "data": {}
    }


def handle_timeline_set_range(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置时间线范围"""
    scene = bpy.context.scene
    
    if "frame_start" in params:
        scene.frame_start = params["frame_start"]
    
    if "frame_end" in params:
        scene.frame_end = params["frame_end"]
    
    if "frame_current" in params:
        scene.frame_set(params["frame_current"])
    
    return {
        "success": True,
        "data": {
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "frame_current": scene.frame_current
        }
    }


def handle_goto_frame(params: Dict[str, Any]) -> Dict[str, Any]:
    """跳转到帧"""
    frame = params.get("frame", 1)
    
    bpy.context.scene.frame_set(frame)
    
    return {
        "success": True,
        "data": {
            "frame_current": bpy.context.scene.frame_current
        }
    }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙动画"""
    object_name = params.get("object_name")
    frame_start = params.get("frame_start")
    frame_end = params.get("frame_end")
    step = params.get("step", 1)
    bake_location = params.get("bake_location", True)
    bake_rotation = params.get("bake_rotation", True)
    bake_scale = params.get("bake_scale", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    scene = bpy.context.scene
    start = frame_start if frame_start is not None else scene.frame_start
    end = frame_end if frame_end is not None else scene.frame_end
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 烘焙动画
    bpy.ops.nla.bake(
        frame_start=start,
        frame_end=end,
        step=step,
        only_selected=True,
        visual_keying=True,
        clear_constraints=False,
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'} if obj.type == 'ARMATURE' else {'OBJECT'}
    )
    
    return {
        "success": True,
        "data": {}
    }
