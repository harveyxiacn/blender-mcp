"""
对象操作工具

提供对象创建、删除、变换、选择等功能。
"""

from typing import TYPE_CHECKING, Optional, List, Union
from enum import Enum
import json

from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ObjectType(str, Enum):
    """对象类型"""
    # 网格
    CUBE = "CUBE"
    SPHERE = "SPHERE"
    UV_SPHERE = "UV_SPHERE"
    ICO_SPHERE = "ICO_SPHERE"
    CYLINDER = "CYLINDER"
    CONE = "CONE"
    TORUS = "TORUS"
    PLANE = "PLANE"
    CIRCLE = "CIRCLE"
    GRID = "GRID"
    MONKEY = "MONKEY"
    # 曲线
    BEZIER = "BEZIER"
    NURBS_CURVE = "NURBS_CURVE"
    NURBS_CIRCLE = "NURBS_CIRCLE"
    PATH = "PATH"
    # 其他
    TEXT = "TEXT"
    EMPTY = "EMPTY"
    ARMATURE = "ARMATURE"
    LATTICE = "LATTICE"
    CAMERA = "CAMERA"
    LIGHT = "LIGHT"


class ResponseFormat(str, Enum):
    """响应格式"""
    MARKDOWN = "markdown"
    JSON = "json"


# ==================== 输入模型 ====================

class Vector3(BaseModel):
    """3D 向量"""
    x: float = Field(default=0.0)
    y: float = Field(default=0.0)
    z: float = Field(default=0.0)
    
    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class ObjectCreateInput(BaseModel):
    """创建对象输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: ObjectType = Field(..., description="对象类型")
    name: Optional[str] = Field(default=None, description="对象名称", max_length=100)
    location: Optional[List[float]] = Field(
        default=None,
        description="位置坐标 [x, y, z]"
    )
    rotation: Optional[List[float]] = Field(
        default=None,
        description="旋转角度（弧度）[x, y, z]"
    )
    scale: Optional[List[float]] = Field(
        default=None,
        description="缩放 [x, y, z]"
    )
    
    @field_validator("location", "rotation", "scale")
    @classmethod
    def validate_vector(cls, v):
        if v is not None and len(v) != 3:
            raise ValueError("向量必须包含 3 个元素")
        return v


class ObjectDeleteInput(BaseModel):
    """删除对象输入"""
    name: str = Field(..., description="对象名称")
    delete_data: bool = Field(default=True, description="是否同时删除对象数据")


class ObjectDuplicateInput(BaseModel):
    """复制对象输入"""
    name: str = Field(..., description="源对象名称")
    new_name: Optional[str] = Field(default=None, description="新对象名称")
    linked: bool = Field(default=False, description="是否关联复制")
    offset: Optional[List[float]] = Field(default=None, description="位置偏移 [x, y, z]")


class ObjectTransformInput(BaseModel):
    """变换对象输入"""
    name: str = Field(..., description="对象名称")
    location: Optional[List[float]] = Field(default=None, description="新位置（绝对值）")
    rotation: Optional[List[float]] = Field(default=None, description="新旋转（弧度）")
    scale: Optional[List[float]] = Field(default=None, description="新缩放")
    delta_location: Optional[List[float]] = Field(default=None, description="位置增量")
    delta_rotation: Optional[List[float]] = Field(default=None, description="旋转增量")
    delta_scale: Optional[List[float]] = Field(default=None, description="缩放增量")


class ObjectSelectInput(BaseModel):
    """选择对象输入"""
    names: Optional[List[str]] = Field(default=None, description="要选择的对象名称列表")
    pattern: Optional[str] = Field(default=None, description="选择匹配模式（支持通配符）")
    deselect_all: bool = Field(default=True, description="是否先取消所有选择")
    set_active: Optional[str] = Field(default=None, description="设置活动对象")


class ObjectListInput(BaseModel):
    """列出对象输入"""
    type_filter: Optional[str] = Field(default=None, description="过滤对象类型")
    name_pattern: Optional[str] = Field(default=None, description="名称匹配模式")
    limit: int = Field(default=50, description="返回数量限制", ge=1, le=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ObjectGetInfoInput(BaseModel):
    """获取对象信息输入"""
    name: str = Field(..., description="对象名称")
    include_mesh_stats: bool = Field(default=True, description="包含网格统计")
    include_modifiers: bool = Field(default=True, description="包含修改器信息")
    include_materials: bool = Field(default=True, description="包含材质信息")


class ObjectRenameInput(BaseModel):
    """重命名对象输入"""
    name: str = Field(..., description="当前对象名称")
    new_name: str = Field(..., description="新名称", min_length=1, max_length=100)


class ObjectParentInput(BaseModel):
    """设置父子关系输入"""
    child_name: str = Field(..., description="子对象名称")
    parent_name: Optional[str] = Field(default=None, description="父对象名称（为空则清除父级）")
    keep_transform: bool = Field(default=True, description="保持世界变换")


class ObjectJoinInput(BaseModel):
    """合并对象输入"""
    objects: List[str] = Field(..., description="要合并的对象名称列表", min_length=2)
    target: Optional[str] = Field(default=None, description="目标对象（合并到此对象）")


# ==================== 工具注册 ====================

def register_object_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册对象操作工具"""
    
    @mcp.tool(
        name="blender_object_create",
        annotations={
            "title": "创建对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_create(params: ObjectCreateInput) -> str:
        """在 Blender 中创建新对象。
        
        支持创建各种类型的对象，包括网格（立方体、球体等）、曲线、文本等。
        
        Args:
            params: 对象类型、名称、位置、旋转、缩放
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "object", "create",
            {
                "type": params.type.value,
                "name": params.name,
                "location": params.location or [0, 0, 0],
                "rotation": params.rotation or [0, 0, 0],
                "scale": params.scale or [1, 1, 1]
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            name = data.get("object_name", params.name or params.type.value)
            return f"成功创建 {params.type.value} 对象 '{name}'，位置: {data.get('location', params.location)}"
        else:
            return f"创建对象失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_delete",
        annotations={
            "title": "删除对象",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_delete(params: ObjectDeleteInput) -> str:
        """删除指定对象。
        
        Args:
            params: 对象名称和删除选项
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "object", "delete",
            {"name": params.name, "delete_data": params.delete_data}
        )
        
        if result.get("success"):
            return f"已删除对象 '{params.name}'"
        else:
            return f"删除对象失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_duplicate",
        annotations={
            "title": "复制对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_duplicate(params: ObjectDuplicateInput) -> str:
        """复制对象。
        
        可以创建独立副本或关联副本（共享网格数据）。
        
        Args:
            params: 源对象名称、新名称、是否关联复制、位置偏移
            
        Returns:
            复制结果
        """
        result = await server.execute_command(
            "object", "duplicate",
            {
                "name": params.name,
                "new_name": params.new_name,
                "linked": params.linked,
                "offset": params.offset or [0, 0, 0]
            }
        )
        
        if result.get("success"):
            new_name = result.get("data", {}).get("new_object_name", params.new_name)
            return f"已复制对象 '{params.name}' 为 '{new_name}'"
        else:
            return f"复制对象失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_transform",
        annotations={
            "title": "变换对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_transform(params: ObjectTransformInput) -> str:
        """变换对象（位置、旋转、缩放）。
        
        可以设置绝对值或增量变换。
        
        Args:
            params: 对象名称和变换参数
            
        Returns:
            变换结果
        """
        transform = {}
        if params.location is not None:
            transform["location"] = params.location
        if params.rotation is not None:
            transform["rotation"] = params.rotation
        if params.scale is not None:
            transform["scale"] = params.scale
        if params.delta_location is not None:
            transform["delta_location"] = params.delta_location
        if params.delta_rotation is not None:
            transform["delta_rotation"] = params.delta_rotation
        if params.delta_scale is not None:
            transform["delta_scale"] = params.delta_scale
        
        if not transform:
            return "没有指定任何变换参数"
        
        result = await server.execute_command(
            "object", "transform",
            {"name": params.name, **transform}
        )
        
        if result.get("success"):
            return f"已变换对象 '{params.name}'"
        else:
            return f"变换失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_select",
        annotations={
            "title": "选择对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_select(params: ObjectSelectInput) -> str:
        """选择对象。
        
        可以通过名称列表或通配符模式选择对象。
        
        Args:
            params: 选择参数
            
        Returns:
            选择结果
        """
        result = await server.execute_command(
            "object", "select",
            {
                "names": params.names,
                "pattern": params.pattern,
                "deselect_all": params.deselect_all,
                "set_active": params.set_active
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("selected_count", 0)
            return f"已选择 {count} 个对象"
        else:
            return f"选择失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_list",
        annotations={
            "title": "列出对象",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_list(params: ObjectListInput) -> str:
        """列出场景中的对象。
        
        可以按类型或名称模式过滤。
        
        Args:
            params: 过滤和格式选项
            
        Returns:
            对象列表
        """
        result = await server.execute_command(
            "object", "list",
            {
                "type_filter": params.type_filter,
                "name_pattern": params.name_pattern,
                "limit": params.limit
            }
        )
        
        if not result.get("success"):
            return f"获取对象列表失败: {result.get('error', {}).get('message', '未知错误')}"
        
        objects = result.get("data", {}).get("objects", [])
        total = result.get("data", {}).get("total", len(objects))
        
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"objects": objects, "total": total}, indent=2)
        
        # Markdown 格式
        lines = ["# 对象列表", ""]
        lines.append(f"共 {total} 个对象" + (f"（显示 {len(objects)} 个）" if len(objects) < total else ""))
        lines.append("")
        
        for obj in objects:
            lines.append(f"## {obj['name']}")
            lines.append(f"- **类型**: {obj.get('type', '未知')}")
            lines.append(f"- **位置**: {obj.get('location', [0, 0, 0])}")
            lines.append(f"- **可见**: {'是' if obj.get('visible', True) else '否'}")
            lines.append("")
        
        return "\n".join(lines)
    
    @mcp.tool(
        name="blender_object_get_info",
        annotations={
            "title": "获取对象信息",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_get_info(params: ObjectGetInfoInput) -> str:
        """获取对象的详细信息。
        
        包括变换、网格统计、修改器、材质等信息。
        
        Args:
            params: 对象名称和包含选项
            
        Returns:
            对象详细信息
        """
        result = await server.execute_command(
            "object", "get_info",
            {
                "name": params.name,
                "include_mesh_stats": params.include_mesh_stats,
                "include_modifiers": params.include_modifiers,
                "include_materials": params.include_materials
            }
        )
        
        if not result.get("success"):
            return f"获取对象信息失败: {result.get('error', {}).get('message', '未知错误')}"
        
        data = result.get("data", {})
        
        lines = [f"# 对象: {data.get('name', params.name)}", ""]
        lines.append(f"- **类型**: {data.get('type', '未知')}")
        lines.append(f"- **位置**: {data.get('location', [0, 0, 0])}")
        lines.append(f"- **旋转**: {data.get('rotation_euler', [0, 0, 0])}")
        lines.append(f"- **缩放**: {data.get('scale', [1, 1, 1])}")
        lines.append(f"- **尺寸**: {data.get('dimensions', [0, 0, 0])}")
        
        if params.include_mesh_stats and "mesh_stats" in data:
            stats = data["mesh_stats"]
            lines.append("")
            lines.append("## 网格统计")
            lines.append(f"- 顶点: {stats.get('vertices', 0)}")
            lines.append(f"- 边: {stats.get('edges', 0)}")
            lines.append(f"- 面: {stats.get('faces', 0)}")
            lines.append(f"- 三角形: {stats.get('triangles', 0)}")
        
        if params.include_modifiers:
            mods = data.get("modifiers", [])
            if mods:
                lines.append("")
                lines.append("## 修改器")
                for mod in mods:
                    lines.append(f"- {mod}")
        
        if params.include_materials:
            mats = data.get("materials", [])
            if mats:
                lines.append("")
                lines.append("## 材质")
                for mat in mats:
                    lines.append(f"- {mat}")
        
        return "\n".join(lines)
    
    @mcp.tool(
        name="blender_object_rename",
        annotations={
            "title": "重命名对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_rename(params: ObjectRenameInput) -> str:
        """重命名对象。
        
        Args:
            params: 当前名称和新名称
            
        Returns:
            重命名结果
        """
        result = await server.execute_command(
            "object", "rename",
            {"name": params.name, "new_name": params.new_name}
        )
        
        if result.get("success"):
            return f"已将对象 '{params.name}' 重命名为 '{params.new_name}'"
        else:
            return f"重命名失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_parent",
        annotations={
            "title": "设置父子关系",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_object_parent(params: ObjectParentInput) -> str:
        """设置对象的父子关系。
        
        Args:
            params: 子对象、父对象名称
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "object", "set_parent",
            {
                "child_name": params.child_name,
                "parent_name": params.parent_name,
                "keep_transform": params.keep_transform
            }
        )
        
        if result.get("success"):
            if params.parent_name:
                return f"已将 '{params.child_name}' 设为 '{params.parent_name}' 的子对象"
            else:
                return f"已清除 '{params.child_name}' 的父级关系"
        else:
            return f"设置父子关系失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_object_join",
        annotations={
            "title": "合并对象",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_object_join(params: ObjectJoinInput) -> str:
        """合并多个对象为一个。
        
        Args:
            params: 要合并的对象列表和目标对象
            
        Returns:
            合并结果
        """
        result = await server.execute_command(
            "object", "join",
            {"objects": params.objects, "target": params.target}
        )
        
        if result.get("success"):
            target = result.get("data", {}).get("result_object", params.target or params.objects[0])
            return f"已将 {len(params.objects)} 个对象合并为 '{target}'"
        else:
            return f"合并失败: {result.get('error', {}).get('message', '未知错误')}"
