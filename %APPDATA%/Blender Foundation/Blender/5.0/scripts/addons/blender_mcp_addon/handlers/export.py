"""
导出处理器

处理各种格式的导出命令。
"""

from typing import Any, Dict
import bpy
import os


def handle_fbx(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出 FBX"""
    filepath = params.get("filepath")
    
    if not filepath:
        return {
            "success": False,
            "error": {
                "code": "MISSING_FILEPATH",
                "message": "需要指定导出路径"
            }
        }
    
    # 确保目录存在
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # 确保扩展名正确
    if not filepath.lower().endswith('.fbx'):
        filepath += '.fbx'
    
    try:
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=params.get("selected_only", False),
            apply_scale_options=params.get("apply_scale", "FBX_SCALE_ALL"),
            use_mesh_modifiers=params.get("use_mesh_modifiers", True),
            use_armature_deform_only=params.get("use_armature_deform_only", False),
            add_leaf_bones=params.get("add_leaf_bones", False),
            primary_bone_axis=params.get("primary_bone_axis", "Y"),
            secondary_bone_axis=params.get("secondary_bone_axis", "X"),
            bake_anim=params.get("include_animation", True),
            bake_anim_use_all_actions=params.get("bake_animation", False),
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "EXPORT_ERROR",
                "message": str(e)
            }
        }


def handle_gltf(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出 glTF"""
    filepath = params.get("filepath")
    
    if not filepath:
        return {
            "success": False,
            "error": {
                "code": "MISSING_FILEPATH",
                "message": "需要指定导出路径"
            }
        }
    
    # 确保目录存在
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    export_format = params.get("export_format", "GLB")
    
    # 确保扩展名正确
    if export_format == "GLB" and not filepath.lower().endswith('.glb'):
        filepath += '.glb'
    elif export_format == "GLTF_SEPARATE" and not filepath.lower().endswith('.gltf'):
        filepath += '.gltf'
    
    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=params.get("selected_only", False),
            export_format=export_format,
            export_animations=params.get("include_animation", True),
            export_image_format='AUTO' if params.get("export_textures", True) else 'NONE',
            export_draco_mesh_compression_enable=params.get("export_draco", False),
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "EXPORT_ERROR",
                "message": str(e)
            }
        }


def handle_obj(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出 OBJ"""
    filepath = params.get("filepath")
    
    if not filepath:
        return {
            "success": False,
            "error": {
                "code": "MISSING_FILEPATH",
                "message": "需要指定导出路径"
            }
        }
    
    # 确保目录存在
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # 确保扩展名正确
    if not filepath.lower().endswith('.obj'):
        filepath += '.obj'
    
    try:
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=params.get("selected_only", False),
            apply_modifiers=params.get("apply_modifiers", True),
            export_materials=params.get("export_materials", True),
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "EXPORT_ERROR",
                "message": str(e)
            }
        }
