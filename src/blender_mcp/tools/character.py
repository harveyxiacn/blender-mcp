"""
Character System Tools

Provides character creation and editing features, including advanced face system, clothing system, hair system, and more.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class BodyType(str, Enum):
    """Body type"""

    SLIM = "SLIM"
    AVERAGE = "AVERAGE"
    MUSCULAR = "MUSCULAR"
    HEAVY = "HEAVY"


class Gender(str, Enum):
    """Gender"""

    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"


class HairStyle(str, Enum):
    """Hair style"""

    BALD = "BALD"
    BUZZ = "BUZZ"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"
    VERY_LONG = "VERY_LONG"
    PONYTAIL = "PONYTAIL"
    BUN = "BUN"
    BRAIDS = "BRAIDS"
    MOHAWK = "MOHAWK"
    AFRO = "AFRO"
    CURLY = "CURLY"
    WAVY = "WAVY"
    ANCIENT_MALE = "ANCIENT_MALE"
    ANCIENT_FEMALE = "ANCIENT_FEMALE"
    TOPKNOT = "TOPKNOT"


class ClothingType(str, Enum):
    """Clothing type"""

    SHIRT = "SHIRT"
    T_SHIRT = "T_SHIRT"
    PANTS = "PANTS"
    SHORTS = "SHORTS"
    JACKET = "JACKET"
    COAT = "COAT"
    DRESS = "DRESS"
    SKIRT = "SKIRT"
    ROBE = "ROBE"
    HANFU_TOP = "HANFU_TOP"
    HANFU_BOTTOM = "HANFU_BOTTOM"
    ARMOR_CHEST = "ARMOR_CHEST"
    ARMOR_FULL = "ARMOR_FULL"
    CAPE = "CAPE"
    SHOES = "SHOES"
    BOOTS = "BOOTS"
    GLOVES = "GLOVES"
    HAT = "HAT"
    HELMET = "HELMET"


class OutfitStyle(str, Enum):
    """Outfit style"""

    CASUAL = "CASUAL"
    FORMAL = "FORMAL"
    WARRIOR = "WARRIOR"
    MAGE = "MAGE"
    HANFU = "HANFU"
    ANCIENT_WARRIOR = "ANCIENT_WARRIOR"
    NOBLE = "NOBLE"
    DANCER = "DANCER"


class Expression(str, Enum):
    """Facial expression"""

    NEUTRAL = "neutral"
    SMILE = "smile"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEAR = "fear"
    DISGUST = "disgust"
    CONTEMPT = "contempt"


# ==================== Input Models ====================


class CharacterCreateHumanoidInput(BaseModel):
    """Create humanoid character input"""

    name: str | None = Field(default="Character", description="Character name")
    height: float = Field(default=1.8, description="Height (meters)", ge=0.5, le=3.0)
    body_type: BodyType = Field(default=BodyType.AVERAGE, description="Body type")
    gender: Gender = Field(default=Gender.NEUTRAL, description="Gender")
    subdivisions: int = Field(default=2, description="Subdivision level", ge=0, le=4)
    create_face_rig: bool = Field(default=True, description="Whether to create face shape keys")


class CharacterAddFaceFeaturesInput(BaseModel):
    """Add face features input (enhanced)"""

    character_name: str = Field(..., description="Character name")
    # Eye parameters
    eye_size: float = Field(default=1.0, description="Eye size", ge=0.5, le=1.5)
    eye_distance: float = Field(default=1.0, description="Eye spacing", ge=0.8, le=1.2)
    eye_height: float = Field(default=1.0, description="Eye height", ge=0.8, le=1.2)
    eye_tilt: float = Field(default=0.0, description="Eye tilt", ge=-0.3, le=0.3)
    eye_depth: float = Field(default=1.0, description="Eye depth", ge=0.8, le=1.2)
    # Nose parameters
    nose_length: float = Field(default=1.0, description="Nose length", ge=0.5, le=1.5)
    nose_width: float = Field(default=1.0, description="Nose width", ge=0.7, le=1.3)
    nose_height: float = Field(default=1.0, description="Nose bridge height", ge=0.8, le=1.2)
    nose_tip: float = Field(default=1.0, description="Nose tip size", ge=0.8, le=1.2)
    # Mouth parameters
    mouth_width: float = Field(default=1.0, description="Mouth width", ge=0.7, le=1.3)
    mouth_height: float = Field(default=1.0, description="Mouth height", ge=0.8, le=1.2)
    lip_thickness_upper: float = Field(
        default=1.0, description="Upper lip thickness", ge=0.5, le=1.5
    )
    lip_thickness_lower: float = Field(
        default=1.0, description="Lower lip thickness", ge=0.5, le=1.5
    )
    # Jaw and face shape parameters
    jaw_width: float = Field(default=1.0, description="Jaw width", ge=0.7, le=1.3)
    jaw_height: float = Field(default=1.0, description="Jaw height", ge=0.8, le=1.2)
    chin_length: float = Field(default=1.0, description="Chin length", ge=0.8, le=1.2)
    cheekbone_height: float = Field(default=1.0, description="Cheekbone height", ge=0.8, le=1.2)
    cheekbone_width: float = Field(default=1.0, description="Cheekbone width", ge=0.8, le=1.2)
    # Forehead parameters
    forehead_height: float = Field(default=1.0, description="Forehead height", ge=0.8, le=1.2)
    forehead_width: float = Field(default=1.0, description="Forehead width", ge=0.8, le=1.2)
    # Ear parameters
    ear_size: float = Field(default=1.0, description="Ear size", ge=0.7, le=1.3)
    ear_position: float = Field(default=1.0, description="Ear position", ge=0.8, le=1.2)


class CharacterSetExpressionInput(BaseModel):
    """Set facial expression input"""

    character_name: str = Field(..., description="Character name")
    expression: Expression = Field(default=Expression.NEUTRAL, description="Expression type")
    intensity: float = Field(default=1.0, description="Expression intensity", ge=0.0, le=1.0)


class CharacterAddHairInput(BaseModel):
    """Add hair input (enhanced)"""

    character_name: str = Field(..., description="Character name")
    hair_style: HairStyle = Field(default=HairStyle.SHORT, description="Hair style")
    hair_color: list[float] | None = Field(default=None, description="Hair color [r, g, b]")
    use_particles: bool = Field(default=True, description="Use particle hair")
    hair_density: float = Field(default=1.0, description="Hair density multiplier", ge=0.1, le=3.0)
    hair_thickness: float = Field(
        default=1.0, description="Hair thickness multiplier", ge=0.5, le=2.0
    )
    use_dynamics: bool = Field(default=False, description="Enable hair dynamics")


class CharacterAddClothingInput(BaseModel):
    """Add clothing input (enhanced)"""

    character_name: str = Field(..., description="Character name")
    clothing_type: ClothingType = Field(..., description="Clothing type")
    color: list[float] | None = Field(default=None, description="Primary clothing color [r, g, b]")
    secondary_color: list[float] | None = Field(
        default=None, description="Secondary clothing color [r, g, b]"
    )
    use_cloth_simulation: bool = Field(default=False, description="Enable cloth simulation")
    metallic: float = Field(default=0.0, description="Metallic", ge=0.0, le=1.0)
    roughness: float = Field(default=0.8, description="Roughness", ge=0.0, le=1.0)
    pattern: str | None = Field(default=None, description="Pattern: SOLID, STRIPES, PLAID, FLORAL")


class CharacterCreateOutfitInput(BaseModel):
    """Create complete outfit input"""

    character_name: str = Field(..., description="Character name")
    outfit_style: OutfitStyle = Field(default=OutfitStyle.CASUAL, description="Outfit style")
    color_scheme: str = Field(
        default="DEFAULT",
        description="Color scheme: DEFAULT, RED, BLUE, GREEN, WHITE, BLACK, GOLD, PURPLE",
    )
    use_cloth_simulation: bool = Field(default=False, description="Enable cloth simulation")


# ==================== Tool Registration ====================


def register_character_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register character system tools"""

    @mcp.tool(
        name="blender_character_create_humanoid",
        annotations={
            "title": "Create Humanoid Character",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_character_create_humanoid(params: CharacterCreateHumanoidInput) -> str:
        """Create a humanoid base mesh (enhanced).

        Creates a detailed humanoid character mesh including:
        - Adjustable height, body type, and gender
        - Face shape key system
        - Body vertex groups (for clothing binding)

        Args:
            params: Character name, body type settings, whether to create face system

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "character",
            "create_humanoid",
            {
                "name": params.name,
                "height": params.height,
                "body_type": params.body_type.value,
                "gender": params.gender.value,
                "subdivisions": params.subdivisions,
                "create_face_rig": params.create_face_rig,
            },
        )

        if result.get("success"):
            body_types = {
                "SLIM": "slim",
                "AVERAGE": "average",
                "MUSCULAR": "muscular",
                "HEAVY": "heavy",
            }
            data = result.get("data", {})
            face_info = " (with face system)" if data.get("has_face_rig") else ""
            return f"Successfully created character '{params.name}', height: {params.height}m, body type: {body_types.get(params.body_type.value)}{face_info}"
        else:
            return f"Failed to create character: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_add_face_features",
        annotations={
            "title": "Add Face Features",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_character_add_face_features(params: CharacterAddFaceFeaturesInput) -> str:
        """Adjust a character's face features (enhanced - using shape keys).

        Supports fine-tuning of 22 face parameters:
        - Eyes: size, spacing, height, tilt, depth
        - Nose: length, width, height, tip
        - Mouth: width, height, upper/lower lip thickness
        - Face shape: jaw width/height, cheekbones, forehead
        - Ears: size, position

        Args:
            params: Character name and face parameters

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character",
            "add_face_features",
            {
                "character_name": params.character_name,
                "eye_size": params.eye_size,
                "eye_distance": params.eye_distance,
                "eye_height": params.eye_height,
                "eye_tilt": params.eye_tilt,
                "eye_depth": params.eye_depth,
                "nose_length": params.nose_length,
                "nose_width": params.nose_width,
                "nose_height": params.nose_height,
                "nose_tip": params.nose_tip,
                "mouth_width": params.mouth_width,
                "mouth_height": params.mouth_height,
                "lip_thickness_upper": params.lip_thickness_upper,
                "lip_thickness_lower": params.lip_thickness_lower,
                "jaw_width": params.jaw_width,
                "jaw_height": params.jaw_height,
                "chin_length": params.chin_length,
                "cheekbone_height": params.cheekbone_height,
                "cheekbone_width": params.cheekbone_width,
                "forehead_height": params.forehead_height,
                "forehead_width": params.forehead_width,
                "ear_size": params.ear_size,
                "ear_position": params.ear_position,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            count = len(data.get("applied_params", []))
            return f"Adjusted {count} face parameters for '{params.character_name}'"
        else:
            return f"Failed to add face features: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_set_expression",
        annotations={
            "title": "Set Facial Expression",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_character_set_expression(params: CharacterSetExpressionInput) -> str:
        """Set a character's facial expression.

        Supported expressions:
        - neutral: Neutral
        - smile: Smile
        - sad: Sad
        - angry: Angry
        - surprised: Surprised
        - fear: Fear
        - disgust: Disgust
        - contempt: Contempt

        Args:
            params: Character name, expression type, intensity

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character",
            "set_face_expression",
            {
                "character_name": params.character_name,
                "expression": params.expression.value,
                "intensity": params.intensity,
            },
        )

        expr_names = {
            "neutral": "neutral",
            "smile": "smile",
            "sad": "sad",
            "angry": "angry",
            "surprised": "surprised",
            "fear": "fear",
            "disgust": "disgust",
            "contempt": "contempt",
        }

        if result.get("success"):
            return f"Set {expr_names.get(params.expression.value, params.expression.value)} expression for '{params.character_name}' (intensity: {params.intensity:.0%})"
        else:
            return f"Failed to set expression: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_add_hair",
        annotations={
            "title": "Add Hair",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_character_add_hair(params: CharacterAddHairInput) -> str:
        """Add a hair system to a character (enhanced).

        Supports 16 hair style presets including:
        - Basic styles: BALD, BUZZ, SHORT, MEDIUM, LONG, VERY_LONG
        - Special styles: PONYTAIL, BUN, BRAIDS, MOHAWK, AFRO
        - Curly types: CURLY, WAVY
        - Ancient styles: ANCIENT_MALE, ANCIENT_FEMALE, TOPKNOT

        Args:
            params: Character name, hair style, color, density, dynamics, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character",
            "add_hair",
            {
                "character_name": params.character_name,
                "hair_style": params.hair_style.value,
                "hair_color": params.hair_color or [0.1, 0.08, 0.05],
                "use_particles": params.use_particles,
                "hair_density": params.hair_density,
                "hair_thickness": params.hair_thickness,
                "use_dynamics": params.use_dynamics,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            dyn_info = " (dynamics enabled)" if data.get("dynamics_enabled") else ""
            return (
                f"Added {params.hair_style.value} hair style to '{params.character_name}'{dyn_info}"
            )
        else:
            return f"Failed to add hair: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_add_clothing",
        annotations={
            "title": "Add Clothing",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_character_add_clothing(params: CharacterAddClothingInput) -> str:
        """Add clothing to a character (enhanced).

        Supports 19 clothing types:
        - Tops: SHIRT, T_SHIRT, JACKET, COAT
        - Bottoms: PANTS, SHORTS, SKIRT
        - Full body: DRESS, ROBE
        - Traditional: HANFU_TOP, HANFU_BOTTOM
        - Armor: ARMOR_CHEST, ARMOR_FULL, HELMET
        - Accessories: CAPE, SHOES, BOOTS, GLOVES, HAT

        Args:
            params: Character name, clothing type, color, cloth simulation, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character",
            "add_clothing",
            {
                "character_name": params.character_name,
                "clothing_type": params.clothing_type.value,
                "color": params.color or [0.5, 0.5, 0.5],
                "secondary_color": params.secondary_color,
                "use_cloth_simulation": params.use_cloth_simulation,
                "metallic": params.metallic,
                "roughness": params.roughness,
                "pattern": params.pattern,
            },
        )

        clothing_names = {
            "SHIRT": "shirt",
            "T_SHIRT": "T-shirt",
            "PANTS": "pants",
            "SHORTS": "shorts",
            "JACKET": "jacket",
            "COAT": "coat",
            "DRESS": "dress",
            "SKIRT": "skirt",
            "ROBE": "robe",
            "HANFU_TOP": "hanfu top",
            "HANFU_BOTTOM": "hanfu bottom",
            "ARMOR_CHEST": "chest armor",
            "ARMOR_FULL": "full armor",
            "CAPE": "cape",
            "SHOES": "shoes",
            "BOOTS": "boots",
            "GLOVES": "gloves",
            "HAT": "hat",
            "HELMET": "helmet",
        }

        if result.get("success"):
            data = result.get("data", {})
            cloth_info = " (cloth simulation enabled)" if data.get("cloth_simulation") else ""
            name = clothing_names.get(params.clothing_type.value, params.clothing_type.value)
            return f"Added {name} to '{params.character_name}'{cloth_info}"
        else:
            return (
                f"Failed to add clothing: {result.get('error', {}).get('message', 'unknown error')}"
            )

    @mcp.tool(
        name="blender_character_create_outfit",
        annotations={
            "title": "Create Complete Outfit",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_character_create_outfit(params: CharacterCreateOutfitInput) -> str:
        """Create a complete outfit for a character.

        Supports 8 outfit styles:
        - CASUAL: Casual wear (T-shirt + pants + shoes)
        - FORMAL: Formal wear (shirt + pants + shoes)
        - WARRIOR: Warrior outfit (chest armor + pants + boots + gloves)
        - MAGE: Mage outfit (robe + boots + gloves + hat)
        - HANFU: Hanfu (top + bottom + shoes)
        - ANCIENT_WARRIOR: Ancient warrior (full armor + boots + helmet)
        - NOBLE: Noble outfit (jacket + pants + boots + cape)
        - DANCER: Dancer outfit (dress + shoes)

        Color schemes: DEFAULT, RED, BLUE, GREEN, WHITE, BLACK, GOLD, PURPLE

        Args:
            params: Character name, outfit style, color scheme, cloth simulation

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character",
            "create_outfit",
            {
                "character_name": params.character_name,
                "outfit_style": params.outfit_style.value,
                "color_scheme": params.color_scheme,
                "use_cloth_simulation": params.use_cloth_simulation,
            },
        )

        style_names = {
            "CASUAL": "casual",
            "FORMAL": "formal",
            "WARRIOR": "warrior",
            "MAGE": "mage",
            "HANFU": "hanfu",
            "ANCIENT_WARRIOR": "ancient warrior",
            "NOBLE": "noble",
            "DANCER": "dancer",
        }

        if result.get("success"):
            data = result.get("data", {})
            items = data.get("items_created", [])
            name = style_names.get(params.outfit_style.value, params.outfit_style.value)
            return f"Created {name} outfit for '{params.character_name}' with {len(items)} clothing items"
        else:
            return f"Failed to create outfit: {result.get('error', {}).get('message', 'unknown error')}"
