"""
偏好设置工具

提供Blender偏好设置管理的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class PrefGetInput(BaseModel):
    """获取设置"""
    category: str = Field(..., description="设置类别")
    key: str = Field(..., description="设置键")


class PrefSetInput(BaseModel):
    """设置偏好"""
    category: str = Field(..., description="设置类别")
    key: str = Field(..., description="设置键")
    value: Any = Field(..., description="设置值")


class PrefThemeInput(BaseModel):
    """主题设置"""
    preset: Optional[str] = Field(None, description="预设主题名称")
    custom_colors: Optional[Dict[str, List[float]]] = Field(None, description="自定义颜色")


class PrefViewportInput(BaseModel):
    """视口设置"""
    show_gizmo: Optional[bool] = Field(None, description="显示小工具")
    show_floor: Optional[bool] = Field(None, description="显示地面")
    show_axis_x: Optional[bool] = Field(None, description="显示X轴")
    show_axis_y: Optional[bool] = Field(None, description="显示Y轴")
    show_axis_z: Optional[bool] = Field(None, description="显示Z轴")
    clip_start: Optional[float] = Field(None, description="近裁剪")
    clip_end: Optional[float] = Field(None, description="远裁剪")


class PrefSystemInput(BaseModel):
    """系统设置"""
    memory_cache_limit: Optional[int] = Field(None, description="内存缓存限制(MB)")
    undo_steps: Optional[int] = Field(None, description="撤销步数")
    use_gpu_subdivision: Optional[bool] = Field(None, description="GPU细分")


# ============ 工具注册 ============

def register_preferences_tools(mcp: FastMCP, server):
    """注册偏好设置工具"""
    
    @mcp.tool()
    async def blender_pref_get(
        category: str,
        key: str
    ) -> Dict[str, Any]:
        """
        获取Blender偏好设置
        
        Args:
            category: 设置类别 (view, system, edit, input, etc.)
            key: 设置键名
        """
        params = PrefGetInput(category=category, key=key)
        return await server.send_command("preferences", "get", params.model_dump())
    
    @mcp.tool()
    async def blender_pref_set(
        category: str,
        key: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        设置Blender偏好
        
        Args:
            category: 设置类别 (view, system, edit, input, etc.)
            key: 设置键名
            value: 设置值
        """
        params = PrefSetInput(category=category, key=key, value=value)
        return await server.send_command("preferences", "set", params.model_dump())
    
    @mcp.tool()
    async def blender_pref_theme(
        preset: Optional[str] = None,
        custom_colors: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, Any]:
        """
        设置主题
        
        Args:
            preset: 预设主题名称 (Dark, Light, etc.)
            custom_colors: 自定义颜色字典
        """
        params = PrefThemeInput(preset=preset, custom_colors=custom_colors)
        return await server.send_command("preferences", "theme", params.model_dump())
    
    @mcp.tool()
    async def blender_pref_viewport(
        show_gizmo: Optional[bool] = None,
        show_floor: Optional[bool] = None,
        show_axis_x: Optional[bool] = None,
        show_axis_y: Optional[bool] = None,
        show_axis_z: Optional[bool] = None,
        clip_start: Optional[float] = None,
        clip_end: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        设置视口偏好
        
        Args:
            show_gizmo: 显示小工具
            show_floor: 显示地面网格
            show_axis_x/y/z: 显示坐标轴
            clip_start: 近裁剪距离
            clip_end: 远裁剪距离
        """
        params = PrefViewportInput(
            show_gizmo=show_gizmo,
            show_floor=show_floor,
            show_axis_x=show_axis_x,
            show_axis_y=show_axis_y,
            show_axis_z=show_axis_z,
            clip_start=clip_start,
            clip_end=clip_end
        )
        return await server.send_command("preferences", "viewport", params.model_dump())
    
    @mcp.tool()
    async def blender_pref_system(
        memory_cache_limit: Optional[int] = None,
        undo_steps: Optional[int] = None,
        use_gpu_subdivision: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        设置系统偏好
        
        Args:
            memory_cache_limit: 内存缓存限制(MB)
            undo_steps: 撤销步数
            use_gpu_subdivision: 使用GPU细分
        """
        params = PrefSystemInput(
            memory_cache_limit=memory_cache_limit,
            undo_steps=undo_steps,
            use_gpu_subdivision=use_gpu_subdivision
        )
        return await server.send_command("preferences", "system", params.model_dump())
    
    @mcp.tool()
    async def blender_pref_save() -> Dict[str, Any]:
        """
        保存偏好设置
        """
        return await server.send_command("preferences", "save", {})
    
    @mcp.tool()
    async def blender_pref_load_factory() -> Dict[str, Any]:
        """
        加载出厂设置
        """
        return await server.send_command("preferences", "load_factory", {})
