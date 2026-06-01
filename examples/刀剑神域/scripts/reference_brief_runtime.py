"""Runtime helpers for applying reference-brief tuning to SAO build scripts."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = SCRIPT_DIR.parent
OUTPUT_ROOT = EXAMPLE_DIR / "outputs" / "reference_workflow"

DEFAULT_TUNING = {
    "head_radius_scale": 1.0,
    "eye_scale": 1.0,
    "hair_volume_scale": 1.0,
    "bang_length_scale": 1.0,
    "side_hair_length_scale": 1.0,
    "back_hair_length_scale": 1.0,
    "top_hair_length_scale": 1.0,
    "torso_width_scale": 1.0,
    "torso_depth_scale": 1.0,
    "coat_length_scale": 1.0,
    "coat_flare_scale": 1.0,
    "skirt_length_scale": 1.0,
    "skirt_flare_scale": 1.0,
    "armor_width_scale": 1.0,
    "armor_height_scale": 1.0,
}

CHARACTER_DEFAULTS = {
    "kirito": {
        "head_radius_scale": 1.02,
        "eye_scale": 1.05,
        "hair_volume_scale": 1.10,
        "bang_length_scale": 1.08,
        "side_hair_length_scale": 1.05,
        "back_hair_length_scale": 1.08,
        "top_hair_length_scale": 1.04,
        "torso_width_scale": 0.98,
        "torso_depth_scale": 0.98,
        "coat_length_scale": 1.06,
        "coat_flare_scale": 0.98,
    },
    "asuna": {
        "head_radius_scale": 1.01,
        "eye_scale": 1.08,
        "hair_volume_scale": 1.08,
        "bang_length_scale": 1.03,
        "side_hair_length_scale": 1.10,
        "back_hair_length_scale": 1.20,
        "torso_width_scale": 0.99,
        "torso_depth_scale": 0.99,
        "skirt_length_scale": 1.04,
        "skirt_flare_scale": 1.06,
        "armor_width_scale": 1.03,
        "armor_height_scale": 1.02,
    },
}

KEYWORD_RULES: list[tuple[tuple[str, ...], dict[str, float]]] = [
    (
        ("slim", "slender", "lean", "纤细", "修身", "纤长"),
        {
            "torso_width_scale": 0.97,
            "torso_depth_scale": 0.98,
            "coat_flare_scale": 0.97,
        },
    ),
    (
        ("large eyes", "big eyes", "anime eyes", "大眼", "大而", "动漫眼"),
        {
            "eye_scale": 1.05,
        },
    ),
    (
        ("bang", "bangs", "fringe", "刘海"),
        {
            "bang_length_scale": 1.05,
        },
    ),
    (
        ("long hair", "flowing hair", "超长", "长发", "过腰", "waist"),
        {
            "back_hair_length_scale": 1.12,
            "hair_volume_scale": 1.04,
        },
    ),
    (
        ("coat", "风衣", "long coat"),
        {
            "coat_length_scale": 1.04,
        },
    ),
    (
        ("pleated skirt", "百褶裙", "外裙"),
        {
            "skirt_length_scale": 1.04,
            "skirt_flare_scale": 1.05,
        },
    ),
    (
        ("armor", "breastplate", "胸甲", "kob"),
        {
            "armor_width_scale": 1.03,
            "armor_height_scale": 1.02,
        },
    ),
]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _merge_text_chunks(brief: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("must_match_features", "modeling_priorities", "ambiguities", "notes"):
        value = brief.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value if item)
        elif value:
            parts.append(str(value))

    vision = brief.get("vision_analysis") or {}
    if isinstance(vision, dict):
        for value in vision.values():
            if isinstance(value, dict):
                parts.extend(str(item) for item in value.values() if item)
            elif isinstance(value, list):
                parts.extend(str(item) for item in value if item)
            elif value:
                parts.append(str(value))

    return _normalize_text(" ".join(parts))


def _find_latest_brief(character_name: str) -> Path | None:
    root = OUTPUT_ROOT / character_name
    if not root.exists():
        return None

    candidates = sorted(
        root.glob("*/brief.json"), key=lambda item: item.stat().st_mtime, reverse=True
    )
    return candidates[0] if candidates else None


def load_reference_brief(character_name: str) -> tuple[dict[str, Any], str | None]:
    env_path = os.environ.get("SAO_REFERENCE_BRIEF_PATH")
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")), str(path.resolve())

    latest = _find_latest_brief(character_name)
    if latest is not None:
        return json.loads(latest.read_text(encoding="utf-8")), str(latest.resolve())

    return {}, None


def get_reference_tuning(character_name: str) -> dict[str, Any]:
    brief, brief_path = load_reference_brief(character_name)

    tuning: dict[str, Any] = dict(DEFAULT_TUNING)
    tuning.update(CHARACTER_DEFAULTS.get(character_name, {}))
    tuning["character_name"] = character_name
    tuning["brief_path"] = brief_path

    if not brief:
        return tuning

    text_blob = _merge_text_chunks(brief)
    tuning["brief_status"] = brief.get("status")

    for keywords, updates in KEYWORD_RULES:
        if any(keyword in text_blob for keyword in keywords):
            for key, value in updates.items():
                tuning[key] = round(float(tuning.get(key, 1.0)) * value, 4)

    vision = brief.get("vision_analysis") or {}
    if isinstance(vision, dict):
        body = vision.get("body") or {}
        if isinstance(body, dict):
            build = _normalize_text(str(body.get("build", "")))
            if any(token in build for token in ("slim", "slender", "lean", "纤细")):
                tuning["torso_width_scale"] = round(tuning["torso_width_scale"] * 0.97, 4)
                tuning["torso_depth_scale"] = round(tuning["torso_depth_scale"] * 0.98, 4)

        hair = vision.get("hair") or {}
        if isinstance(hair, dict):
            hair_text = _normalize_text(
                " ".join(str(hair.get(key, "")) for key in ("cut", "silhouette", "color"))
            )
            if any(token in hair_text for token in ("long", "waist", "flow", "过腰", "长")):
                tuning["back_hair_length_scale"] = round(tuning["back_hair_length_scale"] * 1.08, 4)
            if any(token in hair_text for token in ("spiky", "spike", "刺", "蓬松")):
                tuning["hair_volume_scale"] = round(tuning["hair_volume_scale"] * 1.05, 4)

    return tuning


def scale_hair_entries(
    entries: list[tuple[float, float, float, tuple[float, float, float], float, float, float]],
    *,
    length_scale: float = 1.0,
    width_scale: float = 1.0,
) -> list[tuple[float, float, float, tuple[float, float, float], float, float, float]]:
    return [
        (x, y, z, rot, ln * length_scale, bw * width_scale, tw * width_scale)
        for x, y, z, rot, ln, bw, tw in entries
    ]


def scale_loft_profiles(
    profiles: list[tuple[float, float, float, float, float]],
    *,
    radius_x: float = 1.0,
    radius_y: float = 1.0,
    span_scale: float = 1.0,
    anchor: str = "top",
) -> list[tuple[float, float, float, float, float]]:
    if not profiles:
        return profiles

    z_values = [profile[0] for profile in profiles]
    anchor_z = max(z_values) if anchor == "top" else min(z_values)
    scaled: list[tuple[float, float, float, float, float]] = []

    for z, rx, ry, ox, oy in profiles:
        if anchor == "top":
            new_z = anchor_z - (anchor_z - z) * span_scale
        else:
            new_z = anchor_z + (z - anchor_z) * span_scale
        scaled.append((new_z, rx * radius_x, ry * radius_y, ox, oy))

    return scaled
