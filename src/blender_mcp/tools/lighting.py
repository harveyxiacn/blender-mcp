"""
灯光工具

提供灯光创建和设置功能。
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class LightType(str, Enum):
    """灯光类型"""
    POINT = "POINT"      # 点光源
    SUN = "SUN"          # 太阳光
    SPOT = "SPOT"        # 聚光灯
    AREA = "AREA"        # 面光源


# ==================== 输入模型 ====================

class LightCreateInput(BaseModel):
    """创建灯光输入"""
    type: LightType = Field(..., description="灯光类型")
    name: Optional[str] = Field(default=None, description="灯光名称")
    location: Optional[List[float]] = Field(default=None, description="位置 [x, y, z]")
    rotation: Optional[List[float]] = Field(default=None, description="旋转 [x, y, z]")
    color: Optional[List[float]] = Field(default=None, description="RGB 颜色")
    energy: float = Field(default=1000.0, description="能量/强度（瓦特）", ge=0)
    radius: float = Field(default=0.25, description="灯光半径", ge=0)
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is not None and len(v) != 3:
            raise ValueError("颜色必须包含 3 个分量 (RGB)")
        return v


class LightSetPropertiesInput(BaseModel):
    """设置灯光属性输入"""
    light_name: str = Field(..., description="灯光名称")
    color: Optional[List[float]] = Field(default=None, description="RGB 颜色")
    energy: Optional[float] = Field(default=None, description="能量", ge=0)
    radius: Optional[float] = Field(default=None, description="半径", ge=0)
    spot_size: Optional[float] = Field(default=None, description="聚光灯角度（弧度）", ge=0)
    spot_blend: Optional[float] = Field(default=None, description="聚光灯边缘柔和度", ge=0, le=1)
    shadow_soft_size: Optional[float] = Field(default=None, description="阴影柔和度", ge=0)
    use_shadow: Optional[bool] = Field(default=None, description="是否投射阴影")


class LightDeleteInput(BaseModel):
    """删除灯光输入"""
    light_name: str = Field(..., description="灯光名称")


class HDRISetupInput(BaseModel):
    """HDRI 设置输入"""
    hdri_path: str = Field(..., description="HDRI 文件路径")
    strength: float = Field(default=1.0, description="环境光强度", ge=0)
    rotation: float = Field(default=0.0, description="旋转角度（弧度）")


# ==================== 工具注册 ====================

def register_lighting_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册灯光工具"""
    
    @mcp.tool(
        name="blender_light_create",
        annotations={
            "title": "创建灯光",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_light_create(params: LightCreateInput) -> str:
        """创建灯光。
        
        支持点光源、太阳光、聚光灯和面光源。
        
        Args:
            params: 灯光类型和属性
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "lighting", "create",
            {
                "type": params.type.value,
                "name": params.name,
                "location": params.location or [0, 0, 5],
                "rotation": params.rotation or [0, 0, 0],
                "color": params.color or [1, 1, 1],
                "energy": params.energy,
                "radius": params.radius
            }
        )
        
        if result.get("success"):
            name = result.get("data", {}).get("light_name", params.name or params.type.value)
            light_names = {
                "POINT": "点光源",
                "SUN": "太阳光",
                "SPOT": "聚光灯",
                "AREA": "面光源"
            }
            return f"成功创建{light_names.get(params.type.value, params.type.value)} '{name}'，能量: {params.energy}W"
        else:
            return f"创建灯光失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_light_set_properties",
        annotations={
            "title": "设置灯光属性",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_light_set_properties(params: LightSetPropertiesInput) -> str:
        """设置灯光属性。
        
        可以设置颜色、能量、阴影等属性。
        
        Args:
            params: 灯光名称和要设置的属性
            
        Returns:
            设置结果
        """
        properties = {}
        if params.color is not None:
            properties["color"] = params.color
        if params.energy is not None:
            properties["energy"] = params.energy
        if params.radius is not None:
            properties["radius"] = params.radius
        if params.spot_size is not None:
            properties["spot_size"] = params.spot_size
        if params.spot_blend is not None:
            properties["spot_blend"] = params.spot_blend
        if params.shadow_soft_size is not None:
            properties["shadow_soft_size"] = params.shadow_soft_size
        if params.use_shadow is not None:
            properties["use_shadow"] = params.use_shadow
        
        if not properties:
            return "没有指定任何属性"
        
        result = await server.execute_command(
            "lighting", "set_properties",
            {"light_name": params.light_name, "properties": properties}
        )
        
        if result.get("success"):
            return f"灯光 '{params.light_name}' 属性已更新"
        else:
            return f"设置灯光属性失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_light_delete",
        annotations={
            "title": "删除灯光",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_light_delete(params: LightDeleteInput) -> str:
        """删除灯光。
        
        Args:
            params: 灯光名称
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "lighting", "delete",
            {"light_name": params.light_name}
        )
        
        if result.get("success"):
            return f"已删除灯光 '{params.light_name}'"
        else:
            return f"删除灯光失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_hdri_setup",
        annotations={
            "title": "设置 HDRI 环境光",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_hdri_setup(params: HDRISetupInput) -> str:
        """设置 HDRI 环境光。
        
        加载 HDRI 图像作为场景的环境光照。
        
        Args:
            params: HDRI 文件路径和设置
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "lighting", "hdri_setup",
            {
                "hdri_path": params.hdri_path,
                "strength": params.strength,
                "rotation": params.rotation
            }
        )
        
        if result.get("success"):
            return f"HDRI 环境光已设置，强度: {params.strength}"
        else:
            return f"设置 HDRI 失败: {result.get('error', {}).get('message', '未知错误')}"
