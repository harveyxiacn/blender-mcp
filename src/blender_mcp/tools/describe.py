"""
Blender MCP - Scene Describe & Hierarchy Tools

Provide structured scene understanding for AI assistants.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

from mcp.server.fastmcp import FastMCP


class DescribeFormat(str, Enum):
    """Output format"""

    MARKDOWN = "markdown"
    JSON = "json"


class DescribeSceneInput(BaseModel):
    """Scene describe input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    format: DescribeFormat = Field(
        default=DescribeFormat.MARKDOWN, description="Output format: markdown or json"
    )


class DescribeHierarchyInput(BaseModel):
    """Hierarchy describe input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    format: DescribeFormat = Field(
        default=DescribeFormat.MARKDOWN, description="Output format: markdown or json"
    )


class DescribeObjectInput(BaseModel):
    """Object describe input"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Object name to inspect", min_length=1, max_length=200)
    format: DescribeFormat = Field(
        default=DescribeFormat.MARKDOWN, description="Output format: markdown or json"
    )


def register_describe_tools(mcp: FastMCP, server: BlenderMCPServer) -> None:
    """Register describe tools"""

    @mcp.tool(
        name="blender_describe_scene",
        annotations={
            "title": "Describe Scene",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_describe_scene(params: DescribeSceneInput) -> str:
        """Get a structured summary of the current scene: object counts by type, materials,
        lights, camera, render settings, and frame range.

        Example: Describe the scene to understand what objects exist before making changes.
        """
        result = await server.execute_command(
            "describe", "scene", {"format": params.format.value}
        )

        if result.get("success"):
            data = result.get("data", {})
            if params.format == DescribeFormat.JSON:
                import json

                return json.dumps(data, indent=2)
            return data.get("summary", str(data))
        else:
            error = result.get("error", {})
            return f"Describe scene failed: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_describe_hierarchy",
        annotations={
            "title": "Describe Object Hierarchy",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_describe_hierarchy(params: DescribeHierarchyInput) -> str:
        """Get the full parent-child object tree of the scene as indented text or JSON.

        Example: Show the hierarchy to understand how objects are organized and parented.
        """
        result = await server.execute_command(
            "describe", "hierarchy", {"format": params.format.value}
        )

        if result.get("success"):
            data = result.get("data", {})
            if params.format == DescribeFormat.JSON:
                import json

                return json.dumps(data, indent=2)
            return data.get("tree", str(data))
        else:
            error = result.get("error", {})
            return f"Describe hierarchy failed: {error.get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_describe_object",
        annotations={
            "title": "Deep Inspect Object",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def blender_describe_object(params: DescribeObjectInput) -> str:
        """Deep inspection of a single object: topology stats (verts/edges/faces/ngons),
        material slots, modifier stack, constraints, parent chain, and bounding box.

        Example: Inspect 'Cube' to check its polygon count and applied modifiers.
        """
        result = await server.execute_command(
            "describe",
            "object",
            {"name": params.name, "format": params.format.value},
        )

        if result.get("success"):
            data = result.get("data", {})
            if params.format == DescribeFormat.JSON:
                import json

                return json.dumps(data, indent=2)
            return data.get("summary", str(data))
        else:
            error = result.get("error", {})
            suggestion = error.get("suggestion", "")
            msg = f"Describe object failed: {error.get('message', 'Unknown error')}"
            if suggestion:
                msg += f"\nSuggestion: {suggestion}"
            return msg
