"""
自动骨骼绑定处理器

处理骨骼创建、权重绑定、IK设置等命令。
"""

from typing import Any, Dict, List
import bpy
import math


# 人形骨骼配置
HUMANOID_BONES = {
    "root": {"head": [0, 0, 0], "tail": [0, 0, 0.1]},
    "spine": {"head": [0, 0, 0.1], "tail": [0, 0, 0.3], "parent": "root"},
    "spine.001": {"head": [0, 0, 0.3], "tail": [0, 0, 0.5], "parent": "spine"},
    "spine.002": {"head": [0, 0, 0.5], "tail": [0, 0, 0.7], "parent": "spine.001"},
    "neck": {"head": [0, 0, 0.7], "tail": [0, 0, 0.8], "parent": "spine.002"},
    "head": {"head": [0, 0, 0.8], "tail": [0, 0, 1.0], "parent": "neck"},
    
    # 左臂
    "shoulder.L": {"head": [0, 0, 0.65], "tail": [0.1, 0, 0.65], "parent": "spine.002"},
    "upper_arm.L": {"head": [0.1, 0, 0.65], "tail": [0.3, 0, 0.65], "parent": "shoulder.L"},
    "forearm.L": {"head": [0.3, 0, 0.65], "tail": [0.5, 0, 0.65], "parent": "upper_arm.L"},
    "hand.L": {"head": [0.5, 0, 0.65], "tail": [0.6, 0, 0.65], "parent": "forearm.L"},
    
    # 右臂
    "shoulder.R": {"head": [0, 0, 0.65], "tail": [-0.1, 0, 0.65], "parent": "spine.002"},
    "upper_arm.R": {"head": [-0.1, 0, 0.65], "tail": [-0.3, 0, 0.65], "parent": "shoulder.R"},
    "forearm.R": {"head": [-0.3, 0, 0.65], "tail": [-0.5, 0, 0.65], "parent": "upper_arm.R"},
    "hand.R": {"head": [-0.5, 0, 0.65], "tail": [-0.6, 0, 0.65], "parent": "forearm.R"},
    
    # 左腿
    "thigh.L": {"head": [0.1, 0, 0.1], "tail": [0.1, 0, -0.3], "parent": "root"},
    "shin.L": {"head": [0.1, 0, -0.3], "tail": [0.1, 0, -0.6], "parent": "thigh.L"},
    "foot.L": {"head": [0.1, 0, -0.6], "tail": [0.1, -0.1, -0.65], "parent": "shin.L"},
    "toe.L": {"head": [0.1, -0.1, -0.65], "tail": [0.1, -0.2, -0.65], "parent": "foot.L"},
    
    # 右腿
    "thigh.R": {"head": [-0.1, 0, 0.1], "tail": [-0.1, 0, -0.3], "parent": "root"},
    "shin.R": {"head": [-0.1, 0, -0.3], "tail": [-0.1, 0, -0.6], "parent": "thigh.R"},
    "foot.R": {"head": [-0.1, 0, -0.6], "tail": [-0.1, -0.1, -0.65], "parent": "shin.R"},
    "toe.R": {"head": [-0.1, -0.1, -0.65], "tail": [-0.1, -0.2, -0.65], "parent": "foot.R"},
}

# 简单骨骼配置
SIMPLE_BONES = {
    "root": {"head": [0, 0, 0], "tail": [0, 0, 0.2]},
    "body": {"head": [0, 0, 0.2], "tail": [0, 0, 0.6], "parent": "root"},
    "head": {"head": [0, 0, 0.6], "tail": [0, 0, 0.9], "parent": "body"},
}

POSE_PRESETS = {
    "t_pose": {
        "upper_arm.L": [0, 0, 0],
        "upper_arm.R": [0, 0, 0],
        "forearm.L": [0, 0, 0],
        "forearm.R": [0, 0, 0],
    },
    "a_pose": {
        "upper_arm.L": [0, 0, 0.5],
        "upper_arm.R": [0, 0, -0.5],
        "forearm.L": [0, 0, 0],
        "forearm.R": [0, 0, 0],
    },
    "rest": {},
}


def handle_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """自动创建骨骼系统"""
    character_name = params.get("character_name")
    rig_type = params.get("rig_type", "humanoid")
    auto_weight = params.get("auto_weight", True)
    symmetric = params.get("symmetric", True)
    
    # 获取角色对象
    body = bpy.data.objects.get(f"{character_name}_Body")
    head = bpy.data.objects.get(f"{character_name}_Head")
    
    if not body:
        return {
            "success": False,
            "error": {"code": "BODY_NOT_FOUND", "message": f"找不到角色: {character_name}"}
        }
    
    # 计算角色尺寸
    all_parts = [obj for obj in bpy.data.objects if obj.name.startswith(f"{character_name}_")]
    if not all_parts:
        return {
            "success": False,
            "error": {"code": "NO_PARTS", "message": "找不到角色部件"}
        }
    
    # 计算边界框
    min_z = min(obj.location.z - obj.dimensions.z/2 for obj in all_parts)
    max_z = max(obj.location.z + obj.dimensions.z/2 for obj in all_parts)
    height = max_z - min_z
    center_x = sum(obj.location.x for obj in all_parts) / len(all_parts)
    center_y = sum(obj.location.y for obj in all_parts) / len(all_parts)
    
    # 选择骨骼配置
    if rig_type == "humanoid":
        bone_config = HUMANOID_BONES
    elif rig_type == "simple":
        bone_config = SIMPLE_BONES
    else:
        bone_config = SIMPLE_BONES
    
    # 创建骨架
    armature_name = f"{character_name}_Armature"
    bpy.ops.object.armature_add(location=[center_x, center_y, min_z])
    armature_obj = bpy.context.active_object
    armature_obj.name = armature_name
    armature = armature_obj.data
    armature.name = armature_name
    
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 删除默认骨骼
    for bone in armature.edit_bones:
        armature.edit_bones.remove(bone)
    
    # 创建骨骼
    created_bones = []
    scale_factor = height / 1.0  # 假设配置是基于单位高度
    
    for bone_name, config in bone_config.items():
        bone = armature.edit_bones.new(bone_name)
        
        # 缩放位置
        head_pos = [p * scale_factor for p in config["head"]]
        tail_pos = [p * scale_factor for p in config["tail"]]
        
        bone.head = head_pos
        bone.tail = tail_pos
        
        # 设置父骨骼
        parent_name = config.get("parent")
        if parent_name and parent_name in armature.edit_bones:
            bone.parent = armature.edit_bones[parent_name]
            if config.get("connect", False):
                bone.use_connect = True
        
        created_bones.append(bone_name)
    
    # 退出编辑模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 自动权重绑定
    if auto_weight:
        for part in all_parts:
            if part.type == 'MESH':
                # 添加骨架修改器
                modifier = part.modifiers.new(name="Armature", type='ARMATURE')
                modifier.object = armature_obj
                
                # 选择对象进行自动权重
                bpy.ops.object.select_all(action='DESELECT')
                part.select_set(True)
                armature_obj.select_set(True)
                bpy.context.view_layer.objects.active = armature_obj
                
                try:
                    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
                except:
                    # 如果自动权重失败，使用骨架变形
                    bpy.ops.object.parent_set(type='ARMATURE')
    
    return {
        "success": True,
        "data": {
            "armature_name": armature_name,
            "bones_created": len(created_bones),
            "bones": created_bones
        }
    }


def handle_bone_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """手动添加骨骼"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    head = params.get("head")
    tail = params.get("tail")
    parent_bone = params.get("parent_bone")
    connect = params.get("connect", False)
    
    armature_obj = bpy.data.objects.get(armature_name)
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    # 进入编辑模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    armature = armature_obj.data
    
    # 创建骨骼
    bone = armature.edit_bones.new(bone_name)
    bone.head = head
    bone.tail = tail
    
    # 设置父骨骼
    if parent_bone and parent_bone in armature.edit_bones:
        bone.parent = armature.edit_bones[parent_bone]
        bone.use_connect = connect
    
    # 退出编辑模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "bone_name": bone_name
        }
    }


def handle_ik_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置IK约束"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    chain_length = params.get("chain_length", 2)
    target_name = params.get("target_name")
    pole_target = params.get("pole_target")
    
    armature_obj = bpy.data.objects.get(armature_name)
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    # 进入姿态模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # 获取骨骼
    pose_bone = armature_obj.pose.bones.get(bone_name)
    if not pose_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {"code": "BONE_NOT_FOUND", "message": f"骨骼不存在: {bone_name}"}
        }
    
    # 添加IK约束
    ik_constraint = pose_bone.constraints.new('IK')
    ik_constraint.chain_count = chain_length
    
    # 设置目标
    if target_name:
        target_obj = bpy.data.objects.get(target_name)
        if target_obj:
            ik_constraint.target = target_obj
    
    # 设置极向量
    if pole_target:
        pole_obj = bpy.data.objects.get(pole_target)
        if pole_obj:
            ik_constraint.pole_target = pole_obj
            ik_constraint.pole_angle = math.radians(90)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "bone_name": bone_name,
            "chain_length": chain_length
        }
    }


def handle_weight_paint(params: Dict[str, Any]) -> Dict[str, Any]:
    """自动权重绑定"""
    object_name = params.get("object_name")
    armature_name = params.get("armature_name")
    method = params.get("method", "automatic")
    
    obj = bpy.data.objects.get(object_name)
    armature_obj = bpy.data.objects.get(armature_name)
    
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    
    # 根据方法选择绑定类型
    if method == "automatic":
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    elif method == "envelope":
        bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
    else:
        bpy.ops.object.parent_set(type='ARMATURE')
    
    return {
        "success": True,
        "data": {
            "object_name": object_name,
            "method": method
        }
    }


def handle_pose_apply(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用预设姿势"""
    armature_name = params.get("armature_name")
    pose_name = params.get("pose_name", "t_pose")
    
    armature_obj = bpy.data.objects.get(armature_name)
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    pose_config = POSE_PRESETS.get(pose_name, {})
    
    # 进入姿态模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # 重置所有骨骼
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.scale_clear()
    
    # 应用姿势
    for bone_name, rotation in pose_config.items():
        pose_bone = armature_obj.pose.bones.get(bone_name)
        if pose_bone:
            pose_bone.rotation_euler = rotation
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "pose_name": pose_name
        }
    }


def handle_constraint_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加骨骼约束"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    constraint_type = params.get("constraint_type", "COPY_ROTATION")
    target_armature = params.get("target_armature")
    target_bone = params.get("target_bone")
    
    armature_obj = bpy.data.objects.get(armature_name)
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    # 进入姿态模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bone = armature_obj.pose.bones.get(bone_name)
    if not pose_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {"code": "BONE_NOT_FOUND", "message": f"骨骼不存在: {bone_name}"}
        }
    
    # 添加约束
    constraint = pose_bone.constraints.new(constraint_type)
    
    # 设置目标
    if target_armature:
        target_obj = bpy.data.objects.get(target_armature)
        if target_obj:
            constraint.target = target_obj
            if target_bone:
                constraint.subtarget = target_bone
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "constraint_type": constraint_type
        }
    }
