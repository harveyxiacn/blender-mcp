#!/usr/bin/env python
"""
Blender MCP Addon Build Script

Packages the addon directory into a zip file that can be installed directly in Blender.

Usage:
    python build_addon.py

Output:
    dist/blender_mcp_addon.zip
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def build_addon():
    """Package the addon into a zip file"""

    # Path configuration
    script_dir = Path(__file__).parent
    addon_source = script_dir / "addon" / "blender_mcp_addon"
    dist_dir = script_dir / "dist"
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    # Generate timestamped filename (optional)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"blender_mcp_addon.zip"
    zip_path = dist_dir / zip_name
    
    # Remove if already exists
    if zip_path.exists():
        zip_path.unlink()
    
    # Files/directories to exclude
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
        """Check if the path should be excluded"""
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False
    
    def add_to_zip(zf: zipfile.ZipFile, source: Path, arcname: str):
        """Recursively add files to the zip archive"""
        if source.is_file():
            if not should_exclude(source):
                zf.write(source, arcname)
                print(f"  Added: {arcname}")
        elif source.is_dir():
            if not should_exclude(source):
                for item in source.iterdir():
                    add_to_zip(zf, item, f"{arcname}/{item.name}")
    
    print(f"Packaging Blender MCP Addon...")
    print(f"Source directory: {addon_source}")
    print(f"Output file: {zip_path}")
    print()
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_to_zip(zf, addon_source, "blender_mcp_addon")
    
    # Calculate file size
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
