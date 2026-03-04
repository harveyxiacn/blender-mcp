"""Regression tests for Principled BSDF helper usage in addon handlers."""

from pathlib import Path


HANDLERS = [
    "ai_generation.py",
    "character_template.py",
    "substance.py",
    "vr_ar.py",
    "zbrush.py",
]

HELPER_IMPORT = "from .node_utils import find_principled_bsdf as get_principled_bsdf"


def test_handlers_use_shared_principled_bsdf_helper():
    base = Path(__file__).resolve().parent.parent / "addon" / "blender_mcp_addon" / "handlers"

    for filename in HANDLERS:
        content = (base / filename).read_text(encoding="utf-8")
        assert HELPER_IMPORT in content, f"{filename} should import shared helper"
        assert "def get_principled_bsdf(" not in content, f"{filename} should not redefine helper"
