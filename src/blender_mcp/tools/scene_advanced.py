"""
场景增强工具

提供环境预设、程序化生成、HDRI设置等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class EnvironmentPresetInput(BaseModel):
    """环境预设输入"""
    preset: str = Field(
        default="studio",
        description="预设: studio, outdoor_day, outdoor_night, sunset, indoor, stadium, space"
    )
    intensity: float = Field(default=1.0, description="环境光强度", ge=0)


class ScatterObjectsInput(BaseModel):
    """散布对象输入"""
    source_object: str = Field(..., description="源对象名称")
    target_surface: str = Field(..., description="目标表面名称")
    count: int = Field(default=100, description="散布数量", ge=1, le=10000)
    seed: int = Field(default=0, description="随机种子")
    scale_min: float = Field(default=0.8, description="最小缩放", ge=0.1)
    scale_max: float = Field(default=1.2, description="最大缩放", ge=0.1)
    rotation_random: bool = Field(default=True, description="随机旋转")
    align_to_normal: bool = Field(default=True, description="对齐法线")


class ArrayGenerateInput(BaseModel):
    """阵列生成输入"""
    object_name: str = Field(..., description="对象名称")
    count_x: int = Field(default=1, description="X方向数量", ge=1)
    count_y: int = Field(default=1, description="Y方向数量", ge=1)
    count_z: int = Field(default=1, description="Z方向数量", ge=1)
    offset_x: float = Field(default=2.0, description="X方向偏移")
    offset_y: float = Field(default=2.0, description="Y方向偏移")
    offset_z: float = Field(default=2.0, description="Z方向偏移")


class HDRISetupInput(BaseModel):
    """HDRI设置输入"""
    hdri_path: Optional[str] = Field(default=None, description="HDRI文件路径")
    rotation: float = Field(default=0.0, description="旋转角度 (度)")
    strength: float = Field(default=1.0, description="强度", ge=0)
    use_background: bool = Field(default=True, description="用作背景")


class GroundPlaneInput(BaseModel):
    """地面平面输入"""
    size: float = Field(default=100.0, description="尺寸", ge=1)
    material_preset: str = Field(
        default="concrete",
        description="材质预设: concrete, grass, wood, marble, sand, water"
    )
    location: Optional[List[float]] = Field(default=None, description="位置")


class SkySetupInput(BaseModel):
    """天空设置输入"""
    sky_type: str = Field(
        default="hosek_wilkie",
        description="天空类型: hosek_wilkie, preetham, nishita"
    )
    sun_elevation: float = Field(default=45.0, description="太阳仰角 (度)", ge=-90, le=90)
    sun_rotation: float = Field(default=0.0, description="太阳方位角 (度)")
    turbidity: float = Field(default=2.0, description="浑浊度", ge=1, le=10)


class FogAddInput(BaseModel):
    """添加雾效输入"""
    density: float = Field(default=0.1, description="密度", ge=0)
    color: Optional[List[float]] = Field(default=None, description="颜色 RGB")
    height: float = Field(default=0.0, description="雾高度")
    falloff: float = Field(default=1.0, description="衰减", ge=0)


# ==================== 工具注册 ====================

def register_scene_advanced_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册场景增强工具"""
    
    @mcp.tool(
        name="blender_scene_environment_preset",
        annotations={
            "title": "应用环境预设",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_environment_preset(params: EnvironmentPresetInput) -> str:
        """应用环境预设。
        
        可用预设:
        - studio: 摄影棚灯光
        - outdoor_day: 户外白天
        - outdoor_night: 户外夜晚
        - sunset: 日落
        - indoor: 室内
        - stadium: 体育场
        - space: 太空
        
        Args:
            params: 预设类型、强度
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "scene_advanced", "environment_preset",
            {
                "preset": params.preset,
                "intensity": params.intensity
            }
        )
        
        if result.get("success"):
            return f"成功应用 {params.preset} 环境预设"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_scatter",
        annotations={
            "title": "散布对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_scatter(params: ScatterObjectsInput) -> str:
        """在表面上散布对象（草、树、石头等）。
        
        Args:
            params: 源对象、目标表面、数量等
            
        Returns:
            散布结果
        """
        result = await server.execute_command(
            "scene_advanced", "scatter",
            {
                "source_object": params.source_object,
                "target_surface": params.target_surface,
                "count": params.count,
                "seed": params.seed,
                "scale_min": params.scale_min,
                "scale_max": params.scale_max,
                "rotation_random": params.rotation_random,
                "align_to_normal": params.align_to_normal
            }
        )
        
        if result.get("success"):
            created = result.get("data", {}).get("instances_created", 0)
            return f"成功散布 {created} 个 '{params.source_object}' 实例"
        else:
            return f"散布失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_array_generate",
        annotations={
            "title": "阵列生成",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_array_generate(params: ArrayGenerateInput) -> str:
        """生成对象阵列（建筑、座位等）。
        
        Args:
            params: 对象、各方向数量和偏移
            
        Returns:
            生成结果
        """
        result = await server.execute_command(
            "scene_advanced", "array_generate",
            {
                "object_name": params.object_name,
                "count_x": params.count_x,
                "count_y": params.count_y,
                "count_z": params.count_z,
                "offset_x": params.offset_x,
                "offset_y": params.offset_y,
                "offset_z": params.offset_z
            }
        )
        
        if result.get("success"):
            total = params.count_x * params.count_y * params.count_z
            return f"成功生成 {total} 个对象阵列"
        else:
            return f"生成失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_ground_plane",
        annotations={
            "title": "创建地面",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_scene_ground_plane(params: GroundPlaneInput) -> str:
        """创建带材质的地面平面。
        
        Args:
            params: 尺寸、材质预设、位置
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "scene_advanced", "ground_plane",
            {
                "size": params.size,
                "material_preset": params.material_preset,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            return f"成功创建 {params.material_preset} 材质地面 ({params.size}m)"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_sky_setup",
        annotations={
            "title": "设置天空",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_sky_setup(params: SkySetupInput) -> str:
        """设置程序化天空。
        
        Args:
            params: 天空类型、太阳位置等
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "scene_advanced", "sky_setup",
            {
                "sky_type": params.sky_type,
                "sun_elevation": params.sun_elevation,
                "sun_rotation": params.sun_rotation,
                "turbidity": params.turbidity
            }
        )
        
        if result.get("success"):
            return f"成功设置 {params.sky_type} 天空"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_scene_fog_add",
        annotations={
            "title": "添加雾效",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_scene_fog_add(params: FogAddInput) -> str:
        """添加体积雾效果。
        
        Args:
            params: 密度、颜色、高度等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "scene_advanced", "fog_add",
            {
                "density": params.density,
                "color": params.color or [0.8, 0.9, 1.0],
                "height": params.height,
                "falloff": params.falloff
            }
        )
        
        if result.get("success"):
            return f"成功添加雾效 (密度: {params.density})"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
