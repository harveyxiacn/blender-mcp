"""
Node System Tools

Provides creation and editing functionality for shader nodes, geometry nodes, and compositor nodes.
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== Input Models ====================

class NodeAddInput(BaseModel):
    """Add node input"""
    target: str = Field(..., description="Target: material name, 'compositor', or object name (geometry nodes)")
    node_type: str = Field(..., description="Node type (e.g. ShaderNodeBsdfPrincipled)")
    location: Optional[List[float]] = Field(default=None, description="Node position [x, y]")
    name: Optional[str] = Field(default=None, description="Node name")


class NodeConnectInput(BaseModel):
    """Connect nodes input"""
    target: str = Field(..., description="Target material/compositor/object name")
    from_node: str = Field(..., description="Source node name")
    from_socket: str = Field(..., description="Source socket name or index")
    to_node: str = Field(..., description="Target node name")
    to_socket: str = Field(..., description="Target socket name or index")


class NodeSetValueInput(BaseModel):
    """Set node value input"""
    target: str = Field(..., description="Target material/compositor/object name")
    node_name: str = Field(..., description="Node name")
    input_name: str = Field(..., description="Input name")
    value: Any = Field(..., description="Value (number, color array, etc.)")


class NodeGroupCreateInput(BaseModel):
    """Create node group input"""
    group_name: str = Field(..., description="Node group name")
    node_type: str = Field(default="SHADER", description="Type: SHADER, GEOMETRY, COMPOSITOR")


class ShaderPresetInput(BaseModel):
    """Shader preset input"""
    material_name: str = Field(..., description="Material name")
    preset: str = Field(
        default="pbr_basic",
        description="Preset: pbr_basic, glass, metal, emission, subsurface, toon"
    )
    color: Optional[List[float]] = Field(default=None, description="Base color RGBA")


class GeometryNodesAddInput(BaseModel):
    """Add geometry nodes modifier input"""
    object_name: str = Field(..., description="Object name")
    modifier_name: str = Field(default="GeometryNodes", description="Modifier name")


class GeometryNodesPresetInput(BaseModel):
    """Geometry nodes preset input"""
    object_name: str = Field(..., description="Object name")
    preset: str = Field(
        default="scatter",
        description="Preset: scatter, array, curve_to_mesh, instance_points"
    )
    params: Optional[Dict[str, Any]] = Field(default=None, description="Preset parameters")


# ==================== Tool Registration ====================

def register_node_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """Register node system tools"""

    @mcp.tool(
        name="blender_node_add",
        annotations={
            "title": "Add Node",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_node_add(params: NodeAddInput) -> str:
        """Add a node to a node tree.

        Common shader node types:
        - ShaderNodeBsdfPrincipled (Principled BSDF)
        - ShaderNodeMixShader (Mix Shader)
        - ShaderNodeTexImage (Image Texture)
        - ShaderNodeTexNoise (Noise Texture)
        - ShaderNodeBump (Bump)
        - ShaderNodeNormalMap (Normal Map)
        - ShaderNodeMath (Math)
        - ShaderNodeMixRGB (Mix RGB)

        Args:
            params: Target, node type, position

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "nodes", "add",
            {
                "target": params.target,
                "node_type": params.node_type,
                "location": params.location or [0, 0],
                "name": params.name
            }
        )

        if result.get("success"):
            node_name = result.get("data", {}).get("node_name", "")
            return f"Successfully added node '{node_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_node_connect",
        annotations={
            "title": "Connect Nodes",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_node_connect(params: NodeConnectInput) -> str:
        """Connect two nodes.

        Args:
            params: Source node, target node, sockets

        Returns:
            Connection result
        """
        result = await server.execute_command(
            "nodes", "connect",
            {
                "target": params.target,
                "from_node": params.from_node,
                "from_socket": params.from_socket,
                "to_node": params.to_node,
                "to_socket": params.to_socket
            }
        )

        if result.get("success"):
            return f"Successfully connected {params.from_node} -> {params.to_node}"
        else:
            return f"Failed to connect: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_node_set_value",
        annotations={
            "title": "Set Node Value",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_node_set_value(params: NodeSetValueInput) -> str:
        """Set a node input value.

        Args:
            params: Target, node name, input name, value

        Returns:
            Setting result
        """
        result = await server.execute_command(
            "nodes", "set_value",
            {
                "target": params.target,
                "node_name": params.node_name,
                "input_name": params.input_name,
                "value": params.value
            }
        )

        if result.get("success"):
            return f"Successfully set {params.node_name}.{params.input_name}"
        else:
            return f"Failed to set: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_shader_preset",
        annotations={
            "title": "Apply Shader Preset",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_shader_preset(params: ShaderPresetInput) -> str:
        """Apply a shader preset (PBR, glass, metal, etc.).

        Available presets:
        - pbr_basic: Basic PBR material
        - glass: Glass material
        - metal: Metal material
        - emission: Emission material
        - subsurface: Subsurface scattering (skin)
        - toon: Toon shading

        Args:
            params: Material name, preset type, color

        Returns:
            Application result
        """
        result = await server.execute_command(
            "nodes", "shader_preset",
            {
                "material_name": params.material_name,
                "preset": params.preset,
                "color": params.color
            }
        )

        if result.get("success"):
            return f"Successfully applied {params.preset} preset to '{params.material_name}'"
        else:
            return f"Failed to apply: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_geometry_nodes_add",
        annotations={
            "title": "Add Geometry Nodes Modifier",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_geometry_nodes_add(params: GeometryNodesAddInput) -> str:
        """Add a geometry nodes modifier to an object.

        Args:
            params: Object name, modifier name

        Returns:
            Addition result
        """
        result = await server.execute_command(
            "nodes", "geonodes_add",
            {
                "object_name": params.object_name,
                "modifier_name": params.modifier_name
            }
        )

        if result.get("success"):
            return f"Successfully added geometry nodes to '{params.object_name}'"
        else:
            return f"Failed to add: {result.get('error', {}).get('message', 'Unknown error')}"

    @mcp.tool(
        name="blender_geometry_nodes_preset",
        annotations={
            "title": "Apply Geometry Nodes Preset",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_geometry_nodes_preset(params: GeometryNodesPresetInput) -> str:
        """Apply a geometry nodes preset (scatter, array, etc.).

        Available presets:
        - scatter: Scatter instances on surface
        - array: Linear array
        - curve_to_mesh: Curve to mesh
        - instance_points: Instance on points

        Args:
            params: Object name, preset type, parameters

        Returns:
            Application result
        """
        result = await server.execute_command(
            "nodes", "geonodes_preset",
            {
                "object_name": params.object_name,
                "preset": params.preset,
                "params": params.params or {}
            }
        )

        if result.get("success"):
            return f"Successfully applied {params.preset} geometry nodes to '{params.object_name}'"
        else:
            return f"Failed to apply: {result.get('error', {}).get('message', 'Unknown error')}"
