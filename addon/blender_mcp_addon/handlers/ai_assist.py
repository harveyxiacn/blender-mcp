"""
AI辅助处理器

处理AI辅助功能命令。
"""

from typing import Any, Dict, List
import bpy
import math


def handle_describe_scene(params: Dict[str, Any]) -> Dict[str, Any]:
    """描述场景"""
    detail_level = params.get("detail_level", "medium")
    include_materials = params.get("include_materials", True)
    include_animations = params.get("include_animations", True)
    
    try:
        scene = bpy.context.scene
        
        description = {
            "name": scene.name,
            "frame_range": [scene.frame_start, scene.frame_end],
            "current_frame": scene.frame_current,
            "render_engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y]
        }
        
        # 对象统计
        objects = {
            "total": len(scene.objects),
            "by_type": {}
        }
        
        for obj in scene.objects:
            obj_type = obj.type
            if obj_type not in objects["by_type"]:
                objects["by_type"][obj_type] = 0
            objects["by_type"][obj_type] += 1
        
        description["objects"] = objects
        
        # 详细信息
        if detail_level in ["medium", "high"]:
            object_list = []
            for obj in scene.objects:
                obj_info = {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                    "visible": obj.visible_get()
                }
                
                if detail_level == "high":
                    obj_info["rotation"] = list(obj.rotation_euler)
                    obj_info["scale"] = list(obj.scale)
                    
                    if obj.type == 'MESH':
                        mesh = obj.data
                        obj_info["vertices"] = len(mesh.vertices)
                        obj_info["faces"] = len(mesh.polygons)
                        obj_info["edges"] = len(mesh.edges)
                
                object_list.append(obj_info)
            
            description["object_list"] = object_list
        
        # 材质信息
        if include_materials:
            materials = []
            for mat in bpy.data.materials:
                mat_info = {
                    "name": mat.name,
                    "use_nodes": mat.use_nodes
                }
                if mat.use_nodes and mat.node_tree:
                    mat_info["node_count"] = len(mat.node_tree.nodes)
                materials.append(mat_info)
            
            description["materials"] = {
                "count": len(materials),
                "list": materials[:20] if detail_level != "high" else materials
            }
        
        # 动画信息
        if include_animations:
            animations = []
            for action in bpy.data.actions:
                anim_info = {
                    "name": action.name,
                    "frame_range": list(action.frame_range)
                }
                if detail_level == "high":
                    anim_info["fcurve_count"] = len(action.fcurves)
                animations.append(anim_info)
            
            description["animations"] = {
                "count": len(animations),
                "list": animations
            }
        
        # 世界设置
        if scene.world:
            description["world"] = {
                "name": scene.world.name,
                "use_nodes": scene.world.use_nodes
            }
        
        return {
            "success": True,
            "data": description
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DESCRIBE_ERROR", "message": str(e)}
        }


def handle_analyze_object(params: Dict[str, Any]) -> Dict[str, Any]:
    """分析对象"""
    object_name = params.get("object_name")
    include_modifiers = params.get("include_modifiers", True)
    include_topology = params.get("include_topology", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        analysis = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "dimensions": list(obj.dimensions),
            "visible": obj.visible_get(),
            "parent": obj.parent.name if obj.parent else None
        }
        
        # 网格拓扑分析
        if obj.type == 'MESH' and include_topology:
            mesh = obj.data
            
            analysis["topology"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "faces": len(mesh.polygons),
                "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons),
                "has_custom_normals": mesh.has_custom_normals,
                "uv_layers": len(mesh.uv_layers),
                "vertex_colors": len(mesh.vertex_colors) if hasattr(mesh, 'vertex_colors') else 0
            }
            
            # 分析面类型
            ngons = 0
            quads = 0
            tris = 0
            for poly in mesh.polygons:
                if len(poly.vertices) > 4:
                    ngons += 1
                elif len(poly.vertices) == 4:
                    quads += 1
                else:
                    tris += 1
            
            analysis["topology"]["face_types"] = {
                "triangles": tris,
                "quads": quads,
                "ngons": ngons
            }
        
        # 修改器分析
        if include_modifiers:
            modifiers = []
            for mod in obj.modifiers:
                mod_info = {
                    "name": mod.name,
                    "type": mod.type,
                    "show_viewport": mod.show_viewport,
                    "show_render": mod.show_render
                }
                modifiers.append(mod_info)
            
            analysis["modifiers"] = modifiers
        
        # 材质
        if obj.data and hasattr(obj.data, 'materials'):
            analysis["materials"] = [mat.name if mat else None for mat in obj.data.materials]
        
        # 约束
        if obj.constraints:
            analysis["constraints"] = [{"name": c.name, "type": c.type} for c in obj.constraints]
        
        # 动画数据
        if obj.animation_data:
            analysis["animation"] = {
                "action": obj.animation_data.action.name if obj.animation_data.action else None,
                "nla_tracks": len(obj.animation_data.nla_tracks)
            }
        
        return {
            "success": True,
            "data": analysis
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "ANALYZE_ERROR", "message": str(e)}
        }


def handle_suggest_optimization(params: Dict[str, Any]) -> Dict[str, Any]:
    """优化建议"""
    target = params.get("target", "performance")
    
    try:
        suggestions = []
        
        scene = bpy.context.scene
        
        # 检查高多边形对象
        high_poly_objects = []
        for obj in scene.objects:
            if obj.type == 'MESH':
                face_count = len(obj.data.polygons)
                if face_count > 100000:
                    high_poly_objects.append({
                        "name": obj.name,
                        "faces": face_count
                    })
        
        if high_poly_objects:
            suggestions.append({
                "type": "HIGH_POLY",
                "severity": "warning",
                "message": f"发现 {len(high_poly_objects)} 个高多边形对象",
                "suggestion": "考虑使用细分修改器或减面工具",
                "objects": high_poly_objects[:5]
            })
        
        # 检查未应用的变换
        unapplied_transforms = []
        for obj in scene.objects:
            if obj.type == 'MESH':
                if list(obj.scale) != [1, 1, 1]:
                    unapplied_transforms.append(obj.name)
        
        if unapplied_transforms:
            suggestions.append({
                "type": "UNAPPLIED_SCALE",
                "severity": "info",
                "message": f"发现 {len(unapplied_transforms)} 个对象有未应用的缩放",
                "suggestion": "应用缩放以避免导出问题",
                "objects": unapplied_transforms[:10]
            })
        
        # 检查材质
        unused_materials = []
        for mat in bpy.data.materials:
            if mat.users == 0:
                unused_materials.append(mat.name)
        
        if unused_materials:
            suggestions.append({
                "type": "UNUSED_MATERIALS",
                "severity": "info" if target != "memory" else "warning",
                "message": f"发现 {len(unused_materials)} 个未使用的材质",
                "suggestion": "删除未使用的材质以减少内存使用",
                "items": unused_materials[:10]
            })
        
        # 检查纹理大小
        large_textures = []
        for img in bpy.data.images:
            if img.size[0] * img.size[1] > 4096 * 4096:
                large_textures.append({
                    "name": img.name,
                    "size": list(img.size)
                })
        
        if large_textures:
            suggestions.append({
                "type": "LARGE_TEXTURES",
                "severity": "warning" if target in ["performance", "memory"] else "info",
                "message": f"发现 {len(large_textures)} 个超大纹理",
                "suggestion": "考虑降低纹理分辨率",
                "textures": large_textures
            })
        
        # 渲染设置建议
        if target == "performance":
            if scene.render.engine == 'CYCLES':
                suggestions.append({
                    "type": "RENDER_ENGINE",
                    "severity": "info",
                    "message": "当前使用 Cycles 渲染引擎",
                    "suggestion": "对于实时预览，考虑使用 EEVEE"
                })
        
        return {
            "success": True,
            "data": {
                "target": target,
                "suggestions": suggestions,
                "count": len(suggestions)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SUGGEST_ERROR", "message": str(e)}
        }


def handle_auto_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """自动材质"""
    object_name = params.get("object_name")
    description = params.get("description", "")
    style = params.get("style", "realistic")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 根据描述创建材质
        mat = bpy.data.materials.new(name=f"{object_name}_{description[:20]}")
        mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # 清除默认节点
        nodes.clear()
        
        # 创建输出节点
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # 创建 BSDF 节点
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # 根据描述设置参数
        desc_lower = description.lower()
        
        # 金属材质
        if any(word in desc_lower for word in ['metal', '金属', 'steel', '钢', 'iron', '铁', 'gold', '金', 'silver', '银', 'copper', '铜']):
            bsdf.inputs['Metallic'].default_value = 1.0
            bsdf.inputs['Roughness'].default_value = 0.3
            
            if 'gold' in desc_lower or '金' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
            elif 'silver' in desc_lower or '银' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (0.972, 0.960, 0.915, 1.0)
            elif 'copper' in desc_lower or '铜' in desc_lower:
                bsdf.inputs['Base Color'].default_value = (0.955, 0.637, 0.538, 1.0)
            else:
                bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        
        # 木材
        elif any(word in desc_lower for word in ['wood', '木', 'wooden', '木质']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.7
            bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
        
        # 玻璃
        elif any(word in desc_lower for word in ['glass', '玻璃', 'transparent', '透明']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.0
            bsdf.inputs['Transmission'].default_value = 1.0
            bsdf.inputs['IOR'].default_value = 1.45
        
        # 塑料
        elif any(word in desc_lower for word in ['plastic', '塑料']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.4
            bsdf.inputs['Specular IOR Level'].default_value = 0.5
        
        # 布料
        elif any(word in desc_lower for word in ['fabric', '布', 'cloth', '织物', 'cotton', '棉']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.9
            bsdf.inputs['Sheen Weight'].default_value = 0.3
        
        # 皮肤
        elif any(word in desc_lower for word in ['skin', '皮肤']):
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.5
            bsdf.inputs['Subsurface Weight'].default_value = 0.3
            bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.5, 1.0)
        
        # 默认
        else:
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.5
        
        # 风格调整
        if style == "cartoon":
            bsdf.inputs['Roughness'].default_value = 1.0
        elif style == "stylized":
            bsdf.inputs['Roughness'].default_value = 0.7
        
        # 连接节点
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # 应用材质
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        return {
            "success": True,
            "data": {
                "material_name": mat.name,
                "description": description,
                "style": style
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "AUTO_MATERIAL_ERROR", "message": str(e)}
        }


def handle_scene_statistics(params: Dict[str, Any]) -> Dict[str, Any]:
    """场景统计"""
    include_hidden = params.get("include_hidden", False)
    
    try:
        scene = bpy.context.scene
        
        stats = {
            "scene_name": scene.name,
            "objects": {
                "total": 0,
                "visible": 0,
                "by_type": {}
            },
            "geometry": {
                "total_vertices": 0,
                "total_edges": 0,
                "total_faces": 0,
                "total_triangles": 0
            },
            "materials": {
                "total": len(bpy.data.materials),
                "used": 0
            },
            "textures": {
                "total": len(bpy.data.images),
                "memory_estimate_mb": 0
            },
            "animations": {
                "actions": len(bpy.data.actions),
                "total_keyframes": 0
            }
        }
        
        # 对象统计
        for obj in scene.objects:
            if not include_hidden and not obj.visible_get():
                continue
            
            stats["objects"]["total"] += 1
            if obj.visible_get():
                stats["objects"]["visible"] += 1
            
            obj_type = obj.type
            if obj_type not in stats["objects"]["by_type"]:
                stats["objects"]["by_type"][obj_type] = 0
            stats["objects"]["by_type"][obj_type] += 1
            
            # 网格统计
            if obj.type == 'MESH':
                mesh = obj.data
                stats["geometry"]["total_vertices"] += len(mesh.vertices)
                stats["geometry"]["total_edges"] += len(mesh.edges)
                stats["geometry"]["total_faces"] += len(mesh.polygons)
                stats["geometry"]["total_triangles"] += sum(len(p.vertices) - 2 for p in mesh.polygons)
        
        # 材质统计
        for mat in bpy.data.materials:
            if mat.users > 0:
                stats["materials"]["used"] += 1
        
        # 纹理内存估算
        for img in bpy.data.images:
            if img.size[0] > 0 and img.size[1] > 0:
                # 估算：RGBA 4字节每像素
                memory_bytes = img.size[0] * img.size[1] * 4
                stats["textures"]["memory_estimate_mb"] += memory_bytes / (1024 * 1024)
        
        stats["textures"]["memory_estimate_mb"] = round(stats["textures"]["memory_estimate_mb"], 2)
        
        # 动画统计
        for action in bpy.data.actions:
            if hasattr(action, 'fcurves'):
                for fcurve in action.fcurves:
                    stats["animations"]["total_keyframes"] += len(fcurve.keyframe_points)
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "STATISTICS_ERROR", "message": str(e)}
        }


def handle_list_issues(params: Dict[str, Any]) -> Dict[str, Any]:
    """检测问题"""
    try:
        issues = []
        
        scene = bpy.context.scene
        
        # 检查非流形几何
        for obj in scene.objects:
            if obj.type == 'MESH':
                mesh = obj.data
                
                # 检查孤立顶点
                used_verts = set()
                for edge in mesh.edges:
                    used_verts.update(edge.vertices)
                
                isolated = len(mesh.vertices) - len(used_verts)
                if isolated > 0:
                    issues.append({
                        "type": "ISOLATED_VERTICES",
                        "severity": "warning",
                        "object": obj.name,
                        "message": f"发现 {isolated} 个孤立顶点"
                    })
                
                # 检查零面积面
                zero_area_faces = 0
                for poly in mesh.polygons:
                    if poly.area < 0.00001:
                        zero_area_faces += 1
                
                if zero_area_faces > 0:
                    issues.append({
                        "type": "ZERO_AREA_FACES",
                        "severity": "warning",
                        "object": obj.name,
                        "message": f"发现 {zero_area_faces} 个零面积面"
                    })
        
        # 检查缺失的纹理
        for img in bpy.data.images:
            if img.source == 'FILE' and img.filepath:
                import os
                filepath = bpy.path.abspath(img.filepath)
                if not os.path.exists(filepath):
                    issues.append({
                        "type": "MISSING_TEXTURE",
                        "severity": "error",
                        "image": img.name,
                        "message": f"纹理文件不存在: {img.filepath}"
                    })
        
        # 检查循环依赖
        for obj in scene.objects:
            if obj.parent:
                parent = obj.parent
                visited = {obj.name}
                while parent:
                    if parent.name in visited:
                        issues.append({
                            "type": "CIRCULAR_PARENTING",
                            "severity": "error",
                            "object": obj.name,
                            "message": "检测到循环父子关系"
                        })
                        break
                    visited.add(parent.name)
                    parent = parent.parent
        
        # 检查过大的对象
        for obj in scene.objects:
            max_dim = max(obj.dimensions)
            if max_dim > 1000:
                issues.append({
                    "type": "OVERSIZED_OBJECT",
                    "severity": "info",
                    "object": obj.name,
                    "message": f"对象尺寸过大: {max_dim:.1f}"
                })
        
        return {
            "success": True,
            "data": {
                "issues": issues,
                "total": len(issues),
                "by_severity": {
                    "error": len([i for i in issues if i["severity"] == "error"]),
                    "warning": len([i for i in issues if i["severity"] == "warning"]),
                    "info": len([i for i in issues if i["severity"] == "info"])
                }
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "ISSUES_ERROR", "message": str(e)}
        }
