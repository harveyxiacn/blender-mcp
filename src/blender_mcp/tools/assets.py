"""
Asset Management Tools

MCP tools for managing Blender asset libraries.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class AssetMarkInput(BaseModel):
    """Mark as asset"""

    object_name: str = Field(..., description="Object name")
    asset_type: str = Field("OBJECT", description="Asset type: OBJECT, MATERIAL, WORLD, etc.")
    description: str = Field("", description="Asset description")
    tags: list[str] = Field([], description="Tag list")


class AssetCatalogInput(BaseModel):
    """Catalog operation"""

    action: str = Field("LIST", description="Operation: LIST, CREATE, DELETE")
    catalog_name: str | None = Field(None, description="Catalog name")
    parent_catalog: str | None = Field(None, description="Parent catalog")


class AssetImportInput(BaseModel):
    """Import asset"""

    filepath: str = Field(..., description="Asset file path")
    asset_name: str = Field(..., description="Asset name")
    link: bool = Field(False, description="Link instead of append")


class AssetSearchInput(BaseModel):
    """Search assets"""

    query: str = Field(..., description="Search keyword")
    asset_type: str | None = Field(None, description="Asset type filter")


class AssetPreviewInput(BaseModel):
    """Generate preview"""

    object_name: str = Field(..., description="Object name")


class AssetClearInput(BaseModel):
    """Clear asset mark"""

    object_name: str = Field(..., description="Object name")


# ============ Tool Registration ============


def register_asset_tools(mcp: FastMCP, server) -> None:
    """Register asset management tools"""

    @mcp.tool()
    async def blender_asset_mark(
        object_name: str, asset_type: str = "OBJECT", description: str = "", tags: list[str] = None
    ) -> dict[str, Any]:
        """
        Mark an object as an asset

        Args:
            object_name: Object name
            asset_type: Asset type (OBJECT, MATERIAL, WORLD, etc.)
            description: Asset description
            tags: Tag list
        """
        if tags is None:
            tags = []
        params = AssetMarkInput(
            object_name=object_name, asset_type=asset_type, description=description, tags=tags
        )
        return await server.send_command("assets", "mark", params.model_dump())

    @mcp.tool()
    async def blender_asset_catalog(
        action: str = "LIST", catalog_name: str | None = None, parent_catalog: str | None = None
    ) -> dict[str, Any]:
        """
        Asset catalog operations

        Args:
            action: Operation type (LIST, CREATE, DELETE)
            catalog_name: Catalog name
            parent_catalog: Parent catalog name
        """
        params = AssetCatalogInput(
            action=action, catalog_name=catalog_name, parent_catalog=parent_catalog
        )
        return await server.send_command("assets", "catalog", params.model_dump())

    @mcp.tool()
    async def blender_asset_import(
        filepath: str, asset_name: str, link: bool = False
    ) -> dict[str, Any]:
        """
        Import asset from file

        Args:
            filepath: Asset file path (.blend)
            asset_name: Name of the asset to import
            link: True to link, False to append
        """
        params = AssetImportInput(filepath=filepath, asset_name=asset_name, link=link)
        return await server.send_command("assets", "import", params.model_dump())

    @mcp.tool()
    async def blender_asset_search(query: str, asset_type: str | None = None) -> dict[str, Any]:
        """
        Search assets

        Args:
            query: Search keyword
            asset_type: Asset type filter
        """
        params = AssetSearchInput(query=query, asset_type=asset_type)
        return await server.send_command("assets", "search", params.model_dump())

    @mcp.tool()
    async def blender_asset_preview(object_name: str) -> dict[str, Any]:
        """
        Generate asset preview image

        Args:
            object_name: Object name
        """
        params = AssetPreviewInput(object_name=object_name)
        return await server.send_command("assets", "preview", params.model_dump())

    @mcp.tool()
    async def blender_asset_clear(object_name: str) -> dict[str, Any]:
        """
        Clear asset mark

        Args:
            object_name: Object name
        """
        params = AssetClearInput(object_name=object_name)
        return await server.send_command("assets", "clear", params.model_dump())
