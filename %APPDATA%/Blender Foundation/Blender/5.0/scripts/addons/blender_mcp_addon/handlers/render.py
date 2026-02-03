"""
渲染处理器

处理渲染相关的命令。
"""

from typing import Any, Dict
import bpy
import os
import tempfile


def handle_settings(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置渲染参数"""
    scene = bpy.context.scene
    render = scene.render
    
    if "engine" in params:
        render.engine = params["engine"]
    
    if "resolution_x" in params:
        render.resolution_x = params["resolution_x"]
    
    if "resolution_y" in params:
        render.resolution_y = params["resolution_y"]
    
    if "resolution_percentage" in params:
        render.resolution_percentage = params["resolution_percentage"]
    
    if "samples" in params:
        if render.engine == 'CYCLES':
            scene.cycles.samples = params["samples"]
        elif render.engine in ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']:
            scene.eevee.taa_render_samples = params["samples"]
    
    if "use_denoising" in params:
        if render.engine == 'CYCLES':
            scene.cycles.use_denoising = params["use_denoising"]
    
    if "file_format" in params:
        render.image_settings.file_format = params["file_format"]
    
    if "output_path" in params:
        render.filepath = params["output_path"]
    
    return {
        "success": True,
        "data": {}
    }


def handle_image(params: Dict[str, Any]) -> Dict[str, Any]:
    """渲染图像"""
    output_path = params.get("output_path")
    frame = params.get("frame")
    camera = params.get("camera")
    write_still = params.get("write_still", True)
    
    scene = bpy.context.scene
    
    # 设置帧
    if frame is not None:
        scene.frame_set(frame)
    
    # 设置相机
    if camera:
        cam_obj = bpy.data.objects.get(camera)
        if cam_obj and cam_obj.type == 'CAMERA':
            scene.camera = cam_obj
    
    # 设置输出路径
    if output_path:
        scene.render.filepath = output_path
    elif not scene.render.filepath:
        scene.render.filepath = os.path.join(tempfile.gettempdir(), "render.png")
    
    # 渲染
    import time
    start_time = time.time()
    
    bpy.ops.render.render(write_still=write_still)
    
    render_time = time.time() - start_time
    
    return {
        "success": True,
        "data": {
            "output_path": scene.render.filepath,
            "render_time": round(render_time, 2),
            "resolution": [scene.render.resolution_x, scene.render.resolution_y]
        }
    }


def handle_animation(params: Dict[str, Any]) -> Dict[str, Any]:
    """渲染动画"""
    output_path = params.get("output_path")
    frame_start = params.get("frame_start")
    frame_end = params.get("frame_end")
    frame_step = params.get("frame_step", 1)
    
    scene = bpy.context.scene
    
    # 设置帧范围
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end
    
    scene.frame_step = frame_step
    
    # 设置输出路径
    if output_path:
        scene.render.filepath = output_path
    
    # 渲染动画
    bpy.ops.render.render(animation=True)
    
    frames_rendered = (scene.frame_end - scene.frame_start + 1) // frame_step
    
    return {
        "success": True,
        "data": {
            "output_path": scene.render.filepath,
            "frames_rendered": frames_rendered
        }
    }


def handle_preview(params: Dict[str, Any]) -> Dict[str, Any]:
    """渲染预览"""
    resolution_percentage = params.get("resolution_percentage", 50)
    samples = params.get("samples", 32)
    
    scene = bpy.context.scene
    render = scene.render
    
    # 保存原始设置
    orig_res_pct = render.resolution_percentage
    orig_samples = None
    
    if render.engine == 'CYCLES':
        orig_samples = scene.cycles.samples
        scene.cycles.samples = samples
    
    # 设置预览参数
    render.resolution_percentage = resolution_percentage
    
    # 渲染
    bpy.ops.render.render()
    
    # 恢复设置
    render.resolution_percentage = orig_res_pct
    if orig_samples is not None:
        scene.cycles.samples = orig_samples
    
    return {
        "success": True,
        "data": {}
    }


def handle_set_engine(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置渲染引擎"""
    engine = params.get("engine", "CYCLES")
    
    scene = bpy.context.scene
    
    # 有效的引擎列表
    valid_engines = ['CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH']
    
    if engine not in valid_engines:
        return {
            "success": False,
            "error": {
                "code": "INVALID_ENGINE",
                "message": f"无效的渲染引擎: {engine}. 有效值: {valid_engines}"
            }
        }
    
    scene.render.engine = engine
    
    return {
        "success": True,
        "data": {
            "engine": scene.render.engine
        }
    }


def handle_set_resolution(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置渲染分辨率"""
    width = params.get("width", 1920)
    height = params.get("height", 1080)
    percentage = params.get("percentage", 100)
    
    scene = bpy.context.scene
    render = scene.render
    
    render.resolution_x = width
    render.resolution_y = height
    render.resolution_percentage = percentage
    
    return {
        "success": True,
        "data": {
            "width": render.resolution_x,
            "height": render.resolution_y,
            "percentage": render.resolution_percentage
        }
    }


def handle_set_samples(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置渲染采样"""
    samples = params.get("samples", 128)
    
    scene = bpy.context.scene
    render = scene.render
    
    if render.engine == 'CYCLES':
        scene.cycles.samples = samples
        actual_samples = scene.cycles.samples
    elif render.engine in ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']:
        scene.eevee.taa_render_samples = samples
        actual_samples = scene.eevee.taa_render_samples
    else:
        actual_samples = samples
    
    return {
        "success": True,
        "data": {
            "samples": actual_samples,
            "engine": render.engine
        }
    }
