"""
AI 辅助建模工具

提供 AI 生成纹理、材质、3D 模型等功能的 MCP 工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class AITextureGenerateInput(BaseModel):
    """AI生成纹理"""
    prompt: str = Field(..., description="纹理描述")
    negative_prompt: str = Field("", description="负面提示")
    width: int = Field(1024, description="宽度")
    height: int = Field(1024, description="高度")
    seamless: bool = Field(True, description="无缝纹理")
    apply_to: Optional[str] = Field(None, description="应用到对象")


class AIConceptArtInput(BaseModel):
    """生成概念图"""
    prompt: str = Field(..., description="概念描述")
    style: str = Field("realistic", description="风格: realistic, anime, cartoon, sketch")
    aspect_ratio: str = Field("16:9", description="宽高比")


class AIMaterialFromTextInput(BaseModel):
    """文本生成材质"""
    description: str = Field(..., description="材质描述")
    object_name: str = Field(..., description="目标对象")
    generate_textures: bool = Field(True, description="生成纹理贴图")


class AIUpscaleInput(BaseModel):
    """纹理放大"""
    image_path: str = Field(..., description="图像路径")
    scale: int = Field(2, description="放大倍数: 2, 4")


class AIRemoveBackgroundInput(BaseModel):
    """背景移除"""
    image_path: str = Field(..., description="图像路径")
    output_path: Optional[str] = Field(None, description="输出路径")


class AIConfigInput(BaseModel):
    """配置AI服务"""
    provider: str = Field("stability", description="服务商: stability, openai, local, replicate")
    api_key: Optional[str] = Field(None, description="API密钥")
    local_url: str = Field("http://127.0.0.1:7860", description="本地服务URL")
    model: str = Field("sdxl-1.0", description="模型名称")


# ============ 工具注册 ============

def register_ai_generation_tools(mcp: FastMCP, server):
    """注册 AI 辅助建模工具"""
    
    @mcp.tool()
    async def blender_ai_config(
        provider: str = "stability",
        api_key: Optional[str] = None,
        local_url: str = "http://127.0.0.1:7860",
        model: str = "sdxl-1.0"
    ) -> Dict[str, Any]:
        """
        配置 AI 服务
        
        Args:
            provider: 服务商 (stability, openai, local, replicate)
            api_key: API 密钥
            local_url: 本地服务 URL（用于 local 模式）
            model: 模型名称
        """
        params = AIConfigInput(
            provider=provider,
            api_key=api_key,
            local_url=local_url,
            model=model
        )
        return await server.send_command("ai_generation", "config", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_texture_generate(
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        seamless: bool = True,
        apply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI 生成纹理
        
        Args:
            prompt: 纹理描述（如 "木纹纹理"、"砖墙纹理"）
            negative_prompt: 不希望出现的内容
            width: 纹理宽度
            height: 纹理高度
            seamless: 生成无缝纹理
            apply_to: 应用到指定对象的材质
        """
        params = AITextureGenerateInput(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seamless=seamless,
            apply_to=apply_to
        )
        return await server.send_command("ai_generation", "texture_generate", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_concept_art(
        prompt: str,
        style: str = "realistic",
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        生成概念图作为参考
        
        Args:
            prompt: 概念描述
            style: 风格 (realistic, anime, cartoon, sketch)
            aspect_ratio: 宽高比 (16:9, 1:1, 4:3, 9:16)
        """
        params = AIConceptArtInput(
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio
        )
        return await server.send_command("ai_generation", "concept_art", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_material_from_text(
        description: str,
        object_name: str,
        generate_textures: bool = True
    ) -> Dict[str, Any]:
        """
        根据文本描述生成并应用材质
        
        Args:
            description: 材质描述（如 "生锈的金属"、"光滑的大理石"）
            object_name: 目标对象名称
            generate_textures: 是否生成纹理贴图
        """
        params = AIMaterialFromTextInput(
            description=description,
            object_name=object_name,
            generate_textures=generate_textures
        )
        return await server.send_command("ai_generation", "material_from_text", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_upscale_texture(
        image_path: str,
        scale: int = 2
    ) -> Dict[str, Any]:
        """
        AI 纹理放大
        
        Args:
            image_path: 图像路径
            scale: 放大倍数 (2 或 4)
        """
        params = AIUpscaleInput(
            image_path=image_path,
            scale=scale
        )
        return await server.send_command("ai_generation", "upscale", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_remove_background(
        image_path: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI 背景移除
        
        Args:
            image_path: 输入图像路径
            output_path: 输出路径（为空则自动生成）
        """
        params = AIRemoveBackgroundInput(
            image_path=image_path,
            output_path=output_path
        )
        return await server.send_command("ai_generation", "remove_background", params.model_dump())
    
    @mcp.tool()
    async def blender_ai_image_to_reference(
        prompt: str,
        as_background: bool = False
    ) -> Dict[str, Any]:
        """
        生成图像并设置为参考图
        
        Args:
            prompt: 图像描述
            as_background: 设置为背景图像
        """
        return await server.send_command("ai_generation", "image_to_reference", {
            "prompt": prompt,
            "as_background": as_background
        })
