"""
命令执行器

解析并执行 MCP 命令，调用相应的 Blender 操作。
"""

from typing import Any, Dict, Callable
import traceback

import bpy

from .handlers import (
    scene_handler,
    object_handler,
    modeling_handler,
    material_handler,
    lighting_handler,
    camera_handler,
    animation_handler,
    character_handler,
    rigging_handler,
    render_handler,
    utility_handler,
    export_handler,
    character_template_handler,
    auto_rig_handler,
    animation_preset_handler,
    physics_handler,
    scene_advanced_handler,
    batch_handler,
    curves_handler,
    uv_handler,
    nodes_handler,
    compositor_handler,
    vse_handler,
    sculpt_handler,
    texture_paint_handler,
    gpencil_handler,
    simulation_handler,
    hair_handler,
    assets_handler,
    addons_handler,
    world_handler,
    constraints_handler,
    mocap_handler,
    preferences_handler,
    external_handler,
    ai_assist_handler,
    versioning_handler,
    ai_generation_handler,
    vr_ar_handler,
    substance_handler,
    zbrush_handler,
    cloud_render_handler,
    collaboration_handler,
)


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self):
        """初始化执行器"""
        # 注册处理器
        self.handlers: Dict[str, Any] = {
            "scene": scene_handler,
            "object": object_handler,
            "modeling": modeling_handler,
            "material": material_handler,
            "lighting": lighting_handler,
            "camera": camera_handler,
            "animation": animation_handler,
            "character": character_handler,
            "rigging": rigging_handler,
            "render": render_handler,
            "utility": utility_handler,
            "export": export_handler,
            "character_template": character_template_handler,
            "auto_rig": auto_rig_handler,
            "animation_preset": animation_preset_handler,
            "physics": physics_handler,
            "scene_advanced": scene_advanced_handler,
            "batch": batch_handler,
            "curves": curves_handler,
            "uv": uv_handler,
            "nodes": nodes_handler,
            "compositor": compositor_handler,
            "vse": vse_handler,
            "sculpt": sculpt_handler,
            "texture_paint": texture_paint_handler,
            "gpencil": gpencil_handler,
            "simulation": simulation_handler,
            "hair": hair_handler,
            "assets": assets_handler,
            "addons": addons_handler,
            "world": world_handler,
            "constraints": constraints_handler,
            "mocap": mocap_handler,
            "preferences": preferences_handler,
            "external": external_handler,
            "ai_assist": ai_assist_handler,
            "versioning": versioning_handler,
            "ai_generation": ai_generation_handler,
            "vr_ar": vr_ar_handler,
            "substance": substance_handler,
            "zbrush": zbrush_handler,
            "cloud_render": cloud_render_handler,
            "collaboration": collaboration_handler,
            "system": self,  # 系统命令由自己处理
        }
    
    def execute(
        self,
        category: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行命令
        
        Args:
            category: 命令类别
            action: 具体操作
            params: 操作参数
            
        Returns:
            执行结果
        """
        try:
            # 获取处理器
            handler = self.handlers.get(category)
            if handler is None:
                return {
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_CATEGORY",
                        "message": f"未知的命令类别: {category}"
                    }
                }
            
            # 获取操作方法
            method_name = f"handle_{action}"
            method = getattr(handler, method_name, None)
            
            if method is None:
                return {
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_ACTION",
                        "message": f"未知的操作: {category}.{action}"
                    }
                }
            
            # 执行操作
            result = method(params)
            
            return result
            
        except Exception as e:
            traceback.print_exc()
            return {
                "success": False,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e)
                }
            }
    
    # 系统命令处理
    def handle_get_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取 Blender 信息"""
        return {
            "success": True,
            "data": {
                "version": bpy.app.version,
                "version_string": bpy.app.version_string,
                "filepath": bpy.data.filepath or "",
                "scene": bpy.context.scene.name if bpy.context.scene else "",
                "objects_count": len(bpy.data.objects)
            }
        }
