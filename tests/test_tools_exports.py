"""Tests for top-level tool exports."""

from blender_mcp import tools

_EXPECTED_EXPORTS = [
    "register_pipeline_tools",
    "register_quality_audit_tools",
    "register_reference_tools",
    "register_snapshot_tools",
    "register_describe_tools",
    "register_checkpoint_tools",
    "register_quick_tools",
]


def test_all_expected_exports_exist() -> None:
    for name in _EXPECTED_EXPORTS:
        assert hasattr(tools, name), f"tools module missing attribute: {name}"
        assert name in tools.__all__, f"tools.__all__ missing entry: {name}"
        assert callable(getattr(tools, name)), f"{name} is not callable"
