"""Quality audit tools for topology, UV, and performance checks."""

import json
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class TargetPlatform(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    AAA = "aaa"


class TopologyAuditInput(BaseModel):
    object_names: Optional[list[str]] = Field(default=None, description="Object list, scans all meshes if empty")
    include_hidden: bool = Field(default=False, description="Whether to include hidden objects")


class UVAuditInput(BaseModel):
    object_names: Optional[list[str]] = Field(default=None, description="Object list, scans all meshes if empty")
    texture_resolution: int = Field(default=2048, ge=256, le=8192, description="Target texture resolution")


class PerformanceAuditInput(BaseModel):
    target_platform: TargetPlatform = Field(default=TargetPlatform.DESKTOP, description="Target platform budget")
    object_names: Optional[list[str]] = Field(default=None, description="Object list, scans all meshes if empty")


class FullAuditInput(BaseModel):
    target_platform: TargetPlatform = Field(default=TargetPlatform.DESKTOP)
    texture_resolution: int = Field(default=2048, ge=256, le=8192)
    object_names: Optional[list[str]] = Field(default=None)


def _parse_json_from_output(output: str) -> dict[str, Any]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not lines:
        return {}
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"raw_output": output}


async def _list_mesh_objects(
    server: "BlenderMCPServer",
    object_names: Optional[list[str]],
) -> list[str]:
    if object_names:
        return object_names
    result = await server.execute_command("object", "list", {"type_filter": "MESH", "limit": 500})
    if not result.get("success"):
        return []
    objects = result.get("data", {}).get("objects", [])
    return [obj.get("name") for obj in objects if obj.get("name")]


def _budget_for_platform(platform: TargetPlatform) -> dict[str, int]:
    budget = {
        TargetPlatform.WEB: {"triangles": 150_000, "draw_calls": 300},
        TargetPlatform.MOBILE: {"triangles": 250_000, "draw_calls": 500},
        TargetPlatform.DESKTOP: {"triangles": 2_000_000, "draw_calls": 2_000},
        TargetPlatform.AAA: {"triangles": 12_000_000, "draw_calls": 8_000},
    }
    return budget[platform]


def register_quality_audit_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register quality audit tools."""

    @mcp.tool(
        name="blender_quality_audit_topology",
        annotations={
            "title": "Topology Quality Audit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_quality_audit_topology(params: TopologyAuditInput) -> dict[str, Any]:
        """Audit topology quality (N-gons, non-manifold edges, loose vertices, face type distribution)."""
        object_names = await _list_mesh_objects(server, params.object_names)
        if not object_names:
            return {"success": False, "error": "No mesh objects found for analysis"}

        # Use utility.execute_python to compute metrics in Blender main context.
        code = f"""
import bpy, bmesh, json

target_names = set({json.dumps(object_names, ensure_ascii=False)})
include_hidden = {str(params.include_hidden)}
report = {{"objects": [], "totals": {{"triangles": 0, "quads": 0, "ngons": 0, "non_manifold_edges": 0, "loose_verts": 0}}}}

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if obj.name not in target_names:
        continue
    if (not include_hidden) and obj.hide_get():
        continue

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    tris = 0
    quads = 0
    ngons = 0
    for face in bm.faces:
        count = len(face.verts)
        if count == 3:
            tris += 1
        elif count == 4:
            quads += 1
        elif count > 4:
            ngons += 1

    non_manifold_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
    loose_verts = sum(1 for vert in bm.verts if len(vert.link_edges) == 0)
    bm.free()

    report["objects"].append({{
        "name": obj.name,
        "triangles": tris,
        "quads": quads,
        "ngons": ngons,
        "non_manifold_edges": non_manifold_edges,
        "loose_verts": loose_verts
    }})
    report["totals"]["triangles"] += tris
    report["totals"]["quads"] += quads
    report["totals"]["ngons"] += ngons
    report["totals"]["non_manifold_edges"] += non_manifold_edges
    report["totals"]["loose_verts"] += loose_verts

issues = []
if report["totals"]["ngons"] > 0:
    issues.append(f"N-gon faces detected: {{report['totals']['ngons']}}")
if report["totals"]["non_manifold_edges"] > 0:
    issues.append(f"Non-manifold edges detected: {{report['totals']['non_manifold_edges']}}")
if report["totals"]["loose_verts"] > 0:
    issues.append(f"Loose vertices detected: {{report['totals']['loose_verts']}}")

score = 100
score -= min(30, report["totals"]["ngons"])
score -= min(35, report["totals"]["non_manifold_edges"] * 2)
score -= min(20, report["totals"]["loose_verts"] * 2)
report["quality_score"] = max(0, score)
report["issues"] = issues

print(json.dumps(report, ensure_ascii=False))
"""

        result = await server.execute_command("utility", "execute_python", {"code": code})
        if not result.get("success"):
            return {"success": False, "error": result.get("error", {}).get("message", "Topology analysis failed")}

        output = result.get("data", {}).get("output", "")
        report = _parse_json_from_output(output)
        report["success"] = True
        report["object_count"] = len(report.get("objects", []))
        return report

    @mcp.tool(
        name="blender_quality_audit_uv",
        annotations={
            "title": "UV Quality Audit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_quality_audit_uv(params: UVAuditInput) -> dict[str, Any]:
        """Audit UV quality (space utilization, stretch, texel density consistency)."""
        object_names = await _list_mesh_objects(server, params.object_names)
        if not object_names:
            return {"success": False, "error": "No mesh objects found for analysis"}

        object_reports: list[dict[str, Any]] = []
        totals = {
            "space_usage": 0.0,
            "avg_stretch": 0.0,
            "quality_score": 0.0,
            "overlapping_faces": 0,
            "objects_with_uv": 0,
        }
        issues: list[str] = []

        for name in object_names:
            result = await server.execute_command(
                "uv",
                "analyze",
                {"object_name": name, "texture_resolution": params.texture_resolution},
            )
            if not result.get("success"):
                object_reports.append(
                    {"name": name, "ok": False, "error": result.get("error", {}).get("message", "UV analysis failed")}
                )
                continue
            data = result.get("data", {})
            object_reports.append({"name": name, "ok": True, **data})
            totals["space_usage"] += data.get("space_usage", 0.0)
            totals["avg_stretch"] += data.get("avg_stretch", 0.0)
            totals["quality_score"] += data.get("quality_score", 0.0)
            totals["overlapping_faces"] += data.get("overlapping_faces", 0)
            totals["objects_with_uv"] += 1
            issues.extend(data.get("issues", []))

        count = max(1, totals["objects_with_uv"])
        report = {
            "success": True,
            "object_count": len(object_names),
            "objects_with_uv": totals["objects_with_uv"],
            "average_space_usage": round(totals["space_usage"] / count, 2),
            "average_stretch": round(totals["avg_stretch"] / count, 4),
            "average_quality_score": round(totals["quality_score"] / count, 2),
            "total_overlapping_faces": totals["overlapping_faces"],
            "issues": sorted(set(issues)),
            "objects": object_reports,
        }
        return report

    @mcp.tool(
        name="blender_quality_audit_performance",
        annotations={
            "title": "Performance Budget Audit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_quality_audit_performance(params: PerformanceAuditInput) -> dict[str, Any]:
        """Audit performance budget (triangles, material slots, estimated draw calls)."""
        object_names = await _list_mesh_objects(server, params.object_names)
        if not object_names:
            return {"success": False, "error": "No mesh objects found for analysis"}

        budget = _budget_for_platform(params.target_platform)
        totals = {"triangles": 0, "vertices": 0, "faces": 0, "draw_calls_est": 0}
        object_reports: list[dict[str, Any]] = []

        for name in object_names:
            info = await server.execute_command(
                "object",
                "get_info",
                {
                    "name": name,
                    "include_mesh_stats": True,
                    "include_modifiers": False,
                    "include_materials": True,
                },
            )
            if not info.get("success"):
                object_reports.append({"name": name, "ok": False, "error": info.get("error", {}).get("message", "Failed to get object info")})
                continue

            data = info.get("data", {})
            mesh_stats = data.get("mesh_stats", {})
            materials = data.get("materials", [])
            triangles = int(mesh_stats.get("triangles", 0))
            vertices = int(mesh_stats.get("vertices", 0))
            faces = int(mesh_stats.get("faces", 0))
            draw_calls = max(1, len(materials)) if triangles > 0 else 0

            totals["triangles"] += triangles
            totals["vertices"] += vertices
            totals["faces"] += faces
            totals["draw_calls_est"] += draw_calls

            object_reports.append(
                {
                    "name": name,
                    "ok": True,
                    "triangles": triangles,
                    "vertices": vertices,
                    "faces": faces,
                    "materials": len(materials),
                    "draw_calls_est": draw_calls,
                }
            )

        tri_ratio = (totals["triangles"] / max(1, budget["triangles"])) * 100
        draw_ratio = (totals["draw_calls_est"] / max(1, budget["draw_calls"])) * 100

        issues = []
        if tri_ratio > 100:
            issues.append(f"Triangle budget exceeded: {totals['triangles']} / {budget['triangles']}")
        if draw_ratio > 100:
            issues.append(f"Draw-call budget exceeded: {totals['draw_calls_est']} / {budget['draw_calls']}")

        score = 100
        score -= min(60, max(0, tri_ratio - 100) * 0.6)
        score -= min(40, max(0, draw_ratio - 100) * 0.8)
        score = round(max(0, score), 2)

        return {
            "success": True,
            "target_platform": params.target_platform.value,
            "budget": budget,
            "totals": totals,
            "usage_percent": {
                "triangles": round(tri_ratio, 2),
                "draw_calls": round(draw_ratio, 2),
            },
            "quality_score": score,
            "issues": issues,
            "objects": object_reports,
        }

    @mcp.tool(
        name="blender_quality_audit_full",
        annotations={
            "title": "Full Quality Audit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_quality_audit_full(params: FullAuditInput) -> dict[str, Any]:
        """Run topology + UV + performance triple audit and output a combined score."""
        topo = await blender_quality_audit_topology(
            TopologyAuditInput(object_names=params.object_names, include_hidden=False)
        )
        uv = await blender_quality_audit_uv(
            UVAuditInput(object_names=params.object_names, texture_resolution=params.texture_resolution)
        )
        perf = await blender_quality_audit_performance(
            PerformanceAuditInput(object_names=params.object_names, target_platform=params.target_platform)
        )

        if not topo.get("success") or not uv.get("success") or not perf.get("success"):
            return {
                "success": False,
                "topology": topo,
                "uv": uv,
                "performance": perf,
            }

        final_score = round(
            (float(topo.get("quality_score", 0)) * 0.35)
            + (float(uv.get("average_quality_score", 0)) * 0.35)
            + (float(perf.get("quality_score", 0)) * 0.30),
            2,
        )

        return {
            "success": True,
            "final_score": final_score,
            "topology": topo,
            "uv": uv,
            "performance": perf,
            "grade": "A" if final_score >= 90 else "B" if final_score >= 75 else "C" if final_score >= 60 else "D",
        }
