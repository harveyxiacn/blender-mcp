"""
Procedural material preset tools

Provides 50+ procedural material presets generated through node combinations without external textures.
Covers categories including metal, wood, stone, fabric, nature, skin, effects, and more.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class MaterialCategory(str, Enum):
    """Material category"""

    METAL = "METAL"
    WOOD = "WOOD"
    STONE = "STONE"
    FABRIC = "FABRIC"
    NATURE = "NATURE"
    SKIN = "SKIN"
    EFFECT = "EFFECT"
    TOON = "TOON"


class ProceduralMaterialInput(BaseModel):
    """Procedural material preset input"""

    preset: str = Field(
        ...,
        description="Material preset name. Available presets: "
        "Metal: STEEL, IRON, GOLD, SILVER, BRONZE, COPPER, CHROME, BRUSHED_METAL, RUSTY_METAL, DAMASCUS; "
        "Wood: OAK, PINE, CHERRY, WALNUT, BIRCH, BAMBOO, PLYWOOD, AGED_WOOD; "
        "Stone: GRANITE, MARBLE, LIMESTONE, SLATE, COBBLESTONE, SANDSTONE, BRICK, TILE, CONCRETE; "
        "Fabric: COTTON, SILK, LEATHER, DENIM, VELVET, CANVAS, WOOL, CHAIN_MAIL; "
        "Nature: GRASS, DIRT, SAND, SNOW, MUD, GRAVEL, MOSS, LAVA, WATER, ICE; "
        "Skin: SKIN_REALISTIC, SKIN_STYLIZED, SCALES, CARTOON_SKIN; "
        "Effects: GLASS, CRYSTAL, HOLOGRAM, ENERGY, PORTAL, EMISSION_GLOW, FORCE_FIELD; "
        "Toon: TOON_BASIC, TOON_METAL, TOON_SKIN, TOON_FABRIC, ANIME_HAIR, GENSHIN_STYLE, CEL_SHADE",
    )
    material_name: str | None = Field(
        default=None, description="Material name (auto-named if empty)"
    )
    object_name: str | None = Field(
        default=None, description="Object name to apply to (create only if empty)"
    )
    color_override: list[float] | None = Field(
        default=None, description="Override base color [R,G,B] (0-1)"
    )
    scale: float = Field(default=1.0, description="Texture scale (affects pattern size)", gt=0)
    roughness_override: float | None = Field(
        default=None, description="Override roughness (0-1)", ge=0, le=1
    )


class MaterialWearInput(BaseModel):
    """Material wear effect input"""

    object_name: str = Field(..., description="Object name")
    material_name: str | None = Field(
        default=None, description="Material name (uses active material if empty)"
    )
    wear_type: str = Field(
        default="EDGE_WEAR",
        description="Wear type: "
        "EDGE_WEAR (edge wear/highlights), SCRATCHES (scratches), RUST (rust), "
        "DIRT (dirt), DUST (dust), MOSS (moss), PAINT_CHIP (paint chipping)",
    )
    intensity: float = Field(default=0.5, description="Wear intensity (0-1)", ge=0, le=1)
    color: list[float] | None = Field(
        default=None, description="Wear color [R,G,B] (auto by default)"
    )


# ==================== Tool Registration ====================


def register_procedural_material_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register procedural material tools"""

    @mcp.tool(
        name="blender_procedural_material",
        annotations={
            "title": "Procedural Material Preset",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_procedural_material(params: ProceduralMaterialInput) -> str:
        """Create a procedural material preset (no external textures required).

        Provides 50+ presets covering metal, wood, stone, fabric, nature, skin, effects, toon, and more.
        All materials are procedurally generated using Blender's built-in nodes, no external files needed.

        Optionally apply to a specified object, or just create the material for later use.

        Args:
            params: Preset name, optional color/roughness overrides, target object

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "procedural_materials",
            "create",
            {
                "preset": params.preset,
                "material_name": params.material_name,
                "object_name": params.object_name,
                "color_override": params.color_override,
                "scale": params.scale,
                "roughness_override": params.roughness_override,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            mat_name = data.get("material_name", params.preset)
            applied_to = data.get("applied_to", "")
            msg = f"Created procedural material '{mat_name}' (preset: {params.preset})"
            if applied_to:
                msg += f", applied to object '{applied_to}'"
            return msg
        else:
            return f"Failed to create material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_wear",
        annotations={
            "title": "Material Wear Effect",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_material_wear(params: MaterialWearInput) -> str:
        """Add wear/aging effects to a material.

        Uses Pointiness (curvature) and procedural textures to add
        wear, scratches, rust, dirt, and other effects on edges and surfaces
        for more realistic materials.

        Suitable for PBR realistic and AAA styles.

        Args:
            params: Object name, wear type, intensity

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "procedural_materials",
            "wear",
            {
                "object_name": params.object_name,
                "material_name": params.material_name,
                "wear_type": params.wear_type,
                "intensity": params.intensity,
                "color": params.color,
            },
        )

        if result.get("success"):
            wear_names = {
                "EDGE_WEAR": "edge wear",
                "SCRATCHES": "scratches",
                "RUST": "rust",
                "DIRT": "dirt",
                "DUST": "dust",
                "MOSS": "moss",
                "PAINT_CHIP": "paint chipping",
            }
            return f"Added {wear_names.get(params.wear_type, params.wear_type)} effect, intensity: {params.intensity}"
        else:
            return f"Failed to add wear effect: {result.get('error', {}).get('message', 'Unknown error')}"
