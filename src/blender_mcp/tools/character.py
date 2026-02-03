"""
角色系统工具

提供角色创建和编辑功能。
"""

from typing import TYPE_CHECKING, Optional
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


# ==================== 输入模型 ====================

class CharacterCreateHumanoidInput(BaseModel):
    """创建人形角色输入"""
    name: Optional[str] = Field(default="Character", description="角色名称")
    height: float = Field(default=1.8, description="身高（米）", ge=0.5, le=3.0)
    body_type: BodyType = Field(default=BodyType.AVERAGE, description="体型")
    gender: Gender = Field(default=Gender.NEUTRAL, description="性别")
    subdivisions: int = Field(default=2, description="细分级别", ge=0, le=4)


class CharacterAddFaceFeaturesInput(BaseModel):
    """添加面部特征输入"""
    character_name: str = Field(..., description="角色名称")
    eye_size: float = Field(default=1.0, description="眼睛大小", ge=0.5, le=1.5)
    nose_length: float = Field(default=1.0, description="鼻子长度", ge=0.5, le=1.5)
    mouth_width: float = Field(default=1.0, description="嘴宽度", ge=0.5, le=1.5)
    jaw_width: float = Field(default=1.0, description="下巴宽度", ge=0.5, le=1.5)


class CharacterAddHairInput(BaseModel):
    """添加头发输入"""
    character_name: str = Field(..., description="角色名称")
    hair_style: str = Field(default="SHORT", description="发型：SHORT, MEDIUM, LONG, BALD")
    hair_color: Optional[list] = Field(default=None, description="头发颜色 [r, g, b]")
    use_particles: bool = Field(default=True, description="使用粒子头发")


class CharacterAddClothingInput(BaseModel):
    """添加服装输入"""
    character_name: str = Field(..., description="角色名称")
    clothing_type: str = Field(..., description="服装类型：SHIRT, PANTS, JACKET, DRESS, SHOES")
    color: Optional[list] = Field(default=None, description="服装颜色 [r, g, b]")


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
        """创建人形基础网格。
        
        创建一个基础的人形角色网格，可以设置身高、体型和性别。
        
        Args:
            params: 角色名称和体型设置
            
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
                "subdivisions": params.subdivisions
            }
        )
        
        if result.get("success"):
            body_types = {"SLIM": "纤细", "AVERAGE": "普通", "MUSCULAR": "健壮", "HEAVY": "魁梧"}
            return f"成功创建角色 '{params.name}'，身高: {params.height}m，体型: {body_types.get(params.body_type.value)}"
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
        """调整角色的面部特征。
        
        可以调整眼睛大小、鼻子长度、嘴宽度等。
        
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
                "nose_length": params.nose_length,
                "mouth_width": params.mouth_width,
                "jaw_width": params.jaw_width
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 添加面部特征"
        else:
            return f"添加面部特征失败: {result.get('error', {}).get('message', '未知错误')}"
    
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
        """为角色添加头发系统。
        
        Args:
            params: 角色名称和头发设置
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "add_hair",
            {
                "character_name": params.character_name,
                "hair_style": params.hair_style,
                "hair_color": params.hair_color or [0.1, 0.08, 0.05],
                "use_particles": params.use_particles
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.character_name}' 添加头发"
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
        """为角色添加服装。
        
        支持的服装类型：SHIRT, PANTS, JACKET, DRESS, SHOES
        
        Args:
            params: 角色名称和服装设置
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "character", "add_clothing",
            {
                "character_name": params.character_name,
                "clothing_type": params.clothing_type,
                "color": params.color or [0.5, 0.5, 0.5]
            }
        )
        
        if result.get("success"):
            clothing_names = {
                "SHIRT": "上衣",
                "PANTS": "裤子",
                "JACKET": "夹克",
                "DRESS": "连衣裙",
                "SHOES": "鞋子"
            }
            return f"已为 '{params.character_name}' 添加{clothing_names.get(params.clothing_type, params.clothing_type)}"
        else:
            return f"添加服装失败: {result.get('error', {}).get('message', '未知错误')}"
