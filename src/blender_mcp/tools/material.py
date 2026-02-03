"""
材质工具

提供材质创建、分配、属性设置等功能。
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum
import json

from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class BlendMode(str, Enum):
    """混合模式"""
    OPAQUE = "OPAQUE"
    CLIP = "CLIP"
    HASHED = "HASHED"
    BLEND = "BLEND"


class TextureType(str, Enum):
    """纹理类型"""
    COLOR = "COLOR"
    NORMAL = "NORMAL"
    ROUGHNESS = "ROUGHNESS"
    METALLIC = "METALLIC"
    EMISSION = "EMISSION"


class TextureMapping(str, Enum):
    """纹理映射方式"""
    UV = "UV"
    BOX = "BOX"
    SPHERE = "SPHERE"
    CYLINDER = "CYLINDER"


# ==================== 输入模型 ====================

class MaterialCreateInput(BaseModel):
    """创建材质输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="材质名称", min_length=1, max_length=100)
    color: Optional[List[float]] = Field(
        default=None,
        description="RGBA 颜色 [r, g, b, a]，值范围 0-1"
    )
    metallic: Optional[float] = Field(default=None, description="金属度", ge=0, le=1)
    roughness: Optional[float] = Field(default=None, description="粗糙度", ge=0, le=1)
    use_nodes: bool = Field(default=True, description="使用节点材质")
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is not None:
            if len(v) not in [3, 4]:
                raise ValueError("颜色必须包含 3 或 4 个分量")
            if any(c < 0 or c > 1 for c in v):
                raise ValueError("颜色分量必须在 0-1 范围内")
        return v


class MaterialAssignInput(BaseModel):
    """分配材质输入"""
    object_name: str = Field(..., description="对象名称")
    material_name: str = Field(..., description="材质名称")
    slot_index: int = Field(default=0, description="材质槽索引", ge=0)


class MaterialSetPropertiesInput(BaseModel):
    """设置材质属性输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    material_name: str = Field(..., description="材质名称")
    color: Optional[List[float]] = Field(default=None, description="RGBA 颜色")
    metallic: Optional[float] = Field(default=None, description="金属度", ge=0, le=1)
    roughness: Optional[float] = Field(default=None, description="粗糙度", ge=0, le=1)
    specular: Optional[float] = Field(default=None, description="高光强度", ge=0, le=1)
    emission_color: Optional[List[float]] = Field(default=None, description="自发光颜色")
    emission_strength: Optional[float] = Field(default=None, description="自发光强度", ge=0)
    alpha: Optional[float] = Field(default=None, description="透明度", ge=0, le=1)
    blend_mode: Optional[BlendMode] = Field(default=None, description="混合模式")


class MaterialAddTextureInput(BaseModel):
    """添加纹理输入"""
    material_name: str = Field(..., description="材质名称")
    texture_path: str = Field(..., description="纹理文件路径")
    texture_type: TextureType = Field(default=TextureType.COLOR, description="纹理类型")
    mapping: TextureMapping = Field(default=TextureMapping.UV, description="映射方式")


class MaterialListInput(BaseModel):
    """列出材质输入"""
    limit: int = Field(default=50, description="返回数量限制", ge=1, le=500)


class MaterialDeleteInput(BaseModel):
    """删除材质输入"""
    material_name: str = Field(..., description="材质名称")


# ==================== 工具注册 ====================

def register_material_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册材质工具"""
    
    @mcp.tool(
        name="blender_material_create",
        annotations={
            "title": "创建材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_material_create(params: MaterialCreateInput) -> str:
        """创建新材质。
        
        创建具有指定属性的 PBR 材质。
        
        Args:
            params: 材质名称和属性
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "material", "create",
            {
                "name": params.name,
                "color": params.color or [0.8, 0.8, 0.8, 1.0],
                "metallic": params.metallic if params.metallic is not None else 0.0,
                "roughness": params.roughness if params.roughness is not None else 0.5,
                "use_nodes": params.use_nodes
            }
        )
        
        if result.get("success"):
            return f"成功创建材质 '{params.name}'"
        else:
            return f"创建材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_assign",
        annotations={
            "title": "分配材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_material_assign(params: MaterialAssignInput) -> str:
        """将材质分配给对象。
        
        Args:
            params: 对象名称、材质名称、材质槽索引
            
        Returns:
            分配结果
        """
        result = await server.execute_command(
            "material", "assign",
            {
                "object_name": params.object_name,
                "material_name": params.material_name,
                "slot_index": params.slot_index
            }
        )
        
        if result.get("success"):
            return f"已将材质 '{params.material_name}' 分配给对象 '{params.object_name}'"
        else:
            return f"分配材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_set_properties",
        annotations={
            "title": "设置材质属性",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_material_set_properties(params: MaterialSetPropertiesInput) -> str:
        """设置材质属性。
        
        可以设置颜色、金属度、粗糙度、自发光等属性。
        
        Args:
            params: 材质名称和要设置的属性
            
        Returns:
            设置结果
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
            return "没有指定任何属性"
        
        result = await server.execute_command(
            "material", "set_properties",
            {"material_name": params.material_name, "properties": properties}
        )
        
        if result.get("success"):
            return f"材质 '{params.material_name}' 属性已更新"
        else:
            return f"设置材质属性失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_add_texture",
        annotations={
            "title": "添加纹理",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_material_add_texture(params: MaterialAddTextureInput) -> str:
        """为材质添加纹理。
        
        支持颜色、法线、粗糙度、金属度、自发光等纹理类型。
        
        Args:
            params: 材质名称、纹理路径、纹理类型
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "material", "add_texture",
            {
                "material_name": params.material_name,
                "texture_path": params.texture_path,
                "texture_type": params.texture_type.value,
                "mapping": params.mapping.value
            }
        )
        
        if result.get("success"):
            return f"已为材质 '{params.material_name}' 添加 {params.texture_type.value} 纹理"
        else:
            return f"添加纹理失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_list",
        annotations={
            "title": "列出材质",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_material_list(params: MaterialListInput) -> str:
        """列出所有材质。
        
        Args:
            params: 返回数量限制
            
        Returns:
            材质列表
        """
        result = await server.execute_command(
            "material", "list",
            {"limit": params.limit}
        )
        
        if not result.get("success"):
            return f"获取材质列表失败: {result.get('error', {}).get('message', '未知错误')}"
        
        materials = result.get("data", {}).get("materials", [])
        total = result.get("data", {}).get("total", len(materials))
        
        lines = ["# 材质列表", ""]
        lines.append(f"共 {total} 个材质")
        lines.append("")
        
        for mat in materials:
            lines.append(f"## {mat['name']}")
            if "color" in mat:
                lines.append(f"- 颜色: {mat['color']}")
            if "metallic" in mat:
                lines.append(f"- 金属度: {mat['metallic']}")
            if "roughness" in mat:
                lines.append(f"- 粗糙度: {mat['roughness']}")
            lines.append("")
        
        return "\n".join(lines)
    
    @mcp.tool(
        name="blender_material_delete",
        annotations={
            "title": "删除材质",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_material_delete(params: MaterialDeleteInput) -> str:
        """删除材质。
        
        Args:
            params: 材质名称
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "material", "delete",
            {"material_name": params.material_name}
        )
        
        if result.get("success"):
            return f"已删除材质 '{params.material_name}'"
        else:
            return f"删除材质失败: {result.get('error', {}).get('message', '未知错误')}"
