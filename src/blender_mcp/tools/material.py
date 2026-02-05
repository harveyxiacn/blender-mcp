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


class NodeType(str, Enum):
    """节点类型"""
    SSS = "SSS"                     # 次表面散射配置
    EMISSION = "EMISSION"           # 发光配置
    MIX_RGB = "MIX_RGB"             # 混合 RGB
    COLOR_RAMP = "COLOR_RAMP"       # 颜色渐变
    NOISE_TEXTURE = "NOISE_TEXTURE" # 噪波纹理
    IMAGE_TEXTURE = "IMAGE_TEXTURE" # 图像纹理
    NORMAL_MAP = "NORMAL_MAP"       # 法线贴图
    BUMP = "BUMP"                   # 凹凸贴图


class MaterialNodeAddInput(BaseModel):
    """添加材质节点输入"""
    material_name: str = Field(..., description="材质名称")
    node_type: NodeType = Field(..., description="节点类型")
    settings: Optional[dict] = Field(
        default=None,
        description="节点设置（如 SSS: {subsurface: 0.3}, EMISSION: {color: [1,1,1], strength: 1.0}）"
    )
    connect_to: Optional[dict] = Field(
        default=None,
        description="连接配置 {input: 'Base Color', output: 'Color'}"
    )
    location: Optional[List[float]] = Field(default=None, description="节点位置 [x, y]")


class TextureApplyInput(BaseModel):
    """应用纹理贴图输入"""
    material_name: str = Field(..., description="材质名称")
    image_path: str = Field(..., description="图片文件路径")
    mapping_type: TextureMapping = Field(default=TextureMapping.UV, description="映射类型")
    texture_type: TextureType = Field(default=TextureType.COLOR, description="纹理用途")


class SkinTone(str, Enum):
    """肤色类型"""
    LIGHT = "LIGHT"     # 浅肤色
    MEDIUM = "MEDIUM"   # 中等肤色
    DARK = "DARK"       # 深肤色
    CUSTOM = "CUSTOM"   # 自定义


class CreateSkinMaterialInput(BaseModel):
    """创建皮肤材质输入"""
    name: str = Field(default="SkinMaterial", description="材质名称")
    skin_tone: SkinTone = Field(default=SkinTone.MEDIUM, description="肤色类型")
    custom_color: Optional[List[float]] = Field(
        default=None,
        description="自定义颜色（当 skin_tone 为 CUSTOM 时使用）"
    )


class CreateToonMaterialInput(BaseModel):
    """创建卡通材质输入"""
    name: str = Field(default="ToonMaterial", description="材质名称")
    color: List[float] = Field(default=[0.8, 0.8, 0.8, 1.0], description="基础颜色")
    shadow_color: Optional[List[float]] = Field(default=None, description="阴影颜色")
    outline: bool = Field(default=False, description="是否添加描边效果")


# ==================== 生产标准优化输入模型 ====================

class GameEngine(str, Enum):
    """目标游戏引擎"""
    UNITY = "UNITY"                 # Unity引擎
    UNREAL = "UNREAL"               # Unreal引擎
    GODOT = "GODOT"                 # Godot引擎
    GENERIC = "GENERIC"             # 通用glTF
    BLENDER = "BLENDER"             # Blender Eevee/Cycles


class MaterialAnalyzeInput(BaseModel):
    """材质分析输入"""
    material_name: str = Field(..., description="材质名称")
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="目标游戏引擎")


class MaterialOptimizeInput(BaseModel):
    """材质优化输入"""
    material_name: str = Field(..., description="材质名称")
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="目标游戏引擎")
    fix_metallic: bool = Field(default=True, description="修复金属度值（确保为0或1）")
    fix_color_space: bool = Field(default=True, description="修复纹理色彩空间")
    combine_textures: bool = Field(default=False, description="合并纹理通道（ORM/RMA）")


class PBRMaterialCreateInput(BaseModel):
    """创建标准PBR材质输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="材质名称", min_length=1, max_length=100)
    target_engine: GameEngine = Field(default=GameEngine.GENERIC, description="目标游戏引擎")
    
    # PBR基础属性
    base_color: Optional[List[float]] = Field(
        default=None,
        description="基础颜色 [r, g, b, a]，值范围 0-1"
    )
    metallic: float = Field(default=0.0, description="金属度（生产标准：0=非金属，1=金属）", ge=0, le=1)
    roughness: float = Field(default=0.5, description="粗糙度", ge=0, le=1)
    
    # 纹理路径（可选）
    base_color_texture: Optional[str] = Field(default=None, description="基础颜色贴图路径")
    normal_texture: Optional[str] = Field(default=None, description="法线贴图路径")
    metallic_texture: Optional[str] = Field(default=None, description="金属度贴图路径")
    roughness_texture: Optional[str] = Field(default=None, description="粗糙度贴图路径")
    ao_texture: Optional[str] = Field(default=None, description="环境光遮蔽贴图路径")
    emission_texture: Optional[str] = Field(default=None, description="自发光贴图路径")
    
    # 额外设置
    emission_strength: float = Field(default=0.0, description="自发光强度", ge=0)
    alpha_mode: BlendMode = Field(default=BlendMode.OPAQUE, description="透明度模式")
    double_sided: bool = Field(default=False, description="双面渲染")
    
    @field_validator("base_color")
    @classmethod
    def validate_base_color(cls, v):
        if v is not None:
            if len(v) not in [3, 4]:
                raise ValueError("颜色必须包含 3 或 4 个分量")
            if any(c < 0 or c > 1 for c in v):
                raise ValueError("颜色分量必须在 0-1 范围内")
        return v


class TextureColorSpaceInput(BaseModel):
    """纹理色彩空间设置输入"""
    material_name: str = Field(..., description="材质名称")
    auto_detect: bool = Field(default=True, description="自动检测并修复色彩空间")


class MaterialBakeTexturesInput(BaseModel):
    """烘焙材质纹理输入"""
    material_name: str = Field(..., description="材质名称")
    output_directory: str = Field(..., description="输出目录路径")
    resolution: int = Field(default=1024, description="纹理分辨率", ge=64, le=8192)
    bake_types: List[str] = Field(
        default=["DIFFUSE", "ROUGHNESS", "NORMAL"],
        description="烘焙类型列表：DIFFUSE, ROUGHNESS, METALLIC, NORMAL, AO, EMISSION"
    )


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
    
    @mcp.tool(
        name="blender_material_node_add",
        annotations={
            "title": "添加材质节点",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_material_node_add(params: MaterialNodeAddInput) -> str:
        """添加高级材质节点。
        
        支持 SSS（次表面散射）、Emission（发光）等节点，
        用于创建皮肤材质或发光的乒乓球等效果。
        
        Args:
            params: 材质名称、节点类型、设置
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "material", "node_add",
            {
                "material_name": params.material_name,
                "node_type": params.node_type.value,
                "settings": params.settings or {},
                "connect_to": params.connect_to,
                "location": params.location or [-300, 0]
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已为材质 '{params.material_name}' 添加 {params.node_type.value} 节点"
        else:
            return f"添加节点失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_texture_apply",
        annotations={
            "title": "应用纹理贴图",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_texture_apply(params: TextureApplyInput) -> str:
        """应用纹理贴图到材质。
        
        支持多种纹理类型和映射方式，可用于添加国旗、队服Logo等。
        
        Args:
            params: 材质名称、图片路径、映射类型、纹理用途
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "material", "texture_apply",
            {
                "material_name": params.material_name,
                "image_path": params.image_path,
                "mapping_type": params.mapping_type.value,
                "texture_type": params.texture_type.value
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已将纹理 '{data.get('image_name', 'N/A')}' 应用到材质 '{params.material_name}'"
        else:
            return f"应用纹理失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_create_skin_material",
        annotations={
            "title": "创建皮肤材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_create_skin_material(params: CreateSkinMaterialInput) -> str:
        """创建预设的皮肤材质。
        
        包含次表面散射（SSS）效果，适用于 Q 版角色皮肤。
        
        Args:
            params: 材质名称、肤色类型
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "material", "create_skin_material",
            {
                "name": params.name,
                "skin_tone": params.skin_tone.value,
                "custom_color": params.custom_color
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            tone_names = {
                "LIGHT": "浅肤色",
                "MEDIUM": "中等肤色",
                "DARK": "深肤色",
                "CUSTOM": "自定义"
            }
            return f"已创建{tone_names.get(params.skin_tone.value)}皮肤材质 '{data.get('material_name', params.name)}'"
        else:
            return f"创建皮肤材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_create_toon_material",
        annotations={
            "title": "创建卡通材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_create_toon_material(params: CreateToonMaterialInput) -> str:
        """创建卡通风格材质。
        
        适用于 Q 版角色的风格化卡通渲染。
        
        Args:
            params: 材质名称、颜色、描边选项
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "material", "create_toon_material",
            {
                "name": params.name,
                "color": params.color,
                "shadow_color": params.shadow_color,
                "outline": params.outline
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已创建卡通材质 '{data.get('material_name', params.name)}'"
        else:
            return f"创建卡通材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    # ==================== 生产标准优化工具 ====================
    
    @mcp.tool(
        name="blender_material_analyze",
        annotations={
            "title": "PBR材质分析",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_material_analyze(params: MaterialAnalyzeInput) -> str:
        """分析材质是否符合PBR生产标准。
        
        检查材质的PBR参数是否符合游戏引擎最佳实践：
        - 金属度是否为0或1（生产标准）
        - 纹理色彩空间是否正确
        - 法线贴图设置是否正确
        - 是否符合目标引擎要求
        
        Args:
            params: 材质名称和目标引擎
            
        Returns:
            详细的材质分析报告
        """
        result = await server.execute_command(
            "material", "analyze",
            {
                "material_name": params.material_name,
                "target_engine": params.target_engine.value
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            lines = [f"# PBR材质分析报告: {params.material_name}", ""]
            
            # 基础信息
            lines.append("## 基础信息")
            lines.append(f"- 使用节点: {'是' if data.get('uses_nodes') else '否'}")
            lines.append(f"- 目标引擎: {params.target_engine.value}")
            lines.append("")
            
            # PBR参数
            pbr = data.get("pbr_values", {})
            lines.append("## PBR参数")
            lines.append(f"- 金属度: {pbr.get('metallic', 'N/A')}")
            lines.append(f"- 粗糙度: {pbr.get('roughness', 'N/A')}")
            lines.append(f"- 基础颜色: {pbr.get('base_color', 'N/A')}")
            lines.append("")
            
            # 纹理信息
            textures = data.get("textures", [])
            if textures:
                lines.append("## 纹理列表")
                for tex in textures:
                    lines.append(f"- {tex.get('name', 'Unknown')}")
                    lines.append(f"  - 类型: {tex.get('type', 'N/A')}")
                    lines.append(f"  - 色彩空间: {tex.get('colorspace', 'N/A')}")
                    correct = tex.get('colorspace_correct', True)
                    lines.append(f"  - 色彩空间正确: {'是' if correct else '否 ⚠️'}")
                lines.append("")
            
            # 问题和建议
            issues = data.get("issues", [])
            if issues:
                lines.append("## ⚠️ 发现的问题")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")
            
            suggestions = data.get("suggestions", [])
            if suggestions:
                lines.append("## 💡 优化建议")
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")
                lines.append("")
            
            # 兼容性评分
            score = data.get("compatibility_score", 0)
            lines.append(f"## 兼容性评分: {score}/100")
            
            return "\n".join(lines)
        else:
            return f"分析失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_optimize",
        annotations={
            "title": "优化PBR材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_material_optimize(params: MaterialOptimizeInput) -> str:
        """优化材质以符合游戏引擎PBR标准。
        
        自动修复常见问题：
        - 将金属度值修正为0或1
        - 修复纹理色彩空间（法线/粗糙度等使用Non-Color）
        - 针对目标引擎优化设置
        
        Args:
            params: 材质名称和优化选项
            
        Returns:
            优化结果
        """
        result = await server.execute_command(
            "material", "optimize",
            {
                "material_name": params.material_name,
                "target_engine": params.target_engine.value,
                "fix_metallic": params.fix_metallic,
                "fix_color_space": params.fix_color_space,
                "combine_textures": params.combine_textures
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            fixes = data.get("fixes_applied", [])
            
            lines = [f"材质 '{params.material_name}' 优化完成", ""]
            
            if fixes:
                lines.append("已应用的修复:")
                for fix in fixes:
                    lines.append(f"- {fix}")
            else:
                lines.append("材质已符合标准，无需修复。")
            
            return "\n".join(lines)
        else:
            return f"优化失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_pbr_material_create",
        annotations={
            "title": "创建标准PBR材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_pbr_material_create(params: PBRMaterialCreateInput) -> str:
        """创建符合生产标准的PBR材质。
        
        按照游戏引擎最佳实践创建材质：
        - 自动设置正确的色彩空间
        - 金属度遵循0/1规则
        - 支持完整的PBR纹理工作流
        
        Args:
            params: PBR材质参数和纹理路径
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "material", "create_pbr",
            {
                "name": params.name,
                "target_engine": params.target_engine.value,
                "base_color": params.base_color or [0.8, 0.8, 0.8, 1.0],
                "metallic": params.metallic,
                "roughness": params.roughness,
                "base_color_texture": params.base_color_texture,
                "normal_texture": params.normal_texture,
                "metallic_texture": params.metallic_texture,
                "roughness_texture": params.roughness_texture,
                "ao_texture": params.ao_texture,
                "emission_texture": params.emission_texture,
                "emission_strength": params.emission_strength,
                "alpha_mode": params.alpha_mode.value,
                "double_sided": params.double_sided
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            textures_loaded = data.get("textures_loaded", [])
            
            lines = [f"成功创建PBR材质 '{params.name}'", ""]
            lines.append(f"- 目标引擎: {params.target_engine.value}")
            lines.append(f"- 金属度: {params.metallic}")
            lines.append(f"- 粗糙度: {params.roughness}")
            
            if textures_loaded:
                lines.append("")
                lines.append("已加载纹理:")
                for tex in textures_loaded:
                    lines.append(f"- {tex}")
            
            return "\n".join(lines)
        else:
            return f"创建PBR材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_texture_colorspace_fix",
        annotations={
            "title": "修复纹理色彩空间",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_texture_colorspace_fix(params: TextureColorSpaceInput) -> str:
        """自动修复材质中纹理的色彩空间设置。
        
        根据纹理用途自动设置正确的色彩空间：
        - 颜色贴图: sRGB
        - 法线/粗糙度/金属度: Non-Color
        
        Args:
            params: 材质名称
            
        Returns:
            修复结果
        """
        result = await server.execute_command(
            "material", "fix_colorspace",
            {
                "material_name": params.material_name,
                "auto_detect": params.auto_detect
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            fixed = data.get("fixed_textures", [])
            
            if fixed:
                lines = ["已修复以下纹理的色彩空间:"]
                for tex in fixed:
                    lines.append(f"- {tex.get('name')}: {tex.get('old_space')} → {tex.get('new_space')}")
                return "\n".join(lines)
            else:
                return "所有纹理色彩空间已正确设置，无需修复。"
        else:
            return f"修复失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_material_bake_textures",
        annotations={
            "title": "烘焙材质纹理",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True
        }
    )
    async def blender_material_bake_textures(params: MaterialBakeTexturesInput) -> str:
        """将程序化材质烘焙为纹理图像。
        
        支持烘焙：漫反射、粗糙度、金属度、法线、AO、自发光。
        烘焙后的纹理可导出到游戏引擎使用。
        
        Args:
            params: 材质名称、输出目录、分辨率、烘焙类型
            
        Returns:
            烘焙结果
        """
        result = await server.execute_command(
            "material", "bake_textures",
            {
                "material_name": params.material_name,
                "output_directory": params.output_directory,
                "resolution": params.resolution,
                "bake_types": params.bake_types
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            baked = data.get("baked_textures", [])
            
            lines = [f"材质 '{params.material_name}' 纹理烘焙完成", ""]
            lines.append(f"输出目录: {params.output_directory}")
            lines.append(f"分辨率: {params.resolution}x{params.resolution}")
            lines.append("")
            
            if baked:
                lines.append("已烘焙的纹理:")
                for tex in baked:
                    lines.append(f"- {tex}")
            
            return "\n".join(lines)
        else:
            return f"烘焙失败: {result.get('error', {}).get('message', '未知错误')}"
