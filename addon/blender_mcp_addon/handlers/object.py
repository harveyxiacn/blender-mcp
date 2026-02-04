"""
对象处理器

处理对象相关的命令。
"""

from typing import Any, Dict, List
import bpy
import mathutils
import fnmatch


# 对象创建函数映射
MESH_CREATORS = {
    "CUBE": lambda: bpy.ops.mesh.primitive_cube_add(),
    "SPHERE": lambda: bpy.ops.mesh.primitive_uv_sphere_add(),
    "UV_SPHERE": lambda: bpy.ops.mesh.primitive_uv_sphere_add(),
    "ICO_SPHERE": lambda: bpy.ops.mesh.primitive_ico_sphere_add(),
    "CYLINDER": lambda: bpy.ops.mesh.primitive_cylinder_add(),
    "CONE": lambda: bpy.ops.mesh.primitive_cone_add(),
    "TORUS": lambda: bpy.ops.mesh.primitive_torus_add(),
    "PLANE": lambda: bpy.ops.mesh.primitive_plane_add(),
    "CIRCLE": lambda: bpy.ops.mesh.primitive_circle_add(),
    "GRID": lambda: bpy.ops.mesh.primitive_grid_add(),
    "MONKEY": lambda: bpy.ops.mesh.primitive_monkey_add(),
}


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建对象"""
    obj_type = params.get("type", "CUBE")
    name = params.get("name")
    location = params.get("location", [0, 0, 0])
    rotation = params.get("rotation", [0, 0, 0])
    scale = params.get("scale", [1, 1, 1])
    
    # 创建对象
    creator = MESH_CREATORS.get(obj_type)
    if creator:
        creator()
    elif obj_type == "EMPTY":
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    elif obj_type == "TEXT":
        bpy.ops.object.text_add(location=location)
    elif obj_type == "CAMERA":
        bpy.ops.object.camera_add(location=location)
    elif obj_type == "LIGHT":
        bpy.ops.object.light_add(type='POINT', location=location)
    elif obj_type == "ARMATURE":
        bpy.ops.object.armature_add(location=location)
    else:
        return {
            "success": False,
            "error": {
                "code": "INVALID_TYPE",
                "message": f"不支持的对象类型: {obj_type}"
            }
        }
    
    # 获取新创建的对象
    obj = bpy.context.active_object
    
    # 设置变换
    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale
    
    # 重命名
    if name:
        obj.name = name
    
    return {
        "success": True,
        "data": {
            "object_name": obj.name,
            "object_type": obj.type,
            "location": list(obj.location)
        }
    }


def handle_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除对象"""
    name = params.get("name")
    delete_data = params.get("delete_data", True)
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    # 保存数据引用
    data = obj.data if delete_data else None
    
    # 删除对象
    bpy.data.objects.remove(obj, do_unlink=True)
    
    # 删除数据
    if data:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)
        # 其他类型...
    
    return {
        "success": True,
        "data": {}
    }


def handle_duplicate(params: Dict[str, Any]) -> Dict[str, Any]:
    """复制对象"""
    name = params.get("name")
    new_name = params.get("new_name")
    linked = params.get("linked", False)
    offset = params.get("offset", [0, 0, 0])
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    # 复制对象
    if linked:
        new_obj = obj.copy()
    else:
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
    
    # 设置名称
    if new_name:
        new_obj.name = new_name
    
    # 设置位置偏移
    new_obj.location = (
        obj.location.x + offset[0],
        obj.location.y + offset[1],
        obj.location.z + offset[2]
    )
    
    # 链接到场景
    bpy.context.collection.objects.link(new_obj)
    
    return {
        "success": True,
        "data": {
            "new_object_name": new_obj.name
        }
    }


def handle_transform(params: Dict[str, Any]) -> Dict[str, Any]:
    """变换对象"""
    name = params.get("name")
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    # 绝对变换
    if "location" in params:
        obj.location = params["location"]
    if "rotation" in params:
        obj.rotation_euler = params["rotation"]
    if "scale" in params:
        obj.scale = params["scale"]
    
    # 增量变换
    if "delta_location" in params:
        delta = params["delta_location"]
        obj.location = (
            obj.location.x + delta[0],
            obj.location.y + delta[1],
            obj.location.z + delta[2]
        )
    if "delta_rotation" in params:
        delta = params["delta_rotation"]
        obj.rotation_euler = (
            obj.rotation_euler.x + delta[0],
            obj.rotation_euler.y + delta[1],
            obj.rotation_euler.z + delta[2]
        )
    if "delta_scale" in params:
        delta = params["delta_scale"]
        obj.scale = (
            obj.scale.x + delta[0],
            obj.scale.y + delta[1],
            obj.scale.z + delta[2]
        )
    
    return {
        "success": True,
        "data": {
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale)
        }
    }


def handle_select(params: Dict[str, Any]) -> Dict[str, Any]:
    """选择对象"""
    names = params.get("names")
    pattern = params.get("pattern")
    deselect_all = params.get("deselect_all", True)
    set_active = params.get("set_active")
    
    # 取消所有选择
    if deselect_all:
        bpy.ops.object.select_all(action='DESELECT')
    
    selected_count = 0
    
    # 按名称选择
    if names:
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
                selected_count += 1
    
    # 按模式选择
    if pattern:
        for obj in bpy.data.objects:
            if fnmatch.fnmatch(obj.name, pattern):
                obj.select_set(True)
                selected_count += 1
    
    # 设置活动对象
    if set_active:
        obj = bpy.data.objects.get(set_active)
        if obj:
            bpy.context.view_layer.objects.active = obj
    
    return {
        "success": True,
        "data": {
            "selected_count": selected_count
        }
    }


def handle_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出对象"""
    type_filter = params.get("type_filter")
    name_pattern = params.get("name_pattern")
    limit = params.get("limit", 50)
    
    objects = []
    
    for obj in bpy.data.objects:
        # 类型过滤
        if type_filter and obj.type != type_filter:
            continue
        
        # 名称过滤
        if name_pattern and not fnmatch.fnmatch(obj.name, name_pattern):
            continue
        
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "visible": obj.visible_get()
        })
        
        if len(objects) >= limit:
            break
    
    return {
        "success": True,
        "data": {
            "objects": objects,
            "total": len(bpy.data.objects)
        }
    }


def handle_get_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取对象信息"""
    name = params.get("name")
    include_mesh_stats = params.get("include_mesh_stats", True)
    include_modifiers = params.get("include_modifiers", True)
    include_materials = params.get("include_materials", True)
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions)
    }
    
    # 网格统计
    if include_mesh_stats and obj.type == 'MESH' and obj.data:
        mesh = obj.data
        data["mesh_stats"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons)
        }
    
    # 修改器
    if include_modifiers:
        data["modifiers"] = [mod.name for mod in obj.modifiers]
    
    # 材质
    if include_materials:
        data["materials"] = [
            slot.material.name if slot.material else None
            for slot in obj.material_slots
        ]
    
    return {
        "success": True,
        "data": data
    }


def handle_rename(params: Dict[str, Any]) -> Dict[str, Any]:
    """重命名对象"""
    name = params.get("name")
    new_name = params.get("new_name")
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    obj.name = new_name
    
    return {
        "success": True,
        "data": {
            "new_name": obj.name
        }
    }


def handle_set_parent(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置父子关系"""
    child_name = params.get("child_name")
    parent_name = params.get("parent_name")
    keep_transform = params.get("keep_transform", True)
    
    child = bpy.data.objects.get(child_name)
    if not child:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"子对象不存在: {child_name}"
            }
        }
    
    if parent_name:
        parent = bpy.data.objects.get(parent_name)
        if not parent:
            return {
                "success": False,
                "error": {
                    "code": "OBJECT_NOT_FOUND",
                    "message": f"父对象不存在: {parent_name}"
                }
            }
        
        if keep_transform:
            child.parent = parent
            child.matrix_parent_inverse = parent.matrix_world.inverted()
        else:
            child.parent = parent
    else:
        child.parent = None
    
    return {
        "success": True,
        "data": {}
    }


def handle_join(params: Dict[str, Any]) -> Dict[str, Any]:
    """合并对象"""
    objects = params.get("objects", [])
    target = params.get("target")
    
    if len(objects) < 2:
        return {
            "success": False,
            "error": {
                "code": "INVALID_PARAMS",
                "message": "至少需要两个对象才能合并"
            }
        }
    
    # 取消所有选择
    bpy.ops.object.select_all(action='DESELECT')
    
    # 选择要合并的对象
    target_obj = None
    for name in objects:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.select_set(True)
            if target and name == target:
                target_obj = obj
            elif target_obj is None:
                target_obj = obj
    
    if not target_obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "找不到要合并的对象"
            }
        }
    
    # 设置活动对象
    bpy.context.view_layer.objects.active = target_obj
    
    # 合并
    bpy.ops.object.join()
    
    return {
        "success": True,
        "data": {
            "result_object": bpy.context.active_object.name
        }
    }


def handle_set_origin(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置对象原点
    
    Args:
        params:
            - name: 对象名称
            - origin_type: 原点类型
                - GEOMETRY: 原点到几何中心
                - CURSOR: 原点到 3D 游标
                - BOTTOM: 原点到底部中心（脚底）
                - CENTER_OF_MASS: 原点到质心
                - CENTER_OF_VOLUME: 原点到体积中心
            - center: 几何中心计算方式（MEDIAN, BOUNDS）
    """
    name = params.get("name")
    origin_type = params.get("origin_type", "GEOMETRY")
    center = params.get("center", "MEDIAN")
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    # 保存当前选择和活动对象
    original_active = bpy.context.view_layer.objects.active
    original_selected = [o for o in bpy.context.selected_objects]
    
    # 选择目标对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    try:
        if origin_type == "GEOMETRY":
            # 原点到几何中心
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center=center)
        elif origin_type == "CURSOR":
            # 原点到 3D 游标
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        elif origin_type == "BOTTOM":
            # 原点到底部中心（用于角色，脚底）
            if obj.type == 'MESH':
                # 获取对象的边界框
                bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                # 找到最低点
                min_z = min(v.z for v in bbox)
                # 计算底部中心
                center_x = sum(v.x for v in bbox) / 8
                center_y = sum(v.y for v in bbox) / 8
                
                # 保存当前游标位置
                cursor_loc = bpy.context.scene.cursor.location.copy()
                
                # 将游标移动到底部中心
                bpy.context.scene.cursor.location = (center_x, center_y, min_z)
                
                # 设置原点到游标
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                # 恢复游标位置
                bpy.context.scene.cursor.location = cursor_loc
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_TYPE",
                        "message": "BOTTOM 原点类型仅支持网格对象"
                    }
                }
        elif origin_type == "CENTER_OF_MASS":
            # 原点到质心（表面）
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        elif origin_type == "CENTER_OF_VOLUME":
            # 原点到体积中心
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        else:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ORIGIN_TYPE",
                    "message": f"不支持的原点类型: {origin_type}"
                }
            }
        
        # 恢复选择
        bpy.ops.object.select_all(action='DESELECT')
        for o in original_selected:
            if o:
                o.select_set(True)
        if original_active:
            bpy.context.view_layer.objects.active = original_active
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "origin_type": origin_type,
                "new_origin": list(obj.location)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SET_ORIGIN_ERROR",
                "message": str(e)
            }
        }


def handle_apply_transform(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用变换
    
    Args:
        params:
            - name: 对象名称
            - location: 应用位置
            - rotation: 应用旋转
            - scale: 应用缩放
    """
    name = params.get("name")
    apply_location = params.get("location", False)
    apply_rotation = params.get("rotation", False)
    apply_scale = params.get("scale", True)
    
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "success": False,
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": f"对象不存在: {name}"
            }
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    try:
        bpy.ops.object.transform_apply(
            location=apply_location,
            rotation=apply_rotation,
            scale=apply_scale
        )
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "APPLY_TRANSFORM_ERROR",
                "message": str(e)
            }
        }
