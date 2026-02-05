"""
角色系统工具

提供角色创建和编辑功能，包括高级面部系统、服装系统、发型系统等。
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class BodyType(str, Enum):
    """体型"""
    SLIM = "SLIM"
    AVERAGE = "AVERAGE"
    MUSCULAR = "MUSCULAR"
    HEAVY = "HEAVY"


class Gender(str, Enum):
    """性别"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"


class HairStyle(str, Enum):
    """发型"""
    BALD = "BALD"
    BUZZ = "BUZZ"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"
    VERY_LONG = "VERY_LONG"
    PONYTAIL = "PONYTAIL"
    BUN = "BUN"
    BRAIDS = "BRAIDS"
    MOHAWK = "MOHAWK"
    AFRO = "AFRO"
    CURLY = "CURLY"
    WAVY = "WAVY"
    ANCIENT_MALE = "ANCIENT_MALE"
    ANCIENT_FEMALE = "ANCIENT_FEMALE"
    TOPKNOT = "TOPKNOT"


class ClothingType(str, Enum):
    """服装类型"""
    SHIRT = "SHIRT"
    T_SHIRT = "T_SHIRT"
    PANTS = "PANTS"
    SHORTS = "SHORTS"
    JACKET = "JACKET"
    COAT = "COAT"
    DRESS = "DRESS"
    SKIRT = "SKIRT"
    ROBE = "ROBE"
    HANFU_TOP = "HANFU_TOP"
    HANFU_BOTTOM = "HANFU_BOTTOM"
    ARMOR_CHEST = "ARMOR_CHEST"
    ARMOR_FULL = "ARMOR_FULL"
    CAPE = "CAPE"
    SHOES = "SHOES"
    BOOTS = "BOOTS"
    GLOVES = "GLOVES"
    HAT = "HAT"
    HELMET = "HELMET"


class OutfitStyle(str, Enum):
    """套装风格"""
    CASUAL = "CASUAL"
    FORMAL = "FORMAL"
    WARRIOR = "WARRIOR"
    MAGE = "MAGE"
    HANFU = "HANFU"
    ANCIENT_WARRIOR = "ANCIENT_WARRIOR"
    NOBLE = "NOBLE"
    DANCER = "DANCER"


class Expression(str, Enum):
    """面部表情"""
    NEUTRAL = "neutral"
    SMILE = "smile"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEAR = "fear"
    DISGUST = "disgust"
    CONTEMPT = "contempt"


# ==================== 输入模型 ====================

class CharacterCreateHumanoidInput(BaseModel):
    """创建人形角色输入"""
    name: Optional[str] = Field(default="Character", description="角色名称")
    height: float = Field(default=1.8, description="身高（米）", ge=0.5, le=3.0)
    body_type: BodyType = Field(default=BodyType.AVERAGE, description="体型")
    gender: Gender = Field(default=Gender.NEUTRAL, description="性别")
    subdivisions: int = Field(default=2, description="细分级别", ge=0, le=4)
    create_face_rig: bool = Field(default=True, description="是否创建面部形态键")


class CharacterAddFaceFeaturesInput(BaseModel):
    """添加面部特征输入（增强版）"""
    character_name: str = Field(..., description="角色名称")
    # 眼睛参数
    eye_size: float = Field(default=1.0, description="眼睛大小", ge=0.5, le=1.5)
    eye_distance: float = Field(default=1.0, description="眼睛间距", ge=0.8, le=1.2)
    eye_height: float = Field(default=1.0, description="眼睛高度", ge=0.8, le=1.2)
    eye_tilt: float = Field(default=0.0, description="眼睛倾斜", ge=-0.3, le=0.3)
    eye_depth: float = Field(default=1.0, description="眼睛深度", ge=0.8, le=1.2)
    # 鼻子参数
    nose_length: float = Field(default=1.0, description="鼻子长度", ge=0.5, le=1.5)
    nose_width: float = Field(default=1.0, description="鼻子宽度", ge=0.7, le=1.3)
    nose_height: float = Field(default=1.0, description="鼻梁高度", ge=0.8, le=1.2)
    nose_tip: float = Field(default=1.0, description="鼻尖大小", ge=0.8, le=1.2)
    # 嘴巴参数
    mouth_width: float = Field(default=1.0, description="嘴宽度", ge=0.7, le=1.3)
    mouth_height: float = Field(default=1.0, description="嘴高度", ge=0.8, le=1.2)
    lip_thickness_upper: float = Field(default=1.0, description="上唇厚度", ge=0.5, le=1.5)
    lip_thickness_lower: float = Field(default=1.0, description="下唇厚度", ge=0.5, le=1.5)
    # 下巴和脸型参数
    jaw_width: float = Field(default=1.0, description="下巴宽度", ge=0.7, le=1.3)
    jaw_height: float = Field(default=1.0, description="下巴高度", ge=0.8, le=1.2)
    chin_length: float = Field(default=1.0, description="下巴长度", ge=0.8, le=1.2)
    cheekbone_height: float = Field(default=1.0, description="颧骨高度", ge=0.8, le=1.2)
    cheekbone_width: float = Field(default=1.0, description="颧骨宽度", ge=0.8, le=1.2)
    # 额头参数
    forehead_height: float = Field(default=1.0, description="额头高度", ge=0.8, le=1.2)
    forehead_width: float = Field(default=1.0, description="额头宽度", ge=0.8, le=1.2)
    # 耳朵参数
    ear_size: float = Field(default=1.0, description="耳朵大小", ge=0.7, le=1.3)
    ear_position: float = Field(default=1.0, description="耳朵位置", ge=0.8, le=1.2)


class CharacterSetExpressionInput(BaseModel):
    """设置面部表情输入"""
    character_name: str = Field(..., description="角色名称")
    expression: Expression = Field(default=Expression.NEUTRAL, description="表情类型")
    intensity: float = Field(default=1.0, description="表情强度", ge=0.0, le=1.0)


class CharacterAddHairInput(BaseModel):
    """添加头发输入（增强版）"""
    character_name: str = Field(..., description="角色名称")
    hair_style: HairStyle = Field(default=HairStyle.SHORT, description="发型")
    hair_color: Optional[List[float]] = Field(default=None, description="头发颜色 [r, g, b]")
    use_particles: bool = Field(default=True, description="使用粒子头发")
    hair_density: float = Field(default=1.0, description="头发密度倍率", ge=0.1, le=3.0)
    hair_thickness: float = Field(default=1.0, description="头发粗细倍率", ge=0.5, le=2.0)
    use_dynamics: bool = Field(default=False, description="启用头发动力学")


class CharacterAddClothingInput(BaseModel):
    """添加服装输入（增强版）"""
    character_name: str = Field(..., description="角色名称")
    clothing_type: ClothingType = Field(..., description="服装类型")
    color: Optional[List[float]] = Field(default=None, description="服装主色 [r, g, b]")
    secondary_color: Optional[List[float]] = Field(default=None, description="服装次色 [r, g, b]")
    use_cloth_simulation: bool = Field(default=False, description="启用布料模拟")
    metallic: float = Field(default=0.0, description="金属度", ge=0.0, le=1.0)
    roughness: float = Field(default=0.8, description="粗糙度", ge=0.0, le=1.0)
    pattern: Optional[str] = Field(default=None, description="图案: SOLID, STRIPES, PLAID, FLORAL")


class CharacterCreateOutfitInput(BaseModel):
    """创建完整套装输入"""
    character_name: str = Field(..., description="角色名称")
    outfit_style: OutfitStyle = Field(default=OutfitStyle.CASUAL, description="套装风格")
    color_scheme: str = Field(default="DEFAULT", description="颜色方案: DEFAULT, RED, BLUE, GREEN, WHITE, BLACK, GOLD, PURPLE")
    use_cloth_simulation: bool = Field(default=False, description="启用布料模拟")


# ==================== 工具注册 ====================

def register_character_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册角色系统工具"""
    
    @mcp.tool(
        name="blender_character_create_humanoid",
        annotations={
            "title": "创建人形角色",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_create_humanoid(params: CharacterCreateHumanoidInput) -> str:
        """创建人形基础网格（增强版）。
        
        创建一个详细的人形角色网格，包含：
        - 可调节的身高、体型和性别
        - 面部形态键系统
        - 身体顶点组（用于服装绑定）
        
        Args:
            params: 角色名称、体型设置、是否创建面部系统
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "character", "create_humanoid",
            {
                "name": params.name,
                "height": params.height,
                "body_type": params.body_type.value,
                "gender": params.gender.value,
                "subdivisions": params.subdivisions,
                "create_face_rig": params.create_face_rig
            }
        )
        
        if result.get("success"):
            body_types = {"SLIM": "纤细", "AVERAGE": "普通", "MUSCULAR": "健壮", "HEAVY": "魁梧"}
            data = result.get("data", {})
            face_info = "（含面部系统）" if data.get("has_face_rig") else ""
            return f"成功创建角色 '{params.name}'，身高: {params.height}m，体型: {body_types.get(params.body_type.value)}{face_info}"
        else:
            return f"创建角色失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_add_face_features",
        annotations={
            "title": "添加面部特征",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_add_face_features(params: CharacterAddFaceFeaturesInput) -> str:
        """调整角色的面部特征（增强版 - 使用形态键）。
        
        支持22个面部参数的精细调节：
        - 眼睛：大小、间距、高度、倾斜、深度
        - 鼻子：长度、宽度、高度、鼻尖
        - 嘴巴：宽度、高度、上下唇厚度
        - 脸型：下巴宽高、颧骨、额头
        - 耳朵：大小、位置
        
        Args:
            params: 角色名称和面部参数
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "add_face_features",
            {
                "character_name": params.character_name,
                "eye_size": params.eye_size,
                "eye_distance": params.eye_distance,
                "eye_height": params.eye_height,
                "eye_tilt": params.eye_tilt,
                "eye_depth": params.eye_depth,
                "nose_length": params.nose_length,
                "nose_width": params.nose_width,
                "nose_height": params.nose_height,
                "nose_tip": params.nose_tip,
                "mouth_width": params.mouth_width,
                "mouth_height": params.mouth_height,
                "lip_thickness_upper": params.lip_thickness_upper,
                "lip_thickness_lower": params.lip_thickness_lower,
                "jaw_width": params.jaw_width,
                "jaw_height": params.jaw_height,
                "chin_length": params.chin_length,
                "cheekbone_height": params.cheekbone_height,
                "cheekbone_width": params.cheekbone_width,
                "forehead_height": params.forehead_height,
                "forehead_width": params.forehead_width,
                "ear_size": params.ear_size,
                "ear_position": params.ear_position
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            count = len(data.get("applied_params", []))
            return f"已为 '{params.character_name}' 调整 {count} 个面部参数"
        else:
            return f"添加面部特征失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_set_expression",
        annotations={
            "title": "设置面部表情",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_set_expression(params: CharacterSetExpressionInput) -> str:
        """设置角色面部表情。
        
        支持的表情：
        - neutral: 中性
        - smile: 微笑
        - sad: 悲伤
        - angry: 愤怒
        - surprised: 惊讶
        - fear: 恐惧
        - disgust: 厌恶
        - contempt: 蔑视
        
        Args:
            params: 角色名称、表情类型、强度
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "set_face_expression",
            {
                "character_name": params.character_name,
                "expression": params.expression.value,
                "intensity": params.intensity
            }
        )
        
        expr_names = {
            "neutral": "中性", "smile": "微笑", "sad": "悲伤",
            "angry": "愤怒", "surprised": "惊讶", "fear": "恐惧",
            "disgust": "厌恶", "contempt": "蔑视"
        }
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 设置{expr_names.get(params.expression.value, params.expression.value)}表情（强度: {params.intensity:.0%}）"
        else:
            return f"设置表情失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_add_hair",
        annotations={
            "title": "添加头发",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_add_hair(params: CharacterAddHairInput) -> str:
        """为角色添加头发系统（增强版）。
        
        支持16种发型预设，包括：
        - 基础发型：BALD, BUZZ, SHORT, MEDIUM, LONG, VERY_LONG
        - 特殊发型：PONYTAIL, BUN, BRAIDS, MOHAWK, AFRO
        - 卷发类型：CURLY, WAVY
        - 古风发型：ANCIENT_MALE, ANCIENT_FEMALE, TOPKNOT
        
        Args:
            params: 角色名称、发型、颜色、密度、动力学等
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "add_hair",
            {
                "character_name": params.character_name,
                "hair_style": params.hair_style.value,
                "hair_color": params.hair_color or [0.1, 0.08, 0.05],
                "use_particles": params.use_particles,
                "hair_density": params.hair_density,
                "hair_thickness": params.hair_thickness,
                "use_dynamics": params.use_dynamics
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            dyn_info = "（启用动力学）" if data.get("dynamics_enabled") else ""
            return f"已为 '{params.character_name}' 添加 {params.hair_style.value} 发型{dyn_info}"
        else:
            return f"添加头发失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_add_clothing",
        annotations={
            "title": "添加服装",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_add_clothing(params: CharacterAddClothingInput) -> str:
        """为角色添加服装（增强版）。
        
        支持19种服装类型：
        - 上装：SHIRT, T_SHIRT, JACKET, COAT
        - 下装：PANTS, SHORTS, SKIRT
        - 连体：DRESS, ROBE
        - 古风：HANFU_TOP, HANFU_BOTTOM
        - 盔甲：ARMOR_CHEST, ARMOR_FULL, HELMET
        - 配件：CAPE, SHOES, BOOTS, GLOVES, HAT
        
        Args:
            params: 角色名称、服装类型、颜色、布料模拟等
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "add_clothing",
            {
                "character_name": params.character_name,
                "clothing_type": params.clothing_type.value,
                "color": params.color or [0.5, 0.5, 0.5],
                "secondary_color": params.secondary_color,
                "use_cloth_simulation": params.use_cloth_simulation,
                "metallic": params.metallic,
                "roughness": params.roughness,
                "pattern": params.pattern
            }
        )
        
        clothing_names = {
            "SHIRT": "衬衫", "T_SHIRT": "T恤", "PANTS": "长裤",
            "SHORTS": "短裤", "JACKET": "夹克", "COAT": "大衣",
            "DRESS": "连衣裙", "SKIRT": "裙子", "ROBE": "长袍",
            "HANFU_TOP": "汉服上衣", "HANFU_BOTTOM": "汉服下裳",
            "ARMOR_CHEST": "胸甲", "ARMOR_FULL": "全身盔甲",
            "CAPE": "披风", "SHOES": "鞋子", "BOOTS": "靴子",
            "GLOVES": "手套", "HAT": "帽子", "HELMET": "头盔"
        }
        
        if result.get("success"):
            data = result.get("data", {})
            cloth_info = "（启用布料模拟）" if data.get("cloth_simulation") else ""
            name = clothing_names.get(params.clothing_type.value, params.clothing_type.value)
            return f"已为 '{params.character_name}' 添加{name}{cloth_info}"
        else:
            return f"添加服装失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_create_outfit",
        annotations={
            "title": "创建完整套装",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_create_outfit(params: CharacterCreateOutfitInput) -> str:
        """为角色创建完整套装。
        
        支持8种套装风格：
        - CASUAL: 休闲装（T恤+长裤+鞋子）
        - FORMAL: 正装（衬衫+长裤+鞋子）
        - WARRIOR: 战士装（胸甲+长裤+靴子+手套）
        - MAGE: 法师装（长袍+靴子+手套+帽子）
        - HANFU: 汉服（上衣+下裳+鞋子）
        - ANCIENT_WARRIOR: 古代战士（全身盔甲+靴子+头盔）
        - NOBLE: 贵族装（夹克+长裤+靴子+披风）
        - DANCER: 舞者装（连衣裙+鞋子）
        
        颜色方案：DEFAULT, RED, BLUE, GREEN, WHITE, BLACK, GOLD, PURPLE
        
        Args:
            params: 角色名称、套装风格、颜色方案、布料模拟
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "create_outfit",
            {
                "character_name": params.character_name,
                "outfit_style": params.outfit_style.value,
                "color_scheme": params.color_scheme,
                "use_cloth_simulation": params.use_cloth_simulation
            }
        )
        
        style_names = {
            "CASUAL": "休闲装", "FORMAL": "正装", "WARRIOR": "战士装",
            "MAGE": "法师装", "HANFU": "汉服", "ANCIENT_WARRIOR": "古代战士装",
            "NOBLE": "贵族装", "DANCER": "舞者装"
        }
        
        if result.get("success"):
            data = result.get("data", {})
            items = data.get("items_created", [])
            name = style_names.get(params.outfit_style.value, params.outfit_style.value)
            return f"已为 '{params.character_name}' 创建{name}套装，包含 {len(items)} 件服装"
        else:
            return f"创建套装失败: {result.get('error', {}).get('message', '未知错误')}"
