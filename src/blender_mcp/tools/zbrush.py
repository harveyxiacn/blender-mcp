"""
ZBrush 连接工具

提供与 ZBrush 集成的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class ZBrushExportInput(BaseModel):
    """导出到 ZBrush"""
    object_name: str = Field(..., description="对象名称")
    filepath: Optional[str] = Field(None, description="导出路径（为空则使用 GoZ）")
    subdivisions: int = Field(0, description="细分级别")


class ZBrushImportInput(BaseModel):
    """从 ZBrush 导入"""
    filepath: Optional[str] = Field(None, description="文件路径（为空则从 GoZ）")
    import_polypaint: bool = Field(True, description="导入顶点颜色")
    import_mask: bool = Field(True, description="导入遮罩")


class ZBrushMapsInput(BaseModel):
    """导入 ZBrush 贴图"""
    displacement_path: Optional[str] = Field(None, description="置换贴图路径")
    normal_path: Optional[str] = Field(None, description="法线贴图路径")
    polypaint_path: Optional[str] = Field(None, description="顶点绘制贴图路径")
    object_name: str = Field(..., description="目标对象")


class ZBrushDecimateInput(BaseModel):
    """导出减面模型"""
    object_name: str = Field(..., description="对象名称")
    target_faces: int = Field(10000, description="目标面数")
    filepath: str = Field(..., description="导出路径")


# ============ 工具注册 ============

def register_zbrush_tools(mcp: FastMCP, server):
    """注册 ZBrush 连接工具"""
    
    @mcp.tool()
    async def blender_zbrush_export(
        object_name: str,
        filepath: Optional[str] = None,
        subdivisions: int = 0
    ) -> Dict[str, Any]:
        """
        导出模型到 ZBrush
        
        Args:
            object_name: 对象名称
            filepath: 导出路径（为空则使用 GoZ 协议）
            subdivisions: 细分级别
        """
        params = ZBrushExportInput(
            object_name=object_name,
            filepath=filepath,
            subdivisions=subdivisions
        )
        return await server.send_command("zbrush", "export", params.model_dump())
    
    @mcp.tool()
    async def blender_zbrush_import(
        filepath: Optional[str] = None,
        import_polypaint: bool = True,
        import_mask: bool = True
    ) -> Dict[str, Any]:
        """
        从 ZBrush 导入模型
        
        Args:
            filepath: 文件路径（为空则从 GoZ 导入）
            import_polypaint: 导入顶点颜色
            import_mask: 导入遮罩
        """
        params = ZBrushImportInput(
            filepath=filepath,
            import_polypaint=import_polypaint,
            import_mask=import_mask
        )
        return await server.send_command("zbrush", "import", params.model_dump())
    
    @mcp.tool()
    async def blender_zbrush_goz_send(
        object_name: str
    ) -> Dict[str, Any]:
        """
        通过 GoZ 发送到 ZBrush
        
        Args:
            object_name: 对象名称
        """
        return await server.send_command("zbrush", "goz_send", {
            "object_name": object_name
        })
    
    @mcp.tool()
    async def blender_zbrush_goz_receive() -> Dict[str, Any]:
        """
        从 GoZ 接收 ZBrush 模型
        """
        return await server.send_command("zbrush", "goz_receive", {})
    
    @mcp.tool()
    async def blender_zbrush_maps(
        object_name: str,
        displacement_path: Optional[str] = None,
        normal_path: Optional[str] = None,
        polypaint_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导入 ZBrush 导出的贴图
        
        Args:
            object_name: 目标对象名称
            displacement_path: 置换贴图路径
            normal_path: 法线贴图路径
            polypaint_path: 顶点绘制贴图路径
        """
        params = ZBrushMapsInput(
            object_name=object_name,
            displacement_path=displacement_path,
            normal_path=normal_path,
            polypaint_path=polypaint_path
        )
        return await server.send_command("zbrush", "maps", params.model_dump())
    
    @mcp.tool()
    async def blender_zbrush_decimate_export(
        object_name: str,
        target_faces: int = 10000,
        filepath: str = ""
    ) -> Dict[str, Any]:
        """
        导出减面后的模型用于 ZBrush 投射
        
        Args:
            object_name: 对象名称
            target_faces: 目标面数
            filepath: 导出路径
        """
        params = ZBrushDecimateInput(
            object_name=object_name,
            target_faces=target_faces,
            filepath=filepath
        )
        return await server.send_command("zbrush", "decimate_export", params.model_dump())
    
    @mcp.tool()
    async def blender_zbrush_detect() -> Dict[str, Any]:
        """
        检测 ZBrush 安装和 GoZ 配置
        """
        return await server.send_command("zbrush", "detect", {})
