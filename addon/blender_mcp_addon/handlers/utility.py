"""
实用工具处理器

处理实用工具相关的命令。
"""

from typing import Any, Dict
import bpy
import os
import tempfile


def handle_execute_python(params: Dict[str, Any]) -> Dict[str, Any]:
    """执行 Python 代码"""
    code = params.get("code", "")
    timeout = params.get("timeout", 30)
    
    # 注意：这是一个危险操作，实际使用时应该添加安全检查
    
    try:
        # 创建执行环境
        exec_globals = {"bpy": bpy, "__builtins__": __builtins__}
        exec_locals = {}
        
        # 捕获输出
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            exec(code, exec_globals, exec_locals)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return {
            "success": True,
            "data": {
                "output": output
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "EXECUTION_ERROR",
                "message": str(e)
            }
        }


def handle_viewport_screenshot(params: Dict[str, Any]) -> Dict[str, Any]:
    """视口截图"""
    output_path = params.get("output_path")
    width = params.get("width", 800)
    height = params.get("height", 600)
    
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), "viewport_screenshot.png")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 获取 3D 视口
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            # 设置渲染尺寸
            for region in area.regions:
                if region.type == 'WINDOW':
                    # 使用 OpenGL 渲染视口
                    override = bpy.context.copy()
                    override['area'] = area
                    override['region'] = region
                    
                    # 渲染视口
                    bpy.ops.render.opengl(
                        override,
                        write_still=True
                    )
                    
                    # 保存图像
                    bpy.data.images['Render Result'].save_render(output_path)
                    
                    return {
                        "success": True,
                        "data": {
                            "output_path": output_path
                        }
                    }
    
    return {
        "success": False,
        "error": {
            "code": "NO_3D_VIEWPORT",
            "message": "找不到 3D 视口"
        }
    }


def handle_file_save(params: Dict[str, Any]) -> Dict[str, Any]:
    """保存文件"""
    filepath = params.get("filepath")
    compress = params.get("compress", True)
    
    if filepath:
        bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
    else:
        if bpy.data.filepath:
            bpy.ops.wm.save_mainfile(compress=compress)
        else:
            return {
                "success": False,
                "error": {
                    "code": "NO_FILEPATH",
                    "message": "请指定文件路径"
                }
            }
    
    return {
        "success": True,
        "data": {
            "filepath": bpy.data.filepath
        }
    }


def handle_file_open(params: Dict[str, Any]) -> Dict[str, Any]:
    """打开文件"""
    filepath = params.get("filepath")
    load_ui = params.get("load_ui", False)
    
    if not filepath:
        return {
            "success": False,
            "error": {
                "code": "NO_FILEPATH",
                "message": "请指定文件路径"
            }
        }
    
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error": {
                "code": "FILE_NOT_FOUND",
                "message": f"文件不存在: {filepath}"
            }
        }
    
    bpy.ops.wm.open_mainfile(filepath=filepath, load_ui=load_ui)
    
    return {
        "success": True,
        "data": {
            "filepath": bpy.data.filepath
        }
    }


def handle_get_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取 Blender 信息"""
    return {
        "success": True,
        "data": {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "filepath": bpy.data.filepath or "",
            "scene": bpy.context.scene.name if bpy.context.scene else "",
            "objects_count": len(bpy.data.objects)
        }
    }


def handle_undo(params: Dict[str, Any]) -> Dict[str, Any]:
    """撤销"""
    steps = params.get("steps", 1)
    
    for _ in range(steps):
        bpy.ops.ed.undo()
    
    return {
        "success": True,
        "data": {}
    }


def handle_redo(params: Dict[str, Any]) -> Dict[str, Any]:
    """重做"""
    steps = params.get("steps", 1)
    
    for _ in range(steps):
        bpy.ops.ed.redo()
    
    return {
        "success": True,
        "data": {}
    }


def handle_get_blender_version(params: Dict[str, Any]) -> Dict[str, Any]:
    """获取 Blender 版本"""
    return {
        "success": True,
        "data": {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "build_date": bpy.app.build_date.decode() if hasattr(bpy.app, 'build_date') else "",
            "build_platform": bpy.app.build_platform.decode() if hasattr(bpy.app, 'build_platform') else ""
        }
    }
