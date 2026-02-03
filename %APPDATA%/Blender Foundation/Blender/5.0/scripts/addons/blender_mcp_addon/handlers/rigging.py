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
