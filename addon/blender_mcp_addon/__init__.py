"""
Blender MCP Addon - 插件入口

在 Blender 中启用 MCP 通信服务，接收并执行来自 MCP 服务器的命令。
"""

bl_info = {
    "name": "Blender MCP",
    "author": "Blender MCP Team",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Enable AI assistants to control Blender through MCP protocol",
    "category": "Interface",
    "doc_url": "https://github.com/your-username/blender-mcp",
    "tracker_url": "https://github.com/your-username/blender-mcp/issues",
}

import bpy
import sys
import importlib
from pathlib import Path
from bpy.props import IntProperty, BoolProperty, StringProperty

# 模块导入
from . import server
from . import operators
from . import panels


# 热更新支持
def get_addon_modules():
    """获取所有需要重新加载的模块"""
    addon_package = __name__
    modules_to_reload = []
    
    for name, module in list(sys.modules.items()):
        if name.startswith(addon_package):
            modules_to_reload.append((name, module))
    
    # 按模块层级深度排序，确保子模块先重新加载
    modules_to_reload.sort(key=lambda x: x[0].count('.'), reverse=True)
    return modules_to_reload


def hot_reload():
    """执行热更新 - 重新加载所有addon模块"""
    import shutil
    
    # 获取偏好设置
    prefs = bpy.context.preferences.addons.get(__name__)
    if not prefs or not prefs.preferences.dev_source_path:
        return False, "未设置开发源代码目录"
    
    source_path = Path(prefs.preferences.dev_source_path)
    if not source_path.exists():
        return False, f"源代码目录不存在: {source_path}"
    
    # 检查是否是有效的addon目录
    if not (source_path / "__init__.py").exists():
        return False, f"目录不是有效的Python包: {source_path}"
    
    # 获取当前addon安装目录
    addon_path = Path(__file__).parent
    
    # 停止服务
    was_running = server.is_running()
    if was_running:
        server.stop_server()
    
    # 要排除的项目
    exclude = {"__pycache__", ".git", ".gitignore", "*.pyc", "*.pyo"}
    
    def should_exclude(name):
        if name in exclude:
            return True
        for pattern in exclude:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
        return False
    
    try:
        # 复制文件
        for item in source_path.iterdir():
            if should_exclude(item.name):
                continue
            
            dest = addon_path / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude))
            else:
                shutil.copy2(item, dest)
        
        # 重新加载模块
        modules = get_addon_modules()
        for name, module in modules:
            if module is not None:
                try:
                    importlib.reload(module)
                except Exception as e:
                    print(f"[MCP] 重新加载模块失败 {name}: {e}")
        
        # 重启服务
        if was_running:
            port = prefs.preferences.port if prefs else 9876
            server.start_server(port)
        
        return True, "热更新完成"
        
    except Exception as e:
        return False, f"热更新失败: {e}"


class BlenderMCPPreferences(bpy.types.AddonPreferences):
    """插件偏好设置"""
    bl_idname = __name__
    
    port: IntProperty(
        name="服务端口",
        description="MCP 通信服务端口",
        default=9876,
        min=1024,
        max=65535
    )
    
    auto_start: BoolProperty(
        name="自动启动",
        description="Blender 启动时自动启动 MCP 服务",
        default=True
    )
    
    log_level: StringProperty(
        name="日志级别",
        description="日志详细程度",
        default="INFO"
    )
    
    dev_source_path: StringProperty(
        name="开发源代码目录",
        description="用于热更新的源代码目录路径 (addon/blender_mcp_addon)",
        default="",
        subtype='DIR_PATH'
    )
    
    def draw(self, context):
        layout = self.layout
        
        # 基本设置
        box = layout.box()
        box.label(text="基本设置", icon='PREFERENCES')
        box.prop(self, "port")
        box.prop(self, "auto_start")
        box.prop(self, "log_level")
        
        # 开发者设置
        layout.separator()
        box = layout.box()
        box.label(text="开发者设置", icon='TOOL_SETTINGS')
        box.prop(self, "dev_source_path")
        
        if self.dev_source_path:
            row = box.row()
            row.operator("mcp.hot_reload", text="执行热更新", icon='FILE_REFRESH')


# 所有需要注册的类
classes = [
    BlenderMCPPreferences,
]


def register():
    """注册插件"""
    # 注册类
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # 注册子模块
    operators.register()
    panels.register()
    
    # 自动启动服务
    prefs = bpy.context.preferences.addons.get(__name__)
    if prefs and prefs.preferences.auto_start:
        # 延迟启动，确保 Blender 完全初始化
        bpy.app.timers.register(
            lambda: _delayed_start(),
            first_interval=1.0
        )


def unregister():
    """注销插件"""
    # 停止服务
    server.stop_server()
    
    # 注销子模块
    panels.unregister()
    operators.unregister()
    
    # 注销类
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def _delayed_start():
    """延迟启动服务"""
    try:
        prefs = bpy.context.preferences.addons.get(__name__)
        if prefs:
            port = prefs.preferences.port
            server.start_server(port)
    except Exception as e:
        print(f"[MCP] 自动启动服务失败: {e}")
    return None  # 不重复执行


if __name__ == "__main__":
    register()
