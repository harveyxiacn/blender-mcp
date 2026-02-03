"""
相机工具

提供相机创建和设置功能。
"""

from typing import TYPE_CHECKING, Optional, List, Union

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class CameraCreateInput(BaseModel):
    """创建相机输入"""
    name: Optional[str] = Field(default="Camera", description="相机名称")
    location: Optional[List[float]] = Field(default=None, description="位置")
    rotation: Optional[List[float]] = Field(default=None, description="旋转")
    lens: float = Field(default=50.0, description="焦距 (mm)", ge=1, le=500)
    sensor_width: float = Field(default=36.0, description="传感器宽度 (mm)", ge=1)
    set_active: bool = Field(default=True, description="设为活动相机")


class CameraSetPropertiesInput(BaseModel):
    """设置相机属性输入"""
    camera_name: str = Field(..., description="相机名称")
    lens: Optional[float] = Field(default=None, description="焦距", ge=1, le=500)
    sensor_width: Optional[float] = Field(default=None, description="传感器宽度", ge=1)
    clip_start: Optional[float] = Field(default=None, description="近裁剪", gt=0)
    clip_end: Optional[float] = Field(default=None, description="远裁剪", gt=0)
    dof_focus_object: Optional[str] = Field(default=None, description="景深焦点对象")
    dof_focus_distance: Optional[float] = Field(default=None, description="景深焦点距离", ge=0)
    dof_aperture_fstop: Optional[float] = Field(default=None, description="光圈值", gt=0)


class CameraLookAtInput(BaseModel):
    """相机朝向目标输入"""
    camera_name: str = Field(..., description="相机名称")
    target: Union[str, List[float]] = Field(..., description="目标对象名称或位置坐标")
    use_constraint: bool = Field(default=False, description="使用约束（持续朝向）")


class CameraSetActiveInput(BaseModel):
    """设置活动相机输入"""
    camera_name: str = Field(..., description="相机名称")


# ==================== 工具注册 ====================

def register_camera_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册相机工具"""
    
    @mcp.tool(
        name="blender_camera_create",
        annotations={
            "title": "创建相机",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_camera_create(params: CameraCreateInput) -> str:
        """创建相机。
        
        Args:
            params: 相机名称、位置、焦距等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "camera", "create",
            {
                "name": params.name,
                "location": params.location or [0, -10, 5],
                "rotation": params.rotation or [1.1, 0, 0],
                "lens": params.lens,
                "sensor_width": params.sensor_width,
                "set_active": params.set_active
            }
        )
        
        if result.get("success"):
            name = result.get("data", {}).get("camera_name", params.name)
            return f"成功创建相机 '{name}'，焦距: {params.lens}mm"
        else:
            return f"创建相机失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_camera_set_properties",
        annotations={
            "title": "设置相机属性",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_camera_set_properties(params: CameraSetPropertiesInput) -> str:
        """设置相机属性。
        
        可以设置焦距、裁剪距离、景深等属性。
        
        Args:
            params: 相机名称和要设置的属性
            
        Returns:
            设置结果
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
            return "没有指定任何属性"
        
        result = await server.execute_command(
            "camera", "set_properties",
            {"camera_name": params.camera_name, "properties": properties}
        )
        
        if result.get("success"):
            return f"相机 '{params.camera_name}' 属性已更新"
        else:
            return f"设置相机属性失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_camera_look_at",
        annotations={
            "title": "相机朝向目标",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_camera_look_at(params: CameraLookAtInput) -> str:
        """使相机朝向指定目标。
        
        可以朝向一个对象或一个坐标点。
        
        Args:
            params: 相机名称和目标
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "camera", "look_at",
            {
                "camera_name": params.camera_name,
                "target": params.target,
                "use_constraint": params.use_constraint
            }
        )
        
        if result.get("success"):
            target_str = params.target if isinstance(params.target, str) else f"坐标 {params.target}"
            return f"相机 '{params.camera_name}' 已朝向 {target_str}"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_camera_set_active",
        annotations={
            "title": "设置活动相机",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_camera_set_active(params: CameraSetActiveInput) -> str:
        """设置活动相机。
        
        Args:
            params: 相机名称
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "camera", "set_active",
            {"camera_name": params.camera_name}
        )
        
        if result.get("success"):
            return f"已将 '{params.camera_name}' 设为活动相机"
        else:
            return f"设置活动相机失败: {result.get('error', {}).get('message', '未知错误')}"
