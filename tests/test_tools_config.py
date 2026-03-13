"""Tests for tools_config module."""

from blender_mcp.tools_config import (
    CORE_MODULES,
    FOCUSED_MODULES,
    FULL_MODULES,
    MINIMAL_MODULES,
    MODULE_REGISTRY,
    SKILL_MODULES,
    STANDARD_MODULES,
    get_enabled_modules,
)


def test_core_modules_subset_of_all_profiles() -> None:
    for mod in CORE_MODULES:
        assert mod in FULL_MODULES


def test_all_profile_modules_in_registry() -> None:
    for mod in FULL_MODULES:
        assert mod in MODULE_REGISTRY, f"{mod} missing from MODULE_REGISTRY"


def test_skill_modules_include_core() -> None:
    for mod in CORE_MODULES:
        assert mod in SKILL_MODULES


def test_minimal_equals_core() -> None:
    assert MINIMAL_MODULES == CORE_MODULES


def test_standard_includes_core() -> None:
    for mod in CORE_MODULES:
        assert mod in STANDARD_MODULES


def test_get_enabled_modules_returns_list() -> None:
    result = get_enabled_modules()
    assert isinstance(result, list)
    assert len(result) > 0


def test_no_duplicate_modules_in_full() -> None:
    assert len(FULL_MODULES) == len(set(FULL_MODULES)), "Duplicate modules in FULL_MODULES"


def test_automation_modules_in_registry() -> None:
    assert MODULE_REGISTRY["pipeline"] == "register_pipeline_tools"
    assert MODULE_REGISTRY["quality_audit"] == "register_quality_audit_tools"


def test_automation_modules_in_major_profiles() -> None:
    for profile_modules in (FOCUSED_MODULES, STANDARD_MODULES, FULL_MODULES):
        assert "pipeline" in profile_modules
        assert "quality_audit" in profile_modules
