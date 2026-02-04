"""
建模工具

提供网格编辑、修改器等建模功能。
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class SelectMode(str, Enum):
    """选择模式"""
    VERT = "VERT"
    EDGE = "EDGE"
    FACE = "FACE"


class SelectAction(str, Enum):
    """选择操作"""
    ALL = "ALL"
    NONE = "NONE"
    INVERT = "INVERT"
    RANDOM = "RANDOM"
    LINKED = "LINKED"


class ModifierType(str, Enum):
    """修改器类型"""
    SUBSURF = "SUBSURF"
    MIRROR = "MIRROR"
    ARRAY = "ARRAY"
    BEVEL = "BEVEL"
    SOLIDIFY = "SOLIDIFY"
    BOOLEAN = "BOOLEAN"
    ARMATURE = "ARMATURE"
    SKIN = "SKIN"
    DECIMATE = "DECIMATE"
    SMOOTH = "SMOOTH"
    DISPLACE = "DISPLACE"
    SHRINKWRAP = "SHRINKWRAP"


class BooleanOperation(str, Enum):
    """布尔运算类型"""
    UNION = "UNION"
    DIFFERENCE = "DIFFERENCE"
    INTERSECT = "INTERSECT"


# ==================== 输入模型 ====================

class MeshEditModeInput(BaseModel):
    """编辑模式输入"""
    object_name: str = Field(..., description="对象名称")
    enter: bool = Field(default=True, description="true=进入，false=退出")


class MeshSelectInput(BaseModel):
    """网格选择输入"""
    object_name: str = Field(..., description="对象名称")
    select_mode: SelectMode = Field(default=SelectMode.VERT, description="选择模式")
    action: SelectAction = Field(..., description="选择操作")
    random_ratio: float = Field(default=0.5, description="随机选择比例", ge=0, le=1)


class MeshExtrudeInput(BaseModel):
    """挤出输入"""
    object_name: str = Field(..., description="对象名称")
    direction: Optional[List[float]] = Field(default=None, description="挤出方向向量")
    distance: float = Field(default=1.0, description="挤出距离")
    use_normal: bool = Field(default=True, description="沿法线方向")


class MeshSubdivideInput(BaseModel):
    """细分输入"""
    object_name: str = Field(..., description="对象名称")
    cuts: int = Field(default=1, description="切割次数", ge=1, le=100)
    smoothness: float = Field(default=0.0, description="平滑度", ge=0, le=1)


class MeshBevelInput(BaseModel):
    """倒角输入"""
    object_name: str = Field(..., description="对象名称")
    width: float = Field(default=0.1, description="倒角宽度", gt=0)
    segments: int = Field(default=1, description="分段数", ge=1, le=100)
    profile: float = Field(default=0.5, description="轮廓形状", ge=0, le=1)
    affect: str = Field(default="EDGES", description="影响：VERTICES, EDGES")


class MeshLoopCutInput(BaseModel):
    """环切输入"""
    object_name: str = Field(..., description="对象名称")
    number_cuts: int = Field(default=1, description="切割数量", ge=1, le=100)
    smoothness: float = Field(default=0.0, description="平滑度", ge=0, le=1)
    edge_index: Optional[int] = Field(default=None, description="边索引")


class ModifierAddInput(BaseModel):
    """添加修改器输入"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    object_name: str = Field(..., description="对象名称")
    modifier_type: ModifierType = Field(..., description="修改器类型")
    modifier_name: Optional[str] = Field(default=None, description="修改器名称")
    settings: Optional[dict] = Field(default=None, description="修改器设置")


class ModifierApplyInput(BaseModel):
    """应用修改器输入"""
    object_name: str = Field(..., description="对象名称")
    modifier_name: str = Field(..., description="修改器名称")


class ModifierRemoveInput(BaseModel):
    """移除修改器输入"""
    object_name: str = Field(..., description="对象名称")
    modifier_name: str = Field(..., description="修改器名称")


class BooleanOperationInput(BaseModel):
    """布尔运算输入"""
    object_name: str = Field(..., description="主对象名称")
    target_name: str = Field(..., description="目标对象名称")
    operation: BooleanOperation = Field(..., description="运算类型")
    apply: bool = Field(default=True, description="是否立即应用")
    hide_target: bool = Field(default=True, description="隐藏目标对象")


# ==================== 形态键输入模型 ====================

class ShapeKeyCreateInput(BaseModel):
    """创建形态键输入"""
    object_name: str = Field(..., description="对象名称")
    key_name: str = Field(default="Key", description="形态键名称")
    from_mix: bool = Field(default=False, description="从当前混合状态创建")


class ShapeKeyEditInput(BaseModel):
    """编辑形态键输入"""
    object_name: str = Field(..., description="对象名称")
    key_name: str = Field(..., description="形态键名称")
    value: Optional[float] = Field(default=None, description="形态键值 (0.0-1.0)", ge=0, le=1)
    mute: Optional[bool] = Field(default=None, description="是否静音")
    vertex_offsets: Optional[List[dict]] = Field(
        default=None,
        description="顶点偏移列表 [{\"index\": int, \"offset\": [x, y, z]}, ...]"
    )


class ShapeKeyDeleteInput(BaseModel):
    """删除形态键输入"""
    object_name: str = Field(..., description="对象名称")
    key_name: str = Field(..., description="形态键名称")


class ShapeKeyListInput(BaseModel):
    """列出形态键输入"""
    object_name: str = Field(..., description="对象名称")


class ExpressionType(str, Enum):
    """表情类型"""
    SMILE = "smile"
    FROWN = "frown"
    SURPRISE = "surprise"
    ANGRY = "angry"
    SAD = "sad"
    BLINK_L = "blink_l"
    BLINK_R = "blink_r"
    BLINK = "blink"
    MOUTH_OPEN = "mouth_open"
    MOUTH_WIDE = "mouth_wide"


class ShapeKeyCreateExpressionInput(BaseModel):
    """创建表情形态键集输入"""
    object_name: str = Field(..., description="对象名称")
    expressions: List[ExpressionType] = Field(
        default=[ExpressionType.SMILE, ExpressionType.BLINK, ExpressionType.SURPRISE, ExpressionType.ANGRY],
        description="要创建的表情类型列表"
    )


class MeshAssignMaterialToFacesInput(BaseModel):
    """给特定面分配材质输入"""
    object_name: str = Field(..., description="对象名称")
    face_indices: List[int] = Field(..., description="面索引列表")
    material_slot: Optional[int] = Field(default=None, description="材质槽索引")
    material_name: Optional[str] = Field(default=None, description="材质名称（与material_slot二选一）")


class SelectFacesByMaterialInput(BaseModel):
    """按材质选择面输入"""
    object_name: str = Field(..., description="对象名称")
    material_slot: Optional[int] = Field(default=None, description="材质槽索引")
    material_name: Optional[str] = Field(default=None, description="材质名称（与material_slot二选一）")


# ==================== 工具注册 ====================

def register_modeling_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册建模工具"""
    
    @mcp.tool(
        name="blender_mesh_edit_mode",
        annotations={
            "title": "编辑模式切换",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_edit_mode(params: MeshEditModeInput) -> str:
        """进入或退出网格编辑模式。
        
        Args:
            params: 对象名称和操作
            
        Returns:
            操作结果
        """
        result = await server.execute_command(
            "modeling", "edit_mode",
            {"object_name": params.object_name, "enter": params.enter}
        )
        
        if result.get("success"):
            action = "进入" if params.enter else "退出"
            return f"对象 '{params.object_name}' 已{action}编辑模式"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_select",
        annotations={
            "title": "网格选择",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_select(params: MeshSelectInput) -> str:
        """在编辑模式下选择网格元素。
        
        Args:
            params: 选择参数
            
        Returns:
            选择结果
        """
        result = await server.execute_command(
            "modeling", "select",
            {
                "object_name": params.object_name,
                "select_mode": params.select_mode.value,
                "action": params.action.value,
                "random_ratio": params.random_ratio
            }
        )
        
        if result.get("success"):
            return f"选择操作完成"
        else:
            return f"选择失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_extrude",
        annotations={
            "title": "挤出",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_extrude(params: MeshExtrudeInput) -> str:
        """挤出选中的网格元素。
        
        Args:
            params: 挤出参数
            
        Returns:
            挤出结果
        """
        result = await server.execute_command(
            "modeling", "extrude",
            {
                "object_name": params.object_name,
                "direction": params.direction or [0, 0, 1],
                "distance": params.distance,
                "use_normal": params.use_normal
            }
        )
        
        if result.get("success"):
            return f"挤出操作完成，距离: {params.distance}"
        else:
            return f"挤出失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_subdivide",
        annotations={
            "title": "细分",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_subdivide(params: MeshSubdivideInput) -> str:
        """细分选中的网格。
        
        Args:
            params: 细分参数
            
        Returns:
            细分结果
        """
        result = await server.execute_command(
            "modeling", "subdivide",
            {
                "object_name": params.object_name,
                "cuts": params.cuts,
                "smoothness": params.smoothness
            }
        )
        
        if result.get("success"):
            return f"细分完成，切割次数: {params.cuts}"
        else:
            return f"细分失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_bevel",
        annotations={
            "title": "倒角",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_bevel(params: MeshBevelInput) -> str:
        """对选中的边或顶点进行倒角。
        
        Args:
            params: 倒角参数
            
        Returns:
            倒角结果
        """
        result = await server.execute_command(
            "modeling", "bevel",
            {
                "object_name": params.object_name,
                "width": params.width,
                "segments": params.segments,
                "profile": params.profile,
                "affect": params.affect
            }
        )
        
        if result.get("success"):
            return f"倒角完成，宽度: {params.width}，分段: {params.segments}"
        else:
            return f"倒角失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_modifier_add",
        annotations={
            "title": "添加修改器",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_modifier_add(params: ModifierAddInput) -> str:
        """为对象添加修改器。
        
        支持的修改器类型包括：细分曲面、镜像、阵列、倒角、实体化、布尔等。
        
        Args:
            params: 修改器参数
            
        Returns:
            添加结果
        """
        result = await server.execute_command(
            "modeling", "modifier_add",
            {
                "object_name": params.object_name,
                "modifier_type": params.modifier_type.value,
                "modifier_name": params.modifier_name,
                "settings": params.settings or {}
            }
        )
        
        if result.get("success"):
            name = result.get("data", {}).get("modifier_name", params.modifier_type.value)
            return f"已添加 {params.modifier_type.value} 修改器 '{name}'"
        else:
            return f"添加修改器失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_modifier_apply",
        annotations={
            "title": "应用修改器",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_modifier_apply(params: ModifierApplyInput) -> str:
        """应用修改器到网格。
        
        应用后修改器将被移除，效果永久应用到网格。
        
        Args:
            params: 对象名称和修改器名称
            
        Returns:
            应用结果
        """
        result = await server.execute_command(
            "modeling", "modifier_apply",
            {"object_name": params.object_name, "modifier_name": params.modifier_name}
        )
        
        if result.get("success"):
            return f"已应用修改器 '{params.modifier_name}'"
        else:
            return f"应用修改器失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_modifier_remove",
        annotations={
            "title": "移除修改器",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_modifier_remove(params: ModifierRemoveInput) -> str:
        """移除修改器。
        
        Args:
            params: 对象名称和修改器名称
            
        Returns:
            移除结果
        """
        result = await server.execute_command(
            "modeling", "modifier_remove",
            {"object_name": params.object_name, "modifier_name": params.modifier_name}
        )
        
        if result.get("success"):
            return f"已移除修改器 '{params.modifier_name}'"
        else:
            return f"移除修改器失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_boolean_operation",
        annotations={
            "title": "布尔运算",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_boolean_operation(params: BooleanOperationInput) -> str:
        """执行布尔运算。
        
        支持并集、差集、交集运算。
        
        Args:
            params: 布尔运算参数
            
        Returns:
            运算结果
        """
        result = await server.execute_command(
            "modeling", "boolean",
            {
                "object_name": params.object_name,
                "target_name": params.target_name,
                "operation": params.operation.value,
                "apply": params.apply,
                "hide_target": params.hide_target
            }
        )
        
        if result.get("success"):
            op_names = {"UNION": "并集", "DIFFERENCE": "差集", "INTERSECT": "交集"}
            return f"布尔{op_names.get(params.operation.value, params.operation.value)}运算完成"
        else:
            return f"布尔运算失败: {result.get('error', {}).get('message', '未知错误')}"
    
    # ==================== 形态键工具 ====================
    
    @mcp.tool(
        name="blender_shapekey_create",
        annotations={
            "title": "创建形态键",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_shapekey_create(params: ShapeKeyCreateInput) -> str:
        """创建形态键。
        
        用于创建表情控制、面部动画等变形效果。
        首次调用会自动创建基础形态键（Basis）。
        
        Args:
            params: 对象名称和形态键名称
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "modeling", "shapekey_create",
            {
                "object_name": params.object_name,
                "key_name": params.key_name,
                "from_mix": params.from_mix
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已创建形态键 '{data.get('key_name', params.key_name)}' (索引: {data.get('key_index', 'N/A')})"
        else:
            return f"创建形态键失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_shapekey_edit",
        annotations={
            "title": "编辑形态键",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_shapekey_edit(params: ShapeKeyEditInput) -> str:
        """编辑形态键属性。
        
        可以设置形态键的值、静音状态，以及应用顶点偏移。
        
        Args:
            params: 编辑参数
            
        Returns:
            编辑结果
        """
        result = await server.execute_command(
            "modeling", "shapekey_edit",
            {
                "object_name": params.object_name,
                "key_name": params.key_name,
                "value": params.value,
                "mute": params.mute,
                "vertex_offsets": params.vertex_offsets or []
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已编辑形态键 '{params.key_name}'，当前值: {data.get('value', 'N/A')}"
        else:
            return f"编辑形态键失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_shapekey_delete",
        annotations={
            "title": "删除形态键",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_shapekey_delete(params: ShapeKeyDeleteInput) -> str:
        """删除形态键。
        
        Args:
            params: 对象名称和形态键名称
            
        Returns:
            删除结果
        """
        result = await server.execute_command(
            "modeling", "shapekey_delete",
            {
                "object_name": params.object_name,
                "key_name": params.key_name
            }
        )
        
        if result.get("success"):
            return f"已删除形态键 '{params.key_name}'"
        else:
            return f"删除形态键失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_shapekey_list",
        annotations={
            "title": "列出形态键",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_shapekey_list(params: ShapeKeyListInput) -> str:
        """列出对象的所有形态键。
        
        Args:
            params: 对象名称
            
        Returns:
            形态键列表
        """
        result = await server.execute_command(
            "modeling", "shapekey_list",
            {"object_name": params.object_name}
        )
        
        if result.get("success"):
            data = result.get("data", {})
            keys = data.get("shape_keys", [])
            
            if not keys:
                return f"对象 '{params.object_name}' 没有形态键"
            
            lines = [f"# {params.object_name} 的形态键", ""]
            for key in keys:
                status = "🔇" if key.get("mute") else "🔊"
                lines.append(f"- {status} **{key['name']}** (索引: {key['index']}, 值: {key['value']:.2f})")
            
            return "\n".join(lines)
        else:
            return f"获取形态键列表失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_shapekey_create_expressions",
        annotations={
            "title": "创建表情形态键集",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_shapekey_create_expressions(params: ShapeKeyCreateExpressionInput) -> str:
        """为角色创建一组常用表情形态键。
        
        快速创建微笑、惊讶、闭眼等表情形态键框架。
        
        Args:
            params: 对象名称和表情类型列表
            
        Returns:
            创建结果
        """
        result = await server.execute_command(
            "modeling", "shapekey_create_expression",
            {
                "object_name": params.object_name,
                "expressions": [e.value for e in params.expressions]
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            created = data.get("created_keys", [])
            if created:
                return f"已创建 {len(created)} 个表情形态键: {', '.join(created)}"
            else:
                return "所有指定的表情形态键已存在，未创建新的形态键"
        else:
            return f"创建表情形态键失败: {result.get('error', {}).get('message', '未知错误')}"
    
    # ==================== 面材质分配工具 ====================
    
    @mcp.tool(
        name="blender_mesh_assign_material_to_faces",
        annotations={
            "title": "给特定面分配材质",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_assign_material_to_faces(params: MeshAssignMaterialToFacesInput) -> str:
        """给网格的特定面分配材质。
        
        用于给队服的领口、袖口等特定区域分配不同材质。
        
        Args:
            params: 对象名称、面索引列表、材质槽或材质名称
            
        Returns:
            分配结果
        """
        result = await server.execute_command(
            "modeling", "mesh_assign_material_to_faces",
            {
                "object_name": params.object_name,
                "face_indices": params.face_indices,
                "material_slot": params.material_slot,
                "material_name": params.material_name
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已将 {data.get('assigned_faces', len(params.face_indices))} 个面分配到材质槽 {data.get('material_slot', 'N/A')}"
        else:
            return f"分配材质失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_select_faces_by_material",
        annotations={
            "title": "按材质选择面",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_select_faces_by_material(params: SelectFacesByMaterialInput) -> str:
        """按材质选择网格面。
        
        选择使用特定材质的所有面。
        
        Args:
            params: 对象名称和材质槽或材质名称
            
        Returns:
            选择结果
        """
        result = await server.execute_command(
            "modeling", "select_faces_by_material",
            {
                "object_name": params.object_name,
                "material_slot": params.material_slot,
                "material_name": params.material_name
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"已选择 {data.get('selected_faces', 0)} 个使用材质槽 {data.get('material_slot', 'N/A')} 的面"
        else:
            return f"选择面失败: {result.get('error', {}).get('message', '未知错误')}"
