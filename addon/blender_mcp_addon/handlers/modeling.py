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


# ==================== 形态键（Shape Keys）功能 ====================

def handle_shapekey_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建形态键
    
    Args:
        params:
            - object_name: 对象名称
            - key_name: 形态键名称
            - from_mix: 是否从当前混合状态创建
    """
    object_name = params.get("object_name")
    key_name = params.get("key_name", "Key")
    from_mix = params.get("from_mix", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_TYPE",
                "message": "形态键只支持网格对象"
            }
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 确保在对象模式
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 如果没有形态键，先创建基础形态键
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    
    # 创建新形态键
    shape_key = obj.shape_key_add(name=key_name, from_mix=from_mix)
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "key_name": shape_key.name,
            "key_index": len(obj.data.shape_keys.key_blocks) - 1
        }
    }


def handle_shapekey_edit(params: Dict[str, Any]) -> Dict[str, Any]:
    """编辑形态键
    
    Args:
        params:
            - object_name: 对象名称
            - key_name: 形态键名称
            - vertex_offsets: 顶点偏移列表 [{"index": int, "offset": [x, y, z]}, ...]
            - value: 形态键值 (0.0 - 1.0)
            - mute: 是否静音
    """
    object_name = params.get("object_name")
    key_name = params.get("key_name")
    vertex_offsets = params.get("vertex_offsets", [])
    value = params.get("value")
    mute = params.get("mute")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if not obj.data.shape_keys:
        return {
            "success": False,
            "error": {
                "code": "NO_SHAPE_KEYS",
                "message": "对象没有形态键"
            }
        }
    
    shape_key = obj.data.shape_keys.key_blocks.get(key_name)
    if not shape_key:
        return {
            "success": False,
            "error": {
                "code": "SHAPE_KEY_NOT_FOUND",
                "message": f"形态键不存在: {key_name}"
            }
        }
    
    # 设置值
    if value is not None:
        shape_key.value = value
    
    # 设置静音
    if mute is not None:
        shape_key.mute = mute
    
    # 应用顶点偏移
    if vertex_offsets:
        basis = obj.data.shape_keys.key_blocks.get("Basis")
        if not basis:
            return {
                "success": False,
                "error": {
                    "code": "NO_BASIS",
                    "message": "找不到基础形态键"
                }
            }
        
        for offset_data in vertex_offsets:
            idx = offset_data.get("index")
            offset = offset_data.get("offset", [0, 0, 0])
            
            if idx is not None and 0 <= idx < len(shape_key.data):
                # 获取基础位置并应用偏移
                base_co = basis.data[idx].co
                shape_key.data[idx].co = (
                    base_co.x + offset[0],
                    base_co.y + offset[1],
                    base_co.z + offset[2]
                )
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "key_name": key_name,
            "value": shape_key.value,
            "mute": shape_key.mute
        }
    }


def handle_shapekey_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除形态键
    
    Args:
        params:
            - object_name: 对象名称
            - key_name: 形态键名称
    """
    object_name = params.get("object_name")
    key_name = params.get("key_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if not obj.data.shape_keys:
        return {
            "success": False,
            "error": {
                "code": "NO_SHAPE_KEYS",
                "message": "对象没有形态键"
            }
        }
    
    # 找到形态键索引
    key_index = None
    for i, key in enumerate(obj.data.shape_keys.key_blocks):
        if key.name == key_name:
            key_index = i
            break
    
    if key_index is None:
        return {
            "success": False,
            "error": {
                "code": "SHAPE_KEY_NOT_FOUND",
                "message": f"形态键不存在: {key_name}"
            }
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 设置活动形态键
    obj.active_shape_key_index = key_index
    
    # 删除形态键
    bpy.ops.object.shape_key_remove()
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "deleted_key": key_name
        }
    }


def handle_shapekey_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出形态键
    
    Args:
        params:
            - object_name: 对象名称
    """
    object_name = params.get("object_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if not obj.data.shape_keys:
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "shape_keys": [],
                "total": 0
            }
        }
    
    keys = []
    for i, key in enumerate(obj.data.shape_keys.key_blocks):
        keys.append({
            "index": i,
            "name": key.name,
            "value": key.value,
            "mute": key.mute,
            "slider_min": key.slider_min,
            "slider_max": key.slider_max
        })
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "shape_keys": keys,
            "total": len(keys)
        }
    }


def handle_shapekey_create_expression(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建表情形态键集
    
    为角色快速创建一组常用表情形态键。
    
    Args:
        params:
            - object_name: 对象名称
            - expressions: 要创建的表情列表，可选值:
                - smile: 微笑
                - frown: 皱眉
                - surprise: 惊讶
                - angry: 愤怒
                - sad: 悲伤
                - blink_l: 左眼闭合
                - blink_r: 右眼闭合
                - blink: 双眼闭合
                - mouth_open: 张嘴
                - mouth_wide: 大张嘴
    """
    object_name = params.get("object_name")
    expressions = params.get("expressions", ["smile", "blink", "surprise", "angry"])
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_TYPE",
                "message": "形态键只支持网格对象"
            }
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 确保有基础形态键
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    
    # 表情名称映射
    expression_names = {
        "smile": "Smile_微笑",
        "frown": "Frown_皱眉",
        "surprise": "Surprise_惊讶",
        "angry": "Angry_愤怒",
        "sad": "Sad_悲伤",
        "blink_l": "Blink_L_左眼闭合",
        "blink_r": "Blink_R_右眼闭合",
        "blink": "Blink_双眼闭合",
        "mouth_open": "MouthOpen_张嘴",
        "mouth_wide": "MouthWide_大张嘴"
    }
    
    created_keys = []
    for expr in expressions:
        name = expression_names.get(expr, expr)
        # 检查是否已存在
        if obj.data.shape_keys.key_blocks.get(name):
            continue
        
        shape_key = obj.shape_key_add(name=name, from_mix=False)
        created_keys.append(shape_key.name)
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "created_keys": created_keys,
            "total": len(created_keys)
        }
    }


def handle_mesh_assign_material_to_faces(params: Dict[str, Any]) -> Dict[str, Any]:
    """给特定面分配材质
    
    Args:
        params:
            - object_name: 对象名称
            - face_indices: 面索引列表
            - material_slot: 材质槽索引
            - material_name: 或者通过材质名称指定
    """
    object_name = params.get("object_name")
    face_indices = params.get("face_indices", [])
    material_slot = params.get("material_slot")
    material_name = params.get("material_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_TYPE",
                "message": "只支持网格对象"
            }
        }
    
    # 通过材质名称找到槽索引
    if material_name and material_slot is None:
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name == material_name:
                material_slot = i
                break
        
        if material_slot is None:
            return {
                "success": False,
                "error": {
                    "code": "MATERIAL_NOT_FOUND",
                    "message": f"材质不在对象的材质槽中: {material_name}"
                }
            }
    
    if material_slot is None:
        return {
            "success": False,
            "error": {
                "code": "INVALID_PARAMS",
                "message": "请指定 material_slot 或 material_name"
            }
        }
    
    if material_slot >= len(obj.material_slots):
        return {
            "success": False,
            "error": {
                "code": "INVALID_SLOT",
                "message": f"材质槽索引超出范围: {material_slot}"
            }
        }
    
    # 分配材质到面
    mesh = obj.data
    
    # 确保在对象模式
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    assigned_count = 0
    for idx in face_indices:
        if 0 <= idx < len(mesh.polygons):
            mesh.polygons[idx].material_index = material_slot
            assigned_count += 1
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "material_slot": material_slot,
            "assigned_faces": assigned_count
        }
    }


def handle_select_faces_by_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """按材质选择面
    
    Args:
        params:
            - object_name: 对象名称
            - material_slot: 材质槽索引
            - material_name: 或通过材质名称指定
    """
    object_name = params.get("object_name")
    material_slot = params.get("material_slot")
    material_name = params.get("material_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {object_name}"
            }
        }
    
    if obj.type != 'MESH':
        return {
            "success": False,
            "error": {
                "code": "INVALID_TYPE",
                "message": "只支持网格对象"
            }
        }
    
    # 通过材质名称找到槽索引
    if material_name and material_slot is None:
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name == material_name:
                material_slot = i
                break
    
    if material_slot is None:
        return {
            "success": False,
            "error": {
                "code": "INVALID_PARAMS",
                "message": "请指定 material_slot 或 material_name"
            }
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 取消所有选择
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # 设置面选择模式
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)
    
    # 设置活动材质槽
    obj.active_material_index = material_slot
    
    # 选择使用该材质的面
    bpy.ops.object.material_slot_select()
    
    # 返回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 统计选中的面数
    selected_count = sum(1 for p in obj.data.polygons if p.select)
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "material_slot": material_slot,
            "selected_faces": selected_count
        }
    }
