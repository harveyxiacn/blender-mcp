"""
高级网格编辑工具

合并了 inset_faces, bridge_edge_loops, spin, knife_cut, fill_grid,
separate, symmetrize, edge_crease, edge_sharp, edge_seam 等操作到
少量复合工具中，避免工具数量膨胀。
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 枚举 ====================

class MeshEditOperation(str, Enum):
    """高级网格编辑操作类型"""
    INSET_FACES = "INSET_FACES"
    BRIDGE_EDGE_LOOPS = "BRIDGE_EDGE_LOOPS"
    SPIN = "SPIN"
    KNIFE_CUT = "KNIFE_CUT"
    FILL = "FILL"
    GRID_FILL = "GRID_FILL"
    SEPARATE = "SEPARATE"
    SYMMETRIZE = "SYMMETRIZE"
    POKE_FACES = "POKE_FACES"
    TRIANGULATE = "TRIANGULATE"
    TRIS_TO_QUADS = "TRIS_TO_QUADS"
    DISSOLVE = "DISSOLVE"


class EdgeMarkOperation(str, Enum):
    """边标记操作类型"""
    CREASE = "CREASE"
    SHARP = "SHARP"
    SEAM = "SEAM"
    BEVEL_WEIGHT = "BEVEL_WEIGHT"


class SelectByTraitType(str, Enum):
    """按特征选择类型"""
    ALL = "ALL"
    NONE = "NONE"
    NON_MANIFOLD = "NON_MANIFOLD"
    LOOSE = "LOOSE"
    INTERIOR_FACES = "INTERIOR_FACES"
    FACE_SIDES = "FACE_SIDES"
    UNGROUPED = "UNGROUPED"
    BOUNDARY = "BOUNDARY"
    SHARP_EDGES = "SHARP_EDGES"
    LINKED_FLAT = "LINKED_FLAT"


class VertexGroupAction(str, Enum):
    """顶点组操作"""
    CREATE = "CREATE"
    ASSIGN = "ASSIGN"
    REMOVE = "REMOVE"
    SELECT = "SELECT"
    DESELECT = "DESELECT"


# ==================== 输入模型 ====================

class MeshEditAdvancedInput(BaseModel):
    """高级网格编辑输入 - 统一接口"""
    object_name: str = Field(..., description="对象名称")
    operation: MeshEditOperation = Field(..., description="操作类型")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="操作参数(按operation类型): "
                    "INSET_FACES: thickness(float,0.01), depth(float,0), individual(bool,false), use_boundary(bool,true), use_even_offset(bool,true); "
                    "BRIDGE_EDGE_LOOPS: segments(int,1), twist(int,0), profile_shape(str,'SMOOTH'), blend(float,1.0); "
                    "SPIN: angle(float,6.28=360°), steps(int,12), axis(str,'Z'), center([x,y,z]), dupli(bool,false); "
                    "KNIFE_CUT: cut_through(bool,false); "
                    "FILL: use_beauty(bool,true); "
                    "GRID_FILL: span(int,1), offset(int,0); "
                    "SEPARATE: mode(str: SELECTED/MATERIAL/LOOSE); "
                    "SYMMETRIZE: direction(str: NEGATIVE_X/POSITIVE_X/NEGATIVE_Y/POSITIVE_Y/NEGATIVE_Z/POSITIVE_Z); "
                    "POKE_FACES: (无额外参数); "
                    "TRIANGULATE: quad_method(str,'BEAUTY'), ngon_method(str,'BEAUTY'); "
                    "TRIS_TO_QUADS: max_angle(float,40.0); "
                    "DISSOLVE: use_verts(bool,false), use_face_split(bool,false)"
    )


class EdgeMarkInput(BaseModel):
    """边标记工具输入"""
    object_name: str = Field(..., description="对象名称")
    mark_type: EdgeMarkOperation = Field(..., description="标记类型: CREASE(折痕), SHARP(锐边), SEAM(UV接缝), BEVEL_WEIGHT(倒角权重)")
    value: float = Field(default=1.0, description="标记值 (0.0-1.0)，0=清除标记", ge=0.0, le=1.0)
    clear: bool = Field(default=False, description="是否清除标记(设为true则清除选中边的标记)")


class SelectByTraitInput(BaseModel):
    """按特征选择输入"""
    object_name: str = Field(..., description="对象名称")
    select_mode: str = Field(default="FACE", description="选择模式: VERT, EDGE, FACE")
    trait: SelectByTraitType = Field(..., description="特征类型")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="特征参数: "
                    "FACE_SIDES: number(int,4), type(str: LESS/EQUAL/GREATER), extend(bool,false); "
                    "LINKED_FLAT: sharpness(float,0.0175=1°); "
                    "NON_MANIFOLD: extend(bool,false), use_wire(bool,true), use_boundary(bool,true), use_multi_face(bool,true), use_non_contiguous(bool,true), use_verts(bool,true); "
                    "SHARP_EDGES: sharpness(float,0.523=30°); "
                    "LOOSE: extend(bool,false)"
    )


class VertexGroupInput(BaseModel):
    """顶点组操作输入"""
    object_name: str = Field(..., description="对象名称")
    action: VertexGroupAction = Field(..., description="操作类型")
    group_name: str = Field(default="Group", description="顶点组名称")
    weight: float = Field(default=1.0, description="权重值 (0.0-1.0)", ge=0.0, le=1.0)
    vertex_indices: Optional[List[int]] = Field(default=None, description="顶点索引列表(为空则使用当前选择)")


class VertexColorInput(BaseModel):
    """顶点色操作输入"""
    object_name: str = Field(..., description="对象名称")
    action: str = Field(default="CREATE", description="操作: CREATE(创建图层), PAINT(绘制), FILL(填充全部)")
    layer_name: str = Field(default="Col", description="顶点色图层名称")
    color: Optional[List[float]] = Field(default=None, description="颜色 [R,G,B,A] (0-1范围)")
    face_indices: Optional[List[int]] = Field(default=None, description="面索引列表(仅PAINT时用，为空则对所有面)")


# ==================== 工具注册 ====================

def register_mesh_edit_advanced_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册高级网格编辑工具"""

    @mcp.tool(
        name="blender_mesh_edit_advanced",
        annotations={
            "title": "高级网格编辑",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_mesh_edit_advanced(params: MeshEditAdvancedInput) -> str:
        """执行高级网格编辑操作。

        支持面内插(Inset)、桥接边循环(Bridge)、旋转体(Spin)、
        刀切(Knife)、填充(Fill/GridFill)、分离(Separate)、
        对称化(Symmetrize)等操作。

        注意：需要先进入编辑模式并选择元素。

        Args:
            params: 操作类型和参数

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "edit",
            {
                "object_name": params.object_name,
                "operation": params.operation.value,
                "params": params.params or {}
            }
        )

        if result.get("success"):
            op_names = {
                "INSET_FACES": "面内插", "BRIDGE_EDGE_LOOPS": "桥接边循环",
                "SPIN": "旋转体", "KNIFE_CUT": "刀切", "FILL": "填充",
                "GRID_FILL": "栅格填充", "SEPARATE": "分离", "SYMMETRIZE": "对称化",
                "POKE_FACES": "戳面", "TRIANGULATE": "三角化",
                "TRIS_TO_QUADS": "三角转四边", "DISSOLVE": "溶解"
            }
            return f"{op_names.get(params.operation.value, params.operation.value)}操作完成"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_mesh_edge_mark",
        annotations={
            "title": "边标记工具",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_edge_mark(params: EdgeMarkInput) -> str:
        """设置边的折痕(Crease)、锐边(Sharp)、UV接缝(Seam)或倒角权重(BevelWeight)。

        用于控制细分曲面保锐边(Crease)、平滑着色硬边(Sharp)、
        UV展开接缝(Seam)等。需先进入编辑模式并选择边。

        Args:
            params: 标记类型、值

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "edge_mark",
            {
                "object_name": params.object_name,
                "mark_type": params.mark_type.value,
                "value": params.value,
                "clear": params.clear
            }
        )

        if result.get("success"):
            mark_names = {"CREASE": "折痕", "SHARP": "锐边", "SEAM": "UV接缝", "BEVEL_WEIGHT": "倒角权重"}
            action = "清除" if params.clear else f"设置(值={params.value})"
            return f"已{action} {mark_names.get(params.mark_type.value, params.mark_type.value)}"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_mesh_select_by_trait",
        annotations={
            "title": "按特征选择网格",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_mesh_select_by_trait(params: SelectByTraitInput) -> str:
        """按特征选择网格元素。

        支持选择非流形(Non-Manifold)、孤立元素(Loose)、内部面(Interior)、
        按面边数(三角/四边/N-gon)、未分组顶点、边界边、锐边、相连平面等。

        需要先进入编辑模式。

        Args:
            params: 选择模式和特征类型

        Returns:
            选择结果
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "select_by_trait",
            {
                "object_name": params.object_name,
                "select_mode": params.select_mode,
                "trait": params.trait.value,
                "params": params.params or {}
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            count = data.get("selected_count", "N/A")
            trait_names = {
                "NON_MANIFOLD": "非流形", "LOOSE": "孤立", "INTERIOR_FACES": "内部面",
                "FACE_SIDES": "按边数", "UNGROUPED": "未分组", "BOUNDARY": "边界",
                "SHARP_EDGES": "锐边", "LINKED_FLAT": "相连平面",
                "ALL": "全选", "NONE": "取消全选"
            }
            return f"按{trait_names.get(params.trait.value, params.trait.value)}选择完成，已选择 {count} 个元素"
        else:
            return f"选择失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_vertex_group",
        annotations={
            "title": "顶点组操作",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_group(params: VertexGroupInput) -> str:
        """创建、分配、选择顶点组。

        顶点组用于绑定权重、修改器影响范围、粒子分布密度等。

        Args:
            params: 操作类型、组名、权重

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "vertex_group",
            {
                "object_name": params.object_name,
                "action": params.action.value,
                "group_name": params.group_name,
                "weight": params.weight,
                "vertex_indices": params.vertex_indices
            }
        )

        if result.get("success"):
            action_names = {
                "CREATE": "创建", "ASSIGN": "分配", "REMOVE": "移除",
                "SELECT": "选择", "DESELECT": "取消选择"
            }
            return f"顶点组 '{params.group_name}' {action_names.get(params.action.value, params.action.value)}操作完成"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_vertex_color",
        annotations={
            "title": "顶点色操作",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_vertex_color(params: VertexColorInput) -> str:
        """创建和编辑顶点色(Vertex Color)。

        Low Poly风格的核心着色方式。支持创建顶点色图层、
        按面填充颜色、全部填充。

        Args:
            params: 操作类型、颜色、面索引

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "mesh_edit_advanced", "vertex_color",
            {
                "object_name": params.object_name,
                "action": params.action,
                "layer_name": params.layer_name,
                "color": params.color or [1.0, 1.0, 1.0, 1.0],
                "face_indices": params.face_indices
            }
        )

        if result.get("success"):
            action_names = {"CREATE": "创建图层", "PAINT": "绘制", "FILL": "填充"}
            return f"顶点色{action_names.get(params.action, params.action)}完成"
        else:
            return f"操作失败: {result.get('error', {}).get('message', '未知错误')}"
