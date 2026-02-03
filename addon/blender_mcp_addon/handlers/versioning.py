"""
版本控制处理器

处理Blender场景版本管理命令。
"""

from typing import Any, Dict, List
import bpy
import os
import json
import shutil
from datetime import datetime


# 版本存储目录名
VERSION_DIR = ".blender_versions"
MANIFEST_FILE = "manifest.json"


def _get_version_dir() -> str:
    """获取版本控制目录"""
    blend_path = bpy.data.filepath
    if not blend_path:
        # 使用临时目录
        import tempfile
        return os.path.join(tempfile.gettempdir(), "blender_versions")
    
    project_dir = os.path.dirname(blend_path)
    return os.path.join(project_dir, VERSION_DIR)


def _get_manifest_path() -> str:
    """获取清单文件路径"""
    return os.path.join(_get_version_dir(), MANIFEST_FILE)


def _load_manifest() -> Dict:
    """加载版本清单"""
    manifest_path = _get_manifest_path()
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "project_name": os.path.basename(os.path.dirname(_get_version_dir())),
        "created": datetime.now().isoformat(),
        "current_branch": "main",
        "branches": {
            "main": {
                "versions": [],
                "head": None
            }
        }
    }


def _save_manifest(manifest: Dict):
    """保存版本清单"""
    manifest_path = _get_manifest_path()
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def _generate_version_id() -> str:
    """生成版本ID"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def handle_init(params: Dict[str, Any]) -> Dict[str, Any]:
    """初始化版本控制"""
    project_path = params.get("project_path")
    
    try:
        # 如果指定了项目路径，先保存文件
        if project_path:
            if not bpy.data.filepath:
                blend_path = os.path.join(project_path, "scene.blend")
                bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        
        version_dir = _get_version_dir()
        os.makedirs(version_dir, exist_ok=True)
        
        manifest = _load_manifest()
        _save_manifest(manifest)
        
        return {
            "success": True,
            "data": {
                "version_dir": version_dir,
                "project_name": manifest["project_name"],
                "current_branch": manifest["current_branch"]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "INIT_ERROR", "message": str(e)}
        }


def handle_save(params: Dict[str, Any]) -> Dict[str, Any]:
    """保存版本"""
    name = params.get("name")
    description = params.get("description", "")
    create_thumbnail = params.get("create_thumbnail", True)
    
    try:
        # 确保当前文件已保存
        if bpy.data.is_dirty:
            bpy.ops.wm.save_mainfile()
        
        version_dir = _get_version_dir()
        manifest = _load_manifest()
        
        # 生成版本ID
        version_id = _generate_version_id()
        if not name:
            name = f"v{len(manifest['branches'][manifest['current_branch']]['versions']) + 1:03d}"
        
        # 创建版本目录
        version_path = os.path.join(version_dir, manifest["current_branch"], version_id)
        os.makedirs(version_path, exist_ok=True)
        
        # 复制当前文件
        blend_path = bpy.data.filepath
        if blend_path:
            dest_blend = os.path.join(version_path, "scene.blend")
            shutil.copy2(blend_path, dest_blend)
        
        # 创建缩略图
        thumbnail_path = None
        if create_thumbnail:
            try:
                thumbnail_path = os.path.join(version_path, "thumbnail.png")
                # 使用 OpenGL 渲染预览
                bpy.context.scene.render.filepath = thumbnail_path
                bpy.context.scene.render.resolution_x = 256
                bpy.context.scene.render.resolution_y = 256
                bpy.ops.render.opengl(write_still=True)
            except:
                thumbnail_path = None
        
        # 更新清单
        version_info = {
            "id": version_id,
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "blend_file": "scene.blend",
            "thumbnail": "thumbnail.png" if thumbnail_path else None,
            "objects_count": len(bpy.data.objects),
            "materials_count": len(bpy.data.materials)
        }
        
        branch = manifest["current_branch"]
        manifest["branches"][branch]["versions"].append(version_info)
        manifest["branches"][branch]["head"] = version_id
        _save_manifest(manifest)
        
        return {
            "success": True,
            "data": {
                "version_id": version_id,
                "name": name,
                "branch": branch,
                "path": version_path
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SAVE_ERROR", "message": str(e)}
        }


def handle_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出版本"""
    branch = params.get("branch", "main")
    limit = params.get("limit", 20)
    
    try:
        manifest = _load_manifest()
        
        if branch not in manifest["branches"]:
            return {
                "success": False,
                "error": {"code": "BRANCH_NOT_FOUND", "message": f"分支不存在: {branch}"}
            }
        
        versions = manifest["branches"][branch]["versions"]
        versions = versions[-limit:]  # 返回最近的版本
        versions.reverse()  # 最新的在前
        
        return {
            "success": True,
            "data": {
                "branch": branch,
                "head": manifest["branches"][branch]["head"],
                "versions": versions,
                "total": len(manifest["branches"][branch]["versions"])
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "LIST_ERROR", "message": str(e)}
        }


def handle_restore(params: Dict[str, Any]) -> Dict[str, Any]:
    """恢复版本"""
    version_id = params.get("version_id")
    create_backup = params.get("create_backup", True)
    
    try:
        manifest = _load_manifest()
        version_dir = _get_version_dir()
        branch = manifest["current_branch"]
        
        # 查找版本
        version_info = None
        for v in manifest["branches"][branch]["versions"]:
            if v["id"] == version_id:
                version_info = v
                break
        
        if not version_info:
            return {
                "success": False,
                "error": {"code": "VERSION_NOT_FOUND", "message": f"版本不存在: {version_id}"}
            }
        
        # 创建备份
        backup_id = None
        if create_backup and bpy.data.filepath:
            backup_result = handle_save({
                "name": f"backup_before_{version_id}",
                "description": f"恢复到 {version_id} 前的自动备份",
                "create_thumbnail": False
            })
            if backup_result["success"]:
                backup_id = backup_result["data"]["version_id"]
        
        # 恢复文件
        version_path = os.path.join(version_dir, branch, version_id)
        blend_file = os.path.join(version_path, version_info["blend_file"])
        
        if os.path.exists(blend_file):
            bpy.ops.wm.open_mainfile(filepath=blend_file)
        
        return {
            "success": True,
            "data": {
                "restored_version": version_id,
                "backup_version": backup_id,
                "version_info": version_info
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "RESTORE_ERROR", "message": str(e)}
        }


def handle_compare(params: Dict[str, Any]) -> Dict[str, Any]:
    """比较版本"""
    version_id_1 = params.get("version_id_1")
    version_id_2 = params.get("version_id_2")
    
    try:
        manifest = _load_manifest()
        version_dir = _get_version_dir()
        branch = manifest["current_branch"]
        
        # 查找两个版本
        v1_info = None
        v2_info = None
        for v in manifest["branches"][branch]["versions"]:
            if v["id"] == version_id_1:
                v1_info = v
            if v["id"] == version_id_2:
                v2_info = v
        
        if not v1_info or not v2_info:
            return {
                "success": False,
                "error": {"code": "VERSION_NOT_FOUND", "message": "版本不存在"}
            }
        
        # 简单的元数据比较
        diff = {
            "version_1": {
                "id": v1_info["id"],
                "name": v1_info["name"],
                "timestamp": v1_info["timestamp"],
                "objects_count": v1_info.get("objects_count", 0),
                "materials_count": v1_info.get("materials_count", 0)
            },
            "version_2": {
                "id": v2_info["id"],
                "name": v2_info["name"],
                "timestamp": v2_info["timestamp"],
                "objects_count": v2_info.get("objects_count", 0),
                "materials_count": v2_info.get("materials_count", 0)
            },
            "changes": {
                "objects_diff": v2_info.get("objects_count", 0) - v1_info.get("objects_count", 0),
                "materials_diff": v2_info.get("materials_count", 0) - v1_info.get("materials_count", 0)
            }
        }
        
        return {
            "success": True,
            "data": diff
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "COMPARE_ERROR", "message": str(e)}
        }


def handle_branch(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建分支"""
    branch_name = params.get("branch_name")
    from_version = params.get("from_version")
    
    try:
        manifest = _load_manifest()
        
        if branch_name in manifest["branches"]:
            return {
                "success": False,
                "error": {"code": "BRANCH_EXISTS", "message": f"分支已存在: {branch_name}"}
            }
        
        # 创建新分支
        current_branch = manifest["current_branch"]
        if from_version:
            # 从指定版本创建
            source_versions = []
            for v in manifest["branches"][current_branch]["versions"]:
                source_versions.append(v)
                if v["id"] == from_version:
                    break
        else:
            # 从当前版本创建
            source_versions = manifest["branches"][current_branch]["versions"].copy()
        
        manifest["branches"][branch_name] = {
            "versions": source_versions,
            "head": source_versions[-1]["id"] if source_versions else None,
            "parent_branch": current_branch,
            "created": datetime.now().isoformat()
        }
        
        _save_manifest(manifest)
        
        # 创建分支目录
        version_dir = _get_version_dir()
        branch_path = os.path.join(version_dir, branch_name)
        os.makedirs(branch_path, exist_ok=True)
        
        # 复制版本文件
        if source_versions:
            for v in source_versions:
                src = os.path.join(version_dir, current_branch, v["id"])
                dst = os.path.join(branch_path, v["id"])
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copytree(src, dst)
        
        return {
            "success": True,
            "data": {
                "branch_name": branch_name,
                "from_version": from_version,
                "versions_count": len(source_versions)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BRANCH_ERROR", "message": str(e)}
        }


def handle_branches(params: Dict[str, Any]) -> Dict[str, Any]:
    """列出分支"""
    try:
        manifest = _load_manifest()
        
        branches = []
        for name, data in manifest["branches"].items():
            branches.append({
                "name": name,
                "head": data.get("head"),
                "versions_count": len(data["versions"]),
                "is_current": name == manifest["current_branch"],
                "created": data.get("created")
            })
        
        return {
            "success": True,
            "data": {
                "current_branch": manifest["current_branch"],
                "branches": branches
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BRANCHES_ERROR", "message": str(e)}
        }


def handle_switch_branch(params: Dict[str, Any]) -> Dict[str, Any]:
    """切换分支"""
    branch_name = params.get("branch_name")
    
    try:
        manifest = _load_manifest()
        
        if branch_name not in manifest["branches"]:
            return {
                "success": False,
                "error": {"code": "BRANCH_NOT_FOUND", "message": f"分支不存在: {branch_name}"}
            }
        
        manifest["current_branch"] = branch_name
        _save_manifest(manifest)
        
        # 恢复到分支的 head 版本
        head = manifest["branches"][branch_name]["head"]
        if head:
            handle_restore({"version_id": head, "create_backup": False})
        
        return {
            "success": True,
            "data": {
                "branch": branch_name,
                "head": head
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SWITCH_ERROR", "message": str(e)}
        }


def handle_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """删除版本"""
    version_id = params.get("version_id")
    force = params.get("force", False)
    
    try:
        manifest = _load_manifest()
        version_dir = _get_version_dir()
        branch = manifest["current_branch"]
        
        # 查找版本
        version_index = None
        for i, v in enumerate(manifest["branches"][branch]["versions"]):
            if v["id"] == version_id:
                version_index = i
                break
        
        if version_index is None:
            return {
                "success": False,
                "error": {"code": "VERSION_NOT_FOUND", "message": f"版本不存在: {version_id}"}
            }
        
        # 检查是否是 head
        if manifest["branches"][branch]["head"] == version_id and not force:
            return {
                "success": False,
                "error": {"code": "CANNOT_DELETE_HEAD", "message": "不能删除当前 head 版本，使用 force=True 强制删除"}
            }
        
        # 删除文件
        version_path = os.path.join(version_dir, branch, version_id)
        if os.path.exists(version_path):
            shutil.rmtree(version_path)
        
        # 更新清单
        del manifest["branches"][branch]["versions"][version_index]
        
        # 更新 head
        if manifest["branches"][branch]["head"] == version_id:
            if manifest["branches"][branch]["versions"]:
                manifest["branches"][branch]["head"] = manifest["branches"][branch]["versions"][-1]["id"]
            else:
                manifest["branches"][branch]["head"] = None
        
        _save_manifest(manifest)
        
        return {
            "success": True,
            "data": {
                "deleted_version": version_id
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "DELETE_ERROR", "message": str(e)}
        }


def handle_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取版本信息"""
    version_id = params.get("version_id")
    
    try:
        manifest = _load_manifest()
        branch = manifest["current_branch"]
        
        for v in manifest["branches"][branch]["versions"]:
            if v["id"] == version_id:
                return {
                    "success": True,
                    "data": {
                        "branch": branch,
                        "version": v
                    }
                }
        
        return {
            "success": False,
            "error": {"code": "VERSION_NOT_FOUND", "message": f"版本不存在: {version_id}"}
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "INFO_ERROR", "message": str(e)}
        }
