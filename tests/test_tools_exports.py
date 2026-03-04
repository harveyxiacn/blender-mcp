"""Tests for top-level tool exports."""

from blender_mcp import tools


def test_pipeline_and_quality_audit_exports_exist():
    assert hasattr(tools, "register_pipeline_tools")
    assert hasattr(tools, "register_quality_audit_tools")
    assert "register_pipeline_tools" in tools.__all__
    assert "register_quality_audit_tools" in tools.__all__
