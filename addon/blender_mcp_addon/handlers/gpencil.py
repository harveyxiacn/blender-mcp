"""
油笔处理器

处理油笔（Grease Pencil）相关的命令。
"""

from typing import Any, Dict
import bpy


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建油笔对象"""
    name = params.get("name", "GPencil")
    location = params.get("location", [0, 0, 0])
    stroke_depth_order = params.get("stroke_depth_order", "3D")
    
    try:
        # 确保在对象模式
        if bpy.context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
        
        # Blender 5.0+ 使用新的 Grease Pencil v3 API
        # 首先尝试使用 bpy.ops
        try:
            bpy.ops.object.gpencil_add(location=location, type='EMPTY')
            obj = bpy.context.active_object
            obj.name = name
            
            # 获取图层名称（Blender 5.0+ 使用 name 而不是 info）
            layer_name = "Layer"
            if hasattr(obj.data, 'layers') and len(obj.data.layers) > 0:
                layer = obj.data.layers[0]
                layer_name = getattr(layer, 'name', getattr(layer, 'info', 'Layer'))
            
            return {
                "success": True,
                "data": {
                    "object_name": obj.name,
                    "layer_name": layer_name
                }
            }
        except Exception as ops_error:
            # 回退到旧 API
            gpd = bpy.data.grease_pencils.new(name)
            obj = bpy.data.objects.new(name, gpd)
            obj.location = location
            
            # 链接到场景
            bpy.context.collection.objects.link(obj)
            
            # 选择对象
            for o in bpy.context.selected_objects:
                o.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            # 添加默认图层
            layer = gpd.layers.new("Layer", set_active=True)
            layer_name = getattr(layer, 'name', getattr(layer, 'info', 'Layer'))
            
            # 添加默认材质
            mat = bpy.data.materials.new(name=f"{name}_Material")
            bpy.data.materials.create_gpencil_data(mat)
            obj.data.materials.append(mat)
            
            return {
                "success": True,
                "data": {
                    "object_name": obj.name,
                    "layer_name": layer_name
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CREATE_ERROR", "message": str(e)}
        }


def handle_layer(params: Dict[str, Any]) -> Dict[str, Any]:
    """图层操作"""
    gpencil_name = params.get("gpencil_name")
    action = params.get("action", "ADD")
    layer_name = params.get("layer_name", "Layer")
    new_name = params.get("new_name")
    color = params.get("color")
    
    obj = bpy.data.objects.get(gpencil_name)
    # Blender 5.0+ 可能使用 GREASEPENCIL 而不是 GPENCIL
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    gpd = obj.data
    
    try:
        if action == "ADD":
            layer = gpd.layers.new(layer_name, set_active=True)
            if color and hasattr(layer, 'channel_color'):
                layer.channel_color = color[:3] if len(color) >= 3 else [0, 0, 0]
            
            # Blender 5.0+ 使用 name 而不是 info
            result_name = getattr(layer, 'name', getattr(layer, 'info', layer_name))
            
            return {
                "success": True,
                "data": {
                    "layer_name": result_name,
                    "action": "ADD"
                }
            }
        
        elif action == "REMOVE":
            layer = gpd.layers.get(layer_name)
            if layer:
                gpd.layers.remove(layer)
                return {
                    "success": True,
                    "data": {"action": "REMOVE"}
                }
            return {
                "success": False,
                "error": {"code": "LAYER_NOT_FOUND", "message": f"图层不存在: {layer_name}"}
            }
        
        elif action == "RENAME":
            layer = gpd.layers.get(layer_name)
            if layer and new_name:
                # Blender 5.0+ 使用 name
                if hasattr(layer, 'name'):
                    layer.name = new_name
                elif hasattr(layer, 'info'):
                    layer.info = new_name
                return {
                    "success": True,
                    "data": {
                        "old_name": layer_name,
                        "new_name": new_name
                    }
                }
            return {
                "success": False,
                "error": {"code": "RENAME_FAILED", "message": "重命名失败"}
            }
        
        elif action == "MOVE":
            # 移动图层顺序
            pass
        
        return {
            "success": False,
            "error": {"code": "INVALID_ACTION", "message": f"未知操作: {action}"}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LAYER_ERROR", "message": str(e)}
        }


def handle_frame(params: Dict[str, Any]) -> Dict[str, Any]:
    """帧操作"""
    gpencil_name = params.get("gpencil_name")
    layer_name = params.get("layer_name", "Layer")
    action = params.get("action", "ADD")
    frame_number = params.get("frame_number", 1)
    target_frame = params.get("target_frame")
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    gpd = obj.data
    layer = gpd.layers.get(layer_name)
    
    if not layer:
        return {
            "success": False,
            "error": {"code": "LAYER_NOT_FOUND", "message": f"图层不存在: {layer_name}"}
        }
    
    if action == "ADD":
        frame = layer.frames.new(frame_number)
        return {
            "success": True,
            "data": {
                "frame_number": frame.frame_number,
                "action": "ADD"
            }
        }
    
    elif action == "REMOVE":
        frame = layer.frames.get(frame_number)
        if frame:
            layer.frames.remove(frame)
            return {
                "success": True,
                "data": {"action": "REMOVE"}
            }
        return {
            "success": False,
            "error": {"code": "FRAME_NOT_FOUND", "message": f"帧不存在: {frame_number}"}
        }
    
    elif action == "COPY":
        source_frame = None
        for frame in layer.frames:
            if frame.frame_number == frame_number:
                source_frame = frame
                break
        
        if source_frame and target_frame:
            new_frame = layer.frames.copy(source_frame)
            new_frame.frame_number = target_frame
            return {
                "success": True,
                "data": {
                    "source": frame_number,
                    "target": target_frame
                }
            }
    
    elif action == "DUPLICATE":
        # 复制帧
        pass
    
    return {
        "success": False,
        "error": {"code": "INVALID_ACTION", "message": f"未知操作: {action}"}
    }


def handle_draw(params: Dict[str, Any]) -> Dict[str, Any]:
    """绘制笔触"""
    gpencil_name = params.get("gpencil_name")
    layer_name = params.get("layer_name", "Layer")
    points = params.get("points", [])
    material_index = params.get("material_index", 0)
    line_width = params.get("line_width", 10)
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    gpd = obj.data
    layer = gpd.layers.get(layer_name)
    
    if not layer:
        # 创建图层
        layer = gpd.layers.new(layer_name, set_active=True)
    
    # 获取或创建当前帧
    current_frame = bpy.context.scene.frame_current
    frame = None
    for f in layer.frames:
        if f.frame_number == current_frame:
            frame = f
            break
    
    if not frame:
        frame = layer.frames.new(current_frame)
    
    # 创建笔触
    stroke = frame.strokes.new()
    stroke.line_width = line_width
    stroke.material_index = material_index
    
    # 添加点
    stroke.points.add(len(points))
    
    for i, point in enumerate(points):
        x = point[0] if len(point) > 0 else 0
        y = point[1] if len(point) > 1 else 0
        z = point[2] if len(point) > 2 else 0
        pressure = point[3] if len(point) > 3 else 1.0
        strength = point[4] if len(point) > 4 else 1.0
        
        stroke.points[i].co = (x, y, z)
        stroke.points[i].pressure = pressure
        stroke.points[i].strength = strength
    
    return {
        "success": True,
        "data": {
            "stroke_points": len(points),
            "frame": current_frame
        }
    }


def handle_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """油笔材质"""
    gpencil_name = params.get("gpencil_name")
    name = params.get("name", "GPMaterial")
    mode = params.get("mode", "LINE")
    stroke_color = params.get("stroke_color", [0, 0, 0, 1])
    fill_color = params.get("fill_color")
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    # 创建材质
    mat = bpy.data.materials.new(name=name)
    bpy.data.materials.create_gpencil_data(mat)
    
    gp_mat = mat.grease_pencil
    
    # 设置模式
    mode_map = {
        "LINE": 'LINE',
        "DOTS": 'DOTS',
        "BOX": 'BOX',
        "FILL": 'FILL'
    }
    gp_mat.mode = mode_map.get(mode, 'LINE')
    
    # 设置颜色
    gp_mat.color = stroke_color[:4] if len(stroke_color) >= 4 else stroke_color + [1.0]
    
    if fill_color:
        gp_mat.show_fill = True
        gp_mat.fill_color = fill_color[:4] if len(fill_color) >= 4 else fill_color + [1.0]
    
    # 添加到对象
    obj.data.materials.append(mat)
    
    return {
        "success": True,
        "data": {
            "material_name": mat.name,
            "mode": mode
        }
    }


def handle_modifier(params: Dict[str, Any]) -> Dict[str, Any]:
    """油笔修改器"""
    gpencil_name = params.get("gpencil_name")
    modifier_type = params.get("modifier_type", "SMOOTH")
    modifier_name = params.get("modifier_name")
    settings = params.get("settings", {})
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    # 修改器类型映射
    mod_map = {
        "SMOOTH": 'GP_SMOOTH',
        "NOISE": 'GP_NOISE',
        "THICKNESS": 'GP_THICK',
        "TINT": 'GP_TINT',
        "OFFSET": 'GP_OFFSET',
        "OPACITY": 'GP_OPACITY',
        "COLOR": 'GP_COLOR',
        "SUBDIV": 'GP_SUBDIV',
        "SIMPLIFY": 'GP_SIMPLIFY',
        "ARRAY": 'GP_ARRAY',
        "MIRROR": 'GP_MIRROR',
        "BUILD": 'GP_BUILD',
        "LATTICE": 'GP_LATTICE',
        "LENGTH": 'GP_LENGTH',
        "ARMATURE": 'GP_ARMATURE',
        "TIME": 'GP_TIME',
        "MULTIPLY": 'GP_MULTIPLY'
    }
    
    mod_type = mod_map.get(modifier_type, 'GP_SMOOTH')
    
    # 添加修改器
    mod = obj.grease_pencil_modifiers.new(
        name=modifier_name or modifier_type,
        type=mod_type
    )
    
    # 应用设置
    for key, value in settings.items():
        if hasattr(mod, key):
            setattr(mod, key, value)
    
    return {
        "success": True,
        "data": {
            "modifier_name": mod.name,
            "modifier_type": modifier_type
        }
    }


def handle_effect(params: Dict[str, Any]) -> Dict[str, Any]:
    """油笔特效"""
    gpencil_name = params.get("gpencil_name")
    effect_type = params.get("effect_type", "BLUR")
    effect_name = params.get("effect_name")
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    # 特效类型映射
    effect_map = {
        "BLUR": 'FX_BLUR',
        "COLORIZE": 'FX_COLORIZE',
        "FLIP": 'FX_FLIP',
        "GLOW": 'FX_GLOW',
        "LIGHT": 'FX_LIGHT',
        "PIXELATE": 'FX_PIXEL',
        "RIM": 'FX_RIM',
        "SHADOW": 'FX_SHADOW',
        "SWIRL": 'FX_SWIRL',
        "WAVE": 'FX_WAVE'
    }
    
    fx_type = effect_map.get(effect_type, 'FX_BLUR')
    
    # 添加特效
    fx = obj.shader_effects.new(
        name=effect_name or effect_type,
        type=fx_type
    )
    
    return {
        "success": True,
        "data": {
            "effect_name": fx.name,
            "effect_type": effect_type
        }
    }


def handle_convert(params: Dict[str, Any]) -> Dict[str, Any]:
    """转换"""
    gpencil_name = params.get("gpencil_name")
    target_type = params.get("target_type", "CURVE")
    keep_original = params.get("keep_original", True)
    
    obj = bpy.data.objects.get(gpencil_name)
    if not obj or obj.type not in ('GPENCIL', 'GREASEPENCIL'):
        return {
            "success": False,
            "error": {"code": "NOT_GPENCIL", "message": f"不是油笔对象: {gpencil_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    try:
        if target_type == "CURVE":
            bpy.ops.gpencil.convert(type='CURVE', use_timing_data=False)
        elif target_type == "MESH":
            bpy.ops.gpencil.convert(type='POLY', use_timing_data=False)
        
        # 获取新创建的对象
        new_obj = bpy.context.active_object
        
        # 删除原对象（如果需要）
        if not keep_original:
            bpy.data.objects.remove(obj, do_unlink=True)
        
        return {
            "success": True,
            "data": {
                "new_object": new_obj.name if new_obj else None,
                "target_type": target_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CONVERT_ERROR", "message": str(e)}
        }
