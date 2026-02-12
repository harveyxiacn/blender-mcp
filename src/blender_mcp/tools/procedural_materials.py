"""
程序化材质预设工具

提供50+种程序化材质预设，无需外部贴图，通过节点组合生成。
覆盖金属、木材、石材、布料、自然、皮肤、特效等类别。
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class MaterialCategory(str, Enum):
    """材质类别"""
    METAL = "METAL"
    WOOD = "WOOD"
    STONE = "STONE"
    FABRIC = "FABRIC"
    NATURE = "NATURE"
    SKIN = "SKIN"
    EFFECT = "EFFECT"
    TOON = "TOON"


class ProceduralMaterialInput(BaseModel):
    """程序化材质预设输入"""
    preset: str = Field(
        ...,
        description="材质预设名称。可用预设: "
                    "金属: STEEL, IRON, GOLD, SILVER, BRONZE, COPPER, CHROME, BRUSHED_METAL, RUSTY_METAL, DAMASCUS; "
                    "木材: OAK, PINE, CHERRY, WALNUT, BIRCH, BAMBOO, PLYWOOD, AGED_WOOD; "
                    "石材: GRANITE, MARBLE, LIMESTONE, SLATE, COBBLESTONE, SANDSTONE, BRICK, TILE, CONCRETE; "
                    "布料: COTTON, SILK, LEATHER, DENIM, VELVET, CANVAS, WOOL, CHAIN_MAIL; "
                    "自然: GRASS, DIRT, SAND, SNOW, MUD, GRAVEL, MOSS, LAVA, WATER, ICE; "
                    "皮肤: SKIN_REALISTIC, SKIN_STYLIZED, SCALES, CARTOON_SKIN; "
                    "特效: GLASS, CRYSTAL, HOLOGRAM, ENERGY, PORTAL, EMISSION_GLOW, FORCE_FIELD; "
                    "卡通: TOON_BASIC, TOON_METAL, TOON_SKIN, TOON_FABRIC, ANIME_HAIR, GENSHIN_STYLE, CEL_SHADE"
    )
    material_name: Optional[str] = Field(default=None, description="材质名称(为空则自动命名)")
    object_name: Optional[str] = Field(default=None, description="要应用到的对象名称(为空则只创建不应用)")
    color_override: Optional[List[float]] = Field(default=None, description="覆盖基础颜色 [R,G,B] (0-1)")
    scale: float = Field(default=1.0, description="纹理缩放(影响图案大小)", gt=0)
    roughness_override: Optional[float] = Field(default=None, description="覆盖粗糙度 (0-1)", ge=0, le=1)


class MaterialWearInput(BaseModel):
    """材质磨损效果输入"""
    object_name: str = Field(..., description="对象名称")
    material_name: Optional[str] = Field(default=None, description="材质名称(为空则使用活动材质)")
    wear_type: str = Field(
        default="EDGE_WEAR",
        description="磨损类型: "
                    "EDGE_WEAR(边缘磨损/高光), SCRATCHES(划痕), RUST(锈迹), "
                    "DIRT(污垢), DUST(灰尘), MOSS(苔藓), PAINT_CHIP(掉漆)"
    )
    intensity: float = Field(default=0.5, description="磨损强度 (0-1)", ge=0, le=1)
    color: Optional[List[float]] = Field(default=None, description="磨损颜色 [R,G,B] (默认自动)")


# ==================== 工具注册 ====================

def register_procedural_material_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册程序化材质工具"""

    @mcp.tool(
        name="blender_procedural_material",
        annotations={
            "title": "程序化材质预设",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_procedural_material(params: ProceduralMaterialInput) -> str:
        """创建程序化材质预设（无需外部贴图）。

        提供50+种预设，覆盖金属、木材、石材、布料、自然、皮肤、特效、卡通等类别。
        所有材质通过Blender内置节点程序化生成，无需外部文件。

        可选择应用到指定对象，或仅创建材质供后续使用。

        Args:
            params: 预设名称、可选颜色/粗糙度覆盖、目标对象

        Returns:
            创建结果
        """
        result = await server.execute_command(
            "procedural_materials", "create",
            {
                "preset": params.preset,
                "material_name": params.material_name,
                "object_name": params.object_name,
                "color_override": params.color_override,
                "scale": params.scale,
                "roughness_override": params.roughness_override
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            mat_name = data.get("material_name", params.preset)
            applied_to = data.get("applied_to", "")
            msg = f"已创建程序化材质 '{mat_name}' (预设: {params.preset})"
            if applied_to:
                msg += f"，已应用到对象 '{applied_to}'"
            return msg
        else:
            return f"创建材质失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_material_wear",
        annotations={
            "title": "材质磨损效果",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_material_wear(params: MaterialWearInput) -> str:
        """为材质添加磨损/做旧效果。

        通过Pointiness(曲率)和程序化纹理在边缘和表面添加
        磨损、划痕、锈迹、污垢等效果，让材质更真实。

        适用于PBR写实和3A级风格。

        Args:
            params: 对象名、磨损类型、强度

        Returns:
            添加结果
        """
        result = await server.execute_command(
            "procedural_materials", "wear",
            {
                "object_name": params.object_name,
                "material_name": params.material_name,
                "wear_type": params.wear_type,
                "intensity": params.intensity,
                "color": params.color
            }
        )

        if result.get("success"):
            wear_names = {
                "EDGE_WEAR": "边缘磨损", "SCRATCHES": "划痕", "RUST": "锈迹",
                "DIRT": "污垢", "DUST": "灰尘", "MOSS": "苔藓", "PAINT_CHIP": "掉漆"
            }
            return f"已添加{wear_names.get(params.wear_type, params.wear_type)}效果，强度: {params.intensity}"
        else:
            return f"添加磨损效果失败: {result.get('error', {}).get('message', '未知错误')}"
