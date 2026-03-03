"""
命令执行器

解析并执行 MCP 命令，调用相应的 Blender 操作。
使用懒加载避免启动时循环导入。
"""

from typing import Any, Dict
import traceback

import bpy

from .handlers import get_handler


class CommandExecutor:
    """命令执行器 - 使用懒加载按需导入处理器模块"""
    
    def __init__(self):
        """初始化执行器"""
        pass
    
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
            # 系统命令由自己处理
            if category == "system":
                method_name = f"handle_{action}"
                method = getattr(self, method_name, None)
                if method is None:
                    return {
                        "success": False,
                        "error": {
                            "code": "UNKNOWN_ACTION",
                            "message": f"未知的操作: system.{action}"
                        }
                    }
                return method(params)
            
            # 懒加载获取处理器
            handler = get_handler(category)
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
    
    def handle_execute_python(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """在 Blender 中执行 Python 代码（含安全检查）"""
        code = params.get("code", "")
        if not code:
            return {"success": False, "error": {"code": "MISSING_CODE", "message": "缺少code参数"}}
        
        from .handlers.utility import _check_code_safety
        warning = _check_code_safety(code)
        if warning:
            return {
                "success": False,
                "error": {"code": "SAFETY_CHECK_FAILED", "message": warning}
            }
        
        try:
            local_vars = {"bpy": bpy, "result": None}
            exec(code, {"__builtins__": __builtins__, "bpy": bpy}, local_vars)
            return {
                "success": True,
                "data": {"result": str(local_vars.get("result", "OK"))}
            }
        except Exception as e:
            traceback.print_exc()
            return {
                "success": False,
                "error": {"code": "PYTHON_ERROR", "message": str(e)}
            }
