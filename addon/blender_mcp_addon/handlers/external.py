"""
外部集成处理器

处理与外部工具（Unity、Unreal等）集成的命令。
"""

from typing import Any, Dict, List
import bpy
import os


def _select_objects(object_names: List[str] = None):
    """选择指定对象"""
    bpy.ops.object.select_all(action='DESELECT')
    
    if object_names:
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
    else:
        # 选择所有可见的网格对象
        for obj in bpy.context.view_layer.objects:
            if obj.type in ('MESH', 'ARMATURE', 'CURVE'):
                obj.select_set(True)


def handle_unity_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """Unity导出"""
    filepath = params.get("filepath")
    objects = params.get("objects")
    apply_modifiers = params.get("apply_modifiers", True)
    apply_scale = params.get("apply_scale", True)
    export_animations = params.get("export_animations", True)
    bake_animation = params.get("bake_animation", False)
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        _select_objects(objects)
        
        # Unity FBX 导出设置
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=bool(objects),
            apply_scale_options='FBX_SCALE_ALL' if apply_scale else 'FBX_SCALE_NONE',
            use_mesh_modifiers=apply_modifiers,
            bake_anim=export_animations,
            bake_anim_use_all_actions=export_animations,
            bake_anim_use_nla_strips=export_animations,
            bake_anim_force_startend_keying=bake_animation,
            # Unity 特定设置
            axis_forward='-Z',
            axis_up='Y',
            global_scale=1.0,
            apply_unit_scale=True,
            # 几何设置
            mesh_smooth_type='FACE',
            use_mesh_edges=False,
            use_triangles=False,
            use_tspace=True,
            # 骨架设置
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=True
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "target": "Unity"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "UNITY_EXPORT_ERROR", "message": str(e)}
        }


def handle_unreal_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """Unreal导出"""
    filepath = params.get("filepath")
    objects = params.get("objects")
    export_animations = params.get("export_animations", True)
    smoothing = params.get("smoothing", "FACE")
    use_tspace = params.get("use_tspace", True)
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        _select_objects(objects)
        
        # Unreal FBX 导出设置
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=bool(objects),
            apply_scale_options='FBX_SCALE_ALL',
            use_mesh_modifiers=True,
            bake_anim=export_animations,
            bake_anim_use_all_actions=export_animations,
            # Unreal 特定设置
            axis_forward='X',
            axis_up='Z',
            global_scale=1.0,
            apply_unit_scale=True,
            # 几何设置
            mesh_smooth_type=smoothing,
            use_mesh_edges=False,
            use_triangles=False,
            use_tspace=use_tspace,
            # 骨架设置
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=True,
            # 其他
            batch_mode='OFF',
            use_metadata=True
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "target": "Unreal"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "UNREAL_EXPORT_ERROR", "message": str(e)}
        }


def handle_godot_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """Godot导出"""
    filepath = params.get("filepath")
    objects = params.get("objects")
    export_format = params.get("export_format", "GLTF")
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        _select_objects(objects)
        
        # 确保扩展名正确
        if export_format == "GLB":
            if not filepath.lower().endswith('.glb'):
                filepath = os.path.splitext(filepath)[0] + '.glb'
            export_format_enum = 'GLB'
        else:
            if not filepath.lower().endswith('.gltf'):
                filepath = os.path.splitext(filepath)[0] + '.gltf'
            export_format_enum = 'GLTF_SEPARATE'
        
        # Godot GLTF 导出设置
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=bool(objects),
            export_format=export_format_enum,
            # Godot 特定设置
            export_apply=True,
            export_animations=True,
            export_materials='EXPORT',
            export_colors=True,
            export_cameras=False,
            export_lights=False,
            # 变换设置
            export_yup=True
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "target": "Godot",
                "format": export_format
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "GODOT_EXPORT_ERROR", "message": str(e)}
        }


def handle_batch_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """批量导出"""
    output_dir = params.get("output_dir")
    format = params.get("format", "FBX")
    separate_files = params.get("separate_files", True)
    objects = params.get("objects")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取要导出的对象
        if objects:
            export_objects = [bpy.data.objects.get(name) for name in objects if bpy.data.objects.get(name)]
        else:
            export_objects = [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']
        
        exported_files = []
        
        if separate_files:
            # 每个对象单独导出
            for obj in export_objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                filename = f"{obj.name}.{format.lower()}"
                filepath = os.path.join(output_dir, filename)
                
                if format == "FBX":
                    bpy.ops.export_scene.fbx(
                        filepath=filepath,
                        use_selection=True,
                        use_mesh_modifiers=True
                    )
                elif format == "GLTF":
                    bpy.ops.export_scene.gltf(
                        filepath=filepath,
                        use_selection=True,
                        export_format='GLTF_SEPARATE'
                    )
                elif format == "OBJ":
                    bpy.ops.wm.obj_export(
                        filepath=filepath,
                        export_selected_objects=True
                    )
                
                exported_files.append(filepath)
        else:
            # 所有对象导出到一个文件
            _select_objects([obj.name for obj in export_objects])
            
            filename = f"export_all.{format.lower()}"
            filepath = os.path.join(output_dir, filename)
            
            if format == "FBX":
                bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
            elif format == "GLTF":
                bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True)
            elif format == "OBJ":
                bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
            
            exported_files.append(filepath)
        
        return {
            "success": True,
            "data": {
                "output_dir": output_dir,
                "exported_files": exported_files,
                "count": len(exported_files)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BATCH_EXPORT_ERROR", "message": str(e)}
        }


def handle_collection_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """集合导出"""
    collection_name = params.get("collection_name")
    filepath = params.get("filepath")
    format = params.get("format", "FBX")
    
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        return {
            "success": False,
            "error": {"code": "COLLECTION_NOT_FOUND", "message": f"集合不存在: {collection_name}"}
        }
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 选择集合中的所有对象
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.objects:
            obj.select_set(True)
        
        if format == "FBX":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                use_mesh_modifiers=True
            )
        elif format == "GLTF":
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                use_selection=True,
                export_format='GLTF_SEPARATE' if filepath.lower().endswith('.gltf') else 'GLB'
            )
        elif format == "OBJ":
            bpy.ops.wm.obj_export(
                filepath=filepath,
                export_selected_objects=True
            )
        
        return {
            "success": True,
            "data": {
                "collection": collection_name,
                "filepath": filepath,
                "format": format,
                "objects_count": len(collection.objects)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "COLLECTION_EXPORT_ERROR", "message": str(e)}
        }
