"""
Substance 连接处理器

处理与 Substance Painter 集成的命令。
"""

from typing import Any, Dict, List
import bpy


def get_principled_bsdf(nodes):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    # 先尝试按名称查找
    bsdf = get_principled_bsdf(nodes)
    if bsdf:
        return bsdf
    # 再按类型查找
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

import os
import glob


# Substance 链接状态
SUBSTANCE_LINK = {
    "active": False,
    "project_path": None,
    "watch_interval": 2.0,
    "timer": None
}


def _find_substance_installation() -> str:
    """查找 Substance Painter 安装路径"""
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        # 常见安装路径
        paths = [
            r"C:\Program Files\Adobe\Adobe Substance 3D Painter",
            r"C:\Program Files\Allegorithmic\Substance Painter",
            os.path.expandvars(r"%LOCALAPPDATA%\Adobe\Adobe Substance 3D Painter")
        ]
    elif system == "Darwin":  # macOS
        paths = [
            "/Applications/Adobe Substance 3D Painter.app",
            "/Applications/Substance Painter.app"
        ]
    else:  # Linux
        paths = [
            "/opt/Adobe/Adobe_Substance_3D_Painter",
            os.path.expanduser("~/Adobe/Adobe_Substance_3D_Painter")
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None


def handle_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出到 Substance"""
    object_name = params.get("object_name")
    filepath = params.get("filepath")
    format = params.get("format", "FBX")
    export_uvs = params.get("export_uvs", True)
    triangulate = params.get("triangulate", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 选择对象
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 应用三角化修改器（如果需要）
        if triangulate:
            mod = obj.modifiers.new(name="Triangulate_Export", type='TRIANGULATE')
            mod.quad_method = 'BEAUTY'
            mod.ngon_method = 'BEAUTY'
        
        if format == "FBX":
            if not filepath.lower().endswith('.fbx'):
                filepath = filepath + '.fbx'
            
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                use_mesh_modifiers=True,
                mesh_smooth_type='FACE',
                use_tspace=True,
                # Substance 优化设置
                axis_forward='-Z',
                axis_up='Y',
                global_scale=1.0
            )
        else:
            if not filepath.lower().endswith('.obj'):
                filepath = filepath + '.obj'
            
            bpy.ops.wm.obj_export(
                filepath=filepath,
                export_selected_objects=True,
                export_uv=export_uvs,
                export_triangulated_mesh=triangulate
            )
        
        # 移除临时修改器
        if triangulate and "Triangulate_Export" in obj.modifiers:
            obj.modifiers.remove(obj.modifiers["Triangulate_Export"])
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "format": format,
                "object": object_name
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "EXPORT_ERROR", "message": str(e)}
        }


def handle_import(params: Dict[str, Any]) -> Dict[str, Any]:
    """导入 Substance 纹理"""
    texture_folder = params.get("texture_folder")
    object_name = params.get("object_name")
    naming_convention = params.get("naming_convention", "substance")
    
    if not os.path.exists(texture_folder):
        return {
            "success": False,
            "error": {"code": "FOLDER_NOT_FOUND", "message": f"文件夹不存在: {texture_folder}"}
        }
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # Substance Painter 默认命名模式
        texture_patterns = {
            "substance": {
                "base_color": ["*_BaseColor.*", "*_basecolor.*", "*_diffuse.*"],
                "roughness": ["*_Roughness.*", "*_roughness.*"],
                "metallic": ["*_Metallic.*", "*_metallic.*"],
                "normal": ["*_Normal.*", "*_normal.*", "*_NormalOpenGL.*"],
                "height": ["*_Height.*", "*_height.*", "*_displacement.*"],
                "ao": ["*_AO.*", "*_ao.*", "*_ambientocclusion.*"],
                "emissive": ["*_Emissive.*", "*_emissive.*"]
            }
        }
        
        patterns = texture_patterns.get(naming_convention, texture_patterns["substance"])
        
        # 查找纹理文件
        found_textures = {}
        for tex_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = glob.glob(os.path.join(texture_folder, pattern))
                if matches:
                    found_textures[tex_type] = matches[0]
                    break
        
        if not found_textures:
            return {
                "success": False,
                "error": {"code": "NO_TEXTURES", "message": "未找到符合命名规范的纹理文件"}
            }
        
        # 创建材质
        mat = bpy.data.materials.new(name=f"Substance_{object_name}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # 获取 Principled BSDF
        bsdf = get_principled_bsdf(nodes)
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        output = nodes.get("Material Output")
        if not output:
            output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # 加载纹理
        x_offset = -600
        y_offset = 300
        
        for tex_type, tex_path in found_textures.items():
            img = bpy.data.images.load(tex_path)
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.location = (x_offset, y_offset)
            
            if tex_type == "base_color":
                links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
            elif tex_type == "roughness":
                img.colorspace_settings.name = 'Non-Color'
                links.new(tex_node.outputs['Color'], bsdf.inputs['Roughness'])
            elif tex_type == "metallic":
                img.colorspace_settings.name = 'Non-Color'
                links.new(tex_node.outputs['Color'], bsdf.inputs['Metallic'])
            elif tex_type == "normal":
                img.colorspace_settings.name = 'Non-Color'
                normal_map = nodes.new('ShaderNodeNormalMap')
                normal_map.location = (x_offset + 200, y_offset)
                links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
            elif tex_type == "emissive":
                links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
                bsdf.inputs['Emission Strength'].default_value = 1.0
            
            y_offset -= 300
        
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
                "textures_imported": list(found_textures.keys()),
                "object": object_name
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "IMPORT_ERROR", "message": str(e)}
        }


def handle_link(params: Dict[str, Any]) -> Dict[str, Any]:
    """建立实时链接"""
    project_path = params.get("project_path")
    watch_interval = params.get("watch_interval", 2.0)
    
    try:
        global SUBSTANCE_LINK
        
        SUBSTANCE_LINK["active"] = True
        SUBSTANCE_LINK["project_path"] = project_path
        SUBSTANCE_LINK["watch_interval"] = watch_interval
        
        # 获取导出目录
        export_dir = os.path.dirname(project_path)
        
        return {
            "success": True,
            "data": {
                "status": "linked",
                "project_path": project_path,
                "watch_interval": watch_interval,
                "export_directory": export_dir,
                "note": "监控功能需要在 Blender 中启用定时器"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LINK_ERROR", "message": str(e)}
        }


def handle_unlink(params: Dict[str, Any]) -> Dict[str, Any]:
    """断开链接"""
    try:
        global SUBSTANCE_LINK
        
        SUBSTANCE_LINK["active"] = False
        SUBSTANCE_LINK["project_path"] = None
        
        return {
            "success": True,
            "data": {
                "status": "unlinked"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "UNLINK_ERROR", "message": str(e)}
        }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """准备烘焙"""
    high_poly = params.get("high_poly")
    low_poly = params.get("low_poly")
    output_folder = params.get("output_folder")
    maps = params.get("maps", ["normal", "ao", "curvature"])
    resolution = params.get("resolution", 2048)
    
    hp_obj = bpy.data.objects.get(high_poly)
    lp_obj = bpy.data.objects.get(low_poly)
    
    if not hp_obj:
        return {
            "success": False,
            "error": {"code": "HIGH_POLY_NOT_FOUND", "message": f"高模不存在: {high_poly}"}
        }
    
    if not lp_obj:
        return {
            "success": False,
            "error": {"code": "LOW_POLY_NOT_FOUND", "message": f"低模不存在: {low_poly}"}
        }
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        # 导出高模
        hp_path = os.path.join(output_folder, f"{high_poly}_high.fbx")
        bpy.ops.object.select_all(action='DESELECT')
        hp_obj.select_set(True)
        bpy.context.view_layer.objects.active = hp_obj
        bpy.ops.export_scene.fbx(filepath=hp_path, use_selection=True)
        
        # 导出低模
        lp_path = os.path.join(output_folder, f"{low_poly}_low.fbx")
        bpy.ops.object.select_all(action='DESELECT')
        lp_obj.select_set(True)
        bpy.context.view_layer.objects.active = lp_obj
        bpy.ops.export_scene.fbx(filepath=lp_path, use_selection=True)
        
        return {
            "success": True,
            "data": {
                "high_poly_path": hp_path,
                "low_poly_path": lp_path,
                "output_folder": output_folder,
                "maps": maps,
                "resolution": resolution,
                "note": "模型已导出，请在 Substance Painter 中进行烘焙"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BAKE_ERROR", "message": str(e)}
        }


def handle_detect(params: Dict[str, Any]) -> Dict[str, Any]:
    """检测 Substance 安装"""
    try:
        install_path = _find_substance_installation()
        
        return {
            "success": True,
            "data": {
                "installed": bool(install_path),
                "path": install_path
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DETECT_ERROR", "message": str(e)}
        }
