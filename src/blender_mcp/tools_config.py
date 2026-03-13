"""
Tool Module Configuration - Control which tool modules are enabled

Usage:
1. Set TOOL_PROFILE = "minimal" to enable minimal tools (~30)
2. Set TOOL_PROFILE = "standard" to enable standard tools (~80)
3. Set TOOL_PROFILE = "full" to enable all tools (~300)

Or manually set the ENABLED_MODULES list.
"""

# Tool Profile
# Options: "skill", "minimal", "focused", "standard", "extended", "full", "custom"
#
# Recommended profiles:
# - "skill": ~31 tools + on-demand loading - AI-driven dynamic tool management (recommended)
# - "focused": ~89 tools - covers most automation needs
# - "standard": ~153 tools - includes character and scene features
# - "full": ~326 tools - all features
TOOL_PROFILE = "skill"

# ============================================================
# Tool Module Categories
# ============================================================

# Core tools - must be enabled, these are the most basic features
CORE_MODULES = [
    "scene",  # Scene management (5 tools)
    "object",  # Object operations (15 tools)
    "utility",  # Utility tools (8 tools) - includes execute_python
    "export",  # Export tools (4 tools)
]

# Modeling tools - create and edit 3D models
MODELING_MODULES = [
    "modeling",  # Modeling tools (20 tools)
    "material",  # Material system (15 tools)
    "curves",  # Curve tools (8 tools)
    "uv_mapping",  # UV mapping (10 tools)
    "mesh_edit_advanced",  # Advanced mesh editing (5 tools) - inset/bridge/spin/edge_mark/select_by_trait/vertex_group/vertex_color
    "style_presets",  # Style presets (3 tools) - style_setup/outline/bake_maps
    "procedural_materials",  # Procedural materials (2 tools) - 50+ presets/wear effects
]

# Character tools - character creation and animation
CHARACTER_MODULES = [
    "character_templates",  # Character templates (8 tools)
    "rigging",  # Rigging (10 tools)
    "auto_rig",  # Auto rigging (5 tools)
    "animation",  # Animation tools (12 tools)
    "animation_presets",  # Animation presets (5 tools)
]

# Scene tools - scene setup and rendering
SCENE_MODULES = [
    "lighting",  # Lighting (5 tools)
    "camera",  # Camera (4 tools)
    "world",  # World settings (4 tools)
    "render",  # Render (5 tools)
    "scene_advanced",  # Advanced scene (6 tools)
]

# Physics tools - physics simulation
PHYSICS_MODULES = [
    "physics",  # Physics system (8 tools)
    "constraints",  # Constraint system (10 tools)
]

# Batch tools - bulk operations
BATCH_MODULES = [
    "batch",  # Batch tools (6 tools)
    "assets",  # Asset management (5 tools)
]

# Automation pipeline tools - one-click pipelines and quality gates
AUTOMATION_MODULES = [
    "pipeline",  # Automation pipeline (3 tools) - character/prop/scene
    "quality_audit",  # Quality audit (4 tools) - topology/UV/performance/overall score
]

# Advanced tools - professional features, less commonly used
ADVANCED_MODULES = [
    "nodes",  # Node tools (8 tools)
    "compositor",  # Compositor (6 tools)
    "sculpting",  # Sculpting (10 tools)
    "texture_painting",  # Texture painting (8 tools)
    "grease_pencil",  # Grease Pencil (10 tools)
    "hair",  # Hair (8 tools)
    "simulation",  # Simulation (10 tools)
    "video_editing",  # Video editing (8 tools)
]

# External integration tools - integration with other software
EXTERNAL_MODULES = [
    "external",  # External integration (5 tools)
    "substance",  # Substance (5 tools)
    "zbrush",  # ZBrush (5 tools)
    "mocap",  # Motion capture (5 tools)
]

# AI and cloud tools - require external services
AI_CLOUD_MODULES = [
    "ai_assist",  # AI assist (6 tools)
    "ai_generation",  # AI generation (8 tools)
    "cloud_render",  # Cloud render (6 tools)
    "collaboration",  # Collaboration (8 tools)
]

# System tools - system settings and management
SYSTEM_MODULES = [
    "addons",  # Addon management (4 tools)
    "preferences",  # Preferences (5 tools)
    "versioning",  # Version control (8 tools)
    "vr_ar",  # VR/AR (8 tools)
]

# Character extensions - additional character features
CHARACTER_EXTRA_MODULES = [
    "character",  # Character extensions (10 tools)
]

# Sport character tools - dedicated to athlete 3D modeling
SPORT_CHARACTER_MODULES = [
    "sport_character",  # Sport character (7 tools) - athlete creation, gear, sportswear, poses, reference images, optimization, scenes
]

# Training system - interactive learning and project exercises
TRAINING_MODULES = [
    "training",  # Training system (11 tools) - course browsing, exercise execution, progress tracking
]

# ============================================================
# Preset Configurations
# ============================================================

# Skill profile (~31 tools) - core + skill management meta-tools (recommended)
# AI loads tool groups on demand via list_skills/activate_skill/deactivate_skill
# Only core tools at startup; modeling/materials/animation etc. loaded as needed
SKILL_MODULES = CORE_MODULES + ["skills"]

# Minimal profile (~28 tools) - core functionality only
MINIMAL_MODULES = CORE_MODULES

# Focused profile (~89 tools) - full automation capability with streamlined tool count (recommended)
# Core concept: utility.execute_python can execute arbitrary Python code,
# so only the most commonly used convenience tools are needed; complex features via execute_python
FOCUSED_MODULES = [
    # Core features (28 tools)
    "scene",  # Scene management - required
    "object",  # Object operations - required
    "utility",  # Utility tools (includes execute_python) - most important!
    "export",  # Export tools - required
    # Modeling basics (38 tools)
    "modeling",  # Modeling tools - create geometry
    "material",  # Material system - create materials
    # Style coverage (pixel to AAA) - 10 tools
    "mesh_edit_advanced",  # Advanced mesh: inset/bridge/spin/edge_mark/select_trait/vertex_group/vertex_color
    "style_presets",  # Style presets: style_setup/outline/bake_maps
    "procedural_materials",  # Procedural materials: 50+ presets/wear effects
    # Character templates (6 tools)
    "character_templates",  # Character templates - quick chibi character creation
    # Sport character (7 tools)
    "sport_character",  # Sport character - athlete modeling, gear, sportswear, poses, web optimization
    # Training system (11 tools)
    "training",  # Training system - interactive learning and project exercises
    "pipeline",  # End-to-end automation pipeline
    "quality_audit",  # Production quality audit
]
# Total: ~89 tools
#
# Style coverage tools explained:
# - mesh_edit_advanced: inset_faces, bridge, spin, edge_mark, select_by_trait, vertex_group, vertex_color
# - style_presets: one-click style config (PIXEL/LOW_POLY/TOON/PBR/AAA), outline effects, bake workflow
# - procedural_materials: 50+ procedural material presets (metal/wood/stone/fabric/nature/skin/effects/toon), wear effects
# Note: animation, lighting, render features can be achieved via utility.execute_python

# Standard profile (~153 tools) - includes more convenience features
STANDARD_MODULES = (
    CORE_MODULES + MODELING_MODULES + CHARACTER_MODULES + SCENE_MODULES + AUTOMATION_MODULES
)

# Extended profile (~120 tools) - includes physics and batch processing
EXTENDED_MODULES = STANDARD_MODULES + PHYSICS_MODULES + BATCH_MODULES

# Full profile (~326 tools) - all features
FULL_MODULES = (
    CORE_MODULES
    + MODELING_MODULES
    + CHARACTER_MODULES
    + SCENE_MODULES
    + PHYSICS_MODULES
    + BATCH_MODULES
    + AUTOMATION_MODULES
    + ADVANCED_MODULES
    + EXTERNAL_MODULES
    + AI_CLOUD_MODULES
    + SYSTEM_MODULES
    + CHARACTER_EXTRA_MODULES
    + SPORT_CHARACTER_MODULES
    + TRAINING_MODULES
)

# ============================================================
# Get Enabled Module List
# ============================================================


def get_enabled_modules() -> list[str]:
    """Return the list of enabled modules based on TOOL_PROFILE"""
    profile_map = {
        "skill": SKILL_MODULES,
        "minimal": MINIMAL_MODULES,
        "focused": FOCUSED_MODULES,
        "standard": STANDARD_MODULES,
        "extended": EXTENDED_MODULES,
        "full": FULL_MODULES,
        "custom": CUSTOM_MODULES,
    }
    return profile_map.get(TOOL_PROFILE, FOCUSED_MODULES)


# Custom module list (used when TOOL_PROFILE = "custom")
CUSTOM_MODULES = [
    # Add the modules you need
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
# Module to Register Function Mapping
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

# The skills module does not use the standard mapping in MODULE_REGISTRY
# because it is dynamically loaded via skill_manager

# ============================================================
# Print Configuration Info
# ============================================================


def print_config_info() -> None:
    """Print current configuration info"""
    enabled = get_enabled_modules()
    print(f"Tool Profile: {TOOL_PROFILE}")
    print(f"Enabled Modules: {len(enabled)}")
    print(f"Estimated Tools: ~{len(enabled) * 7} (approximately)")
    print("\nEnabled modules:")
    for module in enabled:
        print(f"  - {module}")


if __name__ == "__main__":
    print_config_info()
