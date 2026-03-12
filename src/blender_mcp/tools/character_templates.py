"""
Character Template Tools

Provides preset character template creation, face system, clothing system, hair system, and more.
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class CharacterTemplateInput(BaseModel):
    """Character template input"""
    template: str = Field(
        default="chibi",
        description="Template type: chibi, realistic, anime, stylized, mascot"
    )
    name: str = Field(default="Character", description="Character name")
    height: float = Field(default=1.7, description="Character height", ge=0.5, le=3.0)
    location: Optional[List[float]] = Field(default=None, description="Location")
    skin_color: Optional[List[float]] = Field(default=None, description="Skin color RGBA")
    gender: str = Field(default="neutral", description="Gender: male, female, neutral")


class FaceExpressionInput(BaseModel):
    """Face expression input"""
    character_name: str = Field(..., description="Character name prefix")
    expression: str = Field(
        default="neutral",
        description="Expression: neutral, happy, sad, angry, surprised, wink, smile"
    )
    intensity: float = Field(default=1.0, description="Expression intensity", ge=0.0, le=1.0)


class FaceSetupInput(BaseModel):
    """Face setup input"""
    character_name: str = Field(..., description="Character name prefix")
    eye_size: float = Field(default=1.0, description="Eye size", ge=0.5, le=2.0)
    eye_spacing: float = Field(default=1.0, description="Eye spacing", ge=0.5, le=1.5)
    mouth_width: float = Field(default=1.0, description="Mouth width", ge=0.5, le=1.5)
    nose_size: float = Field(default=1.0, description="Nose size", ge=0.5, le=1.5)


class ClothingAddInput(BaseModel):
    """Add clothing input"""
    character_name: str = Field(..., description="Character name prefix")
    clothing_type: str = Field(
        default="shirt",
        description="Clothing type: shirt, pants, jacket, dress, uniform, sportswear"
    )
    color: Optional[List[float]] = Field(default=None, description="Color RGBA")
    style: str = Field(default="casual", description="Style: casual, formal, sport, fantasy")


class HairCreateInput(BaseModel):
    """Create hair input"""
    character_name: str = Field(..., description="Character name prefix")
    hair_style: str = Field(
        default="short",
        description="Hair style: short, medium, long, ponytail, braided, spiky, bald"
    )
    color: Optional[List[float]] = Field(default=None, description="Hair color RGBA")
    volume: float = Field(default=1.0, description="Volume", ge=0.5, le=2.0)


class AccessoryAddInput(BaseModel):
    """Add accessory input"""
    character_name: str = Field(..., description="Character name prefix")
    accessory_type: str = Field(
        default="glasses",
        description="Accessory type: glasses, hat, earrings, necklace, watch, medal, badge"
    )
    color: Optional[List[float]] = Field(default=None, description="Color RGBA")
    location: str = Field(default="auto", description="Location: auto, head, neck, wrist, chest")


# ==================== Tool Registration ====================

def register_character_template_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register character template tools"""

    @mcp.tool(
        name="blender_character_template_create",
        annotations={
            "title": "Create Character from Template",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_template_create(params: CharacterTemplateInput) -> str:
        """Create a character from a preset template.

        Supported templates:
        - chibi: Cute chibi style, big head small body
        - realistic: Realistic human proportions
        - anime: Anime style
        - stylized: Stylized cartoon
        - mascot: Mascot style

        Args:
            params: Template type, name, size, etc.

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "character_template", "create",
            {
                "template": params.template,
                "name": params.name,
                "height": params.height,
                "location": params.location or [0, 0, 0],
                "skin_color": params.skin_color,
                "gender": params.gender
            }
        )

        if result.get("success"):
            parts = result.get("data", {}).get("parts_created", 0)
            return f"Successfully created {params.template} style character '{params.name}' with {parts} parts"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_face_expression",
        annotations={
            "title": "Set Facial Expression",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_face_expression(params: FaceExpressionInput) -> str:
        """Set a character's facial expression.

        Args:
            params: Character name, expression type, intensity

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character_template", "face_expression",
            {
                "character_name": params.character_name,
                "expression": params.expression,
                "intensity": params.intensity
            }
        )

        if result.get("success"):
            return f"Set expression of '{params.character_name}' to {params.expression}"
        else:
            return f"Setting failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_face_setup",
        annotations={
            "title": "Adjust Face Features",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_face_setup(params: FaceSetupInput) -> str:
        """Adjust a character's face feature proportions.

        Args:
            params: Eye size, spacing, mouth width, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "character_template", "face_setup",
            {
                "character_name": params.character_name,
                "eye_size": params.eye_size,
                "eye_spacing": params.eye_spacing,
                "mouth_width": params.mouth_width,
                "nose_size": params.nose_size
            }
        )

        if result.get("success"):
            return f"Adjusted face features for '{params.character_name}'"
        else:
            return f"Adjustment failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_clothing_add",
        annotations={
            "title": "Add Clothing",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_clothing_add(params: ClothingAddInput) -> str:
        """Add clothing to a character.

        Args:
            params: Clothing type, color, style

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "character_template", "clothing_add",
            {
                "character_name": params.character_name,
                "clothing_type": params.clothing_type,
                "color": params.color,
                "style": params.style
            }
        )

        if result.get("success"):
            return f"Added {params.clothing_type} to '{params.character_name}'"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_hair_create",
        annotations={
            "title": "Create Hair Style",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_hair_create(params: HairCreateInput) -> str:
        """Create a hair style for a character.

        Args:
            params: Hair style type, color, volume

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "character_template", "hair_create",
            {
                "character_name": params.character_name,
                "hair_style": params.hair_style,
                "color": params.color,
                "volume": params.volume
            }
        )

        if result.get("success"):
            return f"Created {params.hair_style} hair style for '{params.character_name}'"
        else:
            return f"Creation failed: {result.get('error', {}).get('message', 'unknown error')}"

    @mcp.tool(
        name="blender_character_accessory_add",
        annotations={
            "title": "Add Accessory",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_accessory_add(params: AccessoryAddInput) -> str:
        """Add an accessory to a character (glasses, hat, jewelry, etc.).

        Args:
            params: Accessory type, color, location

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "character_template", "accessory_add",
            {
                "character_name": params.character_name,
                "accessory_type": params.accessory_type,
                "color": params.color,
                "location": params.location
            }
        )

        if result.get("success"):
            return f"Added {params.accessory_type} to '{params.character_name}'"
        else:
            return f"Addition failed: {result.get('error', {}).get('message', 'unknown error')}"
