"""
外部集成工具

提供与外部工具（Unity、Unreal等）集成的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class UnityExportInput(BaseModel):
    """Unity导出"""
    filepath: str = Field(..., description="导出文件路径")
    objects: Optional[List[str]] = Field(None, description="要导出的对象列表")
    apply_modifiers: bool = Field(True, description="应用修改器")
    apply_scale: bool = Field(True, description="应用缩放")
    export_animations: bool = Field(True, description="导出动画")
    bake_animation: bool = Field(False, description="烘焙动画")


class UnrealExportInput(BaseModel):
    """Unreal导出"""
    filepath: str = Field(..., description="导出文件路径")
    objects: Optional[List[str]] = Field(None, description="要导出的对象列表")
    export_animations: bool = Field(True, description="导出动画")
    smoothing: str = Field("FACE", description="平滑类型: FACE, EDGE, OFF")
    use_tspace: bool = Field(True, description="使用切线空间")


class GodotExportInput(BaseModel):
    """Godot导出"""
    filepath: str = Field(..., description="导出文件路径")
    objects: Optional[List[str]] = Field(None, description="要导出的对象列表")
    export_format: str = Field("GLTF", description="导出格式: GLTF, GLB")


class BatchExportInput(BaseModel):
    """批量导出"""
    output_dir: str = Field(..., description="输出目录")
    format: str = Field("FBX", description="格式: FBX, GLTF, OBJ")
    separate_files: bool = Field(True, description="分别导出到单独文件")
    objects: Optional[List[str]] = Field(None, description="要导出的对象列表")


class CollectionExportInput(BaseModel):
    """集合导出"""
    collection_name: str = Field(..., description="集合名称")
    filepath: str = Field(..., description="导出文件路径")
    format: str = Field("FBX", description="格式: FBX, GLTF, OBJ")


# ============ 工具注册 ============

def register_external_tools(mcp: FastMCP, server):
    """注册外部集成工具"""
    
    @mcp.tool()
    async def blender_unity_export(
        filepath: str,
        objects: Optional[List[str]] = None,
        apply_modifiers: bool = True,
        apply_scale: bool = True,
        export_animations: bool = True,
        bake_animation: bool = False
    ) -> Dict[str, Any]:
        """
        优化为Unity导出
        
        Args:
            filepath: 导出文件路径 (.fbx)
            objects: 要导出的对象列表
            apply_modifiers: 应用修改器
            apply_scale: 应用缩放（Unity使用不同的坐标系）
            export_animations: 导出动画
            bake_animation: 烘焙动画
        """
        params = UnityExportInput(
            filepath=filepath,
            objects=objects,
            apply_modifiers=apply_modifiers,
            apply_scale=apply_scale,
            export_animations=export_animations,
            bake_animation=bake_animation
        )
        return await server.send_command("external", "unity_export", params.model_dump())
    
    @mcp.tool()
    async def blender_unreal_export(
        filepath: str,
        objects: Optional[List[str]] = None,
        export_animations: bool = True,
        smoothing: str = "FACE",
        use_tspace: bool = True
    ) -> Dict[str, Any]:
        """
        优化为Unreal Engine导出
        
        Args:
            filepath: 导出文件路径 (.fbx)
            objects: 要导出的对象列表
            export_animations: 导出动画
            smoothing: 平滑类型 (FACE, EDGE, OFF)
            use_tspace: 使用切线空间
        """
        params = UnrealExportInput(
            filepath=filepath,
            objects=objects,
            export_animations=export_animations,
            smoothing=smoothing,
            use_tspace=use_tspace
        )
        return await server.send_command("external", "unreal_export", params.model_dump())
    
    @mcp.tool()
    async def blender_godot_export(
        filepath: str,
        objects: Optional[List[str]] = None,
        export_format: str = "GLTF"
    ) -> Dict[str, Any]:
        """
        优化为Godot导出
        
        Args:
            filepath: 导出文件路径
            objects: 要导出的对象列表
            export_format: 导出格式 (GLTF, GLB)
        """
        params = GodotExportInput(
            filepath=filepath,
            objects=objects,
            export_format=export_format
        )
        return await server.send_command("external", "godot_export", params.model_dump())
    
    # 注意：blender_batch_export 已移至 batch.py 避免重复注册
    
    @mcp.tool()
    async def blender_collection_export(
        collection_name: str,
        filepath: str,
        format: str = "FBX"
    ) -> Dict[str, Any]:
        """
        导出整个集合
        
        Args:
            collection_name: 集合名称
            filepath: 导出文件路径
            format: 导出格式 (FBX, GLTF, OBJ)
        """
        params = CollectionExportInput(
            collection_name=collection_name,
            filepath=filepath,
            format=format
        )
        return await server.send_command("external", "collection_export", params.model_dump())
