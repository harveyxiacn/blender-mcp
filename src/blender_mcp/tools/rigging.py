"""
骨骼绑定工具

提供骨架创建、骨骼添加、IK 设置等功能。
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class RigType(str, Enum):
    """绑定类型"""
    HUMAN = "HUMAN"
    QUADRUPED = "QUADRUPED"
    BIRD = "BIRD"
    BASIC = "BASIC"


# ==================== 输入模型 ====================

class ArmatureCreateInput(BaseModel):
    """创建骨架输入"""
    name: Optional[str] = Field(default="Armature", description="骨架名称")
    location: Optional[List[float]] = Field(default=None, description="位置")


class BoneAddInput(BaseModel):
    """添加骨骼输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    head: List[float] = Field(..., description="骨头位置 [x, y, z]")
    tail: List[float] = Field(..., description="骨尾位置 [x, y, z]")
    parent: Optional[str] = Field(default=None, description="父骨骼名称")
    use_connect: bool = Field(default=False, description="连接到父骨骼")


class ArmatureGenerateRigInput(BaseModel):
    """生成绑定输入"""
    target_mesh: str = Field(..., description="目标网格名称")
    rig_type: RigType = Field(default=RigType.HUMAN, description="绑定类型")
    auto_weights: bool = Field(default=True, description="自动计算权重")


class IKSetupInput(BaseModel):
    """IK 设置输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    target: str = Field(..., description="目标对象或骨骼")
    chain_length: int = Field(default=2, description="IK 链长度", ge=1, le=10)
    pole_target: Optional[str] = Field(default=None, description="极向量目标")


class PoseSetInput(BaseModel):
    """设置姿势输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    location: Optional[List[float]] = Field(default=None, description="位置")
    rotation: Optional[List[float]] = Field(default=None, description="旋转（欧拉角）")
    rotation_mode: str = Field(default="XYZ", description="旋转模式")


class WeightPaintInput(BaseModel):
    """权重绘制输入"""
    mesh_name: str = Field(..., description="网格名称")
    armature_name: str = Field(..., description="骨架名称")
    auto_normalize: bool = Field(default=True, description="自动归一化权重")


class BindType(str, Enum):
    """绑定类型"""
    AUTO = "AUTO"           # 自动权重（推荐）
    ENVELOPE = "ENVELOPE"   # 包络线权重
    EMPTY = "EMPTY"         # 仅绑定，不设置权重


class ArmatureBindInput(BaseModel):
    """骨架绑定输入"""
    mesh_name: str = Field(..., description="网格对象名称")
    armature_name: str = Field(..., description="骨架对象名称")
    bind_type: BindType = Field(
        default=BindType.AUTO,
        description="绑定类型: AUTO(自动权重), ENVELOPE(包络线权重), EMPTY(仅绑定)"
    )
    preserve_volume: bool = Field(
        default=True,
        description="保持体积（防止关节处变形过度）"
    )


class VertexGroupCreateInput(BaseModel):
    """创建顶点组输入"""
    object_name: str = Field(..., description="对象名称")
    group_name: str = Field(..., description="顶点组名称")
    vertex_indices: Optional[List[int]] = Field(default=None, description="顶点索引列表")
    weight: float = Field(default=1.0, description="权重值 (0.0-1.0)", ge=0, le=1)


class VertexGroupAssignMode(str, Enum):
    """顶点组分配模式"""
    REPLACE = "REPLACE"     # 替换
    ADD = "ADD"             # 添加
    SUBTRACT = "SUBTRACT"   # 减去


class VertexGroupAssignInput(BaseModel):
    """分配顶点到顶点组输入"""
    object_name: str = Field(..., description="对象名称")
    group_name: str = Field(..., description="顶点组名称")
    vertex_indices: List[int] = Field(..., description="顶点索引列表")
    weight: float = Field(default=1.0, description="权重值 (0.0-1.0)", ge=0, le=1)
    mode: VertexGroupAssignMode = Field(default=VertexGroupAssignMode.REPLACE, description="分配模式")


class ConstraintType(str, Enum):
    """约束类型"""
    IK = "IK"
    COPY_ROTATION = "COPY_ROTATION"
    COPY_LOCATION = "COPY_LOCATION"
    COPY_TRANSFORMS = "COPY_TRANSFORMS"
    LIMIT_ROTATION = "LIMIT_ROTATION"
    LIMIT_LOCATION = "LIMIT_LOCATION"
    DAMPED_TRACK = "DAMPED_TRACK"
    STRETCH_TO = "STRETCH_TO"
    FLOOR = "FLOOR"


class BoneConstraintAddInput(BaseModel):
    """添加骨骼约束输入"""
    armature_name: str = Field(..., description="骨架名称")
    bone_name: str = Field(..., description="骨骼名称")
    constraint_type: ConstraintType = Field(..., description="约束类型")
    settings: Optional[dict] = Field(default=None, description="约束设置")


# ==================== 工具注册 ====================

def register_rigging_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册骨骼绑定工具"""
    
    @mcp.tool(
        name="blender_armature_create",
        annotations={
            "title": "创建骨架",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_create(params: ArmatureCreateInput) -> str:
        """创建骨架对象。
        
        Args:
            params: 骨架名称和位置
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "rigging", "armature_create",
            {
                "name": params.name,
                "location": params.location or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            name = result.get("data", {}).get("armature_name", params.name)
            return f"成功创建骨架 '{name}'"
        else:
            return f"创建骨架失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_bone_add",
        annotations={
            "title": "添加骨骼",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_bone_add(params: BoneAddInput) -> str:
        """向骨架添加骨骼。
        
        Args:
            params: 骨架名称、骨骼名称、位置、父级
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "rigging", "bone_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "head": params.head,
                "tail": params.tail,
                "parent": params.parent,
                "use_connect": params.use_connect
            }
        )
        
        if result.get("success"):
            return f"已添加骨骼 '{params.bone_name}' 到骨架 '{params.armature_name}'"
        else:
            return f"添加骨骼失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_armature_generate_rig",
        annotations={
            "title": "生成角色绑定",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_generate_rig(params: ArmatureGenerateRigInput) -> str:
        """使用 Rigify 生成完整的角色绑定。
        
        支持人形、四足动物、鸟类等不同类型的绑定。
        
        Args:
            params: 目标网格、绑定类型、是否自动权重
            
        Returns:
            生成结果
        """
        result = await server.execute_command(
            "rigging", "generate_rig",
            {
                "target_mesh": params.target_mesh,
                "rig_type": params.rig_type.value,
                "auto_weights": params.auto_weights
            }
        )
        
        if result.get("success"):
            rig_names = {
                "HUMAN": "人形",
                "QUADRUPED": "四足动物",
                "BIRD": "鸟类",
                "BASIC": "基础"
            }
            return f"已为 '{params.target_mesh}' 生成{rig_names.get(params.rig_type.value)}绑定"
        else:
            return f"生成绑定失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_ik_setup",
        annotations={
            "title": "设置 IK",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_ik_setup(params: IKSetupInput) -> str:
        """设置反向运动学 (IK) 约束。
        
        Args:
            params: 骨架名称、骨骼名称、目标、链长度
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "rigging", "ik_setup",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "target": params.target,
                "chain_length": params.chain_length,
                "pole_target": params.pole_target
            }
        )
        
        if result.get("success"):
            return f"已为骨骼 '{params.bone_name}' 设置 IK 约束"
        else:
            return f"设置 IK 失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_pose_set",
        annotations={
            "title": "设置姿势",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_pose_set(params: PoseSetInput) -> str:
        """设置骨骼姿势。
        
        Args:
            params: 骨架名称、骨骼名称、位置、旋转
            
        Returns:
            设置结果
        """
        pose = {}
        if params.location is not None:
            pose["location"] = params.location
        if params.rotation is not None:
            pose["rotation"] = params.rotation
            pose["rotation_mode"] = params.rotation_mode
        
        if not pose:
            return "没有指定任何姿势参数"
        
        result = await server.execute_command(
            "rigging", "pose_set",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                **pose
            }
        )
        
        if result.get("success"):
            return f"已设置骨骼 '{params.bone_name}' 的姿势"
        else:
            return f"设置姿势失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_weight_paint",
        annotations={
            "title": "自动权重绘制",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_weight_paint(params: WeightPaintInput) -> str:
        """自动为网格计算骨骼权重。
        
        Args:
            params: 网格名称和骨架名称
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "rigging", "weight_paint",
            {
                "mesh_name": params.mesh_name,
                "armature_name": params.armature_name,
                "auto_normalize": params.auto_normalize
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.mesh_name}' 计算骨骼权重"
        else:
            return f"权重绘制失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_armature_bind",
        annotations={
            "title": "骨架绑定",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_armature_bind(params: ArmatureBindInput) -> str:
        """将网格绑定到骨架。
        
        支持自动权重、包络线权重或仅绑定三种模式。
        
        Args:
            params: 网格名称、骨架名称、绑定类型
            
        Returns:
            绑定结果
        """
        result = await server.execute_command(
            "rigging", "armature_bind",
            {
                "mesh_name": params.mesh_name,
                "armature_name": params.armature_name,
                "bind_type": params.bind_type.value,
                "preserve_volume": params.preserve_volume
            }
        )
        
        if result.get("success"):
            bind_names = {
                "AUTO": "自动权重",
                "ENVELOPE": "包络线权重",
                "EMPTY": "仅绑定"
            }
            return f"已将 '{params.mesh_name}' 绑定到 '{params.armature_name}'（{bind_names.get(params.bind_type.value, params.bind_type.value)}）"
        else:
            return f"绑定失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vertex_group_create",
        annotations={
            "title": "创建顶点组",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group_create(params: VertexGroupCreateInput) -> str:
        """创建顶点组。
        
        顶点组用于骨骼权重、材质分配等。
        
        Args:
            params: 对象名称、组名称、顶点列表
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "rigging", "vertex_group_create",
            {
                "object_name": params.object_name,
                "group_name": params.group_name,
                "vertex_indices": params.vertex_indices or [],
                "weight": params.weight
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已创建顶点组 '{data.get('group_name', params.group_name)}'（索引: {data.get('group_index', 'N/A')}）"
        else:
            return f"创建顶点组失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_vertex_group_assign",
        annotations={
            "title": "分配顶点到顶点组",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group_assign(params: VertexGroupAssignInput) -> str:
        """将顶点分配到顶点组。
        
        Args:
            params: 对象名称、组名称、顶点列表、权重、模式
            
        Returns:
            分配结果
        """
        result = await server.execute_command(
            "rigging", "vertex_group_assign",
            {
                "object_name": params.object_name,
                "group_name": params.group_name,
                "vertex_indices": params.vertex_indices,
                "weight": params.weight,
                "mode": params.mode.value
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已将 {data.get('assigned_count', len(params.vertex_indices))} 个顶点分配到 '{params.group_name}'"
        else:
            return f"分配顶点失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_bone_constraint_add",
        annotations={
            "title": "添加骨骼约束",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_bone_constraint_add(params: BoneConstraintAddInput) -> str:
        """为骨骼添加约束。
        
        支持 IK、复制旋转、复制位置等多种约束类型。
        
        Args:
            params: 骨架名称、骨骼名称、约束类型、设置
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "rigging", "bone_constraint_add",
            {
                "armature_name": params.armature_name,
                "bone_name": params.bone_name,
                "constraint_type": params.constraint_type.value,
                "settings": params.settings or {}
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已为骨骼 '{params.bone_name}' 添加 {params.constraint_type.value} 约束"
        else:
            return f"添加约束失败: {result.get('error', {}).get('message', '未知错误')}"
