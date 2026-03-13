"""
Material Tools

Provides material creation, assignment, property setting, and other features.
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class BlendMode(str, Enum):
    """Blend mode"""

    OPAQUE = "OPAQUE"
    CLIP = "CLIP"
    HASHED = "HASHED"
    BLEND = "BLEND"


class TextureType(str, Enum):
    """Texture type"""

    COLOR = "COLOR"
    NORMAL = "NORMAL"
    ROUGHNESS = "ROUGHNESS"
    METALLIC = "METALLIC"
    EMISSION = "EMISSION"


class TextureMapping(str, Enum):
    """Texture mapping method"""

    UV = "UV"
    BOX = "BOX"
    SPHERE = "SPHERE"
    CYLINDER = "CYLINDER"


# ==================== Input Models ====================


class MaterialCreateInput(BaseModel):
    """Create material input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Material name", min_length=1, max_length=100)
    color: list[float] | None = Field(
        default=None, description="RGBA color [r, g, b, a], value range 0-1"
    )
    metallic: float | None = Field(default=None, description="Metallic", ge=0, le=1)
    roughness: float | None = Field(default=None, description="Roughness", ge=0, le=1)
    use_nodes: bool = Field(default=True, description="Use node-based material")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is not None:
            if len(v) not in [3, 4]:
                raise ValueError("Color must contain 3 or 4 components")
            if any(c < 0 or c > 1 for c in v):
                raise ValueError("Color components must be in 0-1 range")
        return v


class MaterialAssignInput(BaseModel):
    """Assign material input"""

    object_name: str = Field(..., description="Object name")
    material_name: str = Field(..., description="Material name")
    slot_index: int = Field(default=0, description="Material slot index", ge=0)


class MaterialSetPropertiesInput(BaseModel):
    """Set material properties input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    material_name: str = Field(..., description="Material name")
    color: list[float] | None = Field(default=None, description="RGBA color")
    metallic: float | None = Field(default=None, description="Metallic", ge=0, le=1)
    roughness: float | None = Field(default=None, description="Roughness", ge=0, le=1)
    specular: float | None = Field(default=None, description="Specular intensity", ge=0, le=1)
    emission_color: list[float] | None = Field(default=None, description="Emission color")
    emission_strength: float | None = Field(default=None, description="Emission strength", ge=0)
    alpha: float | None = Field(default=None, description="Alpha (opacity)", ge=0, le=1)
    blend_mode: BlendMode | None = Field(default=None, description="Blend mode")


class MaterialAddTextureInput(BaseModel):
    """Add texture input"""

    material_name: str = Field(..., description="Material name")
    texture_path: str = Field(..., description="Texture file path")
    texture_type: TextureType = Field(default=TextureType.COLOR, description="Texture type")
    mapping: TextureMapping = Field(default=TextureMapping.UV, description="Mapping method")


class MaterialListInput(BaseModel):
    """List materials input"""

    limit: int = Field(default=50, description="Return count limit", ge=1, le=500)


class MaterialDeleteInput(BaseModel):
    """Delete material input"""

    material_name: str = Field(..., description="Material name")


class NodeType(str, Enum):
    """Node type"""

    SSS = "SSS"  # Subsurface scattering configuration
    EMISSION = "EMISSION"  # Emission configuration
    MIX_RGB = "MIX_RGB"  # Mix RGB
    COLOR_RAMP = "COLOR_RAMP"  # Color ramp
    NOISE_TEXTURE = "NOISE_TEXTURE"  # Noise texture
    IMAGE_TEXTURE = "IMAGE_TEXTURE"  # Image texture
    NORMAL_MAP = "NORMAL_MAP"  # Normal map
    BUMP = "BUMP"  # Bump map


class MaterialNodeAddInput(BaseModel):
    """Add material node input"""

    material_name: str = Field(..., description="Material name")
    node_type: NodeType = Field(..., description="Node type")
    settings: dict | None = Field(
        default=None,
        description="Node settings (e.g. SSS: {subsurface: 0.3}, EMISSION: {color: [1,1,1], strength: 1.0})",
    )
    connect_to: dict | None = Field(
        default=None, description="Connection config {input: 'Base Color', output: 'Color'}"
    )
    location: list[float] | None = Field(default=None, description="Node position [x, y]")


class TextureApplyInput(BaseModel):
    """Apply texture map input"""

    material_name: str = Field(..., description="Material name")
    image_path: str = Field(..., description="Image file path")
    mapping_type: TextureMapping = Field(default=TextureMapping.UV, description="Mapping type")
    texture_type: TextureType = Field(default=TextureType.COLOR, description="Texture usage")


class SkinTone(str, Enum):
    """Skin tone type"""

    LIGHT = "LIGHT"  # Light skin tone
    MEDIUM = "MEDIUM"  # Medium skin tone
    DARK = "DARK"  # Dark skin tone
    CUSTOM = "CUSTOM"  # Custom


class CreateSkinMaterialInput(BaseModel):
    """Create skin material input"""

    name: str = Field(default="SkinMaterial", description="Material name")
    skin_tone: SkinTone = Field(default=SkinTone.MEDIUM, description="Skin tone type")
    custom_color: list[float] | None = Field(
        default=None, description="Custom color (used when skin_tone is CUSTOM)"
    )


class CreateToonMaterialInput(BaseModel):
    """Create toon material input"""

    name: str = Field(default="ToonMaterial", description="Material name")
    color: list[float] = Field(default=[0.8, 0.8, 0.8, 1.0], description="Base color")
    shadow_color: list[float] | None = Field(default=None, description="Shadow color")
    outline: bool = Field(default=False, description="Whether to add outline effect")


# ==================== Production Standard Optimization Input Models ====================


class GameEngine(str, Enum):
    """Target game engine"""

    UNITY = "UNITY"  # Unity engine
    UNREAL = "UNREAL"  # Unreal engine
    GODOT = "GODOT"  # Godot engine
    GENERIC = "GENERIC"  # Generic glTF
    BLENDER = "BLENDER"  # Blender Eevee/Cycles


class MaterialAnalyzeInput(BaseModel):
    """Material analysis input"""

    material_name: str = Field(..., description="Material name")
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="Target game engine")


class MaterialOptimizeInput(BaseModel):
    """Material optimization input"""

    material_name: str = Field(..., description="Material name")
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="Target game engine")
    fix_metallic: bool = Field(default=True, description="Fix metallic value (ensure 0 or 1)")
    fix_color_space: bool = Field(default=True, description="Fix texture color space")
    combine_textures: bool = Field(default=False, description="Combine texture channels (ORM/RMA)")


class PBRMaterialCreateInput(BaseModel):
    """Create standard PBR material input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Material name", min_length=1, max_length=100)
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="Target game engine")

    # PBR base properties
    base_color: list[float] | None = Field(
        default=None, description="Base color [r, g, b, a], value range 0-1"
    )
    metallic: float = Field(
        default=0.0, description="Metallic (production standard: 0=non-metal, 1=metal)", ge=0, le=1
    )
    roughness: float = Field(default=0.5, description="Roughness", ge=0, le=1)

    # Texture paths (optional)
    base_color_texture: str | None = Field(default=None, description="Base color texture path")
    normal_texture: str | None = Field(default=None, description="Normal map path")
    metallic_texture: str | None = Field(default=None, description="Metallic map path")
    roughness_texture: str | None = Field(default=None, description="Roughness map path")
    ao_texture: str | None = Field(default=None, description="Ambient occlusion map path")
    emission_texture: str | None = Field(default=None, description="Emission map path")

    # Additional settings
    emission_strength: float = Field(default=0.0, description="Emission strength", ge=0)
    alpha_mode: BlendMode = Field(default=BlendMode.OPAQUE, description="Alpha mode")
    double_sided: bool = Field(default=False, description="Double-sided rendering")

    @field_validator("base_color")
    @classmethod
    def validate_base_color(cls, v):
        if v is not None:
            if len(v) not in [3, 4]:
                raise ValueError("Color must contain 3 or 4 components")
            if any(c < 0 or c > 1 for c in v):
                raise ValueError("Color components must be in 0-1 range")
        return v


class TextureColorSpaceInput(BaseModel):
    """Texture color space setting input"""

    material_name: str = Field(..., description="Material name")
    auto_detect: bool = Field(default=True, description="Auto-detect and fix color space")


class MaterialBakeTexturesInput(BaseModel):
    """Bake material textures input"""

    material_name: str = Field(..., description="Material name")
    output_directory: str = Field(..., description="Output directory path")
    resolution: int = Field(default=1024, description="Texture resolution", ge=64, le=8192)
    bake_types: list[str] = Field(
        default=["DIFFUSE", "ROUGHNESS", "NORMAL"],
        description="Bake type list: DIFFUSE, ROUGHNESS, METALLIC, NORMAL, AO, EMISSION",
    )


# ==================== Tool Registration ====================


def register_material_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register material tools"""

    @mcp.tool(
        name="blender_material_create",
        annotations={
            "title": "Create Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_material_create(params: MaterialCreateInput) -> str:
        """Create a new material.

        Creates a PBR material with specified properties.

        Args:
            params: Material name and properties

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "material",
            "create",
            {
                "name": params.name,
                "color": params.color or [0.8, 0.8, 0.8, 1.0],
                "metallic": params.metallic if params.metallic is not None else 0.0,
                "roughness": params.roughness if params.roughness is not None else 0.5,
                "use_nodes": params.use_nodes,
            },
        )

        if result.get("success"):
            return f"Successfully created material '{params.name}'"
        else:
            return f"Failed to create material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_assign",
        annotations={
            "title": "Assign Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_material_assign(params: MaterialAssignInput) -> str:
        """Assign a material to an object.

        Args:
            params: Object name, material name, material slot index

        Returns:
            Assignment result
        """
        result = await server.execute_command(
            "material",
            "assign",
            {
                "object_name": params.object_name,
                "material_name": params.material_name,
                "slot_index": params.slot_index,
            },
        )

        if result.get("success"):
            return f"Assigned material '{params.material_name}' to object '{params.object_name}'"
        else:
            return f"Failed to assign material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_set_properties",
        annotations={
            "title": "Set Material Properties",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_material_set_properties(params: MaterialSetPropertiesInput) -> str:
        """Set material properties.

        Can set color, metallic, roughness, emission, and other properties.

        Args:
            params: Material name and properties to set

        Returns:
            Setting result
        """
        properties = {}
        if params.color is not None:
            properties["color"] = params.color
        if params.metallic is not None:
            properties["metallic"] = params.metallic
        if params.roughness is not None:
            properties["roughness"] = params.roughness
        if params.specular is not None:
            properties["specular"] = params.specular
        if params.emission_color is not None:
            properties["emission_color"] = params.emission_color
        if params.emission_strength is not None:
            properties["emission_strength"] = params.emission_strength
        if params.alpha is not None:
            properties["alpha"] = params.alpha
        if params.blend_mode is not None:
            properties["blend_mode"] = params.blend_mode.value

        if not properties:
            return "No properties specified"

        result = await server.execute_command(
            "material",
            "set_properties",
            {"material_name": params.material_name, "properties": properties},
        )

        if result.get("success"):
            return f"Material '{params.material_name}' properties updated"
        else:
            return f"Failed to set material properties: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_add_texture",
        annotations={
            "title": "Add Texture",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_material_add_texture(params: MaterialAddTextureInput) -> str:
        """Add a texture to a material.

        Supports color, normal, roughness, metallic, emission, and other texture types.

        Args:
            params: Material name, texture path, texture type

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "material",
            "add_texture",
            {
                "material_name": params.material_name,
                "texture_path": params.texture_path,
                "texture_type": params.texture_type.value,
                "mapping": params.mapping.value,
            },
        )

        if result.get("success"):
            return f"Added {params.texture_type.value} texture to material '{params.material_name}'"
        else:
            return (
                f"Failed to add texture: {result.get('error', {}).get('message', 'Unknown error')}"
            )

    @mcp.tool(
        name="blender_material_list",
        annotations={
            "title": "List Materials",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_material_list(params: MaterialListInput) -> str:
        """List all materials.

        Args:
            params: Return count limit

        Returns:
            Material list
        """
        result = await server.execute_command("material", "list", {"limit": params.limit})

        if not result.get("success"):
            return f"Failed to get material list: {result.get('error', {}).get('message', 'Unknown error')}"

        materials = result.get("data", {}).get("materials", [])
        total = result.get("data", {}).get("total", len(materials))

        lines = ["# Material List", ""]
        lines.append(f"Total: {total} material(s)")
        lines.append("")

        for mat in materials:
            lines.append(f"## {mat['name']}")
            if "color" in mat:
                lines.append(f"- Color: {mat['color']}")
            if "metallic" in mat:
                lines.append(f"- Metallic: {mat['metallic']}")
            if "roughness" in mat:
                lines.append(f"- Roughness: {mat['roughness']}")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_material_delete",
        annotations={
            "title": "Delete Material",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_material_delete(params: MaterialDeleteInput) -> str:
        """Delete a material.

        Args:
            params: Material name

        Returns:
            Deletion result
        """
        result = await server.execute_command(
            "material", "delete", {"material_name": params.material_name}
        )

        if result.get("success"):
            return f"Deleted material '{params.material_name}'"
        else:
            return f"Failed to delete material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_node_add",
        annotations={
            "title": "Add Material Node",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_material_node_add(params: MaterialNodeAddInput) -> str:
        """Add an advanced material node.

        Supports SSS (Subsurface Scattering), Emission, and other nodes
        for creating skin materials or glowing effects.

        Args:
            params: Material name, node type, settings

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "material",
            "node_add",
            {
                "material_name": params.material_name,
                "node_type": params.node_type.value,
                "settings": params.settings or {},
                "connect_to": params.connect_to,
                "location": params.location or [-300, 0],
            },
        )

        if result.get("success"):
            result.get("data", {})
            return f"Added {params.node_type.value} node to material '{params.material_name}'"
        else:
            return f"Failed to add node: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_texture_apply",
        annotations={
            "title": "Apply Texture Map",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_texture_apply(params: TextureApplyInput) -> str:
        """Apply a texture map to a material.

        Supports multiple texture types and mapping methods, can be used for adding flags, logos, etc.

        Args:
            params: Material name, image path, mapping type, texture usage

        Returns:
            Apply result
        """
        result = await server.execute_command(
            "material",
            "texture_apply",
            {
                "material_name": params.material_name,
                "image_path": params.image_path,
                "mapping_type": params.mapping_type.value,
                "texture_type": params.texture_type.value,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Applied texture '{data.get('image_name', 'N/A')}' to material '{params.material_name}'"
        else:
            return f"Failed to apply texture: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_create_skin_material",
        annotations={
            "title": "Create Skin Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_create_skin_material(params: CreateSkinMaterialInput) -> str:
        """Create a preset skin material.

        Includes subsurface scattering (SSS) effect, suitable for chibi/stylized character skin.

        Args:
            params: Material name, skin tone type

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "material",
            "create_skin_material",
            {
                "name": params.name,
                "skin_tone": params.skin_tone.value,
                "custom_color": params.custom_color,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            tone_names = {"LIGHT": "light", "MEDIUM": "medium", "DARK": "dark", "CUSTOM": "custom"}
            return f"Created {tone_names.get(params.skin_tone.value)} skin material '{data.get('material_name', params.name)}'"
        else:
            return f"Failed to create skin material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_create_toon_material",
        annotations={
            "title": "Create Toon Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_create_toon_material(params: CreateToonMaterialInput) -> str:
        """Create a toon-style material.

        Suitable for stylized cartoon rendering of chibi characters.

        Args:
            params: Material name, color, outline options

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "material",
            "create_toon_material",
            {
                "name": params.name,
                "color": params.color,
                "shadow_color": params.shadow_color,
                "outline": params.outline,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return f"Created toon material '{data.get('material_name', params.name)}'"
        else:
            return f"Failed to create toon material: {result.get('error', {}).get('message', 'Unknown error')}"

    # ==================== Production Standard Optimization Tools ====================

    @mcp.tool(
        name="blender_material_analyze",
        annotations={
            "title": "PBR Material Analysis",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_material_analyze(params: MaterialAnalyzeInput) -> str:
        """Analyze whether a material meets PBR production standards.

        Checks if material PBR parameters follow game engine best practices:
        - Whether metallic is 0 or 1 (production standard)
        - Whether texture color spaces are correct
        - Whether normal map settings are correct
        - Whether it meets target engine requirements

        Args:
            params: Material name and target engine

        Returns:
            Detailed material analysis report
        """
        result = await server.execute_command(
            "material",
            "analyze",
            {"material_name": params.material_name, "target_engine": params.target_engine.value},
        )

        if result.get("success"):
            data = result.get("data", {})

            lines = [f"# PBR Material Analysis Report: {params.material_name}", ""]

            # Basic info
            lines.append("## Basic Info")
            lines.append(f"- Uses nodes: {'Yes' if data.get('uses_nodes') else 'No'}")
            lines.append(f"- Target engine: {params.target_engine.value}")
            lines.append("")

            # PBR parameters
            pbr = data.get("pbr_values", {})
            lines.append("## PBR Parameters")
            lines.append(f"- Metallic: {pbr.get('metallic', 'N/A')}")
            lines.append(f"- Roughness: {pbr.get('roughness', 'N/A')}")
            lines.append(f"- Base color: {pbr.get('base_color', 'N/A')}")
            lines.append("")

            # Texture info
            textures = data.get("textures", [])
            if textures:
                lines.append("## Texture List")
                for tex in textures:
                    lines.append(f"- {tex.get('name', 'Unknown')}")
                    lines.append(f"  - Type: {tex.get('type', 'N/A')}")
                    lines.append(f"  - Color space: {tex.get('colorspace', 'N/A')}")
                    correct = tex.get("colorspace_correct", True)
                    lines.append(f"  - Color space correct: {'Yes' if correct else 'No ⚠️'}")
                lines.append("")

            # Issues and suggestions
            issues = data.get("issues", [])
            if issues:
                lines.append("## ⚠️ Issues Found")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")

            suggestions = data.get("suggestions", [])
            if suggestions:
                lines.append("## Optimization Suggestions")
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")
                lines.append("")

            # Compatibility score
            score = data.get("compatibility_score", 0)
            lines.append(f"## Compatibility Score: {score}/100")

            return "\n".join(lines)
        else:
            return f"Analysis failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_optimize",
        annotations={
            "title": "Optimize PBR Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_material_optimize(params: MaterialOptimizeInput) -> str:
        """Optimize material to meet game engine PBR standards.

        Automatically fixes common issues:
        - Corrects metallic values to 0 or 1
        - Fixes texture color spaces (normal/roughness etc. use Non-Color)
        - Optimizes settings for target engine

        Args:
            params: Material name and optimization options

        Returns:
            Optimization result
        """
        result = await server.execute_command(
            "material",
            "optimize",
            {
                "material_name": params.material_name,
                "target_engine": params.target_engine.value,
                "fix_metallic": params.fix_metallic,
                "fix_color_space": params.fix_color_space,
                "combine_textures": params.combine_textures,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            fixes = data.get("fixes_applied", [])

            lines = [f"Material '{params.material_name}' optimization completed", ""]

            if fixes:
                lines.append("Applied fixes:")
                for fix in fixes:
                    lines.append(f"- {fix}")
            else:
                lines.append("Material already meets standards, no fixes needed.")

            return "\n".join(lines)
        else:
            return f"Optimization failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_pbr_material_create",
        annotations={
            "title": "Create Standard PBR Material",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_pbr_material_create(params: PBRMaterialCreateInput) -> str:
        """Create a production-standard PBR material.

        Creates material following game engine best practices:
        - Automatically sets correct color spaces
        - Metallic follows 0/1 rule
        - Supports full PBR texture workflow

        Args:
            params: PBR material parameters and texture paths

        Returns:
            Creation result
        """
        result = await server.execute_command(
            "material",
            "create_pbr",
            {
                "name": params.name,
                "target_engine": params.target_engine.value,
                "base_color": params.base_color or [0.8, 0.8, 0.8, 1.0],
                "metallic": params.metallic,
                "roughness": params.roughness,
                "base_color_texture": params.base_color_texture,
                "normal_texture": params.normal_texture,
                "metallic_texture": params.metallic_texture,
                "roughness_texture": params.roughness_texture,
                "ao_texture": params.ao_texture,
                "emission_texture": params.emission_texture,
                "emission_strength": params.emission_strength,
                "alpha_mode": params.alpha_mode.value,
                "double_sided": params.double_sided,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            textures_loaded = data.get("textures_loaded", [])

            lines = [f"Successfully created PBR material '{params.name}'", ""]
            lines.append(f"- Target engine: {params.target_engine.value}")
            lines.append(f"- Metallic: {params.metallic}")
            lines.append(f"- Roughness: {params.roughness}")

            if textures_loaded:
                lines.append("")
                lines.append("Loaded textures:")
                for tex in textures_loaded:
                    lines.append(f"- {tex}")

            return "\n".join(lines)
        else:
            return f"Failed to create PBR material: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_texture_colorspace_fix",
        annotations={
            "title": "Fix Texture Color Space",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_texture_colorspace_fix(params: TextureColorSpaceInput) -> str:
        """Automatically fix texture color space settings in a material.

        Automatically sets correct color space based on texture usage:
        - Color maps: sRGB
        - Normal/roughness/metallic: Non-Color

        Args:
            params: Material name

        Returns:
            Fix result
        """
        result = await server.execute_command(
            "material",
            "fix_colorspace",
            {"material_name": params.material_name, "auto_detect": params.auto_detect},
        )

        if result.get("success"):
            data = result.get("data", {})
            fixed = data.get("fixed_textures", [])

            if fixed:
                lines = ["Fixed color space for the following textures:"]
                for tex in fixed:
                    lines.append(
                        f"- {tex.get('name')}: {tex.get('old_space')} -> {tex.get('new_space')}"
                    )
                return "\n".join(lines)
            else:
                return "All texture color spaces are already correct, no fixes needed."
        else:
            return f"Fix failed: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_material_bake_textures",
        annotations={
            "title": "Bake Material Textures",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def blender_material_bake_textures(params: MaterialBakeTexturesInput) -> str:
        """Bake procedural material to texture images.

        Supports baking: diffuse, roughness, metallic, normal, AO, emission.
        Baked textures can be exported to game engines.

        Args:
            params: Material name, output directory, resolution, bake types

        Returns:
            Bake result
        """
        result = await server.execute_command(
            "material",
            "bake_textures",
            {
                "material_name": params.material_name,
                "output_directory": params.output_directory,
                "resolution": params.resolution,
                "bake_types": params.bake_types,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            baked = data.get("baked_textures", [])

            lines = [f"Material '{params.material_name}' texture bake completed", ""]
            lines.append(f"Output directory: {params.output_directory}")
            lines.append(f"Resolution: {params.resolution}x{params.resolution}")
            lines.append("")

            if baked:
                lines.append("Baked textures:")
                for tex in baked:
                    lines.append(f"- {tex}")

            return "\n".join(lines)
        else:
            return f"Bake failed: {result.get('error', {}).get('message', 'Unknown error')}"
