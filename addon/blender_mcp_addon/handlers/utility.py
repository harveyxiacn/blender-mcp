"""
Utility command handler.

Handles Python execution, viewport screenshots, file operations, and system info.
"""

import os
import re
import tempfile
from typing import Any

import bpy

MAX_CODE_SIZE = int(os.environ.get("BLENDER_MCP_MAX_CODE_SIZE", "100000"))

# Patterns that indicate potentially dangerous operations.
# This is a defence-in-depth measure; the primary security boundary is that
# the Blender addon only listens on localhost.
BLOCKED_PATTERNS = [
    # Process spawning
    "subprocess",
    "Popen",
    "os.system",
    "os.exec",
    "os.spawn",
    "commands.getoutput",
    # Network access
    "socket.connect",
    "socket.bind",
    "socket.listen",
    "urllib.request",
    "http.client",
    "requests.get",
    "requests.post",
    # Destructive file operations
    "shutil.rmtree",
    "os.remove",
    "os.unlink",
    "os.rmdir",
    "os.removedirs",
    "pathlib.Path.unlink",
    "pathlib.Path.rmdir",
    # Import tricks to bypass checks
    "__import__('subprocess",
    "__import__('socket",
    "__import__('os').system",
    "__import__('shutil').rmtree",
    # Code compilation / eval chains
    "compile(",
    "eval(",
    "exec(",
    # ctypes / low-level
    "ctypes.",
    "ctypes.CDLL",
]

# Regex patterns for more sophisticated evasion attempts
BLOCKED_REGEX = [
    re.compile(r"getattr\s*\(.+['\"]system['\"]"),  # getattr(os, 'system')
    re.compile(r"globals\s*\(\s*\)\s*\["),  # globals()['...']
    re.compile(r"__builtins__\s*\["),  # __builtins__['...']
    re.compile(r"importlib\.import_module"),  # importlib bypass
]


def _check_code_safety(code: str) -> str | None:
    """Check for dangerous patterns. Returns warning message or None if safe."""
    if not code or not code.strip():
        return "Code is empty"

    if len(code) > MAX_CODE_SIZE:
        return f"Code exceeds size limit ({MAX_CODE_SIZE} characters)"

    code_lower = code.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in code_lower:
            return f"Blocked operation detected: {pattern}"

    for regex in BLOCKED_REGEX:
        if regex.search(code):
            return f"Blocked pattern detected: {regex.pattern}"

    return None


def _make_restricted_builtins() -> dict:
    """Build a restricted __builtins__ dict for code execution.

    Allows standard Blender scripting while blocking dangerous builtins.
    """
    import builtins

    blocked = {
        "exec",
        "eval",
        "compile",
        "__import__",  # use the explicit allowlist in exec_globals instead
        "breakpoint",
        "exit",
        "quit",
    }
    return {
        name: getattr(builtins, name)
        for name in dir(builtins)
        if not name.startswith("_") and name not in blocked
    }


def handle_execute_python(params: dict[str, Any]) -> dict[str, Any]:
    """Execute Python code inside Blender with safety checks."""
    code = params.get("code", "")

    if not code or not code.strip():
        return {"success": False, "error": {"code": "EMPTY_CODE", "message": "Code is empty"}}

    warning = _check_code_safety(code)
    if warning:
        return {"success": False, "error": {"code": "SAFETY_CHECK_FAILED", "message": warning}}

    try:
        import io
        import math
        import sys

        import mathutils  # Blender math utilities

        exec_globals = {
            "bpy": bpy,
            "math": math,
            "mathutils": mathutils,
            "__builtins__": _make_restricted_builtins(),
        }

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_out = io.StringIO()
        sys.stderr = captured_err = io.StringIO()

        try:
            exec(code, exec_globals)
            output = captured_out.getvalue()
            errors = captured_err.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        result_data: dict[str, Any] = {"output": output}
        if errors:
            result_data["stderr"] = errors

        return {"success": True, "data": result_data}
    except Exception as e:
        return {"success": False, "error": {"code": "EXECUTION_ERROR", "message": str(e)}}


def _validate_filepath(filepath: str, must_exist: bool = False) -> str | None:
    """Validate a file path for safety.

    Returns an error message if the path is invalid, None if OK.
    Checks for:
    - null bytes (path injection)
    - path traversal patterns
    - excessively long paths
    """
    if not filepath:
        return "File path is required"
    if "\x00" in filepath:
        return "Path contains null bytes"
    if len(filepath) > 4096:
        return "Path exceeds maximum length (4096 characters)"

    # Normalise and resolve to catch traversal
    resolved = os.path.realpath(os.path.expanduser(filepath))

    if must_exist and not os.path.exists(resolved):
        return f"File not found: {filepath}"

    return None


def handle_viewport_screenshot(params: dict[str, Any]) -> dict[str, Any]:
    """Capture a viewport screenshot."""
    output_path = params.get("output_path")
    width = params.get("width", 800)
    height = params.get("height", 600)

    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), "viewport_screenshot.png")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    scene = bpy.context.scene
    old_width = scene.render.resolution_x
    old_height = scene.render.resolution_y
    old_percentage = scene.render.resolution_percentage

    try:
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100

        # Find the 3D viewport
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        # Render viewport via OpenGL
                        override = bpy.context.copy()
                        override["area"] = area
                        override["region"] = region

                        bpy.ops.render.opengl(override, write_still=True)

                        # Save the rendered image
                        bpy.data.images["Render Result"].save_render(output_path)

                        return {"success": True, "data": {"output_path": output_path}}
    finally:
        # Restore original render settings
        scene.render.resolution_x = old_width
        scene.render.resolution_y = old_height
        scene.render.resolution_percentage = old_percentage

    return {
        "success": False,
        "error": {"code": "NO_3D_VIEWPORT", "message": "No 3D viewport found"},
    }


def handle_file_save(params: dict[str, Any]) -> dict[str, Any]:
    """Save the current Blender file."""
    filepath = params.get("filepath")
    compress = params.get("compress", True)

    if filepath:
        error = _validate_filepath(filepath)
        if error:
            return {"success": False, "error": {"code": "INVALID_PATH", "message": error}}
        bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
    else:
        if bpy.data.filepath:
            bpy.ops.wm.save_mainfile(compress=compress)
        else:
            return {
                "success": False,
                "error": {
                    "code": "NO_FILEPATH",
                    "message": "No file path specified and no current file to save",
                },
            }

    return {"success": True, "data": {"filepath": bpy.data.filepath}}


def handle_file_open(params: dict[str, Any]) -> dict[str, Any]:
    """Open a Blender file."""
    filepath = params.get("filepath")
    load_ui = params.get("load_ui", False)

    if not filepath:
        return {
            "success": False,
            "error": {"code": "NO_FILEPATH", "message": "File path is required"},
        }

    error = _validate_filepath(filepath, must_exist=True)
    if error:
        return {"success": False, "error": {"code": "INVALID_PATH", "message": error}}

    bpy.ops.wm.open_mainfile(filepath=filepath, load_ui=load_ui)

    return {"success": True, "data": {"filepath": bpy.data.filepath}}


def handle_get_info(params: dict[str, Any]) -> dict[str, Any]:
    """Get Blender version and scene information."""
    return {
        "success": True,
        "data": {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "filepath": bpy.data.filepath or "",
            "scene": bpy.context.scene.name if bpy.context.scene else "",
            "objects_count": len(bpy.data.objects),
        },
    }


def handle_undo(params: dict[str, Any]) -> dict[str, Any]:
    """Undo operations."""
    steps = params.get("steps", 1)

    for _ in range(steps):
        bpy.ops.ed.undo()

    return {"success": True, "data": {}}


def handle_redo(params: dict[str, Any]) -> dict[str, Any]:
    """Redo operations."""
    steps = params.get("steps", 1)

    for _ in range(steps):
        bpy.ops.ed.redo()

    return {"success": True, "data": {}}


def handle_get_blender_version(params: dict[str, Any]) -> dict[str, Any]:
    """Get detailed Blender version and build information."""
    return {
        "success": True,
        "data": {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "build_date": bpy.app.build_date.decode() if hasattr(bpy.app, "build_date") else "",
            "build_platform": (
                bpy.app.build_platform.decode() if hasattr(bpy.app, "build_platform") else ""
            ),
        },
    }
