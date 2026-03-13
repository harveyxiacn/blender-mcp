"""Tests for server-addon parity.

Verifies that every tool module registered on the MCP server side has a
corresponding command handler on the Blender addon side, and vice-versa.

Naming conventions differ between the two registries (e.g. the server uses
"sculpting" while the addon handler is called "sculpt"), so this module
maintains an explicit mapping of known aliases.  Modules that exist only on
one side are tracked as *known gaps* and are expected to produce warnings
rather than hard failures.
"""

import ast
import importlib
import pathlib
import warnings

import pytest

from blender_mcp.tools_config import MODULE_REGISTRY

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_HANDLERS_INIT = _REPO_ROOT / "addon" / "blender_mcp_addon" / "handlers" / "__init__.py"

# ---------------------------------------------------------------------------
# Known naming differences: server module name -> addon handler key
#
# The server and addon evolved independently, so some module names diverge.
# This map lets the parity check recognise them as equivalent.
# ---------------------------------------------------------------------------

SERVER_TO_ADDON_ALIASES: dict[str, str] = {
    "character_templates": "character_template",
    "animation_presets": "animation_preset",
    "uv_mapping": "uv",
    "video_editing": "vse",
    "sculpting": "sculpt",
    "texture_painting": "texture_paint",
    "grease_pencil": "gpencil",
}

# Server-only modules that intentionally have no addon handler.
# These are orchestration / meta modules that run entirely on the server.
KNOWN_SERVER_ONLY: set[str] = {"pipeline", "quality_audit", "skills"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_handler_modules() -> dict[str, str]:
    """Parse HANDLER_MODULES from the addon handlers __init__.py via AST.

    This avoids importing the addon code (which depends on ``bpy``) and
    instead extracts the dictionary literal directly from the source file.
    """
    assert _HANDLERS_INIT.exists(), f"Addon handlers __init__.py not found at {_HANDLERS_INIT}"
    source = _HANDLERS_INIT.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_HANDLERS_INIT))

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "HANDLER_MODULES"
        ):
            # Safely evaluate the dict literal.
            value = ast.literal_eval(node.value)
            assert isinstance(value, dict), "HANDLER_MODULES is not a dict"
            return value

    pytest.fail("Could not find HANDLER_MODULES in addon handlers __init__.py")


# Module-level fixture so every test in this file shares the same parsed data.
HANDLER_MODULES: dict[str, str] = _parse_handler_modules()

# ---------------------------------------------------------------------------
# Tests: server -> addon parity
# ---------------------------------------------------------------------------


class TestServerToAddonParity:
    """Every server MODULE_REGISTRY entry should have an addon handler."""

    def test_all_server_modules_have_addon_handler(self) -> None:
        """Check that each server module maps to an addon handler.

        Known server-only modules (pipeline, quality_audit, skills) are
        expected to be absent and trigger warnings instead of failures.
        """
        missing: list[str] = []

        for server_module in MODULE_REGISTRY:
            if server_module in KNOWN_SERVER_ONLY:
                continue

            addon_key = SERVER_TO_ADDON_ALIASES.get(server_module, server_module)
            if addon_key not in HANDLER_MODULES:
                missing.append(server_module)

        assert not missing, f"Server modules without addon handler: {sorted(missing)}"

    @pytest.mark.parametrize("module_name", sorted(KNOWN_SERVER_ONLY))
    def test_known_server_only_gaps_warn(self, module_name: str) -> None:
        """Known server-only modules should not have addon handlers.

        If someone adds an addon handler for one of these, this test will
        fail -- a signal to remove the module from KNOWN_SERVER_ONLY.
        """
        addon_key = SERVER_TO_ADDON_ALIASES.get(module_name, module_name)
        if addon_key in HANDLER_MODULES:
            pytest.fail(
                f"'{module_name}' is listed in KNOWN_SERVER_ONLY but now has "
                f"an addon handler ('{addon_key}'). Remove it from "
                f"KNOWN_SERVER_ONLY."
            )
        # Emit a warning so CI dashboards can track the gap.
        warnings.warn(
            f"Server module '{module_name}' has no addon handler (known gap)",
            stacklevel=1,
        )


# ---------------------------------------------------------------------------
# Tests: addon -> server parity
# ---------------------------------------------------------------------------


class TestAddonToServerParity:
    """Every addon handler should have a corresponding server module."""

    # Build the reverse alias map: addon key -> server module name
    _ADDON_TO_SERVER: dict[str, str] = {v: k for k, v in SERVER_TO_ADDON_ALIASES.items()}

    def test_all_addon_handlers_have_server_module(self) -> None:
        """Each addon handler key should map to a MODULE_REGISTRY entry."""
        missing: list[str] = []

        for addon_key in HANDLER_MODULES:
            server_key = self._ADDON_TO_SERVER.get(addon_key, addon_key)
            if server_key not in MODULE_REGISTRY:
                missing.append(addon_key)

        assert not missing, f"Addon handlers without server module: {sorted(missing)}"


# ---------------------------------------------------------------------------
# Tests: server tool module imports
# ---------------------------------------------------------------------------


class TestServerModuleImports:
    """All server tool modules referenced in MODULE_REGISTRY should be
    importable without errors."""

    @pytest.mark.parametrize("module_name", sorted(MODULE_REGISTRY.keys()))
    def test_tool_module_imports(self, module_name: str) -> None:
        """Import ``blender_mcp.tools.<module_name>`` and verify it exposes
        the register function listed in MODULE_REGISTRY."""
        mod = importlib.import_module(f"blender_mcp.tools.{module_name}")
        register_func_name = MODULE_REGISTRY[module_name]
        assert hasattr(mod, register_func_name), (
            f"blender_mcp.tools.{module_name} does not export " f"'{register_func_name}'"
        )


# ---------------------------------------------------------------------------
# Tests: addon handler files exist on disk
# ---------------------------------------------------------------------------


class TestAddonHandlerFilesExist:
    """Every entry in HANDLER_MODULES should correspond to a Python file
    inside the addon handlers directory."""

    _HANDLERS_DIR = _HANDLERS_INIT.parent

    @pytest.mark.parametrize(
        "handler_key,filename",
        sorted(HANDLER_MODULES.items()),
    )
    def test_handler_file_exists(self, handler_key: str, filename: str) -> None:
        """Check that ``handlers/<filename>.py`` exists on disk."""
        handler_file = self._HANDLERS_DIR / f"{filename}.py"
        assert handler_file.exists(), (
            f"Handler file missing for '{handler_key}': expected " f"{handler_file}"
        )
