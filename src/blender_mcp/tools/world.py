"""
世界/环境工具

提供Blender世界和环境设置的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class WorldCreateInput(BaseModel):
    """创建世界"""
    name: str = Field("World", description="世界名称")
    use_nodes: bool = Field(True, description="使用节点")


class WorldBackgroundInput(BaseModel):
    """设置背景"""
    color: Optional[List[float]] = Field(None, description="背景颜色 [R, G, B]")
    strength: float = Field(1.0, description="强度")
    use_sky_texture: bool = Field(False, description="使用天空纹理")


class WorldHDRIInput(BaseModel):
    """设置HDRI环境"""
    hdri_path: str = Field(..., description="HDRI文件路径")
    strength: float = Field(1.0, description="强度")
    rotation: float = Field(0.0, description="旋转角度（弧度）")


class WorldSkyInput(BaseModel):
    """设置程序化天空"""
    sky_type: str = Field("NISHITA", description="天空类型: PREETHAM, HOSEK_WILKIE, NISHITA")
    sun_elevation: float = Field(0.785, description="太阳高度（弧度）")
    sun_rotation: float = Field(0.0, description="太阳旋转（弧度）")
    air_density: float = Field(1.0, description="空气密度")
    dust_density: float = Field(0.0, description="尘埃密度")
    ozone_density: float = Field(1.0, description="臭氧密度")


class WorldFogInput(BaseModel):
    """设置体积雾"""
    use_fog: bool = Field(True, description="启用雾")
    density: float = Field(0.01, description="密度")
    color: List[float] = Field([0.5, 0.6, 0.7], description="颜色")
    anisotropy: float = Field(0.0, description="各向异性")


class WorldAmbientOcclusionInput(BaseModel):
    """设置环境光遮蔽"""
    use_ao: bool = Field(True, description="启用AO")
    distance: float = Field(1.0, description="距离")
    factor: float = Field(1.0, description="因子")


# ============ 工具注册 ============

def register_world_tools(mcp: FastMCP, server):
    """注册世界/环境工具"""
    
    @mcp.tool()
    async def blender_world_create(
        name: str = "World",
        use_nodes: bool = True
    ) -> Dict[str, Any]:
        """
        创建新世界
        
        Args:
            name: 世界名称
            use_nodes: 是否使用节点
        """
        params = WorldCreateInput(name=name, use_nodes=use_nodes)
        return await server.send_command("world", "create", params.model_dump())
    
    @mcp.tool()
    async def blender_world_background(
        color: Optional[List[float]] = None,
        strength: float = 1.0,
        use_sky_texture: bool = False
    ) -> Dict[str, Any]:
        """
        设置世界背景
        
        Args:
            color: 背景颜色 [R, G, B]
            strength: 强度
            use_sky_texture: 使用天空纹理
        """
        params = WorldBackgroundInput(
            color=color,
            strength=strength,
            use_sky_texture=use_sky_texture
        )
        return await server.send_command("world", "background", params.model_dump())
    
    @mcp.tool()
    async def blender_world_hdri(
        hdri_path: str,
        strength: float = 1.0,
        rotation: float = 0.0
    ) -> Dict[str, Any]:
        """
        设置HDRI环境贴图
        
        Args:
            hdri_path: HDRI文件路径
            strength: 环境光强度
            rotation: 旋转角度（弧度）
        """
        params = WorldHDRIInput(
            hdri_path=hdri_path,
            strength=strength,
            rotation=rotation
        )
        return await server.send_command("world", "hdri", params.model_dump())
    
    @mcp.tool()
    async def blender_world_sky(
        sky_type: str = "NISHITA",
        sun_elevation: float = 0.785,
        sun_rotation: float = 0.0,
        air_density: float = 1.0,
        dust_density: float = 0.0,
        ozone_density: float = 1.0
    ) -> Dict[str, Any]:
        """
        设置程序化天空
        
        Args:
            sky_type: 天空类型 (PREETHAM, HOSEK_WILKIE, NISHITA)
            sun_elevation: 太阳高度（弧度）
            sun_rotation: 太阳旋转（弧度）
            air_density: 空气密度
            dust_density: 尘埃密度
            ozone_density: 臭氧密度
        """
        params = WorldSkyInput(
            sky_type=sky_type,
            sun_elevation=sun_elevation,
            sun_rotation=sun_rotation,
            air_density=air_density,
            dust_density=dust_density,
            ozone_density=ozone_density
        )
        return await server.send_command("world", "sky", params.model_dump())
    
    @mcp.tool()
    async def blender_world_fog(
        use_fog: bool = True,
        density: float = 0.01,
        color: List[float] = [0.5, 0.6, 0.7],
        anisotropy: float = 0.0
    ) -> Dict[str, Any]:
        """
        设置体积雾
        
        Args:
            use_fog: 启用雾
            density: 雾密度
            color: 雾颜色 [R, G, B]
            anisotropy: 各向异性
        """
        params = WorldFogInput(
            use_fog=use_fog,
            density=density,
            color=color,
            anisotropy=anisotropy
        )
        return await server.send_command("world", "fog", params.model_dump())
    
    @mcp.tool()
    async def blender_world_ambient_occlusion(
        use_ao: bool = True,
        distance: float = 1.0,
        factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        设置环境光遮蔽
        
        Args:
            use_ao: 启用环境光遮蔽
            distance: AO距离
            factor: AO因子
        """
        params = WorldAmbientOcclusionInput(
            use_ao=use_ao,
            distance=distance,
            factor=factor
        )
        return await server.send_command("world", "ambient_occlusion", params.model_dump())
