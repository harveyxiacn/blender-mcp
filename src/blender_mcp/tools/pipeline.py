"""Automation pipeline tools for end-to-end model production workflows."""

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class PipelineStyle(str, Enum):
    PIXEL = "PIXEL"
    LOW_POLY = "LOW_POLY"
    STYLIZED = "STYLIZED"
    TOON = "TOON"
    HAND_PAINTED = "HAND_PAINTED"
    SEMI_REALISTIC = "SEMI_REALISTIC"
    PBR_REALISTIC = "PBR_REALISTIC"
    AAA = "AAA"


class CharacterTemplate(str, Enum):
    CHIBI = "chibi"
    REALISTIC = "realistic"
    ANIME = "anime"
    STYLIZED = "stylized"
    MASCOT = "mascot"


class QualityTarget(str, Enum):
    DRAFT = "draft"
    PRODUCTION = "production"
    HERO = "hero"


class CharacterPipelineInput(BaseModel):
    name: str = Field(..., description="角色名称")
    template: CharacterTemplate = Field(default=CharacterTemplate.CHIBI, description="模板类型")
    style: PipelineStyle = Field(default=PipelineStyle.TOON, description="目标风格")
    height: float = Field(default=1.7, ge=0.5, le=3.0, description="角色身高")
    location: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="角色位置 [x, y, z]")
    with_hair: bool = Field(default=True, description="自动创建头发")
    hair_style: str = Field(default="short", description="头发风格")
    with_clothing: bool = Field(default=True, description="自动添加服装")
    clothing_type: str = Field(default="sportswear", description="服装类型")
    with_accessory: bool = Field(default=True, description="自动添加配饰")
    accessory_type: str = Field(default="medal", description="配饰类型")
    auto_rig: bool = Field(default=True, description="是否自动绑定")
    rig_type: str = Field(default="simple", description="绑定类型")


class PropPipelineInput(BaseModel):
    name: str = Field(..., description="道具名称")
    primitive: str = Field(default="CUBE", description="基础图元类型")
    style: PipelineStyle = Field(default=PipelineStyle.LOW_POLY, description="目标风格")
    quality_target: QualityTarget = Field(default=QualityTarget.PRODUCTION, description="质量档位")
    location: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="位置 [x, y, z]")
    scale: list[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0], description="缩放 [x, y, z]")
    material_preset: Optional[str] = Field(default=None, description="程序化材质预设（为空则自动按风格选择）")
    auto_uv: bool = Field(default=True, description="自动UV展开")
    add_outline: bool = Field(default=False, description="是否添加描边（卡通风格推荐）")


class ScenePipelineInput(BaseModel):
    style: PipelineStyle = Field(default=PipelineStyle.SEMI_REALISTIC, description="场景目标风格")
    environment_preset: Optional[str] = Field(default=None, description="环境预设（为空则按风格自动选择）")
    create_ground: bool = Field(default=True, description="创建地面")
    ground_size: float = Field(default=30.0, ge=1.0, le=500.0, description="地面尺寸")
    ground_material: str = Field(default="concrete", description="地面材质预设")
    create_camera: bool = Field(default=True, description="自动创建并激活相机")
    camera_location: list[float] = Field(default_factory=lambda: [7.0, -7.0, 5.0], description="相机位置")
    resolution_x: int = Field(default=1920, ge=256, le=8192)
    resolution_y: int = Field(default=1080, ge=256, le=8192)
    samples: int = Field(default=128, ge=1, le=8192)


def _material_for_style(style: PipelineStyle) -> str:
    if style in {PipelineStyle.PIXEL, PipelineStyle.LOW_POLY}:
        return "TOON_BASIC"
    if style in {PipelineStyle.STYLIZED, PipelineStyle.TOON, PipelineStyle.HAND_PAINTED}:
        return "GENSHIN_STYLE"
    if style in {PipelineStyle.PBR_REALISTIC, PipelineStyle.AAA}:
        return "STEEL"
    return "CONCRETE"


def _environment_for_style(style: PipelineStyle) -> str:
    mapping = {
        PipelineStyle.PIXEL: "studio",
        PipelineStyle.LOW_POLY: "studio",
        PipelineStyle.STYLIZED: "forest",
        PipelineStyle.TOON: "studio",
        PipelineStyle.HAND_PAINTED: "outdoor_day",
        PipelineStyle.SEMI_REALISTIC: "outdoor_day",
        PipelineStyle.PBR_REALISTIC: "outdoor_day",
        PipelineStyle.AAA: "stadium",
    }
    return mapping[style]


def _engine_for_style(style: PipelineStyle) -> str:
    if style in {PipelineStyle.PBR_REALISTIC, PipelineStyle.AAA}:
        return "CYCLES"
    return "BLENDER_EEVEE_NEXT"


def _mesh_params_for_quality(primitive: str, quality: QualityTarget) -> dict[str, Any]:
    quality_map = {
        QualityTarget.DRAFT: {"segments": 8, "ring_count": 6, "vertices": 8, "subdivisions": 1},
        QualityTarget.PRODUCTION: {"segments": 24, "ring_count": 16, "vertices": 16, "subdivisions": 2},
        QualityTarget.HERO: {"segments": 48, "ring_count": 24, "vertices": 32, "subdivisions": 3},
    }
    cfg = quality_map[quality]
    prim = primitive.upper()
    if prim in {"SPHERE", "UV_SPHERE"}:
        return {"segments": cfg["segments"], "ring_count": cfg["ring_count"], "radius": 1.0}
    if prim == "ICO_SPHERE":
        return {"subdivisions": cfg["subdivisions"], "radius": 1.0}
    if prim in {"CYLINDER", "CONE"}:
        return {"vertices": cfg["vertices"], "radius": 1.0, "depth": 2.0}
    if prim == "TORUS":
        return {"major_segments": cfg["segments"], "minor_segments": max(8, cfg["vertices"]), "major_radius": 1.0, "minor_radius": 0.25}
    return {"size": 2.0}


async def _run_step(
    server: "BlenderMCPServer",
    steps: list[dict[str, Any]],
    step_name: str,
    category: str,
    action: str,
    params: dict[str, Any],
    *,
    required: bool = True,
) -> tuple[bool, dict[str, Any]]:
    result = await server.execute_command(category, action, params)
    ok = bool(result.get("success"))
    steps.append(
        {
            "step": step_name,
            "category": category,
            "action": action,
            "ok": ok,
            "required": required,
            "error": result.get("error", {}).get("message") if not ok else None,
        }
    )
    return ok, result


def register_pipeline_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register workflow pipeline tools."""

    @mcp.tool(
        name="blender_pipeline_generate_character",
        annotations={
            "title": "自动角色流程",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_pipeline_generate_character(params: CharacterPipelineInput) -> dict[str, Any]:
        """一键执行角色创建流程（模板 -> 服装/配饰 -> 绑定 -> 风格设置）。"""
        steps: list[dict[str, Any]] = []

        ok, create_result = await _run_step(
            server,
            steps,
            "create_character_template",
            "character_template",
            "create",
            {
                "template": params.template.value,
                "name": params.name,
                "height": params.height,
                "location": params.location,
            },
            required=True,
        )
        if not ok:
            return {"success": False, "steps": steps}

        data = create_result.get("data", {})
        parts = data.get("parts", [])

        if params.with_hair:
            await _run_step(
                server,
                steps,
                "create_hair",
                "character_template",
                "hair_create",
                {
                    "character_name": params.name,
                    "hair_style": params.hair_style,
                },
                required=False,
            )

        if params.with_clothing:
            await _run_step(
                server,
                steps,
                "add_clothing",
                "character_template",
                "clothing_add",
                {
                    "character_name": params.name,
                    "clothing_type": params.clothing_type,
                },
                required=False,
            )

        if params.with_accessory:
            await _run_step(
                server,
                steps,
                "add_accessory",
                "character_template",
                "accessory_add",
                {
                    "character_name": params.name,
                    "accessory_type": params.accessory_type,
                },
                required=False,
            )

        if params.auto_rig:
            await _run_step(
                server,
                steps,
                "auto_rig_setup",
                "auto_rig",
                "setup",
                {
                    "character_name": params.name,
                    "rig_type": params.rig_type,
                    "auto_weight": True,
                },
                required=False,
            )

        await _run_step(
            server,
            steps,
            "apply_style",
            "style_presets",
            "setup",
            {
                "style": params.style.value,
                "apply_to_scene": False,
                "apply_to_objects": parts,
            },
            required=False,
        )

        return {
            "success": True,
            "character_name": params.name,
            "template": params.template.value,
            "style": params.style.value,
            "parts_created": len(parts),
            "parts": parts,
            "steps": steps,
        }

    @mcp.tool(
        name="blender_pipeline_generate_prop",
        annotations={
            "title": "自动道具流程",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_pipeline_generate_prop(params: PropPipelineInput) -> dict[str, Any]:
        """一键执行道具流程（建模 -> 材质 -> UV -> 风格）。"""
        steps: list[dict[str, Any]] = []
        mesh_params = _mesh_params_for_quality(params.primitive, params.quality_target)

        ok, _ = await _run_step(
            server,
            steps,
            "create_base_primitive",
            "object",
            "create",
            {
                "type": params.primitive.upper(),
                "name": params.name,
                "location": params.location,
                "scale": params.scale,
                "mesh_params": mesh_params,
            },
            required=True,
        )
        if not ok:
            return {"success": False, "steps": steps}

        await _run_step(
            server,
            steps,
            "apply_style",
            "style_presets",
            "setup",
            {
                "style": params.style.value,
                "apply_to_scene": False,
                "apply_to_objects": [params.name],
            },
            required=False,
        )

        material_preset = params.material_preset or _material_for_style(params.style)
        await _run_step(
            server,
            steps,
            "create_procedural_material",
            "procedural_materials",
            "create",
            {
                "preset": material_preset,
                "material_name": f"{params.name}_Mat",
                "object_name": params.name,
            },
            required=False,
        )

        if params.auto_uv:
            await _run_step(
                server,
                steps,
                "auto_uv_unwrap",
                "uv",
                "smart_project",
                {
                    "object_name": params.name,
                    "angle_limit": 66.0,
                    "island_margin": 0.02,
                },
                required=False,
            )

        if params.add_outline:
            await _run_step(
                server,
                steps,
                "add_outline",
                "style_presets",
                "outline",
                {
                    "object_name": params.name,
                    "method": "SOLIDIFY",
                    "thickness": 0.01,
                    "color": [0, 0, 0],
                },
                required=False,
            )

        return {
            "success": True,
            "object_name": params.name,
            "style": params.style.value,
            "quality_target": params.quality_target.value,
            "material_preset": material_preset,
            "steps": steps,
        }

    @mcp.tool(
        name="blender_pipeline_assemble_scene",
        annotations={
            "title": "自动场景流程",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_pipeline_assemble_scene(params: ScenePipelineInput) -> dict[str, Any]:
        """一键执行场景流程（风格 -> 环境 -> 地面 -> 灯光 -> 相机 -> 渲染设置）。"""
        steps: list[dict[str, Any]] = []
        env_preset = params.environment_preset or _environment_for_style(params.style)

        await _run_step(
            server,
            steps,
            "apply_scene_style",
            "style_presets",
            "setup",
            {
                "style": params.style.value,
                "apply_to_scene": True,
                "apply_to_objects": [],
            },
            required=False,
        )

        await _run_step(
            server,
            steps,
            "apply_environment_preset",
            "scene_advanced",
            "environment_preset",
            {"preset": env_preset, "intensity": 1.0},
            required=False,
        )

        if params.create_ground:
            await _run_step(
                server,
                steps,
                "create_ground_plane",
                "scene_advanced",
                "ground_plane",
                {
                    "size": params.ground_size,
                    "material_preset": params.ground_material,
                    "location": [0, 0, 0],
                },
                required=False,
            )

        if params.create_camera:
            cam_name = "Pipeline_Camera"
            await _run_step(
                server,
                steps,
                "create_camera",
                "camera",
                "create",
                {
                    "name": cam_name,
                    "location": params.camera_location,
                    "rotation": [1.1, 0, 0],
                },
                required=False,
            )
            await _run_step(
                server,
                steps,
                "camera_look_at_origin",
                "camera",
                "look_at",
                {"camera_name": cam_name, "target": [0, 0, 0], "use_constraint": False},
                required=False,
            )
            await _run_step(
                server,
                steps,
                "set_active_camera",
                "camera",
                "set_active",
                {"camera_name": cam_name, "name": cam_name},
                required=False,
            )

        await _run_step(
            server,
            steps,
            "create_key_light",
            "lighting",
            "create",
            {
                "type": "AREA",
                "name": "Pipeline_KeyLight",
                "location": [4, -4, 6],
                "energy": 1200.0,
                "color": [1.0, 0.98, 0.95],
            },
            required=False,
        )
        await _run_step(
            server,
            steps,
            "create_fill_light",
            "lighting",
            "create",
            {
                "type": "AREA",
                "name": "Pipeline_FillLight",
                "location": [-4, -2, 4],
                "energy": 450.0,
                "color": [0.85, 0.9, 1.0],
            },
            required=False,
        )

        await _run_step(
            server,
            steps,
            "set_render_engine",
            "render",
            "set_engine",
            {"engine": _engine_for_style(params.style)},
            required=False,
        )
        await _run_step(
            server,
            steps,
            "set_render_resolution",
            "render",
            "set_resolution",
            {"width": params.resolution_x, "height": params.resolution_y, "percentage": 100},
            required=False,
        )
        await _run_step(
            server,
            steps,
            "set_render_samples",
            "render",
            "set_samples",
            {"samples": params.samples},
            required=False,
        )

        return {
            "success": True,
            "style": params.style.value,
            "environment_preset": env_preset,
            "render": {
                "engine": _engine_for_style(params.style),
                "resolution": [params.resolution_x, params.resolution_y],
                "samples": params.samples,
            },
            "steps": steps,
        }
