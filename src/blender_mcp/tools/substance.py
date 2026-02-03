"""
Substance 连接工具

提供与 Substance Painter 集成的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class SubstanceExportInput(BaseModel):
    """导出到 Substance"""
    object_name: str = Field(..., description="对象名称")
    filepath: str = Field(..., description="导出路径")
    format: str = Field("FBX", description="格式: FBX, OBJ")
    export_uvs: bool = Field(True, description="导出 UV")
    triangulate: bool = Field(True, description="三角化")


class SubstanceImportInput(BaseModel):
    """导入 Substance 纹理"""
    texture_folder: str = Field(..., description="纹理文件夹")
    object_name: str = Field(..., description="目标对象")
    naming_convention: str = Field("substance", description="命名约定: substance, custom")


class SubstanceLinkInput(BaseModel):
    """建立实时链接"""
    project_path: str = Field(..., description="Substance 项目路径")
    watch_interval: float = Field(2.0, description="监控间隔（秒）")


class SubstanceBakeInput(BaseModel):
    """请求烘焙贴图"""
    high_poly: str = Field(..., description="高模对象")
    low_poly: str = Field(..., description="低模对象")
    output_folder: str = Field(..., description="输出文件夹")
    maps: List[str] = Field(["normal", "ao", "curvature"], description="烘焙贴图类型")
    resolution: int = Field(2048, description="分辨率")


# ============ 工具注册 ============

def register_substance_tools(mcp: FastMCP, server):
    """注册 Substance 连接工具"""
    
    @mcp.tool()
    async def blender_substance_export(
        object_name: str,
        filepath: str,
        format: str = "FBX",
        export_uvs: bool = True,
        triangulate: bool = True
    ) -> Dict[str, Any]:
        """
        导出模型到 Substance Painter
        
        Args:
            object_name: 对象名称
            filepath: 导出路径
            format: 导出格式 (FBX, OBJ)
            export_uvs: 是否导出 UV
            triangulate: 是否三角化
        """
        params = SubstanceExportInput(
            object_name=object_name,
            filepath=filepath,
            format=format,
            export_uvs=export_uvs,
            triangulate=triangulate
        )
        return await server.send_command("substance", "export", params.model_dump())
    
    @mcp.tool()
    async def blender_substance_import(
        texture_folder: str,
        object_name: str,
        naming_convention: str = "substance"
    ) -> Dict[str, Any]:
        """
        导入 Substance Painter 输出的纹理
        
        Args:
            texture_folder: 纹理文件夹路径
            object_name: 目标对象名称
            naming_convention: 命名约定 (substance, custom)
        """
        params = SubstanceImportInput(
            texture_folder=texture_folder,
            object_name=object_name,
            naming_convention=naming_convention
        )
        return await server.send_command("substance", "import", params.model_dump())
    
    @mcp.tool()
    async def blender_substance_link(
        project_path: str,
        watch_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        建立与 Substance Painter 的实时链接
        
        Args:
            project_path: Substance 项目路径 (.spp)
            watch_interval: 监控间隔（秒）
        """
        params = SubstanceLinkInput(
            project_path=project_path,
            watch_interval=watch_interval
        )
        return await server.send_command("substance", "link", params.model_dump())
    
    @mcp.tool()
    async def blender_substance_unlink() -> Dict[str, Any]:
        """
        断开 Substance Painter 链接
        """
        return await server.send_command("substance", "unlink", {})
    
    @mcp.tool()
    async def blender_substance_bake(
        high_poly: str,
        low_poly: str,
        output_folder: str,
        maps: List[str] = ["normal", "ao", "curvature"],
        resolution: int = 2048
    ) -> Dict[str, Any]:
        """
        准备并导出用于 Substance 烘焙的模型
        
        Args:
            high_poly: 高模对象名称
            low_poly: 低模对象名称
            output_folder: 输出文件夹
            maps: 要烘焙的贴图类型
            resolution: 分辨率
        """
        params = SubstanceBakeInput(
            high_poly=high_poly,
            low_poly=low_poly,
            output_folder=output_folder,
            maps=maps,
            resolution=resolution
        )
        return await server.send_command("substance", "bake", params.model_dump())
    
    @mcp.tool()
    async def blender_substance_detect() -> Dict[str, Any]:
        """
        检测 Substance Painter 安装
        """
        return await server.send_command("substance", "detect", {})
