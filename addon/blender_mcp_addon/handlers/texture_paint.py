"""
纹理绘制处理器

处理纹理绘制相关的命令。
"""

from typing import Any, Dict
import bpy
import os


def handle_mode(params: Dict[str, Any]) -> Dict[str, Any]:
    """进入/退出纹理绘制模式"""
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
            "error": {"code": "INVALID_TYPE", "message": "只有网格对象可以进行纹理绘制"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 切换模式
    if enable:
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        "success": True,
        "data": {
            "mode": bpy.context.object.mode
        }
    }


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建新纹理"""
    name = params.get("name", "Texture")
    width = params.get("width", 1024)
    height = params.get("height", 1024)
    color = params.get("color", [0.0, 0.0, 0.0, 1.0])
    alpha = params.get("alpha", True)
    float_buffer = params.get("float_buffer", False)
    
    # 创建新图像
    image = bpy.data.images.new(
        name=name,
        width=width,
        height=height,
        alpha=alpha,
        float_buffer=float_buffer
    )
    
    # 填充颜色
    if color:
        pixels = [0.0] * (width * height * 4)
        for i in range(width * height):
            pixels[i * 4] = color[0]
            pixels[i * 4 + 1] = color[1]
            pixels[i * 4 + 2] = color[2]
            pixels[i * 4 + 3] = color[3] if len(color) > 3 else 1.0
        image.pixels = pixels
    
    return {
        "success": True,
        "data": {
            "image_name": image.name,
            "width": width,
            "height": height
        }
    }


def handle_set_brush(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置绘制笔刷"""
    brush_type = params.get("brush_type", "DRAW")
    color = params.get("color", [1.0, 1.0, 1.0])
    radius = params.get("radius", 50.0)
    strength = params.get("strength", 1.0)
    blend = params.get("blend", "MIX")
    
    try:
        # 获取当前工具设置
        tool_settings = bpy.context.tool_settings
        
        # 笔刷类型映射
        brush_map = {
            "DRAW": "TexDraw",
            "SOFTEN": "Soften",
            "SMEAR": "Smear",
            "CLONE": "Clone",
            "FILL": "Fill",
            "MASK": "Mask"
        }
        
        brush_name = brush_map.get(brush_type, "TexDraw")
        
        # 查找笔刷 - Blender 5.0+ 兼容
        brush = bpy.data.brushes.get(brush_name)
        if not brush:
            for b in bpy.data.brushes:
                # Blender 5.0+ 可能使用不同属性
                tool = getattr(b, 'image_tool', None) or getattr(b, 'image_paint_tool', None)
                if tool == brush_type:
                    brush = b
                    break
        
        if not brush:
            # 创建新笔刷
            brush = bpy.data.brushes.new(name=brush_name, mode='TEXTURE_PAINT')
        
        if brush:
            # Blender 5.0+ brush 属性是只读的
            # 直接设置笔刷属性
            brush.size = int(radius)
            brush.strength = strength
            brush.color = color[:3] if len(color) >= 3 else [1, 1, 1]
            
            # 设置混合模式
            blend_map = {
                "MIX": "MIX",
                "ADD": "ADD",
                "SUBTRACT": "SUB",
                "MULTIPLY": "MUL",
                "LIGHTEN": "LIGHTEN",
                "DARKEN": "DARKEN",
                "ERASE_ALPHA": "ERASE_ALPHA",
                "ADD_ALPHA": "ADD_ALPHA"
            }
            if hasattr(brush, 'blend'):
                brush.blend = blend_map.get(blend, "MIX")
        
        return {
            "success": True,
            "data": {
                "brush": brush.name if brush else "default",
                "color": color,
                "radius": radius
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BRUSH_ERROR", "message": str(e)}
        }


def handle_stroke(params: Dict[str, Any]) -> Dict[str, Any]:
    """执行绘制笔触"""
    object_name = params.get("object_name")
    uv_points = params.get("uv_points", [])
    color = params.get("color")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    # 确保对象有材质和纹理
    if not obj.active_material:
        return {
            "success": False,
            "error": {"code": "NO_MATERIAL", "message": "对象没有材质"}
        }
    
    # 确保在纹理绘制模式
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    if bpy.context.object.mode != 'TEXTURE_PAINT':
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    
    # 设置颜色
    if color:
        brush = bpy.context.tool_settings.image_paint.brush
        if brush:
            brush.color = color[:3] if len(color) >= 3 else [1, 1, 1]
    
    # 注意：直接程序化绘制纹理
    # 获取活动的绘制图像
    paint_slot = obj.active_material.paint_active_slot
    tex_slot = obj.active_material.texture_paint_slots[paint_slot] if paint_slot < len(obj.active_material.texture_paint_slots) else None
    
    if tex_slot and tex_slot.image:
        image = tex_slot.image
        width, height = image.size
        pixels = list(image.pixels)
        
        brush_color = color if color else [1.0, 1.0, 1.0]
        
        # 在UV坐标位置绘制
        for point in uv_points:
            u, v = point[:2]
            pressure = point[2] if len(point) > 2 else 1.0
            
            # 转换UV到像素坐标
            px = int(u * width)
            py = int(v * height)
            
            # 简单的点绘制
            radius = int(10 * pressure)
            
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        x = px + dx
                        y = py + dy
                        
                        if 0 <= x < width and 0 <= y < height:
                            idx = (y * width + x) * 4
                            # 混合颜色
                            alpha = pressure
                            pixels[idx] = pixels[idx] * (1-alpha) + brush_color[0] * alpha
                            pixels[idx+1] = pixels[idx+1] * (1-alpha) + brush_color[1] * alpha
                            pixels[idx+2] = pixels[idx+2] * (1-alpha) + brush_color[2] * alpha
        
        image.pixels = pixels
        image.update()
        
        return {
            "success": True,
            "data": {
                "points_applied": len(uv_points),
                "image": image.name
            }
        }
    
    return {
        "success": False,
        "error": {"code": "NO_PAINT_SLOT", "message": "没有可绘制的纹理槽"}
    }


def handle_fill(params: Dict[str, Any]) -> Dict[str, Any]:
    """填充颜色"""
    object_name = params.get("object_name")
    color = params.get("color", [1.0, 1.0, 1.0, 1.0])
    texture_slot = params.get("texture_slot", 0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    if not obj.active_material:
        return {
            "success": False,
            "error": {"code": "NO_MATERIAL", "message": "对象没有材质"}
        }
    
    # 获取纹理
    mat = obj.active_material
    slots = mat.texture_paint_slots
    
    if texture_slot >= len(slots) or not slots[texture_slot]:
        return {
            "success": False,
            "error": {"code": "INVALID_SLOT", "message": f"纹理槽 {texture_slot} 不存在"}
        }
    
    image = slots[texture_slot].image
    if not image:
        return {
            "success": False,
            "error": {"code": "NO_IMAGE", "message": "纹理槽没有图像"}
        }
    
    width, height = image.size
    
    # 填充颜色
    pixels = [0.0] * (width * height * 4)
    for i in range(width * height):
        pixels[i * 4] = color[0]
        pixels[i * 4 + 1] = color[1]
        pixels[i * 4 + 2] = color[2]
        pixels[i * 4 + 3] = color[3] if len(color) > 3 else 1.0
    
    image.pixels = pixels
    image.update()
    
    return {
        "success": True,
        "data": {
            "image": image.name,
            "color": color
        }
    }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙纹理"""
    object_name = params.get("object_name")
    bake_type = params.get("bake_type", "DIFFUSE")
    width = params.get("width", 1024)
    height = params.get("height", 1024)
    margin = params.get("margin", 16)
    output_path = params.get("output_path")
    
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
    
    # 创建烘焙用图像
    bake_image = bpy.data.images.new(
        name=f"{object_name}_bake",
        width=width,
        height=height,
        alpha=True
    )
    
    # 确保有材质和UV
    if not obj.active_material:
        mat = bpy.data.materials.new(name=f"{object_name}_Material")
        obj.data.materials.append(mat)
        mat.use_nodes = True
    
    mat = obj.active_material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # 添加图像纹理节点用于烘焙
    tex_node = nodes.new('ShaderNodeTexImage')
    tex_node.image = bake_image
    tex_node.select = True
    nodes.active = tex_node
    
    # 设置烘焙参数
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = bake_type
    bpy.context.scene.render.bake.margin = margin
    
    try:
        # 执行烘焙
        bpy.ops.object.bake(type=bake_type)
        
        # 保存图像
        if output_path:
            bake_image.filepath_raw = output_path
            bake_image.file_format = 'PNG'
            bake_image.save()
        
        return {
            "success": True,
            "data": {
                "image_name": bake_image.name,
                "bake_type": bake_type,
                "output_path": output_path
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BAKE_ERROR", "message": str(e)}
        }


def handle_slot(params: Dict[str, Any]) -> Dict[str, Any]:
    """纹理槽管理"""
    object_name = params.get("object_name")
    action = params.get("action", "ADD")
    texture_name = params.get("texture_name")
    slot_index = params.get("slot_index", 0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    # 确保有材质
    if not obj.active_material:
        mat = bpy.data.materials.new(name=f"{object_name}_Material")
        obj.data.materials.append(mat)
        mat.use_nodes = True
    
    mat = obj.active_material
    
    if action == "ADD":
        # 创建或获取图像
        if texture_name:
            image = bpy.data.images.get(texture_name)
            if not image:
                image = bpy.data.images.new(name=texture_name, width=1024, height=1024)
        else:
            image = bpy.data.images.new(name=f"{object_name}_texture", width=1024, height=1024)
        
        # 在节点中添加图像纹理
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = image
        tex_node.location = (-300, 300)
        
        return {
            "success": True,
            "data": {
                "image_name": image.name,
                "action": "ADD"
            }
        }
    
    elif action == "REMOVE":
        # 移除纹理槽
        slots = mat.texture_paint_slots
        if slot_index < len(slots):
            # 不能直接移除槽，但可以清除图像
            pass
        
        return {
            "success": True,
            "data": {
                "action": "REMOVE"
            }
        }
    
    elif action == "SELECT":
        mat.paint_active_slot = slot_index
        
        return {
            "success": True,
            "data": {
                "active_slot": slot_index
            }
        }
    
    return {
        "success": False,
        "error": {"code": "INVALID_ACTION", "message": f"未知操作: {action}"}
    }


def handle_save(params: Dict[str, Any]) -> Dict[str, Any]:
    """保存纹理"""
    texture_name = params.get("texture_name")
    filepath = params.get("filepath")
    file_format = params.get("file_format", "PNG")
    
    image = bpy.data.images.get(texture_name)
    if not image:
        return {
            "success": False,
            "error": {"code": "IMAGE_NOT_FOUND", "message": f"图像不存在: {texture_name}"}
        }
    
    # 确保目录存在
    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # 设置格式和保存
    image.filepath_raw = filepath
    image.file_format = file_format
    image.save()
    
    return {
        "success": True,
        "data": {
            "filepath": filepath,
            "format": file_format
        }
    }
