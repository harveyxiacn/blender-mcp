"""
实用工具

提供脚本执行、截图、文件操作等实用功能。
"""

from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class ExecutePythonInput(BaseModel):
    """执行 Python 代码输入"""
    code: str = Field(..., description="Python 代码")
    timeout: int = Field(default=30, description="超时时间（秒）", ge=1, le=300)


class ViewportScreenshotInput(BaseModel):
    """视口截图输入"""
    output_path: Optional[str] = Field(default=None, description="输出路径")
    width: int = Field(default=800, description="图像宽度", ge=100, le=4096)
    height: int = Field(default=600, description="图像高度", ge=100, le=4096)


class FileSaveInput(BaseModel):
    """保存文件输入"""
    filepath: Optional[str] = Field(default=None, description="文件路径")
    compress: bool = Field(default=True, description="压缩文件")


class FileOpenInput(BaseModel):
    """打开文件输入"""
    filepath: str = Field(..., description="文件路径")
    load_ui: bool = Field(default=False, description="加载 UI 布局")


class GetBlenderInfoInput(BaseModel):
    """获取 Blender 信息输入"""
    pass


class UndoInput(BaseModel):
    """撤销输入"""
    steps: int = Field(default=1, description="撤销步数", ge=1, le=100)


class RedoInput(BaseModel):
    """重做输入"""
    steps: int = Field(default=1, description="重做步数", ge=1, le=100)


# ==================== 工具注册 ====================

def register_utility_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册实用工具"""
    
    @mcp.tool(
        name="blender_execute_python",
        annotations={
            "title": "执行 Python 代码",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_execute_python(params: ExecutePythonInput) -> str:
        """在 Blender 中执行 Python 代码。
        
        注意：此功能需要谨慎使用，可能会修改场景或执行危险操作。
        
        Args:
            params: Python 代码和超时时间
            
        Returns:
            执行结果
        """
        result = await server.execute_command(
            "utility", "execute_python",
            {"code": params.code, "timeout": params.timeout}
        )
        
        if result.get("success"):
            output = result.get("data", {}).get("output", "")
            return f"代码执行成功\n{output}" if output else "代码执行成功"
        else:
            return f"执行失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_get_viewport_screenshot",
        annotations={
            "title": "获取视口截图",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_get_viewport_screenshot(params: ViewportScreenshotInput) -> str:
        """获取当前视口的截图。
        
        Args:
            params: 输出路径和尺寸
            
        Returns:
            截图路径
        """
        result = await server.execute_command(
            "utility", "viewport_screenshot",
            {
                "output_path": params.output_path,
                "width": params.width,
                "height": params.height
            }
        )
        
        if result.get("success"):
            path = result.get("data", {}).get("output_path", "临时文件")
            return f"视口截图已保存: {path}"
        else:
            return f"截图失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_file_save",
        annotations={
            "title": "保存文件",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    )
    async def blender_file_save(params: FileSaveInput) -> str:
        """保存 Blender 文件。
        
        Args:
            params: 文件路径和压缩选项
            
        Returns:
            保存结果
        """
        result = await server.execute_command(
            "utility", "file_save",
            {"filepath": params.filepath, "compress": params.compress}
        )
        
        if result.get("success"):
            path = result.get("data", {}).get("filepath", params.filepath or "当前文件")
            return f"文件已保存: {path}"
        else:
            return f"保存失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_file_open",
        annotations={
            "title": "打开文件",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_file_open(params: FileOpenInput) -> str:
        """打开 Blender 文件。
        
        注意：这将替换当前场景，未保存的更改将丢失。
        
        Args:
            params: 文件路径
            
        Returns:
            打开结果
        """
        result = await server.execute_command(
            "utility", "file_open",
            {"filepath": params.filepath, "load_ui": params.load_ui}
        )
        
        if result.get("success"):
            return f"已打开文件: {params.filepath}"
        else:
            return f"打开文件失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_get_info",
        annotations={
            "title": "获取 Blender 信息",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_get_info(params: GetBlenderInfoInput) -> str:
        """获取 Blender 版本和状态信息。
        
        Returns:
            Blender 信息
        """
        result = await server.execute_command(
            "utility", "get_info",
            {}
        )
        
        if result.get("success"):
            data = result.get("data", {})
            lines = ["# Blender 信息", ""]
            lines.append(f"- **版本**: {data.get('version', '未知')}")
            lines.append(f"- **版本号**: {data.get('version_string', '未知')}")
            lines.append(f"- **当前文件**: {data.get('filepath', '未保存')}")
            lines.append(f"- **当前场景**: {data.get('scene', '未知')}")
            lines.append(f"- **对象数量**: {data.get('objects_count', 0)}")
            return "\n".join(lines)
        else:
            return f"获取信息失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_undo",
        annotations={
            "title": "撤销",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_undo(params: UndoInput) -> str:
        """撤销操作。
        
        Args:
            params: 撤销步数
            
        Returns:
            撤销结果
        """
        result = await server.execute_command(
            "utility", "undo",
            {"steps": params.steps}
        )
        
        if result.get("success"):
            return f"已撤销 {params.steps} 步操作"
        else:
            return f"撤销失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_redo",
        annotations={
            "title": "重做",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_redo(params: RedoInput) -> str:
        """重做操作。
        
        Args:
            params: 重做步数
            
        Returns:
            重做结果
        """
        result = await server.execute_command(
            "utility", "redo",
            {"steps": params.steps}
        )
        
        if result.get("success"):
            return f"已重做 {params.steps} 步操作"
        else:
            return f"重做失败: {result.get('error', {}).get('message', '未知错误')}"
