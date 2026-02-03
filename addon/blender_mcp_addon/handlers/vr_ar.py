"""
VR/AR 场景处理器

处理 VR/AR 场景配置和导出命令。
"""

from typing import Any, Dict
import bpy
import os
import math


def handle_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """配置 VR 场景"""
    xr_runtime = params.get("xr_runtime", "OPENXR")
    floor_height = params.get("floor_height", 0.0)
    
    try:
        scene = bpy.context.scene
        
        # 设置单位为米
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 1.0
        
        # 创建地板
        bpy.ops.mesh.primitive_plane_add(
            size=10,
            location=(0, 0, floor_height)
        )
        floor = bpy.context.active_object
        floor.name = "VR_Floor"
        
        # 创建 VR 原点标记
        bpy.ops.object.empty_add(
            type='ARROWS',
            location=(0, 0, floor_height)
        )
        origin = bpy.context.active_object
        origin.name = "VR_Origin"
        origin.empty_display_size = 0.5
        
        # 尝试启用 VR 插件
        try:
            bpy.ops.preferences.addon_enable(module="viewport_vr_preview")
        except:
            pass
        
        return {
            "success": True,
            "data": {
                "xr_runtime": xr_runtime,
                "floor_height": floor_height,
                "floor_object": floor.name,
                "origin_object": origin.name
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "VR_SETUP_ERROR", "message": str(e)}
        }


def handle_camera(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建 VR 相机"""
    camera_type = params.get("camera_type", "stereo")
    ipd = params.get("ipd", 0.064)  # 64mm 默认瞳距
    convergence_distance = params.get("convergence_distance", 1.95)
    location = params.get("location", [0, 0, 1.7])
    
    try:
        # 创建相机
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.active_object
        camera.name = "VR_Camera"
        
        cam_data = camera.data
        
        if camera_type == "panorama":
            # 全景相机设置
            cam_data.type = 'PANO'
            cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'
            cam_data.stereo.convergence_distance = convergence_distance
            cam_data.stereo.interocular_distance = ipd
        else:
            # 立体相机设置
            cam_data.type = 'PERSP'
            cam_data.stereo.convergence_mode = 'OFFAXIS'
            cam_data.stereo.convergence_distance = convergence_distance
            cam_data.stereo.interocular_distance = ipd
        
        # 设置为活动相机
        bpy.context.scene.camera = camera
        
        # 启用立体 3D
        bpy.context.scene.render.use_multiview = True
        bpy.context.scene.render.views_format = 'STEREO_3D'
        
        return {
            "success": True,
            "data": {
                "camera_name": camera.name,
                "camera_type": camera_type,
                "ipd": ipd,
                "convergence_distance": convergence_distance,
                "location": location
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "VR_CAMERA_ERROR", "message": str(e)}
        }


def handle_export(params: Dict[str, Any]) -> Dict[str, Any]:
    """导出为 VR 格式"""
    filepath = params.get("filepath")
    format = params.get("format", "GLB")
    include_animations = params.get("include_animations", True)
    compress = params.get("compress", True)
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 确保文件扩展名正确
        if format == "GLB":
            if not filepath.lower().endswith('.glb'):
                filepath = os.path.splitext(filepath)[0] + '.glb'
            export_format = 'GLB'
        else:
            if not filepath.lower().endswith('.gltf'):
                filepath = os.path.splitext(filepath)[0] + '.gltf'
            export_format = 'GLTF_SEPARATE'
        
        # 导出 glTF
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format=export_format,
            export_animations=include_animations,
            # VR 优化设置
            export_apply=True,
            export_materials='EXPORT',
            export_colors=True,
            export_cameras=True,
            export_lights=True,
            # KHR 扩展
            export_extras=True,
            export_yup=True
        )
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "format": format,
                "include_animations": include_animations
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "VR_EXPORT_ERROR", "message": str(e)}
        }


def handle_ar_marker(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建 AR 标记点"""
    marker_name = params.get("marker_name")
    marker_type = params.get("marker_type", "image")
    position = params.get("position", [0, 0, 0])
    size = params.get("size", 0.1)
    
    try:
        # 创建标记平面
        bpy.ops.mesh.primitive_plane_add(
            size=size,
            location=position
        )
        marker = bpy.context.active_object
        marker.name = f"AR_Marker_{marker_name}"
        
        # 添加自定义属性
        marker["ar_marker_type"] = marker_type
        marker["ar_marker_name"] = marker_name
        marker["ar_marker_size"] = size
        
        # 创建标记材质
        mat = bpy.data.materials.new(name=f"AR_Marker_Mat_{marker_name}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # 使用醒目的颜色
            if marker_type == "image":
                bsdf.inputs['Base Color'].default_value = (0, 1, 0, 1)  # 绿色
            elif marker_type == "qr":
                bsdf.inputs['Base Color'].default_value = (0, 0, 1, 1)  # 蓝色
            else:
                bsdf.inputs['Base Color'].default_value = (1, 1, 0, 1)  # 黄色
            
            bsdf.inputs['Alpha'].default_value = 0.5
            mat.blend_method = 'BLEND'
        
        marker.data.materials.append(mat)
        
        return {
            "success": True,
            "data": {
                "marker_name": marker.name,
                "marker_type": marker_type,
                "position": position,
                "size": size
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "AR_MARKER_ERROR", "message": str(e)}
        }


def handle_xr_interaction(params: Dict[str, Any]) -> Dict[str, Any]:
    """配置 XR 交互点"""
    object_name = params.get("object_name")
    interaction_type = params.get("interaction_type", "grab")
    highlight_color = params.get("highlight_color", [1, 1, 0, 1])
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        # 添加自定义属性
        obj["xr_interaction_type"] = interaction_type
        obj["xr_highlight_color"] = highlight_color
        obj["xr_interactable"] = True
        
        # 创建高亮材质
        mat_name = f"XR_Highlight_{object_name}"
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Emission Color'].default_value = highlight_color[:3] + (1.0,)
            bsdf.inputs['Emission Strength'].default_value = 0.5
        
        # 存储原始材质引用
        if obj.data and hasattr(obj.data, 'materials'):
            obj["xr_original_materials"] = [m.name if m else "" for m in obj.data.materials]
        
        return {
            "success": True,
            "data": {
                "object": object_name,
                "interaction_type": interaction_type,
                "highlight_material": mat_name
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "XR_INTERACTION_ERROR", "message": str(e)}
        }


def handle_preview_start(params: Dict[str, Any]) -> Dict[str, Any]:
    """启动 VR 预览"""
    try:
        # 尝试启动 VR 预览
        try:
            bpy.ops.wm.xr_session_toggle()
            return {
                "success": True,
                "data": {
                    "status": "VR preview started"
                }
            }
        except:
            return {
                "success": False,
                "error": {"code": "VR_NOT_AVAILABLE", "message": "VR 预览不可用，请确保已安装 VR 插件和 XR 运行时"}
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PREVIEW_START_ERROR", "message": str(e)}
        }


def handle_preview_stop(params: Dict[str, Any]) -> Dict[str, Any]:
    """停止 VR 预览"""
    try:
        try:
            # 如果 VR 会话正在运行，停止它
            if hasattr(bpy.context, 'window_manager') and hasattr(bpy.context.window_manager, 'xr_session_state'):
                if bpy.context.window_manager.xr_session_state:
                    bpy.ops.wm.xr_session_toggle()
            
            return {
                "success": True,
                "data": {
                    "status": "VR preview stopped"
                }
            }
        except:
            return {
                "success": True,
                "data": {
                    "status": "VR preview was not running"
                }
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PREVIEW_STOP_ERROR", "message": str(e)}
        }


def handle_panorama_render(params: Dict[str, Any]) -> Dict[str, Any]:
    """渲染 360 度全景图"""
    filepath = params.get("filepath")
    resolution = params.get("resolution", 4096)
    stereo = params.get("stereo", False)
    
    try:
        scene = bpy.context.scene
        
        # 保存原始设置
        original_engine = scene.render.engine
        original_res_x = scene.render.resolution_x
        original_res_y = scene.render.resolution_y
        original_filepath = scene.render.filepath
        
        # 设置全景渲染
        scene.render.engine = 'CYCLES'
        scene.render.resolution_x = resolution
        scene.render.resolution_y = resolution // 2  # 等距圆柱投影 2:1
        scene.render.filepath = filepath
        
        # 配置相机
        camera = scene.camera
        if camera:
            cam_data = camera.data
            original_type = cam_data.type
            
            cam_data.type = 'PANO'
            cam_data.cycles.panorama_type = 'EQUIRECTANGULAR'
            
            if stereo:
                scene.render.use_multiview = True
                scene.render.views_format = 'STEREO_3D'
                cam_data.stereo.interocular_distance = 0.064
        
        # 渲染
        bpy.ops.render.render(write_still=True)
        
        # 恢复设置
        scene.render.engine = original_engine
        scene.render.resolution_x = original_res_x
        scene.render.resolution_y = original_res_y
        scene.render.filepath = original_filepath
        
        if camera:
            cam_data.type = original_type
        
        return {
            "success": True,
            "data": {
                "filepath": filepath,
                "resolution": [resolution, resolution // 2],
                "stereo": stereo
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PANORAMA_RENDER_ERROR", "message": str(e)}
        }
