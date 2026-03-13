"""
Cloud Rendering Integration Tools

MCP tools for cloud rendering service integration.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class CloudRenderSetupInput(BaseModel):
    """Configure cloud rendering"""

    service: str = Field("local", description="Service: local, sheepit, custom")
    api_key: str | None = Field(None, description="API key")
    endpoint: str | None = Field(None, description="Custom endpoint")


class CloudRenderSubmitInput(BaseModel):
    """Submit render job"""

    frame_start: int = Field(1, description="Start frame")
    frame_end: int = Field(250, description="End frame")
    output_path: str = Field(..., description="Output path")
    samples: int = Field(128, description="Sample count")
    resolution_x: int = Field(1920, description="Width")
    resolution_y: int = Field(1080, description="Height")


class LocalFarmInput(BaseModel):
    """Local render farm"""

    nodes: list[str] = Field(..., description="Node address list")
    port: int = Field(5000, description="Port")


# ============ Tool Registration ============


def register_cloud_render_tools(mcp: FastMCP, server) -> None:
    """Register cloud rendering tools"""

    @mcp.tool()
    async def blender_cloud_render_setup(
        service: str = "local", api_key: str | None = None, endpoint: str | None = None
    ) -> dict[str, Any]:
        """
        Configure cloud rendering service

        Args:
            service: Render service (local, sheepit, custom)
            api_key: API key (required for some services)
            endpoint: Custom service endpoint
        """
        params = CloudRenderSetupInput(service=service, api_key=api_key, endpoint=endpoint)
        return await server.send_command("cloud_render", "setup", params.model_dump())

    @mcp.tool()
    async def blender_cloud_render_submit(
        frame_start: int = 1,
        frame_end: int = 250,
        output_path: str = "",
        samples: int = 128,
        resolution_x: int = 1920,
        resolution_y: int = 1080,
    ) -> dict[str, Any]:
        """
        Submit render job

        Args:
            frame_start: Start frame
            frame_end: End frame
            output_path: Output path
            samples: Sample count
            resolution_x: Resolution width
            resolution_y: Resolution height
        """
        params = CloudRenderSubmitInput(
            frame_start=frame_start,
            frame_end=frame_end,
            output_path=output_path,
            samples=samples,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
        )
        return await server.send_command("cloud_render", "submit", params.model_dump())

    @mcp.tool()
    async def blender_cloud_render_status(job_id: str | None = None) -> dict[str, Any]:
        """
        Query render job status

        Args:
            job_id: Job ID (queries all jobs if empty)
        """
        return await server.send_command("cloud_render", "status", {"job_id": job_id})

    @mcp.tool()
    async def blender_cloud_render_cancel(job_id: str) -> dict[str, Any]:
        """
        Cancel render job

        Args:
            job_id: Job ID
        """
        return await server.send_command("cloud_render", "cancel", {"job_id": job_id})

    @mcp.tool()
    async def blender_cloud_render_download(job_id: str, output_folder: str) -> dict[str, Any]:
        """
        Download render results

        Args:
            job_id: Job ID
            output_folder: Output folder
        """
        return await server.send_command(
            "cloud_render", "download", {"job_id": job_id, "output_folder": output_folder}
        )

    @mcp.tool()
    async def blender_render_farm_local(nodes: list[str], port: int = 5000) -> dict[str, Any]:
        """
        Configure local render farm

        Args:
            nodes: Render node address list (e.g. ["192.168.1.100", "192.168.1.101"])
            port: Port number
        """
        params = LocalFarmInput(nodes=nodes, port=port)
        return await server.send_command("cloud_render", "local_farm", params.model_dump())

    @mcp.tool()
    async def blender_render_farm_discover() -> dict[str, Any]:
        """
        Discover render nodes on the local network
        """
        return await server.send_command("cloud_render", "discover", {})

    @mcp.tool()
    async def blender_cloud_render_estimate(
        frame_count: int, samples: int = 128, resolution_x: int = 1920, resolution_y: int = 1080
    ) -> dict[str, Any]:
        """
        Estimate rendering cost/time

        Args:
            frame_count: Number of frames
            samples: Sample count
            resolution_x: Resolution width
            resolution_y: Resolution height
        """
        return await server.send_command(
            "cloud_render",
            "estimate",
            {
                "frame_count": frame_count,
                "samples": samples,
                "resolution_x": resolution_x,
                "resolution_y": resolution_y,
            },
        )
