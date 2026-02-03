"""
毛发系统工具

提供毛发创建和编辑的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class HairSystemInput(BaseModel):
    """添加毛发系统"""
    object_name: str = Field(..., description="对象名称")
    name: str = Field("Hair", description="毛发系统名称")
    hair_length: float = Field(0.1, description="毛发长度")
    hair_count: int = Field(1000, description="毛发数量")
    segments: int = Field(5, description="毛发段数")


class HairSettingsInput(BaseModel):
    """毛发设置"""
    object_name: str = Field(..., description="对象名称")
    system_name: Optional[str] = Field(None, description="毛发系统名称")
    hair_length: Optional[float] = Field(None, description="毛发长度")
    root_radius: Optional[float] = Field(None, description="根部半径")
    tip_radius: Optional[float] = Field(None, description="尖端半径")
    random_length: Optional[float] = Field(None, description="长度随机")
    random_rotation: Optional[float] = Field(None, description="旋转随机")


class HairDynamicsInput(BaseModel):
    """毛发动力学"""
    object_name: str = Field(..., description="对象名称")
    enable: bool = Field(True, description="启用动力学")
    stiffness: float = Field(0.5, description="刚度")
    damping: float = Field(0.1, description="阻尼")
    gravity: float = Field(1.0, description="重力影响")


class HairMaterialInput(BaseModel):
    """毛发材质"""
    object_name: str = Field(..., description="对象名称")
    color: List[float] = Field([0.1, 0.05, 0.02, 1.0], description="颜色")
    roughness: float = Field(0.4, description="粗糙度")
    use_hair_bsdf: bool = Field(True, description="使用毛发BSDF")


class HairChildrenInput(BaseModel):
    """毛发子代"""
    object_name: str = Field(..., description="对象名称")
    child_type: str = Field("INTERPOLATED", description="类型: NONE, SIMPLE, INTERPOLATED")
    child_count: int = Field(10, description="子代数量")
    clump: float = Field(0.0, description="聚集度")
    roughness: float = Field(0.0, description="粗糙度")


class HairGroomInput(BaseModel):
    """毛发梳理"""
    object_name: str = Field(..., description="对象名称")
    action: str = Field("COMB", description="操作: COMB, CUT, LENGTH, PUFF, SMOOTH")
    strength: float = Field(0.5, description="强度")


# ============ 工具注册 ============

def register_hair_tools(mcp: FastMCP, server):
    """注册毛发工具"""
    
    @mcp.tool()
    async def blender_hair_add(
        object_name: str,
        name: str = "Hair",
        hair_length: float = 0.1,
        hair_count: int = 1000,
        segments: int = 5
    ) -> Dict[str, Any]:
        """
        添加毛发系统
        
        Args:
            object_name: 目标对象名称
            name: 毛发系统名称
            hair_length: 毛发长度
            hair_count: 毛发数量
            segments: 每根毛发的段数
        """
        params = HairSystemInput(
            object_name=object_name,
            name=name,
            hair_length=hair_length,
            hair_count=hair_count,
            segments=segments
        )
        return await server.send_command("hair", "add", params.model_dump())
    
    @mcp.tool()
    async def blender_hair_settings(
        object_name: str,
        system_name: Optional[str] = None,
        hair_length: Optional[float] = None,
        root_radius: Optional[float] = None,
        tip_radius: Optional[float] = None,
        random_length: Optional[float] = None,
        random_rotation: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        设置毛发属性
        
        Args:
            object_name: 对象名称
            system_name: 毛发系统名称
            hair_length: 毛发长度
            root_radius: 根部半径
            tip_radius: 尖端半径
            random_length: 长度随机度
            random_rotation: 旋转随机度
        """
        params = HairSettingsInput(
            object_name=object_name,
            system_name=system_name,
            hair_length=hair_length,
            root_radius=root_radius,
            tip_radius=tip_radius,
            random_length=random_length,
            random_rotation=random_rotation
        )
        return await server.send_command("hair", "settings", params.model_dump())
    
    @mcp.tool()
    async def blender_hair_dynamics(
        object_name: str,
        enable: bool = True,
        stiffness: float = 0.5,
        damping: float = 0.1,
        gravity: float = 1.0
    ) -> Dict[str, Any]:
        """
        设置毛发动力学
        
        Args:
            object_name: 对象名称
            enable: 启用动力学
            stiffness: 刚度 (0-1)
            damping: 阻尼 (0-1)
            gravity: 重力影响
        """
        params = HairDynamicsInput(
            object_name=object_name,
            enable=enable,
            stiffness=stiffness,
            damping=damping,
            gravity=gravity
        )
        return await server.send_command("hair", "dynamics", params.model_dump())
    
    @mcp.tool()
    async def blender_hair_material(
        object_name: str,
        color: List[float] = [0.1, 0.05, 0.02, 1.0],
        roughness: float = 0.4,
        use_hair_bsdf: bool = True
    ) -> Dict[str, Any]:
        """
        设置毛发材质
        
        Args:
            object_name: 对象名称
            color: 毛发颜色 [R, G, B, A]
            roughness: 粗糙度
            use_hair_bsdf: 使用毛发BSDF着色器
        """
        params = HairMaterialInput(
            object_name=object_name,
            color=color,
            roughness=roughness,
            use_hair_bsdf=use_hair_bsdf
        )
        return await server.send_command("hair", "material", params.model_dump())
    
    @mcp.tool()
    async def blender_hair_children(
        object_name: str,
        child_type: str = "INTERPOLATED",
        child_count: int = 10,
        clump: float = 0.0,
        roughness: float = 0.0
    ) -> Dict[str, Any]:
        """
        设置毛发子代
        
        Args:
            object_name: 对象名称
            child_type: 子代类型 (NONE, SIMPLE, INTERPOLATED)
            child_count: 子代数量
            clump: 聚集度
            roughness: 子代粗糙度
        """
        params = HairChildrenInput(
            object_name=object_name,
            child_type=child_type,
            child_count=child_count,
            clump=clump,
            roughness=roughness
        )
        return await server.send_command("hair", "children", params.model_dump())
    
    @mcp.tool()
    async def blender_hair_groom(
        object_name: str,
        action: str = "COMB",
        strength: float = 0.5
    ) -> Dict[str, Any]:
        """
        毛发梳理操作
        
        Args:
            object_name: 对象名称
            action: 梳理操作 (COMB, CUT, LENGTH, PUFF, SMOOTH)
            strength: 操作强度
        """
        params = HairGroomInput(
            object_name=object_name,
            action=action,
            strength=strength
        )
        return await server.send_command("hair", "groom", params.model_dump())
