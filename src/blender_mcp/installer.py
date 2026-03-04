"""
Blender 插件安装器

自动检测 Blender 安装路径并安装 MCP 插件。
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


def resolve_addon_source() -> Path:
    """解析 addon 源码目录。

    优先支持仓库源码布局:
      repo_root/src/blender_mcp/installer.py
      repo_root/addon/blender_mcp_addon
    """
    module_file = Path(__file__).resolve()
    candidates = [
        module_file.parents[2] / "addon" / "blender_mcp_addon",  # repo_root/addon/...
        module_file.parents[1] / "addon" / "blender_mcp_addon",  # src/addon/... (备用)
        Path.cwd() / "addon" / "blender_mcp_addon",              # 从仓库根目录运行时的备用路径
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = "\n".join(f"  - {path}" for path in candidates)
    raise FileNotFoundError(f"插件源文件不存在，已尝试路径:\n{tried}")


def find_blender_paths() -> List[Path]:
    """查找系统中的 Blender 安装路径"""
    paths = []
    
    if sys.platform == "win32":
        # Windows 常见路径
        common_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Blender Foundation",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Blender Foundation",
            Path.home() / "AppData" / "Roaming" / "Blender Foundation",
        ]
        
        for base in common_paths:
            if base.exists():
                for item in base.iterdir():
                    if item.is_dir() and item.name.startswith("Blender"):
                        paths.append(item)
    
    elif sys.platform == "darwin":
        # macOS 常见路径
        common_paths = [
            Path("/Applications/Blender.app"),
            Path.home() / "Applications" / "Blender.app",
        ]
        paths.extend([p for p in common_paths if p.exists()])
    
    else:
        # Linux 常见路径
        common_paths = [
            Path("/usr/share/blender"),
            Path("/usr/local/share/blender"),
            Path.home() / ".local" / "share" / "blender",
            Path("/opt/blender"),
        ]
        
        for base in common_paths:
            if base.exists():
                if base.name == "blender":
                    paths.append(base)
                else:
                    for item in base.iterdir():
                        if item.is_dir():
                            paths.append(item)
    
    return paths


def get_addon_path(blender_path: Path) -> Optional[Path]:
    """获取 Blender 插件目录路径"""
    if sys.platform == "darwin":
        # macOS
        if blender_path.suffix == ".app":
            # 查找版本号目录
            contents = blender_path / "Contents" / "Resources"
            for item in contents.iterdir():
                if item.is_dir() and item.name[0].isdigit():
                    return item / "scripts" / "addons"
    else:
        # Windows / Linux
        for item in blender_path.iterdir():
            if item.is_dir() and item.name[0].isdigit():
                return item / "scripts" / "addons"
    
    return None


def get_user_addon_path() -> Path:
    """获取用户插件目录路径"""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Blender Foundation" / "Blender" / "5.0" / "scripts" / "addons"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Blender" / "5.0" / "scripts" / "addons"
    else:
        return Path.home() / ".config" / "blender" / "5.0" / "scripts" / "addons"


def install_blender_addon(
    blender_path: Optional[str] = None,
    force: bool = False
) -> bool:
    """安装 Blender 插件
    
    Args:
        blender_path: Blender 安装路径（可选）
        force: 是否强制重新安装
        
    Returns:
        是否安装成功
    """
    # 确定源插件路径
    addon_source = resolve_addon_source()
    
    # 确定目标路径
    if blender_path:
        target_base = get_addon_path(Path(blender_path))
        if not target_base:
            raise ValueError(f"无法确定 Blender 插件目录: {blender_path}")
    else:
        # 使用用户插件目录
        target_base = get_user_addon_path()
    
    target_path = target_base / "blender_mcp_addon"
    
    # 创建目录
    target_base.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已存在
    if target_path.exists():
        if force:
            logger.info(f"删除现有插件: {target_path}")
            shutil.rmtree(target_path)
        else:
            logger.info(f"插件已存在: {target_path}")
            return False
    
    # 复制插件
    logger.info(f"安装插件到: {target_path}")
    shutil.copytree(addon_source, target_path)
    
    logger.info("插件安装完成")
    return True
