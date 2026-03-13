"""
Sport character tools

Provides athlete character modeling features, supporting chibi/realistic sport character creation,
including table tennis-specific equipment, sportswear, athletic poses, reference image loading, web-optimized export, etc.

Designed for:
- Fan Zhendong fan site 3D model creation
- Table tennis/sports game character modeling
- Chibi athletes (Pop Mart style)
"""

from enum import Enum
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Enum Definitions ====================


class SportType(str, Enum):
    """Sport type"""

    TABLE_TENNIS = "TABLE_TENNIS"
    BASKETBALL = "BASKETBALL"
    SOCCER = "SOCCER"
    BADMINTON = "BADMINTON"
    TENNIS = "TENNIS"
    VOLLEYBALL = "VOLLEYBALL"


class CharacterStyle(str, Enum):
    """Character style"""

    CHIBI = "CHIBI"  # Chibi/Pop Mart (head-body ratio 2:1~2.5:1)
    ANIME = "ANIME"  # Anime (head-body ratio 5:1~6:1)
    STYLIZED = "STYLIZED"  # Stylized (head-body ratio 4:1)
    REALISTIC = "REALISTIC"  # Realistic (head-body ratio 7:1~8:1)


class AthletePreset(str, Enum):
    """Athlete preset"""

    FAN_ZHENDONG = "FAN_ZHENDONG"  # Fan Zhendong
    CUSTOM = "CUSTOM"  # Custom


class EquipmentType(str, Enum):
    """Sport equipment type"""

    # Table tennis
    PADDLE = "PADDLE"  # Table tennis paddle
    BALL = "BALL"  # Table tennis ball
    TABLE = "TABLE"  # Table tennis table
    NET = "NET"  # Net
    # General accessories
    WRISTBAND = "WRISTBAND"  # Wristband
    HEADBAND = "HEADBAND"  # Headband
    MEDAL_GOLD = "MEDAL_GOLD"  # Gold medal
    MEDAL_SILVER = "MEDAL_SILVER"  # Silver medal
    MEDAL_BRONZE = "MEDAL_BRONZE"  # Bronze medal
    TROPHY = "TROPHY"  # Trophy
    TOWEL = "TOWEL"  # Towel


class UniformTeam(str, Enum):
    """Sport team"""

    CHINA_NATIONAL = "CHINA_NATIONAL"  # China National Team (red)
    CHINA_NATIONAL_BLUE = "CHINA_NATIONAL_BLUE"  # China Team (blue away)
    CHINA_NATIONAL_WHITE = "CHINA_NATIONAL_WHITE"  # China Team (white ceremony)
    CLUB_SHENZHEN = "CLUB_SHENZHEN"  # Shenzhen Club
    CLUB_CUSTOM = "CLUB_CUSTOM"  # Custom club
    TRAINING = "TRAINING"  # Training uniform


class UniformStyle(str, Enum):
    """Sportswear type"""

    MATCH_JERSEY = "MATCH_JERSEY"  # Match jersey
    TRAINING_WEAR = "TRAINING_WEAR"  # Training wear
    AWARD_CEREMONY = "AWARD_CEREMONY"  # Award ceremony outfit
    WARMUP_JACKET = "WARMUP_JACKET"  # Warmup jacket


class SportPose(str, Enum):
    """Sport pose"""

    READY_STANCE = "READY_STANCE"  # Ready stance
    FOREHAND_ATTACK = "FOREHAND_ATTACK"  # Forehand attack
    BACKHAND_ATTACK = "BACKHAND_ATTACK"  # Backhand loop
    SERVE_TOSS = "SERVE_TOSS"  # Serve toss
    SERVE_HIT = "SERVE_HIT"  # Serve hit
    FOREHAND_LOOP = "FOREHAND_LOOP"  # Forehand loop drive
    CELEBRATE = "CELEBRATE"  # Celebration
    FIST_PUMP = "FIST_PUMP"  # Fist pump celebration
    HOLD_MEDAL = "HOLD_MEDAL"  # Holding medal
    RECEIVING_AWARD = "RECEIVING_AWARD"  # Receiving award
    T_POSE = "T_POSE"  # T-Pose (for modeling/rigging)
    A_POSE = "A_POSE"  # A-Pose (for modeling/rigging)


class ReferenceView(str, Enum):
    """Reference image view"""

    FRONT = "FRONT"
    SIDE = "SIDE"
    BACK = "BACK"
    THREE_QUARTER = "THREE_QUARTER"


class SceneType(str, Enum):
    """Scene type"""

    MATCH = "MATCH"  # Match scene
    TRAINING = "TRAINING"  # Training scene
    AWARD_CEREMONY = "AWARD_CEREMONY"  # Award ceremony scene
    PORTRAIT = "PORTRAIT"  # Portrait/display scene
    PRODUCT = "PRODUCT"  # Product display (figurine style)


class OptimizeTarget(str, Enum):
    """Optimization target platform"""

    WEB = "WEB"  # Web (3000-4500 tris)
    MOBILE = "MOBILE"  # Mobile (5000-8000 tris)
    PC_CONSOLE = "PC_CONSOLE"  # PC/Console (10000-20000 tris)
    PRINT_3D = "PRINT_3D"  # 3D printing (high detail)


# ==================== Input Models ====================


class SportCharacterCreateInput(BaseModel):
    """Create sport character input"""

    name: str = Field(default="Athlete", description="Character name")
    sport: SportType = Field(default=SportType.TABLE_TENNIS, description="Sport type")
    style: CharacterStyle = Field(
        default=CharacterStyle.CHIBI,
        description="Character style: CHIBI (chibi 2.5:1), ANIME (anime 5:1), STYLIZED (stylized 4:1), REALISTIC (realistic 7:1)",
    )
    preset: AthletePreset = Field(
        default=AthletePreset.FAN_ZHENDONG, description="Athlete preset: FAN_ZHENDONG, CUSTOM"
    )
    height: float = Field(
        default=1.0,
        description="Character overall height (meters), chibi recommended 0.8-1.2",
        ge=0.3,
        le=3.0,
    )
    head_body_ratio: float | None = Field(
        default=None,
        description="Head-body ratio override, uses style default if empty. Chibi 2.0-2.5, anime 5-6, realistic 7-8",
    )
    skin_color: list[float] | None = Field(
        default=None, description="Skin color [r, g, b, a], uses preset default if empty"
    )
    build: str = Field(default="athletic", description="Build: slim, athletic, muscular, stocky")
    create_armature: bool = Field(default=True, description="Whether to create skeleton system")
    face_count_budget: int = Field(
        default=4500,
        description="Face count budget (triangles), Web: 3000-4500, PC: 5000-20000",
        ge=1000,
        le=50000,
    )


class SportEquipmentAddInput(BaseModel):
    """Add sport equipment input"""

    character_name: str = Field(..., description="Character name")
    equipment_type: EquipmentType = Field(..., description="Equipment type")
    attach_to: str = Field(
        default="auto",
        description="Attach position: auto, right_hand, left_hand, neck, head, waist",
    )
    color: list[float] | None = Field(default=None, description="Equipment primary color [r, g, b]")
    secondary_color: list[float] | None = Field(
        default=None, description="Equipment secondary color [r, g, b]"
    )
    scale: float = Field(default=1.0, description="Equipment scale", ge=0.1, le=3.0)


class SportUniformCreateInput(BaseModel):
    """Create sportswear input"""

    character_name: str = Field(..., description="Character name")
    team: UniformTeam = Field(default=UniformTeam.CHINA_NATIONAL, description="Team")
    uniform_style: UniformStyle = Field(
        default=UniformStyle.MATCH_JERSEY, description="Sportswear type"
    )
    jersey_number: int = Field(
        default=20, description="Jersey number (Fan Zhendong is #20)", ge=0, le=99
    )
    player_name: str = Field(default="FAN ZHENDONG", description="Name on jersey back")
    brand: str = Field(
        default="Li-Ning", description="Brand: Li-Ning, Nike, Adidas, Butterfly, Custom"
    )
    custom_primary_color: list[float] | None = Field(
        default=None, description="Custom primary color [r, g, b], only for CLUB_CUSTOM"
    )
    custom_secondary_color: list[float] | None = Field(
        default=None, description="Custom secondary color [r, g, b], only for CLUB_CUSTOM"
    )


class SportPoseSetInput(BaseModel):
    """Set sport pose input"""

    character_name: str = Field(..., description="Character name")
    pose: SportPose = Field(default=SportPose.READY_STANCE, description="Sport pose")
    intensity: float = Field(
        default=1.0,
        description="Pose intensity/exaggeration, chibi recommended 1.2-1.5",
        ge=0.1,
        le=2.0,
    )
    mirror: bool = Field(default=False, description="Whether to mirror (left-hand paddle)")
    add_motion_trail: bool = Field(default=False, description="Whether to add motion trail effect")


class SportReferenceLoadInput(BaseModel):
    """Load reference image input"""

    image_path: str = Field(..., description="Reference image file path")
    view: ReferenceView = Field(
        default=ReferenceView.FRONT, description="View: FRONT, SIDE, BACK, THREE_QUARTER"
    )
    opacity: float = Field(default=0.5, description="Opacity", ge=0.1, le=1.0)
    offset_x: float = Field(default=0.0, description="X offset")
    offset_y: float = Field(default=0.0, description="Y offset")
    scale: float = Field(default=1.0, description="Reference image scale", ge=0.1, le=10.0)


class SportModelOptimizeInput(BaseModel):
    """Sport model optimization input"""

    character_name: str = Field(..., description="Character name")
    target: OptimizeTarget = Field(
        default=OptimizeTarget.WEB, description="Optimization target platform"
    )
    target_tris: int | None = Field(
        default=None, description="Target triangle count, uses platform default if empty"
    )
    texture_size: int = Field(default=1024, description="Texture size", ge=256, le=4096)
    generate_lod: bool = Field(default=False, description="Whether to generate LOD levels")
    lod_levels: int = Field(default=3, description="LOD level count", ge=2, le=5)
    export_glb: bool = Field(default=True, description="Whether to also export GLB file")
    export_path: str | None = Field(
        default=None, description="Export path, uses current blend file directory if empty"
    )
    apply_draco_compression: bool = Field(
        default=True, description="Whether to apply Draco compression (GLB)"
    )


class SportSceneSetupInput(BaseModel):
    """Sport scene setup input"""

    scene_type: SceneType = Field(default=SceneType.PORTRAIT, description="Scene type")
    character_name: str | None = Field(default=None, description="Character name to place in scene")
    background_color: list[float] | None = Field(
        default=None, description="Background color [r, g, b]"
    )
    use_hdri: bool = Field(default=False, description="Whether to use HDRI environment lighting")
    camera_distance: float = Field(default=3.0, description="Camera distance", ge=1.0, le=20.0)
    render_engine: str = Field(default="EEVEE", description="Render engine: EEVEE, CYCLES")


# ==================== Tool Registration ====================


def register_sport_character_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register sport character tools"""

    @mcp.tool(
        name="blender_sport_character_create",
        annotations={
            "title": "Create Sport Character",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_sport_character_create(params: SportCharacterCreateInput) -> str:
        """Create an athlete character (supports chibi/realistic/anime styles).

        Creates a complete athlete character model based on sport type and style:
        - Chibi (CHIBI): Pop Mart style, head-body ratio 2:1~2.5:1, round face with big eyes, suitable for web display
        - Anime (ANIME): Japanese anime style, head-body ratio 5:1~6:1
        - Stylized (STYLIZED): Game stylized, head-body ratio 4:1
        - Realistic (REALISTIC): Realistic proportions, head-body ratio 7:1~8:1

        Built-in athlete presets:
        - FAN_ZHENDONG: Fan Zhendong - China national team star, 172cm tall, athletic build,
          round face, short black hair, thick eyebrows, big eyes, confident expression

        Modeling workflow follows best practices:
        - Base sphere -> sculpt -> decimate -> UV -> color block materials -> Rigify rig
        - Face count budget control: Web 3000-4500, PC 5000-20000
        - Auto-create vertex groups for clothing binding

        Args:
            params: Character name, sport type, style, build, face count budget, etc.

        Returns:
            Creation result with list of created parts
        """
        result = await server.execute_command(
            "sport_character",
            "create_character",
            {
                "name": params.name,
                "sport": params.sport.value,
                "style": params.style.value,
                "preset": params.preset.value,
                "height": params.height,
                "head_body_ratio": params.head_body_ratio,
                "skin_color": params.skin_color,
                "build": params.build,
                "create_armature": params.create_armature,
                "face_count_budget": params.face_count_budget,
            },
        )

        style_names = {
            "CHIBI": "chibi",
            "ANIME": "anime",
            "STYLIZED": "stylized",
            "REALISTIC": "realistic",
        }
        sport_names = {
            "TABLE_TENNIS": "table tennis",
            "BASKETBALL": "basketball",
            "SOCCER": "soccer",
            "BADMINTON": "badminton",
            "TENNIS": "tennis",
            "VOLLEYBALL": "volleyball",
        }
        preset_names = {"FAN_ZHENDONG": "Fan Zhendong", "CUSTOM": "custom"}

        if result.get("success"):
            data = result.get("data", {})
            parts = data.get("created_parts", [])
            style_name = style_names.get(params.style.value, params.style.value)
            sport_name = sport_names.get(params.sport.value, params.sport.value)
            preset_name = preset_names.get(params.preset.value, "")
            preset_info = (
                f" ({preset_name} preset)" if params.preset != AthletePreset.CUSTOM else ""
            )
            armature_info = "with skeleton" if data.get("has_armature") else "no skeleton"
            return (
                f"Successfully created {style_name} {sport_name} athlete '{params.name}'{preset_info}\n"
                f"Height: {params.height}m, head-body ratio: {data.get('head_body_ratio', 'N/A')}:1, "
                f"build: {params.build}, {armature_info}\n"
                f"Created parts: {', '.join(parts)}\n"
                f"Face count budget: {params.face_count_budget} tris"
            )
        else:
            return f"Failed to create sport character: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_equipment_add",
        annotations={
            "title": "Add Sport Equipment",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_sport_equipment_add(params: SportEquipmentAddInput) -> str:
        """Add sport equipment to a sport character.

        Supported equipment types:
        - Table tennis: PADDLE (paddle), BALL (ball), TABLE (table), NET (net)
        - Medals: MEDAL_GOLD (gold medal), MEDAL_SILVER (silver medal), MEDAL_BRONZE (bronze medal)
        - Accessories: WRISTBAND (wristband), HEADBAND (headband), TROPHY (trophy), TOWEL (towel)

        Paddle auto-adapts to chibi/realistic proportions, defaults to character's right hand.
        Medals default to neck position.

        Args:
            params: Character name, equipment type, attach position, color, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "sport_character",
            "add_equipment",
            {
                "character_name": params.character_name,
                "equipment_type": params.equipment_type.value,
                "attach_to": params.attach_to,
                "color": params.color,
                "secondary_color": params.secondary_color,
                "scale": params.scale,
            },
        )

        equip_names = {
            "PADDLE": "paddle",
            "BALL": "ball",
            "TABLE": "table",
            "NET": "net",
            "WRISTBAND": "wristband",
            "HEADBAND": "headband",
            "MEDAL_GOLD": "gold medal",
            "MEDAL_SILVER": "silver medal",
            "MEDAL_BRONZE": "bronze medal",
            "TROPHY": "trophy",
            "TOWEL": "towel",
        }

        if result.get("success"):
            data = result.get("data", {})
            equip_name = equip_names.get(params.equipment_type.value, params.equipment_type.value)
            attach_info = data.get("attached_to", params.attach_to)
            return f"Added {equip_name} to '{params.character_name}' (position: {attach_info})"
        else:
            return f"Failed to add equipment: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_uniform_create",
        annotations={
            "title": "Create Sportswear",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_sport_uniform_create(params: SportUniformCreateInput) -> str:
        """Create sportswear for a sport character.

        Built-in team color schemes:
        - CHINA_NATIONAL: China National Team red (match home)
        - CHINA_NATIONAL_BLUE: China Team blue (match away)
        - CHINA_NATIONAL_WHITE: China Team white (ceremony outfit/jacket)
        - CLUB_SHENZHEN: Shenzhen Club
        - TRAINING: Training uniform

        Sportswear types:
        - MATCH_JERSEY: Match jersey (with number and name)
        - TRAINING_WEAR: Training wear
        - AWARD_CEREMONY: Award ceremony outfit (white base with red stripes)
        - WARMUP_JACKET: Warmup jacket

        Fan Zhendong default jersey number: 20
        Brand: Li-Ning

        Args:
            params: Character name, team, jersey type, number, name, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "sport_character",
            "create_uniform",
            {
                "character_name": params.character_name,
                "team": params.team.value,
                "uniform_style": params.uniform_style.value,
                "jersey_number": params.jersey_number,
                "player_name": params.player_name,
                "brand": params.brand,
                "custom_primary_color": params.custom_primary_color,
                "custom_secondary_color": params.custom_secondary_color,
            },
        )

        team_names = {
            "CHINA_NATIONAL": "China National Team (red)",
            "CHINA_NATIONAL_BLUE": "China Team (blue)",
            "CHINA_NATIONAL_WHITE": "China Team (white)",
            "CLUB_SHENZHEN": "Shenzhen Club",
            "CLUB_CUSTOM": "Custom Club",
            "TRAINING": "Training",
        }
        style_names = {
            "MATCH_JERSEY": "match jersey",
            "TRAINING_WEAR": "training wear",
            "AWARD_CEREMONY": "ceremony outfit",
            "WARMUP_JACKET": "warmup jacket",
        }

        if result.get("success"):
            result.get("data", {})
            team_name = team_names.get(params.team.value, params.team.value)
            style_name = style_names.get(params.uniform_style.value, params.uniform_style.value)
            return (
                f"Created {team_name} {style_name} for '{params.character_name}'\n"
                f"Number: {params.jersey_number}, Name: {params.player_name}, Brand: {params.brand}"
            )
        else:
            return f"Failed to create sportswear: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_pose_set",
        annotations={
            "title": "Set Sport Pose",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_sport_pose_set(params: SportPoseSetInput) -> str:
        """Set a sport pose for the sport character.

        Table tennis-specific poses:
        - READY_STANCE: Ready to receive stance (slight crouch, paddle forward)
        - FOREHAND_ATTACK: Forehand attack (side stance, loaded swing)
        - BACKHAND_ATTACK: Backhand loop (fast backhand arc)
        - SERVE_TOSS: Serve toss (palm up, ball tossed upward)
        - SERVE_HIT: Serve hit (moment of ball contact)
        - FOREHAND_LOOP: Forehand loop drive (full power arc)

        General celebration poses:
        - CELEBRATE: Arms raised celebration
        - FIST_PUMP: Fist pump with shout (Fan Zhendong's signature move)
        - HOLD_MEDAL: Holding up medal with both hands
        - RECEIVING_AWARD: Standing on podium

        Modeling helper poses:
        - T_POSE: Standard T-Pose
        - A_POSE: Standard A-Pose

        Chibi characters recommended intensity 1.2-1.5 for added cuteness.

        Args:
            params: Character name, pose type, intensity, whether to mirror

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "sport_character",
            "set_pose",
            {
                "character_name": params.character_name,
                "pose": params.pose.value,
                "intensity": params.intensity,
                "mirror": params.mirror,
                "add_motion_trail": params.add_motion_trail,
            },
        )

        pose_names = {
            "READY_STANCE": "ready stance",
            "FOREHAND_ATTACK": "forehand attack",
            "BACKHAND_ATTACK": "backhand loop",
            "SERVE_TOSS": "serve toss",
            "SERVE_HIT": "serve hit",
            "FOREHAND_LOOP": "forehand loop drive",
            "CELEBRATE": "celebration",
            "FIST_PUMP": "fist pump",
            "HOLD_MEDAL": "holding medal",
            "RECEIVING_AWARD": "receiving award",
            "T_POSE": "T-Pose",
            "A_POSE": "A-Pose",
        }

        if result.get("success"):
            data = result.get("data", {})
            pose_name = pose_names.get(params.pose.value, params.pose.value)
            mirror_info = " (left-hand mirror)" if params.mirror else ""
            trail_info = " + motion trail" if data.get("has_motion_trail") else ""
            return f"Set {pose_name}{mirror_info} for '{params.character_name}' (intensity: {params.intensity:.0%}){trail_info}"
        else:
            return f"Failed to set pose: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_reference_load",
        annotations={
            "title": "Load Sport Reference Image",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_sport_reference_load(params: SportReferenceLoadInput) -> str:
        """Load a reference image in the viewport for modeling reference.

        Supports loading front, side, back, and 3/4 view reference images.
        Reference images are added to the scene as Empty Image objects,
        with adjustable opacity, position, and scale.

        Use cases:
        - Load real photos of Fan Zhendong as modeling reference
        - Load chibi illustrations as style reference
        - Load match action screenshots as pose reference

        Supported formats: PNG, JPG, JPEG, WEBP, BMP, AVIF

        Args:
            params: Image path, view, opacity, etc.

        Returns:
            Operation result
        """
        result = await server.execute_command(
            "sport_character",
            "load_reference",
            {
                "image_path": params.image_path,
                "view": params.view.value,
                "opacity": params.opacity,
                "offset_x": params.offset_x,
                "offset_y": params.offset_y,
                "scale": params.scale,
            },
        )

        view_names = {"FRONT": "front", "SIDE": "side", "BACK": "back", "THREE_QUARTER": "3/4 view"}

        if result.get("success"):
            data = result.get("data", {})
            view_name = view_names.get(params.view.value, params.view.value)
            return f"Loaded {view_name} reference image: {data.get('image_name', params.image_path)} (opacity: {params.opacity:.0%})"
        else:
            return f"Failed to load reference image: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_model_optimize",
        annotations={
            "title": "Sport Model Web Optimization",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_sport_model_optimize(params: SportModelOptimizeInput) -> str:
        """Optimize sport character model for different platforms.

        Platform preset triangle counts:
        - WEB: 3000-4500 tris (Three.js/WebGL)
        - MOBILE: 5000-8000 tris
        - PC_CONSOLE: 10000-20000 tris
        - PRINT_3D: High detail, unlimited triangles

        Optimization workflow:
        1. Apply Decimate modifier to reduce to target face count
        2. Clean up isolated vertices and overlapping faces
        3. Optimize UV layout
        4. Bake materials to textures (optional)
        5. Generate LOD levels (optional)
        6. Export GLB format (optional, with Draco compression)

        Follows game asset optimization best practices.

        Args:
            params: Character name, target platform, face count, texture size, etc.

        Returns:
            Optimization result with final face count and export path
        """
        result = await server.execute_command(
            "sport_character",
            "optimize_model",
            {
                "character_name": params.character_name,
                "target": params.target.value,
                "target_tris": params.target_tris,
                "texture_size": params.texture_size,
                "generate_lod": params.generate_lod,
                "lod_levels": params.lod_levels,
                "export_glb": params.export_glb,
                "export_path": params.export_path,
                "apply_draco_compression": params.apply_draco_compression,
            },
        )

        target_names = {
            "WEB": "Web",
            "MOBILE": "Mobile",
            "PC_CONSOLE": "PC/Console",
            "PRINT_3D": "3D Print",
        }

        if result.get("success"):
            data = result.get("data", {})
            target_name = target_names.get(params.target.value, params.target.value)
            original_tris = data.get("original_tris", "N/A")
            final_tris = data.get("final_tris", "N/A")
            export_info = (
                f"\nExport path: {data.get('export_path')}" if data.get("export_path") else ""
            )
            lod_info = f"\nLOD levels: {data.get('lod_count', 0)}" if data.get("lod_count") else ""
            return (
                f"Optimized '{params.character_name}' to {target_name} standard\n"
                f"Triangles: {original_tris} -> {final_tris} tris\n"
                f"Texture size: {params.texture_size}px{lod_info}{export_info}"
            )
        else:
            return f"Failed to optimize model: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_sport_scene_setup",
        annotations={
            "title": "Setup Sport Scene",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_sport_scene_setup(params: SportSceneSetupInput) -> str:
        """Set up a sport-themed scene.

        Scene types:
        - MATCH: Match scene (table, lights, audience hint)
        - TRAINING: Training scene (simple indoor, training equipment)
        - AWARD_CEREMONY: Award ceremony scene (podium, backdrop)
        - PORTRAIT: Portrait display (simple background, three-point lighting)
        - PRODUCT: Product display/figurine style (base, display lighting)

        Lighting follows best practices:
        - Low ambient + strong directional light + contrasting backlight
        - EEVEE: Filmic color management, soft shadows, Bloom
        - Three-point lighting: key (warm) + fill (cool) + rim

        Args:
            params: Scene type, character name, background color, camera settings, etc.

        Returns:
            Scene setup result
        """
        result = await server.execute_command(
            "sport_character",
            "setup_scene",
            {
                "scene_type": params.scene_type.value,
                "character_name": params.character_name,
                "background_color": params.background_color,
                "use_hdri": params.use_hdri,
                "camera_distance": params.camera_distance,
                "render_engine": params.render_engine,
            },
        )

        scene_names = {
            "MATCH": "match scene",
            "TRAINING": "training scene",
            "AWARD_CEREMONY": "award ceremony scene",
            "PORTRAIT": "portrait display",
            "PRODUCT": "product display",
        }

        if result.get("success"):
            data = result.get("data", {})
            scene_name = scene_names.get(params.scene_type.value, params.scene_type.value)
            lights_info = f"Lights: {data.get('lights_count', 0)}"
            return (
                f"Set up {scene_name}\n"
                f"Render engine: {params.render_engine}, {lights_info}\n"
                f"Camera distance: {params.camera_distance}m"
            )
        else:
            return (
                f"Failed to set up scene: {result.get('error', {}).get('message', 'Unknown error')}"
            )
