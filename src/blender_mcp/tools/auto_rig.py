"""
自动骨骼绑定工具

提供自动骨骼创建、权重绑定、IK/FK设置等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class AutoRigSetupInput(BaseModel):
    """自动骨骼设置输入"""
    character_name: str = Field(..., description="角色名称前缀")
    rig_type: str = Field(
        default="humanoid",
        description="骨骼类型: humanoid(人形), quadruped(四足), bird(鸟类), simple(简单)"
    )
    auto_weight: bool = Field(default=True, description="自动权重绑定")
    symmetric: bool = Field(default=True, description="对称骨骼")


class BoneAddInput(BaseModel):
    """添加骨骼输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    head: List[float] = Field(..., description="骨骼头部位置")
    tail: List[float] = Field(..., description="骨骼尾部位置")
    parent_bone: Optional[str] = Field(default=None, description="父骨骼名称")
    connect: bool = Field(default=False, description="连接到父骨骼")


class IKSetupInput(BaseModel):
    """IK设置输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="要添加IK的骨骼")
    chain_length: int = Field(default=2, description="IK链长度")
    target_name: Optional[str] = Field(default=None, description="IK目标对象")
    pole_target: Optional[str] = Field(default=None, description="极向量目标")


class WeightPaintInput(BaseModel):
    """权重绘制输入"""
    object_name: str = Field(..., description="网格对象名称")
    armature_name: str = Field(..., description="骨架名称")
    method: str = Field(
        default="automatic",
        description="方法: automatic(自动), envelope(包络), nearest(最近)"
    )


class PoseApplyInput(BaseModel):
    """应用姿势输入"""
    armature_name: str = Field(..., description="骨架名称")
    pose_name: str = Field(
        default="t_pose",
        description="姿势: t_pose, a_pose, rest, action_pose"
    )


class RigConstraintInput(BaseModel):
    """骨骼约束输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    constraint_type: str = Field(
        default="COPY_ROTATION",
        description="约束类型: COPY_ROTATION, COPY_LOCATION, LIMIT_ROTATION, DAMPED_TRACK"
    )
    target_armature: Optional[str] = Field(default=None, description="目标骨架")
    target_bone: Optional[str] = Field(default=None, description="目标骨骼")


# ==================== 工具注册 ====================

def register_auto_rig_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册自动骨骼绑定工具"""
    
    @mcp.tool(
        name="blender_rig_auto_setup",
        annotations={
            "title": "自动创建骨骼",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_rig_auto_setup(params: AutoRigSetupInput) -> str:
        """为角色自动创建骨骼系统。
        
        根据角色网格自动创建适合的骨骼结构。
        
        Args:
            params: 角色名称、骨骼类型等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "auto_rig", "setup",
            {
                "character_name": params.character_name,
                "rig_type": params.rig_type,
                "auto_weight": params.auto_weight,
                "symmetric": params.symmetric
            }
        )
        
        if result.get("success"):
            bones = result.get("data", {}).get("bones_created", 0)
            return f"成功为 '{params.character_name}' 创建 {params.rig_type} 骨骼系统，共 {bones} 根骨骼"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_rig_bone_add",
        annotations={
            "title": "添加骨骼",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_rig_bone_add(params: BoneAddInput) -> str:
        """手动添加骨骼。
        
        Args:
            params: 骨架、骨骼名称、位置等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "auto_rig", "bone_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "head": params.head,
                "tail": params.tail,
                "parent_bone": params.parent_bone,
                "connect": params.connect
            }
        )
        
        if result.get("success"):
            return f"成功添加骨骼 '{params.bone_name}'"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_rig_ik_setup",
        annotations={
            "title": "设置IK",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_rig_ik_setup(params: IKSetupInput) -> str:
        """为骨骼设置反向动力学（IK）。
        
        Args:
            params: 骨架、骨骼、链长度等
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "auto_rig", "ik_setup",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "chain_length": params.chain_length,
                "target_name": params.target_name,
                "pole_target": params.pole_target
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.bone_name}' 设置 IK（链长度: {params.chain_length}）"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_rig_weight_paint",
        annotations={
            "title": "自动权重绑定",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_rig_weight_paint(params: WeightPaintInput) -> str:
        """为网格对象进行自动权重绑定。
        
        Args:
            params: 网格对象、骨架、方法
            
        Returns:
            绑定结果
        """
        result = await server.execute_command(
            "auto_rig", "weight_paint",
            {
                "object_name": params.object_name,
                "armature_name": params.armature_name,
                "method": params.method
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 进行 {params.method} 权重绑定"
        else:
            return f"绑定失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_rig_pose_apply",
        annotations={
            "title": "应用预设姿势",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_rig_pose_apply(params: PoseApplyInput) -> str:
        """应用预设姿势到骨架。
        
        Args:
            params: 骨架名称、姿势类型
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "auto_rig", "pose_apply",
            {
                "armature_name": params.armature_name,
                "pose_name": params.pose_name
            }
        )
        
        if result.get("success"):
            return f"成功应用 {params.pose_name} 姿势"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_rig_constraint_add",
        annotations={
            "title": "添加骨骼约束",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_rig_constraint_add(params: RigConstraintInput) -> str:
        """为骨骼添加约束。
        
        Args:
            params: 骨架、骨骼、约束类型等
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "auto_rig", "constraint_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "constraint_type": params.constraint_type,
                "target_armature": params.target_armature,
                "target_bone": params.target_bone
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.bone_name}' 添加 {params.constraint_type} 约束"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
