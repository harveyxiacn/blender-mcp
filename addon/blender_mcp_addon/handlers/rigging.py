"""
骨骼绑定处理器

处理骨骼和绑定相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_armature_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建骨架"""
    name = params.get("name", "Armature")
    location = params.get("location", [0, 0, 0])
    
    # 创建骨架数据
    arm_data = bpy.data.armatures.new(name=name)
    
    # 创建骨架对象
    arm_obj = bpy.data.objects.new(name=name, object_data=arm_data)
    arm_obj.location = location
    
    # 链接到场景
    bpy.context.collection.objects.link(arm_obj)
    
    return {
        "success": True,
        "data": {
            "armature_name": arm_obj.name
        }
    }


def handle_bone_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加骨骼"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    head = params.get("head", [0, 0, 0])
    tail = params.get("tail", [0, 0, 1])
    parent = params.get("parent")
    use_connect = params.get("use_connect", False)
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 切换到编辑模式
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 创建骨骼
    arm = obj.data
    bone = arm.edit_bones.new(bone_name)
    bone.head = head
    bone.tail = tail
    
    # 设置父骨骼
    if parent:
        parent_bone = arm.edit_bones.get(parent)
        if parent_bone:
            bone.parent = parent_bone
            bone.use_connect = use_connect
    
    # 返回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "bone_name": bone_name
        }
    }


def handle_generate_rig(params: Dict[str, Any]) -> Dict[str, Any]:
    """生成角色绑定"""
    target_mesh = params.get("target_mesh")
    rig_type = params.get("rig_type", "HUMAN")
    auto_weights = params.get("auto_weights", True)
    
    mesh_obj = bpy.data.objects.get(target_mesh)
    if not mesh_obj or mesh_obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "MESH_NOT_FOUND",
                "message": f"网格不存在: {target_mesh}"
            }
        }
    
    # 创建基础骨架
    bpy.ops.object.armature_add(location=mesh_obj.location)
    arm_obj = bpy.context.active_object
    arm_obj.name = f"{target_mesh}_Rig"
    
    # 根据绑定类型添加骨骼
    bpy.ops.object.mode_set(mode='EDIT')
    arm = arm_obj.data
    
    # 删除默认骨骼
    for bone in arm.edit_bones:
        arm.edit_bones.remove(bone)
    
    # 添加基础骨骼结构（简化版本）
    if rig_type == "HUMAN":
        # 脊柱
        root = arm.edit_bones.new("root")
        root.head = (0, 0, 0)
        root.tail = (0, 0, 0.2)
        
        spine = arm.edit_bones.new("spine")
        spine.head = (0, 0, 0.2)
        spine.tail = (0, 0, 0.5)
        spine.parent = root
        
        chest = arm.edit_bones.new("chest")
        chest.head = (0, 0, 0.5)
        chest.tail = (0, 0, 0.8)
        chest.parent = spine
        
        neck = arm.edit_bones.new("neck")
        neck.head = (0, 0, 0.8)
        neck.tail = (0, 0, 0.9)
        neck.parent = chest
        
        head = arm.edit_bones.new("head")
        head.head = (0, 0, 0.9)
        head.tail = (0, 0, 1.1)
        head.parent = neck
        
        # 手臂
        for side in ["L", "R"]:
            sign = 1 if side == "L" else -1
            
            shoulder = arm.edit_bones.new(f"shoulder.{side}")
            shoulder.head = (sign * 0.1, 0, 0.75)
            shoulder.tail = (sign * 0.2, 0, 0.75)
            shoulder.parent = chest
            
            upper_arm = arm.edit_bones.new(f"upper_arm.{side}")
            upper_arm.head = (sign * 0.2, 0, 0.75)
            upper_arm.tail = (sign * 0.45, 0, 0.55)
            upper_arm.parent = shoulder
            
            forearm = arm.edit_bones.new(f"forearm.{side}")
            forearm.head = (sign * 0.45, 0, 0.55)
            forearm.tail = (sign * 0.65, 0, 0.35)
            forearm.parent = upper_arm
            forearm.use_connect = True
            
            hand = arm.edit_bones.new(f"hand.{side}")
            hand.head = (sign * 0.65, 0, 0.35)
            hand.tail = (sign * 0.75, 0, 0.3)
            hand.parent = forearm
            hand.use_connect = True
        
        # 腿部
        for side in ["L", "R"]:
            sign = 1 if side == "L" else -1
            
            thigh = arm.edit_bones.new(f"thigh.{side}")
            thigh.head = (sign * 0.1, 0, 0.2)
            thigh.tail = (sign * 0.12, 0.02, -0.2)
            thigh.parent = root
            
            shin = arm.edit_bones.new(f"shin.{side}")
            shin.head = (sign * 0.12, 0.02, -0.2)
            shin.tail = (sign * 0.12, 0, -0.6)
            shin.parent = thigh
            shin.use_connect = True
            
            foot = arm.edit_bones.new(f"foot.{side}")
            foot.head = (sign * 0.12, 0, -0.6)
            foot.tail = (sign * 0.12, -0.15, -0.65)
            foot.parent = shin
            foot.use_connect = True
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 绑定网格到骨架
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    if auto_weights:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    else:
        bpy.ops.object.parent_set(type='ARMATURE')
    
    return {
        "success": True,
        "data": {
            "armature_name": arm_obj.name
        }
    }


def handle_ik_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置 IK"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    target = params.get("target")
    chain_length = params.get("chain_length", 2)
    pole_target = params.get("pole_target")
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 切换到姿势模式
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # 获取姿势骨骼
    pose_bone = obj.pose.bones.get(bone_name)
    if not pose_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {
                "code": "BONE_NOT_FOUND",
                "message": f"骨骼不存在: {bone_name}"
            }
        }
    
    # 添加 IK 约束
    ik = pose_bone.constraints.new(type='IK')
    ik.chain_count = chain_length
    
    # 设置目标
    target_obj = bpy.data.objects.get(target)
    if target_obj:
        ik.target = target_obj
    
    # 设置极向量目标
    if pole_target:
        pole_obj = bpy.data.objects.get(pole_target)
        if pole_obj:
            ik.pole_target = pole_obj
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_pose_set(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置姿势"""
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    location = params.get("location")
    rotation = params.get("rotation")
    rotation_mode = params.get("rotation_mode", "XYZ")
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 切换到姿势模式
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # 获取姿势骨骼
    pose_bone = obj.pose.bones.get(bone_name)
    if not pose_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {
                "code": "BONE_NOT_FOUND",
                "message": f"骨骼不存在: {bone_name}"
            }
        }
    
    # 设置旋转模式
    pose_bone.rotation_mode = rotation_mode
    
    # 设置位置
    if location:
        pose_bone.location = location
    
    # 设置旋转
    if rotation:
        pose_bone.rotation_euler = rotation
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_weight_paint(params: Dict[str, Any]) -> Dict[str, Any]:
    """自动权重绘制"""
    mesh_name = params.get("mesh_name")
    armature_name = params.get("armature_name")
    auto_normalize = params.get("auto_normalize", True)
    
    mesh_obj = bpy.data.objects.get(mesh_name)
    arm_obj = bpy.data.objects.get(armature_name)
    
    if not mesh_obj or mesh_obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "MESH_NOT_FOUND",
                "message": f"网格不存在: {mesh_name}"
            }
        }
    
    if not arm_obj or arm_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 选择网格和骨架
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    # 自动权重
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    return {
        "success": True,
        "data": {}
    }


def handle_armature_bind(params: Dict[str, Any]) -> Dict[str, Any]:
    """将网格绑定到骨架
    
    Args:
        params:
            - mesh_name: 网格对象名称
            - armature_name: 骨架对象名称
            - bind_type: 绑定类型
                - AUTO: 自动权重（推荐）
                - ENVELOPE: 包络线权重
                - EMPTY: 仅绑定，不设置权重
            - preserve_volume: 是否保持体积（防止关节处变形过度）
    """
    mesh_name = params.get("mesh_name")
    armature_name = params.get("armature_name")
    bind_type = params.get("bind_type", "AUTO")
    preserve_volume = params.get("preserve_volume", True)
    
    mesh_obj = bpy.data.objects.get(mesh_name)
    arm_obj = bpy.data.objects.get(armature_name)
    
    if not mesh_obj or mesh_obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "MESH_NOT_FOUND",
                "message": f"网格不存在: {mesh_name}"
            }
        }
    
    if not arm_obj or arm_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 确保在对象模式
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 选择网格和骨架（网格先选，骨架作为活动对象）
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    # 根据绑定类型执行绑定
    try:
        if bind_type == "AUTO":
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        elif bind_type == "ENVELOPE":
            bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
        elif bind_type == "EMPTY":
            bpy.ops.object.parent_set(type='ARMATURE')
        else:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BIND_TYPE",
                    "message": f"不支持的绑定类型: {bind_type}"
                }
            }
        
        # 设置骨架修改器的保持体积选项
        if preserve_volume:
            for mod in mesh_obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object == arm_obj:
                    mod.use_deform_preserve_volume = True
                    break
        
        return {
            "success": True,
            "data": {
                "mesh_name": mesh_obj.name,
                "armature_name": arm_obj.name,
                "bind_type": bind_type,
                "preserve_volume": preserve_volume
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "BIND_ERROR",
                "message": str(e)
            }
        }


def handle_vertex_group_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建顶点组
    
    Args:
        params:
            - object_name: 对象名称
            - group_name: 顶点组名称
            - vertex_indices: 顶点索引列表（可选）
            - weight: 权重值（0.0-1.0）
    """
    object_name = params.get("object_name")
    group_name = params.get("group_name")
    vertex_indices = params.get("vertex_indices", [])
    weight = params.get("weight", 1.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"网格对象不存在: {object_name}"
            }
        }
    
    # 创建顶点组
    vg = obj.vertex_groups.new(name=group_name)
    
    # 如果指定了顶点，添加到组中
    if vertex_indices:
        vg.add(vertex_indices, weight, 'REPLACE')
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "group_name": vg.name,
            "group_index": vg.index
        }
    }


def handle_vertex_group_assign(params: Dict[str, Any]) -> Dict[str, Any]:
    """分配顶点到顶点组
    
    Args:
        params:
            - object_name: 对象名称
            - group_name: 顶点组名称
            - vertex_indices: 顶点索引列表
            - weight: 权重值（0.0-1.0）
            - mode: 分配模式（REPLACE, ADD, SUBTRACT）
    """
    object_name = params.get("object_name")
    group_name = params.get("group_name")
    vertex_indices = params.get("vertex_indices", [])
    weight = params.get("weight", 1.0)
    mode = params.get("mode", "REPLACE")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"网格对象不存在: {object_name}"
            }
        }
    
    vg = obj.vertex_groups.get(group_name)
    if not vg:
        return {
            "success": False,
            "error": {
                "code": "GROUP_NOT_FOUND",
                "message": f"顶点组不存在: {group_name}"
            }
        }
    
    # 分配顶点
    vg.add(vertex_indices, weight, mode)
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "group_name": vg.name,
            "assigned_count": len(vertex_indices)
        }
    }


def handle_bone_constraint_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """为骨骼添加约束
    
    Args:
        params:
            - armature_name: 骨架名称
            - bone_name: 骨骼名称
            - constraint_type: 约束类型（IK, COPY_ROTATION, COPY_LOCATION, LIMIT_ROTATION等）
            - settings: 约束设置
    """
    armature_name = params.get("armature_name")
    bone_name = params.get("bone_name")
    constraint_type = params.get("constraint_type")
    settings = params.get("settings", {})
    
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {
                "code": "ARMATURE_NOT_FOUND",
                "message": f"骨架不存在: {armature_name}"
            }
        }
    
    # 切换到姿势模式
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bone = obj.pose.bones.get(bone_name)
    if not pose_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {
                "code": "BONE_NOT_FOUND",
                "message": f"骨骼不存在: {bone_name}"
            }
        }
    
    # 添加约束
    try:
        constraint = pose_bone.constraints.new(type=constraint_type)
        
        # 应用设置
        for key, value in settings.items():
            if hasattr(constraint, key):
                # 处理对象引用
                if key in ['target', 'pole_target'] and isinstance(value, str):
                    target_obj = bpy.data.objects.get(value)
                    if target_obj:
                        setattr(constraint, key, target_obj)
                else:
                    setattr(constraint, key, value)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {
            "success": True,
            "data": {
                "armature_name": obj.name,
                "bone_name": bone_name,
                "constraint_name": constraint.name,
                "constraint_type": constraint_type
            }
        }
    except Exception as e:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {
            "success": False,
            "error": {
                "code": "CONSTRAINT_ERROR",
                "message": str(e)
            }
        }
