"""
节点系统工具

提供着色器节点、几何节点、合成器节点的创建和编辑功能。
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class NodeAddInput(BaseModel):
    """添加节点输入"""
    target: str = Field(..., description="目标: material名称 或 'compositor' 或 object名称(几何节点)")
    node_type: str = Field(..., description="节点类型 (如 ShaderNodeBsdfPrincipled)")
    location: Optional[List[float]] = Field(default=None, description="节点位置 [x, y]")
    name: Optional[str] = Field(default=None, description="节点名称")


class NodeConnectInput(BaseModel):
    """连接节点输入"""
    target: str = Field(..., description="目标材质/合成器/对象名称")
    from_node: str = Field(..., description="源节点名称")
    from_socket: str = Field(..., description="源插槽名称或索引")
    to_node: str = Field(..., description="目标节点名称")
    to_socket: str = Field(..., description="目标插槽名称或索引")


class NodeSetValueInput(BaseModel):
    """设置节点值输入"""
    target: str = Field(..., description="目标材质/合成器/对象名称")
    node_name: str = Field(..., description="节点名称")
    input_name: str = Field(..., description="输入名称")
    value: Any = Field(..., description="值 (数字、颜色数组等)")


class NodeGroupCreateInput(BaseModel):
    """创建节点组输入"""
    group_name: str = Field(..., description="节点组名称")
    node_type: str = Field(default="SHADER", description="类型: SHADER, GEOMETRY, COMPOSITOR")


class ShaderPresetInput(BaseModel):
    """着色器预设输入"""
    material_name: str = Field(..., description="材质名称")
    preset: str = Field(
        default="pbr_basic",
        description="预设: pbr_basic, glass, metal, emission, subsurface, toon"
    )
    color: Optional[List[float]] = Field(default=None, description="基础颜色 RGBA")


class GeometryNodesAddInput(BaseModel):
    """添加几何节点修改器输入"""
    object_name: str = Field(..., description="对象名称")
    modifier_name: str = Field(default="GeometryNodes", description="修改器名称")


class GeometryNodesPresetInput(BaseModel):
    """几何节点预设输入"""
    object_name: str = Field(..., description="对象名称")
    preset: str = Field(
        default="scatter",
        description="预设: scatter, array, curve_to_mesh, instance_points"
    )
    params: Optional[Dict[str, Any]] = Field(default=None, description="预设参数")


# ==================== 工具注册 ====================

def register_node_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册节点系统工具"""
    
    @mcp.tool(
        name="blender_node_add",
        annotations={
            "title": "添加节点",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_node_add(params: NodeAddInput) -> str:
        """在节点树中添加节点。
        
        常用着色器节点类型:
        - ShaderNodeBsdfPrincipled (原理化BSDF)
        - ShaderNodeMixShader (混合着色器)
        - ShaderNodeTexImage (图像纹理)
        - ShaderNodeTexNoise (噪波纹理)
        - ShaderNodeBump (凹凸)
        - ShaderNodeNormalMap (法线贴图)
        - ShaderNodeMath (数学)
        - ShaderNodeMixRGB (混合RGB)
        
        Args:
            params: 目标、节点类型、位置
            
        Returns:
            添加结果
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
            return f"成功添加节点 '{node_name}'"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_node_connect",
        annotations={
            "title": "连接节点",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_node_connect(params: NodeConnectInput) -> str:
        """连接两个节点。
        
        Args:
            params: 源节点、目标节点、插槽
            
        Returns:
            连接结果
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
            return f"成功连接 {params.from_node} -> {params.to_node}"
        else:
            return f"连接失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_node_set_value",
        annotations={
            "title": "设置节点值",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_node_set_value(params: NodeSetValueInput) -> str:
        """设置节点输入值。
        
        Args:
            params: 目标、节点名称、输入名称、值
            
        Returns:
            设置结果
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
            return f"成功设置 {params.node_name}.{params.input_name}"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_shader_preset",
        annotations={
            "title": "应用着色器预设",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_shader_preset(params: ShaderPresetInput) -> str:
        """应用着色器预设（PBR、玻璃、金属等）。
        
        可用预设:
        - pbr_basic: 基础PBR材质
        - glass: 玻璃材质
        - metal: 金属材质
        - emission: 自发光材质
        - subsurface: 次表面散射（皮肤）
        - toon: 卡通着色
        
        Args:
            params: 材质名称、预设类型、颜色
            
        Returns:
            应用结果
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
            return f"成功为 '{params.material_name}' 应用 {params.preset} 预设"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_geometry_nodes_add",
        annotations={
            "title": "添加几何节点修改器",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_geometry_nodes_add(params: GeometryNodesAddInput) -> str:
        """为对象添加几何节点修改器。
        
        Args:
            params: 对象名称、修改器名称
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "nodes", "geonodes_add",
            {
                "object_name": params.object_name,
                "modifier_name": params.modifier_name
            }
        )
        
        if result.get("success"):
            return f"成功为 '{params.object_name}' 添加几何节点"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_geometry_nodes_preset",
        annotations={
            "title": "应用几何节点预设",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_geometry_nodes_preset(params: GeometryNodesPresetInput) -> str:
        """应用几何节点预设（散布、阵列等）。
        
        可用预设:
        - scatter: 在表面散布实例
        - array: 线性阵列
        - curve_to_mesh: 曲线转网格
        - instance_points: 点实例化
        
        Args:
            params: 对象名称、预设类型、参数
            
        Returns:
            应用结果
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
            return f"成功为 '{params.object_name}' 应用 {params.preset} 几何节点"
        else:
            return f"应用失败: {result.get('error', {}).get('message', '未知错误')}"
