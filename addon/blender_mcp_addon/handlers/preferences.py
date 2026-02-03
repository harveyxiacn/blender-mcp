"""
偏好设置处理器

处理Blender偏好设置管理命令。
"""

from typing import Any, Dict
import bpy


def handle_get(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取设置"""
    category = params.get("category")
    key = params.get("key")
    
    try:
        prefs = bpy.context.preferences
        
        category_map = {
            "view": prefs.view,
            "system": prefs.system,
            "edit": prefs.edit,
            "input": prefs.inputs,
            "filepaths": prefs.filepaths,
            "addons": prefs.addons
        }
        
        if category not in category_map:
            return {
                "success": False,
                "error": {"code": "INVALID_CATEGORY", "message": f"无效类别: {category}"}
            }
        
        cat_prefs = category_map[category]
        
        if hasattr(cat_prefs, key):
            value = getattr(cat_prefs, key)
            # 转换为可序列化的值
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = list(value)
            
            return {
                "success": True,
                "data": {
                    "category": category,
                    "key": key,
                    "value": value
                }
            }
        else:
            return {
                "success": False,
                "error": {"code": "KEY_NOT_FOUND", "message": f"键不存在: {key}"}
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "GET_ERROR", "message": str(e)}
        }


def handle_set(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置偏好"""
    category = params.get("category")
    key = params.get("key")
    value = params.get("value")
    
    try:
        prefs = bpy.context.preferences
        
        category_map = {
            "view": prefs.view,
            "system": prefs.system,
            "edit": prefs.edit,
            "input": prefs.inputs,
            "filepaths": prefs.filepaths
        }
        
        if category not in category_map:
            return {
                "success": False,
                "error": {"code": "INVALID_CATEGORY", "message": f"无效类别: {category}"}
            }
        
        cat_prefs = category_map[category]
        
        if hasattr(cat_prefs, key):
            setattr(cat_prefs, key, value)
            
            return {
                "success": True,
                "data": {
                    "category": category,
                    "key": key,
                    "value": value
                }
            }
        else:
            return {
                "success": False,
                "error": {"code": "KEY_NOT_FOUND", "message": f"键不存在: {key}"}
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SET_ERROR", "message": str(e)}
        }


def handle_theme(params: Dict[str, Any]) -> Dict[str, Any]:
    """主题设置"""
    preset = params.get("preset")
    custom_colors = params.get("custom_colors")
    
    try:
        if preset:
            # 加载预设主题
            # Blender 5.0 主题预设
            preset_map = {
                "Dark": "blender_dark",
                "Light": "blender_light",
                "Default": "Default"
            }
            
            preset_name = preset_map.get(preset, preset)
            
            try:
                bpy.ops.script.execute_preset(
                    filepath=f"//presets/interface_theme/{preset_name}.xml",
                    menu_idname="USERPREF_MT_interface_theme_presets"
                )
            except:
                # 如果预设不存在，尝试设置基本颜色
                pass
        
        if custom_colors:
            theme = bpy.context.preferences.themes[0]
            
            # 应用自定义颜色
            if "background" in custom_colors:
                theme.view_3d.space.gradients.high_gradient = custom_colors["background"][:3]
            
            if "text" in custom_colors:
                theme.user_interface.wcol_regular.text = custom_colors["text"][:3]
            
            if "accent" in custom_colors:
                theme.user_interface.wcol_state.inner_sel = custom_colors["accent"][:4]
        
        return {
            "success": True,
            "data": {
                "preset": preset,
                "custom_colors_applied": bool(custom_colors)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "THEME_ERROR", "message": str(e)}
        }


def handle_viewport(params: Dict[str, Any]) -> Dict[str, Any]:
    """视口设置"""
    show_gizmo = params.get("show_gizmo")
    show_floor = params.get("show_floor")
    show_axis_x = params.get("show_axis_x")
    show_axis_y = params.get("show_axis_y")
    show_axis_z = params.get("show_axis_z")
    clip_start = params.get("clip_start")
    clip_end = params.get("clip_end")
    
    try:
        # 获取当前3D视图
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                
                if show_gizmo is not None:
                    space.show_gizmo = show_gizmo
                
                overlay = space.overlay
                
                if show_floor is not None:
                    overlay.show_floor = show_floor
                
                if show_axis_x is not None:
                    overlay.show_axis_x = show_axis_x
                
                if show_axis_y is not None:
                    overlay.show_axis_y = show_axis_y
                
                if show_axis_z is not None:
                    overlay.show_axis_z = show_axis_z
                
                if clip_start is not None:
                    space.clip_start = clip_start
                
                if clip_end is not None:
                    space.clip_end = clip_end
                
                break
        
        return {
            "success": True,
            "data": {
                "viewport_updated": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "VIEWPORT_ERROR", "message": str(e)}
        }


def handle_system(params: Dict[str, Any]) -> Dict[str, Any]:
    """系统设置"""
    memory_cache_limit = params.get("memory_cache_limit")
    undo_steps = params.get("undo_steps")
    use_gpu_subdivision = params.get("use_gpu_subdivision")
    
    try:
        prefs = bpy.context.preferences
        
        if memory_cache_limit is not None:
            prefs.system.memory_cache_limit = memory_cache_limit
        
        if undo_steps is not None:
            prefs.edit.undo_steps = undo_steps
        
        if use_gpu_subdivision is not None:
            prefs.system.use_gpu_subdivision = use_gpu_subdivision
        
        return {
            "success": True,
            "data": {
                "system_updated": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SYSTEM_ERROR", "message": str(e)}
        }


def handle_save(params: Dict[str, Any]) -> Dict[str, Any]:
    """保存偏好设置"""
    try:
        bpy.ops.wm.save_userpref()
        
        return {
            "success": True,
            "data": {
                "saved": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SAVE_ERROR", "message": str(e)}
        }


def handle_load_factory(params: Dict[str, Any]) -> Dict[str, Any]:
    """加载出厂设置"""
    try:
        bpy.ops.wm.read_factory_userpref()
        
        return {
            "success": True,
            "data": {
                "factory_loaded": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "FACTORY_ERROR", "message": str(e)}
        }
