"""
物理模拟工具

提供布料、刚体、粒子系统等物理模拟功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class ClothAddInput(BaseModel):
    """添加布料模拟输入"""
    object_name: str = Field(..., description="网格对象名称")
    preset: str = Field(
        default="cotton",
        description="布料预设: cotton, silk, leather, denim, rubber"
    )
    pin_group: Optional[str] = Field(default=None, description="固定顶点组")
    collision_quality: int = Field(default=2, description="碰撞质量", ge=1, le=10)


class RigidBodyAddInput(BaseModel):
    """添加刚体输入"""
    object_name: str = Field(..., description="对象名称")
    body_type: str = Field(default="ACTIVE", description="类型: ACTIVE(活动), PASSIVE(被动)")
    shape: str = Field(default="CONVEX_HULL", description="碰撞形状: BOX, SPHERE, CAPSULE, CYLINDER, CONE, CONVEX_HULL, MESH")
    mass: float = Field(default=1.0, description="质量 (kg)", ge=0)
    friction: float = Field(default=0.5, description="摩擦力", ge=0, le=1)
    bounciness: float = Field(default=0.0, description="弹性", ge=0, le=1)


class CollisionAddInput(BaseModel):
    """添加碰撞体输入"""
    object_name: str = Field(..., description="对象名称")
    damping: float = Field(default=0.0, description="阻尼", ge=0, le=1)
    thickness: float = Field(default=0.02, description="厚度", ge=0)
    friction: float = Field(default=0.0, description="摩擦力", ge=0, le=1)


class ParticleSystemInput(BaseModel):
    """粒子系统输入"""
    object_name: str = Field(..., description="发射器对象名称")
    particle_type: str = Field(default="EMITTER", description="类型: EMITTER, HAIR")
    count: int = Field(default=1000, description="粒子数量", ge=1, le=100000)
    lifetime: float = Field(default=50.0, description="生命周期 (帧)", ge=1)
    emit_from: str = Field(default="FACE", description="发射位置: VERT, FACE, VOLUME")
    velocity_normal: float = Field(default=1.0, description="法向速度")


class ForceFieldInput(BaseModel):
    """力场输入"""
    force_type: str = Field(
        default="WIND",
        description="力场类型: WIND, VORTEX, TURBULENCE, DRAG, FORCE, MAGNETIC"
    )
    location: Optional[List[float]] = Field(default=None, description="位置")
    strength: float = Field(default=1.0, description="强度")
    flow: float = Field(default=0.0, description="流动")


class SoftBodyAddInput(BaseModel):
    """添加软体输入"""
    object_name: str = Field(..., description="对象名称")
    mass: float = Field(default=1.0, description="质量", ge=0)
    friction: float = Field(default=0.5, description="摩擦力", ge=0, le=1)
    goal_strength: float = Field(default=0.7, description="目标强度", ge=0, le=1)


# ==================== 工具注册 ====================

def register_physics_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册物理模拟工具"""
    
    @mcp.tool(
        name="blender_physics_cloth_add",
        annotations={
            "title": "添加布料模拟",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_cloth_add(params: ClothAddInput) -> str:
        """为网格添加布料模拟。
        
        Args:
            params: 对象名称、布料预设等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "physics", "cloth_add",
            {
                "object_name": params.object_name,
                "preset": params.preset,
                "pin_group": params.pin_group,
                "collision_quality": params.collision_quality
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 添加 {params.preset} 布料模拟"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_physics_rigid_body_add",
        annotations={
            "title": "添加刚体",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_rigid_body_add(params: RigidBodyAddInput) -> str:
        """为对象添加刚体物理。
        
        Args:
            params: 对象名称、类型、质量等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "physics", "rigid_body_add",
            {
                "object_name": params.object_name,
                "body_type": params.body_type,
                "shape": params.shape,
                "mass": params.mass,
                "friction": params.friction,
                "bounciness": params.bounciness
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 添加 {params.body_type} 刚体"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_physics_collision_add",
        annotations={
            "title": "添加碰撞体",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_collision_add(params: CollisionAddInput) -> str:
        """为对象添加碰撞体（用于布料/软体碰撞）。
        
        Args:
            params: 对象名称、阻尼、厚度等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "physics", "collision_add",
            {
                "object_name": params.object_name,
                "damping": params.damping,
                "thickness": params.thickness,
                "friction": params.friction
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 添加碰撞体"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_physics_particles_create",
        annotations={
            "title": "创建粒子系统",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_particles_create(params: ParticleSystemInput) -> str:
        """创建粒子系统。
        
        Args:
            params: 发射器、粒子数量、生命周期等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "physics", "particles_create",
            {
                "object_name": params.object_name,
                "particle_type": params.particle_type,
                "count": params.count,
                "lifetime": params.lifetime,
                "emit_from": params.emit_from,
                "velocity_normal": params.velocity_normal
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 创建粒子系统 ({params.count} 粒子)"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_physics_force_field_add",
        annotations={
            "title": "添加力场",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_force_field_add(params: ForceFieldInput) -> str:
        """添加力场（风、涡流、湍流等）。
        
        Args:
            params: 力场类型、位置、强度等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "physics", "force_field_add",
            {
                "force_type": params.force_type,
                "location": params.location or [0, 0, 0],
                "strength": params.strength,
                "flow": params.flow
            }
        )
        
        if result.get("success"):
            return f"成功创建 {params.force_type} 力场"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_physics_soft_body_add",
        annotations={
            "title": "添加软体",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_physics_soft_body_add(params: SoftBodyAddInput) -> str:
        """为对象添加软体模拟。
        
        Args:
            params: 对象名称、质量、摩擦力等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "physics", "soft_body_add",
            {
                "object_name": params.object_name,
                "mass": params.mass,
                "friction": params.friction,
                "goal_strength": params.goal_strength
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 添加软体模拟"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
