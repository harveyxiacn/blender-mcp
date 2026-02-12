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
    # 生成类
    SUBSURF = "SUBSURF"
    MIRROR = "MIRROR"
    ARRAY = "ARRAY"
    BEVEL = "BEVEL"
    SOLIDIFY = "SOLIDIFY"
    BOOLEAN = "BOOLEAN"
    SKIN = "SKIN"
    SCREW = "SCREW"
    WIREFRAME = "WIREFRAME"
    WELD = "WELD"
    REMESH = "REMESH"
    BUILD = "BUILD"
    MULTIRES = "MULTIRES"
    # 变形类
    ARMATURE = "ARMATURE"
    CAST = "CAST"
    CURVE = "CURVE"
    DISPLACE = "DISPLACE"
    LATTICE = "LATTICE"
    SHRINKWRAP = "SHRINKWRAP"
    SIMPLE_DEFORM = "SIMPLE_DEFORM"
    SMOOTH = "SMOOTH"
    LAPLACIANSMOOTH = "LAPLACIANSMOOTH"
    CORRECTIVE_SMOOTH = "CORRECTIVE_SMOOTH"
    SURFACE_DEFORM = "SURFACE_DEFORM"
    MESH_DEFORM = "MESH_DEFORM"
    WARP = "WARP"
    WAVE = "WAVE"
    # 物理类
    CLOTH = "CLOTH"
    COLLISION = "COLLISION"
    PARTICLE_SYSTEM = "PARTICLE_SYSTEM"
    # 数据类
    DATA_TRANSFER = "DATA_TRANSFER"
    WEIGHTED_NORMAL = "WEIGHTED_NORMAL"
    UV_PROJECT = "UV_PROJECT"
    UV_WARP = "UV_WARP"
    VERTEX_WEIGHT_EDIT = "VERTEX_WEIGHT_EDIT"
    VERTEX_WEIGHT_MIX = "VERTEX_WEIGHT_MIX"
    VERTEX_WEIGHT_PROXIMITY = "VERTEX_WEIGHT_PROXIMITY"
    # 减面类
    DECIMATE = "DECIMATE"
    TRIANGULATE = "TRIANGULATE"
    EDGE_SPLIT = "EDGE_SPLIT"
    # 几何节点
    NODES = "NODES"


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


# ==================== 生产标准优化工具输入模型 ====================

class TargetPlatform(str, Enum):
    """目标平台"""
    MOBILE = "MOBILE"           # 移动端：500-2000三角形
    PC_CONSOLE = "PC_CONSOLE"   # PC/主机：2000-50000三角形
    CINEMATIC = "CINEMATIC"     # 电影级：不限制
    VR = "VR"                   # VR：1000-10000三角形


class MeshAnalyzeInput(BaseModel):
    """网格分析输入"""
    object_name: str = Field(..., description="对象名称")
    target_platform: TargetPlatform = Field(default=TargetPlatform.PC_CONSOLE, description="目标平台")


class MeshOptimizeInput(BaseModel):
    """网格优化输入"""
    object_name: str = Field(..., description="对象名称")
    target_triangles: Optional[int] = Field(default=None, description="目标三角形数量")
    target_platform: TargetPlatform = Field(default=TargetPlatform.PC_CONSOLE, description="目标平台")
    preserve_uvs: bool = Field(default=True, description="保留UV坐标")
    preserve_normals: bool = Field(default=True, description="保留法线")
    symmetry: bool = Field(default=False, description="保持对称性")


class MeshCleanupInput(BaseModel):
    """网格清理输入"""
    object_name: str = Field(..., description="对象名称")
    merge_distance: float = Field(default=0.0001, description="合并距离（合并重叠顶点）", ge=0)
    remove_doubles: bool = Field(default=True, description="移除重复顶点")
    dissolve_degenerate: bool = Field(default=True, description="溶解退化几何体")
    fix_non_manifold: bool = Field(default=True, description="修复非流形几何体")
    recalculate_normals: bool = Field(default=True, description="重新计算法线")
    remove_loose: bool = Field(default=True, description="移除孤立几何体")


class TrisToQuadsInput(BaseModel):
    """三角形转四边形输入"""
    object_name: str = Field(..., description="对象名称")
    max_angle: float = Field(default=40.0, description="最大角度（度）", ge=0, le=180)
    compare_uvs: bool = Field(default=True, description="比较UV坐标")
    compare_vcol: bool = Field(default=True, description="比较顶点色")
    compare_materials: bool = Field(default=True, description="比较材质")


class LODGenerateInput(BaseModel):
    """LOD生成输入"""
    object_name: str = Field(..., description="对象名称")
    lod_levels: int = Field(default=3, description="LOD级别数量", ge=1, le=5)
    ratio_step: float = Field(default=0.5, description="每级减少比例", gt=0, lt=1)
    create_collection: bool = Field(default=True, description="创建LOD集合")


class SmartSubdivideInput(BaseModel):
    """智能细分输入"""
    object_name: str = Field(..., description="对象名称")
    levels: int = Field(default=1, description="细分级别", ge=1, le=4)
    render_levels: Optional[int] = Field(default=None, description="渲染级别（可选，默认等于levels）")
    use_creases: bool = Field(default=True, description="使用折痕边保持锐边")
    apply_smooth: bool = Field(default=False, description="应用平滑着色")
    quality: int = Field(default=3, description="质量等级（1-5）", ge=1, le=5)


class AutoSmoothInput(BaseModel):
    """自动平滑输入"""
    object_name: str = Field(..., description="对象名称")
    angle: float = Field(default=30.0, description="平滑角度阈值（度）", ge=0, le=180)
    use_sharp_edges: bool = Field(default=True, description="对锐边使用硬边")


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
    
    # ==================== 生产标准优化工具 ====================
    
    @mcp.tool(
        name="blender_mesh_analyze",
        annotations={
            "title": "网格拓扑分析",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_analyze(params: MeshAnalyzeInput) -> str:
        """分析网格拓扑质量，检查是否符合生产标准。
        
        根据目标平台（移动端、PC/主机、电影级、VR）检查：
        - 三角形/四边形/N-gon比例
        - 面数是否在平台限制内
        - 非流形几何体
        - 孤立顶点/边
        - 法线一致性
        
        Args:
            params: 对象名称和目标平台
            
        Returns:
            详细的拓扑分析报告
        """
        result = await server.execute_command(
            "modeling", "mesh_analyze",
            {
                "object_name": params.object_name,
                "target_platform": params.target_platform.value
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            lines = [f"# 网格分析报告: {params.object_name}", ""]
            
            # 基础统计
            stats = data.get("stats", {})
            lines.append("## 基础统计")
            lines.append(f"- 顶点数: {stats.get('vertices', 0)}")
            lines.append(f"- 边数: {stats.get('edges', 0)}")
            lines.append(f"- 面数: {stats.get('faces', 0)}")
            lines.append(f"- 三角形数: {stats.get('triangles', 0)}")
            lines.append("")
            
            # 面类型分布
            face_types = data.get("face_types", {})
            lines.append("## 面类型分布")
            lines.append(f"- 三角形: {face_types.get('tris', 0)} ({face_types.get('tris_percent', 0):.1f}%)")
            lines.append(f"- 四边形: {face_types.get('quads', 0)} ({face_types.get('quads_percent', 0):.1f}%)")
            lines.append(f"- N-gon: {face_types.get('ngons', 0)} ({face_types.get('ngons_percent', 0):.1f}%)")
            lines.append("")
            
            # 平台兼容性
            platform_check = data.get("platform_check", {})
            lines.append(f"## 平台兼容性 ({params.target_platform.value})")
            lines.append(f"- 状态: {'✅ 通过' if platform_check.get('passed') else '❌ 不通过'}")
            lines.append(f"- 推荐三角形范围: {platform_check.get('min_tris', 0)} - {platform_check.get('max_tris', 0)}")
            if not platform_check.get('passed'):
                lines.append(f"- 建议: {platform_check.get('suggestion', '减少面数')}")
            lines.append("")
            
            # 问题检测
            issues = data.get("issues", [])
            if issues:
                lines.append("## ⚠️ 检测到的问题")
                for issue in issues:
                    lines.append(f"- {issue}")
            else:
                lines.append("## ✅ 未检测到问题")
            
            # 质量评分
            quality_score = data.get("quality_score", 0)
            lines.append("")
            lines.append(f"## 拓扑质量评分: {quality_score}/100")
            
            return "\n".join(lines)
        else:
            return f"分析失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_optimize",
        annotations={
            "title": "网格优化（减面）",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_optimize(params: MeshOptimizeInput) -> str:
        """优化网格，减少面数以满足目标平台要求。
        
        使用Decimate修改器智能减少面数，同时保持模型外观。
        
        Args:
            params: 优化参数
            
        Returns:
            优化结果
        """
        result = await server.execute_command(
            "modeling", "mesh_optimize",
            {
                "object_name": params.object_name,
                "target_triangles": params.target_triangles,
                "target_platform": params.target_platform.value,
                "preserve_uvs": params.preserve_uvs,
                "preserve_normals": params.preserve_normals,
                "symmetry": params.symmetry
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            original = data.get("original_triangles", 0)
            optimized = data.get("optimized_triangles", 0)
            reduction = data.get("reduction_percent", 0)
            return f"网格优化完成: {original} → {optimized} 三角形（减少 {reduction:.1f}%）"
        else:
            return f"优化失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_mesh_cleanup",
        annotations={
            "title": "网格清理",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_cleanup(params: MeshCleanupInput) -> str:
        """清理网格，修复常见拓扑问题。
        
        包括：合并重叠顶点、移除退化几何体、修复非流形、
        重新计算法线、移除孤立几何体等。
        
        Args:
            params: 清理选项
            
        Returns:
            清理结果
        """
        result = await server.execute_command(
            "modeling", "mesh_cleanup",
            {
                "object_name": params.object_name,
                "merge_distance": params.merge_distance,
                "remove_doubles": params.remove_doubles,
                "dissolve_degenerate": params.dissolve_degenerate,
                "fix_non_manifold": params.fix_non_manifold,
                "recalculate_normals": params.recalculate_normals,
                "remove_loose": params.remove_loose
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            removed = data.get("removed_vertices", 0)
            fixed = data.get("fixed_issues", 0)
            return f"网格清理完成: 移除 {removed} 个重复顶点，修复 {fixed} 个问题"
        else:
            return f"清理失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_tris_to_quads",
        annotations={
            "title": "三角形转四边形",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_tris_to_quads(params: TrisToQuadsInput) -> str:
        """将三角形面转换为四边形。
        
        四边形拓扑更适合细分曲面和动画变形。
        
        Args:
            params: 转换参数
            
        Returns:
            转换结果
        """
        result = await server.execute_command(
            "modeling", "tris_to_quads",
            {
                "object_name": params.object_name,
                "max_angle": params.max_angle,
                "compare_uvs": params.compare_uvs,
                "compare_vcol": params.compare_vcol,
                "compare_materials": params.compare_materials
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            converted = data.get("converted_faces", 0)
            return f"已将 {converted} 对三角形转换为四边形"
        else:
            return f"转换失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_lod_generate",
        annotations={
            "title": "生成LOD（细节层次）",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_lod_generate(params: LODGenerateInput) -> str:
        """为模型生成多级细节（LOD）版本。
        
        LOD用于游戏中根据距离显示不同精度的模型，优化性能。
        
        Args:
            params: LOD生成参数
            
        Returns:
            生成结果
        """
        result = await server.execute_command(
            "modeling", "lod_generate",
            {
                "object_name": params.object_name,
                "lod_levels": params.lod_levels,
                "ratio_step": params.ratio_step,
                "create_collection": params.create_collection
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            lods = data.get("lod_objects", [])
            lines = ["# LOD生成完成", ""]
            for lod in lods:
                lines.append(f"- {lod['name']}: {lod['triangles']} 三角形")
            return "\n".join(lines)
        else:
            return f"LOD生成失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_smart_subdivide",
        annotations={
            "title": "智能细分",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_smart_subdivide(params: SmartSubdivideInput) -> str:
        """智能细分网格，自动处理折痕边和平滑组。
        
        比普通细分曲面更智能，会自动检测并保护锐边。
        
        Args:
            params: 细分参数
            
        Returns:
            细分结果
        """
        result = await server.execute_command(
            "modeling", "smart_subdivide",
            {
                "object_name": params.object_name,
                "levels": params.levels,
                "render_levels": params.render_levels or params.levels,
                "use_creases": params.use_creases,
                "apply_smooth": params.apply_smooth,
                "quality": params.quality
            }
        )
        
        if result.get("success"):
            data = result.get("data", {})
            return f"智能细分完成: 视口级别 {params.levels}，渲染级别 {params.render_levels or params.levels}"
        else:
            return f"细分失败: {result.get('error', {}).get('message', '未知错误')}"
    
    @mcp.tool(
        name="blender_auto_smooth",
        annotations={
            "title": "自动平滑",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_auto_smooth(params: AutoSmoothInput) -> str:
        """设置自动平滑，根据角度阈值区分平滑面和硬边。
        
        这是游戏和电影制作中的标准做法，用于控制模型的着色外观。
        
        Args:
            params: 自动平滑参数
            
        Returns:
            设置结果
        """
        result = await server.execute_command(
            "modeling", "auto_smooth",
            {
                "object_name": params.object_name,
                "angle": params.angle,
                "use_sharp_edges": params.use_sharp_edges
            }
        )
        
        if result.get("success"):
            return f"已为 '{params.object_name}' 设置自动平滑，角度阈值: {params.angle}°"
        else:
            return f"设置失败: {result.get('error', {}).get('message', '未知错误')}"
