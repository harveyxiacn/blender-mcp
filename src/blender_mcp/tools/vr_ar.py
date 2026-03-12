"""
VR/AR Scene Support Tools

Provides MCP tools for VR/AR scene configuration and export.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class VRSetupInput(BaseModel):
    """VR scene configuration"""
    xr_runtime: str = Field("OPENXR", description="XR runtime: OPENXR, OCULUS")
    floor_height: float = Field(0.0, description="Floor height")


class VRCameraInput(BaseModel):
    """VR camera configuration"""
    camera_type: str = Field("stereo", description="Camera type: stereo, panorama")
    ipd: float = Field(0.064, description="Interpupillary distance (meters)")
    convergence_distance: float = Field(1.95, description="Convergence distance")
    location: List[float] = Field([0, 0, 1.7], description="Camera location")


class VRExportInput(BaseModel):
    """VR export"""
    filepath: str = Field(..., description="Export file path")
    format: str = Field("GLB", description="Format: GLB, GLTF")
    include_animations: bool = Field(True, description="Include animations")
    compress: bool = Field(True, description="Compress")


class ARMarkerInput(BaseModel):
    """AR marker configuration"""
    marker_name: str = Field(..., description="Marker name")
    marker_type: str = Field("image", description="Type: image, qr, plane")
    position: List[float] = Field([0, 0, 0], description="Position")
    size: float = Field(0.1, description="Size (meters)")


class XRInteractionInput(BaseModel):
    """XR interaction point configuration"""
    object_name: str = Field(..., description="Object name")
    interaction_type: str = Field("grab", description="Interaction type: grab, touch, gaze")
    highlight_color: List[float] = Field([1, 1, 0, 1], description="Highlight color")


# ============ Tool Registration ============

def register_vr_ar_tools(mcp: FastMCP, server):
    """Register VR/AR tools"""

    @mcp.tool()
    async def blender_vr_setup(
        xr_runtime: str = "OPENXR",
        floor_height: float = 0.0
    ) -> Dict[str, Any]:
        """
        Configure VR scene

        Args:
            xr_runtime: XR runtime (OPENXR, OCULUS)
            floor_height: Floor height (meters)
        """
        params = VRSetupInput(
            xr_runtime=xr_runtime,
            floor_height=floor_height
        )
        return await server.send_command("vr_ar", "setup", params.model_dump())

    @mcp.tool()
    async def blender_vr_camera(
        camera_type: str = "stereo",
        ipd: float = 0.064,
        convergence_distance: float = 1.95,
        location: List[float] = [0, 0, 1.7]
    ) -> Dict[str, Any]:
        """
        Create VR camera

        Args:
            camera_type: Camera type (stereo, panorama)
            ipd: Interpupillary distance (meters)
            convergence_distance: Convergence distance
            location: Camera location
        """
        params = VRCameraInput(
            camera_type=camera_type,
            ipd=ipd,
            convergence_distance=convergence_distance,
            location=location
        )
        return await server.send_command("vr_ar", "camera", params.model_dump())

    @mcp.tool()
    async def blender_vr_export(
        filepath: str,
        format: str = "GLB",
        include_animations: bool = True,
        compress: bool = True
    ) -> Dict[str, Any]:
        """
        Export in VR format

        Args:
            filepath: Export file path
            format: Export format (GLB, GLTF)
            include_animations: Include animations
            compress: Whether to compress
        """
        params = VRExportInput(
            filepath=filepath,
            format=format,
            include_animations=include_animations,
            compress=compress
        )
        return await server.send_command("vr_ar", "export", params.model_dump())

    @mcp.tool()
    async def blender_ar_marker(
        marker_name: str,
        marker_type: str = "image",
        position: List[float] = [0, 0, 0],
        size: float = 0.1
    ) -> Dict[str, Any]:
        """
        Create an AR marker point

        Args:
            marker_name: Marker name
            marker_type: Marker type (image, qr, plane)
            position: Position
            size: Size (meters)
        """
        params = ARMarkerInput(
            marker_name=marker_name,
            marker_type=marker_type,
            position=position,
            size=size
        )
        return await server.send_command("vr_ar", "ar_marker", params.model_dump())

    @mcp.tool()
    async def blender_xr_interaction(
        object_name: str,
        interaction_type: str = "grab",
        highlight_color: List[float] = [1, 1, 0, 1]
    ) -> Dict[str, Any]:
        """
        Configure XR interaction point

        Args:
            object_name: Object name
            interaction_type: Interaction type (grab, touch, gaze)
            highlight_color: Highlight color
        """
        params = XRInteractionInput(
            object_name=object_name,
            interaction_type=interaction_type,
            highlight_color=highlight_color
        )
        return await server.send_command("vr_ar", "xr_interaction", params.model_dump())

    @mcp.tool()
    async def blender_vr_preview_start() -> Dict[str, Any]:
        """
        Start VR preview
        """
        return await server.send_command("vr_ar", "preview_start", {})

    @mcp.tool()
    async def blender_vr_preview_stop() -> Dict[str, Any]:
        """
        Stop VR preview
        """
        return await server.send_command("vr_ar", "preview_stop", {})

    @mcp.tool()
    async def blender_panorama_render(
        filepath: str,
        resolution: int = 4096,
        stereo: bool = False
    ) -> Dict[str, Any]:
        """
        Render 360-degree panorama

        Args:
            filepath: Output file path
            resolution: Resolution (width)
            stereo: Stereo rendering
        """
        return await server.send_command("vr_ar", "panorama_render", {
            "filepath": filepath,
            "resolution": resolution,
            "stereo": stereo
        })
