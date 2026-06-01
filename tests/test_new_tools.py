"""Tests for the new Smart Tools v2 modules.

Verifies that all new tool modules import correctly, register functions exist,
and addon handler files are present with expected action methods.
"""

import ast
import importlib
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_HANDLERS_DIR = _REPO_ROOT / "addon" / "blender_mcp_addon" / "handlers"

# ---------------------------------------------------------------------------
# New modules and their expected tools/actions
# ---------------------------------------------------------------------------

NEW_MODULES = {
    "snapshot": {
        "register_func": "register_snapshot_tools",
        "handler_file": "snapshot.py",
        "expected_actions": ["handle_viewport", "handle_render_preview"],
    },
    "describe": {
        "register_func": "register_describe_tools",
        "handler_file": "describe.py",
        "expected_actions": ["handle_scene", "handle_hierarchy", "handle_object"],
    },
    "checkpoint": {
        "register_func": "register_checkpoint_tools",
        "handler_file": "checkpoint.py",
        "expected_actions": ["handle_save", "handle_restore", "handle_list", "handle_delete"],
    },
    "quick": {
        "register_func": "register_quick_tools",
        "handler_file": "quick.py",
        "expected_actions": ["handle_product_shot", "handle_turntable", "handle_scene_setup"],
    },
}


# ---------------------------------------------------------------------------
# Tests: MCP tool module imports
# ---------------------------------------------------------------------------


class TestNewToolModuleImports:
    """All new tool modules should be importable and expose register functions."""

    @pytest.mark.parametrize("module_name", sorted(NEW_MODULES.keys()))
    def test_import_and_register(self, module_name: str) -> None:
        """Import the tool module and verify the register function exists."""
        info = NEW_MODULES[module_name]
        mod = importlib.import_module(f"blender_mcp.tools.{module_name}")
        assert hasattr(mod, info["register_func"]), (
            f"blender_mcp.tools.{module_name} does not export '{info['register_func']}'"
        )

    @pytest.mark.parametrize("module_name", sorted(NEW_MODULES.keys()))
    def test_register_func_is_callable(self, module_name: str) -> None:
        """Register function should be callable."""
        info = NEW_MODULES[module_name]
        mod = importlib.import_module(f"blender_mcp.tools.{module_name}")
        func = getattr(mod, info["register_func"])
        assert callable(func)


# ---------------------------------------------------------------------------
# Tests: Addon handler files exist
# ---------------------------------------------------------------------------


class TestNewHandlerFiles:
    """All new handler files should exist on disk."""

    @pytest.mark.parametrize("module_name", sorted(NEW_MODULES.keys()))
    def test_handler_file_exists(self, module_name: str) -> None:
        info = NEW_MODULES[module_name]
        handler_file = _HANDLERS_DIR / info["handler_file"]
        assert handler_file.exists(), f"Handler file missing: {handler_file}"


# ---------------------------------------------------------------------------
# Tests: Handler actions exist (via AST parsing, no bpy import needed)
# ---------------------------------------------------------------------------


class TestNewHandlerActions:
    """All expected handler actions should be defined as functions."""

    @pytest.mark.parametrize("module_name", sorted(NEW_MODULES.keys()))
    def test_handler_has_expected_actions(self, module_name: str) -> None:
        """Parse the handler file with AST and check for expected function definitions."""
        info = NEW_MODULES[module_name]
        handler_file = _HANDLERS_DIR / info["handler_file"]
        source = handler_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(handler_file))

        defined_functions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

        for action in info["expected_actions"]:
            assert action in defined_functions, (
                f"Handler {info['handler_file']} missing function '{action}'. "
                f"Found: {sorted(defined_functions)}"
            )


# ---------------------------------------------------------------------------
# Tests: Error suggestions module
# ---------------------------------------------------------------------------


class TestErrorSuggestions:
    """Verify error_suggestions.py is well-formed."""

    def test_error_suggestions_file_exists(self) -> None:
        path = _HANDLERS_DIR / "error_suggestions.py"
        assert path.exists(), "error_suggestions.py handler file missing"

    def test_enrich_error_function_exists(self) -> None:
        """Parse the file and check for enrich_error function."""
        path = _HANDLERS_DIR / "error_suggestions.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        funcs = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        assert "enrich_error" in funcs

    def test_suggestions_dict_exists(self) -> None:
        """Parse the file and check for SUGGESTIONS dict."""
        path = _HANDLERS_DIR / "error_suggestions.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        # Check both Assign and AnnAssign (type-annotated assignment)
        names: set[str] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                names.add(node.targets[0].id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
        assert "SUGGESTIONS" in names


# ---------------------------------------------------------------------------
# Tests: tools_config.py integration
# ---------------------------------------------------------------------------


class TestToolsConfigIntegration:
    """New modules should be in MODULE_REGISTRY."""

    def test_new_modules_in_registry(self) -> None:
        from blender_mcp.tools_config import MODULE_REGISTRY

        for module_name in NEW_MODULES:
            assert module_name in MODULE_REGISTRY, (
                f"'{module_name}' not found in MODULE_REGISTRY"
            )

    def test_describe_and_snapshot_in_core(self) -> None:
        from blender_mcp.tools_config import CORE_MODULES

        assert "describe" in CORE_MODULES
        assert "snapshot" in CORE_MODULES

    def test_checkpoint_and_quick_in_full(self) -> None:
        from blender_mcp.tools_config import FULL_MODULES

        assert "checkpoint" in FULL_MODULES
        assert "quick" in FULL_MODULES


# ---------------------------------------------------------------------------
# Tests: Executor integration with enrich_error
# ---------------------------------------------------------------------------


class TestExecutorIntegration:
    """Verify executor.py imports enrich_error."""

    def test_executor_imports_enrich_error(self) -> None:
        executor_path = _REPO_ROOT / "addon" / "blender_mcp_addon" / "executor.py"
        source = executor_path.read_text(encoding="utf-8")
        assert "enrich_error" in source, "executor.py should import and use enrich_error"

    def test_executor_calls_enrich_error(self) -> None:
        executor_path = _REPO_ROOT / "addon" / "blender_mcp_addon" / "executor.py"
        source = executor_path.read_text(encoding="utf-8")
        # Should call enrich_error at least 3 times (handler result + error returns)
        assert source.count("enrich_error(") >= 3, (
            "executor.py should call enrich_error() on all return paths"
        )
