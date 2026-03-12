"""
Advanced Mesh Editing Tools

Consolidates inset_faces, bridge_edge_loops, spin, knife_cut, fill_grid,
separate, symmetrize, edge_crease, edge_sharp, edge_seam and other operations
into a small number of composite tools to avoid tool count bloat.
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Enums ====================

class MeshEditOperation(str, Enum):
    """Advanced mesh edit operation type"""
    INSET_FACES = "INSET_FACES"
    BRIDGE_EDGE_LOOPS = "BRIDGE_EDGE_LOOPS"
    SPIN = "SPIN"
    KNIFE_CUT = "KNIFE_CUT"
    FILL = "FILL"
    GRID_FILL = "GRID_FILL"
    SEPARATE = "SEPARATE"
    SYMMETRIZE = "SYMMETRIZE"
    POKE_FACES = "POKE_FACES"
    TRIANGULATE = "TRIANGULATE"
    TRIS_TO_QUADS = "TRIS_TO_QUADS"
    DISSOLVE = "DISSOLVE"


class EdgeMarkOperation(str, Enum):
    """Edge mark operation type"""
    CREASE = "CREASE"
    SHARP = "SHARP"
    SEAM = "SEAM"
    BEVEL_WEIGHT = "BEVEL_WEIGHT"


class SelectByTraitType(str, Enum):
    """Select by trait type"""
    ALL = "ALL"
    NONE = "NONE"
    NON_MANIFOLD = "NON_MANIFOLD"
    LOOSE = "LOOSE"
    INTERIOR_FACES = "INTERIOR_FACES"
    FACE_SIDES = "FACE_SIDES"
    UNGROUPED = "UNGROUPED"
    BOUNDARY = "BOUNDARY"
    SHARP_EDGES = "SHARP_EDGES"
    LINKED_FLAT = "LINKED_FLAT"


class VertexGroupAction(str, Enum):
    """Vertex group action"""
    CREATE = "CREATE"
    ASSIGN = "ASSIGN"
    REMOVE = "REMOVE"
    SELECT = "SELECT"
    DESELECT = "DESELECT"


# ==================== Input Models ====================

class MeshEditAdvancedInput(BaseModel):
    """Advanced mesh edit input - unified interface"""
    object_name: str = Field(..., description="Object name")
    operation: MeshEditOperation = Field(..., description="Operation type")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Operation parameters (by operation type): "
                    "INSET_FACES: thickness(float,0.01), depth(float,0), individual(bool,false), use_boundary(bool,true), use_even_offset(bool,true); "
                    "BRIDGE_EDGE_LOOPS: segments(int,1), twist(int,0), profile_shape(str,'SMOOTH'), blend(float,1.0); "
                    "SPIN: angle(float,6.28=360°), steps(int,12), axis(str,'Z'), center([x,y,z]), dupli(bool,false); "
                    "KNIFE_CUT: cut_through(bool,false); "
                    "FILL: use_beauty(bool,true); "
                    "GRID_FILL: span(int,1), offset(int,0); "
                    "SEPARATE: mode(str: SELECTED/MATERIAL/LOOSE); "
                    "SYMMETRIZE: direction(str: NEGATIVE_X/POSITIVE_X/NEGATIVE_Y/POSITIVE_Y/NEGATIVE_Z/POSITIVE_Z); "
                    "POKE_FACES: (no extra parameters); "
                    "TRIANGULATE: quad_method(str,'BEAUTY'), ngon_method(str,'BEAUTY'); "
                    "TRIS_TO_QUADS: max_angle(float,40.0); "
                    "DISSOLVE: use_verts(bool,false), use_face_split(bool,false)"
    )


class EdgeMarkInput(BaseModel):
    """Edge mark tool input"""
    object_name: str = Field(..., description="Object name")
    mark_type: EdgeMarkOperation = Field(..., description="Mark type: CREASE, SHARP, SEAM (UV seam), BEVEL_WEIGHT")
    value: float = Field(default=1.0, description="Mark value (0.0-1.0), 0=clear mark", ge=0.0, le=1.0)
    clear: bool = Field(default=False, description="Whether to clear marks (set to true to clear marks on selected edges)")


class SelectByTraitInput(BaseModel):
    """Select by trait input"""
    object_name: str = Field(..., description="Object name")
    select_mode: str = Field(default="FACE", description="Selection mode: VERT, EDGE, FACE")
    trait: SelectByTraitType = Field(..., description="Trait type")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Trait parameters: "
                    "FACE_SIDES: number(int,4), type(str: LESS/EQUAL/GREATER), extend(bool,false); "
                    "LINKED_FLAT: sharpness(float,0.0175=1°); "
                    "NON_MANIFOLD: extend(bool,false), use_wire(bool,true), use_boundary(bool,true), use_multi_face(bool,true), use_non_contiguous(bool,true), use_verts(bool,true); "
                    "SHARP_EDGES: sharpness(float,0.523=30°); "
                    "LOOSE: extend(bool,false)"
    )


class VertexGroupInput(BaseModel):
    """Vertex group operation input"""
    object_name: str = Field(..., description="Object name")
    action: VertexGroupAction = Field(..., description="Action type")
    group_name: str = Field(default="Group", description="Vertex group name")
    weight: float = Field(default=1.0, description="Weight value (0.0-1.0)", ge=0.0, le=1.0)
    vertex_indices: Optional[List[int]] = Field(default=None, description="Vertex index list (uses current selection if empty)")


class VertexColorInput(BaseModel):
    """Vertex color operation input"""
    object_name: str = Field(..., description="Object name")
    action: str = Field(default="CREATE", description="Action: CREATE (create layer), PAINT (paint), FILL (fill all)")
    layer_name: str = Field(default="Col", description="Vertex color layer name")
    color: Optional[List[float]] = Field(default=None, description="Color [R,G,B,A] (0-1 range)")
    face_indices: Optional[List[int]] = Field(default=None, description="Face index list (PAINT only, applies to all faces if empty)")


# ==================== Tool Registration ====================

def register_mesh_edit_advanced_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register advanced mesh editing tools"""

    @mcp.tool(
        name="blender_mesh_edit_advanced",
        annotations={
            "title": "Advanced Mesh Edit",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_edit_advanced(params: MeshEditAdvancedInput) -> str:
        """Perform advanced mesh editing operations.

        Supports Inset Faces, Bridge Edge Loops, Spin, Knife Cut,
        Fill/Grid Fill, Separate, Symmetrize, and other operations.

        Note: Requires entering edit mode and selecting elements first.

        Args:
            params: Operation type and parameters

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "edit",
            {
                "object_name": params.object_name,
                "operation": params.operation.value,
                "params": params.params or {}
            }
        )

        if result.get("success"):
            op_names = {
                "INSET_FACES": "Inset Faces", "BRIDGE_EDGE_LOOPS": "Bridge Edge Loops",
                "SPIN": "Spin", "KNIFE_CUT": "Knife Cut", "FILL": "Fill",
                "GRID_FILL": "Grid Fill", "SEPARATE": "Separate", "SYMMETRIZE": "Symmetrize",
                "POKE_FACES": "Poke Faces", "TRIANGULATE": "Triangulate",
                "TRIS_TO_QUADS": "Tris to Quads", "DISSOLVE": "Dissolve"
            }
            return f"{op_names.get(params.operation.value, params.operation.value)} operation complete"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_edge_mark",
        annotations={
            "title": "Edge Mark Tool",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_edge_mark(params: EdgeMarkInput) -> str:
        """Set edge Crease, Sharp, UV Seam, or Bevel Weight.

        Used to control subdivision surface edge sharpness (Crease),
        smooth shading hard edges (Sharp), UV unwrap seams (Seam), etc.
        Requires entering edit mode and selecting edges first.

        Args:
            params: Mark type, value

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "edge_mark",
            {
                "object_name": params.object_name,
                "mark_type": params.mark_type.value,
                "value": params.value,
                "clear": params.clear
            }
        )

        if result.get("success"):
            mark_names = {"CREASE": "Crease", "SHARP": "Sharp", "SEAM": "UV Seam", "BEVEL_WEIGHT": "Bevel Weight"}
            action = "Cleared" if params.clear else f"Set (value={params.value})"
            return f"{action} {mark_names.get(params.mark_type.value, params.mark_type.value)}"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_select_by_trait",
        annotations={
            "title": "Select Mesh by Trait",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_select_by_trait(params: SelectByTraitInput) -> str:
        """Select mesh elements by trait.

        Supports selecting non-manifold, loose elements, interior faces,
        by face side count (tris/quads/n-gons), ungrouped vertices,
        boundary edges, sharp edges, linked flat faces, etc.

        Requires entering edit mode first.

        Args:
            params: Selection mode and trait type

        Returns:
            Selection result
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "select_by_trait",
            {
                "object_name": params.object_name,
                "select_mode": params.select_mode,
                "trait": params.trait.value,
                "params": params.params or {}
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            count = data.get("selected_count", "N/A")
            trait_names = {
                "NON_MANIFOLD": "Non-Manifold", "LOOSE": "Loose", "INTERIOR_FACES": "Interior Faces",
                "FACE_SIDES": "Face Sides", "UNGROUPED": "Ungrouped", "BOUNDARY": "Boundary",
                "SHARP_EDGES": "Sharp Edges", "LINKED_FLAT": "Linked Flat",
                "ALL": "Select All", "NONE": "Deselect All"
            }
            return f"Selection by {trait_names.get(params.trait.value, params.trait.value)} complete, selected {count} elements"
        else:
            return f"Selection failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vertex_group",
        annotations={
            "title": "Vertex Group Operations",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group(params: VertexGroupInput) -> str:
        """Create, assign, or select vertex groups.

        Vertex groups are used for binding weights, modifier influence ranges,
        particle distribution density, etc.

        Args:
            params: Action type, group name, weight

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "vertex_group",
            {
                "object_name": params.object_name,
                "action": params.action.value,
                "group_name": params.group_name,
                "weight": params.weight,
                "vertex_indices": params.vertex_indices
            }
        )

        if result.get("success"):
            action_names = {
                "CREATE": "Create", "ASSIGN": "Assign", "REMOVE": "Remove",
                "SELECT": "Select", "DESELECT": "Deselect"
            }
            return f"Vertex group '{params.group_name}' {action_names.get(params.action.value, params.action.value)} operation complete"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_vertex_color",
        annotations={
            "title": "Vertex Color Operations",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_color(params: VertexColorInput) -> str:
        """Create and edit vertex colors.

        A core coloring method for Low Poly style. Supports creating vertex color layers,
        filling colors per face, and filling all faces.

        Args:
            params: Action type, color, face indices

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "vertex_color",
            {
                "object_name": params.object_name,
                "action": params.action,
                "layer_name": params.layer_name,
                "color": params.color or [1.0, 1.0, 1.0, 1.0],
                "face_indices": params.face_indices
            }
        )

        if result.get("success"):
            action_names = {"CREATE": "Create Layer", "PAINT": "Paint", "FILL": "Fill"}
            return f"Vertex color {action_names.get(params.action, params.action)} complete"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"
