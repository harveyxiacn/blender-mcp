"""
Camera Tools

Provides camera creation and configuration features.
"""

from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================


class CameraCreateInput(BaseModel):
    """Create camera input"""

    name: str | None = Field(default="Camera", description="Camera name")
    location: list[float] | None = Field(default=None, description="Location")
    rotation: list[float] | None = Field(default=None, description="Rotation")
    lens: float = Field(default=50.0, description="Focal length (mm)", ge=1, le=500)
    sensor_width: float = Field(default=36.0, description="Sensor width (mm)", ge=1)
    set_active: bool = Field(default=True, description="Set as active camera")


class CameraSetPropertiesInput(BaseModel):
    """Set camera properties input"""

    camera_name: str = Field(..., description="Camera name")
    lens: float | None = Field(default=None, description="Focal length", ge=1, le=500)
    sensor_width: float | None = Field(default=None, description="Sensor width", ge=1)
    clip_start: float | None = Field(default=None, description="Near clip", gt=0)
    clip_end: float | None = Field(default=None, description="Far clip", gt=0)
    dof_focus_object: str | None = Field(default=None, description="DOF focus object")
    dof_focus_distance: float | None = Field(default=None, description="DOF focus distance", ge=0)
    dof_aperture_fstop: float | None = Field(default=None, description="Aperture f-stop", gt=0)


class CameraLookAtInput(BaseModel):
    """Camera look at target input"""

    camera_name: str = Field(..., description="Camera name")
    target: str | list[float] = Field(..., description="Target object name or position coordinates")
    use_constraint: bool = Field(default=False, description="Use constraint (continuous tracking)")


class CameraSetActiveInput(BaseModel):
    """Set active camera input"""

    camera_name: str = Field(..., description="Camera name")


# ==================== Tool Registration ====================


def register_camera_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register camera tools"""

    @mcp.tool(
        name="blender_camera_create",
        annotations={
            "title": "Create Camera",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_camera_create(params: CameraCreateInput) -> str:
        """Create a camera.

        Args:
            params: Camera name, location, focal length, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "camera",
            "create",
            {
                "name": params.name,
                "location": params.location or [0, -10, 5],
                "rotation": params.rotation or [1.1, 0, 0],
                "lens": params.lens,
                "sensor_width": params.sensor_width,
                "set_active": params.set_active,
            },
        )

        if result.get("success"):
            name = result.get("data", {}).get("camera_name", params.name)
            return f"Successfully created camera '{name}', focal length: {params.lens}mm"
        else:
            return f"Failed to create camera: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_camera_set_properties",
        annotations={
            "title": "Set Camera Properties",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_camera_set_properties(params: CameraSetPropertiesInput) -> str:
        """Set camera properties.

        Can set focal length, clip distance, depth of field, and other properties.

        Args:
            params: Camera name and properties to set

        Returns:
            Setting result
        """
        properties = {}
        if params.lens is not None:
            properties["lens"] = params.lens
        if params.sensor_width is not None:
            properties["sensor_width"] = params.sensor_width
        if params.clip_start is not None:
            properties["clip_start"] = params.clip_start
        if params.clip_end is not None:
            properties["clip_end"] = params.clip_end
        if params.dof_focus_object is not None:
            properties["dof_focus_object"] = params.dof_focus_object
        if params.dof_focus_distance is not None:
            properties["dof_focus_distance"] = params.dof_focus_distance
        if params.dof_aperture_fstop is not None:
            properties["dof_aperture_fstop"] = params.dof_aperture_fstop

        if not properties:
            return "No properties specified"

        result = await server.execute_command(
            "camera",
            "set_properties",
            {"camera_name": params.camera_name, "properties": properties},
        )

        if result.get("success"):
            return f"Camera '{params.camera_name}' properties updated"
        else:
            return f"Failed to set camera properties: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_camera_look_at",
        annotations={
            "title": "Camera Look At Target",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_camera_look_at(params: CameraLookAtInput) -> str:
        """Point the camera at a specified target.

        Can point at an object or a coordinate point.

        Args:
            params: Camera name and target

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "camera",
            "look_at",
            {
                "camera_name": params.camera_name,
                "target": params.target,
                "use_constraint": params.use_constraint,
            },
        )

        if result.get("success"):
            target_str = (
                params.target if isinstance(params.target, str) else f"coordinates {params.target}"
            )
            return f"Camera '{params.camera_name}' is now pointing at {target_str}"
        else:
            return f"Operation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_camera_set_active",
        annotations={
            "title": "Set Active Camera",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_camera_set_active(params: CameraSetActiveInput) -> str:
        """Set the active camera.

        Args:
            params: Camera name

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "camera", "set_active", {"camera_name": params.camera_name}
        )

        if result.get("success"):
            return f"Set '{params.camera_name}' as the active camera"
        else:
            return f"Failed to set active camera: {result.get('error', {}).get('message', 'unknown error')}"
