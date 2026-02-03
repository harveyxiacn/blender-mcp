"""
UV映射处理器

处理UV展开、投影、编辑等命令。
"""

from typing import Any, Dict, List
import bpy
import math


def handle_unwrap(params: Dict[str, Any]) -> Dict[str, Any]:
    """UV展开"""
    object_name = params.get("object_name")
    method = params.get("method", "ANGLE_BASED")
    fill_holes = params.get("fill_holes", True)
    correct_aspect = params.get("correct_aspect", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 选择所有面
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 执行展开
    bpy.ops.uv.unwrap(
        method=method,
        fill_holes=fill_holes,
        correct_aspect=correct_aspect
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_project(params: Dict[str, Any]) -> Dict[str, Any]:
    """UV投影"""
    object_name = params.get("object_name")
    projection_type = params.get("projection_type", "CUBE")
    scale_to_bounds = params.get("scale_to_bounds", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 根据投影类型执行
    if projection_type == "CUBE":
        bpy.ops.uv.cube_project(scale_to_bounds=scale_to_bounds)
    elif projection_type == "CYLINDER":
        bpy.ops.uv.cylinder_project(scale_to_bounds=scale_to_bounds)
    elif projection_type == "SPHERE":
        bpy.ops.uv.sphere_project(scale_to_bounds=scale_to_bounds)
    elif projection_type == "VIEW":
        bpy.ops.uv.project_from_view(scale_to_bounds=scale_to_bounds)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "projection_type": projection_type
        }
    }


def handle_smart_project(params: Dict[str, Any]) -> Dict[str, Any]:
    """智能UV投影"""
    object_name = params.get("object_name")
    angle_limit = params.get("angle_limit", 66.0)
    island_margin = params.get("island_margin", 0.0)
    area_weight = params.get("area_weight", 0.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # 智能UV投影
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(angle_limit),
        island_margin=island_margin,
        area_weight=area_weight
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_pack(params: Dict[str, Any]) -> Dict[str, Any]:
    """UV打包"""
    object_name = params.get("object_name")
    margin = params.get("margin", 0.001)
    rotate = params.get("rotate", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # UV打包
    bpy.ops.uv.pack_islands(margin=margin, rotate=rotate)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_seam(params: Dict[str, Any]) -> Dict[str, Any]:
    """UV接缝"""
    object_name = params.get("object_name")
    action = params.get("action", "mark")
    edge_indices = params.get("edge_indices")
    from_sharp = params.get("from_sharp", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象并进入编辑模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    if from_sharp:
        # 从锐边标记接缝
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
    elif edge_indices:
        # 选择指定边
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        mesh = obj.data
        for idx in edge_indices:
            if idx < len(mesh.edges):
                mesh.edges[idx].select = True
        
        if action == "mark":
            bpy.ops.mesh.mark_seam(clear=False)
        else:
            bpy.ops.mesh.mark_seam(clear=True)
    else:
        # 对选中的边操作
        if action == "mark":
            bpy.ops.mesh.mark_seam(clear=False)
        else:
            bpy.ops.mesh.mark_seam(clear=True)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {}
    }


def handle_transform(params: Dict[str, Any]) -> Dict[str, Any]:
    """UV变换"""
    object_name = params.get("object_name")
    translate = params.get("translate")
    rotate = params.get("rotate")
    scale = params.get("scale")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    mesh = obj.data
    if not mesh.uv_layers:
        return {
            "success": False,
            "error": {"code": "NO_UV", "message": "对象没有UV层"}
        }
    
    uv_layer = mesh.uv_layers.active.data
    
    # 应用变换
    for loop in mesh.loops:
        uv = uv_layer[loop.index].uv
        
        # 缩放（以中心点）
        if scale:
            uv[0] = (uv[0] - 0.5) * scale[0] + 0.5
            uv[1] = (uv[1] - 0.5) * scale[1] + 0.5
        
        # 旋转（以中心点）
        if rotate:
            angle = math.radians(rotate)
            x = uv[0] - 0.5
            y = uv[1] - 0.5
            uv[0] = x * math.cos(angle) - y * math.sin(angle) + 0.5
            uv[1] = x * math.sin(angle) + y * math.cos(angle) + 0.5
        
        # 平移
        if translate:
            uv[0] += translate[0]
            uv[1] += translate[1]
    
    mesh.update()
    
    return {
        "success": True,
        "data": {}
    }
