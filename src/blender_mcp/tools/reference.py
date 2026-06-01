"""
Reference image tools for reference-driven modeling workflows.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
REFERENCE_MANIFEST_NAME = "reference_manifest.json"
ROLE_ORDER = [
    "front",
    "side",
    "back",
    "three_quarter",
    "face",
    "hair",
    "outfit",
    "weapon",
    "pose",
    "detail",
    "figure_front",
    "figure_side",
    "figure_back",
]
PRESET_RULES: dict[str, dict[str, list[str]]] = {
    "GENERIC": {
        "required": ["front", "side"],
        "optional": ["back", "three_quarter", "face", "detail"],
    },
    "ANIME": {
        "required": ["front", "side", "face"],
        "optional": ["back", "three_quarter", "hair", "outfit", "weapon", "pose"],
    },
    "SAO": {
        "required": ["front", "side", "face"],
        "optional": [
            "back",
            "three_quarter",
            "hair",
            "outfit",
            "weapon",
            "pose",
            "figure_front",
            "figure_side",
        ],
    },
}
REFERENCE_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "character_name": {"type": "string"},
        "style_family": {"type": "string"},
        "body": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "build": {"type": "string"},
                "head_body_ratio_estimate": {"type": "string"},
                "silhouette": {"type": "string"},
            },
            "required": ["build", "head_body_ratio_estimate", "silhouette"],
        },
        "face": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "face_shape": {"type": "string"},
                "eyes": {"type": "string"},
                "expression": {"type": "string"},
                "distinctive_features": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["face_shape", "eyes", "expression", "distinctive_features"],
        },
        "hair": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "color": {"type": "string"},
                "cut": {"type": "string"},
                "silhouette": {"type": "string"},
                "key_clumps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["color", "cut", "silhouette", "key_clumps"],
        },
        "outfit_layers": {"type": "array", "items": {"type": "string"}},
        "weapons": {"type": "array", "items": {"type": "string"}},
        "pose": {"type": "string"},
        "must_match_features": {"type": "array", "items": {"type": "string"}},
        "modeling_priorities": {"type": "array", "items": {"type": "string"}},
        "ambiguities": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "character_name",
        "style_family",
        "body",
        "face",
        "hair",
        "outfit_layers",
        "weapons",
        "pose",
        "must_match_features",
        "modeling_priorities",
        "ambiguities",
    ],
}
REFERENCE_AUDIT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "analysis_mode": {"type": "string"},
        "character_name": {"type": "string"},
        "overall_match": {"type": "string"},
        "match_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "category_scores": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "silhouette": {"type": "integer", "minimum": 0, "maximum": 100},
                "face": {"type": "integer", "minimum": 0, "maximum": 100},
                "hair": {"type": "integer", "minimum": 0, "maximum": 100},
                "outfit": {"type": "integer", "minimum": 0, "maximum": 100},
                "weapon": {"type": "integer", "minimum": 0, "maximum": 100},
                "pose": {"type": "integer", "minimum": 0, "maximum": 100},
                "materials": {"type": "integer", "minimum": 0, "maximum": 100},
            },
            "required": ["silhouette", "face", "hair", "outfit", "weapon", "pose", "materials"],
        },
        "strengths": {"type": "array", "items": {"type": "string"}},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "category": {"type": "string"},
                    "severity": {"type": "string"},
                    "observation": {"type": "string"},
                    "evidence": {"type": "string"},
                    "recommended_fix": {"type": "string"},
                },
                "required": ["category", "severity", "observation", "evidence", "recommended_fix"],
            },
        },
        "priority_actions": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "analysis_mode",
        "character_name",
        "overall_match",
        "match_score",
        "category_scores",
        "strengths",
        "issues",
        "priority_actions",
        "uncertainties",
    ],
}


class ReferenceView(str, Enum):
    """Supported reference view presets."""

    FRONT = "FRONT"
    SIDE = "SIDE"
    BACK = "BACK"
    THREE_QUARTER = "THREE_QUARTER"
    FACE = "FACE"
    DETAIL = "DETAIL"


class ReferencePreset(str, Enum):
    """Expected reference-pack structure presets."""

    GENERIC = "GENERIC"
    ANIME = "ANIME"
    SAO = "SAO"


class VisionProvider(str, Enum):
    """Optional provider for image-aware brief generation."""

    NONE = "none"
    OPENAI = "openai"


class ReferenceLoadImageInput(BaseModel):
    """Load a single reference image."""

    image_path: str = Field(..., description="Reference image file path")
    view: ReferenceView = Field(default=ReferenceView.FRONT, description="Reference view preset")
    name: str | None = Field(default=None, description="Optional object name override")
    collection_name: str = Field(
        default="References", description="Target collection name for reference objects"
    )
    opacity: float = Field(default=0.5, description="Image opacity", ge=0.05, le=1.0)
    scale: float = Field(default=1.0, description="Display scale", ge=0.05, le=20.0)
    offset_x: float = Field(default=0.0, description="X offset")
    offset_y: float = Field(default=0.0, description="Y offset")
    offset_z: float = Field(default=0.0, description="Z offset")
    hide_select: bool = Field(
        default=True, description="Prevent accidental selection while modeling"
    )


class ReferenceLoadSheetInput(BaseModel):
    """Load a small reference board for a single subject."""

    subject_name: str = Field(..., description="Subject name, used in object naming")
    front_image: str | None = Field(default=None, description="Front reference image path")
    side_image: str | None = Field(default=None, description="Side reference image path")
    back_image: str | None = Field(default=None, description="Back reference image path")
    face_image: str | None = Field(default=None, description="Face close-up image path")
    detail_images: list[str] | None = Field(
        default=None, description="Additional detail image paths"
    )
    collection_name: str | None = Field(
        default=None, description="Target collection name (defaults to References_<subject>)"
    )
    opacity: float = Field(default=0.5, description="Image opacity", ge=0.05, le=1.0)
    scale: float = Field(default=1.0, description="Display scale", ge=0.05, le=20.0)
    hide_select: bool = Field(
        default=True, description="Prevent accidental selection while modeling"
    )


class ReferencePackInspectInput(BaseModel):
    """Inspect a character-specific reference pack folder."""

    reference_dir: str = Field(..., description="Directory containing reference images")
    character_name: str = Field(..., description="Character name used to filter files")
    aliases: list[str] | None = Field(
        default=None,
        description="Optional filename aliases, e.g. ['kirito', '桐人']",
    )
    preset: ReferencePreset = Field(
        default=ReferencePreset.ANIME,
        description="Expected pack structure: GENERIC, ANIME, or SAO",
    )


class ReferencePackSetupInput(ReferencePackInspectInput):
    """Inspect and place a full reference board in Blender."""

    collection_name: str | None = Field(
        default=None,
        description="Target collection name (defaults to References_<character>)",
    )
    opacity: float = Field(default=0.55, description="Image opacity", ge=0.05, le=1.0)
    primary_scale: float = Field(
        default=1.6,
        description="Display scale for front/side/back/3-4 sheets",
        ge=0.05,
        le=20.0,
    )
    detail_scale: float = Field(
        default=0.95,
        description="Display scale for face/detail/pose/figure sheets",
        ge=0.05,
        le=20.0,
    )
    replace_existing: bool = Field(
        default=True,
        description="Replace existing reference objects in the target collection",
    )
    create_proportion_guides: bool = Field(
        default=True,
        description="Create height and head-ratio guide objects",
    )
    target_height: float = Field(
        default=1.7,
        description="Target character height in meters for the guides",
        ge=0.3,
        le=3.0,
    )
    head_body_ratio: float = Field(
        default=5.5,
        description="Target head-to-body ratio for the guides",
        ge=1.5,
        le=10.0,
    )
    origin: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 0.0],
        description="Board origin [x, y, z]",
    )
    hide_select: bool = Field(
        default=True, description="Prevent accidental selection while modeling"
    )


class ReferenceUpdateImageInput(BaseModel):
    """Update an existing reference image object."""

    object_name: str = Field(..., description="Reference object name")
    opacity: float | None = Field(default=None, description="New opacity", ge=0.05, le=1.0)
    scale: float | None = Field(default=None, description="New display scale", ge=0.05, le=20.0)
    hide_select: bool | None = Field(default=None, description="Whether object is selectable")
    hide_render: bool | None = Field(default=None, description="Whether object is hidden in renders")


class ReferenceClearInput(BaseModel):
    """Clear reference images."""

    collection_name: str | None = Field(
        default=None, description="Only clear objects from this collection"
    )
    name_prefix: str = Field(default="Ref_", description="Reference object name prefix")
    remove_collection_if_empty: bool = Field(
        default=True, description="Remove target collection after clearing its objects"
    )


class ReferenceBriefInput(ReferencePackInspectInput):
    """Generate a structured modeling brief from a reference pack."""

    franchise: str = Field(default="", description="Series or franchise name")
    target_style: str = Field(
        default="anime",
        description="Target output style, such as anime, stylized, toon, or semi-realistic",
    )
    notes: str = Field(default="", description="Extra user guidance or canon constraints")
    provider: VisionProvider = Field(
        default=VisionProvider.NONE,
        description="Vision provider for image-aware analysis; 'none' stays local only",
    )
    model: str = Field(
        default=DEFAULT_OPENAI_MODEL,
        description="Vision-capable model identifier used when provider=openai",
    )
    max_images: int = Field(
        default=6,
        description="Maximum number of reference images to send to the vision model",
        ge=1,
        le=10,
    )
    output_path: str | None = Field(default=None, description="Optional JSON output path")
    overwrite: bool = Field(default=False, description="Overwrite the JSON brief if it exists")


class ReferenceAuditInput(ReferencePackInspectInput):
    """Compare current model screenshots against a reference pack."""

    franchise: str = Field(default="", description="Series or franchise name")
    target_style: str = Field(
        default="anime",
        description="Target output style, such as anime, stylized, toon, or semi-realistic",
    )
    notes: str = Field(default="", description="Extra user guidance or canon constraints")
    provider: VisionProvider = Field(
        default=VisionProvider.NONE,
        description="Vision provider for image-aware comparison; 'none' produces a checklist only",
    )
    model: str = Field(
        default=DEFAULT_OPENAI_MODEL,
        description="Vision-capable model identifier used when provider=openai",
    )
    review_image_paths: list[str] | None = Field(
        default=None,
        description="Existing model screenshot paths to compare against the references",
    )
    capture_viewport: bool = Field(
        default=False,
        description="Capture the current Blender viewport and include it in the audit",
    )
    viewport_width: int = Field(default=1024, description="Viewport capture width", ge=64, le=3840)
    viewport_height: int = Field(
        default=768, description="Viewport capture height", ge=64, le=2160
    )
    capture_render_preview: bool = Field(
        default=True,
        description="Capture a quick render preview and include it in the audit",
    )
    render_width: int = Field(
        default=768, description="Render preview width in pixels", ge=64, le=1920
    )
    render_samples: int = Field(
        default=16, description="Render preview samples", ge=1, le=128
    )
    max_reference_images: int = Field(
        default=6,
        description="Maximum number of reference images to send to the vision model",
        ge=1,
        le=10,
    )
    max_review_images: int = Field(
        default=3,
        description="Maximum number of model review images to compare",
        ge=1,
        le=6,
    )
    output_path: str | None = Field(default=None, description="Optional JSON output path")
    overwrite: bool = Field(default=False, description="Overwrite the JSON audit if it exists")


def _normalize_name(value: str) -> str:
    return re.sub(r"[^\w]+", "_", value.casefold(), flags=re.UNICODE).strip("_")


def _resolve_reference_dir(reference_dir: str) -> Path:
    path = Path(reference_dir).expanduser()
    try:
        path = path.resolve()
    except OSError:
        path = path.absolute()

    if not path.exists():
        raise FileNotFoundError(f"Reference directory not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Reference path is not a directory: {path}")
    return path


def _candidate_aliases(character_name: str, aliases: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for value in [character_name, *(aliases or [])]:
        token = _normalize_name(value)
        if token and token not in normalized:
            normalized.append(token)
    return normalized


def _load_reference_manifest(reference_path: Path) -> dict[str, Any]:
    manifest_path = reference_path / REFERENCE_MANIFEST_NAME
    if not manifest_path.exists():
        return {}

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Reference manifest must be a JSON object: {manifest_path}")
    return payload


def _manifest_character_spec(
    manifest: dict[str, Any],
    *,
    character_name: str,
    aliases: list[str],
) -> dict[str, Any] | None:
    if not manifest:
        return None

    characters = manifest.get("characters", manifest)
    if not isinstance(characters, dict):
        return None

    alias_set = {token for token in aliases if token}
    alias_set.add(_normalize_name(character_name))

    for key, spec in characters.items():
        if not isinstance(spec, dict):
            continue
        spec_aliases = [_normalize_name(key)]
        spec_aliases.extend(_normalize_name(str(item)) for item in spec.get("aliases", []) if item)
        if alias_set.intersection(spec_aliases):
            return spec
    return None


def _collect_manifest_entries(
    reference_path: Path,
    *,
    manifest: dict[str, Any],
    character_name: str,
    aliases: list[str],
) -> list[dict[str, str]]:
    spec = _manifest_character_spec(manifest, character_name=character_name, aliases=aliases)
    if not spec:
        return []

    entries: list[dict[str, str]] = []
    for item in spec.get("entries", []):
        if not isinstance(item, dict):
            continue

        role = str(item.get("role", "")).strip()
        file_value = str(item.get("file") or item.get("name") or item.get("path") or "").strip()
        if not role or role not in ROLE_ORDER:
            continue
        if not file_value:
            continue

        path = Path(file_value).expanduser()
        if not path.is_absolute():
            path = reference_path / path
        try:
            path = path.resolve()
        except OSError:
            path = path.absolute()

        if not path.exists() or not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        entries.append({"role": role, "name": path.name, "path": str(path)})

    return entries


def _detect_role(stem: str, aliases: list[str]) -> str | None:
    for alias in aliases:
        if stem == alias:
            return "front"

        if stem.startswith(f"figure_{alias}_"):
            suffix = stem[len(f"figure_{alias}_") :]
            if suffix == "front":
                return "figure_front"
            if suffix in {"side", "profile"}:
                return "figure_side"
            if suffix == "back":
                return "figure_back"

        if not (stem == alias or stem.startswith(f"{alias}_")):
            continue

        suffix = stem[len(alias) :].strip("_")
        if suffix in {"front", "full_front", "正面"}:
            return "front"
        if suffix in {"side", "profile", "侧面"}:
            return "side"
        if suffix in {"back", "背面"}:
            return "back"
        if suffix in {"three_quarter", "threequarter", "threeq", "3q", "34", "四分之三"}:
            return "three_quarter"
        if suffix in {"face", "face_close", "face_closeup", "close_face", "bust", "面部特写", "脸部特写"}:
            return "face"
        if suffix.startswith("pose") or "动作" in suffix or "姿态" in suffix:
            return "pose"
        if "weapon" in suffix or suffix in {"逐暗者", "闪光", "武器", "细剑", "佩剑"}:
            return "weapon"
        if suffix.startswith("hair") or "发" in suffix:
            return "hair"
        if suffix.endswith("detail") or suffix.endswith("细节"):
            if any(
                marker in suffix
                for marker in (
                    "coat",
                    "outfit",
                    "armor",
                    "costume",
                    "uniform",
                    "dress",
                    "kob",
                    "服装",
                    "胸甲",
                    "肩甲",
                    "裙",
                )
            ):
                return "outfit"
            return "detail"

    return None


def inspect_reference_pack_data(
    reference_dir: str,
    character_name: str,
    aliases: list[str] | None = None,
    preset: str = ReferencePreset.ANIME.value,
) -> dict[str, Any]:
    """Inspect a reference pack folder and return structured coverage info."""

    reference_path = _resolve_reference_dir(reference_dir)
    alias_tokens = _candidate_aliases(character_name, aliases)
    if not alias_tokens:
        raise ValueError("At least one valid character alias is required.")

    preset_key = preset if preset in PRESET_RULES else ReferencePreset.GENERIC.value
    rules = PRESET_RULES[preset_key]
    manifest = _load_reference_manifest(reference_path)

    matched_files_by_path: dict[str, dict[str, str]] = {}

    for path in sorted(reference_path.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        role = _detect_role(_normalize_name(path.stem), alias_tokens)
        if role is None:
            continue

        matched_files_by_path[str(path)] = {"role": role, "name": path.name, "path": str(path)}

    for item in _collect_manifest_entries(
        reference_path,
        manifest=manifest,
        character_name=character_name,
        aliases=alias_tokens,
    ):
        matched_files_by_path[item["path"]] = item

    matched_files = list(matched_files_by_path.values())
    role_summary: dict[str, int] = {}
    for item in matched_files:
        role = item["role"]
        role_summary[role] = role_summary.get(role, 0) + 1

    missing_required = [role for role in rules["required"] if role not in role_summary]
    missing_optional = [role for role in rules["optional"] if role not in role_summary]

    if not matched_files:
        status = "no_matches"
    elif missing_required:
        status = "missing_required"
    elif missing_optional:
        status = "ready_with_gaps"
    else:
        status = "ready"

    matched_files.sort(
        key=lambda item: (
            ROLE_ORDER.index(item["role"]) if item["role"] in ROLE_ORDER else 999,
            item["name"],
        )
    )

    return {
        "character_name": character_name,
        "aliases": alias_tokens,
        "preset": preset_key,
        "reference_dir": str(reference_path),
        "manifest_used": bool(_manifest_character_spec(manifest, character_name=character_name, aliases=alias_tokens)),
        "status": status,
        "matched_files_count": len(matched_files),
        "matched_files": matched_files,
        "role_summary": role_summary,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
    }


def _pick_reference_images(report: dict[str, Any], max_images: int) -> list[dict[str, str]]:
    return report.get("matched_files", [])[:max_images]


def _heuristic_reference_brief(
    report: dict[str, Any],
    franchise: str,
    target_style: str,
    notes: str,
    selected_images: list[dict[str, str]],
) -> dict[str, Any]:
    roles = set(report.get("role_summary", {}).keys())
    must_match_features: list[str] = []
    modeling_priorities: list[str] = []
    ambiguities: list[str] = []

    if "face" in roles:
        must_match_features.append("Use the face close-up as the authority for eye shape, bangs, and brow spacing.")
        modeling_priorities.append("Lock face and head silhouette before costume micro-detail.")
    else:
        ambiguities.append("No face close-up was found, so facial proportions may drift.")

    if "hair" in roles:
        must_match_features.append("Preserve the major hair masses and parting from the dedicated hair reference.")
        modeling_priorities.append("Block hair clumps before adding loose strands.")

    if "outfit" in roles or "detail" in roles:
        must_match_features.append("Keep the outfit layering readable and avoid collapsing armor/coat/skirt volumes into one shell.")

    if "weapon" in roles:
        must_match_features.append("Match the weapon silhouette, guard shape, and grip proportions from the weapon detail image.")
        modeling_priorities.append("Model weapons as separate clean assets for posing and rendering.")

    if "pose" in roles:
        modeling_priorities.append("Apply the pose reference only after body proportions and weapon lengths are locked.")

    if "figure_front" in roles or "figure_side" in roles:
        must_match_features.append("Cross-check head-to-body ratio and silhouette thickness against the figure photos.")

    if not must_match_features:
        must_match_features.append("Match the front and side silhouette before chasing fine details.")
    if not modeling_priorities:
        modeling_priorities.append("Build from large silhouette to medium forms to surface detail.")

    return {
        "character_name": report["character_name"],
        "franchise": franchise,
        "target_style": target_style,
        "status": report["status"],
        "selected_images": [item["name"] for item in selected_images],
        "must_match_features": must_match_features,
        "modeling_priorities": modeling_priorities,
        "ambiguities": ambiguities,
        "notes": [notes] if notes else [],
        "vision_analysis": None,
    }


def _encode_image_as_data_url(path: str) -> str:
    mime_type = mimetypes.guess_type(path)[0] or "image/png"
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _extract_response_output_text(payload: dict[str, Any]) -> str:
    texts: list[str] = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))
    return "".join(texts).strip()


def _analyze_with_openai(
    report: dict[str, Any],
    franchise: str,
    target_style: str,
    notes: str,
    selected_images: list[dict[str, str]],
    model: str,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    content: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                "Analyze these anime/fan-art character references for Blender modeling. "
                "Focus on visible, stable design cues and call out uncertainty when references disagree."
            ),
        },
        {
            "type": "input_text",
            "text": (
                f"Character: {report['character_name']}\n"
                f"Franchise: {franchise or 'unknown'}\n"
                f"Target style: {target_style}\n"
                f"Notes: {notes or 'none'}"
            ),
        },
    ]

    for item in selected_images:
        content.append(
            {
                "type": "input_text",
                "text": f"Reference role: {item['role']} | file: {item['name']}",
            }
        )
        content.append({"type": "input_image", "image_url": _encode_image_as_data_url(item["path"])})

    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "input": [{"role": "user", "content": content}],
            "store": False,
            "temperature": 0.2,
            "max_output_tokens": 1200,
            "text": {
                "verbosity": "low",
                "format": {
                    "type": "json_schema",
                    "name": "reference_character_analysis",
                    "description": "Reference-driven character analysis for Blender modeling.",
                    "strict": True,
                    "schema": REFERENCE_ANALYSIS_SCHEMA,
                },
            },
        },
        timeout=90.0,
    )
    response.raise_for_status()

    output_text = _extract_response_output_text(response.json())
    if not output_text:
        raise RuntimeError("OpenAI vision response did not contain text output.")

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI vision response was not valid JSON.") from exc


def build_reference_brief(
    reference_dir: str,
    character_name: str,
    aliases: list[str] | None = None,
    preset: str = ReferencePreset.ANIME.value,
    franchise: str = "",
    target_style: str = "anime",
    notes: str = "",
    provider: str = VisionProvider.NONE.value,
    model: str = DEFAULT_OPENAI_MODEL,
    max_images: int = 6,
) -> dict[str, Any]:
    """Build a modeling brief from the reference pack."""

    report = inspect_reference_pack_data(reference_dir, character_name, aliases=aliases, preset=preset)
    selected_images = _pick_reference_images(report, max_images=max_images)
    brief = _heuristic_reference_brief(report, franchise, target_style, notes, selected_images)

    if provider == VisionProvider.OPENAI.value:
        brief["vision_analysis"] = _analyze_with_openai(
            report=report,
            franchise=franchise,
            target_style=target_style,
            notes=notes,
            selected_images=selected_images,
            model=model,
        )
        vision = brief["vision_analysis"]
        brief["must_match_features"] = vision.get("must_match_features", brief["must_match_features"])
        brief["modeling_priorities"] = vision.get("modeling_priorities", brief["modeling_priorities"])
        brief["ambiguities"] = vision.get("ambiguities", brief["ambiguities"])

    return brief


def _default_category_scores(value: int = 0) -> dict[str, int]:
    return {
        "silhouette": value,
        "face": value,
        "hair": value,
        "outfit": value,
        "weapon": value,
        "pose": value,
        "materials": value,
    }


def _resolve_image_path(path_value: str) -> str:
    path = Path(path_value).expanduser()
    try:
        path = path.resolve()
    except OSError:
        path = path.absolute()

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Image path is not a file: {path}")
    return str(path)


async def _collect_review_images(
    server: BlenderMCPServer,
    *,
    review_image_paths: list[str] | None,
    capture_viewport: bool,
    viewport_width: int,
    viewport_height: int,
    capture_render_preview: bool,
    render_width: int,
    render_samples: int,
) -> list[dict[str, str]]:
    collected: list[dict[str, str]] = []

    for index, path_value in enumerate(review_image_paths or []):
        resolved = _resolve_image_path(path_value)
        collected.append(
            {
                "label": f"provided_review_{index + 1}",
                "path": resolved,
                "name": Path(resolved).name,
                "source": "provided",
            }
        )

    if capture_viewport:
        result = await server.execute_command(
            "snapshot",
            "viewport",
            {"width": viewport_width, "height": viewport_height},
        )
        if not result.get("success"):
            raise RuntimeError(
                "Viewport snapshot failed: "
                f"{result.get('error', {}).get('message', 'Unknown error')}"
            )
        path_value = result.get("data", {}).get("path")
        if not path_value:
            raise RuntimeError("Viewport snapshot did not return a file path.")
        collected.append(
            {
                "label": "viewport_snapshot",
                "path": _resolve_image_path(path_value),
                "name": Path(path_value).name,
                "source": "snapshot_viewport",
            }
        )

    if capture_render_preview:
        result = await server.execute_command(
            "snapshot",
            "render_preview",
            {"width": render_width, "samples": render_samples},
        )
        if not result.get("success"):
            raise RuntimeError(
                "Render preview failed: "
                f"{result.get('error', {}).get('message', 'Unknown error')}"
            )
        path_value = result.get("data", {}).get("path")
        if not path_value:
            raise RuntimeError("Render preview did not return a file path.")
        collected.append(
            {
                "label": "render_preview",
                "path": _resolve_image_path(path_value),
                "name": Path(path_value).name,
                "source": "snapshot_render_preview",
            }
        )

    return collected


def _heuristic_reference_audit(
    report: dict[str, Any],
    brief: dict[str, Any],
    review_images: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "analysis_mode": "checklist",
        "character_name": report["character_name"],
        "overall_match": (
            "No image-aware comparison was run. This audit is a checklist scaffold based on the "
            "reference pack and available review images."
        ),
        "match_score": 0,
        "category_scores": _default_category_scores(0),
        "strengths": [
            "Reference pack was parsed successfully.",
            f"Collected {len(review_images)} review image(s) for manual or future multimodal comparison.",
        ],
        "issues": [
            {
                "category": "workflow",
                "severity": "medium",
                "observation": "Visual diff was not executed because provider=openai was not enabled.",
                "evidence": "The audit only has the reference brief and image inventory, not a multimodal comparison result.",
                "recommended_fix": "Re-run with provider=openai and OPENAI_API_KEY configured to get image-aware mismatch detection.",
            }
        ],
        "priority_actions": list(brief.get("modeling_priorities", []))[:5],
        "uncertainties": list(brief.get("ambiguities", []))[:5],
    }


def _analyze_audit_with_openai(
    report: dict[str, Any],
    brief: dict[str, Any],
    review_images: list[dict[str, str]],
    model: str,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    content: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                "Compare the current Blender model screenshots against the reference pack. "
                "Prioritize silhouette, proportions, face, hair, outfit layering, weapon shape, "
                "pose readability, and material readability. Avoid inventing unseen details and "
                "call out uncertainty when a review image does not show the relevant area."
            ),
        },
        {
            "type": "input_text",
            "text": (
                f"Character: {report['character_name']}\n"
                f"Reference status: {report.get('status', 'unknown')}\n"
                f"Must-match features: {'; '.join(brief.get('must_match_features', [])) or 'none'}\n"
                f"Modeling priorities: {'; '.join(brief.get('modeling_priorities', [])) or 'none'}\n"
                f"Known ambiguities: {'; '.join(brief.get('ambiguities', [])) or 'none'}"
            ),
        },
    ]

    for item in _pick_reference_images(report, max_images=6):
        content.append(
            {
                "type": "input_text",
                "text": f"Reference image | role: {item['role']} | file: {item['name']}",
            }
        )
        content.append({"type": "input_image", "image_url": _encode_image_as_data_url(item["path"])})

    for item in review_images:
        content.append(
            {
                "type": "input_text",
                "text": f"Current model review image | source: {item['source']} | file: {item['name']}",
            }
        )
        content.append({"type": "input_image", "image_url": _encode_image_as_data_url(item["path"])})

    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "input": [{"role": "user", "content": content}],
            "store": False,
            "temperature": 0.2,
            "max_output_tokens": 1600,
            "text": {
                "verbosity": "low",
                "format": {
                    "type": "json_schema",
                    "name": "reference_model_audit",
                    "description": "Reference-vs-model audit for Blender character iteration.",
                    "strict": True,
                    "schema": REFERENCE_AUDIT_SCHEMA,
                },
            },
        },
        timeout=90.0,
    )
    response.raise_for_status()

    output_text = _extract_response_output_text(response.json())
    if not output_text:
        raise RuntimeError("OpenAI audit response did not contain text output.")

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI audit response was not valid JSON.") from exc


async def build_reference_model_audit(
    server: BlenderMCPServer,
    *,
    reference_dir: str,
    character_name: str,
    aliases: list[str] | None = None,
    preset: str = ReferencePreset.ANIME.value,
    franchise: str = "",
    target_style: str = "anime",
    notes: str = "",
    provider: str = VisionProvider.NONE.value,
    model: str = DEFAULT_OPENAI_MODEL,
    review_image_paths: list[str] | None = None,
    capture_viewport: bool = False,
    viewport_width: int = 1024,
    viewport_height: int = 768,
    capture_render_preview: bool = True,
    render_width: int = 768,
    render_samples: int = 16,
    max_reference_images: int = 6,
    max_review_images: int = 3,
) -> dict[str, Any]:
    """Build a reference-vs-model audit payload."""

    report = inspect_reference_pack_data(reference_dir, character_name, aliases=aliases, preset=preset)
    review_images = await _collect_review_images(
        server,
        review_image_paths=review_image_paths,
        capture_viewport=capture_viewport,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        capture_render_preview=capture_render_preview,
        render_width=render_width,
        render_samples=render_samples,
    )
    if not review_images:
        raise RuntimeError("No review images were provided or captured for the audit.")

    review_images = review_images[:max_review_images]
    brief = build_reference_brief(
        reference_dir=reference_dir,
        character_name=character_name,
        aliases=aliases,
        preset=preset,
        franchise=franchise,
        target_style=target_style,
        notes=notes,
        provider=VisionProvider.NONE.value,
        max_images=max_reference_images,
    )

    if provider == VisionProvider.OPENAI.value:
        audit = _analyze_audit_with_openai(
            report=report,
            brief=brief,
            review_images=review_images,
            model=model,
        )
    else:
        audit = _heuristic_reference_audit(report, brief, review_images)

    audit["character_name"] = report["character_name"]
    audit["selected_review_images"] = [item["name"] for item in review_images]
    audit["selected_reference_images"] = [
        item["name"] for item in _pick_reference_images(report, max_images=max_reference_images)
    ]
    audit["reference_status"] = report.get("status", "unknown")
    return audit


def _format_brief_summary(brief: dict[str, Any], output_path: str | None = None) -> str:
    lines = [
        f"# Reference Brief: {brief['character_name']}",
        f"Style target: {brief['target_style']}",
        f"Reference status: {brief.get('status', 'unknown')}",
    ]
    if output_path:
        lines.append(f"Saved JSON: {output_path}")
    if brief.get("must_match_features"):
        lines.append("Must match:")
        lines.extend(f"- {item}" for item in brief["must_match_features"][:5])
    if brief.get("ambiguities"):
        lines.append("Ambiguities:")
        lines.extend(f"- {item}" for item in brief["ambiguities"][:5])
    return "\n".join(lines)


def _format_audit_summary(audit: dict[str, Any], output_path: str | None = None) -> str:
    lines = [
        f"# Reference Audit: {audit['character_name']}",
        f"Mode: {audit.get('analysis_mode', 'unknown')}",
        f"Reference status: {audit.get('reference_status', 'unknown')}",
        f"Match score: {audit.get('match_score', 'n/a')}",
        f"Overall: {audit.get('overall_match', 'n/a')}",
    ]
    if output_path:
        lines.append(f"Saved JSON: {output_path}")
    if audit.get("priority_actions"):
        lines.append("Priority actions:")
        lines.extend(f"- {item}" for item in audit["priority_actions"][:5])
    if audit.get("issues"):
        lines.append("Top issues:")
        for item in audit["issues"][:5]:
            lines.append(
                f"- [{item.get('severity', 'unknown')}] {item.get('category', 'general')}: {item.get('observation', '')}"
            )
    return "\n".join(lines)


def _write_json_file(payload: dict[str, Any], output_path: str, overwrite: bool) -> str:
    path = Path(output_path).expanduser()
    try:
        path = path.resolve()
    except OSError:
        path = path.absolute()

    if path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def register_reference_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    """Register reference image tools."""

    @mcp.tool(
        name="blender_reference_image_load",
        annotations={
            "title": "Load Reference Image",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_reference_image_load(params: ReferenceLoadImageInput) -> str:
        """Load one reference image into the viewport as an Empty image.

        This is the generic, non-sport-specific version of reference loading.
        Use it before character modeling to place front/side/back sheets,
        face closeups, or costume detail images in the scene.
        """
        result = await server.execute_command(
            "reference",
            "load_image",
            {
                "image_path": params.image_path,
                "view": params.view.value,
                "name": params.name,
                "collection_name": params.collection_name,
                "opacity": params.opacity,
                "scale": params.scale,
                "offset_x": params.offset_x,
                "offset_y": params.offset_y,
                "offset_z": params.offset_z,
                "hide_select": params.hide_select,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return (
                f"Loaded reference image '{data.get('image_name', params.image_path)}' as "
                f"{data.get('object_name', params.name or 'reference object')} "
                f"({params.view.value.lower()}, opacity {params.opacity:.0%})."
            )
        return f"Failed to load reference image: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_reference_sheet_load",
        annotations={
            "title": "Load Reference Sheet",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_reference_sheet_load(params: ReferenceLoadSheetInput) -> str:
        """Load a small multi-view reference board for a character or prop.

        The tool accepts front/side/back/face images plus optional detail images
        and places them into a dedicated collection for reference-driven modeling.
        """
        result = await server.execute_command(
            "reference",
            "load_sheet",
            {
                "subject_name": params.subject_name,
                "front_image": params.front_image,
                "side_image": params.side_image,
                "back_image": params.back_image,
                "face_image": params.face_image,
                "detail_images": params.detail_images or [],
                "collection_name": params.collection_name,
                "opacity": params.opacity,
                "scale": params.scale,
                "hide_select": params.hide_select,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            loaded = data.get("loaded_objects", [])
            return (
                f"Loaded {len(loaded)} reference images for '{params.subject_name}' "
                f"into collection '{data.get('collection_name')}'."
            )
        return f"Failed to load reference sheet: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_reference_pack_inspect",
        annotations={
            "title": "Inspect Character Reference Pack",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_reference_pack_inspect(params: ReferencePackInspectInput) -> str:
        """Inspect a folder of reference images and report missing character views/details."""
        try:
            data = inspect_reference_pack_data(
                params.reference_dir,
                params.character_name,
                aliases=params.aliases or [],
                preset=params.preset.value,
            )
        except Exception as exc:
            return f"Failed to inspect reference pack: {exc}"

        lines = [
            f"# Reference Pack Check: {params.character_name}",
            f"Preset: {data.get('preset', params.preset.value)}",
            f"Reference dir: {data.get('reference_dir', params.reference_dir)}",
            f"Status: {data.get('status', 'unknown')}",
            f"Matched files: {data.get('matched_files_count', 0)}",
        ]

        role_summary = data.get("role_summary", {})
        if role_summary:
            lines.append("Found roles:")
            for role, count in role_summary.items():
                lines.append(f"- {role}: {count}")

        missing_required = data.get("missing_required", [])
        lines.append(
            f"Missing required: {', '.join(missing_required) if missing_required else 'none'}"
        )

        missing_optional = data.get("missing_optional", [])
        if missing_optional:
            lines.append(f"Optional gaps: {', '.join(missing_optional)}")

        matched_files = data.get("matched_files", [])
        if matched_files:
            lines.append("Matched files:")
            for item in matched_files:
                lines.append(f"- {item['role']}: {item['name']}")

        return "\n".join(lines)

    @mcp.tool(
        name="blender_reference_pack_setup",
        annotations={
            "title": "Set Up Character Reference Pack",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_reference_pack_setup(params: ReferencePackSetupInput) -> str:
        """Inspect a reference folder and build a Blender-side board plus proportion guides."""
        try:
            inspection = inspect_reference_pack_data(
                params.reference_dir,
                params.character_name,
                aliases=params.aliases or [],
                preset=params.preset.value,
            )
        except Exception as exc:
            return f"Failed to set up reference pack: {exc}"

        result = await server.execute_command(
            "reference",
            "setup_pack",
            {
                "character_name": params.character_name,
                "reference_dir": inspection["reference_dir"],
                "preset": inspection["preset"],
                "matched_files": inspection["matched_files"],
                "missing_required": inspection["missing_required"],
                "missing_optional": inspection["missing_optional"],
                "collection_name": params.collection_name,
                "opacity": params.opacity,
                "primary_scale": params.primary_scale,
                "detail_scale": params.detail_scale,
                "replace_existing": params.replace_existing,
                "create_proportion_guides": params.create_proportion_guides,
                "target_height": params.target_height,
                "head_body_ratio": params.head_body_ratio,
                "origin": params.origin,
                "hide_select": params.hide_select,
            },
        )

        if not result.get("success"):
            return (
                "Failed to set up reference pack: "
                f"{result.get('error', {}).get('message', 'Unknown error')}"
            )

        data = result.get("data", {})
        lines = [
            f"# Reference Board Ready: {params.character_name}",
            f"Collection: {data.get('collection_name', 'N/A')}",
            f"Loaded boards: {data.get('loaded_count', 0)}",
            f"Guides created: {len(data.get('guide_objects', []))}",
            f"Target height: {data.get('target_height', params.target_height)}m",
            f"Head-body ratio: {data.get('head_body_ratio', params.head_body_ratio)}:1",
        ]

        loaded_roles = data.get("loaded_roles", {})
        if loaded_roles:
            lines.append("Loaded roles:")
            for role, count in loaded_roles.items():
                lines.append(f"- {role}: {count}")

        missing_required = data.get("missing_required", [])
        if missing_required:
            lines.append(f"Still missing required: {', '.join(missing_required)}")

        lines.append(
            "Next step: build the base character template and refine silhouette against these boards."
        )
        return "\n".join(lines)

    @mcp.tool(
        name="blender_reference_brief_generate",
        annotations={
            "title": "Generate Reference Modeling Brief",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_reference_brief_generate(params: ReferenceBriefInput) -> str:
        """Generate a structured character-modeling brief from a reference pack.

        With provider=openai and OPENAI_API_KEY configured, the brief becomes image-aware.
        Without that, it still produces a deterministic local brief from the pack coverage.
        """

        try:
            brief = build_reference_brief(
                reference_dir=params.reference_dir,
                character_name=params.character_name,
                aliases=params.aliases or [],
                preset=params.preset.value,
                franchise=params.franchise,
                target_style=params.target_style,
                notes=params.notes,
                provider=params.provider.value,
                model=params.model,
                max_images=params.max_images,
            )

            saved_path = None
            if params.output_path:
                saved_path = _write_json_file(brief, params.output_path, overwrite=params.overwrite)

            return _format_brief_summary(brief, output_path=saved_path)
        except Exception as exc:
            return f"Failed to generate reference brief: {exc}"

    @mcp.tool(
        name="blender_reference_model_audit",
        annotations={
            "title": "Audit Current Model Against References",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def blender_reference_model_audit(params: ReferenceAuditInput) -> str:
        """Compare current model screenshots with the reference pack and produce prioritized fixes.

        When provider=openai and OPENAI_API_KEY is configured, this performs an image-aware audit.
        Otherwise it returns a deterministic checklist scaffold using the reference brief plus
        the supplied/captured review images.
        """

        try:
            audit = await build_reference_model_audit(
                server,
                reference_dir=params.reference_dir,
                character_name=params.character_name,
                aliases=params.aliases or [],
                preset=params.preset.value,
                franchise=params.franchise,
                target_style=params.target_style,
                notes=params.notes,
                provider=params.provider.value,
                model=params.model,
                review_image_paths=params.review_image_paths or [],
                capture_viewport=params.capture_viewport,
                viewport_width=params.viewport_width,
                viewport_height=params.viewport_height,
                capture_render_preview=params.capture_render_preview,
                render_width=params.render_width,
                render_samples=params.render_samples,
                max_reference_images=params.max_reference_images,
                max_review_images=params.max_review_images,
            )

            saved_path = None
            if params.output_path:
                saved_path = _write_json_file(audit, params.output_path, overwrite=params.overwrite)

            return _format_audit_summary(audit, output_path=saved_path)
        except Exception as exc:
            return f"Failed to audit current model against references: {exc}"

    @mcp.tool(
        name="blender_reference_image_update",
        annotations={
            "title": "Update Reference Image",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_reference_image_update(params: ReferenceUpdateImageInput) -> str:
        """Adjust opacity, scale, or selection/render visibility of a reference image."""
        result = await server.execute_command(
            "reference",
            "update_image",
            {
                "object_name": params.object_name,
                "opacity": params.opacity,
                "scale": params.scale,
                "hide_select": params.hide_select,
                "hide_render": params.hide_render,
            },
        )

        if result.get("success"):
            return f"Updated reference image '{params.object_name}'."
        return f"Failed to update reference image: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_reference_clear",
        annotations={
            "title": "Clear Reference Images",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def blender_reference_clear(params: ReferenceClearInput) -> str:
        """Remove reference image objects from the scene."""
        result = await server.execute_command(
            "reference",
            "clear",
            {
                "collection_name": params.collection_name,
                "name_prefix": params.name_prefix,
                "remove_collection_if_empty": params.remove_collection_if_empty,
            },
        )

        if result.get("success"):
            data = result.get("data", {})
            return (
                f"Cleared {data.get('removed_count', 0)} reference objects"
                + (
                    f" from collection '{data.get('collection_name')}'."
                    if data.get("collection_name")
                    else "."
                )
            )
        return f"Failed to clear references: {result.get('error', {}).get('message', 'Unknown error')}"
