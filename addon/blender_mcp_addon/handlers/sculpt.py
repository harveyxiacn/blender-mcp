"""
雕刻处理器

处理雕刻相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_mode(params: Dict[str, Any]) -> Dict[str, Any]:
    """进入/退出雕刻模式"""
    object_name = params.get("object_name")
    enable = params.get("enable", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    if obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "INVALID_TYPE", "message": "只有网格对象可以雕刻"}
        }
    
    try:
        # 确保在正确的上下文中
        # 首先切换到对象模式（如果不在）
        current_mode = bpy.context.mode
        if current_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
        
        # 选择对象
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 切换模式
        if enable:
            bpy.ops.object.mode_set(mode='SCULPT')
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return {
            "success": True,
            "data": {
                "mode": bpy.context.object.mode if bpy.context.object else "OBJECT"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "MODE_ERROR", "message": str(e)}
        }


def handle_set_brush(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置雕刻笔刷"""
    brush_type = params.get("brush_type", "DRAW")
    radius = params.get("radius", 50.0)
    strength = params.get("strength", 0.5)
    auto_smooth = params.get("auto_smooth", 0.0)
    
    try:
        # 获取当前工具设置
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt
        
        # 笔刷类型映射
        brush_map = {
            "DRAW": "SculptDraw",
            "CLAY": "Clay",
            "CLAY_STRIPS": "Clay Strips",
            "INFLATE": "Inflate/Deflate",
            "BLOB": "Blob",
            "CREASE": "Crease",
            "SMOOTH": "Smooth",
            "FLATTEN": "Flatten/Contrast",
            "FILL": "Fill/Deepen",
            "SCRAPE": "Scrape/Peaks",
            "PINCH": "Pinch/Magnify",
            "GRAB": "Grab",
            "SNAKE_HOOK": "Snake Hook",
            "THUMB": "Thumb",
            "NUDGE": "Nudge",
            "ROTATE": "Rotate",
            "MASK": "Mask",
            "DRAW_FACE_SETS": "Draw Face Sets"
        }
        
        brush_name = brush_map.get(brush_type, "SculptDraw")
        
        # 查找笔刷 - Blender 5.0+ 兼容方式
        brush = bpy.data.brushes.get(brush_name)
        if not brush:
            # 尝试查找匹配的笔刷
            for b in bpy.data.brushes:
                # Blender 5.0+ 可能使用不同的属性
                tool = getattr(b, 'sculpt_tool', None) or getattr(b, 'brush_type', None)
                if tool == brush_type:
                    brush = b
                    break
        
        if not brush:
            # 创建新笔刷
            brush = bpy.data.brushes.new(name=brush_name, mode='SCULPT')
        
        if brush:
            # Blender 5.0+ brush 属性可能只读，使用 bpy.ops 设置
            try:
                if sculpt:
                    sculpt.brush = brush
            except AttributeError:
                # 使用 ops 设置活动笔刷
                pass
            
            brush.size = int(radius)
            brush.strength = strength
            if hasattr(brush, 'auto_smooth_factor'):
                brush.auto_smooth_factor = auto_smooth
        
        return {
            "success": True,
            "data": {
                "brush": brush.name if brush else "default",
                "radius": radius,
                "strength": strength
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BRUSH_ERROR", "message": str(e)}
        }


def handle_stroke(params: Dict[str, Any]) -> Dict[str, Any]:
    """执行雕刻笔触"""
    object_name = params.get("object_name")
    stroke_points = params.get("stroke_points", [])
    brush_type = params.get("brush_type")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    # 确保在雕刻模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    if bpy.context.object.mode != 'SCULPT':
        bpy.ops.object.mode_set(mode='SCULPT')
    
    # 设置笔刷
    if brush_type:
        handle_set_brush({"brush_type": brush_type})
    
    # 注意：直接执行笔触在 MCP 环境下比较困难
    # 这里使用程序化方式修改网格
    # 对于真实笔触，建议使用 bpy.ops.sculpt.brush_stroke
    
    try:
        # 构建笔触数据
        stroke_data = []
        for point in stroke_points:
            x, y, z = point[:3]
            pressure = point[3] if len(point) > 3 else 1.0
            stroke_data.append({
                "name": "",
                "mouse": (0, 0),
                "mouse_event": (0, 0),
                "x_tilt": 0,
                "y_tilt": 0,
                "pressure": pressure,
                "size": 1.0,
                "pen_flip": False,
                "time": 0,
                "is_start": len(stroke_data) == 0,
                "location": (x, y, z),
            })
        
        # 由于 API 限制，这里使用替代方案
        # 对网格应用变形
        mesh = obj.data
        
        # 简单的变形示例
        for point in stroke_points:
            x, y, z = point[:3]
            pressure = point[3] if len(point) > 3 else 1.0
            
            # 找到最近的顶点并稍微移动它
            for vert in mesh.vertices:
                world_co = obj.matrix_world @ vert.co
                dist = ((world_co.x - x)**2 + (world_co.y - y)**2 + (world_co.z - z)**2) ** 0.5
                
                if dist < 0.5:  # 影响半径
                    # 沿法线方向移动
                    normal = vert.normal
                    factor = pressure * 0.1 * (1 - dist / 0.5)
                    vert.co += normal * factor
        
        mesh.update()
        
        return {
            "success": True,
            "data": {
                "points_applied": len(stroke_points)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "STROKE_ERROR", "message": str(e)}
        }


def handle_remesh(params: Dict[str, Any]) -> Dict[str, Any]:
    """重新网格化"""
    object_name = params.get("object_name")
    mode = params.get("mode", "VOXEL")
    voxel_size = params.get("voxel_size", 0.1)
    smooth_normals = params.get("smooth_normals", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"网格对象不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 确保在对象模式
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    if mode == "VOXEL":
        # 体素重网格
        obj.data.remesh_voxel_size = voxel_size
        obj.data.use_remesh_preserve_volume = True
        obj.data.use_remesh_fix_poles = True
        
        bpy.ops.object.voxel_remesh()
    else:
        # 四边形重网格（使用修改器）
        mod = obj.modifiers.new(name="Remesh", type='REMESH')
        mod.mode = 'VOXEL'
        mod.voxel_size = voxel_size
        mod.use_smooth_shade = smooth_normals
        
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    return {
        "success": True,
        "data": {
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons)
        }
    }


def handle_multires(params: Dict[str, Any]) -> Dict[str, Any]:
    """多分辨率细分"""
    object_name = params.get("object_name")
    levels = params.get("levels", 2)
    sculpt_level = params.get("sculpt_level")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"网格对象不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 确保在对象模式
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 查找或添加多分辨率修改器
    multires = None
    for mod in obj.modifiers:
        if mod.type == 'MULTIRES':
            multires = mod
            break
    
    if not multires:
        multires = obj.modifiers.new(name="Multires", type='MULTIRES')
    
    # 细分
    current_levels = multires.total_levels
    for _ in range(levels - current_levels):
        bpy.ops.object.multires_subdivide(modifier=multires.name, mode='CATMULL_CLARK')
    
    # 设置雕刻级别
    if sculpt_level is not None:
        multires.sculpt_levels = min(sculpt_level, multires.total_levels)
    else:
        multires.sculpt_levels = multires.total_levels
    
    return {
        "success": True,
        "data": {
            "total_levels": multires.total_levels,
            "sculpt_levels": multires.sculpt_levels
        }
    }


def handle_mask(params: Dict[str, Any]) -> Dict[str, Any]:
    """蒙版操作"""
    object_name = params.get("object_name")
    action = params.get("action", "CLEAR")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"网格对象不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 切换到雕刻模式
    if bpy.context.object.mode != 'SCULPT':
        bpy.ops.object.mode_set(mode='SCULPT')
    
    # 执行蒙版操作
    action_map = {
        "CLEAR": "CLEAR",
        "INVERT": "INVERT",
        "SMOOTH": "SMOOTH",
        "EXPAND": "GROW",
        "CONTRACT": "SHRINK"
    }
    
    mask_action = action_map.get(action, "CLEAR")
    
    try:
        if mask_action == "CLEAR":
            bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        elif mask_action == "INVERT":
            bpy.ops.paint.mask_flood_fill(mode='INVERT')
        elif mask_action == "SMOOTH":
            bpy.ops.sculpt.mask_filter(filter_type='SMOOTH')
        elif mask_action in ["GROW", "SHRINK"]:
            bpy.ops.sculpt.mask_filter(filter_type=mask_action)
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "MASK_ERROR", "message": str(e)}
        }
    
    return {
        "success": True,
        "data": {
            "action": action
        }
    }


def handle_symmetry(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置对称"""
    use_x = params.get("use_x", True)
    use_y = params.get("use_y", False)
    use_z = params.get("use_z", False)
    
    sculpt = bpy.context.tool_settings.sculpt
    
    sculpt.use_symmetry_x = use_x
    sculpt.use_symmetry_y = use_y
    sculpt.use_symmetry_z = use_z
    
    return {
        "success": True,
        "data": {
            "use_x": use_x,
            "use_y": use_y,
            "use_z": use_z
        }
    }


def handle_dyntopo(params: Dict[str, Any]) -> Dict[str, Any]:
    """动态拓扑"""
    object_name = params.get("object_name")
    enable = params.get("enable", True)
    detail_size = params.get("detail_size", 12.0)
    detail_type = params.get("detail_type", "RELATIVE")
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"网格对象不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 切换到雕刻模式
    if bpy.context.object.mode != 'SCULPT':
        bpy.ops.object.mode_set(mode='SCULPT')
    
    sculpt = bpy.context.tool_settings.sculpt
    
    try:
        if enable:
            # 启用动态拓扑
            if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
            
            # 设置细节
            sculpt.detail_size = detail_size
            sculpt.detail_type_method = detail_type
        else:
            # 禁用动态拓扑
            if bpy.context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
        
        return {
            "success": True,
            "data": {
                "enabled": enable,
                "detail_size": detail_size,
                "detail_type": detail_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DYNTOPO_ERROR", "message": str(e)}
        }
