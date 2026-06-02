"""
Export Tools

Provides model and animation export features, supporting Unity, Web, and other platforms.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class ExportFBXInput(BaseModel):
    """FBX export input"""

    filepath: str = Field(..., description="Export file path (.fbx)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    apply_modifiers: bool = Field(default=True, description="Apply modifiers")
    include_animation: bool = Field(default=True, description="Include animation")
    bake_animation: bool = Field(default=False, description="Bake animation")
    use_mesh_modifiers: bool = Field(default=True, description="Apply mesh modifiers")
    use_armature_deform_only: bool = Field(default=False, description="Armature deform only")
    add_leaf_bones: bool = Field(default=False, description="Add leaf bones (not needed for Unity)")
    primary_bone_axis: str = Field(default="Y", description="Primary bone axis")
    secondary_bone_axis: str = Field(default="X", description="Secondary bone axis")
    apply_scale: str = Field(default="FBX_SCALE_ALL", description="Scale apply method")
    # --- Engine axis / transform control (Unity-oriented) ---
    unity_static_preset: bool = Field(
        default=False,
        description=(
            "Apply Unity static-prop settings: bake space transform (zeroed "
            "Transform on import, no -90deg X), Face smoothing, Mesh/Empty types. "
            "Use for non-rigged props/environments."
        ),
    )
    axis_forward: str = Field(default="-Z", description="Forward axis (Unity: -Z)")
    axis_up: str = Field(default="Y", description="Up axis (Unity: Y)")
    use_space_transform: bool = Field(default=True, description="Use space transform")
    bake_space_transform: bool = Field(
        default=False, description="Bake (apply) space transform; on by default under unity preset"
    )
    apply_unit_scale: bool = Field(default=True, description="Apply unit scale")
    mesh_smooth_type: str = Field(
        default="OFF", description="Smoothing: OFF/FACE/EDGE (preset uses FACE)"
    )
    object_types: list[str] | None = Field(
        default=None, description="FBX object types, e.g. ['MESH','EMPTY']; None = all"
    )
    path_mode: str = Field(default="AUTO", description="Texture path mode: AUTO/COPY/RELATIVE")
    zero_transform_for_export: bool = Field(
        default=True,
        description=(
            "Under bake_space_transform, auto-zero each exported object's .location "
            "for the export then restore it, so the prop imports into Unity at (0,0,0). "
            "Also warns on unapplied rotation/scale. Set False to export as-is."
        ),
    )


class VerifyFBXInput(BaseModel):
    """FBX verification input"""

    filepath: str = Field(..., description="Path to the FBX to verify")
    tri_budget: int | None = Field(
        default=None, description="Max allowed total triangles (None = no check)"
    )
    expect_origin: bool = Field(
        default=True, description="Assert every object imports at world origin (0,0,0)"
    )
    expect_single_object: bool = Field(
        default=True, description="Assert exactly one mesh object per file"
    )
    origin_epsilon: float = Field(default=1e-4, description="Tolerance for origin == (0,0,0)")


class ExportGLTFInput(BaseModel):
    """glTF export input"""

    filepath: str = Field(..., description="Export file path (.glb or .gltf)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    include_animation: bool = Field(default=True, description="Include animation")
    export_format: str = Field(default="GLB", description="Format: GLB or GLTF_SEPARATE")
    export_textures: bool = Field(default=True, description="Export textures")
    export_draco: bool = Field(default=False, description="Draco compression")


class ExportOBJInput(BaseModel):
    """OBJ export input"""

    filepath: str = Field(..., description="Export file path (.obj)")
    selected_only: bool = Field(default=False, description="Export selected objects only")
    apply_modifiers: bool = Field(default=True, description="Apply modifiers")
    export_materials: bool = Field(default=True, description="Export materials")


class ExportUnityPackageInput(BaseModel):
    """Unity package export input"""

    filepath: str = Field(..., description="Export file path")
    objects: list[str] | None = Field(default=None, description="List of objects to export")
    include_animations: bool = Field(default=True, description="Include animations")
    setup_humanoid: bool = Field(default=False, description="Set up as Humanoid type")
    generate_lod: bool = Field(default=False, description="Generate LOD")


# ==================== Tool Registration ====================


def register_export_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register export tools"""

    @mcp.tool(
        name="blender_export_fbx",
        annotations={
            "title": "Export FBX",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_export_fbx(params: ExportFBXInput) -> str:
        """Export as FBX format (suitable for Unity, Unreal, etc.).

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export",
            "fbx",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "include_animation": params.include_animation,
                "bake_animation": params.bake_animation,
                "use_mesh_modifiers": params.use_mesh_modifiers,
                "use_armature_deform_only": params.use_armature_deform_only,
                "add_leaf_bones": params.add_leaf_bones,
                "primary_bone_axis": params.primary_bone_axis,
                "secondary_bone_axis": params.secondary_bone_axis,
                "apply_scale": params.apply_scale,
                "unity_static_preset": params.unity_static_preset,
                "axis_forward": params.axis_forward,
                "axis_up": params.axis_up,
                "use_space_transform": params.use_space_transform,
                "bake_space_transform": params.bake_space_transform,
                "apply_unit_scale": params.apply_unit_scale,
                "mesh_smooth_type": params.mesh_smooth_type,
                "object_types": params.object_types,
                "path_mode": params.path_mode,
                "zero_transform_for_export": params.zero_transform_for_export,
            },
        )

        if result.get("success"):
            data = result.get("data") or {}
            extra = ""
            zeroed = data.get("zeroed_for_export") or []
            warns = data.get("warnings") or []
            if zeroed:
                extra += f" | zeroed .location for: {', '.join(zeroed)}"
            if warns:
                extra += " | WARNINGS: " + "; ".join(warns)
            return f"Successfully exported FBX to: {params.filepath}{extra}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_export_gltf",
        annotations={
            "title": "Export glTF",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_export_gltf(params: ExportGLTFInput) -> str:
        """Export as glTF format (suitable for Web, Three.js, etc.).

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export",
            "gltf",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "include_animation": params.include_animation,
                "export_format": params.export_format,
                "export_textures": params.export_textures,
                "export_draco": params.export_draco,
            },
        )

        if result.get("success"):
            return f"Successfully exported glTF to: {params.filepath}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_export_obj",
        annotations={
            "title": "Export OBJ",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_export_obj(params: ExportOBJInput) -> str:
        """Export as OBJ format.

        Args:
            params: Export settings

        Returns:
            Export result
        """
        result = await server.execute_command(
            "export",
            "obj",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "export_materials": params.export_materials,
            },
        )

        if result.get("success"):
            return f"Successfully exported OBJ to: {params.filepath}"
        else:
            return f"Export failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_verify_fbx",
        annotations={
            "title": "Verify FBX (engine-readiness QA)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_verify_fbx(params: VerifyFBXInput) -> str:
        """Re-import an exported FBX and assert game-engine readiness.

        Checks world origin == (0,0,0), triangle budget, one-object-per-file,
        and reports materials / emissive slots. Use after blender_export_fbx to
        self-verify each export instead of post-hoc bulk QA.

        Returns:
            PASS/FAIL with the per-object report.
        """
        result = await server.execute_command(
            "export",
            "verify_fbx",
            {
                "filepath": params.filepath,
                "tri_budget": params.tri_budget,
                "expect_origin": params.expect_origin,
                "expect_single_object": params.expect_single_object,
                "origin_epsilon": params.origin_epsilon,
            },
        )

        if not result.get("success"):
            return f"Verification error: {result.get('error', {}).get('message', 'Unknown error')}"

        data = result.get("data") or {}
        status = "PASS" if data.get("passed") else "FAIL"
        lines = [
            f"{status}: {params.filepath}",
            f"  objects={data.get('object_count')} total_triangles={data.get('total_triangles')}",
        ]
        for o in data.get("objects", []):
            emis = f" emissive={o['emissive_materials']}" if o.get("emissive_materials") else ""
            lines.append(
                f"  - {o['name']}: origin={o['world_origin']} tris={o['triangles']} "
                f"mats={o['materials']}{emis}"
            )
        for f in data.get("failures", []):
            lines.append(f"  ✗ {f}")
        return "\n".join(lines)
