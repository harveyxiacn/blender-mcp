"""
批量处理工具

提供批量材质应用、变换、重命名、导出等功能。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class BatchMaterialInput(BaseModel):
    """批量应用材质输入"""
    pattern: str = Field(..., description="对象名称模式 (支持通配符 *)")
    material_name: str = Field(..., description="材质名称")
    replace_existing: bool = Field(default=True, description="替换现有材质")


class BatchTransformInput(BaseModel):
    """批量变换输入"""
    pattern: str = Field(..., description="对象名称模式")
    location_offset: Optional[List[float]] = Field(default=None, description="位置偏移")
    rotation_offset: Optional[List[float]] = Field(default=None, description="旋转偏移")
    scale_factor: Optional[List[float]] = Field(default=None, description="缩放系数")


class BatchRenameInput(BaseModel):
    """批量重命名输入"""
    pattern: str = Field(..., description="对象名称模式")
    new_name: str = Field(..., description="新名称前缀")
    numbering: bool = Field(default=True, description="添加编号")
    start_number: int = Field(default=1, description="起始编号")


class BatchDeleteInput(BaseModel):
    """批量删除输入"""
    pattern: str = Field(..., description="对象名称模式")
    delete_data: bool = Field(default=True, description="删除关联数据")


class BatchExportInput(BaseModel):
    """批量导出输入"""
    pattern: str = Field(..., description="对象名称模式")
    export_path: str = Field(..., description="导出目录路径")
    format: str = Field(default="fbx", description="格式: fbx, obj, gltf")
    individual_files: bool = Field(default=True, description="每个对象单独文件")


class BatchModifierInput(BaseModel):
    """批量添加修改器输入"""
    pattern: str = Field(..., description="对象名称模式")
    modifier_type: str = Field(..., description="修改器类型: SUBSURF, BEVEL, SOLIDIFY, MIRROR")
    settings: Optional[dict] = Field(default=None, description="修改器设置")


class BatchParentInput(BaseModel):
    """批量设置父对象输入"""
    pattern: str = Field(..., description="子对象名称模式")
    parent_name: str = Field(..., description="父对象名称")
    keep_transform: bool = Field(default=True, description="保持变换")


# ==================== 工具注册 ====================

def register_batch_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册批量处理工具"""
    
    @mcp.tool(
        name="blender_batch_apply_material",
        annotations={
            "title": "批量应用材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_apply_material(params: BatchMaterialInput) -> str:
        """批量为匹配的对象应用材质。
        
        Args:
            params: 对象模式、材质名称等
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "batch", "apply_material",
            {
                "pattern": params.pattern,
                "material_name": params.material_name,
                "replace_existing": params.replace_existing
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("objects_affected", 0)
            return f"成功为 {count} 个对象应用材质 '{params.material_name}'"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_transform",
        annotations={
            "title": "批量变换",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_transform(params: BatchTransformInput) -> str:
        """批量变换匹配的对象。
        
        Args:
            params: 对象模式、位置/旋转/缩放偏移
            
        Returns:
            变换结果
        """
        result = await server.execute_command(
            "batch", "transform",
            {
                "pattern": params.pattern,
                "location_offset": params.location_offset,
                "rotation_offset": params.rotation_offset,
                "scale_factor": params.scale_factor
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("objects_affected", 0)
            return f"成功变换 {count} 个对象"
        else:
            return f"变换失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_rename",
        annotations={
            "title": "批量重命名",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_batch_rename(params: BatchRenameInput) -> str:
        """批量重命名匹配的对象。
        
        Args:
            params: 对象模式、新名称、编号等
            
        Returns:
            重命名结果
        """
        result = await server.execute_command(
            "batch", "rename",
            {
                "pattern": params.pattern,
                "new_name": params.new_name,
                "numbering": params.numbering,
                "start_number": params.start_number
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("objects_renamed", 0)
            return f"成功重命名 {count} 个对象"
        else:
            return f"重命名失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_delete",
        annotations={
            "title": "批量删除",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_delete(params: BatchDeleteInput) -> str:
        """批量删除匹配的对象。
        
        Args:
            params: 对象模式、是否删除数据
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "batch", "delete",
            {
                "pattern": params.pattern,
                "delete_data": params.delete_data
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("objects_deleted", 0)
            return f"成功删除 {count} 个对象"
        else:
            return f"删除失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_export",
        annotations={
            "title": "批量导出",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_batch_export(params: BatchExportInput) -> str:
        """批量导出匹配的对象。
        
        Args:
            params: 对象模式、导出路径、格式等
            
        Returns:
            导出结果
        """
        result = await server.execute_command(
            "batch", "export",
            {
                "pattern": params.pattern,
                "export_path": params.export_path,
                "format": params.format,
                "individual_files": params.individual_files
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("files_exported", 0)
            return f"成功导出 {count} 个文件到 '{params.export_path}'"
        else:
            return f"导出失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_add_modifier",
        annotations={
            "title": "批量添加修改器",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_batch_add_modifier(params: BatchModifierInput) -> str:
        """批量为匹配的对象添加修改器。
        
        Args:
            params: 对象模式、修改器类型、设置
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "batch", "add_modifier",
            {
                "pattern": params.pattern,
                "modifier_type": params.modifier_type,
                "settings": params.settings or {}
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("modifiers_added", 0)
            return f"成功为 {count} 个对象添加 {params.modifier_type} 修改器"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_batch_set_parent",
        annotations={
            "title": "批量设置父对象",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_batch_set_parent(params: BatchParentInput) -> str:
        """批量设置匹配对象的父对象。
        
        Args:
            params: 子对象模式、父对象名称
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "batch", "set_parent",
            {
                "pattern": params.pattern,
                "parent_name": params.parent_name,
                "keep_transform": params.keep_transform
            }
        )
        
        if result.get("success"):
            count = result.get("data", {}).get("objects_parented", 0)
            return f"成功将 {count} 个对象设为 '{params.parent_name}' 的子对象"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
