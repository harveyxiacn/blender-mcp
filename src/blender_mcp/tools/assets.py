"""
资产管理工具

提供Blender资产库管理的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class AssetMarkInput(BaseModel):
    """标记为资产"""
    object_name: str = Field(..., description="对象名称")
    asset_type: str = Field("OBJECT", description="资产类型: OBJECT, MATERIAL, WORLD, etc.")
    description: str = Field("", description="资产描述")
    tags: List[str] = Field([], description="标签列表")


class AssetCatalogInput(BaseModel):
    """目录操作"""
    action: str = Field("LIST", description="操作: LIST, CREATE, DELETE")
    catalog_name: Optional[str] = Field(None, description="目录名称")
    parent_catalog: Optional[str] = Field(None, description="父目录")


class AssetImportInput(BaseModel):
    """导入资产"""
    filepath: str = Field(..., description="资产文件路径")
    asset_name: str = Field(..., description="资产名称")
    link: bool = Field(False, description="链接而非追加")


class AssetSearchInput(BaseModel):
    """搜索资产"""
    query: str = Field(..., description="搜索关键词")
    asset_type: Optional[str] = Field(None, description="资产类型过滤")


class AssetPreviewInput(BaseModel):
    """生成预览"""
    object_name: str = Field(..., description="对象名称")


class AssetClearInput(BaseModel):
    """清除资产标记"""
    object_name: str = Field(..., description="对象名称")


# ============ 工具注册 ============

def register_asset_tools(mcp: FastMCP, server):
    """注册资产管理工具"""
    
    @mcp.tool()
    async def blender_asset_mark(
        object_name: str,
        asset_type: str = "OBJECT",
        description: str = "",
        tags: List[str] = []
    ) -> Dict[str, Any]:
        """
        将对象标记为资产
        
        Args:
            object_name: 对象名称
            asset_type: 资产类型 (OBJECT, MATERIAL, WORLD等)
            description: 资产描述
            tags: 标签列表
        """
        params = AssetMarkInput(
            object_name=object_name,
            asset_type=asset_type,
            description=description,
            tags=tags
        )
        return await server.send_command("assets", "mark", params.model_dump())
    
    @mcp.tool()
    async def blender_asset_catalog(
        action: str = "LIST",
        catalog_name: Optional[str] = None,
        parent_catalog: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        资产目录操作
        
        Args:
            action: 操作类型 (LIST, CREATE, DELETE)
            catalog_name: 目录名称
            parent_catalog: 父目录名称
        """
        params = AssetCatalogInput(
            action=action,
            catalog_name=catalog_name,
            parent_catalog=parent_catalog
        )
        return await server.send_command("assets", "catalog", params.model_dump())
    
    @mcp.tool()
    async def blender_asset_import(
        filepath: str,
        asset_name: str,
        link: bool = False
    ) -> Dict[str, Any]:
        """
        从文件导入资产
        
        Args:
            filepath: 资产文件路径 (.blend)
            asset_name: 要导入的资产名称
            link: True链接，False追加
        """
        params = AssetImportInput(
            filepath=filepath,
            asset_name=asset_name,
            link=link
        )
        return await server.send_command("assets", "import", params.model_dump())
    
    @mcp.tool()
    async def blender_asset_search(
        query: str,
        asset_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        搜索资产
        
        Args:
            query: 搜索关键词
            asset_type: 资产类型过滤
        """
        params = AssetSearchInput(
            query=query,
            asset_type=asset_type
        )
        return await server.send_command("assets", "search", params.model_dump())
    
    @mcp.tool()
    async def blender_asset_preview(
        object_name: str
    ) -> Dict[str, Any]:
        """
        生成资产预览图
        
        Args:
            object_name: 对象名称
        """
        params = AssetPreviewInput(
            object_name=object_name
        )
        return await server.send_command("assets", "preview", params.model_dump())
    
    @mcp.tool()
    async def blender_asset_clear(
        object_name: str
    ) -> Dict[str, Any]:
        """
        清除资产标记
        
        Args:
            object_name: 对象名称
        """
        params = AssetClearInput(
            object_name=object_name
        )
        return await server.send_command("assets", "clear", params.model_dump())
