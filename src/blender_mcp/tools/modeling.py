"""
Modeling Tools

Provides mesh editing, modifiers, and other modeling features.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class SelectMode(str, Enum):
    """Selection mode"""

    VERT = "VERT"
    EDGE = "EDGE"
    FACE = "FACE"


class SelectAction(str, Enum):
    """Selection action"""

    ALL = "ALL"
    NONE = "NONE"
    INVERT = "INVERT"
    RANDOM = "RANDOM"
    LINKED = "LINKED"


class ModifierType(str, Enum):
    """Modifier type"""

    # Generate
    SUBSURF = "SUBSURF"
    MIRROR = "MIRROR"
    ARRAY = "ARRAY"
    BEVEL = "BEVEL"
    SOLIDIFY = "SOLIDIFY"
    BOOLEAN = "BOOLEAN"
    SKIN = "SKIN"
    SCREW = "SCREW"
    WIREFRAME = "WIREFRAME"
    WELD = "WELD"
    REMESH = "REMESH"
    BUILD = "BUILD"
    MULTIRES = "MULTIRES"
    # Deform
    ARMATURE = "ARMATURE"
    CAST = "CAST"
    CURVE = "CURVE"
    DISPLACE = "DISPLACE"
    LATTICE = "LATTICE"
    SHRINKWRAP = "SHRINKWRAP"
    SIMPLE_DEFORM = "SIMPLE_DEFORM"
    SMOOTH = "SMOOTH"
    LAPLACIANSMOOTH = "LAPLACIANSMOOTH"
    CORRECTIVE_SMOOTH = "CORRECTIVE_SMOOTH"
    SURFACE_DEFORM = "SURFACE_DEFORM"
    MESH_DEFORM = "MESH_DEFORM"
    WARP = "WARP"
    WAVE = "WAVE"
    # Physics
    CLOTH = "CLOTH"
    COLLISION = "COLLISION"
    PARTICLE_SYSTEM = "PARTICLE_SYSTEM"
    # Data
    DATA_TRANSFER = "DATA_TRANSFER"
    WEIGHTED_NORMAL = "WEIGHTED_NORMAL"
    UV_PROJECT = "UV_PROJECT"
    UV_WARP = "UV_WARP"
    VERTEX_WEIGHT_EDIT = "VERTEX_WEIGHT_EDIT"
    VERTEX_WEIGHT_MIX = "VERTEX_WEIGHT_MIX"
    VERTEX_WEIGHT_PROXIMITY = "VERTEX_WEIGHT_PROXIMITY"
    # Decimation
    DECIMATE = "DECIMATE"
    TRIANGULATE = "TRIANGULATE"
    EDGE_SPLIT = "EDGE_SPLIT"
    # Geometry Nodes
    NODES = "NODES"


class BooleanOperation(str, Enum):
    """Boolean operation type"""

    UNION = "UNION"
    DIFFERENCE = "DIFFERENCE"
    INTERSECT = "INTERSECT"


# ==================== Input Models ====================


class MeshEditModeInput(BaseModel):
    """Edit mode input"""

    object_name: str = Field(..., description="Object name")
    enter: bool = Field(default=True, description="true=enter, false=exit")


class MeshSelectInput(BaseModel):
    """Mesh selection input"""

    object_name: str = Field(..., description="Object name")
    select_mode: SelectMode = Field(default=SelectMode.VERT, description="Selection mode")
    action: SelectAction = Field(..., description="Selection action")
    random_ratio: float = Field(default=0.5, description="Random selection ratio", ge=0, le=1)


class MeshExtrudeInput(BaseModel):
    """Extrude input"""

    object_name: str = Field(..., description="Object name")
    direction: list[float] | None = Field(default=None, description="Extrude direction vector")
    distance: float = Field(default=1.0, description="Extrude distance")
    use_normal: bool = Field(default=True, description="Along normal direction")


class MeshSubdivideInput(BaseModel):
    """Subdivide input"""

    object_name: str = Field(..., description="Object name")
    cuts: int = Field(default=1, description="Number of cuts", ge=1, le=100)
    smoothness: float = Field(default=0.0, description="Smoothness", ge=0, le=1)


class MeshBevelInput(BaseModel):
    """Bevel input"""

    object_name: str = Field(..., description="Object name")
    width: float = Field(default=0.1, description="Bevel width", gt=0)
    segments: int = Field(default=1, description="Number of segments", ge=1, le=100)
    profile: float = Field(default=0.5, description="Profile shape", ge=0, le=1)
    affect: str = Field(default="EDGES", description="Affect: VERTICES, EDGES")


class MeshLoopCutInput(BaseModel):
    """Loop cut input"""

    object_name: str = Field(..., description="Object name")
    number_cuts: int = Field(default=1, description="Number of cuts", ge=1, le=100)
    smoothness: float = Field(default=0.0, description="Smoothness", ge=0, le=1)
    edge_index: int | None = Field(default=None, description="Edge index")


class ModifierAddInput(BaseModel):
    """Add modifier input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    object_name: str = Field(..., description="Object name")
    modifier_type: ModifierType = Field(..., description="Modifier type")
    modifier_name: str | None = Field(default=None, description="Modifier name")
    settings: dict | None = Field(default=None, description="Modifier settings")


class ModifierApplyInput(BaseModel):
    """Apply modifier input"""

    object_name: str = Field(..., description="Object name")
    modifier_name: str = Field(..., description="Modifier name")


class ModifierRemoveInput(BaseModel):
    """Remove modifier input"""

    object_name: str = Field(..., description="Object name")
    modifier_name: str = Field(..., description="Modifier name")


class BooleanOperationInput(BaseModel):
    """Boolean operation input"""

    object_name: str = Field(..., description="Main object name")
    target_name: str = Field(..., description="Target object name")
    operation: BooleanOperation = Field(..., description="Operation type")
    apply: bool = Field(default=True, description="Whether to apply immediately")
    hide_target: bool = Field(default=True, description="Hide target object")


# ==================== Shape Key Input Models ====================


class ShapeKeyCreateInput(BaseModel):
    """Create shape key input"""

    object_name: str = Field(..., description="Object name")
    key_name: str = Field(default="Key", description="Shape key name")
    from_mix: bool = Field(default=False, description="Create from current mix state")


class ShapeKeyEditInput(BaseModel):
    """Edit shape key input"""

    object_name: str = Field(..., description="Object name")
    key_name: str = Field(..., description="Shape key name")
    value: float | None = Field(default=None, description="Shape key value (0.0-1.0)", ge=0, le=1)
    mute: bool | None = Field(default=None, description="Whether to mute")
    vertex_offsets: list[dict] | None = Field(
        default=None, description='Vertex offset list [{"index": int, "offset": [x, y, z]}, ...]'
    )


class ShapeKeyDeleteInput(BaseModel):
    """Delete shape key input"""

    object_name: str = Field(..., description="Object name")
    key_name: str = Field(..., description="Shape key name")


class ShapeKeyListInput(BaseModel):
    """List shape keys input"""

    object_name: str = Field(..., description="Object name")


class ExpressionType(str, Enum):
    """Expression type"""

    SMILE = "smile"
    FROWN = "frown"
    SURPRISE = "surprise"
    ANGRY = "angry"
    SAD = "sad"
    BLINK_L = "blink_l"
    BLINK_R = "blink_r"
    BLINK = "blink"
    MOUTH_OPEN = "mouth_open"
    MOUTH_WIDE = "mouth_wide"


class ShapeKeyCreateExpressionInput(BaseModel):
    """Create expression shape key set input"""

    object_name: str = Field(..., description="Object name")
    expressions: list[ExpressionType] = Field(
        default=[
            ExpressionType.SMILE,
            ExpressionType.BLINK,
            ExpressionType.SURPRISE,
            ExpressionType.ANGRY,
        ],
        description="List of expression types to create",
    )


class MeshAssignMaterialToFacesInput(BaseModel):
    """Assign material to specific faces input"""

    object_name: str = Field(..., description="Object name")
    face_indices: list[int] = Field(..., description="Face index list")
    material_slot: int | None = Field(default=None, description="Material slot index")
    material_name: str | None = Field(
        default=None, description="Material name (alternative to material_slot)"
    )


class SelectFacesByMaterialInput(BaseModel):
    """Select faces by material input"""

    object_name: str = Field(..., description="Object name")
    material_slot: int | None = Field(default=None, description="Material slot index")
    material_name: str | None = Field(
        default=None, description="Material name (alternative to material_slot)"
    )


# ==================== Production Standard Optimization Tool Input Models ====================


class TargetPlatform(str, Enum):
    """Target platform"""

    MOBILE = "MOBILE"  # Mobile: 500-2000 triangles
    PC_CONSOLE = "PC_CONSOLE"  # PC/Console: 2000-50000 triangles
    CINEMATIC = "CINEMATIC"  # Cinematic: no limit
    VR = "VR"  # VR: 1000-10000 triangles


class MeshAnalyzeInput(BaseModel):
    """Mesh analysis input"""

    object_name: str = Field(..., description="Object name")
    target_platform: TargetPlatform = Field(
        default=TargetPlatform.PC_CONSOLE, description="Target platform"
    )


class MeshOptimizeInput(BaseModel):
    """Mesh optimization input"""

    object_name: str = Field(..., description="Object name")
    target_triangles: int | None = Field(default=None, description="Target triangle count")
    target_platform: TargetPlatform = Field(
        default=TargetPlatform.PC_CONSOLE, description="Target platform"
    )
    preserve_uvs: bool = Field(default=True, description="Preserve UV coordinates")
    preserve_normals: bool = Field(default=True, description="Preserve normals")
    symmetry: bool = Field(default=False, description="Maintain symmetry")


class MeshCleanupInput(BaseModel):
    """Mesh cleanup input"""

    object_name: str = Field(..., description="Object name")
    merge_distance: float = Field(
        default=0.0001, description="Merge distance (merge overlapping vertices)", ge=0
    )
    remove_doubles: bool = Field(default=True, description="Remove duplicate vertices")
    dissolve_degenerate: bool = Field(default=True, description="Dissolve degenerate geometry")
    fix_non_manifold: bool = Field(default=True, description="Fix non-manifold geometry")
    recalculate_normals: bool = Field(default=True, description="Recalculate normals")
    remove_loose: bool = Field(default=True, description="Remove loose geometry")


class TrisToQuadsInput(BaseModel):
    """Triangles to quads input"""

    object_name: str = Field(..., description="Object name")
    max_angle: float = Field(default=40.0, description="Maximum angle (degrees)", ge=0, le=180)
    compare_uvs: bool = Field(default=True, description="Compare UV coordinates")
    compare_vcol: bool = Field(default=True, description="Compare vertex colors")
    compare_materials: bool = Field(default=True, description="Compare materials")


class LODGenerateInput(BaseModel):
    """LOD generation input"""

    object_name: str = Field(..., description="Object name")
    lod_levels: int = Field(default=3, description="Number of LOD levels", ge=1, le=5)
    ratio_step: float = Field(default=0.5, description="Reduction ratio per level", gt=0, lt=1)
    create_collection: bool = Field(default=True, description="Create LOD collection")


class SmartSubdivideInput(BaseModel):
    """Smart subdivide input"""

    object_name: str = Field(..., description="Object name")
    levels: int = Field(default=1, description="Subdivision levels", ge=1, le=4)
    render_levels: int | None = Field(
        default=None, description="Render levels (optional, defaults to levels)"
    )
    use_creases: bool = Field(default=True, description="Use crease edges to preserve sharp edges")
    apply_smooth: bool = Field(default=False, description="Apply smooth shading")
    quality: int = Field(default=3, description="Quality level (1-5)", ge=1, le=5)


class AutoSmoothInput(BaseModel):
    """Auto smooth input"""

    object_name: str = Field(..., description="Object name")
    angle: float = Field(default=30.0, description="Smooth angle threshold (degrees)", ge=0, le=180)
    use_sharp_edges: bool = Field(default=True, description="Use hard edges for sharp edges")


# ==================== Tool Registration ====================


def register_modeling_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register modeling tools"""

    @mcp.tool(
        name="blender_mesh_edit_mode",
        annotations={
            "title": "Toggle Edit Mode",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_edit_mode(params: MeshEditModeInput) -> str:
        """Enter or exit mesh edit mode.

        Args:
            params: Object name and action

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "modeling", "edit_mode", {"object_name": params.object_name, "enter": params.enter}
        )

        if result.get("success"):
            action = "entered" if params.enter else "exited"
            return f"Object '{params.object_name}' {action} edit mode"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_select",
        annotations={
            "title": "Mesh Selection",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_select(params: MeshSelectInput) -> str:
        """Select mesh elements in edit mode.

        Args:
            params: Selection parameters

        Returns:
            Selection result
        """
        result = await server.execute_command(
            "modeling",
            "select",
            {
                "object_name": params.object_name,
                "select_mode": params.select_mode.value,
                "action": params.action.value,
                "random_ratio": params.random_ratio,
            },
        )

        if result.get("success"):
            return "Selection operation completed"
        else:
            return f"Selection failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_extrude",
        annotations={
            "title": "Extrude",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_extrude(params: MeshExtrudeInput) -> str:
        """Extrude selected mesh elements.

        Args:
            params: Extrude parameters

        Returns:
            Extrude result
        """
        result = await server.execute_command(
            "modeling",
            "extrude",
            {
                "object_name": params.object_name,
                "direction": params.direction or [0, 0, 1],
                "distance": params.distance,
                "use_normal": params.use_normal,
            },
        )

        if result.get("success"):
            return f"Extrude completed, distance: {params.distance}"
        else:
            return f"Extrude failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_subdivide",
        annotations={
            "title": "Subdivide",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_subdivide(params: MeshSubdivideInput) -> str:
        """Subdivide the selected mesh.

        Args:
            params: Subdivide parameters

        Returns:
            Subdivide result
        """
        result = await server.execute_command(
            "modeling",
            "subdivide",
            {
                "object_name": params.object_name,
                "cuts": params.cuts,
                "smoothness": params.smoothness,
            },
        )

        if result.get("success"):
            return f"Subdivision completed, cuts: {params.cuts}"
        else:
            return f"Subdivision failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_bevel",
        annotations={
            "title": "Bevel",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_bevel(params: MeshBevelInput) -> str:
        """Bevel selected edges or vertices.

        Args:
            params: Bevel parameters

        Returns:
            Bevel result
        """
        result = await server.execute_command(
            "modeling",
            "bevel",
            {
                "object_name": params.object_name,
                "width": params.width,
                "segments": params.segments,
                "profile": params.profile,
                "affect": params.affect,
            },
        )

        if result.get("success"):
            return f"Bevel completed, width: {params.width}, segments: {params.segments}"
        else:
            return f"Bevel failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_modifier_add",
        annotations={
            "title": "Add Modifier",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_modifier_add(params: ModifierAddInput) -> str:
        """Add a modifier to an object.

        Supported modifier types include: Subdivision Surface, Mirror, Array, Bevel, Solidify, Boolean, etc.

        Args:
            params: Modifier parameters

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "modeling",
            "modifier_add",
            {
                "object_name": params.object_name,
                "modifier_type": params.modifier_type.value,
                "modifier_name": params.modifier_name,
                "settings": params.settings or {},
            },
        )

        if result.get("success"):
            name = result.get("data", {}).get("modifier_name", params.modifier_type.value)
            return f"Added {params.modifier_type.value} modifier '{name}'"
        else:
            return (
                f"Failed to add modifier: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_modifier_apply",
        annotations={
            "title": "Apply Modifier",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_modifier_apply(params: ModifierApplyInput) -> str:
        """Apply a modifier to the mesh.

        After applying, the modifier will be removed and its effects permanently applied to the mesh.

        Args:
            params: Object name and modifier name

        Returns:
            Apply result
        """
        result = await server.execute_command(
            "modeling",
            "modifier_apply",
            {"object_name": params.object_name, "modifier_name": params.modifier_name},
        )

        if result.get("success"):
            return f"Applied modifier '{params.modifier_name}'"
        else:
            return f"Failed to apply modifier: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_modifier_remove",
        annotations={
            "title": "Remove Modifier",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_modifier_remove(params: ModifierRemoveInput) -> str:
        """Remove a modifier.

        Args:
            params: Object name and modifier name

        Returns:
            Removal result
        """
        result = await server.execute_command(
            "modeling",
            "modifier_remove",
            {"object_name": params.object_name, "modifier_name": params.modifier_name},
        )

        if result.get("success"):
            return f"Removed modifier '{params.modifier_name}'"
        else:
            return f"Failed to remove modifier: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_boolean_operation",
        annotations={
            "title": "Boolean Operation",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_boolean_operation(params: BooleanOperationInput) -> str:
        """Perform a boolean operation.

        Supports union, difference, and intersect operations.

        Args:
            params: Boolean operation parameters

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "modeling",
            "boolean",
            {
                "object_name": params.object_name,
                "target_name": params.target_name,
                "operation": params.operation.value,
                "apply": params.apply,
                "hide_target": params.hide_target,
            },
        )

        if result.get("success"):
            op_names = {"UNION": "union", "DIFFERENCE": "difference", "INTERSECT": "intersect"}
            return f"Boolean {op_names.get(params.operation.value, params.operation.value)} operation completed"
        else:
            return f"Boolean operation failed: {result.get('error', {}).get('message', 'Unknown error')}"

    # ==================== Shape Key Tools ====================

    @mcp.tool(
        name="blender_shapekey_create",
        annotations={
            "title": "Create Shape Key",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_shapekey_create(params: ShapeKeyCreateInput) -> str:
        """Create a shape key.

        Used for creating expression controls, facial animations, and other deformation effects.
        The first call will automatically create a basis shape key (Basis).

        Args:
            params: Object name and shape key name

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "modeling",
            "shapekey_create",
            {
                "object_name": params.object_name,
                "key_name": params.key_name,
                "from_mix": params.from_mix,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Created shape key '{data.get('key_name', params.key_name)}' (index: {data.get('key_index', 'N/A')})"
        else:
            return f"Failed to create shape key: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_shapekey_edit",
        annotations={
            "title": "Edit Shape Key",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_shapekey_edit(params: ShapeKeyEditInput) -> str:
        """Edit shape key properties.

        Can set the shape key's value, mute state, and apply vertex offsets.

        Args:
            params: Edit parameters

        Returns:
            Edit result
        """
        result = await server.execute_command(
            "modeling",
            "shapekey_edit",
            {
                "object_name": params.object_name,
                "key_name": params.key_name,
                "value": params.value,
                "mute": params.mute,
                "vertex_offsets": params.vertex_offsets or [],
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return (
                f"Edited shape key '{params.key_name}', current value: {data.get('value', 'N/A')}"
            )
        else:
            return f"Failed to edit shape key: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_shapekey_delete",
        annotations={
            "title": "Delete Shape Key",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_shapekey_delete(params: ShapeKeyDeleteInput) -> str:
        """Delete a shape key.

        Args:
            params: Object name and shape key name

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "modeling",
            "shapekey_delete",
            {"object_name": params.object_name, "key_name": params.key_name},
        )

        if result.get("success"):
            return f"Deleted shape key '{params.key_name}'"
        else:
            return f"Failed to delete shape key: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_shapekey_list",
        annotations={
            "title": "List Shape Keys",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_shapekey_list(params: ShapeKeyListInput) -> str:
        """List all shape keys for an object.

        Args:
            params: Object name

        Returns:
            Shape key list
        """
        result = await server.execute_command(
            "modeling", "shapekey_list", {"object_name": params.object_name}
        )

        if result.get("success"):
            data = result.get("data", {})
            keys = data.get("shape_keys", [])

            if not keys:
                return f"Object '{params.object_name}' has no shape keys"

            lines = [f"# Shape Keys for {params.object_name}", ""]
            for key in keys:
                status = "🔇" if key.get("mute") else "🔊"
                lines.append(
                    f"- {status} **{key['name']}** (index: {key['index']}, value: {key['value']:.2f})"
                )

            return "\n".join(lines)
        else:
            return f"Failed to get shape key list: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_shapekey_create_expressions",
        annotations={
            "title": "Create Expression Shape Key Set",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_shapekey_create_expressions(params: ShapeKeyCreateExpressionInput) -> str:
        """Create a set of common expression shape keys for a character.

        Quickly create expression shape key frameworks for smile, surprise, blink, etc.

        Args:
            params: Object name and expression type list

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "modeling",
            "shapekey_create_expression",
            {
                "object_name": params.object_name,
                "expressions": [e.value for e in params.expressions],
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            created = data.get("created_keys", [])
            if created:
                return f"Created {len(created)} expression shape keys: {', '.join(created)}"
            else:
                return (
                    "All specified expression shape keys already exist, no new shape keys created"
                )
        else:
            return f"Failed to create expression shape keys: {result.get('error', {}).get('message', 'Unknown error')}"

    # ==================== Face Material Assignment Tools ====================

    @mcp.tool(
        name="blender_mesh_assign_material_to_faces",
        annotations={
            "title": "Assign Material to Specific Faces",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_assign_material_to_faces(params: MeshAssignMaterialToFacesInput) -> str:
        """Assign a material to specific faces of a mesh.

        Used for assigning different materials to specific areas such as collar, cuffs, etc.

        Args:
            params: Object name, face index list, material slot or material name

        Returns:
            Assignment result
        """
        result = await server.execute_command(
            "modeling",
            "mesh_assign_material_to_faces",
            {
                "object_name": params.object_name,
                "face_indices": params.face_indices,
                "material_slot": params.material_slot,
                "material_name": params.material_name,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Assigned {data.get('assigned_faces', len(params.face_indices))} face(s) to material slot {data.get('material_slot', 'N/A')}"
        else:
            return f"Failed to assign material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_select_faces_by_material",
        annotations={
            "title": "Select Faces by Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_select_faces_by_material(params: SelectFacesByMaterialInput) -> str:
        """Select mesh faces by material.

        Select all faces using a specific material.

        Args:
            params: Object name and material slot or material name

        Returns:
            Selection result
        """
        result = await server.execute_command(
            "modeling",
            "select_faces_by_material",
            {
                "object_name": params.object_name,
                "material_slot": params.material_slot,
                "material_name": params.material_name,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Selected {data.get('selected_faces', 0)} face(s) using material slot {data.get('material_slot', 'N/A')}"
        else:
            return (
                f"Failed to select faces: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    # ==================== Production Standard Optimization Tools ====================

    @mcp.tool(
        name="blender_mesh_analyze",
        annotations={
            "title": "Mesh Topology Analysis",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_analyze(params: MeshAnalyzeInput) -> str:
        """Analyze mesh topology quality and check if it meets production standards.

        Checks based on target platform (mobile, PC/console, cinematic, VR):
        - Triangle/quad/N-gon ratio
        - Whether face count is within platform limits
        - Non-manifold geometry
        - Loose vertices/edges
        - Normal consistency

        Args:
            params: Object name and target platform

        Returns:
            Detailed topology analysis report
        """
        result = await server.execute_command(
            "modeling",
            "mesh_analyze",
            {"object_name": params.object_name, "target_platform": params.target_platform.value},
        )

        if result.get("success"):
            data = result.get("data", {})
            lines = [f"# Mesh Analysis Report: {params.object_name}", ""]

            # Basic statistics
            stats = data.get("stats", {})
            lines.append("## Basic Statistics")
            lines.append(f"- Vertices: {stats.get('vertices', 0)}")
            lines.append(f"- Edges: {stats.get('edges', 0)}")
            lines.append(f"- Faces: {stats.get('faces', 0)}")
            lines.append(f"- Triangles: {stats.get('triangles', 0)}")
            lines.append("")

            # Face type distribution
            face_types = data.get("face_types", {})
            lines.append("## Face Type Distribution")
            lines.append(
                f"- Triangles: {face_types.get('tris', 0)} ({face_types.get('tris_percent', 0):.1f}%)"
            )
            lines.append(
                f"- Quads: {face_types.get('quads', 0)} ({face_types.get('quads_percent', 0):.1f}%)"
            )
            lines.append(
                f"- N-gons: {face_types.get('ngons', 0)} ({face_types.get('ngons_percent', 0):.1f}%)"
            )
            lines.append("")

            # Platform compatibility
            platform_check = data.get("platform_check", {})
            lines.append(f"## Platform Compatibility ({params.target_platform.value})")
            lines.append(
                f"- Status: {'✅ Passed' if platform_check.get('passed') else '❌ Failed'}"
            )
            lines.append(
                f"- Recommended triangle range: {platform_check.get('min_tris', 0)} - {platform_check.get('max_tris', 0)}"
            )
            if not platform_check.get("passed"):
                lines.append(
                    f"- Suggestion: {platform_check.get('suggestion', 'Reduce face count')}"
                )
            lines.append("")

            # Issue detection
            issues = data.get("issues", [])
            if issues:
                lines.append("## ⚠️ Issues Detected")
                for issue in issues:
                    lines.append(f"- {issue}")
            else:
                lines.append("## ✅ No Issues Detected")

            # Quality score
            quality_score = data.get("quality_score", 0)
            lines.append("")
            lines.append(f"## Topology Quality Score: {quality_score}/100")

            return "\n".join(lines)
        else:
            return f"Analysis failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_optimize",
        annotations={
            "title": "Mesh Optimization (Decimation)",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_optimize(params: MeshOptimizeInput) -> str:
        """Optimize mesh by reducing face count to meet target platform requirements.

        Uses the Decimate modifier to intelligently reduce face count while maintaining model appearance.

        Args:
            params: Optimization parameters

        Returns:
            Optimization result
        """
        result = await server.execute_command(
            "modeling",
            "mesh_optimize",
            {
                "object_name": params.object_name,
                "target_triangles": params.target_triangles,
                "target_platform": params.target_platform.value,
                "preserve_uvs": params.preserve_uvs,
                "preserve_normals": params.preserve_normals,
                "symmetry": params.symmetry,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            original = data.get("original_triangles", 0)
            optimized = data.get("optimized_triangles", 0)
            reduction = data.get("reduction_percent", 0)
            return f"Mesh optimization completed: {original} -> {optimized} triangles (reduced {reduction:.1f}%)"
        else:
            return f"Optimization failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_mesh_cleanup",
        annotations={
            "title": "Mesh Cleanup",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_mesh_cleanup(params: MeshCleanupInput) -> str:
        """Clean up mesh and fix common topology issues.

        Includes: merging overlapping vertices, removing degenerate geometry, fixing non-manifold,
        recalculating normals, removing loose geometry, etc.

        Args:
            params: Cleanup options

        Returns:
            Cleanup result
        """
        result = await server.execute_command(
            "modeling",
            "mesh_cleanup",
            {
                "object_name": params.object_name,
                "merge_distance": params.merge_distance,
                "remove_doubles": params.remove_doubles,
                "dissolve_degenerate": params.dissolve_degenerate,
                "fix_non_manifold": params.fix_non_manifold,
                "recalculate_normals": params.recalculate_normals,
                "remove_loose": params.remove_loose,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            removed = data.get("removed_vertices", 0)
            fixed = data.get("fixed_issues", 0)
            return f"Mesh cleanup completed: removed {removed} duplicate vertices, fixed {fixed} issue(s)"
        else:
            return f"Cleanup failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_tris_to_quads",
        annotations={
            "title": "Triangles to Quads",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_tris_to_quads(params: TrisToQuadsInput) -> str:
        """Convert triangle faces to quads.

        Quad topology is more suitable for subdivision surfaces and animation deformation.

        Args:
            params: Conversion parameters

        Returns:
            Conversion result
        """
        result = await server.execute_command(
            "modeling",
            "tris_to_quads",
            {
                "object_name": params.object_name,
                "max_angle": params.max_angle,
                "compare_uvs": params.compare_uvs,
                "compare_vcol": params.compare_vcol,
                "compare_materials": params.compare_materials,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            converted = data.get("converted_faces", 0)
            return f"Converted {converted} triangle pairs to quads"
        else:
            return f"Conversion failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_lod_generate",
        annotations={
            "title": "Generate LOD (Level of Detail)",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_lod_generate(params: LODGenerateInput) -> str:
        """Generate multiple Level of Detail (LOD) versions for a model.

        LOD is used in games to display models at different detail levels based on distance for performance optimization.

        Args:
            params: LOD generation parameters

        Returns:
            Generation result
        """
        result = await server.execute_command(
            "modeling",
            "lod_generate",
            {
                "object_name": params.object_name,
                "lod_levels": params.lod_levels,
                "ratio_step": params.ratio_step,
                "create_collection": params.create_collection,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            lods = data.get("lod_objects", [])
            lines = ["# LOD Generation Completed", ""]
            for lod in lods:
                lines.append(f"- {lod['name']}: {lod['triangles']} triangles")
            return "\n".join(lines)
        else:
            return (
                f"LOD generation failed: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_smart_subdivide",
        annotations={
            "title": "Smart Subdivide",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_smart_subdivide(params: SmartSubdivideInput) -> str:
        """Smart subdivide mesh with automatic crease edge and smoothing group handling.

        More intelligent than regular subdivision surface; automatically detects and protects sharp edges.

        Args:
            params: Subdivision parameters

        Returns:
            Subdivision result
        """
        result = await server.execute_command(
            "modeling",
            "smart_subdivide",
            {
                "object_name": params.object_name,
                "levels": params.levels,
                "render_levels": params.render_levels or params.levels,
                "use_creases": params.use_creases,
                "apply_smooth": params.apply_smooth,
                "quality": params.quality,
            },
        )

        if result.get("success"):
            result.get("data", {})
            return f"Smart subdivision completed: viewport level {params.levels}, render level {params.render_levels or params.levels}"
        else:
            return f"Subdivision failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_auto_smooth",
        annotations={
            "title": "Auto Smooth",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_auto_smooth(params: AutoSmoothInput) -> str:
        """Set auto smooth, distinguishing smooth faces and hard edges by angle threshold.

        This is standard practice in game and film production for controlling model shading appearance.

        Args:
            params: Auto smooth parameters

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "modeling",
            "auto_smooth",
            {
                "object_name": params.object_name,
                "angle": params.angle,
                "use_sharp_edges": params.use_sharp_edges,
            },
        )

        if result.get("success"):
            return f"Auto smooth set for '{params.object_name}', angle threshold: {params.angle} degrees"
        else:
            return f"Setting failed: {result.get('error', {}).get('message', 'Unknown error')}"
