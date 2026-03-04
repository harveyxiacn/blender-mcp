"""
Skill Manager - 按需加载工具组的核心管理器

Skills 系统架构:
- 启动时只注册核心工具 (~30个) + 3个 Skill 元工具
- AI 通过 activate_skill() 按需加载工具组
- 每个 Skill 提供: 工具组注册 + 工作流指引文本
- 通过 MCP tools/list_changed 通知客户端工具列表变更

使用方式:
1. TOOL_PROFILE = "skill" 启用 Skill 模式
2. AI 调用 list_skills() 查看可用 Skill
3. AI 调用 activate_skill("modeling") 按需加载建模工具
4. AI 使用加载的工具完成任务
5. AI 调用 deactivate_skill("modeling") 卸载工具组
"""

import logging
import importlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer

logger = logging.getLogger(__name__)


@dataclass
class SkillInfo:
    """Skill 元数据"""
    name: str
    description: str
    modules: list[str]
    workflow_guide: str = ""
    estimated_tools: int = 0
    tags: list[str] = field(default_factory=list)


# ============================================================
# Skill 注册表 - 定义所有可用的 Skill 及其工具模块映射
# ============================================================

SKILL_DEFINITIONS: dict[str, SkillInfo] = {
    "modeling": SkillInfo(
        name="modeling",
        description="3D建模工具 - 网格编辑、修改器(45种)、曲线、UV映射，支持各风格参数化建模",
        modules=["modeling", "curves", "uv_mapping"],
        estimated_tools=38,
        tags=["3d", "mesh", "modeling"],
        workflow_guide="""## Modeling Skill 工作流指引

### 常用工作流:
1. **基础建模**: blender_create_object 创建几何体 → blender_add_modifier 添加修改器 → blender_apply_modifier 应用
2. **曲线建模**: 曲线工具创建路径 → 添加 Curve/Bevel 修改器
3. **UV展开**: 选择对象 → blender_uv_unwrap 展开 → blender_uv_project 投射

### 各风格推荐 mesh_params:
| 风格 | 球体 segments | 圆柱 vertices | ICO subdivisions |
|------|-------------|-------------|------------------|
| Pixel | 4-6 | 4-6 | 1 |
| Low Poly | 6-12 | 5-8 | 1 |
| Stylized/Toon | 16-24 | 12-16 | 2 |
| Semi Realistic | 32 | 24-32 | 2-3 |
| PBR/AAA | 32-64 | 32 | 3-4 |

示例: `blender_object_create(type="UV_SPHERE", mesh_params={"segments": 8, "ring_count": 6})`

### 各风格常用修改器:
- **Pixel**: REMESH(Blocks), ARRAY
- **Low Poly**: MIRROR, ARRAY, SOLIDIFY, TRIANGULATE
- **Stylized/Toon**: SUBSURF(1-2), BEVEL, MIRROR
- **Sci-Fi硬表面**: BOOLEAN, ARRAY, BEVEL, SOLIDIFY, SCREW, MIRROR
- **PBR/AAA**: SUBSURF(2-3), MIRROR, MULTIRES, BEVEL, SHRINKWRAP

### 修改器支持 45 种类型:
常用: SUBDIVISION, MIRROR, ARRAY, SOLIDIFY, BEVEL, BOOLEAN, REMESH, SCREW, WIREFRAME, WELD, SHRINKWRAP, SIMPLE_DEFORM

### 提示:
- 复杂操作可通过 blender_execute_python 直接执行 Blender Python API
- 详细风格工作流参见 docs/blender_style_modeling_workflows.md
""",
    ),
    
    "materials": SkillInfo(
        name="materials",
        description="材质系统 - 标准材质、程序化材质(67种预设8大类)、磨损效果(7种)",
        modules=["material", "procedural_materials"],
        estimated_tools=17,
        tags=["material", "shader", "texture"],
        workflow_guide="""## Materials Skill 工作流指引

### 常用工作流:
1. **标准材质**: blender_create_material → blender_set_material_color → blender_assign_material
2. **程序化材质**: blender_procedural_material 一键创建 (67种预设, 8大分类)
3. **磨损效果**: blender_material_wear 添加磨损/老化效果

### 程序化材质完整分类:
- **metal** (10种): STEEL, IRON, GOLD, SILVER, BRONZE, COPPER, CHROME, BRUSHED_METAL, RUSTY_METAL, DAMASCUS
- **wood** (8种): OAK, PINE, CHERRY, WALNUT, BIRCH, BAMBOO, PLYWOOD, AGED_WOOD
- **stone** (9种): GRANITE, MARBLE, LIMESTONE, SLATE, COBBLESTONE, SANDSTONE, BRICK, TILE, CONCRETE
- **fabric** (8种): COTTON, SILK, LEATHER, DENIM, VELVET, CANVAS, WOOL, CHAIN_MAIL
- **nature** (10种): GRASS, DIRT, SAND, SNOW, MUD, GRAVEL, MOSS, LAVA, WATER, ICE
- **skin** (4种): SKIN_REALISTIC, SKIN_STYLIZED, SCALES, CARTOON_SKIN
- **effect** (7种): GLASS, CRYSTAL, HOLOGRAM, ENERGY, PORTAL, EMISSION_GLOW, FORCE_FIELD
- **toon** (7种): TOON_BASIC, TOON_METAL, TOON_SKIN, TOON_FABRIC, ANIME_HAIR, GENSHIN_STYLE, CEL_SHADE

### 磨损效果 (7种):
EDGE_WEAR(边缘磨损), SCRATCHES(划痕), RUST(锈蚀), DIRT(污渍), DUST(灰尘), MOSS(苔藓), PAINT_CHIP(掉漆)

### 各风格推荐材质:
- **Pixel/Low Poly**: TOON_BASIC + 顶点色
- **Toon/Q版**: CEL_SHADE, GENSHIN_STYLE, ANIME_HAIR, TOON_SKIN
- **Sci-Fi**: CHROME, BRUSHED_METAL, ENERGY, HOLOGRAM, FORCE_FIELD
- **PBR写实**: 全部 metal/wood/stone/fabric/nature/skin 预设
- **AAA**: SKIN_REALISTIC + 全套预设 + wear 磨损效果叠加

### 提示:
- 程序化材质自动创建完整节点树, 无需手动连接
- 磨损效果可叠加使用, intensity 控制强度 (0-1)
- color_override 可覆盖预设基础色
""",
    ),
    
    "style": SkillInfo(
        name="style",
        description="风格预设 - 像素风→3A级一键环境配置(含摄像机/Bloom/AO/去噪)、描边效果、高低模烘焙",
        modules=["style_presets", "mesh_edit_advanced"],
        estimated_tools=8,
        tags=["style", "pixel", "toon", "pbr", "aaa", "sci-fi"],
        workflow_guide="""## Style Skill 工作流指引

### 一键风格配置 (blender_style_setup):
8 种风格，自动配置渲染引擎+采样+色彩管理+额外设置:

| 风格 | 引擎 | 额外自动配置 |
|------|------|-------------|
| PIXEL | EEVEE | 摄像机→正交, 纹理→Closest, 关Bloom/AO/SSR |
| LOW_POLY | EEVEE | 关Bloom/AO/SSR |
| STYLIZED | EEVEE | 开Bloom(低强度), 关AO |
| TOON | EEVEE | 开Bloom(低强度), 关AO |
| HAND_PAINTED | EEVEE | - |
| SEMI_REALISTIC | EEVEE | 开AO, 开SSR |
| PBR_REALISTIC | Cycles | 开去噪(OpenImageDenoise) |
| AAA | Cycles | 开去噪(OpenImageDenoise) |

对指定对象还会自动设置 Flat/Smooth Shading 和纹理插值。

### 描边效果 (blender_outline_effect):
- SOLIDIFY: 实体化翻转法线 (实时可见, 游戏常用, 推荐卡通风格)
- FREESTYLE: 渲染线条 (仅渲染时可见, 可控线条粗细变化)
- GREASE_PENCIL: Line Art描边 (实时可见, 可手动编辑)

### 高级网格编辑:
- blender_mesh_edit_advanced: inset/bridge/spin/knife/fill/gridFill/separate/symmetrize/poke/triangulate/trisToQuads/dissolve
- blender_mesh_edge_mark: crease/sharp/seam/bevel_weight
- blender_mesh_select_by_trait: non_manifold/loose/interior/face_sides/ungrouped/boundary/sharp/linked_flat
- blender_vertex_group: 创建/分配/移除/选择顶点组
- blender_vertex_color: 创建/绘制/填充顶点颜色 (Low Poly核心)

### 烘焙工作流 (blender_bake_maps):
高模→低模烘焙: NORMAL, AO, CURVATURE, DIFFUSE, ROUGHNESS, COMBINED
用于 PBR_REALISTIC 和 AAA 风格的纹理制作。

### 科幻(Sci-Fi)风格建议:
1. 硬表面建模: Boolean差集挖孔 + Array重复 + Bevel倒角
2. 材质: 激活 materials skill → CHROME/ENERGY/HOLOGRAM/FORCE_FIELD
3. 自发光: Emission + EEVEE Bloom 配合
4. 详细工作流参见 docs/blender_style_modeling_workflows.md
""",
    ),
    
    "character": SkillInfo(
        name="character",
        description="角色创建 - Q版角色模板、骨骼绑定、自动绑定",
        modules=["character_templates", "rigging", "auto_rig"],
        estimated_tools=23,
        tags=["character", "rigging", "template"],
        workflow_guide="""## Character Skill 工作流指引

### Q版角色快速创建:
1. blender_create_character_template → 选择体型预设 (chibi/standard/realistic)
2. 调整比例参数 (head_ratio, body_width 等)
3. 添加服装和配饰

### 骨骼绑定工作流:
1. 创建 Armature → 添加骨骼层级
2. blender_auto_rig 自动绑定 (自动权重)
3. 调整权重绘制

### 提示:
- Q版角色 head_ratio 建议 2.5-3.0
- 自动绑定前确保网格法线正确
- 骨骼命名遵循 Left/Right 约定以支持镜像
""",
    ),
    
    "animation": SkillInfo(
        name="animation",
        description="动画工具 - 关键帧、动画预设、时间线管理",
        modules=["animation", "animation_presets"],
        estimated_tools=17,
        tags=["animation", "keyframe", "timeline"],
        workflow_guide="""## Animation Skill 工作流指引

### 基础动画:
1. 选择对象 → blender_insert_keyframe (location/rotation/scale)
2. 设置帧范围 → 切换帧 → 插入下一关键帧
3. 调整插值曲线 (LINEAR/BEZIER/CONSTANT)

### 动画预设:
- 行走循环、呼吸、弹跳等预设动画
- 可应用到已绑定的角色

### 提示:
- 使用 CONSTANT 插值实现像素风动画
- 循环动画确保首尾帧一致
""",
    ),
    
    "scene_setup": SkillInfo(
        name="scene_setup",
        description="场景配置 - 灯光、相机、世界环境、渲染设置",
        modules=["lighting", "camera", "world", "render"],
        estimated_tools=18,
        tags=["scene", "lighting", "camera", "render"],
        workflow_guide="""## Scene Setup Skill 工作流指引

### 标准场景配置流程:
1. **灯光**: 三点布光 (Key/Fill/Rim) 或 HDRI 环境光
2. **相机**: 设置焦距、景深、构图
3. **世界**: 背景颜色/HDRI/体积雾
4. **渲染**: 选择引擎 (EEVEE/Cycles), 设置采样和分辨率

### 快速配置:
- 产品展示: 3点灯 + 白色背景 + 浅景深
- 室外场景: HDRI + 太阳灯 + 体积散射
- 卡通渲染: 平面光 + 纯色背景 + Freestyle描边
""",
    ),

    "automation": SkillInfo(
        name="automation",
        description="自动化生产线 - 一键生成角色/道具/场景 + 质量审计闭环",
        modules=["pipeline", "quality_audit", "style_presets", "procedural_materials"],
        estimated_tools=12,
        tags=["automation", "pipeline", "quality", "style", "production"],
        workflow_guide="""## Automation Skill 工作流指引

### 推荐全自动流程:
1. `blender_pipeline_generate_character` 生成角色主体（模板/服装/配饰/自动绑定）
2. `blender_pipeline_generate_prop` 批量生成道具（含程序化材质与UV）
3. `blender_pipeline_assemble_scene` 自动完成环境、灯光、相机和渲染参数
4. `blender_quality_audit_full` 进行拓扑 + UV + 性能审计并输出最终评分

### 多风格落地建议:
- 像素/低模: style=PIXEL/LOW_POLY + quality_target=draft/production
- 二次元/卡通: style=TOON/STYLIZED + outline + GENSHIN_STYLE/TOON 系材质
- 写实/3A: style=PBR_REALISTIC/AAA + 更高采样 + 质量审计目标平台设为 desktop/aaa

### 质量门禁建议:
- Topology: N-gon/non-manifold/loose verts 清零或接近零
- UV: 平均评分 >= 80，重叠面最小化
- Performance: 不超过目标平台 triangles/draw calls 预算

### 提示:
- 该 Skill 聚焦“自动生成 + 自动审计”，适合批量资产生产和持续迭代
- 如需细节手工打磨，可再激活 modeling/materials/advanced_3d Skills
""",
    ),
    
    "physics": SkillInfo(
        name="physics",
        description="物理模拟 - 刚体、布料、流体、约束系统",
        modules=["physics", "constraints"],
        estimated_tools=18,
        tags=["physics", "simulation", "constraints"],
        workflow_guide="""## Physics Skill 工作流指引

### 物理模拟:
- 刚体: 设置 Active/Passive → 调整质量/摩擦 → 烘焙
- 布料: 添加 Cloth 修改器 → 设置碰撞体 → 模拟
- 流体: Domain + Inflow/Outflow → 烘焙

### 约束系统:
- Track To, Copy Location/Rotation, IK 等
- 用于相机跟踪、机械联动、角色约束

### 提示:
- 先低分辨率预览, 确认效果后提高精度烘焙
""",
    ),
    
    "batch_assets": SkillInfo(
        name="batch_assets",
        description="批处理和资产管理 - 批量操作、资产库管理",
        modules=["batch", "assets"],
        estimated_tools=11,
        tags=["batch", "assets", "pipeline"],
        workflow_guide="""## Batch & Assets Skill 工作流指引

### 批量操作:
- 批量重命名、批量材质替换、批量导出
- 批量修改器应用

### 资产管理:
- 标记资产、浏览资产库、资产复用
""",
    ),
    
    "advanced_3d": SkillInfo(
        name="advanced_3d",
        description="高级3D工具 - 节点编辑、合成器、雕刻、纹理绘制",
        modules=["nodes", "compositor", "sculpting", "texture_painting"],
        estimated_tools=32,
        tags=["nodes", "compositor", "sculpting", "painting"],
        workflow_guide="""## Advanced 3D Skill 工作流指引

### 几何节点:
- 创建程序化几何、散布系统、参数化模型

### 合成器:
- 后期处理: 光晕、色彩校正、景深

### 雕刻:
- 高模细节雕刻、多分辨率工作流

### 纹理绘制:
- 直接在模型上绘制纹理
""",
    ),
    
    "sport_character": SkillInfo(
        name="sport_character",
        description="运动角色专用 - 运动员建模、装备、运动服、姿势",
        modules=["sport_character"],
        estimated_tools=7,
        tags=["sport", "athlete", "character"],
        workflow_guide="""## Sport Character Skill 工作流指引

### 运动员角色创建:
1. 选择运动类型 (乒乓球/篮球/足球等)
2. 创建基础角色体型
3. 添加运动装备和服装
4. 设置运动姿势
5. Web优化导出 (GLB/GLTF)
""",
    ),
    
    "training": SkillInfo(
        name="training",
        description="培训系统 - 交互式Blender学习课程和项目实战",
        modules=["training"],
        estimated_tools=11,
        tags=["training", "learning", "tutorial"],
        workflow_guide="""## Training Skill 工作流指引

### 使用培训系统:
1. 浏览课程列表 → 选择课程
2. 开始练习 → 按步骤操作
3. 系统自动验证操作结果
4. 查看进度和成绩
""",
    ),
}


class SkillManager:
    """Skill 管理器 - 负责动态加载/卸载工具组"""
    
    def __init__(self, server: "BlenderMCPServer"):
        self.server = server
        self._active_skills: dict[str, list[str]] = {}  # skill_name -> [tool_names]
        self._registered_tool_funcs: dict[str, Any] = {}  # tool_name -> original func (for cleanup)
    
    @property
    def available_skills(self) -> dict[str, SkillInfo]:
        return SKILL_DEFINITIONS
    
    @property
    def active_skills(self) -> dict[str, list[str]]:
        return self._active_skills
    
    def is_active(self, skill_name: str) -> bool:
        return skill_name in self._active_skills

    def _tool_names_snapshot(self) -> set[str]:
        """获取当前已注册工具名快照（同步方式）。"""
        tool_manager = getattr(self.server.mcp, "_tool_manager", None)
        tools = getattr(tool_manager, "_tools", None)
        if isinstance(tools, dict):
            return set(tools.keys())
        return set()

    def _remove_tool_by_name(self, tool_name: str) -> bool:
        """移除已注册工具，兼容不同 FastMCP 版本。"""
        remove_tool = getattr(self.server.mcp, "remove_tool", None)
        if callable(remove_tool):
            remove_tool(tool_name)
            return True

        tool_manager = getattr(self.server.mcp, "_tool_manager", None)
        tools = getattr(tool_manager, "_tools", None)
        if isinstance(tools, dict) and tool_name in tools:
            del tools[tool_name]
            return True
        return False
    
    def activate_skill(self, skill_name: str) -> tuple[bool, str, list[str]]:
        """激活一个 Skill, 动态注册其工具模块
        
        Returns:
            (success, message, registered_tool_names)
        """
        if skill_name not in SKILL_DEFINITIONS:
            available = ", ".join(SKILL_DEFINITIONS.keys())
            return False, f"Unknown skill: {skill_name}. Available: {available}", []
        
        if skill_name in self._active_skills:
            tools = self._active_skills[skill_name]
            return False, f"Skill '{skill_name}' is already active with {len(tools)} tools", tools
        
        skill_info = SKILL_DEFINITIONS[skill_name]
        registered_tools: list[str] = []
        
        from blender_mcp.tools_config import MODULE_REGISTRY
        
        for module_name in skill_info.modules:
            if module_name not in MODULE_REGISTRY:
                logger.warning(f"Skill '{skill_name}': unknown module '{module_name}'")
                continue
            
            register_func_name = MODULE_REGISTRY[module_name]
            
            try:
                tool_module = importlib.import_module(f"blender_mcp.tools.{module_name}")
                register_func = getattr(tool_module, register_func_name)
                
                # 记录注册前的工具列表
                before = self._tool_names_snapshot()
                
                # 调用注册函数
                register_func(self.server.mcp, self.server)
                
                # 计算新注册的工具
                after = self._tool_names_snapshot()
                new_tools = after - before
                registered_tools.extend(new_tools)
                
                logger.info(f"Skill '{skill_name}': loaded module '{module_name}' ({len(new_tools)} tools)")
                
            except Exception as e:
                logger.error(f"Skill '{skill_name}': failed to load module '{module_name}': {e}")
        
        self._active_skills[skill_name] = registered_tools
        
        return True, f"Activated skill '{skill_name}' with {len(registered_tools)} tools", registered_tools
    
    def deactivate_skill(self, skill_name: str) -> tuple[bool, str]:
        """停用一个 Skill, 移除其工具
        
        Returns:
            (success, message)
        """
        if skill_name not in self._active_skills:
            return False, f"Skill '{skill_name}' is not active"
        
        tool_names = self._active_skills[skill_name]
        removed = []
        
        for tool_name in tool_names:
            try:
                if self._remove_tool_by_name(tool_name):
                    removed.append(tool_name)
                else:
                    logger.warning(f"Could not remove tool '{tool_name}': tool not found")
            except Exception as e:
                logger.warning(f"Could not remove tool '{tool_name}': {e}")
        
        del self._active_skills[skill_name]
        
        return True, f"Deactivated skill '{skill_name}', removed {len(removed)} tools"
    
    def get_status_summary(self) -> str:
        """获取所有 Skill 的状态摘要"""
        lines = []
        for name, info in SKILL_DEFINITIONS.items():
            active = name in self._active_skills
            tool_count = len(self._active_skills.get(name, []))
            status = f"✅ ACTIVE ({tool_count} tools)" if active else "⬚ available"
            lines.append(f"- **{name}**: {info.description} [{status}]")
        
        active_count = len(self._active_skills)
        total_tools = sum(len(t) for t in self._active_skills.values())
        
        lines.insert(0, f"## Skills Status ({active_count} active, {total_tools} tools loaded)\n")
        return "\n".join(lines)
