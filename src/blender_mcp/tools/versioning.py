"""
版本控制工具

提供Blender场景版本管理的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class VersionSaveInput(BaseModel):
    """保存版本"""
    name: Optional[str] = Field(None, description="版本名称")
    description: str = Field("", description="版本描述")
    create_thumbnail: bool = Field(True, description="生成缩略图")


class VersionRestoreInput(BaseModel):
    """恢复版本"""
    version_id: str = Field(..., description="版本ID")
    create_backup: bool = Field(True, description="恢复前创建备份")


class VersionCompareInput(BaseModel):
    """比较版本"""
    version_id_1: str = Field(..., description="版本1 ID")
    version_id_2: str = Field(..., description="版本2 ID")


class VersionBranchInput(BaseModel):
    """创建分支"""
    branch_name: str = Field(..., description="分支名称")
    from_version: Optional[str] = Field(None, description="从指定版本创建")


class VersionMergeInput(BaseModel):
    """合并分支"""
    source_branch: str = Field(..., description="源分支")
    target_branch: str = Field("main", description="目标分支")
    strategy: str = Field("theirs", description="合并策略: theirs, ours, manual")


class VersionDeleteInput(BaseModel):
    """删除版本"""
    version_id: str = Field(..., description="版本ID")
    force: bool = Field(False, description="强制删除")


# ============ 工具注册 ============

def register_versioning_tools(mcp: FastMCP, server):
    """注册版本控制工具"""
    
    @mcp.tool()
    async def blender_version_init(
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        初始化版本控制系统
        
        Args:
            project_path: 项目路径（为空则使用当前文件目录）
        """
        return await server.send_command("versioning", "init", {
            "project_path": project_path
        })
    
    @mcp.tool()
    async def blender_version_save(
        name: Optional[str] = None,
        description: str = "",
        create_thumbnail: bool = True
    ) -> Dict[str, Any]:
        """
        保存当前场景为新版本
        
        Args:
            name: 版本名称（为空则自动生成）
            description: 版本描述
            create_thumbnail: 是否生成缩略图
        """
        params = VersionSaveInput(
            name=name,
            description=description,
            create_thumbnail=create_thumbnail
        )
        return await server.send_command("versioning", "save", params.model_dump())
    
    @mcp.tool()
    async def blender_version_list(
        branch: str = "main",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        列出所有版本
        
        Args:
            branch: 分支名称
            limit: 返回数量限制
        """
        return await server.send_command("versioning", "list", {
            "branch": branch,
            "limit": limit
        })
    
    @mcp.tool()
    async def blender_version_restore(
        version_id: str,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        恢复到指定版本
        
        Args:
            version_id: 版本ID
            create_backup: 恢复前是否创建当前状态备份
        """
        params = VersionRestoreInput(
            version_id=version_id,
            create_backup=create_backup
        )
        return await server.send_command("versioning", "restore", params.model_dump())
    
    @mcp.tool()
    async def blender_version_compare(
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        比较两个版本的差异
        
        Args:
            version_id_1: 第一个版本ID
            version_id_2: 第二个版本ID
        """
        params = VersionCompareInput(
            version_id_1=version_id_1,
            version_id_2=version_id_2
        )
        return await server.send_command("versioning", "compare", params.model_dump())
    
    @mcp.tool()
    async def blender_version_branch(
        branch_name: str,
        from_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新分支
        
        Args:
            branch_name: 分支名称
            from_version: 从指定版本创建（为空则从当前版本）
        """
        params = VersionBranchInput(
            branch_name=branch_name,
            from_version=from_version
        )
        return await server.send_command("versioning", "branch", params.model_dump())
    
    @mcp.tool()
    async def blender_version_branches() -> Dict[str, Any]:
        """
        列出所有分支
        """
        return await server.send_command("versioning", "branches", {})
    
    @mcp.tool()
    async def blender_version_switch_branch(
        branch_name: str
    ) -> Dict[str, Any]:
        """
        切换到指定分支
        
        Args:
            branch_name: 分支名称
        """
        return await server.send_command("versioning", "switch_branch", {
            "branch_name": branch_name
        })
    
    @mcp.tool()
    async def blender_version_delete(
        version_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        删除指定版本
        
        Args:
            version_id: 版本ID
            force: 强制删除
        """
        params = VersionDeleteInput(
            version_id=version_id,
            force=force
        )
        return await server.send_command("versioning", "delete", params.model_dump())
    
    @mcp.tool()
    async def blender_version_info(
        version_id: str
    ) -> Dict[str, Any]:
        """
        获取版本详细信息
        
        Args:
            version_id: 版本ID
        """
        return await server.send_command("versioning", "info", {
            "version_id": version_id
        })
