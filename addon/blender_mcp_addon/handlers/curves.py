"""
曲线建模处理器

处理曲线创建、编辑、转换等命令。
"""

from typing import Any, Dict, List
import bpy
import math


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建曲线"""
    curve_type = params.get("curve_type", "BEZIER")
    name = params.get("name", "Curve")
    points = params.get("points", [])
    cyclic = params.get("cyclic", False)
    location = params.get("location", [0, 0, 0])
    
    if len(points) < 2:
        return {
            "success": False,
            "error": {"code": "INVALID_POINTS", "message": "至少需要2个控制点"}
        }
    
    # 创建曲线数据
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    # 创建样条
    if curve_type == "BEZIER":
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)
        
        for i, point in enumerate(points):
            bp = spline.bezier_points[i]
            bp.co = point
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
    
    elif curve_type == "NURBS":
        spline = curve_data.splines.new('NURBS')
        spline.points.add(len(points) - 1)
        
        for i, point in enumerate(points):
            spline.points[i].co = point + [1.0]  # NURBS需要权重
        
        spline.use_endpoint_u = True
    
    else:  # POLY
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(points) - 1)
        
        for i, point in enumerate(points):
            spline.points[i].co = point + [1.0]
    
    spline.use_cyclic_u = cyclic
    
    # 创建对象
    curve_obj = bpy.data.objects.new(name, curve_data)
    curve_obj.location = location
    bpy.context.collection.objects.link(curve_obj)
    
    return {
        "success": True,
        "data": {
            "curve_name": curve_obj.name,
            "points_count": len(points)
        }
    }


def handle_circle(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建圆形曲线"""
    name = params.get("name", "Circle")
    radius = params.get("radius", 1.0)
    location = params.get("location", [0, 0, 0])
    fill_mode = params.get("fill_mode", "FULL")
    
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=location)
    curve_obj = bpy.context.active_object
    curve_obj.name = name
    
    # 设置填充模式 (FULL, BACK, FRONT, HALF)
    if fill_mode in ('FULL', 'BACK', 'FRONT', 'HALF'):
        curve_obj.data.fill_mode = fill_mode
    
    return {
        "success": True,
        "data": {
            "curve_name": curve_obj.name
        }
    }


def handle_path(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建路径曲线"""
    name = params.get("name", "Path")
    length = params.get("length", 4.0)
    points_count = params.get("points_count", 5)
    location = params.get("location", [0, 0, 0])
    
    # 创建曲线数据
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.use_path = True
    
    # 创建 NURBS 样条
    spline = curve_data.splines.new('NURBS')
    spline.points.add(points_count - 1)
    
    # 设置点位置
    step = length / (points_count - 1)
    for i in range(points_count):
        x = -length / 2 + i * step
        spline.points[i].co = [x, 0, 0, 1]
    
    spline.use_endpoint_u = True
    
    # 创建对象
    curve_obj = bpy.data.objects.new(name, curve_data)
    curve_obj.location = location
    bpy.context.collection.objects.link(curve_obj)
    
    return {
        "success": True,
        "data": {
            "curve_name": curve_obj.name
        }
    }


def handle_spiral(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建螺旋曲线"""
    name = params.get("name", "Spiral")
    turns = params.get("turns", 2.0)
    radius = params.get("radius", 1.0)
    height = params.get("height", 2.0)
    location = params.get("location", [0, 0, 0])
    
    # 创建曲线数据
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    # 创建样条
    points_per_turn = 16
    total_points = int(turns * points_per_turn)
    
    spline = curve_data.splines.new('POLY')
    spline.points.add(total_points - 1)
    
    for i in range(total_points):
        t = i / total_points
        angle = t * turns * 2 * math.pi
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = t * height
        spline.points[i].co = [x, y, z, 1]
    
    # 创建对象
    curve_obj = bpy.data.objects.new(name, curve_data)
    curve_obj.location = location
    bpy.context.collection.objects.link(curve_obj)
    
    return {
        "success": True,
        "data": {
            "curve_name": curve_obj.name
        }
    }


def handle_to_mesh(params: Dict[str, Any]) -> Dict[str, Any]:
    """曲线转网格"""
    curve_name = params.get("curve_name")
    resolution = params.get("resolution", 12)
    keep_original = params.get("keep_original", False)
    
    curve_obj = bpy.data.objects.get(curve_name)
    if not curve_obj or curve_obj.type != 'CURVE':
        return {
            "success": False,
            "error": {"code": "CURVE_NOT_FOUND", "message": f"曲线不存在: {curve_name}"}
        }
    
    # 设置分辨率
    curve_obj.data.resolution_u = resolution
    
    # 选择曲线
    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj
    
    # 转换为网格
    bpy.ops.object.convert(target='MESH', keep_original=keep_original)
    
    mesh_obj = bpy.context.active_object
    
    return {
        "success": True,
        "data": {
            "mesh_name": mesh_obj.name
        }
    }


def handle_extrude(params: Dict[str, Any]) -> Dict[str, Any]:
    """曲线挤出设置"""
    curve_name = params.get("curve_name")
    depth = params.get("depth", 0.1)
    bevel_depth = params.get("bevel_depth", 0.0)
    bevel_resolution = params.get("bevel_resolution", 0)
    
    curve_obj = bpy.data.objects.get(curve_name)
    if not curve_obj or curve_obj.type != 'CURVE':
        return {
            "success": False,
            "error": {"code": "CURVE_NOT_FOUND", "message": f"曲线不存在: {curve_name}"}
        }
    
    curve_data = curve_obj.data
    curve_data.extrude = depth
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = bevel_resolution
    
    return {
        "success": True,
        "data": {}
    }


def handle_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建文本"""
    text = params.get("text", "Text")
    name = params.get("name", "Text")
    font_size = params.get("font_size", 1.0)
    extrude = params.get("extrude", 0.0)
    location = params.get("location", [0, 0, 0])
    
    # 创建文本对象
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.active_object
    text_obj.name = name
    
    # 设置文本内容
    text_obj.data.body = text
    text_obj.data.size = font_size
    text_obj.data.extrude = extrude
    
    # 居中对齐
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'
    
    return {
        "success": True,
        "data": {
            "text_name": text_obj.name
        }
    }
