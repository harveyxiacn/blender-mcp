"""
UV Mapping Tools

Provides UV unwrapping, projection, editing, and related functionality.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class UVUnwrapInput(BaseModel):
    """UV unwrap input"""

    object_name: str = Field(..., description="Object name")
    method: str = Field(default="ANGLE_BASED", description="Unwrap method: ANGLE_BASED, CONFORMAL")
    fill_holes: bool = Field(default=True, description="Fill holes")
    correct_aspect: bool = Field(default=True, description="Correct aspect ratio")


class UVProjectInput(BaseModel):
    """UV projection input"""

    object_name: str = Field(..., description="Object name")
    projection_type: str = Field(
        default="CUBE", description="Projection type: CUBE, CYLINDER, SPHERE, VIEW"
    )
    scale_to_bounds: bool = Field(default=True, description="Scale to bounds")


class UVSmartProjectInput(BaseModel):
    """Smart UV projection input"""

    object_name: str = Field(..., description="Object name")
    angle_limit: float = Field(default=66.0, description="Angle limit (degrees)", ge=0, le=89)
    island_margin: float = Field(default=0.0, description="Island margin", ge=0, le=1)
    area_weight: float = Field(default=0.0, description="Area weight", ge=0, le=1)


class UVPackInput(BaseModel):
    """UV pack input"""

    object_name: str = Field(..., description="Object name")
    margin: float = Field(default=0.001, description="Margin", ge=0, le=1)
    rotate: bool = Field(default=True, description="Allow rotation")


class UVSeamInput(BaseModel):
    """UV seam input"""

    object_name: str = Field(..., description="Object name")
    action: str = Field(default="mark", description="Action: mark, clear")
    edge_indices: list[int] | None = Field(default=None, description="Edge index list")
    from_sharp: bool = Field(default=False, description="Mark from sharp edges")


class UVTransformInput(BaseModel):
    """UV transform input"""

    object_name: str = Field(..., description="Object name")
    translate: list[float] | None = Field(default=None, description="Translation [U, V]")
    rotate: float | None = Field(default=None, description="Rotation (degrees)")
    scale: list[float] | None = Field(default=None, description="Scale [U, V]")


# ==================== Production-Standard Optimization Input Models ====================


class TextureResolution(str, Enum):
    """Texture resolution"""

    RES_256 = "256"
    RES_512 = "512"
    RES_1024 = "1024"
    RES_2048 = "2048"
    RES_4096 = "4096"


class UVAnalyzeInput(BaseModel):
    """UV analysis input"""

    object_name: str = Field(..., description="Object name")
    texture_resolution: TextureResolution = Field(
        default=TextureResolution.RES_1024,
        description="Target texture resolution (used for pixel density calculation)",
    )


class UVOptimizeInput(BaseModel):
    """UV optimization input"""

    object_name: str = Field(..., description="Object name")
    target_margin: float = Field(default=0.01, description="Target margin", ge=0, le=0.1)
    straighten_uvs: bool = Field(default=True, description="Attempt to straighten UVs")
    minimize_stretch: bool = Field(default=True, description="Minimize stretch")
    pack_efficiently: bool = Field(default=True, description="Pack efficiently")


class UVDensityInput(BaseModel):
    """UV density normalization input"""

    object_name: str = Field(..., description="Object name")
    target_density: float | None = Field(
        default=None, description="Target density (pixels/unit), None uses average density"
    )
    texture_resolution: TextureResolution = Field(
        default=TextureResolution.RES_1024, description="Target texture resolution"
    )


class TextureAtlasCreateInput(BaseModel):
    """Create texture atlas input"""

    object_names: list[str] = Field(..., description="Object name list")
    atlas_name: str = Field(default="TextureAtlas", description="Atlas name")
    resolution: TextureResolution = Field(
        default=TextureResolution.RES_2048, description="Atlas resolution"
    )
    margin: float = Field(default=0.01, description="UV island margin", ge=0, le=0.1)


class UVAutoSeamInput(BaseModel):
    """Auto seam input"""

    object_name: str = Field(..., description="Object name")
    angle_threshold: float = Field(
        default=30.0, description="Angle threshold (degrees)", ge=0, le=90
    )
    use_hard_edges: bool = Field(default=True, description="Use hard edges as seams")
    optimize_for_deformation: bool = Field(
        default=False, description="Optimize for deformation areas"
    )


class UVGridCheckInput(BaseModel):
    """UV checker grid input"""

    object_name: str = Field(..., description="Object name")
    grid_size: int = Field(default=8, description="Checker grid count", ge=2, le=64)


# ==================== Tool Registration ====================


def register_uv_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register UV mapping tools"""

    @mcp.tool(
        name="blender_uv_unwrap",
        annotations={
            "title": "UV Unwrap",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_unwrap(params: UVUnwrapInput) -> str:
        """Automatic UV unwrap.

        Args:
            params: Object name, unwrap method, etc.

        Returns:
            Unwrap result
        """
        result = await server.execute_command(
            "uv",
            "unwrap",
            {
                "object_name": params.object_name,
                "method": params.method,
                "fill_holes": params.fill_holes,
                "correct_aspect": params.correct_aspect,
            },
        )

        if result.get("success"):
            return f"Successfully unwrapped UV for '{params.object_name}'"
        else:
            return f"Unwrap failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_project",
        annotations={
            "title": "UV Projection",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_project(params: UVProjectInput) -> str:
        """UV projection mapping (cube, cylinder, sphere).

        Args:
            params: Object name, projection type

        Returns:
            Projection result
        """
        result = await server.execute_command(
            "uv",
            "project",
            {
                "object_name": params.object_name,
                "projection_type": params.projection_type,
                "scale_to_bounds": params.scale_to_bounds,
            },
        )

        if result.get("success"):
            return f"Successfully applied {params.projection_type} projection to '{params.object_name}'"
        else:
            return f"Projection failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_smart_project",
        annotations={
            "title": "Smart UV Project",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_smart_project(params: UVSmartProjectInput) -> str:
        """Smart UV projection (automatic island splitting).

        Args:
            params: Object name, angle limit, margin

        Returns:
            Projection result
        """
        result = await server.execute_command(
            "uv",
            "smart_project",
            {
                "object_name": params.object_name,
                "angle_limit": params.angle_limit,
                "island_margin": params.island_margin,
                "area_weight": params.area_weight,
            },
        )

        if result.get("success"):
            return f"Successfully applied smart UV projection to '{params.object_name}'"
        else:
            return f"Projection failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_pack",
        annotations={
            "title": "UV Pack",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_uv_pack(params: UVPackInput) -> str:
        """Optimize UV island layout.

        Args:
            params: Object name, margin, whether to rotate

        Returns:
            Pack result
        """
        result = await server.execute_command(
            "uv",
            "pack",
            {"object_name": params.object_name, "margin": params.margin, "rotate": params.rotate},
        )

        if result.get("success"):
            return f"Successfully packed UV for '{params.object_name}'"
        else:
            return f"Pack failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_seam",
        annotations={
            "title": "UV Seam",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_uv_seam(params: UVSeamInput) -> str:
        """Mark or clear UV seams.

        Args:
            params: Object name, action type

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "uv",
            "seam",
            {
                "object_name": params.object_name,
                "action": params.action,
                "edge_indices": params.edge_indices,
                "from_sharp": params.from_sharp,
            },
        )

        if result.get("success"):
            return f"Successfully performed {params.action} on UV seams"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_transform",
        annotations={
            "title": "UV Transform",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_uv_transform(params: UVTransformInput) -> str:
        """Transform UV coordinates.

        Args:
            params: Object name, translation, rotation, scale

        Returns:
            Transform result
        """
        result = await server.execute_command(
            "uv",
            "transform",
            {
                "object_name": params.object_name,
                "translate": params.translate,
                "rotate": params.rotate,
                "scale": params.scale,
            },
        )

        if result.get("success"):
            return f"Successfully transformed UV for '{params.object_name}'"
        else:
            return f"Transform failed: {result.get('error', {}).get('message', 'Unknown error')}"

    # ==================== Production-Standard Optimization Tools ====================

    @mcp.tool(
        name="blender_uv_analyze",
        annotations={
            "title": "UV Quality Analysis",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_uv_analyze(params: UVAnalyzeInput) -> str:
        """Analyze UV mapping quality.

        Checks UV quality metrics:
        - Stretch/distortion level
        - Island count and distribution
        - UV space utilization
        - Pixel density consistency
        - Overlap detection

        Args:
            params: Object name and target texture resolution

        Returns:
            Detailed UV analysis report
        """
        result = await server.execute_command(
            "uv",
            "analyze",
            {
                "object_name": params.object_name,
                "texture_resolution": int(params.texture_resolution.value),
            },
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"# UV Analysis Report: {params.object_name}", ""]

            # Basic statistics
            lines.append("## Basic Statistics")
            lines.append(f"- UV Layer Count: {data.get('uv_layer_count', 'N/A')}")
            lines.append(f"- Island Count: {data.get('island_count', 'N/A')}")
            lines.append(f"- UV Space Utilization: {data.get('space_usage', 0):.1f}%")
            lines.append("")

            # Quality metrics
            lines.append("## Quality Metrics")
            lines.append(f"- Average Stretch: {data.get('avg_stretch', 0):.3f}")
            lines.append(f"- Maximum Stretch: {data.get('max_stretch', 0):.3f}")
            lines.append(f"- Overlapping Faces: {data.get('overlapping_faces', 0)}")
            lines.append("")

            # Pixel density
            density = data.get("pixel_density", {})
            lines.append(
                f"## Pixel Density (based on {params.texture_resolution.value}x{params.texture_resolution.value} texture)"
            )
            lines.append(f"- Average Density: {density.get('average', 0):.1f} pixels/unit")
            lines.append(f"- Minimum Density: {density.get('min', 0):.1f} pixels/unit")
            lines.append(f"- Maximum Density: {density.get('max', 0):.1f} pixels/unit")
            lines.append(f"- Density Variance: {density.get('variance', 0):.1f}%")
            lines.append("")

            # Issues and suggestions
            issues = data.get("issues", [])
            if issues:
                lines.append("## Issues Found")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")

            # Score
            score = data.get("quality_score", 0)
            lines.append(f"## UV Quality Score: {score}/100")

            return "\n".join(lines)
        else:
            return f"Analysis failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_optimize",
        annotations={
            "title": "Optimize UV Layout",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_optimize(params: UVOptimizeInput) -> str:
        """Optimize UV layout to meet production standards.

        Automatically performs the following optimizations:
        - Minimize UV stretch
        - Efficiently pack UV islands
        - Optimize UV space utilization
        - Set appropriate island margins

        Args:
            params: Object name and optimization options

        Returns:
            Optimization result
        """
        result = await server.execute_command(
            "uv",
            "optimize",
            {
                "object_name": params.object_name,
                "target_margin": params.target_margin,
                "straighten_uvs": params.straighten_uvs,
                "minimize_stretch": params.minimize_stretch,
                "pack_efficiently": params.pack_efficiently,
            },
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"UV optimization complete: {params.object_name}", ""]
            lines.append(
                f"- Space Utilization: {data.get('old_usage', 0):.1f}% -> {data.get('new_usage', 0):.1f}%"
            )
            lines.append(
                f"- Average Stretch: {data.get('old_stretch', 0):.3f} -> {data.get('new_stretch', 0):.3f}"
            )

            return "\n".join(lines)
        else:
            return f"Optimization failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_density_normalize",
        annotations={
            "title": "Normalize UV Density",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_density_normalize(params: UVDensityInput) -> str:
        """Normalize UV pixel density.

        Ensures all UV islands have consistent pixel density, which is critical for:
        - Game asset quality consistency
        - Avoiding blurry or overly sharp texture areas
        - Meeting game engine LOD requirements

        Args:
            params: Object name and target density settings

        Returns:
            Normalization result
        """
        result = await server.execute_command(
            "uv",
            "density_normalize",
            {
                "object_name": params.object_name,
                "target_density": params.target_density,
                "texture_resolution": int(params.texture_resolution.value),
            },
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"UV density normalization complete: {params.object_name}", ""]
            lines.append(f"- Target Density: {data.get('target_density', 0):.1f} pixels/unit")
            lines.append(f"- Adjusted Islands: {data.get('adjusted_islands', 0)}")

            return "\n".join(lines)
        else:
            return (
                f"Normalization failed: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_texture_atlas_create",
        annotations={
            "title": "Create Texture Atlas",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_texture_atlas_create(params: TextureAtlasCreateInput) -> str:
        """Create a texture atlas for multiple objects.

        Merges UV of multiple objects into a single texture space, which is useful for:
        - Reducing draw calls and improving rendering performance
        - Mobile game optimization
        - Batch rendering of static scenes

        Args:
            params: Object list, atlas name, and settings

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "uv",
            "create_atlas",
            {
                "object_names": params.object_names,
                "atlas_name": params.atlas_name,
                "resolution": int(params.resolution.value),
                "margin": params.margin,
            },
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"Texture atlas created successfully: {params.atlas_name}", ""]
            lines.append(f"- Resolution: {params.resolution.value}x{params.resolution.value}")
            lines.append(f"- Objects Included: {len(params.object_names)}")
            lines.append(f"- UV Space Utilization: {data.get('space_usage', 0):.1f}%")

            return "\n".join(lines)
        else:
            return (
                f"Atlas creation failed: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_uv_auto_seam",
        annotations={
            "title": "Auto UV Seam",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_uv_auto_seam(params: UVAutoSeamInput) -> str:
        """Intelligent automatic UV seam marking.

        Automatically generates optimal seams based on geometric features:
        - Detects hard edges based on angle threshold
        - Considers model topology
        - Optional optimization for deformation (character animation)

        Args:
            params: Object name and seam options

        Returns:
            Seam marking result
        """
        result = await server.execute_command(
            "uv",
            "auto_seam",
            {
                "object_name": params.object_name,
                "angle_threshold": params.angle_threshold,
                "use_hard_edges": params.use_hard_edges,
                "optimize_for_deformation": params.optimize_for_deformation,
            },
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"Auto seam complete: {params.object_name}", ""]
            lines.append(f"- Seam Edges Marked: {data.get('seam_count', 0)}")
            lines.append(f"- Estimated Islands: {data.get('estimated_islands', 0)}")

            return "\n".join(lines)
        else:
            return f"Auto seam failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_uv_grid_check",
        annotations={
            "title": "UV Checker Grid",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_uv_grid_check(params: UVGridCheckInput) -> str:
        """Apply checker grid texture for UV quality inspection.

        Creates and applies a checker material for visual inspection of:
        - UV stretch and distortion
        - Pixel density consistency
        - Seam placement

        Args:
            params: Object name and checker grid parameters

        Returns:
            Check result
        """
        result = await server.execute_command(
            "uv", "grid_check", {"object_name": params.object_name, "grid_size": params.grid_size}
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Applied checker grid material '{data.get('material_name', 'UV_Checker')}' to '{params.object_name}'"
        else:
            return f"Check failed: {result.get('error', {}).get('message', 'Unknown error')}"
