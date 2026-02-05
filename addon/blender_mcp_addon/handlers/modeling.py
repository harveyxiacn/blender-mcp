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


# ==================== 生产标准优化工具 ====================

# 平台三角形限制配置
PLATFORM_LIMITS = {
    "MOBILE": {"min": 500, "max": 2000, "recommended": 1500},
    "PC_CONSOLE": {"min": 2000, "max": 50000, "recommended": 20000},
    "CINEMATIC": {"min": 0, "max": float('inf'), "recommended": 100000},
    "VR": {"min": 1000, "max": 10000, "recommended": 5000}
}


def handle_mesh_analyze(params: Dict[str, Any]) -> Dict[str, Any]:
    """分析网格拓扑质量
    
    Args:
        params:
            - object_name: 对象名称
            - target_platform: 目标平台
    """
    import bmesh
    
    object_name = params.get("object_name")
    target_platform = params.get("target_platform", "PC_CONSOLE")
    
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
    
    mesh = obj.data
    
    # 基础统计
    vertex_count = len(mesh.vertices)
    edge_count = len(mesh.edges)
    face_count = len(mesh.polygons)
    
    # 计算三角形数量和面类型分布
    tris = 0
    quads = 0
    ngons = 0
    triangle_count = 0
    
    for poly in mesh.polygons:
        vert_count = len(poly.vertices)
        if vert_count == 3:
            tris += 1
            triangle_count += 1
        elif vert_count == 4:
            quads += 1
            triangle_count += 2  # 一个四边形 = 2个三角形
        else:
            ngons += 1
            triangle_count += vert_count - 2  # N-gon转三角形数量
    
    # 计算百分比
    total_faces = max(face_count, 1)
    tris_percent = (tris / total_faces) * 100
    quads_percent = (quads / total_faces) * 100
    ngons_percent = (ngons / total_faces) * 100
    
    # 使用bmesh进行高级分析
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # 检测问题
    issues = []
    
    # 非流形边
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    if non_manifold_edges:
        issues.append(f"非流形边: {len(non_manifold_edges)} 条")
    
    # 非流形顶点
    non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
    if non_manifold_verts:
        issues.append(f"非流形顶点: {len(non_manifold_verts)} 个")
    
    # 孤立顶点
    loose_verts = [v for v in bm.verts if not v.link_edges]
    if loose_verts:
        issues.append(f"孤立顶点: {len(loose_verts)} 个")
    
    # 孤立边
    loose_edges = [e for e in bm.edges if not e.link_faces]
    if loose_edges:
        issues.append(f"孤立边: {len(loose_edges)} 条")
    
    # 退化面（面积为0）
    degenerate_faces = [f for f in bm.faces if f.calc_area() < 1e-8]
    if degenerate_faces:
        issues.append(f"退化面: {len(degenerate_faces)} 个")
    
    # N-gon警告
    if ngons > 0:
        issues.append(f"包含N-gon，可能导致变形问题")
    
    # 检查法线一致性（简单检查是否有反向法线）
    # 通过检查面法线方向的一致性
    
    bm.free()
    
    # 平台兼容性检查
    limits = PLATFORM_LIMITS.get(target_platform, PLATFORM_LIMITS["PC_CONSOLE"])
    platform_passed = limits["min"] <= triangle_count <= limits["max"]
    
    suggestion = ""
    if triangle_count > limits["max"]:
        suggestion = f"面数过高，建议使用网格优化工具减少到 {limits['recommended']} 以下"
    elif triangle_count < limits["min"]:
        suggestion = f"面数过低，可能需要增加细节"
    
    # 计算质量评分（0-100）
    quality_score = 100
    
    # N-gon惩罚
    if ngons_percent > 0:
        quality_score -= min(20, ngons_percent)
    
    # 问题惩罚
    quality_score -= min(30, len(issues) * 5)
    
    # 平台兼容性惩罚
    if not platform_passed:
        quality_score -= 20
    
    # 四边形奖励（游戏和动画中首选）
    if quads_percent > 80:
        quality_score = min(100, quality_score + 10)
    
    quality_score = max(0, quality_score)
    
    return {
        "success": True,
        "data": {
            "stats": {
                "vertices": vertex_count,
                "edges": edge_count,
                "faces": face_count,
                "triangles": triangle_count
            },
            "face_types": {
                "tris": tris,
                "tris_percent": tris_percent,
                "quads": quads,
                "quads_percent": quads_percent,
                "ngons": ngons,
                "ngons_percent": ngons_percent
            },
            "platform_check": {
                "passed": platform_passed,
                "min_tris": limits["min"],
                "max_tris": limits["max"] if limits["max"] != float('inf') else "无限制",
                "suggestion": suggestion
            },
            "issues": issues,
            "quality_score": int(quality_score)
        }
    }


def handle_mesh_optimize(params: Dict[str, Any]) -> Dict[str, Any]:
    """优化网格（减面）
    
    Args:
        params:
            - object_name: 对象名称
            - target_triangles: 目标三角形数量
            - target_platform: 目标平台
            - preserve_uvs: 保留UV
            - preserve_normals: 保留法线
            - symmetry: 保持对称性
    """
    object_name = params.get("object_name")
    target_triangles = params.get("target_triangles")
    target_platform = params.get("target_platform", "PC_CONSOLE")
    preserve_uvs = params.get("preserve_uvs", True)
    preserve_normals = params.get("preserve_normals", True)
    symmetry = params.get("symmetry", False)
    
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
    
    # 计算原始三角形数量
    original_triangles = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    
    # 确定目标三角形数量
    if target_triangles is None:
        limits = PLATFORM_LIMITS.get(target_platform, PLATFORM_LIMITS["PC_CONSOLE"])
        target_triangles = limits["recommended"]
    
    # 计算需要的减面比例
    if original_triangles <= target_triangles:
        return {
            "success": True,
            "data": {
                "original_triangles": original_triangles,
                "optimized_triangles": original_triangles,
                "reduction_percent": 0,
                "message": "面数已在目标范围内，无需优化"
            }
        }
    
    ratio = target_triangles / original_triangles
    
    # 添加Decimate修改器
    decimate = obj.modifiers.new(name="MCP_Decimate", type='DECIMATE')
    decimate.decimate_type = 'COLLAPSE'
    decimate.ratio = ratio
    
    # 设置UV和法线保留
    if preserve_uvs:
        decimate.use_collapse_triangulate = False
    
    if symmetry:
        decimate.use_symmetry = True
        decimate.symmetry_axis = 'X'
    
    # 应用修改器
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    
    # 计算优化后的三角形数量
    optimized_triangles = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    reduction_percent = ((original_triangles - optimized_triangles) / original_triangles) * 100
    
    return {
        "success": True,
        "data": {
            "original_triangles": original_triangles,
            "optimized_triangles": optimized_triangles,
            "reduction_percent": reduction_percent
        }
    }


def handle_mesh_cleanup(params: Dict[str, Any]) -> Dict[str, Any]:
    """清理网格
    
    Args:
        params:
            - object_name: 对象名称
            - merge_distance: 合并距离
            - remove_doubles: 移除重复顶点
            - dissolve_degenerate: 溶解退化几何体
            - fix_non_manifold: 修复非流形
            - recalculate_normals: 重新计算法线
            - remove_loose: 移除孤立几何体
    """
    import bmesh
    
    object_name = params.get("object_name")
    merge_distance = params.get("merge_distance", 0.0001)
    remove_doubles = params.get("remove_doubles", True)
    dissolve_degenerate = params.get("dissolve_degenerate", True)
    fix_non_manifold = params.get("fix_non_manifold", True)
    recalculate_normals = params.get("recalculate_normals", True)
    remove_loose = params.get("remove_loose", True)
    
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
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    original_verts = len(obj.data.vertices)
    fixed_issues = 0
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 移除重复顶点
    if remove_doubles:
        result = bpy.ops.mesh.remove_doubles(threshold=merge_distance)
        # 统计移除的顶点在后面计算
    
    # 溶解退化几何体
    if dissolve_degenerate:
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        fixed_issues += 1
    
    # 移除孤立几何体
    if remove_loose:
        bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)
        fixed_issues += 1
    
    # 重新计算法线
    if recalculate_normals:
        bpy.ops.mesh.normals_make_consistent(inside=False)
        fixed_issues += 1
    
    # 修复非流形（尝试填充孔洞）
    if fix_non_manifold:
        # 选择非流形几何体
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        # 尝试填充小孔洞
        try:
            bpy.ops.mesh.fill_holes(sides=4)
            fixed_issues += 1
        except:
            pass  # 如果没有选中的非流形边，则跳过
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 计算移除的顶点数
    removed_verts = original_verts - len(obj.data.vertices)
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "removed_vertices": removed_verts,
            "fixed_issues": fixed_issues
        }
    }


def handle_tris_to_quads(params: Dict[str, Any]) -> Dict[str, Any]:
    """三角形转四边形
    
    Args:
        params:
            - object_name: 对象名称
            - max_angle: 最大角度
            - compare_uvs: 比较UV
            - compare_vcol: 比较顶点色
            - compare_materials: 比较材质
    """
    object_name = params.get("object_name")
    max_angle = params.get("max_angle", 40.0)
    compare_uvs = params.get("compare_uvs", True)
    compare_vcol = params.get("compare_vcol", True)
    compare_materials = params.get("compare_materials", True)
    
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
    
    # 记录原始面数
    original_faces = len(obj.data.polygons)
    original_tris = sum(1 for p in obj.data.polygons if len(p.vertices) == 3)
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 选择所有面
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 转换三角形为四边形
    import math
    bpy.ops.mesh.tris_convert_to_quads(
        face_threshold=math.radians(max_angle),
        shape_threshold=math.radians(max_angle),
        uvs=compare_uvs,
        vcols=compare_vcol,
        seam=False,
        sharp=False,
        materials=compare_materials
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 计算转换后的面数
    new_faces = len(obj.data.polygons)
    converted = original_faces - new_faces  # 每对三角形转换为一个四边形会减少一个面
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "original_tris": original_tris,
            "converted_faces": converted
        }
    }


def handle_lod_generate(params: Dict[str, Any]) -> Dict[str, Any]:
    """生成LOD（细节层次）
    
    Args:
        params:
            - object_name: 对象名称
            - lod_levels: LOD级别数量
            - ratio_step: 每级减少比例
            - create_collection: 是否创建集合
    """
    object_name = params.get("object_name")
    lod_levels = params.get("lod_levels", 3)
    ratio_step = params.get("ratio_step", 0.5)
    create_collection = params.get("create_collection", True)
    
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
    
    # 创建LOD集合
    if create_collection:
        lod_collection_name = f"{obj.name}_LOD"
        if lod_collection_name not in bpy.data.collections:
            lod_collection = bpy.data.collections.new(lod_collection_name)
            bpy.context.scene.collection.children.link(lod_collection)
        else:
            lod_collection = bpy.data.collections[lod_collection_name]
    
    lod_objects = []
    original_triangles = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    
    # LOD0 是原始模型
    lod_objects.append({
        "name": f"{obj.name}_LOD0",
        "triangles": original_triangles,
        "level": 0
    })
    
    # 复制原始对象作为LOD0
    lod0 = obj.copy()
    lod0.data = obj.data.copy()
    lod0.name = f"{obj.name}_LOD0"
    if create_collection:
        lod_collection.objects.link(lod0)
    else:
        bpy.context.scene.collection.objects.link(lod0)
    
    # 生成其他LOD级别
    current_ratio = 1.0
    for level in range(1, lod_levels + 1):
        current_ratio *= ratio_step
        
        # 复制原始对象
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = f"{obj.name}_LOD{level}"
        
        if create_collection:
            lod_collection.objects.link(lod_obj)
        else:
            bpy.context.scene.collection.objects.link(lod_obj)
        
        # 添加Decimate修改器
        decimate = lod_obj.modifiers.new(name="LOD_Decimate", type='DECIMATE')
        decimate.decimate_type = 'COLLAPSE'
        decimate.ratio = current_ratio
        
        # 应用修改器
        bpy.context.view_layer.objects.active = lod_obj
        bpy.ops.object.modifier_apply(modifier=decimate.name)
        
        # 计算三角形数
        lod_triangles = sum(len(p.vertices) - 2 for p in lod_obj.data.polygons)
        
        lod_objects.append({
            "name": lod_obj.name,
            "triangles": lod_triangles,
            "level": level
        })
        
        # 偏移位置以便查看
        lod_obj.location.x = obj.location.x + (level * 3)
    
    return {
        "success": True,
        "data": {
            "original_object": obj.name,
            "lod_objects": lod_objects,
            "collection": lod_collection.name if create_collection else None
        }
    }


def handle_smart_subdivide(params: Dict[str, Any]) -> Dict[str, Any]:
    """智能细分
    
    Args:
        params:
            - object_name: 对象名称
            - levels: 细分级别
            - render_levels: 渲染级别
            - use_creases: 使用折痕边
            - apply_smooth: 应用平滑着色
            - quality: 质量等级
    """
    object_name = params.get("object_name")
    levels = params.get("levels", 1)
    render_levels = params.get("render_levels", levels)
    use_creases = params.get("use_creases", True)
    apply_smooth = params.get("apply_smooth", False)
    quality = params.get("quality", 3)
    
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
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 如果使用折痕边，先自动检测并标记锐边
    if use_creases:
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        import bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        
        # 获取或创建折痕层
        crease_layer = bm.edges.layers.crease.verify()
        
        # 根据质量设置角度阈值
        angle_threshold = {1: 60, 2: 45, 3: 30, 4: 20, 5: 10}.get(quality, 30)
        
        import math
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                angle = edge.calc_face_angle()
                if angle and math.degrees(angle) > angle_threshold:
                    edge[crease_layer] = 1.0
        
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 添加细分曲面修改器
    subsurf = obj.modifiers.new(name="MCP_Subdivision", type='SUBSURF')
    subsurf.levels = levels
    subsurf.render_levels = render_levels
    subsurf.subdivision_type = 'CATMULL_CLARK'
    subsurf.use_creases = use_creases
    subsurf.quality = quality
    
    # 应用平滑着色
    if apply_smooth:
        bpy.ops.object.shade_smooth()
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "viewport_levels": levels,
            "render_levels": render_levels,
            "modifier_name": subsurf.name
        }
    }


def handle_auto_smooth(params: Dict[str, Any]) -> Dict[str, Any]:
    """自动平滑
    
    根据 Blender 版本使用不同的实现方式：
    - Blender < 4.1: 使用 use_auto_smooth 属性
    - Blender 4.1+: 使用 Smooth by Angle 修改器
    - Blender 5.0+: 使用 Weighted Normal 修改器或几何节点
    
    Args:
        params:
            - object_name: 对象名称
            - angle: 平滑角度阈值（度）
            - use_sharp_edges: 对锐边使用硬边
    """
    import math
    
    object_name = params.get("object_name")
    angle = params.get("angle", 30.0)
    use_sharp_edges = params.get("use_sharp_edges", True)
    
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
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    blender_version = bpy.app.version
    method_used = "unknown"
    sharp_count = 0
    
    # 根据 Blender 版本选择实现方式
    if blender_version >= (4, 1, 0):
        # Blender 4.1+ (包括 5.0): 使用 WEIGHTED_NORMAL 修改器
        # 注意: SMOOTH_BY_ANGLE 在 Blender 5.0 中不存在
        method_used = "weighted_normal"
        
        # 步骤1: 设置平滑着色
        for poly in obj.data.polygons:
            poly.use_smooth = True
        
        # 步骤2: 添加或更新 WEIGHTED_NORMAL 修改器
        wn_mod = None
        for mod in obj.modifiers:
            if mod.type == 'WEIGHTED_NORMAL':
                wn_mod = mod
                break
        
        if not wn_mod:
            wn_mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        
        if wn_mod:
            wn_mod.weight = 50  # 面积权重
            wn_mod.keep_sharp = use_sharp_edges  # 是否保持锐边
            wn_mod.mode = 'FACE_AREA'
        
        # 步骤3: 如果需要，基于角度标记锐边
        if use_sharp_edges:
            import bmesh
            
            # 确保在对象模式
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # 进入编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(obj.data)
            
            angle_rad = math.radians(angle)
            
            for edge in bm.edges:
                if len(edge.link_faces) == 2:
                    try:
                        face_angle = edge.calc_face_angle()
                        if face_angle is not None and face_angle > angle_rad:
                            edge.smooth = False  # 标记为锐边
                            sharp_count += 1
                        else:
                            edge.smooth = True
                    except:
                        pass
            
            bmesh.update_edit_mesh(obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
    
    else:
        # Blender < 4.1: 使用旧的 use_auto_smooth 属性
        method_used = "legacy_auto_smooth"
        try:
            # 应用平滑着色
            bpy.ops.object.shade_smooth()
            # 设置自动平滑
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(angle)
        except AttributeError:
            # 如果属性不存在，回退到手动设置
            for poly in obj.data.polygons:
                poly.use_smooth = True
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "smooth_angle": angle,
            "sharp_edges_marked": sharp_count,
            "method_used": method_used,
            "blender_version": f"{blender_version[0]}.{blender_version[1]}.{blender_version[2]}"
        }
    }
