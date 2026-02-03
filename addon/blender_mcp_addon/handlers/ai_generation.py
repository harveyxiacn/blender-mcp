"""
AI 辅助建模处理器

处理 AI 生成纹理、材质等命令。
注意：实际的 AI 服务调用应在 MCP 服务端完成，这里处理 Blender 侧的操作。
"""

from typing import Any, Dict
import bpy
import os
import tempfile
import json


# AI 配置存储
AI_CONFIG = {
    "provider": "stability",
    "api_key": None,
    "local_url": "http://127.0.0.1:7860",
    "model": "sdxl-1.0"
}


def handle_config(params: Dict[str, Any]) -> Dict[str, Any]:
    """配置 AI 服务"""
    global AI_CONFIG
    
    try:
        if params.get("provider"):
            AI_CONFIG["provider"] = params["provider"]
        if params.get("api_key"):
            AI_CONFIG["api_key"] = params["api_key"]
        if params.get("local_url"):
            AI_CONFIG["local_url"] = params["local_url"]
        if params.get("model"):
            AI_CONFIG["model"] = params["model"]
        
        return {
            "success": True,
            "data": {
                "provider": AI_CONFIG["provider"],
                "model": AI_CONFIG["model"],
                "local_url": AI_CONFIG["local_url"] if AI_CONFIG["provider"] == "local" else None,
                "api_key_set": bool(AI_CONFIG["api_key"])
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CONFIG_ERROR", "message": str(e)}
        }


def handle_texture_generate(params: Dict[str, Any]) -> Dict[str, Any]:
    """AI 生成纹理"""
    prompt = params.get("prompt")
    negative_prompt = params.get("negative_prompt", "")
    width = params.get("width", 1024)
    height = params.get("height", 1024)
    seamless = params.get("seamless", True)
    apply_to = params.get("apply_to")
    
    try:
        # 注意：实际的 AI 生成应该在 MCP 服务端完成
        # 这里模拟生成并处理 Blender 侧的操作
        
        # 构建完整提示
        full_prompt = prompt
        if seamless:
            full_prompt += ", seamless texture, tileable, pattern"
        
        # 创建一个临时的纯色纹理作为占位符
        # 实际实现中，MCP 服务端会调用 AI API 生成图像并保存
        temp_dir = tempfile.gettempdir()
        texture_path = os.path.join(temp_dir, f"ai_texture_{hash(prompt)}.png")
        
        # 创建新图像
        img = bpy.data.images.new(
            name=f"AI_{prompt[:20]}",
            width=width,
            height=height,
            alpha=True
        )
        
        # 如果指定了应用对象
        if apply_to:
            obj = bpy.data.objects.get(apply_to)
            if obj and obj.type == 'MESH':
                # 创建材质
                mat = bpy.data.materials.new(name=f"AI_Material_{prompt[:15]}")
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                
                # 清除默认节点
                nodes.clear()
                
                # 创建节点
                output = nodes.new('ShaderNodeOutputMaterial')
                output.location = (300, 0)
                
                bsdf = nodes.new('ShaderNodeBsdfPrincipled')
                bsdf.location = (0, 0)
                
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.location = (-300, 0)
                tex_node.image = img
                
                # 连接
                links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
                links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
                
                # 应用材质
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        return {
            "success": True,
            "data": {
                "image_name": img.name,
                "prompt": full_prompt,
                "size": [width, height],
                "applied_to": apply_to,
                "note": "AI generation requires API configuration. Use blender_ai_config to set up."
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "TEXTURE_GEN_ERROR", "message": str(e)}
        }


def handle_concept_art(params: Dict[str, Any]) -> Dict[str, Any]:
    """生成概念图"""
    prompt = params.get("prompt")
    style = params.get("style", "realistic")
    aspect_ratio = params.get("aspect_ratio", "16:9")
    
    try:
        # 解析宽高比
        ratio_map = {
            "16:9": (1920, 1080),
            "1:1": (1024, 1024),
            "4:3": (1024, 768),
            "9:16": (1080, 1920)
        }
        width, height = ratio_map.get(aspect_ratio, (1920, 1080))
        
        # 添加风格提示
        style_prompts = {
            "realistic": "photorealistic, detailed, high quality",
            "anime": "anime style, cel shaded, vibrant colors",
            "cartoon": "cartoon style, bold lines, stylized",
            "sketch": "pencil sketch, line art, concept art drawing"
        }
        
        full_prompt = f"{prompt}, {style_prompts.get(style, '')}"
        
        # 创建图像占位符
        img = bpy.data.images.new(
            name=f"Concept_{prompt[:20]}",
            width=width,
            height=height,
            alpha=False
        )
        
        return {
            "success": True,
            "data": {
                "image_name": img.name,
                "prompt": full_prompt,
                "style": style,
                "size": [width, height],
                "note": "AI generation requires API configuration."
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CONCEPT_ART_ERROR", "message": str(e)}
        }


def handle_material_from_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """从文本描述生成材质"""
    description = params.get("description")
    object_name = params.get("object_name")
    generate_textures = params.get("generate_textures", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 解析材质描述
        desc_lower = description.lower()
        
        # 创建材质
        mat = bpy.data.materials.new(name=f"AI_{description[:20]}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # 获取 Principled BSDF
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        
        # 根据描述设置参数
        # 金属类
        if any(word in desc_lower for word in ['metal', '金属', 'steel', '钢', 'iron', '铁', 'chrome', '铬', 'aluminum', '铝']):
            bsdf.inputs['Metallic'].default_value = 1.0
            bsdf.inputs['Roughness'].default_value = 0.3
            
            if 'rust' in desc_lower or '锈' in desc_lower or '生锈' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.8
            elif 'gold' in desc_lower or '金' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
            elif 'silver' in desc_lower or '银' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (0.972, 0.960, 0.915, 1.0)
            elif 'copper' in desc_lower or '铜' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (0.955, 0.637, 0.538, 1.0)
            else:
                bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        
        # 木材
        elif any(word in desc_lower for word in ['wood', '木', 'wooden', '木质', 'oak', '橡木', 'pine', '松木']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.7
            bsdf.inputs['Base Color'].default_value = (0.4, 0.25, 0.13, 1.0)
        
        # 石材
        elif any(word in desc_lower for word in ['stone', '石', 'marble', '大理石', 'granite', '花岗岩', 'concrete', '混凝土']):
            bsdf.inputs['Metallic'].default_value = 0.0
            if 'marble' in desc_lower or '大理石' in desc_lower:
                bsdf.inputs['Roughness'].default_value = 0.2
                bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
            else:
                bsdf.inputs['Roughness'].default_value = 0.8
                bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
        
        # 玻璃
        elif any(word in desc_lower for word in ['glass', '玻璃', 'transparent', '透明', 'crystal', '水晶']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.0
            bsdf.inputs['Transmission'].default_value = 1.0
            bsdf.inputs['IOR'].default_value = 1.45
        
        # 布料
        elif any(word in desc_lower for word in ['fabric', '布', 'cloth', '织物', 'velvet', '天鹅绒', 'silk', '丝绸']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.8
            bsdf.inputs['Sheen Weight'].default_value = 0.5
        
        # 皮革
        elif any(word in desc_lower for word in ['leather', '皮革', '皮']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.6
            bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.15, 1.0)
        
        # 塑料
        elif any(word in desc_lower for word in ['plastic', '塑料']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.3
            bsdf.inputs['Specular IOR Level'].default_value = 0.5
        
        # 应用材质
        if obj.type == 'MESH':
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
        
        return {
            "success": True,
            "data": {
                "material_name": mat.name,
                "description": description,
                "applied_to": object_name
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "MATERIAL_FROM_TEXT_ERROR", "message": str(e)}
        }


def handle_upscale(params: Dict[str, Any]) -> Dict[str, Any]:
    """AI 纹理放大"""
    image_path = params.get("image_path")
    scale = params.get("scale", 2)
    
    try:
        # 检查图像是否存在
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": {"code": "IMAGE_NOT_FOUND", "message": f"图像不存在: {image_path}"}
            }
        
        # 加载图像
        img = bpy.data.images.load(image_path)
        original_size = [img.size[0], img.size[1]]
        
        # 计算新尺寸
        new_width = original_size[0] * scale
        new_height = original_size[1] * scale
        
        # 注意：实际的 AI 放大需要在 MCP 服务端完成
        # 这里使用 Blender 的缩放作为占位
        img.scale(new_width, new_height)
        
        # 保存
        output_path = image_path.replace('.', f'_x{scale}.')
        img.filepath_raw = output_path
        img.file_format = 'PNG'
        img.save()
        
        return {
            "success": True,
            "data": {
                "input": image_path,
                "output": output_path,
                "original_size": original_size,
                "new_size": [new_width, new_height],
                "scale": scale,
                "note": "True AI upscaling requires API configuration."
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "UPSCALE_ERROR", "message": str(e)}
        }


def handle_remove_background(params: Dict[str, Any]) -> Dict[str, Any]:
    """背景移除"""
    image_path = params.get("image_path")
    output_path = params.get("output_path")
    
    try:
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": {"code": "IMAGE_NOT_FOUND", "message": f"图像不存在: {image_path}"}
            }
        
        # 生成输出路径
        if not output_path:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_nobg.png"
        
        # 加载图像
        img = bpy.data.images.load(image_path)
        
        # 注意：实际的背景移除需要 AI 服务
        # 这里只是返回信息
        
        return {
            "success": True,
            "data": {
                "input": image_path,
                "output": output_path,
                "image_name": img.name,
                "note": "AI background removal requires API configuration."
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "REMOVE_BG_ERROR", "message": str(e)}
        }


def handle_image_to_reference(params: Dict[str, Any]) -> Dict[str, Any]:
    """生成图像并设置为参考图"""
    prompt = params.get("prompt")
    as_background = params.get("as_background", False)
    
    try:
        # 创建参考图像占位符
        img = bpy.data.images.new(
            name=f"Reference_{prompt[:20]}",
            width=1920,
            height=1080,
            alpha=True
        )
        
        if as_background:
            # 设置为世界背景
            world = bpy.context.scene.world
            if not world:
                world = bpy.data.worlds.new("World")
                bpy.context.scene.world = world
            
            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            
            # 添加环境纹理节点
            env_tex = nodes.new('ShaderNodeTexEnvironment')
            env_tex.image = img
            
            bg = nodes.get('Background')
            if bg:
                links.new(env_tex.outputs['Color'], bg.inputs['Color'])
        else:
            # 创建为空物体的参考图
            bpy.ops.object.empty_add(type='IMAGE', location=(0, -5, 0))
            empty = bpy.context.active_object
            empty.name = f"Reference_{prompt[:15]}"
            empty.data = img
            empty.empty_display_size = 5
        
        return {
            "success": True,
            "data": {
                "image_name": img.name,
                "prompt": prompt,
                "as_background": as_background,
                "note": "AI generation requires API configuration."
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "REFERENCE_ERROR", "message": str(e)}
        }
