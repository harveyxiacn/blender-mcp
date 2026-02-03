"""
ZBrush 连接处理器

处理与 ZBrush 集成的命令。
"""

from typing import Any, Dict
import bpy
import os
import platform


def _find_goz_paths() -> Dict[str, str]:
    """查找 GoZ 相关路径"""
    system = platform.system()
    
    if system == "Windows":
        # Windows GoZ 路径
        public_path = os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Pixologic", "GoZBrush")
        zbrush_paths = [
            r"C:\Program Files\Pixologic\ZBrush 2024",
            r"C:\Program Files\Pixologic\ZBrush 2023",
            r"C:\Program Files\Pixologic\ZBrush 2022",
            r"C:\Program Files\Maxon ZBrush"
        ]
    elif system == "Darwin":  # macOS
        public_path = "/Users/Shared/Pixologic/GoZBrush"
        zbrush_paths = [
            "/Applications/ZBrush 2024",
            "/Applications/ZBrush 2023",
            "/Applications/Maxon ZBrush.app"
        ]
    else:  # Linux (通过 Wine)
        public_path = os.path.expanduser("~/.wine/drive_c/users/Public/Pixologic/GoZBrush")
        zbrush_paths = []
    
    # 查找 ZBrush 安装
    zbrush_install = None
    for path in zbrush_paths:
        if os.path.exists(path):
            zbrush_install = path
            break
    
    return {
        "goz_public": public_path,
        "zbrush_install": zbrush_install,
        "goz_objects": os.path.join(public_path, "GoZBrush", "GoZ_ObjectList.txt") if public_path else None
    }


def handle_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出到 ZBrush"""
    object_name = params.get("object_name")
    filepath = params.get("filepath")
    subdivisions = params.get("subdivisions", 0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 选择对象
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 应用细分（如果需要）
        if subdivisions > 0:
            mod = obj.modifiers.new(name="Subdiv_ZBrush", type='SUBSURF')
            mod.levels = subdivisions
            mod.render_levels = subdivisions
            bpy.ops.object.modifier_apply(modifier=mod.name)
        
        # 确定导出路径
        if not filepath:
            goz_paths = _find_goz_paths()
            if goz_paths["goz_public"]:
                filepath = os.path.join(goz_paths["goz_public"], f"{object_name}.obj")
            else:
                import tempfile
                filepath = os.path.join(tempfile.gettempdir(), f"{object_name}.obj")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 导出 OBJ（ZBrush 最佳格式）
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            export_uv=True,
            export_normals=True,
            export_colors=True,
            export_triangulated_mesh=False  # ZBrush 可处理四边形
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "object": object_name,
                "subdivisions": subdivisions
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "EXPORT_ERROR", "message": str(e)}
        }


def handle_import(params: Dict[str, Any]) -> Dict[str, Any]:
    """从 ZBrush 导入"""
    filepath = params.get("filepath")
    import_polypaint = params.get("import_polypaint", True)
    import_mask = params.get("import_mask", True)
    
    try:
        # 如果没有指定路径，尝试从 GoZ 目录查找
        if not filepath:
            goz_paths = _find_goz_paths()
            if goz_paths["goz_objects"] and os.path.exists(goz_paths["goz_objects"]):
                with open(goz_paths["goz_objects"], 'r') as f:
                    lines = f.readlines()
                    if lines:
                        filepath = lines[-1].strip()
        
        if not filepath or not os.path.exists(filepath):
            return {
                "success": False,
                "error": {"code": "FILE_NOT_FOUND", "message": "未找到要导入的文件"}
            }
        
        # 导入 OBJ
        bpy.ops.wm.obj_import(
            filepath=filepath,
            import_vertex_groups=True
        )
        
        imported_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "imported_object": imported_obj.name if imported_obj else None
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "IMPORT_ERROR", "message": str(e)}
        }


def handle_goz_send(params: Dict[str, Any]) -> Dict[str, Any]:
    """通过 GoZ 发送"""
    object_name = params.get("object_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        goz_paths = _find_goz_paths()
        
        if not goz_paths["goz_public"]:
            return {
                "success": False,
                "error": {"code": "GOZ_NOT_FOUND", "message": "未找到 GoZ 安装"}
            }
        
        # 创建 GoZ 目录
        goz_dir = os.path.join(goz_paths["goz_public"], "GoZBrush")
        os.makedirs(goz_dir, exist_ok=True)
        
        # 导出到 GoZ 目录
        goz_file = os.path.join(goz_dir, f"{object_name}.GoZ")
        obj_file = os.path.join(goz_dir, f"{object_name}.obj")
        
        # 选择并导出
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        bpy.ops.wm.obj_export(
            filepath=obj_file,
            export_selected_objects=True
        )
        
        # 写入对象列表
        object_list_file = os.path.join(goz_dir, "GoZ_ObjectList.txt")
        with open(object_list_file, 'w') as f:
            f.write(obj_file)
        
        return {
            "success": True,
            "data": {
                "object": object_name,
                "goz_path": obj_file,
                "note": "请在 ZBrush 中点击 GoZ 按钮导入"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "GOZ_SEND_ERROR", "message": str(e)}
        }


def handle_goz_receive(params: Dict[str, Any]) -> Dict[str, Any]:
    """从 GoZ 接收"""
    try:
        goz_paths = _find_goz_paths()
        
        if not goz_paths["goz_public"]:
            return {
                "success": False,
                "error": {"code": "GOZ_NOT_FOUND", "message": "未找到 GoZ 安装"}
            }
        
        goz_dir = os.path.join(goz_paths["goz_public"], "GoZBrush")
        object_list_file = os.path.join(goz_dir, "GoZ_ObjectList.txt")
        
        if not os.path.exists(object_list_file):
            return {
                "success": False,
                "error": {"code": "NO_GOZ_DATA", "message": "没有待导入的 GoZ 数据"}
            }
        
        # 读取对象列表
        with open(object_list_file, 'r') as f:
            obj_path = f.readline().strip()
        
        if not obj_path or not os.path.exists(obj_path):
            return {
                "success": False,
                "error": {"code": "FILE_NOT_FOUND", "message": f"GoZ 文件不存在: {obj_path}"}
            }
        
        # 导入
        bpy.ops.wm.obj_import(filepath=obj_path)
        
        imported_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
        
        return {
            "success": True,
            "data": {
                "imported_object": imported_obj.name if imported_obj else None,
                "source_path": obj_path
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "GOZ_RECEIVE_ERROR", "message": str(e)}
        }


def handle_maps(params: Dict[str, Any]) -> Dict[str, Any]:
    """导入 ZBrush 贴图"""
    object_name = params.get("object_name")
    displacement_path = params.get("displacement_path")
    normal_path = params.get("normal_path")
    polypaint_path = params.get("polypaint_path")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 获取或创建材质
        if obj.data.materials:
            mat = obj.data.materials[0]
        else:
            mat = bpy.data.materials.new(name=f"ZBrush_{object_name}")
            obj.data.materials.append(mat)
        
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        
        output = nodes.get("Material Output")
        
        imported_maps = []
        
        # 置换贴图
        if displacement_path and os.path.exists(displacement_path):
            img = bpy.data.images.load(displacement_path)
            img.colorspace_settings.name = 'Non-Color'
            
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.location = (-600, -300)
            
            disp_node = nodes.new('ShaderNodeDisplacement')
            disp_node.location = (-200, -300)
            
            links.new(tex_node.outputs['Color'], disp_node.inputs['Height'])
            links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])
            
            mat.cycles.displacement_method = 'DISPLACEMENT'
            imported_maps.append("displacement")
        
        # 法线贴图
        if normal_path and os.path.exists(normal_path):
            img = bpy.data.images.load(normal_path)
            img.colorspace_settings.name = 'Non-Color'
            
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.location = (-600, 0)
            
            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (-300, 0)
            
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
            imported_maps.append("normal")
        
        # 顶点绘制贴图
        if polypaint_path and os.path.exists(polypaint_path):
            img = bpy.data.images.load(polypaint_path)
            
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.location = (-600, 300)
            
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
            imported_maps.append("polypaint")
        
        return {
            "success": True,
            "data": {
                "object": object_name,
                "material": mat.name,
                "imported_maps": imported_maps
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "MAPS_ERROR", "message": str(e)}
        }


def handle_decimate_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出减面模型"""
    object_name = params.get("object_name")
    target_faces = params.get("target_faces", 10000)
    filepath = params.get("filepath")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 复制对象
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        
        decimated_obj = bpy.context.active_object
        decimated_obj.name = f"{object_name}_decimated"
        
        # 计算减面比例
        current_faces = len(decimated_obj.data.polygons)
        if current_faces > target_faces:
            ratio = target_faces / current_faces
            
            # 添加减面修改器
            mod = decimated_obj.modifiers.new(name="Decimate", type='DECIMATE')
            mod.ratio = ratio
            bpy.ops.object.modifier_apply(modifier=mod.name)
        
        # 导出
        if not filepath:
            import tempfile
            filepath = os.path.join(tempfile.gettempdir(), f"{object_name}_decimated.obj")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True
        )
        
        final_faces = len(decimated_obj.data.polygons)
        
        # 删除临时对象
        bpy.data.objects.remove(decimated_obj, do_unlink=True)
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "original_faces": current_faces,
                "final_faces": final_faces
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DECIMATE_ERROR", "message": str(e)}
        }


def handle_detect(params: Dict[str, Any]) -> Dict[str, Any]:
    """检测 ZBrush 安装"""
    try:
        goz_paths = _find_goz_paths()
        
        return {
            "success": True,
            "data": {
                "zbrush_installed": bool(goz_paths["zbrush_install"]),
                "zbrush_path": goz_paths["zbrush_install"],
                "goz_available": bool(goz_paths["goz_public"]),
                "goz_path": goz_paths["goz_public"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DETECT_ERROR", "message": str(e)}
        }
