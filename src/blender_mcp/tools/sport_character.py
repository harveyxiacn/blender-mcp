"""
运动角色工具

提供运动员角色建模功能，支持Q版/写实运动角色创建，
包含乒乓球等运动专用装备、运动服、运动姿势、参考图加载、Web优化导出等。

专门用于：
- 樊振东球迷网3D模型制作
- 乒乓球/体育类游戏角色建模
- Q版运动员（泡泡玛特风格）
"""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from blender_mcp.server import BlenderMCPServer


# ==================== 枚举定义 ====================

class SportType(str, Enum):
    """运动类型"""
    TABLE_TENNIS = "TABLE_TENNIS"
    BASKETBALL = "BASKETBALL"
    SOCCER = "SOCCER"
    BADMINTON = "BADMINTON"
    TENNIS = "TENNIS"
    VOLLEYBALL = "VOLLEYBALL"


class CharacterStyle(str, Enum):
    """角色风格"""
    CHIBI = "CHIBI"           # Q版/泡泡玛特 (头身比 2:1~2.5:1)
    ANIME = "ANIME"           # 动漫风 (头身比 5:1~6:1)
    STYLIZED = "STYLIZED"     # 风格化 (头身比 4:1)
    REALISTIC = "REALISTIC"   # 写实 (头身比 7:1~8:1)


class AthletePreset(str, Enum):
    """运动员预设"""
    FAN_ZHENDONG = "FAN_ZHENDONG"     # 樊振东
    CUSTOM = "CUSTOM"                  # 自定义


class EquipmentType(str, Enum):
    """运动装备类型"""
    # 乒乓球
    PADDLE = "PADDLE"               # 乒乓球拍
    BALL = "BALL"                   # 乒乓球
    TABLE = "TABLE"                 # 乒乓球台
    NET = "NET"                     # 球网
    # 通用配件
    WRISTBAND = "WRISTBAND"         # 护腕
    HEADBAND = "HEADBAND"           # 头带
    MEDAL_GOLD = "MEDAL_GOLD"       # 金牌
    MEDAL_SILVER = "MEDAL_SILVER"   # 银牌
    MEDAL_BRONZE = "MEDAL_BRONZE"   # 铜牌
    TROPHY = "TROPHY"              # 奖杯
    TOWEL = "TOWEL"                # 毛巾


class UniformTeam(str, Enum):
    """运动队伍"""
    CHINA_NATIONAL = "CHINA_NATIONAL"       # 中国国家队（红色）
    CHINA_NATIONAL_BLUE = "CHINA_NATIONAL_BLUE"  # 中国队（蓝色客场）
    CHINA_NATIONAL_WHITE = "CHINA_NATIONAL_WHITE"  # 中国队（白色领奖服）
    CLUB_SHENZHEN = "CLUB_SHENZHEN"         # 深圳俱乐部
    CLUB_CUSTOM = "CLUB_CUSTOM"             # 自定义俱乐部
    TRAINING = "TRAINING"                    # 训练服


class UniformStyle(str, Enum):
    """运动服类型"""
    MATCH_JERSEY = "MATCH_JERSEY"            # 比赛球衣
    TRAINING_WEAR = "TRAINING_WEAR"          # 训练服
    AWARD_CEREMONY = "AWARD_CEREMONY"        # 领奖服
    WARMUP_JACKET = "WARMUP_JACKET"          # 热身外套


class SportPose(str, Enum):
    """运动姿势"""
    READY_STANCE = "READY_STANCE"            # 准备姿势
    FOREHAND_ATTACK = "FOREHAND_ATTACK"      # 正手进攻
    BACKHAND_ATTACK = "BACKHAND_ATTACK"      # 反手拉球
    SERVE_TOSS = "SERVE_TOSS"               # 发球抛球
    SERVE_HIT = "SERVE_HIT"                 # 发球击球
    FOREHAND_LOOP = "FOREHAND_LOOP"          # 正手弧圈球
    CELEBRATE = "CELEBRATE"                  # 庆祝
    FIST_PUMP = "FIST_PUMP"                 # 握拳庆祝
    HOLD_MEDAL = "HOLD_MEDAL"               # 展示奖牌
    RECEIVING_AWARD = "RECEIVING_AWARD"       # 领奖
    T_POSE = "T_POSE"                       # T-Pose (建模/绑定用)
    A_POSE = "A_POSE"                       # A-Pose (建模/绑定用)


class ReferenceView(str, Enum):
    """参考图视角"""
    FRONT = "FRONT"
    SIDE = "SIDE"
    BACK = "BACK"
    THREE_QUARTER = "THREE_QUARTER"


class SceneType(str, Enum):
    """场景类型"""
    MATCH = "MATCH"                   # 比赛场景
    TRAINING = "TRAINING"             # 训练场景
    AWARD_CEREMONY = "AWARD_CEREMONY" # 颁奖场景
    PORTRAIT = "PORTRAIT"             # 肖像/展示场景
    PRODUCT = "PRODUCT"               # 产品展示（手办风）


class OptimizeTarget(str, Enum):
    """优化目标平台"""
    WEB = "WEB"             # Web端 (3000-4500 tris)
    MOBILE = "MOBILE"       # 移动端 (5000-8000 tris)
    PC_CONSOLE = "PC_CONSOLE"  # PC/主机 (10000-20000 tris)
    PRINT_3D = "PRINT_3D"   # 3D打印 (高精度)


# ==================== 输入模型 ====================

class SportCharacterCreateInput(BaseModel):
    """创建运动角色输入"""
    name: str = Field(default="Athlete", description="角色名称")
    sport: SportType = Field(default=SportType.TABLE_TENNIS, description="运动类型")
    style: CharacterStyle = Field(default=CharacterStyle.CHIBI, description="角色风格: CHIBI(Q版2.5:1), ANIME(动漫5:1), STYLIZED(风格化4:1), REALISTIC(写实7:1)")
    preset: AthletePreset = Field(default=AthletePreset.FAN_ZHENDONG, description="运动员预设: FAN_ZHENDONG(樊振东), CUSTOM(自定义)")
    height: float = Field(default=1.0, description="角色整体高度（米），Q版建议0.8-1.2", ge=0.3, le=3.0)
    head_body_ratio: Optional[float] = Field(default=None, description="头身比覆盖值，不填则使用风格默认值。Q版2.0-2.5，动漫5-6，写实7-8")
    skin_color: Optional[List[float]] = Field(default=None, description="皮肤颜色 [r, g, b, a]，不填则使用预设默认")
    build: str = Field(default="athletic", description="体格: slim(纤细), athletic(运动型), muscular(肌肉型), stocky(敦实)")
    create_armature: bool = Field(default=True, description="是否创建骨骼系统")
    face_count_budget: int = Field(default=4500, description="面数预算（三角面），Web: 3000-4500, PC: 5000-20000", ge=1000, le=50000)


class SportEquipmentAddInput(BaseModel):
    """添加运动装备输入"""
    character_name: str = Field(..., description="角色名称")
    equipment_type: EquipmentType = Field(..., description="装备类型")
    attach_to: str = Field(default="auto", description="附着位置: auto(自动), right_hand(右手), left_hand(左手), neck(颈部), head(头部), waist(腰部)")
    color: Optional[List[float]] = Field(default=None, description="装备主色 [r, g, b]")
    secondary_color: Optional[List[float]] = Field(default=None, description="装备次色 [r, g, b]")
    scale: float = Field(default=1.0, description="装备缩放", ge=0.1, le=3.0)


class SportUniformCreateInput(BaseModel):
    """创建运动服输入"""
    character_name: str = Field(..., description="角色名称")
    team: UniformTeam = Field(default=UniformTeam.CHINA_NATIONAL, description="队伍")
    uniform_style: UniformStyle = Field(default=UniformStyle.MATCH_JERSEY, description="运动服类型")
    jersey_number: int = Field(default=20, description="球衣号码（樊振东为20号）", ge=0, le=99)
    player_name: str = Field(default="FAN ZHENDONG", description="球衣背面名字")
    brand: str = Field(default="Li-Ning", description="品牌: Li-Ning, Nike, Adidas, Butterfly, Custom")
    custom_primary_color: Optional[List[float]] = Field(default=None, description="自定义主色 [r, g, b]，仅CLUB_CUSTOM时有效")
    custom_secondary_color: Optional[List[float]] = Field(default=None, description="自定义次色 [r, g, b]，仅CLUB_CUSTOM时有效")


class SportPoseSetInput(BaseModel):
    """设置运动姿势输入"""
    character_name: str = Field(..., description="角色名称")
    pose: SportPose = Field(default=SportPose.READY_STANCE, description="运动姿势")
    intensity: float = Field(default=1.0, description="姿势强度/夸张程度，Q版建议1.2-1.5", ge=0.1, le=2.0)
    mirror: bool = Field(default=False, description="是否镜像（左手持拍）")
    add_motion_trail: bool = Field(default=False, description="是否添加运动轨迹效果")


class SportReferenceLoadInput(BaseModel):
    """加载参考图输入"""
    image_path: str = Field(..., description="参考图文件路径")
    view: ReferenceView = Field(default=ReferenceView.FRONT, description="视角: FRONT(正面), SIDE(侧面), BACK(背面), THREE_QUARTER(3/4视角)")
    opacity: float = Field(default=0.5, description="透明度", ge=0.1, le=1.0)
    offset_x: float = Field(default=0.0, description="X轴偏移")
    offset_y: float = Field(default=0.0, description="Y轴偏移")
    scale: float = Field(default=1.0, description="参考图缩放", ge=0.1, le=10.0)


class SportModelOptimizeInput(BaseModel):
    """运动模型优化输入"""
    character_name: str = Field(..., description="角色名称")
    target: OptimizeTarget = Field(default=OptimizeTarget.WEB, description="优化目标平台")
    target_tris: Optional[int] = Field(default=None, description="目标三角面数，不填则使用平台默认值")
    texture_size: int = Field(default=1024, description="贴图尺寸", ge=256, le=4096)
    generate_lod: bool = Field(default=False, description="是否生成LOD层级")
    lod_levels: int = Field(default=3, description="LOD层级数", ge=2, le=5)
    export_glb: bool = Field(default=True, description="是否同时导出GLB文件")
    export_path: Optional[str] = Field(default=None, description="导出路径，不填则使用当前blend文件同目录")
    apply_draco_compression: bool = Field(default=True, description="是否应用Draco压缩（GLB）")


class SportSceneSetupInput(BaseModel):
    """运动场景设置输入"""
    scene_type: SceneType = Field(default=SceneType.PORTRAIT, description="场景类型")
    character_name: Optional[str] = Field(default=None, description="要放入场景的角色名称")
    background_color: Optional[List[float]] = Field(default=None, description="背景颜色 [r, g, b]")
    use_hdri: bool = Field(default=False, description="是否使用HDRI环境光")
    camera_distance: float = Field(default=3.0, description="相机距离", ge=1.0, le=20.0)
    render_engine: str = Field(default="EEVEE", description="渲染引擎: EEVEE, CYCLES")


# ==================== 工具注册 ====================

def register_sport_character_tools(mcp: FastMCP, server: "BlenderMCPServer") -> None:
    """注册运动角色工具"""

    @mcp.tool(
        name="blender_sport_character_create",
        annotations={
            "title": "创建运动角色",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_sport_character_create(params: SportCharacterCreateInput) -> str:
        """创建运动员角色（支持Q版/写实/动漫风格）。

        根据运动类型和风格创建完整的运动员角色模型：
        - Q版(CHIBI): 泡泡玛特风格，头身比2:1~2.5:1，圆脸大眼，适合Web展示
        - 动漫(ANIME): 日漫风格，头身比5:1~6:1
        - 风格化(STYLIZED): 游戏风格化，头身比4:1
        - 写实(REALISTIC): 写实比例，头身比7:1~8:1

        内置运动员预设:
        - FAN_ZHENDONG: 樊振东 - 国乒主力，身高172cm，运动型体格，
          圆脸、短黑发、浓眉大眼、自信表情

        建模工作流遵循学习笔记最佳实践：
        - 基础球体→雕刻→减面→UV→色块材质→Rigify绑定
        - 面数预算控制：Web 3000-4500, PC 5000-20000
        - 自动创建顶点组用于服装绑定

        Args:
            params: 角色名称、运动类型、风格、体格、面数预算等

        Returns:
            创建结果，包含创建的部件列表
        """
        result = await server.execute_command(
            "sport_character", "create_character",
            {
                "name": params.name,
                "sport": params.sport.value,
                "style": params.style.value,
                "preset": params.preset.value,
                "height": params.height,
                "head_body_ratio": params.head_body_ratio,
                "skin_color": params.skin_color,
                "build": params.build,
                "create_armature": params.create_armature,
                "face_count_budget": params.face_count_budget,
            }
        )

        style_names = {
            "CHIBI": "Q版", "ANIME": "动漫", "STYLIZED": "风格化", "REALISTIC": "写实"
        }
        sport_names = {
            "TABLE_TENNIS": "乒乓球", "BASKETBALL": "篮球", "SOCCER": "足球",
            "BADMINTON": "羽毛球", "TENNIS": "网球", "VOLLEYBALL": "排球"
        }
        preset_names = {
            "FAN_ZHENDONG": "樊振东", "CUSTOM": "自定义"
        }

        if result.get("success"):
            data = result.get("data", {})
            parts = data.get("created_parts", [])
            style_name = style_names.get(params.style.value, params.style.value)
            sport_name = sport_names.get(params.sport.value, params.sport.value)
            preset_name = preset_names.get(params.preset.value, "")
            preset_info = f"（{preset_name}预设）" if params.preset != AthletePreset.CUSTOM else ""
            armature_info = "含骨骼" if data.get("has_armature") else "无骨骼"
            return (
                f"成功创建{style_name}{sport_name}运动员 '{params.name}'{preset_info}\n"
                f"高度: {params.height}m, 头身比: {data.get('head_body_ratio', 'N/A')}:1, "
                f"体格: {params.build}, {armature_info}\n"
                f"创建部件: {', '.join(parts)}\n"
                f"面数预算: {params.face_count_budget} tris"
            )
        else:
            return f"创建运动角色失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_equipment_add",
        annotations={
            "title": "添加运动装备",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_sport_equipment_add(params: SportEquipmentAddInput) -> str:
        """为运动角色添加运动装备。

        支持的装备类型：
        - 乒乓球: PADDLE(球拍), BALL(球), TABLE(球台), NET(球网)
        - 奖牌: MEDAL_GOLD(金牌), MEDAL_SILVER(银牌), MEDAL_BRONZE(铜牌)
        - 配件: WRISTBAND(护腕), HEADBAND(头带), TROPHY(奖杯), TOWEL(毛巾)

        球拍自动适配Q版/写实比例，默认附着到角色右手。
        奖牌默认挂在颈部。

        Args:
            params: 角色名称、装备类型、附着位置、颜色等

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "sport_character", "add_equipment",
            {
                "character_name": params.character_name,
                "equipment_type": params.equipment_type.value,
                "attach_to": params.attach_to,
                "color": params.color,
                "secondary_color": params.secondary_color,
                "scale": params.scale,
            }
        )

        equip_names = {
            "PADDLE": "乒乓球拍", "BALL": "乒乓球", "TABLE": "乒乓球台", "NET": "球网",
            "WRISTBAND": "护腕", "HEADBAND": "头带",
            "MEDAL_GOLD": "金牌", "MEDAL_SILVER": "银牌", "MEDAL_BRONZE": "铜牌",
            "TROPHY": "奖杯", "TOWEL": "毛巾"
        }

        if result.get("success"):
            data = result.get("data", {})
            equip_name = equip_names.get(params.equipment_type.value, params.equipment_type.value)
            attach_info = data.get("attached_to", params.attach_to)
            return f"已为 '{params.character_name}' 添加{equip_name}（位置: {attach_info}）"
        else:
            return f"添加装备失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_uniform_create",
        annotations={
            "title": "创建运动服",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_sport_uniform_create(params: SportUniformCreateInput) -> str:
        """为运动角色创建运动服。

        内置队伍配色:
        - CHINA_NATIONAL: 中国国家队红色（比赛主场）
        - CHINA_NATIONAL_BLUE: 中国队蓝色（比赛客场）
        - CHINA_NATIONAL_WHITE: 中国队白色（领奖服/外套）
        - CLUB_SHENZHEN: 深圳俱乐部
        - TRAINING: 训练服

        运动服类型:
        - MATCH_JERSEY: 比赛球衣（含号码和姓名）
        - TRAINING_WEAR: 训练服
        - AWARD_CEREMONY: 领奖服（白底红条纹）
        - WARMUP_JACKET: 热身外套

        樊振东默认球衣号码: 20
        品牌: Li-Ning (李宁)

        Args:
            params: 角色名称、队伍、球衣类型、号码、姓名等

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "sport_character", "create_uniform",
            {
                "character_name": params.character_name,
                "team": params.team.value,
                "uniform_style": params.uniform_style.value,
                "jersey_number": params.jersey_number,
                "player_name": params.player_name,
                "brand": params.brand,
                "custom_primary_color": params.custom_primary_color,
                "custom_secondary_color": params.custom_secondary_color,
            }
        )

        team_names = {
            "CHINA_NATIONAL": "中国国家队(红)",
            "CHINA_NATIONAL_BLUE": "中国队(蓝)",
            "CHINA_NATIONAL_WHITE": "中国队(白)",
            "CLUB_SHENZHEN": "深圳俱乐部",
            "CLUB_CUSTOM": "自定义俱乐部",
            "TRAINING": "训练队",
        }
        style_names = {
            "MATCH_JERSEY": "比赛球衣", "TRAINING_WEAR": "训练服",
            "AWARD_CEREMONY": "领奖服", "WARMUP_JACKET": "热身外套",
        }

        if result.get("success"):
            data = result.get("data", {})
            team_name = team_names.get(params.team.value, params.team.value)
            style_name = style_names.get(params.uniform_style.value, params.uniform_style.value)
            return (
                f"已为 '{params.character_name}' 创建{team_name}{style_name}\n"
                f"号码: {params.jersey_number}, 姓名: {params.player_name}, 品牌: {params.brand}"
            )
        else:
            return f"创建运动服失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_pose_set",
        annotations={
            "title": "设置运动姿势",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_sport_pose_set(params: SportPoseSetInput) -> str:
        """设置运动角色的运动姿势。

        乒乓球专用姿势:
        - READY_STANCE: 准备接球姿势（微蹲，持拍在前）
        - FOREHAND_ATTACK: 正手进攻（侧身蓄力挥拍）
        - BACKHAND_ATTACK: 反手拉球（快速反手弧圈）
        - SERVE_TOSS: 发球抛球（手掌托球向上抛）
        - SERVE_HIT: 发球击球（接触球瞬间）
        - FOREHAND_LOOP: 正手弧圈球（全力弧圈拉球）

        通用庆祝姿势:
        - CELEBRATE: 双臂举起庆祝
        - FIST_PUMP: 握拳吼叫（樊振东标志性动作）
        - HOLD_MEDAL: 双手展示奖牌
        - RECEIVING_AWARD: 领奖台站姿

        建模辅助姿势:
        - T_POSE: 标准T-Pose
        - A_POSE: 标准A-Pose

        Q版角色建议强度1.2-1.5以增加可爱感。

        Args:
            params: 角色名称、姿势类型、强度、是否镜像

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "sport_character", "set_pose",
            {
                "character_name": params.character_name,
                "pose": params.pose.value,
                "intensity": params.intensity,
                "mirror": params.mirror,
                "add_motion_trail": params.add_motion_trail,
            }
        )

        pose_names = {
            "READY_STANCE": "准备姿势", "FOREHAND_ATTACK": "正手进攻",
            "BACKHAND_ATTACK": "反手拉球", "SERVE_TOSS": "发球抛球",
            "SERVE_HIT": "发球击球", "FOREHAND_LOOP": "正手弧圈球",
            "CELEBRATE": "庆祝", "FIST_PUMP": "握拳庆祝",
            "HOLD_MEDAL": "展示奖牌", "RECEIVING_AWARD": "领奖",
            "T_POSE": "T-Pose", "A_POSE": "A-Pose",
        }

        if result.get("success"):
            data = result.get("data", {})
            pose_name = pose_names.get(params.pose.value, params.pose.value)
            mirror_info = "（左手镜像）" if params.mirror else ""
            trail_info = " + 运动轨迹" if data.get("has_motion_trail") else ""
            return f"已为 '{params.character_name}' 设置{pose_name}{mirror_info}（强度: {params.intensity:.0%}）{trail_info}"
        else:
            return f"设置姿势失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_reference_load",
        annotations={
            "title": "加载运动参考图",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        }
    )
    async def blender_sport_reference_load(params: SportReferenceLoadInput) -> str:
        """在视口中加载参考图像用于建模参考。

        支持加载正面、侧面、背面、3/4视角参考图。
        参考图会以空物体（Empty Image）形式添加到场景中，
        可以调整透明度、位置和缩放。

        用途：
        - 加载樊振东真实照片作为建模参考
        - 加载Q版插画作为风格参考
        - 加载比赛动作截图作为姿势参考

        支持格式: PNG, JPG, JPEG, WEBP, BMP, AVIF

        Args:
            params: 图片路径、视角、透明度等

        Returns:
            操作结果
        """
        result = await server.execute_command(
            "sport_character", "load_reference",
            {
                "image_path": params.image_path,
                "view": params.view.value,
                "opacity": params.opacity,
                "offset_x": params.offset_x,
                "offset_y": params.offset_y,
                "scale": params.scale,
            }
        )

        view_names = {
            "FRONT": "正面", "SIDE": "侧面", "BACK": "背面", "THREE_QUARTER": "3/4视角"
        }

        if result.get("success"):
            data = result.get("data", {})
            view_name = view_names.get(params.view.value, params.view.value)
            return f"已加载{view_name}参考图: {data.get('image_name', params.image_path)}（透明度: {params.opacity:.0%}）"
        else:
            return f"加载参考图失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_model_optimize",
        annotations={
            "title": "运动模型Web优化",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_sport_model_optimize(params: SportModelOptimizeInput) -> str:
        """优化运动角色模型用于不同平台。

        平台预设面数:
        - WEB: 3000-4500 tris（Three.js/WebGL）
        - MOBILE: 5000-8000 tris
        - PC_CONSOLE: 10000-20000 tris
        - PRINT_3D: 高精度，不限面数

        优化流程:
        1. 应用 Decimate 修改器减面至目标面数
        2. 清理孤立顶点和重叠面
        3. 优化UV布局
        4. 烘焙材质到贴图（可选）
        5. 生成LOD层级（可选）
        6. 导出GLB格式（可选，含Draco压缩）

        遵循学习笔记中的游戏资产优化最佳实践。

        Args:
            params: 角色名称、目标平台、面数、贴图尺寸等

        Returns:
            优化结果，包含最终面数和导出路径
        """
        result = await server.execute_command(
            "sport_character", "optimize_model",
            {
                "character_name": params.character_name,
                "target": params.target.value,
                "target_tris": params.target_tris,
                "texture_size": params.texture_size,
                "generate_lod": params.generate_lod,
                "lod_levels": params.lod_levels,
                "export_glb": params.export_glb,
                "export_path": params.export_path,
                "apply_draco_compression": params.apply_draco_compression,
            }
        )

        target_names = {
            "WEB": "Web端", "MOBILE": "移动端",
            "PC_CONSOLE": "PC/主机", "PRINT_3D": "3D打印"
        }

        if result.get("success"):
            data = result.get("data", {})
            target_name = target_names.get(params.target.value, params.target.value)
            original_tris = data.get("original_tris", "N/A")
            final_tris = data.get("final_tris", "N/A")
            export_info = f"\n导出路径: {data.get('export_path')}" if data.get("export_path") else ""
            lod_info = f"\nLOD层级: {data.get('lod_count', 0)}" if data.get("lod_count") else ""
            return (
                f"已优化 '{params.character_name}' 至{target_name}标准\n"
                f"面数: {original_tris} → {final_tris} tris\n"
                f"贴图尺寸: {params.texture_size}px{lod_info}{export_info}"
            )
        else:
            return f"优化模型失败: {result.get('error', {}).get('message', '未知错误')}"

    @mcp.tool(
        name="blender_sport_scene_setup",
        annotations={
            "title": "设置运动场景",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False
        }
    )
    async def blender_sport_scene_setup(params: SportSceneSetupInput) -> str:
        """设置运动主题场景。

        场景类型:
        - MATCH: 比赛场景（球台、灯光、观众席暗示）
        - TRAINING: 训练场景（简洁室内、训练设备）
        - AWARD_CEREMONY: 颁奖场景（领奖台、背景板）
        - PORTRAIT: 肖像展示（简洁背景、三点布光）
        - PRODUCT: 产品展示/手办风（底座、展示灯光）

        灯光遵循学习笔记最佳实践:
        - 低调环境光 + 强方向光 + 对比背光
        - EEVEE: Filmic色彩管理、柔和阴影、Bloom
        - 三点布光: 主光(暖)+辅光(冷)+轮廓光

        Args:
            params: 场景类型、角色名称、背景色、相机设置等

        Returns:
            场景设置结果
        """
        result = await server.execute_command(
            "sport_character", "setup_scene",
            {
                "scene_type": params.scene_type.value,
                "character_name": params.character_name,
                "background_color": params.background_color,
                "use_hdri": params.use_hdri,
                "camera_distance": params.camera_distance,
                "render_engine": params.render_engine,
            }
        )

        scene_names = {
            "MATCH": "比赛场景", "TRAINING": "训练场景",
            "AWARD_CEREMONY": "颁奖场景", "PORTRAIT": "肖像展示",
            "PRODUCT": "产品展示"
        }

        if result.get("success"):
            data = result.get("data", {})
            scene_name = scene_names.get(params.scene_type.value, params.scene_type.value)
            lights_info = f"灯光: {data.get('lights_count', 0)}盏"
            return (
                f"已设置{scene_name}\n"
                f"渲染引擎: {params.render_engine}, {lights_info}\n"
                f"相机距离: {params.camera_distance}m"
            )
        else:
            return f"设置场景失败: {result.get('error', {}).get('message', '未知错误')}"
