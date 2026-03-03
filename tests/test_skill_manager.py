"""Tests for SkillManager."""

from unittest.mock import MagicMock, patch

from blender_mcp.skill_manager import SKILL_DEFINITIONS, SkillInfo, SkillManager


def _make_mock_server():
    server = MagicMock()
    server.mcp = MagicMock()
    server.mcp.list_tools.return_value = []
    server.mcp.remove_tool = MagicMock()
    return server


class TestSkillDefinitions:
    def test_all_skills_have_required_fields(self):
        for name, info in SKILL_DEFINITIONS.items():
            assert info.name == name
            assert info.description
            assert len(info.modules) > 0

    def test_all_skill_modules_in_registry(self):
        from blender_mcp.tools_config import MODULE_REGISTRY

        for name, info in SKILL_DEFINITIONS.items():
            for mod in info.modules:
                assert mod in MODULE_REGISTRY, f"Skill '{name}' references unknown module '{mod}'"


class TestSkillManager:
    def test_initial_state(self):
        server = _make_mock_server()
        mgr = SkillManager(server)
        assert len(mgr.active_skills) == 0

    def test_unknown_skill(self):
        server = _make_mock_server()
        mgr = SkillManager(server)
        ok, msg, tools = mgr.activate_skill("nonexistent_skill_xyz")
        assert not ok
        assert "Unknown skill" in msg

    def test_deactivate_inactive_skill(self):
        server = _make_mock_server()
        mgr = SkillManager(server)
        ok, msg = mgr.deactivate_skill("modeling")
        assert not ok
        assert "not active" in msg

    def test_status_summary(self):
        server = _make_mock_server()
        mgr = SkillManager(server)
        summary = mgr.get_status_summary()
        assert "Skills Status" in summary
        for name in SKILL_DEFINITIONS:
            assert name in summary
