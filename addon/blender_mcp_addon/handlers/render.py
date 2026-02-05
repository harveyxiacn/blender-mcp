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


def handle_get_viewport_screenshot(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取视口截图
    
    使用 offscreen 渲染或直接渲染视口。
    针对 Blender 5.0+ 优化的实现。
    
    Args:
        params:
            - output_path: 输出路径（可选，不提供则使用临时目录）
            - width: 截图宽度（默认800）
            - height: 截图高度（默认600）
            - view_type: 视图类型 ('PERSP', 'FRONT', 'BACK', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM')
    
    Returns:
        截图文件路径和信息
    """
    import base64
    
    output_path = params.get("output_path")
    width = params.get("width", 800)
    height = params.get("height", 600)
    view_type = params.get("view_type")
    return_base64 = params.get("return_base64", False)
    
    # 确定输出路径
    if not output_path:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(tempfile.gettempdir(), f"blender_viewport_{timestamp}.png")
    
    scene = bpy.context.scene
    
    # 保存原始设置
    orig_res_x = scene.render.resolution_x
    orig_res_y = scene.render.resolution_y
    orig_res_pct = scene.render.resolution_percentage
    orig_filepath = scene.render.filepath
    orig_file_format = scene.render.image_settings.file_format
    
    try:
        # 设置渲染分辨率
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = output_path
        
        # 方法1: 尝试使用 screen.areas 直接获取 3D 视口
        area = None
        region = None
        
        # 优先使用当前屏幕的 areas
        if hasattr(bpy.context, 'screen') and bpy.context.screen:
            for a in bpy.context.screen.areas:
                if a.type == 'VIEW_3D':
                    area = a
                    for r in a.regions:
                        if r.type == 'WINDOW':
                            region = r
                            break
                    break
        
        # 如果没找到，遍历所有窗口
        if not area:
            for window in bpy.context.window_manager.windows:
                for a in window.screen.areas:
                    if a.type == 'VIEW_3D':
                        area = a
                        for r in a.regions:
                            if r.type == 'WINDOW':
                                region = r
                                break
                        break
                if area:
                    break
        
        if not area or not region:
            return {
                "success": False,
                "error": {
                    "code": "NO_3D_VIEW",
                    "message": "找不到3D视口"
                }
            }
        
        # 如果指定了视图类型，切换视图
        if view_type:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    region_3d = space.region_3d
                    
                    view_types_map = {
                        'PERSP': 'PERSP',
                        'FRONT': 'ORTHO',
                        'BACK': 'ORTHO',
                        'LEFT': 'ORTHO',
                        'RIGHT': 'ORTHO',
                        'TOP': 'ORTHO',
                        'BOTTOM': 'ORTHO',
                    }
                    
                    if view_type.upper() in view_types_map:
                        region_3d.view_perspective = view_types_map[view_type.upper()]
                    break
        
        # 尝试多种方法执行截图
        success = False
        error_msg = ""
        
        # 方法1: 使用 temp_override (Blender 3.2+)
        try:
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.render.opengl(write_still=True)
            success = True
        except Exception as e1:
            error_msg = f"temp_override 方法失败: {str(e1)}"
            
            # 方法2: 使用标准渲染代替视口渲染
            try:
                # 使用 Workbench 引擎快速渲染
                orig_engine = scene.render.engine
                scene.render.engine = 'BLENDER_WORKBENCH'
                bpy.ops.render.render(write_still=True)
                scene.render.engine = orig_engine
                success = True
            except Exception as e2:
                error_msg += f"; 标准渲染方法失败: {str(e2)}"
                
                # 方法3: 保存渲染结果图像
                try:
                    if 'Render Result' in bpy.data.images:
                        bpy.data.images['Render Result'].save_render(output_path)
                        success = True
                except Exception as e3:
                    error_msg += f"; 保存渲染结果失败: {str(e3)}"
        
        # 检查文件是否创建
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            
            screenshot_base64 = None
            if return_base64:
                with open(output_path, "rb") as f:
                    screenshot_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                "success": True,
                "data": {
                    "output_path": output_path,
                    "width": width,
                    "height": height,
                    "file_size": file_size,
                    "base64": screenshot_base64
                }
            }
        else:
            return {
                "success": False,
                "error": {
                    "code": "SCREENSHOT_FAILED",
                    "message": f"截图失败: {error_msg}" if error_msg else "截图文件未创建"
                }
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SCREENSHOT_ERROR",
                "message": str(e)
            }
        }
    
    finally:
        # 恢复原始设置
        scene.render.resolution_x = orig_res_x
        scene.render.resolution_y = orig_res_y
        scene.render.resolution_percentage = orig_res_pct
        scene.render.filepath = orig_filepath
        scene.render.image_settings.file_format = orig_file_format
