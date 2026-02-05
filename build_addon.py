#!/usr/bin/env python
"""
Blender MCP Addon 打包脚本

将 addon 目录打包为可直接在 Blender 中安装的 zip 文件。

用法:
    python build_addon.py

输出:
    dist/blender_mcp_addon.zip
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def build_addon():
    """打包 addon 为 zip 文件"""
    
    # 路径配置
    script_dir = Path(__file__).parent
    addon_source = script_dir / "addon" / "blender_mcp_addon"
    dist_dir = script_dir / "dist"
    
    # 创建 dist 目录
    dist_dir.mkdir(exist_ok=True)
    
    # 生成带时间戳的文件名（可选）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"blender_mcp_addon.zip"
    zip_path = dist_dir / zip_name
    
    # 如果已存在，先删除
    if zip_path.exists():
        zip_path.unlink()
    
    # 要排除的文件/目录
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".gitignore",
        "*.egg-info",
        ".DS_Store",
        "Thumbs.db",
    ]
    
    def should_exclude(path: Path) -> bool:
        """检查是否应该排除"""
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False
    
    def add_to_zip(zf: zipfile.ZipFile, source: Path, arcname: str):
        """递归添加文件到 zip"""
        if source.is_file():
            if not should_exclude(source):
                zf.write(source, arcname)
                print(f"  添加: {arcname}")
        elif source.is_dir():
            if not should_exclude(source):
                for item in source.iterdir():
                    add_to_zip(zf, item, f"{arcname}/{item.name}")
    
    print(f"打包 Blender MCP Addon...")
    print(f"源目录: {addon_source}")
    print(f"输出文件: {zip_path}")
    print()
    
    # 创建 zip 文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_to_zip(zf, addon_source, "blender_mcp_addon")
    
    # 计算文件大小
    size_kb = zip_path.stat().st_size / 1024
    
    print()
    print(f"[OK] Build completed!")
    print(f"  File: {zip_path}")
    print(f"  Size: {size_kb:.1f} KB")
    print()
    print("Installation:")
    print("  1. Open Blender")
    print("  2. Edit -> Preferences -> Add-ons")
    print("  3. Click Install...")
    print(f"  4. Select {zip_path}")
    print("  5. Enable 'Blender MCP' addon")
    
    return zip_path


if __name__ == "__main__":
    build_addon()
