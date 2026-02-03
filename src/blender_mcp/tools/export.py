"""
导出工具

提供模型和动画导出功能，支持 Unity、Web 等平台。
"""

from typing import TYPE_CHECKING, Optional, List

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class ExportFBXInput(BaseModel):
    """FBX 导出输入"""
    filepath: str = Field(..., description="导出文件路径 (.fbx)")
    selected_only: bool = Field(default=False, description="仅导出选中对象")
    apply_modifiers: bool = Field(default=True, description="应用修改器")
    include_animation: bool = Field(default=True, description="包含动画")
    bake_animation: bool = Field(default=False, description="烘焙动画")
    use_mesh_modifiers: bool = Field(default=True, description="应用网格修改器")
    use_armature_deform_only: bool = Field(default=False, description="仅骨架变形")
    add_leaf_bones: bool = Field(default=False, description="添加叶骨骼 (Unity 不需要)")
    primary_bone_axis: str = Field(default="Y", description="主骨骼轴")
    secondary_bone_axis: str = Field(default="X", description="次骨骼轴")
    apply_scale: str = Field(default="FBX_SCALE_ALL", description="缩放应用方式")


class ExportGLTFInput(BaseModel):
    """glTF 导出输入"""
    filepath: str = Field(..., description="导出文件路径 (.glb 或 .gltf)")
    selected_only: bool = Field(default=False, description="仅导出选中对象")
    include_animation: bool = Field(default=True, description="包含动画")
    export_format: str = Field(default="GLB", description="格式: GLB 或 GLTF_SEPARATE")
    export_textures: bool = Field(default=True, description="导出贴图")
    export_draco: bool = Field(default=False, description="Draco 压缩")


class ExportOBJInput(BaseModel):
    """OBJ 导出输入"""
    filepath: str = Field(..., description="导出文件路径 (.obj)")
    selected_only: bool = Field(default=False, description="仅导出选中对象")
    apply_modifiers: bool = Field(default=True, description="应用修改器")
    export_materials: bool = Field(default=True, description="导出材质")


class ExportUnityPackageInput(BaseModel):
    """Unity 包导出输入"""
    filepath: str = Field(..., description="导出文件路径")
    objects: Optional[List[str]] = Field(default=None, description="要导出的对象列表")
    include_animations: bool = Field(default=True, description="包含动画")
    setup_humanoid: bool = Field(default=False, description="设置为 Humanoid 类型")
    generate_lod: bool = Field(default=False, description="生成 LOD")


# ==================== 工具注册 ====================

def register_export_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册导出工具"""
    
    @mcp.tool(
        name="blender_export_fbx",
        annotations={
            "title": "导出 FBX",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_fbx(params: ExportFBXInput) -> str:
        """导出为 FBX 格式（适用于 Unity、Unreal 等）。
        
        Args:
            params: 导出设置
            
        Returns:
            导出结果
        """
        result = await server.execute_command(
            "export", "fbx",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "include_animation": params.include_animation,
                "bake_animation": params.bake_animation,
                "use_mesh_modifiers": params.use_mesh_modifiers,
                "use_armature_deform_only": params.use_armature_deform_only,
                "add_leaf_bones": params.add_leaf_bones,
                "primary_bone_axis": params.primary_bone_axis,
                "secondary_bone_axis": params.secondary_bone_axis,
                "apply_scale": params.apply_scale
            }
        )
        
        if result.get("success"):
            return f"成功导出 FBX 到: {params.filepath}"
        else:
            return f"导出失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_export_gltf",
        annotations={
            "title": "导出 glTF",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_gltf(params: ExportGLTFInput) -> str:
        """导出为 glTF 格式（适用于 Web、Three.js 等）。
        
        Args:
            params: 导出设置
            
        Returns:
            导出结果
        """
        result = await server.execute_command(
            "export", "gltf",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "include_animation": params.include_animation,
                "export_format": params.export_format,
                "export_textures": params.export_textures,
                "export_draco": params.export_draco
            }
        )
        
        if result.get("success"):
            return f"成功导出 glTF 到: {params.filepath}"
        else:
            return f"导出失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_export_obj",
        annotations={
            "title": "导出 OBJ",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_export_obj(params: ExportOBJInput) -> str:
        """导出为 OBJ 格式。
        
        Args:
            params: 导出设置
            
        Returns:
            导出结果
        """
        result = await server.execute_command(
            "export", "obj",
            {
                "filepath": params.filepath,
                "selected_only": params.selected_only,
                "apply_modifiers": params.apply_modifiers,
                "export_materials": params.export_materials
            }
        )
        
        if result.get("success"):
            return f"成功导出 OBJ 到: {params.filepath}"
        else:
            return f"导出失败: {result.get('error', {}).get('message', '未知错误')}"
