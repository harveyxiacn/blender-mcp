"""
VR/AR 场景支持工具

提供 VR/AR 场景配置和导出的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class VRSetupInput(BaseModel):
    """VR 场景配置"""
    xr_runtime: str = Field("OPENXR", description="XR 运行时: OPENXR, OCULUS")
    floor_height: float = Field(0.0, description="地板高度")


class VRCameraInput(BaseModel):
    """VR 相机配置"""
    camera_type: str = Field("stereo", description="相机类型: stereo, panorama")
    ipd: float = Field(0.064, description="瞳距（米）")
    convergence_distance: float = Field(1.95, description="汇聚距离")
    location: List[float] = Field([0, 0, 1.7], description="相机位置")


class VRExportInput(BaseModel):
    """VR 导出"""
    filepath: str = Field(..., description="导出文件路径")
    format: str = Field("GLB", description="格式: GLB, GLTF")
    include_animations: bool = Field(True, description="包含动画")
    compress: bool = Field(True, description="压缩")


class ARMarkerInput(BaseModel):
    """AR 标记配置"""
    marker_name: str = Field(..., description="标记名称")
    marker_type: str = Field("image", description="类型: image, qr, plane")
    position: List[float] = Field([0, 0, 0], description="位置")
    size: float = Field(0.1, description="尺寸（米）")


class XRInteractionInput(BaseModel):
    """XR 交互点配置"""
    object_name: str = Field(..., description="对象名称")
    interaction_type: str = Field("grab", description="交互类型: grab, touch, gaze")
    highlight_color: List[float] = Field([1, 1, 0, 1], description="高亮颜色")


# ============ 工具注册 ============

def register_vr_ar_tools(mcp: FastMCP, server):
    """注册 VR/AR 工具"""
    
    @mcp.tool()
    async def blender_vr_setup(
        xr_runtime: str = "OPENXR",
        floor_height: float = 0.0
    ) -> Dict[str, Any]:
        """
        配置 VR 场景
        
        Args:
            xr_runtime: XR 运行时 (OPENXR, OCULUS)
            floor_height: 地板高度（米）
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
        创建 VR 相机
        
        Args:
            camera_type: 相机类型 (stereo, panorama)
            ipd: 瞳距（米）
            convergence_distance: 汇聚距离
            location: 相机位置
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
        导出为 VR 格式
        
        Args:
            filepath: 导出文件路径
            format: 导出格式 (GLB, GLTF)
            include_animations: 包含动画
            compress: 是否压缩
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
        创建 AR 标记点
        
        Args:
            marker_name: 标记名称
            marker_type: 标记类型 (image, qr, plane)
            position: 位置
            size: 尺寸（米）
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
        配置 XR 交互点
        
        Args:
            object_name: 对象名称
            interaction_type: 交互类型 (grab, touch, gaze)
            highlight_color: 高亮颜色
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
        启动 VR 预览
        """
        return await server.send_command("vr_ar", "preview_start", {})
    
    @mcp.tool()
    async def blender_vr_preview_stop() -> Dict[str, Any]:
        """
        停止 VR 预览
        """
        return await server.send_command("vr_ar", "preview_stop", {})
    
    @mcp.tool()
    async def blender_panorama_render(
        filepath: str,
        resolution: int = 4096,
        stereo: bool = False
    ) -> Dict[str, Any]:
        """
        渲染 360 度全景图
        
        Args:
            filepath: 输出文件路径
            resolution: 分辨率（宽度）
            stereo: 立体渲染
        """
        return await server.send_command("vr_ar", "panorama_render", {
            "filepath": filepath,
            "resolution": resolution,
            "stereo": stereo
        })
