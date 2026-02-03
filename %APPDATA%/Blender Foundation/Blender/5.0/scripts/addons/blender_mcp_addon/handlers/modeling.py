"""
建模处理器

处理建模相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_edit_mode(params: Dict[str, Any]) -> Dict[str, Any]:
    """进入/退出编辑模式"""
    object_name = params.get("object_name")
    enter = params.get("enter", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 切换模式
    if enter:
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "mode": bpy.context.mode
        }
    }


def handle_select(params: Dict[str, Any]) -> Dict[str, Any]:
    """网格选择"""
    object_name = params.get("object_name")
    select_mode = params.get("select_mode", "VERT")
    action = params.get("action", "ALL")
    random_ratio = params.get("random_ratio", 0.5)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_OBJECT",
                "message": "对象不存在或不是网格"
            }
        }
    
    # 确保在编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 设置选择模式
    mode_map = {
        "VERT": (True, False, False),
        "EDGE": (False, True, False),
        "FACE": (False, False, True)
    }
    bpy.context.tool_settings.mesh_select_mode = mode_map.get(select_mode, (True, False, False))
    
    # 执行选择操作
    if action == "ALL":
        bpy.ops.mesh.select_all(action='SELECT')
    elif action == "NONE":
        bpy.ops.mesh.select_all(action='DESELECT')
    elif action == "INVERT":
        bpy.ops.mesh.select_all(action='INVERT')
    elif action == "RANDOM":
        bpy.ops.mesh.select_random(ratio=random_ratio)
    elif action == "LINKED":
        bpy.ops.mesh.select_linked()
    
    return {
        "success": True,
        "data": {}
    }


def handle_extrude(params: Dict[str, Any]) -> Dict[str, Any]:
    """挤出"""
    object_name = params.get("object_name")
    direction = params.get("direction", [0, 0, 1])
    distance = params.get("distance", 1.0)
    use_normal = params.get("use_normal", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_OBJECT",
                "message": "对象不存在或不是网格"
            }
        }
    
    # 确保在编辑模式
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # 挤出
    if use_normal:
        bpy.ops.mesh.extrude_region_shrink_fatten(
            TRANSFORM_OT_shrink_fatten={"value": distance}
        )
    else:
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (
                direction[0] * distance,
                direction[1] * distance,
                direction[2] * distance
            )}
        )
    
    return {
        "success": True,
        "data": {}
    }


def handle_subdivide(params: Dict[str, Any]) -> Dict[str, Any]:
    """细分"""
    object_name = params.get("object_name")
    cuts = params.get("cuts", 1)
    smoothness = params.get("smoothness", 0.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_OBJECT",
                "message": "对象不存在或不是网格"
            }
        }
    
    # 确保在编辑模式
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.mesh.subdivide(number_cuts=cuts, smoothness=smoothness)
    
    return {
        "success": True,
        "data": {}
    }


def handle_bevel(params: Dict[str, Any]) -> Dict[str, Any]:
    """倒角"""
    object_name = params.get("object_name")
    width = params.get("width", 0.1)
    segments = params.get("segments", 1)
    profile = params.get("profile", 0.5)
    affect = params.get("affect", "EDGES")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_OBJECT",
                "message": "对象不存在或不是网格"
            }
        }
    
    # 确保在编辑模式
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')
    
    bpy.ops.mesh.bevel(
        offset=width,
        segments=segments,
        profile=profile,
        affect=affect
    )
    
    return {
        "success": True,
        "data": {}
    }


def handle_modifier_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加修改器"""
    object_name = params.get("object_name")
    modifier_type = params.get("modifier_type")
    modifier_name = params.get("modifier_name")
    settings = params.get("settings", {})
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    # 确保在对象模式
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 添加修改器
    mod = obj.modifiers.new(name=modifier_name or modifier_type, type=modifier_type)
    
    # 应用设置
    for key, value in settings.items():
        if hasattr(mod, key):
            setattr(mod, key, value)
    
    return {
        "success": True,
        "data": {
            "modifier_name": mod.name
        }
    }


def handle_modifier_apply(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用修改器"""
    object_name = params.get("object_name")
    modifier_name = params.get("modifier_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    mod = obj.modifiers.get(modifier_name)
    if not mod:
        return {
            "success": False,
            "error": {
                "code": "MODIFIER_NOT_FOUND",
                "message": f"修改器不存在: {modifier_name}"
            }
        }
    
    # 确保在对象模式
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.modifier_apply(modifier=modifier_name)
    
    return {
        "success": True,
        "data": {}
    }


def handle_modifier_remove(params: Dict[str, Any]) -> Dict[str, Any]:
    """移除修改器"""
    object_name = params.get("object_name")
    modifier_name = params.get("modifier_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    mod = obj.modifiers.get(modifier_name)
    if not mod:
        return {
            "success": False,
            "error": {
                "code": "MODIFIER_NOT_FOUND",
                "message": f"修改器不存在: {modifier_name}"
            }
        }
    
    obj.modifiers.remove(mod)
    
    return {
        "success": True,
        "data": {}
    }


def handle_boolean(params: Dict[str, Any]) -> Dict[str, Any]:
    """布尔运算"""
    object_name = params.get("object_name")
    target_name = params.get("target_name")
    operation = params.get("operation", "DIFFERENCE")
    apply = params.get("apply", True)
    hide_target = params.get("hide_target", True)
    
    obj = bpy.data.objects.get(object_name)
    target = bpy.data.objects.get(target_name)
    
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if not target:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"目标对象不存在: {target_name}"
            }
        }
    
    # 添加布尔修改器
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = operation
    mod.object = target
    
    # 应用修改器
    if apply:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    # 隐藏目标
    if hide_target:
        target.hide_viewport = True
        target.hide_render = True
    
    return {
        "success": True,
        "data": {}
    }
