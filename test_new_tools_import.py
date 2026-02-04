#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test import of new tools

Verify that all newly added MCP tools can be imported correctly.
"""

import sys
import traceback


def test_tools_import():
    """Test tools module import"""
    print("=" * 60)
    print("Test MCP Tools Import")
    print("=" * 60)
    
    errors = []
    
    # Test object tools
    try:
        from blender_mcp.tools.object import (
            ObjectSetOriginInput,
            ObjectApplyTransformInput,
            OriginType,
        )
        print("[OK] object.py: ObjectSetOriginInput, ObjectApplyTransformInput, OriginType")
    except Exception as e:
        errors.append(f"object.py: {e}")
        print(f"[FAIL] object.py: {e}")
    
    # Test modeling tools (Shape Keys)
    try:
        from blender_mcp.tools.modeling import (
            ShapeKeyCreateInput,
            ShapeKeyEditInput,
            ShapeKeyDeleteInput,
            ShapeKeyListInput,
            ShapeKeyCreateExpressionInput,
            MeshAssignMaterialToFacesInput,
            SelectFacesByMaterialInput,
        )
        print("[OK] modeling.py: ShapeKey* and MeshAssignMaterialToFacesInput")
    except Exception as e:
        errors.append(f"modeling.py: {e}")
        print(f"[FAIL] modeling.py: {e}")
    
    # Test rigging tools
    try:
        from blender_mcp.tools.rigging import (
            ArmatureBindInput,
            BindType,
            VertexGroupCreateInput,
            VertexGroupAssignInput,
            BoneConstraintAddInput,
        )
        print("[OK] rigging.py: ArmatureBindInput, VertexGroupCreateInput, etc.")
    except Exception as e:
        errors.append(f"rigging.py: {e}")
        print(f"[FAIL] rigging.py: {e}")
    
    # Test material tools
    try:
        from blender_mcp.tools.material import (
            MaterialNodeAddInput,
            NodeType,
            TextureApplyInput,
            CreateSkinMaterialInput,
            CreateToonMaterialInput,
        )
        print("[OK] material.py: MaterialNodeAddInput, TextureApplyInput, etc.")
    except Exception as e:
        errors.append(f"material.py: {e}")
        print(f"[FAIL] material.py: {e}")
    
    # Test animation tools
    try:
        from blender_mcp.tools.animation import (
            ActionCreateInput,
            ActionCreateFromPosesInput,
            ActionListInput,
            ActionAssignInput,
            NLAPushActionInput,
        )
        print("[OK] animation.py: ActionCreateInput, ActionCreateFromPosesInput, etc.")
    except Exception as e:
        errors.append(f"animation.py: {e}")
        print(f"[FAIL] animation.py: {e}")
    
    print()
    print("=" * 60)
    
    if errors:
        print(f"Import test failed, {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("All tools modules imported successfully!")
        return True


def test_register_functions():
    """Test tool registration functions"""
    print()
    print("=" * 60)
    print("Test Tool Registration Functions")
    print("=" * 60)
    
    errors = []
    
    modules = [
        ("object", "register_object_tools"),
        ("modeling", "register_modeling_tools"),
        ("material", "register_material_tools"),
        ("rigging", "register_rigging_tools"),
        ("animation", "register_animation_tools"),
    ]
    
    for module_name, func_name in modules:
        try:
            module = __import__(f"blender_mcp.tools.{module_name}", fromlist=[func_name])
            func = getattr(module, func_name)
            print(f"[OK] {module_name}.py: {func_name}")
        except Exception as e:
            errors.append(f"{module_name}.py: {e}")
            print(f"[FAIL] {module_name}.py: {e}")
    
    print()
    print("=" * 60)
    
    if errors:
        print(f"Registration function test failed, {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("All registration functions test passed!")
        return True


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Blender MCP New Tools Import Test")
    print("=" * 60 + "\n")
    
    # Add src directory to path
    import os
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    success = True
    
    try:
        if not test_tools_import():
            success = False
    except Exception as e:
        print(f"Tools import test failed: {e}")
        traceback.print_exc()
        success = False
    
    try:
        if not test_register_functions():
            success = False
    except Exception as e:
        print(f"Registration function test failed: {e}")
        traceback.print_exc()
        success = False
    
    print()
    print("=" * 60)
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed, please check above errors.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
