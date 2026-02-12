"""
风格预设工具

一键配置从像素风格到3A级的完整渲染/材质/建模环境。
将多个工具的调用合并为一个高级风格设置工具。
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


class ModelingStyle(str, Enum):
    """建模风格"""
    PIXEL = "PIXEL"
    LOW_POLY = "LOW_POLY"
    STYLIZED = "STYLIZED"
    TOON = "TOON"
    HAND_PAINTED = "HAND_PAINTED"
    SEMI_REALISTIC = "SEMI_REALISTIC"
    PBR_REALISTIC = "PBR_REALISTIC"
    AAA = "AAA"


class OutlineMethod(str, Enum):
    """描边方法"""
    SOLIDIFY = "SOLIDIFY"
    FREESTYLE = "FREESTYLE"
    GREASE_PENCIL = "GREASE_PENCIL"


class StyleSetupInput(BaseModel):
    """风格设置输入"""
    style: ModelingStyle = Field(
        ...,
        description="建模风格: "
                    "PIXEL(像素/体素,Flat Shading+像素纹理), "
                    "LOW_POLY(低多边形,Flat Shading+纯色/顶点色), "
                    "STYLIZED(风格化,渐变色+简单纹理), "
                    "TOON(卡通/赛璐璐,Cel Shading+描边), "
                    "HAND_PAINTED(手绘,Diffuse-Only纹理), "
                    "SEMI_REALISTIC(半写实,简化PBR), "
                    "PBR_REALISTIC(PBR写实,完整PBR管线), "
                    "AAA(3A/影视级,高模雕刻+全套贴图)"
    )
    apply_to_scene: bool = Field(default=True, description="是否应用到场景渲染设置")
    apply_to_objects: Optional[List[str]] = Field(default=None, description="应用到指定对象(为空则仅设置场景)")


class OutlineSetupInput(BaseModel):
    """描边效果设置输入"""
    object_name: str = Field(..., description="对象名称")
    method: OutlineMethod = Field(
        default=OutlineMethod.SOLIDIFY,
        description="描边方法: SOLIDIFY(实体化翻转法线,最通用), FREESTYLE(渲染线,仅Cycles/EEVEE), GREASE_PENCIL(油笔描边)"
    )
    thickness: float = Field(default=0.02, description="描边粗细", gt=0)
    color: Optional[List[float]] = Field(default=None, description="描边颜色 [R,G,B] (默认黑色)")


class BakeWorkflowInput(BaseModel):
    """烘焙工作流输入"""
    high_poly: str = Field(..., description="高模对象名称")
    low_poly: str = Field(..., description="低模对象名称")
    maps: List[str] = Field(
        default=["NORMAL", "AO"],
        description="要烘焙的贴图类型: NORMAL(法线), AO(环境光遮蔽), CURVATURE(曲率), DIFFUSE(漫射色), ROUGHNESS(粗糙度), COMBINED(综合)"
    )
    resolution: int = Field(default=2048, description="纹理分辨率", ge=256, le=8192)
    cage_extrusion: float = Field(default=0.1, description="笼体挤出距离", ge=0.001)
    output_dir: Optional[str] = Field(default=None, description="输出目录(为空则保存到blend文件同目录)")
    margin: int = Field(default=16, description="边缘扩展像素", ge=0, le=64)


# ==================== 工具注册 ====================

def register_style_preset_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册风格预设工具"""

    @mcp.tool(
        name="blender_style_setup",
        annotations={
            "title": "风格环境设置",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_style_setup(params: StyleSetupInput) -> str:
        """一键配置建模风格环境。

        根据选择的风格（像素→3A）自动配置：
        - 渲染引擎和设置
        - 默认材质模式
        - 着色方式(Flat/Smooth)
        - 纹理过滤(Nearest/Linear)
        - 推荐的建模参数

        这是开始任何风格建模前的第一步。

        Args:
            params: 风格类型和应用范围

        Returns:
            配置结果和建模建议
        """
        result = await server.execute_command(
            "style_presets", "setup",
            {
                "style": params.style.value,
                "apply_to_scene": params.apply_to_scene,
                "apply_to_objects": params.apply_to_objects or []
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            style_names = {
                "PIXEL": "像素/体素", "LOW_POLY": "低多边形", "STYLIZED": "风格化",
                "TOON": "卡通/赛璐璐", "HAND_PAINTED": "手绘", "SEMI_REALISTIC": "半写实",
                "PBR_REALISTIC": "PBR写实", "AAA": "3A/影视级"
            }
            tips = data.get("tips", "")
            settings = data.get("settings_applied", {})
            extra = data.get("extra_applied", [])
            lines = [
                f"# {style_names.get(params.style.value, params.style.value)}风格环境已配置",
                "",
                "## 已应用设置",
            ]
            for k, v in settings.items():
                lines.append(f"- **{k}**: {v}")
            if extra:
                lines.append("")
                lines.append("## 额外配置")
                for item in extra:
                    lines.append(f"- {item}")
            if tips:
                lines.append("")
                lines.append("## 建模建议")
                lines.append(tips)
            return "\n".join(lines)
        else:
            return f"风格设置失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_outline_effect",
        annotations={
            "title": "描边效果",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_outline_effect(params: OutlineSetupInput) -> str:
        """为对象添加描边效果。

        支持三种方法：
        - SOLIDIFY: 实体化+翻转法线（最通用，适合卡通/风格化）
        - FREESTYLE: Blender渲染线（仅在渲染时可见）
        - GREASE_PENCIL: 油笔描边（实时可见）

        Args:
            params: 对象名、方法、粗细、颜色

        Returns:
            设置结果
        """
        result = await server.execute_command(
            "style_presets", "outline",
            {
                "object_name": params.object_name,
                "method": params.method.value,
                "thickness": params.thickness,
                "color": params.color or [0, 0, 0]
            }
        )

        if result.get("success"):
            method_names = {"SOLIDIFY": "实体化翻转", "FREESTYLE": "渲染线", "GREASE_PENCIL": "油笔"}
            return f"已添加{method_names.get(params.method.value, params.method.value)}描边效果，粗细: {params.thickness}"
        else:
            return f"添加描边失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_bake_maps",
        annotations={
            "title": "烘焙贴图",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_bake_maps(params: BakeWorkflowInput) -> str:
        """从高模到低模烘焙贴图（法线/AO/曲率等）。

        3A制作和PBR写实风格的核心环节。自动处理：
        - 选择高模和低模
        - 创建烘焙用图像纹理节点
        - 设置烘焙参数
        - 执行烘焙
        - 保存纹理

        需要Cycles渲染引擎。

        Args:
            params: 高模名、低模名、贴图类型、分辨率

        Returns:
            烘焙结果
        """
        result = await server.execute_command(
            "style_presets", "bake_maps",
            {
                "high_poly": params.high_poly,
                "low_poly": params.low_poly,
                "maps": params.maps,
                "resolution": params.resolution,
                "cage_extrusion": params.cage_extrusion,
                "output_dir": params.output_dir,
                "margin": params.margin
            }
        )

        if result.get("success"):
            data = result.get("data", {})
            baked = data.get("baked_maps", [])
            lines = [f"# 烘焙完成", ""]
            for m in baked:
                lines.append(f"- **{m.get('type', '?')}**: {m.get('path', 'saved')}")
            return "\n".join(lines)
        else:
            return f"烘焙失败: {result.get('error', {}).get('message', '未知错误')}"
