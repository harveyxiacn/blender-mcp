"""
工具模块配置 - 控制启用哪些工具模块
Tool Module Configuration - Control which tool modules are enabled

使用方法:
1. 设置 TOOL_PROFILE = "minimal" 启用最少工具 (~30个)
2. 设置 TOOL_PROFILE = "standard" 启用标准工具 (~80个)
3. 设置 TOOL_PROFILE = "full" 启用所有工具 (~300个)

或者手动设置 ENABLED_MODULES 列表
"""

# 工具配置文件 (Tool Profile)
# 选项: "skill", "minimal", "focused", "standard", "extended", "full", "custom"
# 
# 推荐配置:
# - "skill": ~31个工具 + 按需加载 - AI驱动的动态工具管理 (推荐)
# - "focused": ~89个工具 - 满足大多数自动化需求
# - "standard": ~153个工具 - 包含角色和场景功能
# - "full": ~326个工具 - 完整功能
TOOL_PROFILE = "skill"

# ============================================================
# 工具模块分类
# ============================================================

# 核心工具 - 必须启用，这是最基本的功能
CORE_MODULES = [
    "scene",              # 场景管理 (5个工具)
    "object",             # 对象操作 (15个工具)
    "utility",            # 实用工具 (8个工具) - 包含execute_python
    "export",             # 导出工具 (4个工具)
]

# 建模工具 - 创建和编辑3D模型
MODELING_MODULES = [
    "modeling",           # 建模工具 (20个工具)
    "material",           # 材质系统 (15个工具)
    "curves",             # 曲线工具 (8个工具)
    "uv_mapping",         # UV映射 (10个工具)
    "mesh_edit_advanced", # 高级网格编辑 (5个工具) - inset/bridge/spin/edge_mark/select_by_trait/vertex_group/vertex_color
    "style_presets",      # 风格预设 (3个工具) - style_setup/outline/bake_maps
    "procedural_materials", # 程序化材质 (2个工具) - 50+预设/磨损效果
]

# 角色工具 - 角色创建和动画
CHARACTER_MODULES = [
    "character_templates", # 角色模板 (8个工具)
    "rigging",            # 骨骼绑定 (10个工具)
    "auto_rig",           # 自动绑定 (5个工具)
    "animation",          # 动画工具 (12个工具)
    "animation_presets",  # 动画预设 (5个工具)
]

# 场景工具 - 场景设置和渲染
SCENE_MODULES = [
    "lighting",           # 灯光 (5个工具)
    "camera",             # 相机 (4个工具)
    "world",              # 世界设置 (4个工具)
    "render",             # 渲染 (5个工具)
    "scene_advanced",     # 高级场景 (6个工具)
]

# 物理工具 - 物理模拟
PHYSICS_MODULES = [
    "physics",            # 物理系统 (8个工具)
    "constraints",        # 约束系统 (10个工具)
]

# 批处理工具 - 批量操作
BATCH_MODULES = [
    "batch",              # 批量工具 (6个工具)
    "assets",             # 资产管理 (5个工具)
]

# 自动化流程工具 - 一键流程和质量闭环
AUTOMATION_MODULES = [
    "pipeline",           # 自动流程 (3个工具) - 角色/道具/场景
    "quality_audit",      # 质量审计 (4个工具) - 拓扑/UV/性能/综合评分
]

# 高级工具 - 专业功能，不常用
ADVANCED_MODULES = [
    "nodes",              # 节点工具 (8个工具)
    "compositor",         # 合成器 (6个工具)
    "sculpting",          # 雕刻 (10个工具)
    "texture_painting",   # 纹理绘制 (8个工具)
    "grease_pencil",      # 油笔 (10个工具)
    "hair",               # 毛发 (8个工具)
    "simulation",         # 模拟 (10个工具)
    "video_editing",      # 视频编辑 (8个工具)
]

# 外部集成工具 - 与其他软件集成
EXTERNAL_MODULES = [
    "external",           # 外部集成 (5个工具)
    "substance",          # Substance (5个工具)
    "zbrush",             # ZBrush (5个工具)
    "mocap",              # 动作捕捉 (5个工具)
]

# AI和云工具 - 需要外部服务
AI_CLOUD_MODULES = [
    "ai_assist",          # AI辅助 (6个工具)
    "ai_generation",      # AI生成 (8个工具)
    "cloud_render",       # 云渲染 (6个工具)
    "collaboration",      # 协作 (8个工具)
]

# 系统工具 - 系统设置和管理
SYSTEM_MODULES = [
    "addons",             # 插件管理 (4个工具)
    "preferences",        # 偏好设置 (5个工具)
    "versioning",         # 版本控制 (8个工具)
    "vr_ar",              # VR/AR (8个工具)
]

# 角色扩展 - 更多角色功能
CHARACTER_EXTRA_MODULES = [
    "character",          # 角色扩展 (10个工具)
]

# 运动角色工具 - 运动员3D建模专用
SPORT_CHARACTER_MODULES = [
    "sport_character",    # 运动角色 (7个工具) - 运动员角色创建、装备、运动服、姿势、参考图、优化、场景
]

# 培训系统 - 交互式学习和项目实战
TRAINING_MODULES = [
    "training",           # 培训系统 (11个工具) - 课程浏览、练习执行、进度管理
]

# ============================================================
# 预设配置
# ============================================================

# Skill 配置 (~31个工具) - 核心 + Skill 管理元工具 (推荐)
# AI 通过 list_skills/activate_skill/deactivate_skill 按需加载工具组
# 启动时只有核心工具, 需要时再加载建模/材质/动画等工具
SKILL_MODULES = CORE_MODULES + ["skills"]

# 最小配置 (~28个工具) - 仅核心功能
MINIMAL_MODULES = CORE_MODULES

# 聚焦配置 (~89个工具) - 保留完全自动化能力，精简工具数量 (推荐)
# 核心理念：utility.execute_python 可以执行任意 Python 代码，
# 所以只需保留最常用的便捷工具，复杂功能通过 execute_python 实现
FOCUSED_MODULES = [
    # 核心功能 (28个)
    "scene",              # 场景管理 - 必须
    "object",             # 对象操作 - 必须  
    "utility",            # 实用工具 (含execute_python) - 最重要！
    "export",             # 导出工具 - 必须
    
    # 建模基础 (38个)
    "modeling",           # 建模工具 - 创建几何体
    "material",           # 材质系统 - 创建材质
    
    # 风格覆盖 (像素→3A) - 10个工具
    "mesh_edit_advanced", # 高级网格: inset/bridge/spin/edge_mark/select_trait/vertex_group/vertex_color
    "style_presets",      # 风格预设: style_setup/outline/bake_maps
    "procedural_materials", # 程序化材质: 50+预设/磨损效果
    
    # 角色模板 (6个)
    "character_templates", # 角色模板 - 快速创建Q版角色
    
    # 运动角色 (7个)
    "sport_character",    # 运动角色 - 运动员建模、装备、运动服、姿势、Web优化
    
    # 培训系统 (11个)
    "training",           # 培训系统 - 交互式学习与项目实战
    "pipeline",           # 端到端自动流程
    "quality_audit",      # 生产质量审计
]
# 总计约89个工具
# 
# 新增风格覆盖工具说明:
# - mesh_edit_advanced: inset_faces, bridge, spin, edge_mark, select_by_trait, vertex_group, vertex_color
# - style_presets: 一键风格配置(PIXEL/LOW_POLY/TOON/PBR/AAA), 描边效果, 烘焙工作流
# - procedural_materials: 50+程序化材质预设(金属/木材/石材/布料/自然/皮肤/特效/卡通), 磨损效果
# 注意：动画、灯光、渲染等功能可通过 utility.execute_python 实现

# 标准配置 (~153个工具) - 包含更多便捷功能
STANDARD_MODULES = (
    CORE_MODULES +
    MODELING_MODULES +
    CHARACTER_MODULES +
    SCENE_MODULES +
    AUTOMATION_MODULES
)

# 扩展配置 (~120个工具) - 包含物理和批处理
EXTENDED_MODULES = (
    STANDARD_MODULES +
    PHYSICS_MODULES +
    BATCH_MODULES
)

# 完整配置 (~326个工具) - 所有功能
FULL_MODULES = (
    CORE_MODULES +
    MODELING_MODULES +
    CHARACTER_MODULES +
    SCENE_MODULES +
    PHYSICS_MODULES +
    BATCH_MODULES +
    AUTOMATION_MODULES +
    ADVANCED_MODULES +
    EXTERNAL_MODULES +
    AI_CLOUD_MODULES +
    SYSTEM_MODULES +
    CHARACTER_EXTRA_MODULES +
    SPORT_CHARACTER_MODULES +
    TRAINING_MODULES
)

# ============================================================
# 获取启用的模块列表
# ============================================================

def get_enabled_modules():
    """根据TOOL_PROFILE返回启用的模块列表"""
    if TOOL_PROFILE == "skill":
        return SKILL_MODULES
    elif TOOL_PROFILE == "minimal":
        return MINIMAL_MODULES
    elif TOOL_PROFILE == "focused":
        return FOCUSED_MODULES
    elif TOOL_PROFILE == "standard":
        return STANDARD_MODULES
    elif TOOL_PROFILE == "extended":
        return EXTENDED_MODULES
    elif TOOL_PROFILE == "full":
        return FULL_MODULES
    elif TOOL_PROFILE == "custom":
        # 用户可以在这里自定义模块列表
        return CUSTOM_MODULES
    else:
        return FOCUSED_MODULES  # 默认使用focused配置

# 自定义模块列表 (当TOOL_PROFILE = "custom"时使用)
CUSTOM_MODULES = [
    # 添加你需要的模块
    "scene",
    "object",
    "utility",
    "export",
    "modeling",
    "material",
    "character_templates",
    "animation",
    "lighting",
    "camera",
    "render",
    "world",
]

# ============================================================
# 模块到注册函数的映射
# ============================================================

MODULE_REGISTRY = {
    "scene": "register_scene_tools",
    "object": "register_object_tools",
    "modeling": "register_modeling_tools",
    "material": "register_material_tools",
    "lighting": "register_lighting_tools",
    "camera": "register_camera_tools",
    "animation": "register_animation_tools",
    "character": "register_character_tools",
    "rigging": "register_rigging_tools",
    "render": "register_render_tools",
    "utility": "register_utility_tools",
    "export": "register_export_tools",
    "character_templates": "register_character_template_tools",
    "auto_rig": "register_auto_rig_tools",
    "animation_presets": "register_animation_preset_tools",
    "physics": "register_physics_tools",
    "scene_advanced": "register_scene_advanced_tools",
    "batch": "register_batch_tools",
    "curves": "register_curve_tools",
    "uv_mapping": "register_uv_tools",
    "nodes": "register_node_tools",
    "compositor": "register_compositor_tools",
    "video_editing": "register_video_editing_tools",
    "sculpting": "register_sculpting_tools",
    "texture_painting": "register_texture_painting_tools",
    "grease_pencil": "register_grease_pencil_tools",
    "simulation": "register_simulation_tools",
    "hair": "register_hair_tools",
    "assets": "register_asset_tools",
    "addons": "register_addon_tools",
    "world": "register_world_tools",
    "constraints": "register_constraint_tools",
    "mocap": "register_mocap_tools",
    "preferences": "register_preferences_tools",
    "external": "register_external_tools",
    "ai_assist": "register_ai_assist_tools",
    "versioning": "register_versioning_tools",
    "ai_generation": "register_ai_generation_tools",
    "vr_ar": "register_vr_ar_tools",
    "substance": "register_substance_tools",
    "zbrush": "register_zbrush_tools",
    "cloud_render": "register_cloud_render_tools",
    "collaboration": "register_collaboration_tools",
    "training": "register_training_tools",
    "sport_character": "register_sport_character_tools",
    "skills": "register_skill_tools",
    "mesh_edit_advanced": "register_mesh_edit_advanced_tools",
    "style_presets": "register_style_preset_tools",
    "procedural_materials": "register_procedural_material_tools",
    "pipeline": "register_pipeline_tools",
    "quality_audit": "register_quality_audit_tools",
}

# Skills 模块不在 MODULE_REGISTRY 中使用常规映射
# 因为它通过 skill_manager 动态加载

# ============================================================
# 打印配置信息
# ============================================================

def print_config_info():
    """打印当前配置信息"""
    enabled = get_enabled_modules()
    print(f"Tool Profile: {TOOL_PROFILE}")
    print(f"Enabled Modules: {len(enabled)}")
    print(f"Estimated Tools: ~{len(enabled) * 7} (approximately)")
    print("\nEnabled modules:")
    for module in enabled:
        print(f"  - {module}")

if __name__ == "__main__":
    print_config_info()
