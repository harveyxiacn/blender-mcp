"""
Curve Modeling Tools

Provides curve creation, editing, conversion, and more.
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class CurveCreateInput(BaseModel):
    """Create curve input"""
    curve_type: str = Field(
        default="BEZIER",
        description="Curve type: BEZIER, NURBS, POLY"
    )
    name: str = Field(default="Curve", description="Curve name")
    points: List[List[float]] = Field(..., description="Control point list [[x,y,z], ...]")
    cyclic: bool = Field(default=False, description="Closed curve")
    location: Optional[List[float]] = Field(default=None, description="Location")


class CurveCircleInput(BaseModel):
    """Create circle curve input"""
    name: str = Field(default="Circle", description="Name")
    radius: float = Field(default=1.0, description="Radius", ge=0.001)
    location: Optional[List[float]] = Field(default=None, description="Location")
    fill_mode: str = Field(default="NONE", description="Fill: NONE, FRONT, BACK, BOTH")


class CurvePathInput(BaseModel):
    """Create path curve input"""
    name: str = Field(default="Path", description="Name")
    length: float = Field(default=4.0, description="Length", ge=0.1)
    points_count: int = Field(default=5, description="Point count", ge=2)
    location: Optional[List[float]] = Field(default=None, description="Location")


class CurveSpiralInput(BaseModel):
    """Create spiral curve input"""
    name: str = Field(default="Spiral", description="Name")
    turns: float = Field(default=2.0, description="Number of turns", ge=0.1)
    radius: float = Field(default=1.0, description="Radius", ge=0.001)
    height: float = Field(default=2.0, description="Height")
    location: Optional[List[float]] = Field(default=None, description="Location")


class CurveToMeshInput(BaseModel):
    """Curve to mesh input"""
    curve_name: str = Field(..., description="Curve name")
    resolution: int = Field(default=12, description="Resolution", ge=1, le=64)
    keep_original: bool = Field(default=False, description="Keep original curve")


class CurveExtrudeInput(BaseModel):
    """Curve extrude input"""
    curve_name: str = Field(..., description="Curve name")
    depth: float = Field(default=0.1, description="Extrude depth", ge=0)
    bevel_depth: float = Field(default=0.0, description="Bevel depth", ge=0)
    bevel_resolution: int = Field(default=0, description="Bevel resolution", ge=0)


class CurveProfileInput(BaseModel):
    """Sweep profile along curve input"""
    path_curve: str = Field(..., description="Path curve name")
    profile_curve: str = Field(..., description="Profile curve name")
    name: str = Field(default="Sweep", description="Result name")


class CurveTextInput(BaseModel):
    """Create text curve input"""
    text: str = Field(..., description="Text content")
    name: str = Field(default="Text", description="Name")
    font_size: float = Field(default=1.0, description="Font size", ge=0.01)
    extrude: float = Field(default=0.0, description="Extrude depth", ge=0)
    location: Optional[List[float]] = Field(default=None, description="Location")


# ==================== Tool Registration ====================

def register_curve_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register curve modeling tools"""

    @mcp.tool(
        name="blender_curve_create",
        annotations={
            "title": "Create Curve",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_create(params: CurveCreateInput) -> str:
        """Create a curve from control points.

        Args:
            params: Curve type, control points, whether to close, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "curves", "create",
            {
                "curve_type": params.curve_type,
                "name": params.name,
                "points": params.points,
                "cyclic": params.cyclic,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            return f"Successfully created {params.curve_type} curve '{params.name}' ({len(params.points)} points)"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_circle",
        annotations={
            "title": "Create Circle Curve",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_circle(params: CurveCircleInput) -> str:
        """Create a circle curve.

        Args:
            params: Radius, location, fill mode

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "curves", "circle",
            {
                "name": params.name,
                "radius": params.radius,
                "location": params.location or [0, 0, 0],
                "fill_mode": params.fill_mode
            }
        )

        if result.get("success"):
            return f"Successfully created circle curve '{params.name}' (radius: {params.radius})"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_path",
        annotations={
            "title": "Create Path Curve",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_path(params: CurvePathInput) -> str:
        """Create a path curve (for animation).

        Args:
            params: Length, point count, location

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "curves", "path",
            {
                "name": params.name,
                "length": params.length,
                "points_count": params.points_count,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            return f"Successfully created path curve '{params.name}'"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_spiral",
        annotations={
            "title": "Create Spiral Curve",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_spiral(params: CurveSpiralInput) -> str:
        """Create a spiral curve.

        Args:
            params: Number of turns, radius, height

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "curves", "spiral",
            {
                "name": params.name,
                "turns": params.turns,
                "radius": params.radius,
                "height": params.height,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            return f"Successfully created spiral curve '{params.name}' ({params.turns} turns)"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_to_mesh",
        annotations={
            "title": "Curve to Mesh",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_to_mesh(params: CurveToMeshInput) -> str:
        """Convert a curve to mesh.

        Args:
            params: Curve name, resolution

        Returns:
            Conversion result
        """
        result = await server.execute_command(
            "curves", "to_mesh",
            {
                "curve_name": params.curve_name,
                "resolution": params.resolution,
                "keep_original": params.keep_original
            }
        )

        if result.get("success"):
            mesh_name = result.get("data", {}).get("mesh_name", "")
            return f"Successfully converted curve to mesh '{mesh_name}'"
        else:
            return f"Conversion failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_extrude",
        annotations={
            "title": "Curve Extrude",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_curve_extrude(params: CurveExtrudeInput) -> str:
        """Set curve extrusion and bevel.

        Args:
            params: Curve name, depth, bevel

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "curves", "extrude",
            {
                "curve_name": params.curve_name,
                "depth": params.depth,
                "bevel_depth": params.bevel_depth,
                "bevel_resolution": params.bevel_resolution
            }
        )

        if result.get("success"):
            return f"Successfully set curve extrusion"
        else:
            return f"Setting failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_curve_text",
        annotations={
            "title": "Create Text Curve",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_curve_text(params: CurveTextInput) -> str:
        """Create 3D text.

        Args:
            params: Text content, font size, extrude depth

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "curves", "text",
            {
                "text": params.text,
                "name": params.name,
                "font_size": params.font_size,
                "extrude": params.extrude,
                "location": params.location or [0, 0, 0]
            }
        )

        if result.get("success"):
            return f"Successfully created text '{params.text}'"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"
