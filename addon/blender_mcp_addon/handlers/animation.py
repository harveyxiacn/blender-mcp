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


def handle_action_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建动画动作
    
    Args:
        params:
            - armature_name: 骨架名称
            - action_name: 动作名称
            - fake_user: 是否设置假用户（防止被清理）
    """
    armature_name = params.get("armature_name")
    action_name = params.get("action_name", "Action")
    fake_user = params.get("fake_user", True)
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 创建动作
    action = bpy.data.actions.new(name=action_name)
    action.use_fake_user = fake_user
    
    # 分配给骨架
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = action
    
    return {
        "success": True,
        "data": {
            "action_name": action.name,
            "armature_name": obj.name
        }
    }


def handle_action_create_from_poses(params: Dict[str, Any]) -> Dict[str, Any]:
    """从姿势创建动画动作
    
    批量创建动画关键帧序列。
    
    Args:
        params:
            - armature_name: 骨架名称
            - action_name: 动作名称
            - keyframes: 关键帧数据列表
                [
                    {
                        "frame": int,           # 帧号
                        "bone": str,            # 骨骼名称
                        "location": [x,y,z],    # 位置（可选）
                        "rotation": [x,y,z],    # 旋转欧拉角（可选）
                        "rotation_quaternion": [w,x,y,z],  # 四元数旋转（可选）
                        "scale": [x,y,z]        # 缩放（可选）
                    },
                    ...
                ]
            - fake_user: 是否设置假用户
    """
    armature_name = params.get("armature_name")
    action_name = params.get("action_name", "Action")
    keyframes = params.get("keyframes", [])
    fake_user = params.get("fake_user", True)
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 创建动作
    action = bpy.data.actions.new(name=action_name)
    action.use_fake_user = fake_user
    
    # 分配给骨架
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = action
    
    # 切换到姿势模式
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    
    keyframe_count = 0
    bones_animated = set()
    
    try:
        for kf_data in keyframes:
            frame = kf_data.get("frame", 1)
            bone_name = kf_data.get("bone")
            
            if not bone_name:
                continue
            
            pose_bone = obj.pose.bones.get(bone_name)
            if not pose_bone:
                continue
            
            bones_animated.add(bone_name)
            
            # 设置位置
            if "location" in kf_data:
                pose_bone.location = kf_data["location"]
                pose_bone.keyframe_insert(data_path="location", frame=frame)
                keyframe_count += 1
            
            # 设置旋转（欧拉角）
            if "rotation" in kf_data:
                pose_bone.rotation_mode = 'XYZ'
                pose_bone.rotation_euler = kf_data["rotation"]
                pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
                keyframe_count += 1
            
            # 设置旋转（四元数）
            if "rotation_quaternion" in kf_data:
                pose_bone.rotation_mode = 'QUATERNION'
                pose_bone.rotation_quaternion = kf_data["rotation_quaternion"]
                pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                keyframe_count += 1
            
            # 设置缩放
            if "scale" in kf_data:
                pose_bone.scale = kf_data["scale"]
                pose_bone.keyframe_insert(data_path="scale", frame=frame)
                keyframe_count += 1
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {
            "success": True,
            "data": {
                "action_name": action.name,
                "armature_name": obj.name,
                "keyframe_count": keyframe_count,
                "bones_animated": list(bones_animated)
            }
        }
    
    except Exception as e:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {
                "code": "KEYFRAME_ERROR",
                "message": str(e)
            }
        }


def handle_action_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有动作
    
    Args:
        params:
            - armature_name: 可选，只列出特定骨架的动作
    """
    armature_name = params.get("armature_name")
    
    actions = []
    for action in bpy.data.actions:
        action_info = {
            "name": action.name,
            "frame_start": action.frame_range[0],
            "frame_end": action.frame_range[1],
            "fake_user": action.use_fake_user,
            "users": action.users
        }
        actions.append(action_info)
    
    return {
        "success": True,
        "data": {
            "actions": actions,
            "total": len(actions)
        }
    }


def handle_action_assign(params: Dict[str, Any]) -> Dict[str, Any]:
    """将动作分配给骨架
    
    Args:
        params:
            - armature_name: 骨架名称
            - action_name: 动作名称
    """
    armature_name = params.get("armature_name")
    action_name = params.get("action_name")
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    action = bpy.data.actions.get(action_name)
    if not action:
        return {
            "success": False,
            "error": {
                "code": "ACTION_NOT_FOUND",
                "message": f"动作不存在: {action_name}"
            }
        }
    
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = action
    
    return {
        "success": True,
        "data": {
            "armature_name": obj.name,
            "action_name": action.name
        }
    }


def handle_nla_push_action(params: Dict[str, Any]) -> Dict[str, Any]:
    """将动作推送到 NLA 轨道
    
    Args:
        params:
            - armature_name: 骨架名称
            - action_name: 动作名称（可选，默认使用当前动作）
            - track_name: NLA 轨道名称
            - start_frame: 开始帧
    """
    armature_name = params.get("armature_name")
    action_name = params.get("action_name")
    track_name = params.get("track_name", "NLATrack")
    start_frame = params.get("start_frame", 1)
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    if not obj.animation_data:
        return {
            "success": False,
            "error": {
                "code": "NO_ANIMATION_DATA",
                "message": "骨架没有动画数据"
            }
        }
    
    # 获取动作
    if action_name:
        action = bpy.data.actions.get(action_name)
        if not action:
            return {
                "success": False,
                "error": {
                    "code": "ACTION_NOT_FOUND",
                    "message": f"动作不存在: {action_name}"
                }
            }
    else:
        action = obj.animation_data.action
        if not action:
            return {
                "success": False,
                "error": {
                    "code": "NO_ACTION",
                    "message": "骨架没有当前动作"
                }
            }
    
    # 创建 NLA 轨道
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    
    # 创建 NLA 条带
    strip = track.strips.new(action.name, start_frame, action)
    
    return {
        "success": True,
        "data": {
            "armature_name": obj.name,
            "action_name": action.name,
            "track_name": track.name,
            "strip_name": strip.name
        }
    }
