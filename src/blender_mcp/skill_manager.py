"""
Skill Manager - Core manager for on-demand tool group loading

Skills system architecture:
- On startup, only core tools (~30) + 3 skill meta-tools are registered
- AI loads tool groups on demand via activate_skill()
- Each skill provides: tool group registration + workflow guide text
- Clients are notified of tool list changes via MCP tools/list_changed

Usage:
1. Set TOOL_PROFILE = "skill" to enable skill mode
2. AI calls list_skills() to view available skills
3. AI calls activate_skill("modeling") to load modeling tools on demand
4. AI uses the loaded tools to complete tasks
5. AI calls deactivate_skill("modeling") to unload the tool group
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
    """Skill metadata"""
    name: str
    description: str
    modules: list[str]
    workflow_guide: str = ""
    estimated_tools: int = 0
    tags: list[str] = field(default_factory=list)


# ============================================================
# Skill Registry - Defines all available skills and their tool module mappings
# ============================================================

SKILL_DEFINITIONS: dict[str, SkillInfo] = {
    "modeling": SkillInfo(
        name="modeling",
        description="3D modeling tools - mesh editing, modifiers (45 types), curves, UV mapping, parametric modeling for all styles",
        modules=["modeling", "curves", "uv_mapping"],
        estimated_tools=38,
        tags=["3d", "mesh", "modeling"],
        workflow_guide="""## Modeling Skill Workflow Guide

### Common Workflows:
1. **Basic Modeling**: blender_create_object (create geometry) -> blender_add_modifier (add modifier) -> blender_apply_modifier (apply)
2. **Curve Modeling**: Curve tools to create paths -> add Curve/Bevel modifiers
3. **UV Unwrapping**: Select object -> blender_uv_unwrap -> blender_uv_project

### Recommended mesh_params by Style:
| Style | Sphere segments | Cylinder vertices | ICO subdivisions |
|-------|----------------|-------------------|------------------|
| Pixel | 4-6 | 4-6 | 1 |
| Low Poly | 6-12 | 5-8 | 1 |
| Stylized/Toon | 16-24 | 12-16 | 2 |
| Semi Realistic | 32 | 24-32 | 2-3 |
| PBR/AAA | 32-64 | 32 | 3-4 |

Example: `blender_object_create(type="UV_SPHERE", mesh_params={"segments": 8, "ring_count": 6})`

### Common Modifiers by Style:
- **Pixel**: REMESH(Blocks), ARRAY
- **Low Poly**: MIRROR, ARRAY, SOLIDIFY, TRIANGULATE
- **Stylized/Toon**: SUBSURF(1-2), BEVEL, MIRROR
- **Sci-Fi Hard Surface**: BOOLEAN, ARRAY, BEVEL, SOLIDIFY, SCREW, MIRROR
- **PBR/AAA**: SUBSURF(2-3), MIRROR, MULTIRES, BEVEL, SHRINKWRAP

### Supports 45 Modifier Types:
Common: SUBDIVISION, MIRROR, ARRAY, SOLIDIFY, BEVEL, BOOLEAN, REMESH, SCREW, WIREFRAME, WELD, SHRINKWRAP, SIMPLE_DEFORM

### Tips:
- Complex operations can use blender_execute_python to directly call Blender Python API
- See docs/blender_style_modeling_workflows.md for detailed style workflows
""",
    ),
    
    "materials": SkillInfo(
        name="materials",
        description="Material system - standard materials, procedural materials (67 presets in 8 categories), wear effects (7 types)",
        modules=["material", "procedural_materials"],
        estimated_tools=17,
        tags=["material", "shader", "texture"],
        workflow_guide="""## Materials Skill Workflow Guide

### Common Workflows:
1. **Standard Material**: blender_create_material -> blender_set_material_color -> blender_assign_material
2. **Procedural Material**: blender_procedural_material one-click creation (67 presets, 8 categories)
3. **Wear Effects**: blender_material_wear to add wear/aging effects

### Full Procedural Material Categories:
- **metal** (10): STEEL, IRON, GOLD, SILVER, BRONZE, COPPER, CHROME, BRUSHED_METAL, RUSTY_METAL, DAMASCUS
- **wood** (8): OAK, PINE, CHERRY, WALNUT, BIRCH, BAMBOO, PLYWOOD, AGED_WOOD
- **stone** (9): GRANITE, MARBLE, LIMESTONE, SLATE, COBBLESTONE, SANDSTONE, BRICK, TILE, CONCRETE
- **fabric** (8): COTTON, SILK, LEATHER, DENIM, VELVET, CANVAS, WOOL, CHAIN_MAIL
- **nature** (10): GRASS, DIRT, SAND, SNOW, MUD, GRAVEL, MOSS, LAVA, WATER, ICE
- **skin** (4): SKIN_REALISTIC, SKIN_STYLIZED, SCALES, CARTOON_SKIN
- **effect** (7): GLASS, CRYSTAL, HOLOGRAM, ENERGY, PORTAL, EMISSION_GLOW, FORCE_FIELD
- **toon** (7): TOON_BASIC, TOON_METAL, TOON_SKIN, TOON_FABRIC, ANIME_HAIR, GENSHIN_STYLE, CEL_SHADE

### Wear Effects (7 types):
EDGE_WEAR, SCRATCHES, RUST, DIRT, DUST, MOSS, PAINT_CHIP

### Recommended Materials by Style:
- **Pixel/Low Poly**: TOON_BASIC + vertex color
- **Toon/Chibi**: CEL_SHADE, GENSHIN_STYLE, ANIME_HAIR, TOON_SKIN
- **Sci-Fi**: CHROME, BRUSHED_METAL, ENERGY, HOLOGRAM, FORCE_FIELD
- **PBR Realistic**: All metal/wood/stone/fabric/nature/skin presets
- **AAA**: SKIN_REALISTIC + all presets + layered wear effects

### Tips:
- Procedural materials auto-create full node trees, no manual connections needed
- Wear effects can be stacked; intensity controls strength (0-1)
- color_override can override preset base color
""",
    ),
    
    "style": SkillInfo(
        name="style",
        description="Style presets - pixel to AAA one-click environment setup (camera/Bloom/AO/denoising), outline effects, high-to-low poly baking",
        modules=["style_presets", "mesh_edit_advanced"],
        estimated_tools=8,
        tags=["style", "pixel", "toon", "pbr", "aaa", "sci-fi"],
        workflow_guide="""## Style Skill Workflow Guide

### One-Click Style Configuration (blender_style_setup):
8 styles, auto-configures render engine + samples + color management + extras:

| Style | Engine | Auto Configuration |
|-------|--------|--------------------|
| PIXEL | EEVEE | Camera -> Orthographic, Texture -> Closest, Bloom/AO/SSR off |
| LOW_POLY | EEVEE | Bloom/AO/SSR off |
| STYLIZED | EEVEE | Bloom on (low intensity), AO off |
| TOON | EEVEE | Bloom on (low intensity), AO off |
| HAND_PAINTED | EEVEE | - |
| SEMI_REALISTIC | EEVEE | AO on, SSR on |
| PBR_REALISTIC | Cycles | Denoising on (OpenImageDenoise) |
| AAA | Cycles | Denoising on (OpenImageDenoise) |

Also auto-sets Flat/Smooth Shading and texture interpolation for specified objects.

### Outline Effects (blender_outline_effect):
- SOLIDIFY: Solidify + flipped normals (real-time visible, common in games, recommended for toon)
- FREESTYLE: Render lines (visible only at render time, variable line width)
- GREASE_PENCIL: Line Art outline (real-time visible, manually editable)

### Advanced Mesh Editing:
- blender_mesh_edit_advanced: inset/bridge/spin/knife/fill/gridFill/separate/symmetrize/poke/triangulate/trisToQuads/dissolve
- blender_mesh_edge_mark: crease/sharp/seam/bevel_weight
- blender_mesh_select_by_trait: non_manifold/loose/interior/face_sides/ungrouped/boundary/sharp/linked_flat
- blender_vertex_group: create/assign/remove/select vertex groups
- blender_vertex_color: create/paint/fill vertex colors (core for Low Poly)

### Bake Workflow (blender_bake_maps):
High-poly -> low-poly baking: NORMAL, AO, CURVATURE, DIFFUSE, ROUGHNESS, COMBINED
Used for PBR_REALISTIC and AAA style texture creation.

### Sci-Fi Style Tips:
1. Hard surface modeling: Boolean difference cuts + Array repeats + Bevel chamfers
2. Materials: Activate materials skill -> CHROME/ENERGY/HOLOGRAM/FORCE_FIELD
3. Emissive: Emission + EEVEE Bloom combination
4. See docs/blender_style_modeling_workflows.md for detailed workflows
""",
    ),
    
    "character": SkillInfo(
        name="character",
        description="Character creation - chibi character templates, rigging, auto-rigging",
        modules=["character_templates", "rigging", "auto_rig"],
        estimated_tools=23,
        tags=["character", "rigging", "template"],
        workflow_guide="""## Character Skill Workflow Guide

### Quick Chibi Character Creation:
1. blender_create_character_template -> select body preset (chibi/standard/realistic)
2. Adjust proportion parameters (head_ratio, body_width, etc.)
3. Add clothing and accessories

### Rigging Workflow:
1. Create Armature -> add bone hierarchy
2. blender_auto_rig auto-rig (automatic weights)
3. Adjust weight painting

### Tips:
- Chibi characters: head_ratio recommended 2.5-3.0
- Ensure correct mesh normals before auto-rigging
- Bone naming follows Left/Right convention for mirror support
""",
    ),
    
    "animation": SkillInfo(
        name="animation",
        description="Animation tools - keyframes, animation presets, timeline management",
        modules=["animation", "animation_presets"],
        estimated_tools=17,
        tags=["animation", "keyframe", "timeline"],
        workflow_guide="""## Animation Skill Workflow Guide

### Basic Animation:
1. Select object -> blender_insert_keyframe (location/rotation/scale)
2. Set frame range -> change frame -> insert next keyframe
3. Adjust interpolation curves (LINEAR/BEZIER/CONSTANT)

### Animation Presets:
- Walk cycle, breathing, bounce, and other preset animations
- Can be applied to rigged characters

### Tips:
- Use CONSTANT interpolation for pixel-art style animation
- Ensure first and last frames match for looping animations
""",
    ),
    
    "scene_setup": SkillInfo(
        name="scene_setup",
        description="Scene setup - lighting, camera, world environment, render settings",
        modules=["lighting", "camera", "world", "render"],
        estimated_tools=18,
        tags=["scene", "lighting", "camera", "render"],
        workflow_guide="""## Scene Setup Skill Workflow Guide

### Standard Scene Configuration:
1. **Lighting**: Three-point lighting (Key/Fill/Rim) or HDRI environment
2. **Camera**: Set focal length, depth of field, composition
3. **World**: Background color/HDRI/volumetric fog
4. **Render**: Choose engine (EEVEE/Cycles), set samples and resolution

### Quick Presets:
- Product display: 3-point lighting + white background + shallow DOF
- Outdoor scene: HDRI + sun lamp + volumetric scattering
- Toon render: Flat lighting + solid background + Freestyle outlines
""",
    ),

    "automation": SkillInfo(
        name="automation",
        description="Automation pipeline - one-click character/prop/scene generation + quality audit loop",
        modules=["pipeline", "quality_audit", "style_presets", "procedural_materials"],
        estimated_tools=12,
        tags=["automation", "pipeline", "quality", "style", "production"],
        workflow_guide="""## Automation Skill Workflow Guide

### Recommended Full-Auto Pipeline:
1. `blender_pipeline_generate_character` - generate character body (template/clothing/accessories/auto-rig)
2. `blender_pipeline_generate_prop` - batch generate props (with procedural materials and UVs)
3. `blender_pipeline_assemble_scene` - auto-assemble environment, lighting, camera, and render settings
4. `blender_quality_audit_full` - run topology + UV + performance audit and output final score

### Multi-Style Recommendations:
- Pixel/Low Poly: style=PIXEL/LOW_POLY + quality_target=draft/production
- Anime/Toon: style=TOON/STYLIZED + outline + GENSHIN_STYLE/TOON materials
- Realistic/AAA: style=PBR_REALISTIC/AAA + higher samples + quality audit target=desktop/aaa

### Quality Gate Guidelines:
- Topology: N-gon/non-manifold/loose verts should be zero or near-zero
- UV: Average score >= 80, minimize overlapping faces
- Performance: Stay within target platform triangles/draw calls budget

### Tips:
- This skill focuses on "auto-generate + auto-audit", ideal for batch asset production and iteration
- For manual fine-tuning, activate modeling/materials/advanced_3d skills as needed
""",
    ),
    
    "physics": SkillInfo(
        name="physics",
        description="Physics simulation - rigid body, cloth, fluid, constraint system",
        modules=["physics", "constraints"],
        estimated_tools=18,
        tags=["physics", "simulation", "constraints"],
        workflow_guide="""## Physics Skill Workflow Guide

### Physics Simulation:
- Rigid body: Set Active/Passive -> adjust mass/friction -> bake
- Cloth: Add Cloth modifier -> set collision objects -> simulate
- Fluid: Domain + Inflow/Outflow -> bake

### Constraint System:
- Track To, Copy Location/Rotation, IK, etc.
- Used for camera tracking, mechanical linkage, character constraints

### Tips:
- Preview at low resolution first, then increase quality for final bake
""",
    ),
    
    "batch_assets": SkillInfo(
        name="batch_assets",
        description="Batch processing and asset management - bulk operations, asset library management",
        modules=["batch", "assets"],
        estimated_tools=11,
        tags=["batch", "assets", "pipeline"],
        workflow_guide="""## Batch & Assets Skill Workflow Guide

### Batch Operations:
- Bulk rename, bulk material replace, bulk export
- Bulk modifier application

### Asset Management:
- Mark assets, browse asset library, asset reuse
""",
    ),
    
    "advanced_3d": SkillInfo(
        name="advanced_3d",
        description="Advanced 3D tools - node editing, compositor, sculpting, texture painting",
        modules=["nodes", "compositor", "sculpting", "texture_painting"],
        estimated_tools=32,
        tags=["nodes", "compositor", "sculpting", "painting"],
        workflow_guide="""## Advanced 3D Skill Workflow Guide

### Geometry Nodes:
- Create procedural geometry, scatter systems, parametric models

### Compositor:
- Post-processing: glow, color correction, depth of field

### Sculpting:
- High-poly detail sculpting, multi-resolution workflow

### Texture Painting:
- Paint textures directly on models
""",
    ),
    
    "sport_character": SkillInfo(
        name="sport_character",
        description="Sport character tools - athlete modeling, gear, sportswear, poses",
        modules=["sport_character"],
        estimated_tools=7,
        tags=["sport", "athlete", "character"],
        workflow_guide="""## Sport Character Skill Workflow Guide

### Athlete Character Creation:
1. Select sport type (table tennis/basketball/soccer, etc.)
2. Create base character body
3. Add sport equipment and uniforms
4. Set sport poses
5. Web-optimized export (GLB/GLTF)
""",
    ),
    
    "training": SkillInfo(
        name="training",
        description="Training system - interactive Blender learning courses and project exercises",
        modules=["training"],
        estimated_tools=11,
        tags=["training", "learning", "tutorial"],
        workflow_guide="""## Training Skill Workflow Guide

### Using the Training System:
1. Browse course list -> select a course
2. Start exercise -> follow step-by-step instructions
3. System auto-verifies operation results
4. View progress and scores
""",
    ),
}


class SkillManager:
    """Skill Manager - Handles dynamic loading/unloading of tool groups"""
    
    def __init__(self, server: "BlenderMCPServer"):
        self.server = server
        self._active_skills: dict[str, list[str]] = {}   # skill_name -> [tool_names]
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
        """Get a snapshot of currently registered tool names (synchronous)."""
        tool_manager = getattr(self.server.mcp, "_tool_manager", None)
        tools = getattr(tool_manager, "_tools", None)
        if isinstance(tools, dict):
            return set(tools.keys())
        return set()

    def _remove_tool_by_name(self, tool_name: str) -> bool:
        """Remove a registered tool, compatible with different FastMCP versions."""
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
        """Activate a skill, dynamically registering its tool modules

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
                
                # Record tool list before registration
                before = self._tool_names_snapshot()

                # Call register function
                register_func(self.server.mcp, self.server)

                # Calculate newly registered tools
                after = self._tool_names_snapshot()
                new_tools = after - before
                registered_tools.extend(new_tools)
                
                logger.info(f"Skill '{skill_name}': loaded module '{module_name}' ({len(new_tools)} tools)")
                
            except Exception as e:
                logger.error(f"Skill '{skill_name}': failed to load module '{module_name}': {e}")
        
        self._active_skills[skill_name] = registered_tools
        
        return True, f"Activated skill '{skill_name}' with {len(registered_tools)} tools", registered_tools
    
    def deactivate_skill(self, skill_name: str) -> tuple[bool, str]:
        """Deactivate a skill, removing its tools

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
        """Get a status summary of all skills"""
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
