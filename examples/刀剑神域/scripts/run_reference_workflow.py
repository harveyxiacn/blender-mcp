"""Run a reference-driven SAO character workflow through Blender MCP.

This script ties together the new reference-pack tools:
1. inspect the local reference folder
2. generate a modeling brief
3. optionally run an existing SAO build script in Blender
4. audit the current model against the reference pack
5. stage the reference board in Blender for manual refinement
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from blender_mcp.connection import BlenderConnection, BlenderConnectionError
from blender_mcp.tools.reference import (
    build_reference_brief,
    build_reference_model_audit,
    inspect_reference_pack_data,
)

EXAMPLE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REFERENCE_DIR = EXAMPLE_DIR / "references"
DEFAULT_OUTPUT_ROOT = EXAMPLE_DIR / "outputs" / "reference_workflow"

CHARACTER_CONFIG: dict[str, dict[str, Any]] = {
    "kirito": {
        "aliases": ["桐人"],
        "build_script": "AAA_v2_kirito.py",
        "notes": "Keep the black coat silhouette slim, the bangs layered, and the dual-swords read clearly.",
        "target_height": 1.72,
        "head_body_ratio": 6.0,
    },
    "asuna": {
        "aliases": ["亚丝娜", "結城明日奈"],
        "build_script": "AAA_v2_asuna.py",
        "notes": "Protect the long hair flow, KoB red-white layering, and rapier proportions.",
        "target_height": 1.68,
        "head_body_ratio": 6.1,
    },
    "sachi": {
        "aliases": ["幸"],
        "build_script": "AAA_v2_sachi.py",
        "notes": "Keep the softer silhouette and the blue school-uniform shapes readable.",
        "target_height": 1.6,
        "head_body_ratio": 5.9,
    },
    "klein": {
        "aliases": ["克莱因", "克ライン"],
        "build_script": "AAA_v2_klein.py",
        "notes": "Hold the broader silhouette, tied-back hair, and red armor accents.",
        "target_height": 1.78,
        "head_body_ratio": 6.2,
    },
}


def _normalize_name(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "_", value.lower().strip()).strip("_")


def _resolve_character(value: str) -> str:
    token = _normalize_name(value)
    for key, config in CHARACTER_CONFIG.items():
        candidates = [key, *config.get("aliases", [])]
        if any(_normalize_name(candidate) == token for candidate in candidates):
            return key
    raise KeyError(f"Unsupported character: {value}")


def _character_aliases(character_key: str, extra_aliases: list[str]) -> list[str]:
    aliases = list(CHARACTER_CONFIG[character_key].get("aliases", []))
    aliases.extend(extra_aliases)
    return sorted({alias for alias in aliases if alias})


def _output_dir(root: Path, character_key: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return root / character_key / stamp


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_script_path(character_key: str, override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return (SCRIPT_DIR / CHARACTER_CONFIG[character_key]["build_script"]).resolve()


def _combined_notes(character_key: str, user_notes: str) -> str:
    notes = [CHARACTER_CONFIG[character_key].get("notes", "").strip()]
    if user_notes.strip():
        notes.append(user_notes.strip())
    return " ".join(note for note in notes if note)


def _print_summary(inspect_path: Path, brief_path: Path, audit_path: Path, setup_path: Path) -> None:
    print("\nSaved outputs:")
    for path in (inspect_path, brief_path, audit_path, setup_path):
        print(f"  - {path}")


def _print_audit_highlights(audit: dict[str, Any]) -> None:
    print("\nAudit summary:")
    print(f"  Character: {audit.get('character_name', 'unknown')}")
    print(f"  Mode: {audit.get('analysis_mode', 'unknown')}")
    print(f"  Reference status: {audit.get('reference_status', 'unknown')}")
    print(f"  Match score: {audit.get('match_score', 'n/a')}")
    print(f"  Overall: {audit.get('overall_match', 'n/a')}")

    issues = audit.get("issues", [])
    if issues:
        print("  Top issues:")
        for item in issues[:3]:
            severity = item.get("severity", "unknown")
            category = item.get("category", "general")
            observation = item.get("observation", "")
            print(f"    - [{severity}] {category}: {observation}")


class _ConnectionAdapter:
    def __init__(self, connection: BlenderConnection) -> None:
        self._connection = connection

    async def execute_command(
        self, category: str, action: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._connection.send_command(category, action, params)


async def _run_build_script(
    connection: BlenderConnection,
    script_path: Path,
    *,
    character_key: str,
    brief_path: Path,
    workflow_dir: Path,
    timeout: int,
) -> str:
    if not script_path.exists():
        raise FileNotFoundError(f"Build script not found: {script_path}")

    code = (
        "import os\n"
        "import runpy\n"
        "import sys\n"
        f"path = {json.dumps(str(script_path), ensure_ascii=False)}\n"
        f"os.environ['SAO_REFERENCE_BRIEF_PATH'] = {json.dumps(str(brief_path), ensure_ascii=False)}\n"
        f"os.environ['SAO_REFERENCE_WORKFLOW_DIR'] = {json.dumps(str(workflow_dir), ensure_ascii=False)}\n"
        f"os.environ['SAO_REFERENCE_CHARACTER'] = {json.dumps(character_key, ensure_ascii=False)}\n"
        f"sys.path.insert(0, {json.dumps(str(script_path.parent), ensure_ascii=False)})\n"
        "runpy.run_path(path, run_name='__main__')\n"
        "result = 'OK'\n"
    )
    result = await connection.send_command(
        "system",
        "execute_python",
        {"code": code, "timeout": timeout},
    )
    if not result.get("success"):
        message = result.get("error", {}).get("message", "Unknown error")
        raise RuntimeError(f"Build script failed: {message}")
    return str(result.get("data", {}).get("result", "OK"))


async def _run_workflow(args: argparse.Namespace) -> int:
    character_key = _resolve_character(args.character)
    aliases = _character_aliases(character_key, args.alias)
    reference_dir = Path(args.reference_dir).expanduser().resolve()
    output_dir = _output_dir(Path(args.output_root).expanduser().resolve(), character_key)
    notes = _combined_notes(character_key, args.notes)

    if args.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("provider=openai requires OPENAI_API_KEY to be set.")

    if args.no_render_preview and not args.capture_viewport and not args.review_image:
        raise ValueError(
            "Audit needs at least one review source: --review-image, --capture-viewport, or render preview."
        )

    print(f"Character: {character_key}")
    print(f"Reference dir: {reference_dir}")
    print(f"Output dir: {output_dir}")

    inspection = inspect_reference_pack_data(
        reference_dir=str(reference_dir),
        character_name=character_key,
        aliases=aliases,
        preset="SAO",
    )
    inspect_path = output_dir / "inspect.json"
    _write_json(inspect_path, inspection)

    print(
        "Reference pack:"
        f" status={inspection['status']}, files={inspection['matched_files_count']},"
        f" missing_required={inspection['missing_required'] or 'none'}"
    )
    if inspection["matched_files_count"] == 0:
        raise RuntimeError("No matching reference images were found for the selected character.")

    brief = build_reference_brief(
        reference_dir=str(reference_dir),
        character_name=character_key,
        aliases=aliases,
        preset="SAO",
        franchise="Sword Art Online",
        target_style=args.target_style,
        notes=notes,
        provider=args.provider,
        model=args.model,
    )
    brief_path = output_dir / "brief.json"
    _write_json(brief_path, brief)

    connection = BlenderConnection(host=args.host, port=args.port, timeout=args.timeout)
    adapter = _ConnectionAdapter(connection)

    try:
        await connection.connect()

        if not args.skip_build:
            build_script = _build_script_path(character_key, args.build_script)
            print(f"Running build script: {build_script}")
            build_result = await _run_build_script(
                connection,
                build_script,
                character_key=character_key,
                brief_path=brief_path,
                workflow_dir=output_dir,
                timeout=args.timeout,
            )
            print(f"Build result: {build_result}")

        audit = await build_reference_model_audit(
            adapter,
            reference_dir=str(reference_dir),
            character_name=character_key,
            aliases=aliases,
            preset="SAO",
            franchise="Sword Art Online",
            target_style=args.target_style,
            notes=notes,
            provider=args.provider,
            model=args.model,
            review_image_paths=args.review_image,
            capture_viewport=args.capture_viewport,
            viewport_width=args.viewport_width,
            viewport_height=args.viewport_height,
            capture_render_preview=not args.no_render_preview,
            render_width=args.render_width,
            render_samples=args.render_samples,
        )
        audit_path = output_dir / "audit.json"
        _write_json(audit_path, audit)

        setup_result = await connection.send_command(
            "reference",
            "setup_pack",
            {
                "character_name": character_key,
                "reference_dir": inspection["reference_dir"],
                "preset": inspection["preset"],
                "matched_files": inspection["matched_files"],
                "missing_required": inspection["missing_required"],
                "missing_optional": inspection["missing_optional"],
                "collection_name": args.collection_name or f"References_{character_key}",
                "opacity": args.opacity,
                "primary_scale": args.primary_scale,
                "detail_scale": args.detail_scale,
                "replace_existing": True,
                "create_proportion_guides": args.create_guides,
                "target_height": args.target_height
                if args.target_height is not None
                else CHARACTER_CONFIG[character_key]["target_height"],
                "head_body_ratio": args.head_body_ratio
                if args.head_body_ratio is not None
                else CHARACTER_CONFIG[character_key]["head_body_ratio"],
                "origin": [0.0, 0.0, 0.0],
                "hide_select": True,
            },
        )
        if not setup_result.get("success"):
            message = setup_result.get("error", {}).get("message", "Unknown error")
            raise RuntimeError(f"Reference pack setup failed: {message}")

        setup_path = output_dir / "setup.json"
        _write_json(setup_path, setup_result)
    finally:
        await connection.disconnect()

    _print_summary(inspect_path, brief_path, audit_path, setup_path)
    _print_audit_highlights(audit)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the SAO reference-pack inspect/brief/build/audit/setup workflow."
    )
    parser.add_argument("character", help="Character key or alias, e.g. kirito / 桐人 / asuna")
    parser.add_argument(
        "--reference-dir",
        default=str(DEFAULT_REFERENCE_DIR),
        help="Reference image folder",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root folder for JSON outputs",
    )
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        help="Extra filename alias to match during reference inspection",
    )
    parser.add_argument(
        "--provider",
        choices=["none", "openai"],
        default="none",
        help="Vision provider for brief and audit",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Vision model when provider=openai",
    )
    parser.add_argument(
        "--target-style",
        default="anime",
        help="Target modeling style label written into the brief",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Extra modeling notes appended to the character defaults",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the base character build script and only do audit + reference staging",
    )
    parser.add_argument(
        "--build-script",
        default=None,
        help="Override the default character build script path",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Blender MCP host")
    parser.add_argument("--port", type=int, default=9876, help="Blender MCP port")
    parser.add_argument("--timeout", type=int, default=180, help="Socket timeout in seconds")
    parser.add_argument(
        "--collection-name",
        default=None,
        help="Optional Blender collection for the reference board",
    )
    parser.add_argument("--opacity", type=float, default=0.55, help="Reference image opacity")
    parser.add_argument(
        "--primary-scale",
        type=float,
        default=1.6,
        help="Scale for front/side/back reference boards",
    )
    parser.add_argument(
        "--detail-scale",
        type=float,
        default=0.95,
        help="Scale for face/detail/weapon reference boards",
    )
    parser.add_argument(
        "--target-height",
        type=float,
        default=None,
        help="Override target height for proportion guides",
    )
    parser.add_argument(
        "--head-body-ratio",
        type=float,
        default=None,
        help="Override head-to-body ratio for proportion guides",
    )
    parser.add_argument(
        "--create-guides",
        action="store_true",
        help="Create proportion guides when staging the reference board after the audit",
    )
    parser.add_argument(
        "--review-image",
        action="append",
        default=[],
        help="Existing model screenshot to include in the audit",
    )
    parser.add_argument(
        "--capture-viewport",
        action="store_true",
        help="Capture a viewport snapshot for the audit",
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=1280,
        help="Viewport snapshot width when --capture-viewport is enabled",
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=720,
        help="Viewport snapshot height when --capture-viewport is enabled",
    )
    parser.add_argument(
        "--no-render-preview",
        action="store_true",
        help="Do not capture a Blender render preview for the audit",
    )
    parser.add_argument(
        "--render-width",
        type=int,
        default=960,
        help="Render preview width for the audit",
    )
    parser.add_argument(
        "--render-samples",
        type=int,
        default=16,
        help="Render preview samples for the audit",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(_run_workflow(args))
    except (BlenderConnectionError, FileNotFoundError, KeyError, RuntimeError, ValueError) as exc:
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
