"""
Object Operation Tools

Provides object creation, deletion, transformation, selection, and other features.
"""

from typing import TYPE_CHECKING, Optional, List, Union
from enum import Enum
import json

from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ObjectType(str, Enum):
    """Object type"""
    # Mesh
    CUBE = "CUBE"
    SPHERE = "SPHERE"
    UV_SPHERE = "UV_SPHERE"
    ICO_SPHERE = "ICO_SPHERE"
    CYLINDER = "CYLINDER"
    CONE = "CONE"
    TORUS = "TORUS"
    PLANE = "PLANE"
    CIRCLE = "CIRCLE"
    GRID = "GRID"
    MONKEY = "MONKEY"
    # Curve
    BEZIER = "BEZIER"
    NURBS_CURVE = "NURBS_CURVE"
    NURBS_CIRCLE = "NURBS_CIRCLE"
    PATH = "PATH"
    # Other
    TEXT = "TEXT"
    EMPTY = "EMPTY"
    ARMATURE = "ARMATURE"
    LATTICE = "LATTICE"
    CAMERA = "CAMERA"
    LIGHT = "LIGHT"


class ResponseFormat(str, Enum):
    """Response format"""
    MARKDOWN = "markdown"
    JSON = "json"


# ==================== Input Models ====================

class Vector3(BaseModel):
    """3D vector"""
    x: float = Field(default=0.0)
    y: float = Field(default=0.0)
    z: float = Field(default=0.0)

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class ObjectCreateInput(BaseModel):
    """Create object input"""
    model_config = ConfigDict(str_strip_whitespace=True)

    type: ObjectType = Field(..., description="Object type")
    name: Optional[str] = Field(default=None, description="Object name", max_length=100)
    location: Optional[List[float]] = Field(
        default=None,
        description="Position coordinates [x, y, z]"
    )
    rotation: Optional[List[float]] = Field(
        default=None,
        description="Rotation angles (radians) [x, y, z]"
    )
    scale: Optional[List[float]] = Field(
        default=None,
        description="Scale [x, y, z]"
    )
    mesh_params: Optional[dict] = Field(
        default=None,
        description="Mesh creation parameters (optional). Available parameters depend on type: "
                    "SPHERE/UV_SPHERE: segments(int,default 32), ring_count(int,default 16), radius(float,default 1); "
                    "ICO_SPHERE: subdivisions(int,default 2), radius(float,default 1); "
                    "CYLINDER: vertices(int,default 32), radius(float,default 1), depth(float,default 2), fill_type(str: NGON/TRIS/NOTHING); "
                    "CONE: vertices(int,default 32), radius1(float,default 1), radius2(float,default 0), depth(float,default 2), fill_type(str); "
                    "TORUS: major_segments(int,default 48), minor_segments(int,default 12), major_radius(float,default 1), minor_radius(float,default 0.25); "
                    "CIRCLE: vertices(int,default 32), radius(float,default 1), fill_type(str: NGON/TRIS/NOTHING); "
                    "GRID: x_subdivisions(int,default 10), y_subdivisions(int,default 10), size(float,default 2); "
                    "CUBE: size(float,default 2); "
                    "PLANE: size(float,default 2). "
                    "Low Poly style suggestion: segments=6~12, subdivisions=1~2"
    )

    @field_validator("location", "rotation", "scale")
    @classmethod
    def validate_vector(cls, v):
        if v is not None and len(v) != 3:
            raise ValueError("Vector must contain 3 elements")
        return v


class ObjectDeleteInput(BaseModel):
    """Delete object input"""
    name: str = Field(..., description="Object name")
    delete_data: bool = Field(default=True, description="Whether to also delete object data")


class ObjectDuplicateInput(BaseModel):
    """Duplicate object input"""
    name: str = Field(..., description="Source object name")
    new_name: Optional[str] = Field(default=None, description="New object name")
    linked: bool = Field(default=False, description="Whether to create a linked duplicate")
    offset: Optional[List[float]] = Field(default=None, description="Position offset [x, y, z]")


class ObjectTransformInput(BaseModel):
    """Transform object input"""
    name: str = Field(..., description="Object name")
    location: Optional[List[float]] = Field(default=None, description="New location (absolute)")
    rotation: Optional[List[float]] = Field(default=None, description="New rotation (radians)")
    scale: Optional[List[float]] = Field(default=None, description="New scale")
    delta_location: Optional[List[float]] = Field(default=None, description="Location delta")
    delta_rotation: Optional[List[float]] = Field(default=None, description="Rotation delta")
    delta_scale: Optional[List[float]] = Field(default=None, description="Scale delta")


class ObjectSelectInput(BaseModel):
    """Select object input"""
    names: Optional[List[str]] = Field(default=None, description="List of object names to select")
    pattern: Optional[str] = Field(default=None, description="Selection pattern (supports wildcards)")
    deselect_all: bool = Field(default=True, description="Whether to deselect all first")
    set_active: Optional[str] = Field(default=None, description="Set active object")


class ObjectListInput(BaseModel):
    """List objects input"""
    type_filter: Optional[str] = Field(default=None, description="Filter by object type")
    name_pattern: Optional[str] = Field(default=None, description="Name matching pattern")
    limit: int = Field(default=50, description="Return count limit", ge=1, le=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ObjectGetInfoInput(BaseModel):
    """Get object info input"""
    name: str = Field(..., description="Object name")
    include_mesh_stats: bool = Field(default=True, description="Include mesh statistics")
    include_modifiers: bool = Field(default=True, description="Include modifier info")
    include_materials: bool = Field(default=True, description="Include material info")


class ObjectRenameInput(BaseModel):
    """Rename object input"""
    name: str = Field(..., description="Current object name")
    new_name: str = Field(..., description="New name", min_length=1, max_length=100)


class ObjectParentInput(BaseModel):
    """Set parent-child relationship input"""
    child_name: str = Field(..., description="Child object name")
    parent_name: Optional[str] = Field(default=None, description="Parent object name (empty to clear parent)")
    keep_transform: bool = Field(default=True, description="Keep world transform")


class ObjectJoinInput(BaseModel):
    """Join objects input"""
    objects: List[str] = Field(..., description="List of object names to join", min_length=2)
    target: Optional[str] = Field(default=None, description="Target object (join into this object)")


class OriginType(str, Enum):
    """Origin type"""
    GEOMETRY = "GEOMETRY"           # Origin to geometry center
    CURSOR = "CURSOR"               # Origin to 3D cursor
    BOTTOM = "BOTTOM"               # Origin to bottom center (feet)
    CENTER_OF_MASS = "CENTER_OF_MASS"       # Origin to center of mass
    CENTER_OF_VOLUME = "CENTER_OF_VOLUME"   # Origin to center of volume


class ObjectSetOriginInput(BaseModel):
    """Set origin input"""
    name: str = Field(..., description="Object name")
    origin_type: OriginType = Field(
        default=OriginType.GEOMETRY,
        description="Origin type: GEOMETRY(geometry center), CURSOR(3D cursor), BOTTOM(bottom center/feet), CENTER_OF_MASS(center of mass), CENTER_OF_VOLUME(center of volume)"
    )
    center: str = Field(default="MEDIAN", description="Geometry center calculation method: MEDIAN or BOUNDS")


class ObjectApplyTransformInput(BaseModel):
    """Apply transform input"""
    name: str = Field(..., description="Object name")
    location: bool = Field(default=False, description="Apply location")
    rotation: bool = Field(default=False, description="Apply rotation")
    scale: bool = Field(default=True, description="Apply scale")


# ==================== Tool Registration ====================

def register_object_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register object operation tools"""

    @mcp.tool(
        name="blender_object_create",
        annotations={
            "title": "Create Object",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_create(params: ObjectCreateInput) -> str:
        """Create a new object in Blender.

        Supports creating various types of objects including meshes (cube, sphere, etc.), curves, text, etc.

        Args:
            params: Object type, name, location, rotation, scale

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "object", "create",
            {
                "type": params.type.value,
                "name": params.name,
                "location": params.location or [0, 0, 0],
                "rotation": params.rotation or [0, 0, 0],
                "scale": params.scale or [1, 1, 1],
                "mesh_params": params.mesh_params or {}
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            name = data.get("object_name", params.name or params.type.value)
            return f"Successfully created {params.type.value} object '{name}', location: {data.get('location', params.location)}"
        else:
            return f"Failed to create object: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_delete",
        annotations={
            "title": "Delete Object",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_delete(params: ObjectDeleteInput) -> str:
        """Delete the specified object.

        Args:
            params: Object name and deletion options

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "object", "delete",
            {"name": params.name, "delete_data": params.delete_data}
        )

        if result.get("success"):
            return f"Deleted object '{params.name}'"
        else:
            return f"Failed to delete object: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_duplicate",
        annotations={
            "title": "Duplicate Object",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_duplicate(params: ObjectDuplicateInput) -> str:
        """Duplicate an object.

        Can create an independent copy or a linked copy (sharing mesh data).

        Args:
            params: Source object name, new name, whether to link, position offset

        Returns:
            Duplication result
        """
        result = await server.execute_command(
            "object", "duplicate",
            {
                "name": params.name,
                "new_name": params.new_name,
                "linked": params.linked,
                "offset": params.offset or [0, 0, 0]
            }
        )

        if result.get("success"):
            new_name = result.get("data", {}).get("new_object_name", params.new_name)
            return f"Duplicated object '{params.name}' as '{new_name}'"
        else:
            return f"Failed to duplicate object: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_transform",
        annotations={
            "title": "Transform Object",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_transform(params: ObjectTransformInput) -> str:
        """Transform an object (location, rotation, scale).

        Can set absolute values or delta transforms.

        Args:
            params: Object name and transform parameters

        Returns:
            Transform result
        """
        transform = {}
        if params.location is not None:
            transform["location"] = params.location
        if params.rotation is not None:
            transform["rotation"] = params.rotation
        if params.scale is not None:
            transform["scale"] = params.scale
        if params.delta_location is not None:
            transform["delta_location"] = params.delta_location
        if params.delta_rotation is not None:
            transform["delta_rotation"] = params.delta_rotation
        if params.delta_scale is not None:
            transform["delta_scale"] = params.delta_scale

        if not transform:
            return "No transform parameters specified"

        result = await server.execute_command(
            "object", "transform",
            {"name": params.name, **transform}
        )

        if result.get("success"):
            return f"Transformed object '{params.name}'"
        else:
            return f"Transform failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_select",
        annotations={
            "title": "Select Objects",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_select(params: ObjectSelectInput) -> str:
        """Select objects.

        Can select objects by name list or wildcard pattern.

        Args:
            params: Selection parameters

        Returns:
            Selection result
        """
        result = await server.execute_command(
            "object", "select",
            {
                "names": params.names,
                "pattern": params.pattern,
                "deselect_all": params.deselect_all,
                "set_active": params.set_active
            }
        )

        if result.get("success"):
            count = result.get("data", {}).get("selected_count", 0)
            return f"Selected {count} object(s)"
        else:
            return f"Selection failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_list",
        annotations={
            "title": "List Objects",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_list(params: ObjectListInput) -> str:
        """List objects in the scene.

        Can filter by type or name pattern.

        Args:
            params: Filter and format options

        Returns:
            Object list
        """
        result = await server.execute_command(
            "object", "list",
            {
                "type_filter": params.type_filter,
                "name_pattern": params.name_pattern,
                "limit": params.limit
            }
        )

        if not result.get("success"):
            return f"Failed to get object list: {result.get('error', {}).get('message', 'Unknown error')}"

        objects = result.get("data", {}).get("objects", [])
        total = result.get("data", {}).get("total", len(objects))

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"objects": objects, "total": total}, indent=2)

        # Markdown format
        lines = ["# Object List", ""]
        lines.append(f"Total: {total} object(s)" + (f" (showing {len(objects)})" if len(objects) < total else ""))
        lines.append("")

        for obj in objects:
            lines.append(f"## {obj['name']}")
            lines.append(f"- **Type**: {obj.get('type', 'Unknown')}")
            lines.append(f"- **Location**: {obj.get('location', [0, 0, 0])}")
            lines.append(f"- **Visible**: {'Yes' if obj.get('visible', True) else 'No'}")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_object_get_info",
        annotations={
            "title": "Get Object Info",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_get_info(params: ObjectGetInfoInput) -> str:
        """Get detailed information about an object.

        Includes transform, mesh statistics, modifiers, materials, and other info.

        Args:
            params: Object name and inclusion options

        Returns:
            Detailed object information
        """
        result = await server.execute_command(
            "object", "get_info",
            {
                "name": params.name,
                "include_mesh_stats": params.include_mesh_stats,
                "include_modifiers": params.include_modifiers,
                "include_materials": params.include_materials
            }
        )

        if not result.get("success"):
            return f"Failed to get object info: {result.get('error', {}).get('message', 'Unknown error')}"

        data = result.get("data", {})

        lines = [f"# Object: {data.get('name', params.name)}", ""]
        lines.append(f"- **Type**: {data.get('type', 'Unknown')}")
        lines.append(f"- **Location**: {data.get('location', [0, 0, 0])}")
        lines.append(f"- **Rotation**: {data.get('rotation_euler', [0, 0, 0])}")
        lines.append(f"- **Scale**: {data.get('scale', [1, 1, 1])}")
        lines.append(f"- **Dimensions**: {data.get('dimensions', [0, 0, 0])}")

        if params.include_mesh_stats and "mesh_stats" in data:
            stats = data["mesh_stats"]
            lines.append("")
            lines.append("## Mesh Statistics")
            lines.append(f"- Vertices: {stats.get('vertices', 0)}")
            lines.append(f"- Edges: {stats.get('edges', 0)}")
            lines.append(f"- Faces: {stats.get('faces', 0)}")
            lines.append(f"- Triangles: {stats.get('triangles', 0)}")

        if params.include_modifiers:
            mods = data.get("modifiers", [])
            if mods:
                lines.append("")
                lines.append("## Modifiers")
                for mod in mods:
                    lines.append(f"- {mod}")

        if params.include_materials:
            mats = data.get("materials", [])
            if mats:
                lines.append("")
                lines.append("## Materials")
                for mat in mats:
                    lines.append(f"- {mat}")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_object_rename",
        annotations={
            "title": "Rename Object",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_rename(params: ObjectRenameInput) -> str:
        """Rename an object.

        Args:
            params: Current name and new name

        Returns:
            Rename result
        """
        result = await server.execute_command(
            "object", "rename",
            {"name": params.name, "new_name": params.new_name}
        )

        if result.get("success"):
            return f"Renamed object '{params.name}' to '{params.new_name}'"
        else:
            return f"Rename failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_parent",
        annotations={
            "title": "Set Parent-Child Relationship",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_parent(params: ObjectParentInput) -> str:
        """Set the parent-child relationship for objects.

        Args:
            params: Child object and parent object names

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "object", "set_parent",
            {
                "child_name": params.child_name,
                "parent_name": params.parent_name,
                "keep_transform": params.keep_transform
            }
        )

        if result.get("success"):
            if params.parent_name:
                return f"Set '{params.child_name}' as child of '{params.parent_name}'"
            else:
                return f"Cleared parent relationship for '{params.child_name}'"
        else:
            return f"Failed to set parent-child relationship: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_join",
        annotations={
            "title": "Join Objects",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_join(params: ObjectJoinInput) -> str:
        """Join multiple objects into one.

        Args:
            params: List of objects to join and target object

        Returns:
            Join result
        """
        result = await server.execute_command(
            "object", "join",
            {"objects": params.objects, "target": params.target}
        )

        if result.get("success"):
            target = result.get("data", {}).get("result_object", params.target or params.objects[0])
            return f"Joined {len(params.objects)} objects into '{target}'"
        else:
            return f"Join failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_set_origin",
        annotations={
            "title": "Set Origin",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_set_origin(params: ObjectSetOriginInput) -> str:
        """Set the origin point of an object.

        Supports multiple origin setting methods including geometry center, 3D cursor, bottom center (suitable for character feet), etc.

        Args:
            params: Object name and origin type

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "object", "set_origin",
            {
                "name": params.name,
                "origin_type": params.origin_type.value,
                "center": params.center
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Set origin of '{params.name}' to {params.origin_type.value}, new origin location: {data.get('new_origin', 'N/A')}"
        else:
            return f"Failed to set origin: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_object_apply_transform",
        annotations={
            "title": "Apply Transform",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_apply_transform(params: ObjectApplyTransformInput) -> str:
        """Apply object transforms (location, rotation, scale).

        Applies transform data to the mesh data and resets object transforms to default values.

        Args:
            params: Object name and transform types to apply

        Returns:
            Apply result
        """
        result = await server.execute_command(
            "object", "apply_transform",
            {
                "name": params.name,
                "location": params.location,
                "rotation": params.rotation,
                "scale": params.scale
            }
        )

        if result.get("success"):
            applied = []
            if params.location:
                applied.append("location")
            if params.rotation:
                applied.append("rotation")
            if params.scale:
                applied.append("scale")
            return f"Applied transforms for '{params.name}': {', '.join(applied) if applied else 'none'}"
        else:
            return f"Failed to apply transform: {result.get('error', {}).get('message', 'Unknown error')}"
