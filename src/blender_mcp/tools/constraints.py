"""
约束系统工具

提供Blender对象和骨骼约束的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class ConstraintAddInput(BaseModel):
    """添加约束"""
    object_name: str = Field(..., description="对象名称")
    constraint_type: str = Field(..., description="约束类型")
    name: Optional[str] = Field(None, description="约束名称")
    target: Optional[str] = Field(None, description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标（骨骼名）")


class ConstraintRemoveInput(BaseModel):
    """移除约束"""
    object_name: str = Field(..., description="对象名称")
    constraint_name: str = Field(..., description="约束名称")


class ConstraintCopyLocationInput(BaseModel):
    """位置约束"""
    object_name: str = Field(..., description="对象名称")
    target: str = Field(..., description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标骨骼")
    use_x: bool = Field(True, description="X轴")
    use_y: bool = Field(True, description="Y轴")
    use_z: bool = Field(True, description="Z轴")
    influence: float = Field(1.0, description="影响度")


class ConstraintCopyRotationInput(BaseModel):
    """旋转约束"""
    object_name: str = Field(..., description="对象名称")
    target: str = Field(..., description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标骨骼")
    use_x: bool = Field(True, description="X轴")
    use_y: bool = Field(True, description="Y轴")
    use_z: bool = Field(True, description="Z轴")
    influence: float = Field(1.0, description="影响度")


class ConstraintCopyScaleInput(BaseModel):
    """缩放约束"""
    object_name: str = Field(..., description="对象名称")
    target: str = Field(..., description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标骨骼")
    use_x: bool = Field(True, description="X轴")
    use_y: bool = Field(True, description="Y轴")
    use_z: bool = Field(True, description="Z轴")
    influence: float = Field(1.0, description="影响度")


class ConstraintTrackToInput(BaseModel):
    """跟踪约束"""
    object_name: str = Field(..., description="对象名称")
    target: str = Field(..., description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标骨骼")
    track_axis: str = Field("TRACK_NEGATIVE_Z", description="跟踪轴")
    up_axis: str = Field("UP_Y", description="向上轴")
    influence: float = Field(1.0, description="影响度")


class ConstraintLimitInput(BaseModel):
    """限制约束"""
    object_name: str = Field(..., description="对象名称")
    limit_type: str = Field("LOCATION", description="限制类型: LOCATION, ROTATION, SCALE")
    min_x: Optional[float] = Field(None, description="X最小值")
    max_x: Optional[float] = Field(None, description="X最大值")
    min_y: Optional[float] = Field(None, description="Y最小值")
    max_y: Optional[float] = Field(None, description="Y最大值")
    min_z: Optional[float] = Field(None, description="Z最小值")
    max_z: Optional[float] = Field(None, description="Z最大值")


class ConstraintIKInput(BaseModel):
    """IK约束（反向动力学）"""
    object_name: str = Field(..., description="骨架对象名称")
    bone_name: str = Field(..., description="骨骼名称")
    target: Optional[str] = Field(None, description="目标对象")
    subtarget: Optional[str] = Field(None, description="目标骨骼")
    pole_target: Optional[str] = Field(None, description="极向目标对象")
    pole_subtarget: Optional[str] = Field(None, description="极向目标骨骼")
    chain_count: int = Field(2, description="链长度")
    influence: float = Field(1.0, description="影响度")


class ConstraintParentInput(BaseModel):
    """父级约束"""
    object_name: str = Field(..., description="对象名称")
    target: str = Field(..., description="目标对象")
    subtarget: Optional[str] = Field(None, description="子目标骨骼")
    influence: float = Field(1.0, description="影响度")


# ============ 工具注册 ============

def register_constraint_tools(mcp: FastMCP, server):
    """注册约束工具"""
    
    @mcp.tool()
    async def blender_constraint_add(
        object_name: str,
        constraint_type: str,
        name: Optional[str] = None,
        target: Optional[str] = None,
        subtarget: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加约束
        
        Args:
            object_name: 对象名称
            constraint_type: 约束类型 (COPY_LOCATION, COPY_ROTATION, TRACK_TO, IK, etc.)
            name: 约束名称
            target: 目标对象
            subtarget: 子目标（骨骼名）
        """
        params = ConstraintAddInput(
            object_name=object_name,
            constraint_type=constraint_type,
            name=name,
            target=target,
            subtarget=subtarget
        )
        return await server.send_command("constraints", "add", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_remove(
        object_name: str,
        constraint_name: str
    ) -> Dict[str, Any]:
        """
        移除约束
        
        Args:
            object_name: 对象名称
            constraint_name: 约束名称
        """
        params = ConstraintRemoveInput(
            object_name=object_name,
            constraint_name=constraint_name
        )
        return await server.send_command("constraints", "remove", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_copy_location(
        object_name: str,
        target: str,
        subtarget: Optional[str] = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加位置复制约束
        
        Args:
            object_name: 对象名称
            target: 目标对象
            subtarget: 子目标骨骼
            use_x/y/z: 是否影响各轴
            influence: 影响度 (0-1)
        """
        params = ConstraintCopyLocationInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence
        )
        return await server.send_command("constraints", "copy_location", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_copy_rotation(
        object_name: str,
        target: str,
        subtarget: Optional[str] = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加旋转复制约束
        
        Args:
            object_name: 对象名称
            target: 目标对象
            subtarget: 子目标骨骼
            use_x/y/z: 是否影响各轴
            influence: 影响度 (0-1)
        """
        params = ConstraintCopyRotationInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence
        )
        return await server.send_command("constraints", "copy_rotation", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_copy_scale(
        object_name: str,
        target: str,
        subtarget: Optional[str] = None,
        use_x: bool = True,
        use_y: bool = True,
        use_z: bool = True,
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加缩放复制约束
        
        Args:
            object_name: 对象名称
            target: 目标对象
            subtarget: 子目标骨骼
            use_x/y/z: 是否影响各轴
            influence: 影响度 (0-1)
        """
        params = ConstraintCopyScaleInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            use_x=use_x,
            use_y=use_y,
            use_z=use_z,
            influence=influence
        )
        return await server.send_command("constraints", "copy_scale", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_track_to(
        object_name: str,
        target: str,
        subtarget: Optional[str] = None,
        track_axis: str = "TRACK_NEGATIVE_Z",
        up_axis: str = "UP_Y",
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加跟踪约束
        
        Args:
            object_name: 对象名称
            target: 目标对象
            subtarget: 子目标骨骼
            track_axis: 跟踪轴 (TRACK_X, TRACK_Y, TRACK_Z, TRACK_NEGATIVE_X/Y/Z)
            up_axis: 向上轴 (UP_X, UP_Y, UP_Z)
            influence: 影响度 (0-1)
        """
        params = ConstraintTrackToInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            track_axis=track_axis,
            up_axis=up_axis,
            influence=influence
        )
        return await server.send_command("constraints", "track_to", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_limit(
        object_name: str,
        limit_type: str = "LOCATION",
        min_x: Optional[float] = None,
        max_x: Optional[float] = None,
        min_y: Optional[float] = None,
        max_y: Optional[float] = None,
        min_z: Optional[float] = None,
        max_z: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        添加限制约束
        
        Args:
            object_name: 对象名称
            limit_type: 限制类型 (LOCATION, ROTATION, SCALE)
            min_x/max_x: X轴范围
            min_y/max_y: Y轴范围
            min_z/max_z: Z轴范围
        """
        params = ConstraintLimitInput(
            object_name=object_name,
            limit_type=limit_type,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            min_z=min_z,
            max_z=max_z
        )
        return await server.send_command("constraints", "limit", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_ik(
        object_name: str,
        bone_name: str,
        target: Optional[str] = None,
        subtarget: Optional[str] = None,
        pole_target: Optional[str] = None,
        pole_subtarget: Optional[str] = None,
        chain_count: int = 2,
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加IK约束（反向动力学）
        
        Args:
            object_name: 骨架对象名称
            bone_name: 骨骼名称
            target: 目标对象
            subtarget: 目标骨骼
            pole_target: 极向目标对象
            pole_subtarget: 极向目标骨骼
            chain_count: 链长度
            influence: 影响度 (0-1)
        """
        params = ConstraintIKInput(
            object_name=object_name,
            bone_name=bone_name,
            target=target,
            subtarget=subtarget,
            pole_target=pole_target,
            pole_subtarget=pole_subtarget,
            chain_count=chain_count,
            influence=influence
        )
        return await server.send_command("constraints", "ik", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_parent(
        object_name: str,
        target: str,
        subtarget: Optional[str] = None,
        influence: float = 1.0
    ) -> Dict[str, Any]:
        """
        添加父级约束
        
        Args:
            object_name: 对象名称
            target: 目标对象
            subtarget: 子目标骨骼
            influence: 影响度 (0-1)
        """
        params = ConstraintParentInput(
            object_name=object_name,
            target=target,
            subtarget=subtarget,
            influence=influence
        )
        return await server.send_command("constraints", "parent", params.model_dump())
    
    @mcp.tool()
    async def blender_constraint_list(
        object_name: str
    ) -> Dict[str, Any]:
        """
        列出对象的所有约束
        
        Args:
            object_name: 对象名称
        """
        return await server.send_command("constraints", "list", {"object_name": object_name})
