"""
Live Blender integration tests.

These tests require a running Blender instance with the MCP addon enabled.
Run with: pytest tests/test_blender_live.py -v --tb=short

Skip with: pytest tests/ --ignore=tests/test_blender_live.py
"""

import asyncio
import json
import logging
import sys

import pytest

# Add src to path so we can import the connection module
sys.path.insert(0, "src")

from blender_mcp.connection import BlenderConnection, BlenderConnectionError

logger = logging.getLogger(__name__)

# ============================================================
# Fixtures
# ============================================================

BLENDER_HOST = "127.0.0.1"
BLENDER_PORT = 9876


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def conn():
    """Create a shared connection to Blender for all tests."""
    c = BlenderConnection(host=BLENDER_HOST, port=BLENDER_PORT)
    try:
        await c.connect()
    except BlenderConnectionError:
        pytest.skip("Blender is not running or MCP addon is not enabled")
    yield c
    await c.disconnect()


async def send(conn: BlenderConnection, category: str, action: str, params: dict | None = None):
    """Helper to send a command and return the result."""
    result = await conn.send_command(category, action, params or {})
    return result


# ============================================================
# System Tests
# ============================================================


class TestSystem:
    async def test_get_info(self, conn):
        """Test system.get_info returns Blender version and scene info."""
        result = await send(conn, "system", "get_info")
        assert result.get("success"), f"get_info failed: {result}"
        data = result.get("data", {})
        assert "blender_version" in data or "version" in data, f"No version in: {data}"

    async def test_execute_python(self, conn):
        """Test executing simple Python code in Blender."""
        result = await send(
            conn,
            "utility",
            "execute_python",
            {"code": "import bpy; result = {'scene_name': bpy.context.scene.name}"},
        )
        assert result.get("success"), f"execute_python failed: {result}"


# ============================================================
# Scene Tests
# ============================================================


class TestScene:
    async def test_list(self, conn):
        result = await send(conn, "scene", "list")
        assert result.get("success"), f"scene.list failed: {result}"

    async def test_get_info(self, conn):
        result = await send(conn, "scene", "get_info", {})
        assert result.get("success"), f"scene.get_info failed: {result}"

    async def test_create_and_delete(self, conn):
        # Create
        result = await send(conn, "scene", "create", {"name": "TestScene_LiveTest"})
        assert result.get("success"), f"scene.create failed: {result}"
        # Delete
        result = await send(conn, "scene", "delete", {"name": "TestScene_LiveTest"})
        assert result.get("success"), f"scene.delete failed: {result}"


# ============================================================
# Object Tests
# ============================================================


class TestObject:
    async def test_list(self, conn):
        result = await send(conn, "object", "list", {})
        assert result.get("success"), f"object.list failed: {result}"

    async def test_create_cube(self, conn):
        result = await send(
            conn,
            "object",
            "create",
            {
                "type": "CUBE",
                "name": "TestCube_Live",
                "location": [0, 0, 0],
            },
        )
        assert result.get("success"), f"object.create CUBE failed: {result}"

    async def test_create_sphere(self, conn):
        result = await send(
            conn,
            "object",
            "create",
            {
                "type": "SPHERE",
                "name": "TestSphere_Live",
                "location": [3, 0, 0],
            },
        )
        assert result.get("success"), f"object.create SPHERE failed: {result}"

    async def test_create_cylinder(self, conn):
        result = await send(
            conn,
            "object",
            "create",
            {
                "type": "CYLINDER",
                "name": "TestCylinder_Live",
                "location": [6, 0, 0],
            },
        )
        assert result.get("success"), f"object.create CYLINDER failed: {result}"

    async def test_create_empty(self, conn):
        result = await send(
            conn,
            "object",
            "create",
            {
                "type": "EMPTY",
                "name": "TestEmpty_Live",
                "location": [0, 3, 0],
            },
        )
        assert result.get("success"), f"object.create EMPTY failed: {result}"

    async def test_transform(self, conn):
        result = await send(
            conn,
            "object",
            "transform",
            {
                "name": "TestCube_Live",
                "location": [1, 1, 1],
                "rotation": [0, 0, 45],
                "scale": [2, 2, 2],
            },
        )
        assert result.get("success"), f"object.transform failed: {result}"

    async def test_select(self, conn):
        result = await send(conn, "object", "select", {"name": "TestCube_Live"})
        assert result.get("success"), f"object.select failed: {result}"

    async def test_hide_and_show(self, conn):
        result = await send(conn, "object", "hide", {"name": "TestCube_Live", "hide": True})
        assert result.get("success"), f"object.hide failed: {result}"
        result = await send(conn, "object", "hide", {"name": "TestCube_Live", "hide": False})
        assert result.get("success"), f"object.show failed: {result}"

    async def test_delete(self, conn):
        for name in ["TestCube_Live", "TestSphere_Live", "TestCylinder_Live", "TestEmpty_Live"]:
            await send(conn, "object", "delete", {"name": name})
            # Don't assert - some may already be cleaned up


# ============================================================
# Modeling Tests
# ============================================================


class TestModeling:
    async def test_add_modifier(self, conn):
        # Create a test object first
        await send(
            conn,
            "object",
            "create",
            {"type": "CUBE", "name": "TestModeling_Live", "location": [0, 0, 0]},
        )
        result = await send(
            conn,
            "modeling",
            "add_modifier",
            {
                "object_name": "TestModeling_Live",
                "modifier_type": "SUBSURF",
                "name": "TestSubsurf",
            },
        )
        assert result.get("success"), f"modeling.add_modifier failed: {result}"

    async def test_apply_modifier(self, conn):
        result = await send(
            conn,
            "modeling",
            "apply_modifier",
            {
                "object_name": "TestModeling_Live",
                "modifier_name": "TestSubsurf",
            },
        )
        assert result.get("success"), f"modeling.apply_modifier failed: {result}"

    async def test_set_smooth(self, conn):
        result = await send(
            conn,
            "modeling",
            "set_smooth",
            {
                "object_name": "TestModeling_Live",
                "smooth": True,
            },
        )
        assert result.get("success"), f"modeling.set_smooth failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestModeling_Live"})


# ============================================================
# Material Tests
# ============================================================


class TestMaterial:
    async def test_create_material(self, conn):
        await send(
            conn,
            "object",
            "create",
            {"type": "CUBE", "name": "TestMat_Live", "location": [0, 0, 0]},
        )
        result = await send(
            conn,
            "material",
            "create",
            {
                "name": "TestMaterial_Live",
                "base_color": [1.0, 0.0, 0.0, 1.0],
            },
        )
        assert result.get("success"), f"material.create failed: {result}"

    async def test_assign_material(self, conn):
        result = await send(
            conn,
            "material",
            "assign",
            {
                "object_name": "TestMat_Live",
                "material_name": "TestMaterial_Live",
            },
        )
        assert result.get("success"), f"material.assign failed: {result}"

    async def test_list_materials(self, conn):
        result = await send(conn, "material", "list", {})
        assert result.get("success"), f"material.list failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestMat_Live"})


# ============================================================
# Lighting Tests
# ============================================================


class TestLighting:
    async def test_create_point_light(self, conn):
        result = await send(
            conn,
            "lighting",
            "create",
            {
                "type": "POINT",
                "name": "TestLight_Live",
                "location": [0, 0, 5],
                "energy": 100.0,
            },
        )
        assert result.get("success"), f"lighting.create POINT failed: {result}"

    async def test_create_sun_light(self, conn):
        result = await send(
            conn,
            "lighting",
            "create",
            {
                "type": "SUN",
                "name": "TestSun_Live",
                "location": [0, 0, 10],
                "energy": 5.0,
            },
        )
        assert result.get("success"), f"lighting.create SUN failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestLight_Live"})
        await send(conn, "object", "delete", {"name": "TestSun_Live"})


# ============================================================
# Camera Tests
# ============================================================


class TestCamera:
    async def test_create_camera(self, conn):
        result = await send(
            conn,
            "camera",
            "create",
            {
                "name": "TestCamera_Live",
                "location": [7, -7, 5],
                "focal_length": 50.0,
            },
        )
        assert result.get("success"), f"camera.create failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestCamera_Live"})


# ============================================================
# Animation Tests
# ============================================================


class TestAnimation:
    async def test_insert_keyframe(self, conn):
        await send(
            conn,
            "object",
            "create",
            {"type": "CUBE", "name": "TestAnim_Live", "location": [0, 0, 0]},
        )
        result = await send(
            conn,
            "animation",
            "insert_keyframe",
            {
                "object_name": "TestAnim_Live",
                "data_path": "location",
                "frame": 1,
            },
        )
        assert result.get("success"), f"animation.insert_keyframe failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestAnim_Live"})


# ============================================================
# World Tests
# ============================================================


class TestWorld:
    async def test_get_settings(self, conn):
        result = await send(conn, "world", "get_settings", {})
        assert result.get("success"), f"world.get_settings failed: {result}"

    async def test_set_background(self, conn):
        result = await send(
            conn,
            "world",
            "set_background",
            {
                "color": [0.05, 0.05, 0.1],
            },
        )
        assert result.get("success"), f"world.set_background failed: {result}"


# ============================================================
# Render Tests
# ============================================================


class TestRender:
    async def test_get_settings(self, conn):
        result = await send(conn, "render", "get_settings", {})
        assert result.get("success"), f"render.get_settings failed: {result}"

    async def test_set_engine(self, conn):
        result = await send(
            conn,
            "render",
            "set_engine",
            {
                "engine": "CYCLES",
            },
        )
        assert result.get("success"), f"render.set_engine failed: {result}"
        # Reset to EEVEE for speed
        await send(conn, "render", "set_engine", {"engine": "BLENDER_EEVEE_NEXT"})


# ============================================================
# Curves Tests
# ============================================================


class TestCurves:
    async def test_create_bezier(self, conn):
        result = await send(
            conn,
            "curves",
            "create",
            {
                "type": "BEZIER",
                "name": "TestCurve_Live",
            },
        )
        assert result.get("success"), f"curves.create failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestCurve_Live"})


# ============================================================
# UV Tests
# ============================================================


class TestUV:
    async def test_unwrap(self, conn):
        await send(
            conn, "object", "create", {"type": "CUBE", "name": "TestUV_Live", "location": [0, 0, 0]}
        )
        result = await send(
            conn,
            "uv",
            "unwrap",
            {
                "object_name": "TestUV_Live",
            },
        )
        assert result.get("success"), f"uv.unwrap failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestUV_Live"})


# ============================================================
# Physics Tests
# ============================================================


class TestPhysics:
    async def test_add_rigid_body(self, conn):
        await send(
            conn,
            "object",
            "create",
            {"type": "CUBE", "name": "TestPhysics_Live", "location": [0, 0, 5]},
        )
        result = await send(
            conn,
            "physics",
            "add",
            {
                "object_name": "TestPhysics_Live",
                "physics_type": "RIGID_BODY",
            },
        )
        assert result.get("success"), f"physics.add failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestPhysics_Live"})


# ============================================================
# Constraints Tests
# ============================================================


class TestConstraints:
    async def test_add_constraint(self, conn):
        await send(
            conn,
            "object",
            "create",
            {"type": "CUBE", "name": "TestConstraint_Live", "location": [0, 0, 0]},
        )
        await send(
            conn,
            "object",
            "create",
            {"type": "EMPTY", "name": "TestConstraintTarget_Live", "location": [5, 0, 0]},
        )
        result = await send(
            conn,
            "constraints",
            "add",
            {
                "object_name": "TestConstraint_Live",
                "constraint_type": "COPY_LOCATION",
                "target": "TestConstraintTarget_Live",
            },
        )
        assert result.get("success"), f"constraints.add failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestConstraint_Live"})
        await send(conn, "object", "delete", {"name": "TestConstraintTarget_Live"})


# ============================================================
# Nodes Tests
# ============================================================


class TestNodes:
    async def test_list_nodes(self, conn):
        # Ensure there's a material to list nodes from
        await send(
            conn,
            "material",
            "create",
            {
                "name": "TestNodeMat_Live",
                "base_color": [0.5, 0.5, 0.5, 1.0],
            },
        )
        result = await send(
            conn,
            "nodes",
            "list",
            {
                "material_name": "TestNodeMat_Live",
            },
        )
        assert result.get("success"), f"nodes.list failed: {result}"


# ============================================================
# Export Tests
# ============================================================


class TestExport:
    async def test_list_formats(self, conn):
        result = await send(conn, "export", "list_formats", {})
        assert result.get("success"), f"export.list_formats failed: {result}"


# ============================================================
# Batch Tests
# ============================================================


class TestBatch:
    async def test_list(self, conn):
        result = await send(conn, "batch", "list", {})
        assert result.get("success"), f"batch.list failed: {result}"


# ============================================================
# Assets Tests
# ============================================================


class TestAssets:
    async def test_list(self, conn):
        result = await send(conn, "assets", "list", {})
        assert result.get("success"), f"assets.list failed: {result}"


# ============================================================
# Character Template Tests
# ============================================================


class TestCharacterTemplate:
    async def test_list_templates(self, conn):
        result = await send(conn, "character_template", "list", {})
        assert result.get("success"), f"character_template.list failed: {result}"


# ============================================================
# Rigging Tests
# ============================================================


class TestRigging:
    async def test_create_armature(self, conn):
        result = await send(
            conn,
            "rigging",
            "create_armature",
            {
                "name": "TestArmature_Live",
                "location": [0, 0, 0],
            },
        )
        assert result.get("success"), f"rigging.create_armature failed: {result}"

    async def test_cleanup(self, conn):
        await send(conn, "object", "delete", {"name": "TestArmature_Live"})


# ============================================================
# Addons Tests
# ============================================================


class TestAddons:
    async def test_list(self, conn):
        result = await send(conn, "addons", "list", {})
        assert result.get("success"), f"addons.list failed: {result}"


# ============================================================
# Preferences Tests
# ============================================================


class TestPreferences:
    async def test_get(self, conn):
        result = await send(conn, "preferences", "get", {})
        assert result.get("success"), f"preferences.get failed: {result}"


# ============================================================
# Versioning Tests
# ============================================================


class TestVersioning:
    async def test_get_info(self, conn):
        result = await send(conn, "versioning", "get_info", {})
        assert result.get("success"), f"versioning.get_info failed: {result}"


# ============================================================
# Scene Advanced Tests
# ============================================================


class TestSceneAdvanced:
    async def test_get_stats(self, conn):
        result = await send(conn, "scene_advanced", "get_stats", {})
        assert result.get("success"), f"scene_advanced.get_stats failed: {result}"


# ============================================================
# Utility Tests
# ============================================================


class TestUtility:
    async def test_undo(self, conn):
        result = await send(conn, "utility", "undo", {})
        # Undo may fail if nothing to undo, that's OK
        assert "success" in result or "error" in result

    async def test_get_system_info(self, conn):
        result = await send(conn, "utility", "get_system_info", {})
        assert result.get("success"), f"utility.get_system_info failed: {result}"


# ============================================================
# Comprehensive Handler Coverage Test
# ============================================================


class TestHandlerCoverage:
    """Test that every registered handler can be loaded and has basic actions."""

    HANDLER_BASIC_ACTIONS = {
        "scene": ("list", {}),
        "object": ("list", {}),
        "modeling": ("list_modifiers", {"object_name": "__skip_if_no_object__"}),
        "material": ("list", {}),
        "lighting": ("list", {}),
        "camera": ("list", {}),
        "animation": ("list_actions", {}),
        "render": ("get_settings", {}),
        "utility": ("get_system_info", {}),
        "export": ("list_formats", {}),
        "world": ("get_settings", {}),
        "addons": ("list", {}),
        "preferences": ("get", {}),
        "scene_advanced": ("get_stats", {}),
        "versioning": ("get_info", {}),
        "batch": ("list", {}),
        "assets": ("list", {}),
        "character_template": ("list", {}),
        "constraints": ("list", {}),
        "nodes": ("list", {"material_name": "TestNodeMat_Live"}),
        "curves": ("list", {}),
        "uv": ("list", {}),
        "physics": ("list", {}),
    }

    @pytest.mark.parametrize(
        "category,action_params",
        list(HANDLER_BASIC_ACTIONS.items()),
        ids=list(HANDLER_BASIC_ACTIONS.keys()),
    )
    async def test_handler_responds(self, conn, category, action_params):
        action, params = action_params
        result = await send(conn, category, action, params)
        # We just need the handler to respond without crashing
        assert isinstance(result, dict), f"{category}.{action} returned non-dict: {result}"
        # Success or a structured error is fine - we're testing the handler loads
        assert (
            "success" in result or "error" in result
        ), f"{category}.{action} returned unexpected structure: {result}"


# ============================================================
# Final Cleanup
# ============================================================


class TestFinalCleanup:
    """Clean up all test objects at the end."""

    async def test_cleanup_all(self, conn):
        """Remove any leftover test objects."""
        result = await send(conn, "object", "list", {})
        if result.get("success"):
            objects = result.get("data", {}).get("objects", [])
            for obj in objects:
                name = obj if isinstance(obj, str) else obj.get("name", "")
                if "_Live" in name or "_LiveTest" in name:
                    await send(conn, "object", "delete", {"name": name})
