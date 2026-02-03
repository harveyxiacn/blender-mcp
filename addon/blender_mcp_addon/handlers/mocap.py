"""
动作捕捉处理器

处理动作捕捉数据导入和处理命令。
"""

from typing import Any, Dict
import bpy
import os


def handle_import(params: Dict[str, Any]) -> Dict[str, Any]:
    """导入动捕数据"""
    filepath = params.get("filepath")
    target_armature = params.get("target_armature")
    scale = params.get("scale", 1.0)
    frame_start = params.get("frame_start", 1)
    use_fps_scale = params.get("use_fps_scale", False)
    
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"文件不存在: {filepath}"}
        }
    
    try:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.bvh':
            # 导入 BVH
            bpy.ops.import_anim.bvh(
                filepath=filepath,
                filter_glob="*.bvh",
                global_scale=scale,
                frame_start=frame_start,
                use_fps_scale=use_fps_scale,
                use_cyclic=False,
                rotate_mode='NATIVE'
            )
            
        elif ext == '.fbx':
            # 导入 FBX 动画
            bpy.ops.import_scene.fbx(
                filepath=filepath,
                use_anim=True,
                anim_offset=frame_start,
                global_scale=scale
            )
        else:
            return {
                "success": False,
                "error": {"code": "UNSUPPORTED_FORMAT", "message": f"不支持的格式: {ext}"}
            }
        
        # 获取导入的骨架
        imported_armature = None
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE':
                imported_armature = obj
                break
        
        # 如果指定了目标骨架，尝试重定向
        if target_armature and imported_armature:
            target = bpy.data.objects.get(target_armature)
            if target and target.type == 'ARMATURE':
                # 复制动作到目标骨架
                if imported_armature.animation_data and imported_armature.animation_data.action:
                    action = imported_armature.animation_data.action.copy()
                    if not target.animation_data:
                        target.animation_data_create()
                    target.animation_data.action = action
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "armature": imported_armature.name if imported_armature else None
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "IMPORT_ERROR", "message": str(e)}
        }


def handle_retarget(params: Dict[str, Any]) -> Dict[str, Any]:
    """重定向动作"""
    source_name = params.get("source_armature")
    target_name = params.get("target_armature")
    bone_mapping = params.get("bone_mapping", {})
    
    source = bpy.data.objects.get(source_name)
    target = bpy.data.objects.get(target_name)
    
    if not source or source.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "SOURCE_NOT_FOUND", "message": f"源骨架不存在: {source_name}"}
        }
    
    if not target or target.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "TARGET_NOT_FOUND", "message": f"目标骨架不存在: {target_name}"}
        }
    
    try:
        # 获取源动作
        if not source.animation_data or not source.animation_data.action:
            return {
                "success": False,
                "error": {"code": "NO_ACTION", "message": "源骨架没有动作数据"}
            }
        
        source_action = source.animation_data.action
        
        # 创建新动作
        new_action = bpy.data.actions.new(name=f"{source_action.name}_retargeted")
        
        # 确保目标有动画数据
        if not target.animation_data:
            target.animation_data_create()
        
        # 自动骨骼映射（如果没有提供）
        if not bone_mapping:
            # 尝试匹配同名骨骼
            for source_bone in source.data.bones:
                if source_bone.name in target.data.bones:
                    bone_mapping[source_bone.name] = source_bone.name
        
        # 复制 FCurves
        for fcurve in source_action.fcurves:
            # 解析数据路径
            data_path = fcurve.data_path
            
            # 检查是否是骨骼相关的曲线
            if 'pose.bones' in data_path:
                # 提取骨骼名
                try:
                    bone_name = data_path.split('"')[1]
                    
                    # 查找映射
                    target_bone_name = bone_mapping.get(bone_name, bone_name)
                    
                    if target_bone_name in target.data.bones:
                        # 创建新数据路径
                        new_data_path = data_path.replace(f'"{bone_name}"', f'"{target_bone_name}"')
                        
                        # 复制 FCurve
                        new_fcurve = new_action.fcurves.new(
                            data_path=new_data_path,
                            index=fcurve.array_index
                        )
                        
                        # 复制关键帧
                        for kp in fcurve.keyframe_points:
                            new_fcurve.keyframe_points.insert(kp.co[0], kp.co[1])
                except:
                    continue
        
        # 分配新动作
        target.animation_data.action = new_action
        
        return {
            "success": True,
            "data": {
                "action_name": new_action.name,
                "bones_mapped": len(bone_mapping)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "RETARGET_ERROR", "message": str(e)}
        }


def handle_clean(params: Dict[str, Any]) -> Dict[str, Any]:
    """清理动作数据"""
    armature_name = params.get("armature_name")
    action_name = params.get("action_name")
    threshold = params.get("threshold", 0.001)
    remove_noise = params.get("remove_noise", True)
    
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    try:
        # 获取动作
        action = None
        if action_name:
            action = bpy.data.actions.get(action_name)
        elif armature.animation_data and armature.animation_data.action:
            action = armature.animation_data.action
        
        if not action:
            return {
                "success": False,
                "error": {"code": "NO_ACTION", "message": "未找到动作数据"}
            }
        
        cleaned_count = 0
        
        if remove_noise:
            # 选择骨架
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            
            # 进入姿态模式
            bpy.ops.object.mode_set(mode='POSE')
            
            # 选择所有骨骼
            bpy.ops.pose.select_all(action='SELECT')
            
            # 清理关键帧
            try:
                bpy.ops.action.clean(threshold=threshold)
                cleaned_count = 1
            except:
                pass
            
            # 返回对象模式
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # 移除冗余关键帧
        for fcurve in action.fcurves:
            # 移除几乎相同的连续关键帧
            points_to_remove = []
            prev_value = None
            
            for i, kp in enumerate(fcurve.keyframe_points):
                if prev_value is not None:
                    if abs(kp.co[1] - prev_value) < threshold:
                        points_to_remove.append(i)
                prev_value = kp.co[1]
            
            # 从后往前删除
            for i in reversed(points_to_remove):
                if 0 < i < len(fcurve.keyframe_points) - 1:  # 保留首尾
                    fcurve.keyframe_points.remove(fcurve.keyframe_points[i])
                    cleaned_count += 1
        
        return {
            "success": True,
            "data": {
                "action_name": action.name,
                "cleaned_keyframes": cleaned_count
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CLEAN_ERROR", "message": str(e)}
        }


def handle_blend(params: Dict[str, Any]) -> Dict[str, Any]:
    """混合动作"""
    armature_name = params.get("armature_name")
    action1_name = params.get("action1")
    action2_name = params.get("action2")
    blend_factor = params.get("blend_factor", 0.5)
    output_name = params.get("output_name", "BlendedAction")
    
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    action1 = bpy.data.actions.get(action1_name)
    action2 = bpy.data.actions.get(action2_name)
    
    if not action1:
        return {
            "success": False,
            "error": {"code": "ACTION_NOT_FOUND", "message": f"动作1不存在: {action1_name}"}
        }
    
    if not action2:
        return {
            "success": False,
            "error": {"code": "ACTION_NOT_FOUND", "message": f"动作2不存在: {action2_name}"}
        }
    
    try:
        # 创建新动作
        blended_action = bpy.data.actions.new(name=output_name)
        
        # 获取所有数据路径
        all_paths = set()
        for fc in action1.fcurves:
            all_paths.add((fc.data_path, fc.array_index))
        for fc in action2.fcurves:
            all_paths.add((fc.data_path, fc.array_index))
        
        # 混合每个 FCurve
        for data_path, array_index in all_paths:
            fc1 = action1.fcurves.find(data_path, index=array_index)
            fc2 = action2.fcurves.find(data_path, index=array_index)
            
            if fc1 or fc2:
                new_fc = blended_action.fcurves.new(data_path=data_path, index=array_index)
                
                # 获取所有关键帧时间点
                frames = set()
                if fc1:
                    for kp in fc1.keyframe_points:
                        frames.add(int(kp.co[0]))
                if fc2:
                    for kp in fc2.keyframe_points:
                        frames.add(int(kp.co[0]))
                
                # 在每个帧混合值
                for frame in sorted(frames):
                    val1 = fc1.evaluate(frame) if fc1 else 0
                    val2 = fc2.evaluate(frame) if fc2 else 0
                    
                    blended_value = val1 * (1 - blend_factor) + val2 * blend_factor
                    new_fc.keyframe_points.insert(frame, blended_value)
        
        # 分配混合后的动作
        if not armature.animation_data:
            armature.animation_data_create()
        armature.animation_data.action = blended_action
        
        return {
            "success": True,
            "data": {
                "action_name": blended_action.name,
                "blend_factor": blend_factor
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BLEND_ERROR", "message": str(e)}
        }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙动作"""
    armature_name = params.get("armature_name")
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 250)
    only_selected = params.get("only_selected", False)
    visual_keying = params.get("visual_keying", True)
    
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    try:
        # 选择骨架
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        
        # 进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')
        
        # 选择骨骼
        if not only_selected:
            bpy.ops.pose.select_all(action='SELECT')
        
        # 烘焙动作
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=only_selected,
            visual_keying=visual_keying,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=True,
            bake_types={'POSE'}
        )
        
        # 返回对象模式
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {
            "success": True,
            "data": {
                "armature": armature_name,
                "frame_range": [frame_start, frame_end]
            }
        }
    
    except Exception as e:
        # 确保返回对象模式
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        
        return {
            "success": False,
            "error": {"code": "BAKE_ERROR", "message": str(e)}
        }
