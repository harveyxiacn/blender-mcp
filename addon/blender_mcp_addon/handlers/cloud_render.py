"""
云渲染集成处理器

处理云渲染服务集成的命令。
"""

from typing import Any, Dict, List
import bpy
import os
import json
import tempfile
import shutil
from datetime import datetime


# 云渲染配置
CLOUD_CONFIG = {
    "service": "local",
    "api_key": None,
    "endpoint": None,
    "jobs": {}
}

# 本地渲染农场配置
LOCAL_FARM = {
    "nodes": [],
    "port": 5000
}


def _generate_job_id() -> str:
    """生成任务 ID"""
    return f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _pack_blend_file() -> str:
    """打包 blend 文件及资源"""
    # 保存当前文件
    if bpy.data.is_dirty:
        bpy.ops.wm.save_mainfile()
    
    blend_path = bpy.data.filepath
    if not blend_path:
        # 保存到临时目录
        blend_path = os.path.join(tempfile.gettempdir(), "render_job.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    # 打包所有外部资源
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_mainfile()
    
    return blend_path


def handle_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """配置云渲染服务"""
    service = params.get("service", "local")
    api_key = params.get("api_key")
    endpoint = params.get("endpoint")
    
    try:
        global CLOUD_CONFIG
        
        CLOUD_CONFIG["service"] = service
        CLOUD_CONFIG["api_key"] = api_key
        CLOUD_CONFIG["endpoint"] = endpoint
        
        # 验证服务配置
        if service == "sheepit":
            if not api_key:
                return {
                    "success": False,
                    "error": {"code": "API_KEY_REQUIRED", "message": "SheepIt 需要 API 密钥"}
                }
        
        return {
            "success": True,
            "data": {
                "service": service,
                "endpoint": endpoint,
                "api_key_set": bool(api_key)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SETUP_ERROR", "message": str(e)}
        }


def handle_submit(params: Dict[str, Any]) -> Dict[str, Any]:
    """提交渲染任务"""
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 250)
    output_path = params.get("output_path", "")
    samples = params.get("samples", 128)
    resolution_x = params.get("resolution_x", 1920)
    resolution_y = params.get("resolution_y", 1080)
    
    try:
        scene = bpy.context.scene
        
        # 设置渲染参数
        scene.frame_start = frame_start
        scene.frame_end = frame_end
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        
        if scene.render.engine == 'CYCLES':
            scene.cycles.samples = samples
        elif scene.render.engine == 'BLENDER_EEVEE_NEXT':
            scene.eevee.taa_render_samples = samples
        
        # 设置输出路径
        if output_path:
            scene.render.filepath = output_path
        
        # 生成任务 ID
        job_id = _generate_job_id()
        
        # 打包文件
        blend_path = _pack_blend_file()
        
        # 记录任务
        global CLOUD_CONFIG
        CLOUD_CONFIG["jobs"][job_id] = {
            "status": "pending",
            "blend_file": blend_path,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "submitted": datetime.now().isoformat(),
            "progress": 0,
            "output_path": output_path
        }
        
        # 根据服务类型处理
        if CLOUD_CONFIG["service"] == "local":
            # 本地渲染
            CLOUD_CONFIG["jobs"][job_id]["status"] = "rendering"
            
            # 在后台渲染（异步）
            # 注意：实际实现需要使用线程或子进程
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            
            CLOUD_CONFIG["jobs"][job_id]["status"] = "completed"
        else:
            # 外部服务
            CLOUD_CONFIG["jobs"][job_id]["status"] = "queued"
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "service": CLOUD_CONFIG["service"],
                "frame_range": [frame_start, frame_end],
                "total_frames": frame_end - frame_start + 1,
                "blend_file": blend_path
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SUBMIT_ERROR", "message": str(e)}
        }


def handle_status(params: Dict[str, Any]) -> Dict[str, Any]:
    """查询任务状态"""
    job_id = params.get("job_id")
    
    try:
        global CLOUD_CONFIG
        
        if job_id:
            if job_id not in CLOUD_CONFIG["jobs"]:
                return {
                    "success": False,
                    "error": {"code": "JOB_NOT_FOUND", "message": f"任务不存在: {job_id}"}
                }
            
            return {
                "success": True,
                "data": {
                    "job_id": job_id,
                    "job": CLOUD_CONFIG["jobs"][job_id]
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "jobs": CLOUD_CONFIG["jobs"]
                }
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "STATUS_ERROR", "message": str(e)}
        }


def handle_cancel(params: Dict[str, Any]) -> Dict[str, Any]:
    """取消任务"""
    job_id = params.get("job_id")
    
    try:
        global CLOUD_CONFIG
        
        if job_id not in CLOUD_CONFIG["jobs"]:
            return {
                "success": False,
                "error": {"code": "JOB_NOT_FOUND", "message": f"任务不存在: {job_id}"}
            }
        
        CLOUD_CONFIG["jobs"][job_id]["status"] = "cancelled"
        
        # 尝试取消渲染
        try:
            bpy.ops.render.render('INVOKE_DEFAULT')  # 取消
        except:
            pass
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "cancelled"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CANCEL_ERROR", "message": str(e)}
        }


def handle_download(params: Dict[str, Any]) -> Dict[str, Any]:
    """下载渲染结果"""
    job_id = params.get("job_id")
    output_folder = params.get("output_folder")
    
    try:
        global CLOUD_CONFIG
        
        if job_id not in CLOUD_CONFIG["jobs"]:
            return {
                "success": False,
                "error": {"code": "JOB_NOT_FOUND", "message": f"任务不存在: {job_id}"}
            }
        
        job = CLOUD_CONFIG["jobs"][job_id]
        
        if job["status"] != "completed":
            return {
                "success": False,
                "error": {"code": "JOB_NOT_COMPLETED", "message": "任务尚未完成"}
            }
        
        # 确保输出目录存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 复制渲染结果
        source_path = job.get("output_path", "")
        if source_path and os.path.exists(os.path.dirname(source_path)):
            import glob
            rendered_files = glob.glob(f"{source_path}*")
            
            for f in rendered_files:
                shutil.copy2(f, output_folder)
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "output_folder": output_folder,
                "files_count": len(rendered_files) if 'rendered_files' in dir() else 0
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DOWNLOAD_ERROR", "message": str(e)}
        }


def handle_local_farm(params: Dict[str, Any]) -> Dict[str, Any]:
    """配置本地渲染农场"""
    nodes = params.get("nodes", [])
    port = params.get("port", 5000)
    
    try:
        global LOCAL_FARM
        
        LOCAL_FARM["nodes"] = nodes
        LOCAL_FARM["port"] = port
        
        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "port": port,
                "node_count": len(nodes)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LOCAL_FARM_ERROR", "message": str(e)}
        }


def handle_discover(params: Dict[str, Any]) -> Dict[str, Any]:
    """发现渲染节点"""
    try:
        import socket
        
        # 获取本机 IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 扫描局域网（简化版）
        # 实际实现需要更复杂的网络发现逻辑
        discovered_nodes = []
        
        # 返回本机作为默认节点
        discovered_nodes.append({
            "address": local_ip,
            "hostname": hostname,
            "status": "available"
        })
        
        return {
            "success": True,
            "data": {
                "local_ip": local_ip,
                "discovered_nodes": discovered_nodes
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DISCOVER_ERROR", "message": str(e)}
        }


def handle_estimate(params: Dict[str, Any]) -> Dict[str, Any]:
    """估算渲染成本/时间"""
    frame_count = params.get("frame_count", 1)
    samples = params.get("samples", 128)
    resolution_x = params.get("resolution_x", 1920)
    resolution_y = params.get("resolution_y", 1080)
    
    try:
        # 简单的估算公式
        # 基础时间：每帧 1 秒（1080p, 128 samples）
        base_time_per_frame = 1.0  # 秒
        
        # 分辨率因子
        resolution_factor = (resolution_x * resolution_y) / (1920 * 1080)
        
        # 采样因子
        sample_factor = samples / 128
        
        # 估算每帧时间（秒）
        time_per_frame = base_time_per_frame * resolution_factor * sample_factor
        
        # 总时间
        total_time_seconds = time_per_frame * frame_count
        
        # 转换为更易读的格式
        hours = int(total_time_seconds // 3600)
        minutes = int((total_time_seconds % 3600) // 60)
        seconds = int(total_time_seconds % 60)
        
        return {
            "success": True,
            "data": {
                "frame_count": frame_count,
                "estimated_time_per_frame": round(time_per_frame, 2),
                "estimated_total_seconds": round(total_time_seconds, 2),
                "estimated_total_formatted": f"{hours}h {minutes}m {seconds}s",
                "factors": {
                    "resolution": round(resolution_factor, 2),
                    "samples": round(sample_factor, 2)
                },
                "note": "这是基于标准硬件的粗略估算，实际时间可能因场景复杂度而异"
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "ESTIMATE_ERROR", "message": str(e)}
        }
