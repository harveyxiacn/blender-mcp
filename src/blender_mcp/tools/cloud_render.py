"""
云渲染集成工具

提供云渲染服务集成的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class CloudRenderSetupInput(BaseModel):
    """配置云渲染"""
    service: str = Field("local", description="服务: local, sheepit, custom")
    api_key: Optional[str] = Field(None, description="API 密钥")
    endpoint: Optional[str] = Field(None, description="自定义端点")


class CloudRenderSubmitInput(BaseModel):
    """提交渲染任务"""
    frame_start: int = Field(1, description="开始帧")
    frame_end: int = Field(250, description="结束帧")
    output_path: str = Field(..., description="输出路径")
    samples: int = Field(128, description="采样数")
    resolution_x: int = Field(1920, description="宽度")
    resolution_y: int = Field(1080, description="高度")


class LocalFarmInput(BaseModel):
    """本地渲染农场"""
    nodes: List[str] = Field(..., description="节点地址列表")
    port: int = Field(5000, description="端口")


# ============ 工具注册 ============

def register_cloud_render_tools(mcp: FastMCP, server):
    """注册云渲染工具"""
    
    @mcp.tool()
    async def blender_cloud_render_setup(
        service: str = "local",
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        配置云渲染服务
        
        Args:
            service: 渲染服务 (local, sheepit, custom)
            api_key: API 密钥（某些服务需要）
            endpoint: 自定义服务端点
        """
        params = CloudRenderSetupInput(
            service=service,
            api_key=api_key,
            endpoint=endpoint
        )
        return await server.send_command("cloud_render", "setup", params.model_dump())
    
    @mcp.tool()
    async def blender_cloud_render_submit(
        frame_start: int = 1,
        frame_end: int = 250,
        output_path: str = "",
        samples: int = 128,
        resolution_x: int = 1920,
        resolution_y: int = 1080
    ) -> Dict[str, Any]:
        """
        提交渲染任务
        
        Args:
            frame_start: 开始帧
            frame_end: 结束帧
            output_path: 输出路径
            samples: 采样数
            resolution_x: 分辨率宽度
            resolution_y: 分辨率高度
        """
        params = CloudRenderSubmitInput(
            frame_start=frame_start,
            frame_end=frame_end,
            output_path=output_path,
            samples=samples,
            resolution_x=resolution_x,
            resolution_y=resolution_y
        )
        return await server.send_command("cloud_render", "submit", params.model_dump())
    
    @mcp.tool()
    async def blender_cloud_render_status(
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询渲染任务状态
        
        Args:
            job_id: 任务 ID（为空则查询所有任务）
        """
        return await server.send_command("cloud_render", "status", {
            "job_id": job_id
        })
    
    @mcp.tool()
    async def blender_cloud_render_cancel(
        job_id: str
    ) -> Dict[str, Any]:
        """
        取消渲染任务
        
        Args:
            job_id: 任务 ID
        """
        return await server.send_command("cloud_render", "cancel", {
            "job_id": job_id
        })
    
    @mcp.tool()
    async def blender_cloud_render_download(
        job_id: str,
        output_folder: str
    ) -> Dict[str, Any]:
        """
        下载渲染结果
        
        Args:
            job_id: 任务 ID
            output_folder: 输出文件夹
        """
        return await server.send_command("cloud_render", "download", {
            "job_id": job_id,
            "output_folder": output_folder
        })
    
    @mcp.tool()
    async def blender_render_farm_local(
        nodes: List[str],
        port: int = 5000
    ) -> Dict[str, Any]:
        """
        配置本地渲染农场
        
        Args:
            nodes: 渲染节点地址列表（如 ["192.168.1.100", "192.168.1.101"]）
            port: 端口号
        """
        params = LocalFarmInput(
            nodes=nodes,
            port=port
        )
        return await server.send_command("cloud_render", "local_farm", params.model_dump())
    
    @mcp.tool()
    async def blender_render_farm_discover() -> Dict[str, Any]:
        """
        发现局域网内的渲染节点
        """
        return await server.send_command("cloud_render", "discover", {})
    
    @mcp.tool()
    async def blender_cloud_render_estimate(
        frame_count: int,
        samples: int = 128,
        resolution_x: int = 1920,
        resolution_y: int = 1080
    ) -> Dict[str, Any]:
        """
        估算渲染成本/时间
        
        Args:
            frame_count: 帧数
            samples: 采样数
            resolution_x: 分辨率宽度
            resolution_y: 分辨率高度
        """
        return await server.send_command("cloud_render", "estimate", {
            "frame_count": frame_count,
            "samples": samples,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y
        })
