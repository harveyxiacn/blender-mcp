"""
角色模板工具

提供预设角色模板创建、面部系统、服装系统、发型系统等功能。
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 输入模型 ====================

class CharacterTemplateInput(BaseModel):
    """角色模板输入"""
    template: str = Field(
        default="chibi",
        description="模板类型: chibi(Q版), realistic(写实), anime(动漫), stylized(风格化), mascot(吉祥物)"
    )
    name: str = Field(default="Character", description="角色名称")
    height: float = Field(default=1.7, description="角色高度", ge=0.5, le=3.0)
    location: Optional[List[float]] = Field(default=None, description="位置")
    skin_color: Optional[List[float]] = Field(default=None, description="皮肤颜色 RGBA")
    gender: str = Field(default="neutral", description="性别: male, female, neutral")


class FaceExpressionInput(BaseModel):
    """面部表情输入"""
    character_name: str = Field(..., description="角色名称前缀")
    expression: str = Field(
        default="neutral",
        description="表情: neutral, happy, sad, angry, surprised, wink, smile"
    )
    intensity: float = Field(default=1.0, description="表情强度", ge=0.0, le=1.0)


class FaceSetupInput(BaseModel):
    """面部设置输入"""
    character_name: str = Field(..., description="角色名称前缀")
    eye_size: float = Field(default=1.0, description="眼睛大小", ge=0.5, le=2.0)
    eye_spacing: float = Field(default=1.0, description="眼睛间距", ge=0.5, le=1.5)
    mouth_width: float = Field(default=1.0, description="嘴巴宽度", ge=0.5, le=1.5)
    nose_size: float = Field(default=1.0, description="鼻子大小", ge=0.5, le=1.5)


class ClothingAddInput(BaseModel):
    """添加服装输入"""
    character_name: str = Field(..., description="角色名称前缀")
    clothing_type: str = Field(
        default="shirt",
        description="服装类型: shirt, pants, jacket, dress, uniform, sportswear"
    )
    color: Optional[List[float]] = Field(default=None, description="颜色 RGBA")
    style: str = Field(default="casual", description="风格: casual, formal, sport, fantasy")


class HairCreateInput(BaseModel):
    """创建发型输入"""
    character_name: str = Field(..., description="角色名称前缀")
    hair_style: str = Field(
        default="short",
        description="发型: short, medium, long, ponytail, braided, spiky, bald"
    )
    color: Optional[List[float]] = Field(default=None, description="发色 RGBA")
    volume: float = Field(default=1.0, description="蓬松度", ge=0.5, le=2.0)


class AccessoryAddInput(BaseModel):
    """添加配饰输入"""
    character_name: str = Field(..., description="角色名称前缀")
    accessory_type: str = Field(
        default="glasses",
        description="配饰类型: glasses, hat, earrings, necklace, watch, medal, badge"
    )
    color: Optional[List[float]] = Field(default=None, description="颜色 RGBA")
    location: str = Field(default="auto", description="位置: auto, head, neck, wrist, chest")


# ==================== 工具注册 ====================

def register_character_template_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册角色模板工具"""
    
    @mcp.tool(
        name="blender_character_template_create",
        annotations={
            "title": "从模板创建角色",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_template_create(params: CharacterTemplateInput) -> str:
        """从预设模板创建角色。
        
        支持的模板:
        - chibi: Q版可爱风格，大头小身体
        - realistic: 写实人体比例
        - anime: 动漫风格
        - stylized: 风格化卡通
        - mascot: 吉祥物风格
        
        Args:
            params: 模板类型、名称、尺寸等
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "character_template", "create",
            {
                "template": params.template,
                "name": params.name,
                "height": params.height,
                "location": params.location or [0, 0, 0],
                "skin_color": params.skin_color,
                "gender": params.gender
            }
        )
        
        if result.get("success"):
            parts = result.get("data", {}).get("parts_created", 0)
            return f"成功创建 {params.template} 风格角色 '{params.name}'，共 {parts} 个部件"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_face_expression",
        annotations={
            "title": "设置面部表情",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_face_expression(params: FaceExpressionInput) -> str:
        """设置角色面部表情。
        
        Args:
            params: 角色名称、表情类型、强度
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character_template", "face_expression",
            {
                "character_name": params.character_name,
                "expression": params.expression,
                "intensity": params.intensity
            }
        )
        
        if result.get("success"):
            return f"已将 '{params.character_name}' 的表情设置为 {params.expression}"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_face_setup",
        annotations={
            "title": "调整面部特征",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_character_face_setup(params: FaceSetupInput) -> str:
        """调整角色面部特征比例。
        
        Args:
            params: 眼睛大小、间距、嘴巴宽度等
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character_template", "face_setup",
            {
                "character_name": params.character_name,
                "eye_size": params.eye_size,
                "eye_spacing": params.eye_spacing,
                "mouth_width": params.mouth_width,
                "nose_size": params.nose_size
            }
        )
        
        if result.get("success"):
            return f"已调整 '{params.character_name}' 的面部特征"
        else:
            return f"调整失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_clothing_add",
        annotations={
            "title": "添加服装",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_clothing_add(params: ClothingAddInput) -> str:
        """为角色添加服装。
        
        Args:
            params: 服装类型、颜色、风格
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "character_template", "clothing_add",
            {
                "character_name": params.character_name,
                "clothing_type": params.clothing_type,
                "color": params.color,
                "style": params.style
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 添加 {params.clothing_type}"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_hair_create",
        annotations={
            "title": "创建发型",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_hair_create(params: HairCreateInput) -> str:
        """为角色创建发型。
        
        Args:
            params: 发型类型、颜色、蓬松度
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "character_template", "hair_create",
            {
                "character_name": params.character_name,
                "hair_style": params.hair_style,
                "color": params.color,
                "volume": params.volume
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 创建 {params.hair_style} 发型"
        else:
            return f"创建失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_character_accessory_add",
        annotations={
            "title": "添加配饰",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_character_accessory_add(params: AccessoryAddInput) -> str:
        """为角色添加配饰（眼镜、帽子、首饰等）。
        
        Args:
            params: 配饰类型、颜色、位置
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "character_template", "accessory_add",
            {
                "character_name": params.character_name,
                "accessory_type": params.accessory_type,
                "color": params.color,
                "location": params.location
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 添加 {params.accessory_type}"
        else:
            return f"添加失败: {result.get('error', {}).get('message', '未知错误')}"
