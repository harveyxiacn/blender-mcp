"""
AI-Assisted Modeling Tools

MCP tools for AI-generated textures, materials, 3D models, and more.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ============ Pydantic Models ============


class AITextureGenerateInput(BaseModel):
    """AI texture generation"""

    prompt: str = Field(..., description="Texture description")
    negative_prompt: str = Field("", description="Negative prompt")
    width: int = Field(1024, description="Width")
    height: int = Field(1024, description="Height")
    seamless: bool = Field(True, description="Seamless texture")
    apply_to: str | None = Field(None, description="Apply to object")


class AIConceptArtInput(BaseModel):
    """Generate concept art"""

    prompt: str = Field(..., description="Concept description")
    style: str = Field("realistic", description="Style: realistic, anime, cartoon, sketch")
    aspect_ratio: str = Field("16:9", description="Aspect ratio")


class AIMaterialFromTextInput(BaseModel):
    """Generate material from text"""

    description: str = Field(..., description="Material description")
    object_name: str = Field(..., description="Target object")
    generate_textures: bool = Field(True, description="Generate texture maps")


class AIUpscaleInput(BaseModel):
    """Texture upscale"""

    image_path: str = Field(..., description="Image path")
    scale: int = Field(2, description="Scale factor: 2, 4")


class AIRemoveBackgroundInput(BaseModel):
    """Background removal"""

    image_path: str = Field(..., description="Image path")
    output_path: str | None = Field(None, description="Output path")


class AIConfigInput(BaseModel):
    """Configure AI service"""

    provider: str = Field("stability", description="Provider: stability, openai, local, replicate")
    api_key: str | None = Field(None, description="API key")
    local_url: str = Field("http://127.0.0.1:7860", description="Local service URL")
    model: str = Field("sdxl-1.0", description="Model name")


# ============ Tool Registration ============


def register_ai_generation_tools(mcp: FastMCP, server) -> None:
    """Register AI-assisted modeling tools"""

    @mcp.tool()
    async def blender_ai_config(
        provider: str = "stability",
        api_key: str | None = None,
        local_url: str = "http://127.0.0.1:7860",
        model: str = "sdxl-1.0",
    ) -> dict[str, Any]:
        """
        Configure AI service

        Args:
            provider: Service provider (stability, openai, local, replicate)
            api_key: API key
            local_url: Local service URL (for local mode)
            model: Model name
        """
        params = AIConfigInput(provider=provider, api_key=api_key, local_url=local_url, model=model)
        return await server.send_command("ai_generation", "config", params.model_dump())

    @mcp.tool()
    async def blender_ai_texture_generate(
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        seamless: bool = True,
        apply_to: str | None = None,
    ) -> dict[str, Any]:
        """
        AI texture generation

        Args:
            prompt: Texture description (e.g. "wood grain texture", "brick wall texture")
            negative_prompt: Content to exclude
            width: Texture width
            height: Texture height
            seamless: Generate seamless texture
            apply_to: Apply to specified object's material
        """
        params = AITextureGenerateInput(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seamless=seamless,
            apply_to=apply_to,
        )
        return await server.send_command("ai_generation", "texture_generate", params.model_dump())

    @mcp.tool()
    async def blender_ai_concept_art(
        prompt: str, style: str = "realistic", aspect_ratio: str = "16:9"
    ) -> dict[str, Any]:
        """
        Generate concept art as reference

        Args:
            prompt: Concept description
            style: Style (realistic, anime, cartoon, sketch)
            aspect_ratio: Aspect ratio (16:9, 1:1, 4:3, 9:16)
        """
        params = AIConceptArtInput(prompt=prompt, style=style, aspect_ratio=aspect_ratio)
        return await server.send_command("ai_generation", "concept_art", params.model_dump())

    @mcp.tool()
    async def blender_ai_material_from_text(
        description: str, object_name: str, generate_textures: bool = True
    ) -> dict[str, Any]:
        """
        Generate and apply material from text description

        Args:
            description: Material description (e.g. "rusty metal", "smooth marble")
            object_name: Target object name
            generate_textures: Whether to generate texture maps
        """
        params = AIMaterialFromTextInput(
            description=description, object_name=object_name, generate_textures=generate_textures
        )
        return await server.send_command("ai_generation", "material_from_text", params.model_dump())

    @mcp.tool()
    async def blender_ai_upscale_texture(image_path: str, scale: int = 2) -> dict[str, Any]:
        """
        AI texture upscale

        Args:
            image_path: Image path
            scale: Scale factor (2 or 4)
        """
        params = AIUpscaleInput(image_path=image_path, scale=scale)
        return await server.send_command("ai_generation", "upscale", params.model_dump())

    @mcp.tool()
    async def blender_ai_remove_background(
        image_path: str, output_path: str | None = None
    ) -> dict[str, Any]:
        """
        AI background removal

        Args:
            image_path: Input image path
            output_path: Output path (auto-generated if empty)
        """
        params = AIRemoveBackgroundInput(image_path=image_path, output_path=output_path)
        return await server.send_command("ai_generation", "remove_background", params.model_dump())

    @mcp.tool()
    async def blender_ai_image_to_reference(
        prompt: str, as_background: bool = False
    ) -> dict[str, Any]:
        """
        Generate image and set as reference

        Args:
            prompt: Image description
            as_background: Set as background image
        """
        return await server.send_command(
            "ai_generation",
            "image_to_reference",
            {"prompt": prompt, "as_background": as_background},
        )
