"""
Blender Addon Installer

Automatically detects the Blender installation path and installs the MCP addon.
Supports Blender 4.x and 5.x with automatic version detection.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


def resolve_addon_source() -> Path:
    """Resolve the addon source directory.

    Supports the standard repository layout:
      repo_root/src/blender_mcp/installer.py
      repo_root/addon/blender_mcp_addon
    """
    module_file = Path(__file__).resolve()
    candidates = [
        module_file.parents[2] / "addon" / "blender_mcp_addon",  # repo_root/addon/...
        module_file.parents[1] / "addon" / "blender_mcp_addon",  # src/addon/... (fallback)
        Path.cwd() / "addon" / "blender_mcp_addon",              # cwd fallback
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = "\n".join(f"  - {path}" for path in candidates)
    raise FileNotFoundError(f"Addon source not found. Tried:\n{tried}")


def find_blender_paths() -> List[Path]:
    """Find Blender installation paths on the system."""
    paths = []

    if sys.platform == "win32":
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
        common_paths = [
            Path("/Applications/Blender.app"),
            Path.home() / "Applications" / "Blender.app",
        ]
        paths.extend([p for p in common_paths if p.exists()])

    else:
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
    """Get the addon directory for a specific Blender installation."""
    if sys.platform == "darwin":
        if blender_path.suffix == ".app":
            contents = blender_path / "Contents" / "Resources"
            if contents.exists():
                for item in sorted(contents.iterdir(), reverse=True):
                    if item.is_dir() and item.name[0].isdigit():
                        return item / "scripts" / "addons"
    else:
        for item in sorted(blender_path.iterdir(), reverse=True):
            if item.is_dir() and item.name[0].isdigit():
                return item / "scripts" / "addons"

    return None


def _detect_latest_blender_version() -> str:
    """Auto-detect the latest Blender version from user config directories.

    Scans the platform-specific Blender config directory and returns the
    highest version number found (e.g. '5.0', '4.2'). Falls back to '4.0'
    if no version directories are found.
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        config_dir = base / "Blender Foundation" / "Blender"
    elif sys.platform == "darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "Blender"
    else:
        config_dir = Path.home() / ".config" / "blender"

    if config_dir.exists():
        versions = []
        for item in config_dir.iterdir():
            if item.is_dir() and item.name[0].isdigit():
                try:
                    parts = item.name.split(".")
                    versions.append((int(parts[0]), int(parts[1]) if len(parts) > 1 else 0, item.name))
                except (ValueError, IndexError):
                    continue
        if versions:
            versions.sort(reverse=True)
            return versions[0][2]

    return "4.0"


def get_user_addon_path(version: Optional[str] = None) -> Path:
    """Get the user addon directory path.

    Args:
        version: Blender version string (e.g. '5.0', '4.2').
                 If None, auto-detects the latest installed version.
    """
    if version is None:
        version = _detect_latest_blender_version()

    logger.info(f"Using Blender version: {version}")

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Blender Foundation" / "Blender" / version / "scripts" / "addons"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Blender" / version / "scripts" / "addons"
    else:
        return Path.home() / ".config" / "blender" / version / "scripts" / "addons"


def install_blender_addon(
    blender_path: Optional[str] = None,
    force: bool = False
) -> bool:
    """Install the Blender MCP addon.

    Args:
        blender_path: Explicit Blender installation path (optional).
        force: Force reinstall even if addon already exists.

    Returns:
        True if installed successfully, False if already exists.
    """
    addon_source = resolve_addon_source()

    if blender_path:
        target_base = get_addon_path(Path(blender_path))
        if not target_base:
            raise ValueError(f"Cannot determine addon directory for: {blender_path}")
    else:
        target_base = get_user_addon_path()

    target_path = target_base / "blender_mcp_addon"

    target_base.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        if force:
            logger.info(f"Removing existing addon: {target_path}")
            shutil.rmtree(target_path)
        else:
            logger.info(f"Addon already exists: {target_path}")
            return False

    logger.info(f"Installing addon to: {target_path}")
    shutil.copytree(addon_source, target_path)

    logger.info("Addon installation complete")
    return True
