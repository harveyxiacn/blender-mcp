"""
Command Executor

Parses and executes MCP commands, invoking the corresponding Blender operations.
Uses lazy loading to avoid circular imports at startup.
"""

import importlib
import traceback
from typing import Any

import bpy

from . import handlers as _handlers_pkg
from .handlers import get_handler
from .handlers.error_suggestions import enrich_error


class CommandExecutor:
    """Command executor - uses lazy loading to import handler modules on demand"""

    def __init__(self) -> None:
        """Initialize the executor, ensuring handler registry is up-to-date."""
        # Force reimport of handler registry to pick up new modules
        # (needed when addon is re-enabled without restarting Blender)
        importlib.reload(_handlers_pkg)
        _handlers_pkg._loaded_handlers.clear()

    def execute(self, category: str, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a command

        Args:
            category: Command category
            action: Specific action
            params: Action parameters

        Returns:
            Execution result (enriched with error suggestions on failure)
        """
        try:
            # System commands are handled internally
            if category == "system":
                method_name = f"handle_{action}"
                method = getattr(self, method_name, None)
                if method is None:
                    return enrich_error({
                        "success": False,
                        "error": {
                            "code": "UNKNOWN_ACTION",
                            "message": f"Unknown action: system.{action}",
                        },
                    })
                return enrich_error(method(params))

            # Lazy load the handler
            handler = get_handler(category)
            if handler is None:
                return enrich_error({
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_CATEGORY",
                        "message": f"Unknown command category: {category}",
                    },
                })

            # Get the action method
            method_name = f"handle_{action}"
            method = getattr(handler, method_name, None)

            if method is None:
                return enrich_error({
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_ACTION",
                        "message": f"Unknown action: {category}.{action}",
                    },
                })

            # Execute the action and enrich errors with suggestions
            result = method(params)

            return enrich_error(result)

        except Exception as e:
            traceback.print_exc()
            return enrich_error(
                {"success": False, "error": {"code": "EXECUTION_ERROR", "message": str(e)}}
            )

    # System command handlers
    def handle_get_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get Blender information"""
        return {
            "success": True,
            "data": {
                "version": bpy.app.version,
                "version_string": bpy.app.version_string,
                "filepath": bpy.data.filepath or "",
                "scene": bpy.context.scene.name if bpy.context.scene else "",
                "objects_count": len(bpy.data.objects),
            },
        }

    def handle_execute_python(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute Python code in Blender (with safety checks)"""
        code = params.get("code", "")
        if not code:
            return {
                "success": False,
                "error": {"code": "MISSING_CODE", "message": "Missing 'code' parameter"},
            }

        from .handlers.utility import _check_code_safety

        warning = _check_code_safety(code)
        if warning:
            return {"success": False, "error": {"code": "SAFETY_CHECK_FAILED", "message": warning}}

        try:
            import builtins as _builtins_mod

            local_vars = {"bpy": bpy, "result": None}
            exec(code, {"__builtins__": _builtins_mod, "bpy": bpy}, local_vars)
            return {"success": True, "data": {"result": str(local_vars.get("result", "OK"))}}
        except Exception as e:
            traceback.print_exc()
            return {"success": False, "error": {"code": "PYTHON_ERROR", "message": str(e)}}
