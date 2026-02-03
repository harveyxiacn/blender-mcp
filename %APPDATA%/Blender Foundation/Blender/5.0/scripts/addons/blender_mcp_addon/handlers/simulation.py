"""
高级模拟处理器

处理流体、烟雾、海洋等高级模拟命令。
"""

from typing import Any, Dict
import bpy


def handle_fluid_domain(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置流体域"""
    object_name = params.get("object_name")
    domain_type = params.get("domain_type", "LIQUID")
    resolution = params.get("resolution", 64)
    use_adaptive_domain = params.get("use_adaptive_domain", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加流体修改器
        mod = obj.modifiers.new(name="Fluid", type='FLUID')
        mod.fluid_type = 'DOMAIN'
        
        settings = mod.domain_settings
        settings.domain_type = domain_type
        settings.resolution_max = resolution
        settings.use_adaptive_domain = use_adaptive_domain
        
        # 设置缓存
        settings.cache_frame_start = 1
        settings.cache_frame_end = 250
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "domain_type": domain_type,
                "resolution": resolution
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "FLUID_DOMAIN_ERROR", "message": str(e)}
        }


def handle_fluid_flow(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置流体流入/流出"""
    object_name = params.get("object_name")
    flow_type = params.get("flow_type", "INFLOW")
    flow_behavior = params.get("flow_behavior", "GEOMETRY")
    use_initial_velocity = params.get("use_initial_velocity", False)
    velocity = params.get("velocity", [0, 0, 0])
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加流体修改器
        mod = obj.modifiers.new(name="Fluid", type='FLUID')
        mod.fluid_type = 'FLOW'
        
        settings = mod.flow_settings
        settings.flow_type = flow_type
        settings.flow_behavior = flow_behavior
        settings.use_initial_velocity = use_initial_velocity
        
        if use_initial_velocity:
            settings.velocity_coord = velocity
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "flow_type": flow_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "FLUID_FLOW_ERROR", "message": str(e)}
        }


def handle_fluid_effector(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置流体效果器"""
    object_name = params.get("object_name")
    effector_type = params.get("effector_type", "COLLISION")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加流体修改器
        mod = obj.modifiers.new(name="Fluid", type='FLUID')
        mod.fluid_type = 'EFFECTOR'
        
        settings = mod.effector_settings
        settings.effector_type = effector_type
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "effector_type": effector_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "FLUID_EFFECTOR_ERROR", "message": str(e)}
        }


def handle_smoke_domain(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置烟雾/火焰域"""
    object_name = params.get("object_name")
    smoke_type = params.get("smoke_type", "SMOKE")
    resolution = params.get("resolution", 32)
    use_high_resolution = params.get("use_high_resolution", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加流体修改器（烟雾是GAS类型的流体）
        mod = obj.modifiers.new(name="Smoke", type='FLUID')
        mod.fluid_type = 'DOMAIN'
        
        settings = mod.domain_settings
        settings.domain_type = 'GAS'
        settings.resolution_max = resolution
        settings.use_noise = use_high_resolution
        
        # 设置烟雾/火焰
        if smoke_type == "FIRE":
            settings.use_flame_smoke = False
        elif smoke_type == "BOTH":
            settings.use_flame_smoke = True
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "smoke_type": smoke_type,
                "resolution": resolution
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SMOKE_DOMAIN_ERROR", "message": str(e)}
        }


def handle_smoke_flow(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置烟雾/火焰发射器"""
    object_name = params.get("object_name")
    flow_type = params.get("flow_type", "SMOKE")
    temperature = params.get("temperature", 1.0)
    density = params.get("density", 1.0)
    smoke_color = params.get("smoke_color", [1, 1, 1])
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加流体修改器
        mod = obj.modifiers.new(name="SmokeFlow", type='FLUID')
        mod.fluid_type = 'FLOW'
        
        settings = mod.flow_settings
        settings.flow_type = flow_type
        settings.flow_behavior = 'INFLOW'
        settings.temperature = temperature
        settings.density = density
        settings.smoke_color = smoke_color[:3]
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "flow_type": flow_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SMOKE_FLOW_ERROR", "message": str(e)}
        }


def handle_ocean(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加海洋修改器"""
    object_name = params.get("object_name")
    resolution = params.get("resolution", 7)
    spatial_size = params.get("spatial_size", 50)
    wave_scale = params.get("wave_scale", 1.0)
    choppiness = params.get("choppiness", 1.0)
    wind_velocity = params.get("wind_velocity", 30.0)
    use_foam = params.get("use_foam", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加海洋修改器
        mod = obj.modifiers.new(name="Ocean", type='OCEAN')
        mod.resolution = resolution
        mod.spatial_size = spatial_size
        mod.wave_scale = wave_scale
        mod.choppiness = choppiness
        mod.wind_velocity = wind_velocity
        mod.use_foam = use_foam
        
        # 使用生成的几何
        mod.geometry_mode = 'GENERATE'
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "resolution": resolution,
                "spatial_size": spatial_size
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "OCEAN_ERROR", "message": str(e)}
        }


def handle_dynamic_paint_canvas(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置动态绘制画布"""
    object_name = params.get("object_name")
    surface_type = params.get("surface_type", "PAINT")
    use_dissolve = params.get("use_dissolve", False)
    dissolve_speed = params.get("dissolve_speed", 80)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加动态绘制修改器
        mod = obj.modifiers.new(name="DynamicPaint", type='DYNAMIC_PAINT')
        mod.ui_type = 'CANVAS'
        
        # 添加画布表面
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.dpaint.surface_slot_add()
        
        canvas = mod.canvas_settings
        if canvas and canvas.canvas_surfaces:
            surface = canvas.canvas_surfaces.active
            surface.surface_type = surface_type
            surface.use_dissolve = use_dissolve
            if use_dissolve:
                surface.dissolve_speed = dissolve_speed
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "surface_type": surface_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DYNAMIC_PAINT_CANVAS_ERROR", "message": str(e)}
        }


def handle_dynamic_paint_brush(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置动态绘制笔刷"""
    object_name = params.get("object_name")
    paint_color = params.get("paint_color", [1, 0, 0])
    paint_alpha = params.get("paint_alpha", 1.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加动态绘制修改器
        mod = obj.modifiers.new(name="DynamicPaint", type='DYNAMIC_PAINT')
        mod.ui_type = 'BRUSH'
        
        brush = mod.brush_settings
        brush.paint_color = paint_color[:3]
        brush.paint_alpha = paint_alpha
        
        return {
            "success": True,
            "data": {
                "object_name": obj.name,
                "paint_color": paint_color
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DYNAMIC_PAINT_BRUSH_ERROR", "message": str(e)}
        }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙模拟"""
    object_name = params.get("object_name")
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 250)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 设置帧范围
        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end
        
        # 选择对象
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 查找流体修改器并烘焙
        for mod in obj.modifiers:
            if mod.type == 'FLUID' and mod.fluid_type == 'DOMAIN':
                # 注意：实际烘焙可能需要很长时间
                # 这里只设置参数，用户需要手动烘焙或使用后台任务
                mod.domain_settings.cache_frame_start = frame_start
                mod.domain_settings.cache_frame_end = frame_end
                
                return {
                    "success": True,
                    "data": {
                        "object_name": obj.name,
                        "frame_start": frame_start,
                        "frame_end": frame_end,
                        "note": "Cache settings configured. Use Blender UI to bake."
                    }
                }
        
        return {
            "success": False,
            "error": {"code": "NO_FLUID_DOMAIN", "message": "未找到流体域修改器"}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BAKE_ERROR", "message": str(e)}
        }
