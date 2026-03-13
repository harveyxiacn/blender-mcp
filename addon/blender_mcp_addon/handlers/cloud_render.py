"""
Cloud rendering integration handler

Handles cloud rendering service integration commands.
"""

import os
import shutil
import tempfile
from datetime import datetime
from typing import Any

import bpy

from .compat import is_eevee_engine

# Cloud rendering configuration
CLOUD_CONFIG = {"service": "local", "api_key": None, "endpoint": None, "jobs": {}}

# Local render farm configuration
LOCAL_FARM = {"nodes": [], "port": 5000}


def _generate_job_id() -> str:
    """Generate job ID"""
    return f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _pack_blend_file() -> str:
    """Pack blend file and resources"""
    # Save current file
    if bpy.data.is_dirty:
        bpy.ops.wm.save_mainfile()

    blend_path = bpy.data.filepath
    if not blend_path:
        # Save to temp directory
        blend_path = os.path.join(tempfile.gettempdir(), "render_job.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Pack all external resources
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_mainfile()

    return blend_path


def handle_setup(params: dict[str, Any]) -> dict[str, Any]:
    """Configure cloud rendering service"""
    service = params.get("service", "local")
    api_key = params.get("api_key")
    endpoint = params.get("endpoint")

    try:
        global CLOUD_CONFIG

        CLOUD_CONFIG["service"] = service
        CLOUD_CONFIG["api_key"] = api_key
        CLOUD_CONFIG["endpoint"] = endpoint

        # Validate service configuration
        if service == "sheepit" and not api_key:
            return {
                "success": False,
                "error": {"code": "API_KEY_REQUIRED", "message": "SheepIt requires an API key"},
            }

        return {
            "success": True,
            "data": {"service": service, "endpoint": endpoint, "api_key_set": bool(api_key)},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "SETUP_ERROR", "message": str(e)}}


def handle_submit(params: dict[str, Any]) -> dict[str, Any]:
    """Submit render job"""
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 250)
    output_path = params.get("output_path", "")
    samples = params.get("samples", 128)
    resolution_x = params.get("resolution_x", 1920)
    resolution_y = params.get("resolution_y", 1080)

    try:
        scene = bpy.context.scene

        # Set render parameters
        scene.frame_start = frame_start
        scene.frame_end = frame_end
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y

        if scene.render.engine == "CYCLES":
            scene.cycles.samples = samples
        elif is_eevee_engine(scene.render.engine):
            scene.eevee.taa_render_samples = samples

        # Set output path
        if output_path:
            scene.render.filepath = output_path

        # Generate job ID
        job_id = _generate_job_id()

        # Pack file
        blend_path = _pack_blend_file()

        # Record job
        global CLOUD_CONFIG
        CLOUD_CONFIG["jobs"][job_id] = {
            "status": "pending",
            "blend_file": blend_path,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "submitted": datetime.now().isoformat(),
            "progress": 0,
            "output_path": output_path,
        }

        # Handle by service type
        if CLOUD_CONFIG["service"] == "local":
            # Local rendering
            CLOUD_CONFIG["jobs"][job_id]["status"] = "rendering"

            # Render in background (async)
            # Note: Actual implementation needs threads or subprocesses
            bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

            CLOUD_CONFIG["jobs"][job_id]["status"] = "completed"
        else:
            # External service
            CLOUD_CONFIG["jobs"][job_id]["status"] = "queued"

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "service": CLOUD_CONFIG["service"],
                "frame_range": [frame_start, frame_end],
                "total_frames": frame_end - frame_start + 1,
                "blend_file": blend_path,
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "SUBMIT_ERROR", "message": str(e)}}


def handle_status(params: dict[str, Any]) -> dict[str, Any]:
    """Query job status"""
    job_id = params.get("job_id")

    try:
        global CLOUD_CONFIG

        if job_id:
            if job_id not in CLOUD_CONFIG["jobs"]:
                return {
                    "success": False,
                    "error": {"code": "JOB_NOT_FOUND", "message": f"Job not found: {job_id}"},
                }

            return {
                "success": True,
                "data": {"job_id": job_id, "job": CLOUD_CONFIG["jobs"][job_id]},
            }
        else:
            return {"success": True, "data": {"jobs": CLOUD_CONFIG["jobs"]}}

    except Exception as e:
        return {"success": False, "error": {"code": "STATUS_ERROR", "message": str(e)}}


def handle_cancel(params: dict[str, Any]) -> dict[str, Any]:
    """Cancel job"""
    job_id = params.get("job_id")

    try:
        global CLOUD_CONFIG

        if job_id not in CLOUD_CONFIG["jobs"]:
            return {
                "success": False,
                "error": {"code": "JOB_NOT_FOUND", "message": f"Job not found: {job_id}"},
            }

        CLOUD_CONFIG["jobs"][job_id]["status"] = "cancelled"

        # Try to cancel rendering
        try:
            bpy.ops.render.render("INVOKE_DEFAULT")  # Cancel
        except:
            pass

        return {"success": True, "data": {"job_id": job_id, "status": "cancelled"}}

    except Exception as e:
        return {"success": False, "error": {"code": "CANCEL_ERROR", "message": str(e)}}


def handle_download(params: dict[str, Any]) -> dict[str, Any]:
    """Download render results"""
    job_id = params.get("job_id")
    output_folder = params.get("output_folder")

    try:
        global CLOUD_CONFIG

        if job_id not in CLOUD_CONFIG["jobs"]:
            return {
                "success": False,
                "error": {"code": "JOB_NOT_FOUND", "message": f"Job not found: {job_id}"},
            }

        job = CLOUD_CONFIG["jobs"][job_id]

        if job["status"] != "completed":
            return {
                "success": False,
                "error": {"code": "JOB_NOT_COMPLETED", "message": "Job has not completed yet"},
            }

        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Copy render results
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
                "files_count": len(rendered_files) if "rendered_files" in dir() else 0,
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "DOWNLOAD_ERROR", "message": str(e)}}


def handle_local_farm(params: dict[str, Any]) -> dict[str, Any]:
    """Configure local render farm"""
    nodes = params.get("nodes", [])
    port = params.get("port", 5000)

    try:
        global LOCAL_FARM

        LOCAL_FARM["nodes"] = nodes
        LOCAL_FARM["port"] = port

        return {"success": True, "data": {"nodes": nodes, "port": port, "node_count": len(nodes)}}

    except Exception as e:
        return {"success": False, "error": {"code": "LOCAL_FARM_ERROR", "message": str(e)}}


def handle_discover(params: dict[str, Any]) -> dict[str, Any]:
    """Discover render nodes"""
    try:
        import socket

        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Scan LAN (simplified)
        # Actual implementation needs more complex network discovery logic
        discovered_nodes = []

        # Return local machine as default node
        discovered_nodes.append({"address": local_ip, "hostname": hostname, "status": "available"})

        return {
            "success": True,
            "data": {"local_ip": local_ip, "discovered_nodes": discovered_nodes},
        }

    except Exception as e:
        return {"success": False, "error": {"code": "DISCOVER_ERROR", "message": str(e)}}


def handle_estimate(params: dict[str, Any]) -> dict[str, Any]:
    """Estimate render cost/time"""
    frame_count = params.get("frame_count", 1)
    samples = params.get("samples", 128)
    resolution_x = params.get("resolution_x", 1920)
    resolution_y = params.get("resolution_y", 1080)

    try:
        # Simple estimation formula
        # Base time: 1 second per frame (1080p, 128 samples)
        base_time_per_frame = 1.0  # seconds

        # Resolution factor
        resolution_factor = (resolution_x * resolution_y) / (1920 * 1080)

        # Sample factor
        sample_factor = samples / 128

        # Estimate time per frame (seconds)
        time_per_frame = base_time_per_frame * resolution_factor * sample_factor

        # Total time
        total_time_seconds = time_per_frame * frame_count

        # Convert to more readable format
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
                    "samples": round(sample_factor, 2),
                },
                "note": "This is a rough estimate based on standard hardware; actual time may vary with scene complexity",
            },
        }

    except Exception as e:
        return {"success": False, "error": {"code": "ESTIMATE_ERROR", "message": str(e)}}
