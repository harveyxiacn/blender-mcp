"""Tests for SkillManager."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from blender_mcp.skill_manager import SKILL_DEFINITIONS, SkillManager


class _MockMCP:
    def __init__(self) -> None:
        self._tool_manager = SimpleNamespace(_tools={})


def _make_mock_server() -> MagicMock:
    server = MagicMock()
    server.mcp = _MockMCP()
    return server


class TestSkillDefinitions:
    def test_all_skills_have_required_fields(self) -> None:
        for name, info in SKILL_DEFINITIONS.items():
            assert info.name == name
            assert info.description
            assert len(info.modules) > 0

    def test_automation_skill_present(self) -> None:
        info = SKILL_DEFINITIONS["automation"]
        assert "pipeline" in info.modules
        assert "quality_audit" in info.modules

    def test_all_skill_modules_in_registry(self) -> None:
        from blender_mcp.tools_config import MODULE_REGISTRY

        for name, info in SKILL_DEFINITIONS.items():
            for mod in info.modules:
                assert mod in MODULE_REGISTRY, f"Skill '{name}' references unknown module '{mod}'"


class TestSkillManager:
    def test_initial_state(self) -> None:
        server = _make_mock_server()
        mgr = SkillManager(server)
        assert len(mgr.active_skills) == 0

    def test_unknown_skill(self) -> None:
        server = _make_mock_server()
        mgr = SkillManager(server)
        ok, msg, tools = mgr.activate_skill("nonexistent_skill_xyz")
        assert not ok
        assert "Unknown skill" in msg

    def test_deactivate_inactive_skill(self) -> None:
        server = _make_mock_server()
        mgr = SkillManager(server)
        ok, msg = mgr.deactivate_skill("modeling")
        assert not ok
        assert "not active" in msg

    def test_status_summary(self) -> None:
        server = _make_mock_server()
        mgr = SkillManager(server)
        summary = mgr.get_status_summary()
        assert "Skills Status" in summary
        for name in SKILL_DEFINITIONS:
            assert name in summary

    @patch("importlib.import_module")
    def test_activate_and_deactivate_skill_with_tool_manager(self, mocked_import) -> None:
        server = _make_mock_server()
        mgr = SkillManager(server)

        fake_module = MagicMock()

        def register_training_tools(mcp, _server) -> None:
            mcp._tool_manager._tools["blender_training_courses"] = object()
            mcp._tool_manager._tools["blender_training_start"] = object()

        fake_module.register_training_tools = register_training_tools
        mocked_import.return_value = fake_module

        ok, msg, tools = mgr.activate_skill("training")
        assert ok, msg
        assert set(tools) == {"blender_training_courses", "blender_training_start"}
        assert mgr.is_active("training")

        ok, msg = mgr.deactivate_skill("training")
        assert ok, msg
        assert "removed 2 tools" in msg
        assert "blender_training_courses" not in server.mcp._tool_manager._tools
        assert "blender_training_start" not in server.mcp._tool_manager._tools
