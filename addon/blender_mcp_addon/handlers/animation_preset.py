"""
预设动画处理器

处理预设动画、动作库、NLA等命令。
"""

from typing import Any, Dict, List
import bpy
import math


# 预设动画配置 - 增强版，包含更多游戏动画
ANIMATION_PRESETS = {
    # ==================== 基础动作 ====================
    "idle": {
        "description": "待机呼吸",
        "category": "basic",
        "duration": 60,
        "loop": True,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (30, [0.02, 0, 0]), (60, [0, 0, 0])],
            "spine.001": [(1, [0, 0, 0]), (30, [0.01, 0, 0]), (60, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (45, [0.02, 0, 0]), (60, [0, 0, 0])],
        }
    },
    "idle_combat": {
        "description": "战斗待机",
        "category": "combat",
        "duration": 40,
        "loop": True,
        "keyframes": {
            "spine": [(1, [0.1, 0, 0]), (20, [0.12, 0, 0]), (40, [0.1, 0, 0])],
            "upper_arm.R": [(1, [0.3, 0, -0.5]), (40, [0.3, 0, -0.5])],
            "upper_arm.L": [(1, [0.2, 0, 0.3]), (40, [0.2, 0, 0.3])],
            "thigh.L": [(1, [0.1, 0, 0]), (40, [0.1, 0, 0])],
            "thigh.R": [(1, [-0.1, 0, 0]), (40, [-0.1, 0, 0])],
        }
    },
    "walk": {
        "description": "行走循环",
        "category": "locomotion",
        "duration": 24,
        "loop": True,
        "keyframes": {
            "thigh.L": [(1, [0.3, 0, 0]), (12, [-0.3, 0, 0]), (24, [0.3, 0, 0])],
            "thigh.R": [(1, [-0.3, 0, 0]), (12, [0.3, 0, 0]), (24, [-0.3, 0, 0])],
            "shin.L": [(1, [0.2, 0, 0]), (12, [0.5, 0, 0]), (24, [0.2, 0, 0])],
            "shin.R": [(1, [0.5, 0, 0]), (12, [0.2, 0, 0]), (24, [0.5, 0, 0])],
            "upper_arm.L": [(1, [-0.2, 0, 0]), (12, [0.2, 0, 0]), (24, [-0.2, 0, 0])],
            "upper_arm.R": [(1, [0.2, 0, 0]), (12, [-0.2, 0, 0]), (24, [0.2, 0, 0])],
        }
    },
    "run": {
        "description": "跑步循环",
        "category": "locomotion",
        "duration": 16,
        "loop": True,
        "keyframes": {
            "thigh.L": [(1, [0.5, 0, 0]), (8, [-0.5, 0, 0]), (16, [0.5, 0, 0])],
            "thigh.R": [(1, [-0.5, 0, 0]), (8, [0.5, 0, 0]), (16, [-0.5, 0, 0])],
            "shin.L": [(1, [0.3, 0, 0]), (8, [0.8, 0, 0]), (16, [0.3, 0, 0])],
            "shin.R": [(1, [0.8, 0, 0]), (8, [0.3, 0, 0]), (16, [0.8, 0, 0])],
            "upper_arm.L": [(1, [-0.4, 0, 0]), (8, [0.4, 0, 0]), (16, [-0.4, 0, 0])],
            "upper_arm.R": [(1, [0.4, 0, 0]), (8, [-0.4, 0, 0]), (16, [0.4, 0, 0])],
            "spine": [(1, [0.1, 0, 0]), (8, [-0.05, 0, 0]), (16, [0.1, 0, 0])],
        }
    },
    "sprint": {
        "description": "冲刺",
        "category": "locomotion",
        "duration": 12,
        "loop": True,
        "keyframes": {
            "thigh.L": [(1, [0.7, 0, 0]), (6, [-0.7, 0, 0]), (12, [0.7, 0, 0])],
            "thigh.R": [(1, [-0.7, 0, 0]), (6, [0.7, 0, 0]), (12, [-0.7, 0, 0])],
            "shin.L": [(1, [0.4, 0, 0]), (6, [1.0, 0, 0]), (12, [0.4, 0, 0])],
            "shin.R": [(1, [1.0, 0, 0]), (6, [0.4, 0, 0]), (12, [1.0, 0, 0])],
            "upper_arm.L": [(1, [-0.6, 0, 0]), (6, [0.6, 0, 0]), (12, [-0.6, 0, 0])],
            "upper_arm.R": [(1, [0.6, 0, 0]), (6, [-0.6, 0, 0]), (12, [0.6, 0, 0])],
            "spine": [(1, [0.2, 0, 0]), (6, [0.1, 0, 0]), (12, [0.2, 0, 0])],
        }
    },
    "jump": {
        "description": "跳跃",
        "category": "locomotion",
        "duration": 40,
        "loop": False,
        "keyframes": {
            "root": [(1, [0, 0, 0]), (10, [0, 0, -0.1]), (20, [0, 0, 0.5]), (30, [0, 0, 0.5]), (40, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (10, [0.5, 0, 0]), (20, [-0.2, 0, 0]), (40, [0, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (10, [0.5, 0, 0]), (20, [-0.2, 0, 0]), (40, [0, 0, 0])],
            "upper_arm.L": [(1, [0, 0, 0]), (10, [0, 0, -0.5]), (20, [0, 0, 0.8]), (40, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (10, [0, 0, 0.5]), (20, [0, 0, -0.8]), (40, [0, 0, 0])],
        }
    },
    "double_jump": {
        "description": "二段跳",
        "category": "locomotion",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "root": [(1, [0, 0, 0.3]), (10, [0, 0, 0.6]), (20, [0, 0, 0.8]), (30, [0, 0, 0.4])],
            "thigh.L": [(1, [-0.2, 0, 0]), (15, [0.3, 0, 0]), (30, [-0.1, 0, 0])],
            "thigh.R": [(1, [-0.2, 0, 0]), (15, [0.3, 0, 0]), (30, [-0.1, 0, 0])],
            "spine": [(1, [-0.1, 0, 0]), (15, [0.1, 0, 0]), (30, [0, 0, 0])],
        }
    },
    "land": {
        "description": "落地",
        "category": "locomotion",
        "duration": 20,
        "loop": False,
        "keyframes": {
            "thigh.L": [(1, [-0.1, 0, 0]), (8, [0.5, 0, 0]), (20, [0, 0, 0])],
            "thigh.R": [(1, [-0.1, 0, 0]), (8, [0.5, 0, 0]), (20, [0, 0, 0])],
            "shin.L": [(1, [0.2, 0, 0]), (8, [0.8, 0, 0]), (20, [0, 0, 0])],
            "shin.R": [(1, [0.2, 0, 0]), (8, [0.8, 0, 0]), (20, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (8, [0.15, 0, 0]), (20, [0, 0, 0])],
        }
    },
    "dodge_roll": {
        "description": "闪避翻滚",
        "category": "combat",
        "duration": 24,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (6, [1.0, 0, 0]), (12, [2.0, 0, 0]), (18, [3.0, 0, 0]), (24, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (12, [1.2, 0, 0]), (24, [0, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (12, [1.2, 0, 0]), (24, [0, 0, 0])],
            "upper_arm.L": [(1, [0, 0, 0]), (12, [0.5, 0, 0.5]), (24, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (12, [0.5, 0, -0.5]), (24, [0, 0, 0])],
        }
    },
    "dodge_back": {
        "description": "后跳闪避",
        "category": "combat",
        "duration": 20,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (5, [-0.2, 0, 0]), (10, [-0.1, 0, 0]), (20, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (10, [0.4, 0, 0]), (20, [0, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (10, [0.4, 0, 0]), (20, [0, 0, 0])],
        }
    },
    
    # ==================== 战斗动作 ====================
    "attack": {
        "description": "基础攻击",
        "category": "combat",
        "duration": 20,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (5, [0, 0.8, -0.5]), (10, [0.5, -0.5, 0]), (20, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (5, [0.5, 0, 0]), (10, [0, 0, 0]), (20, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (5, [0, 0.2, 0]), (10, [0, -0.3, 0]), (20, [0, 0, 0])],
        }
    },
    "attack_combo_1": {
        "description": "连击第一段",
        "category": "combat",
        "duration": 15,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (5, [0.3, 0.5, -0.3]), (10, [0.5, -0.3, 0.2]), (15, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (5, [0.4, 0, 0]), (15, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (5, [0, 0.15, 0]), (10, [0, -0.2, 0]), (15, [0, 0, 0])],
        }
    },
    "attack_combo_2": {
        "description": "连击第二段",
        "category": "combat",
        "duration": 18,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (6, [0.3, -0.5, 0.3]), (12, [0.5, 0.3, -0.2]), (18, [0, 0, 0])],
            "forearm.L": [(1, [0, 0, 0]), (6, [0.4, 0, 0]), (18, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (6, [0, -0.15, 0]), (12, [0, 0.2, 0]), (18, [0, 0, 0])],
        }
    },
    "attack_combo_3": {
        "description": "连击第三段（重击）",
        "category": "combat",
        "duration": 25,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (8, [-0.3, 1.0, -0.8]), (15, [0.8, -0.8, 0.3]), (25, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (8, [0.6, 0, 0]), (15, [0.2, 0, 0]), (25, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (8, [0, 0.3, 0]), (15, [0.1, -0.4, 0]), (25, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (15, [0.2, 0, 0]), (25, [0, 0, 0])],
        }
    },
    "attack_heavy": {
        "description": "重攻击",
        "category": "combat",
        "duration": 35,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (10, [-0.5, 1.2, -1.0]), (20, [1.0, -1.0, 0.5]), (35, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (10, [0.8, 0, 0]), (20, [0.3, 0, 0]), (35, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (10, [0, 0.4, 0]), (20, [0.15, -0.5, 0]), (35, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (20, [0.3, 0, 0]), (35, [0, 0, 0])],
        }
    },
    "attack_spin": {
        "description": "旋转攻击",
        "category": "combat",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (15, [0, 3.14, 0]), (30, [0, 6.28, 0])],
            "upper_arm.R": [(1, [0, 0, -1.2]), (30, [0, 0, -1.2])],
            "upper_arm.L": [(1, [0, 0, 1.2]), (30, [0, 0, 1.2])],
        }
    },
    "attack_uppercut": {
        "description": "上勾拳",
        "category": "combat",
        "duration": 20,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (5, [0.5, 0, 0]), (10, [-0.8, 0.3, 0]), (20, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (5, [0.8, 0, 0]), (10, [0.3, 0, 0]), (20, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (5, [0.1, 0, 0]), (10, [-0.2, 0, 0]), (20, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (10, [0.2, 0, 0]), (20, [0, 0, 0])],
        }
    },
    "block": {
        "description": "格挡",
        "category": "combat",
        "duration": 15,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (5, [0.5, 0.5, 0.8]), (15, [0.5, 0.5, 0.8])],
            "upper_arm.R": [(1, [0, 0, 0]), (5, [0.5, -0.5, -0.8]), (15, [0.5, -0.5, -0.8])],
            "forearm.L": [(1, [0, 0, 0]), (5, [1.0, 0, 0]), (15, [1.0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (5, [1.0, 0, 0]), (15, [1.0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (5, [0.1, 0, 0]), (15, [0.1, 0, 0])],
        }
    },
    "parry": {
        "description": "弹反",
        "category": "combat",
        "duration": 12,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0.5, -0.5, -0.8]), (6, [0.3, 0.8, -0.3]), (12, [0, 0, 0])],
            "forearm.R": [(1, [1.0, 0, 0]), (6, [0.5, 0.3, 0]), (12, [0, 0, 0])],
            "spine": [(1, [0.1, 0, 0]), (6, [0, -0.2, 0]), (12, [0, 0, 0])],
        }
    },
    "hit_light": {
        "description": "受击（轻）",
        "category": "combat",
        "duration": 15,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (5, [-0.15, 0, 0]), (15, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (5, [-0.2, 0, 0]), (15, [0, 0, 0])],
        }
    },
    "hit_heavy": {
        "description": "受击（重）",
        "category": "combat",
        "duration": 25,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (8, [-0.4, 0, 0]), (25, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (8, [-0.5, 0, 0]), (25, [0, 0, 0])],
            "upper_arm.L": [(1, [0, 0, 0]), (8, [0.3, 0, 0.5]), (25, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (8, [0.3, 0, -0.5]), (25, [0, 0, 0])],
        }
    },
    "knockdown": {
        "description": "击倒",
        "category": "combat",
        "duration": 40,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (10, [-0.5, 0, 0]), (20, [-1.2, 0, 0]), (40, [-1.57, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (20, [0.5, 0, 0]), (40, [0.2, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (20, [0.5, 0, 0]), (40, [0.2, 0, 0])],
        }
    },
    "getup": {
        "description": "起身",
        "category": "combat",
        "duration": 35,
        "loop": False,
        "keyframes": {
            "spine": [(1, [-1.57, 0, 0]), (15, [-0.8, 0, 0]), (25, [-0.3, 0, 0]), (35, [0, 0, 0])],
            "thigh.L": [(1, [0.2, 0, 0]), (15, [0.8, 0, 0]), (25, [0.3, 0, 0]), (35, [0, 0, 0])],
            "thigh.R": [(1, [0.2, 0, 0]), (15, [0.8, 0, 0]), (25, [0.3, 0, 0]), (35, [0, 0, 0])],
        }
    },
    "death": {
        "description": "死亡",
        "category": "combat",
        "duration": 50,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (15, [-0.3, 0.2, 0]), (30, [-0.8, 0.1, 0]), (50, [-1.57, 0, 0])],
            "head": [(1, [0, 0, 0]), (15, [-0.2, 0.3, 0]), (50, [-0.3, 0, 0])],
            "upper_arm.L": [(1, [0, 0, 0]), (30, [0.5, 0, 0.8]), (50, [0.3, 0, 0.5])],
            "upper_arm.R": [(1, [0, 0, 0]), (30, [0.5, 0, -0.8]), (50, [0.3, 0, -0.5])],
            "thigh.L": [(1, [0, 0, 0]), (30, [0.4, 0, 0.2]), (50, [0.2, 0, 0.1])],
            "thigh.R": [(1, [0, 0, 0]), (30, [0.4, 0, -0.2]), (50, [0.2, 0, -0.1])],
        }
    },
    
    # ==================== 技能动作 ====================
    "cast_spell": {
        "description": "施法",
        "category": "skill",
        "duration": 40,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (15, [0, 0.5, -1.2]), (25, [0, 0.5, -1.2]), (40, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (15, [0, -0.5, 1.2]), (25, [0, -0.5, 1.2]), (40, [0, 0, 0])],
            "forearm.L": [(1, [0, 0, 0]), (15, [0.5, 0, 0]), (25, [0.5, 0, 0]), (40, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (15, [0.5, 0, 0]), (25, [0.5, 0, 0]), (40, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (15, [-0.1, 0, 0]), (25, [-0.1, 0, 0]), (40, [0, 0, 0])],
        }
    },
    "cast_fireball": {
        "description": "投掷火球",
        "category": "skill",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (10, [-0.3, 0.8, -1.0]), (20, [0.5, -0.5, 0.3]), (30, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (10, [0.8, 0, 0]), (20, [0.2, 0, 0]), (30, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (10, [0, 0.3, 0]), (20, [0, -0.2, 0]), (30, [0, 0, 0])],
        }
    },
    "cast_heal": {
        "description": "治疗施法",
        "category": "skill",
        "duration": 50,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (20, [0, 0, -2.0]), (35, [0, 0, -2.0]), (50, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (20, [0, 0, 2.0]), (35, [0, 0, 2.0]), (50, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (20, [-0.2, 0, 0]), (35, [-0.2, 0, 0]), (50, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (20, [-0.1, 0, 0]), (35, [-0.1, 0, 0]), (50, [0, 0, 0])],
        }
    },
    "charge_power": {
        "description": "蓄力",
        "category": "skill",
        "duration": 60,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (30, [0.3, 0, 0.5]), (60, [0.3, 0, 0.5])],
            "upper_arm.R": [(1, [0, 0, 0]), (30, [0.3, 0, -0.5]), (60, [0.3, 0, -0.5])],
            "spine": [(1, [0, 0, 0]), (30, [0.1, 0, 0]), (60, [0.1, 0, 0])],
            "head": [(1, [0, 0, 0]), (30, [-0.1, 0, 0]), (60, [-0.1, 0, 0])],
        }
    },
    "release_power": {
        "description": "释放能量",
        "category": "skill",
        "duration": 25,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0.3, 0, 0.5]), (10, [0, 0, -1.5]), (25, [0, 0, 0])],
            "upper_arm.R": [(1, [0.3, 0, -0.5]), (10, [0, 0, 1.5]), (25, [0, 0, 0])],
            "spine": [(1, [0.1, 0, 0]), (10, [-0.2, 0, 0]), (25, [0, 0, 0])],
        }
    },
    
    # ==================== 交互动作 ====================
    "wave": {
        "description": "挥手",
        "category": "social",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, -1.2]), (30, [0, 0, -1.2])],
            "forearm.R": [(1, [0, 0, 0]), (8, [0, 0.3, 0]), (16, [0, -0.3, 0]), (24, [0, 0.3, 0]), (30, [0, 0, 0])],
        }
    },
    "celebrate": {
        "description": "庆祝",
        "category": "social",
        "duration": 60,
        "loop": False,
        "keyframes": {
            "upper_arm.L": [(1, [0, 0, 0]), (15, [0, 0, -2.5]), (30, [0, 0, -2.3]), (45, [0, 0, -2.5]), (60, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (15, [0, 0, 2.5]), (30, [0, 0, 2.3]), (45, [0, 0, 2.5]), (60, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (15, [-0.2, 0, 0]), (30, [-0.1, 0.1, 0]), (45, [-0.2, -0.1, 0]), (60, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (20, [-0.1, 0, 0]), (40, [-0.15, 0, 0]), (60, [0, 0, 0])],
        }
    },
    "dance": {
        "description": "跳舞",
        "category": "social",
        "duration": 48,
        "loop": True,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (12, [0, 0.1, 0]), (24, [0, -0.1, 0]), (36, [0, 0.1, 0]), (48, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (12, [0, 0.15, 0]), (24, [0, -0.15, 0]), (36, [0, 0.15, 0]), (48, [0, 0, 0])],
            "upper_arm.L": [(1, [0, 0, -0.5]), (12, [0, 0, -1.0]), (24, [0, 0, -0.5]), (36, [0, 0, -1.0]), (48, [0, 0, -0.5])],
            "upper_arm.R": [(1, [0, 0, 0.5]), (12, [0, 0, 1.0]), (24, [0, 0, 0.5]), (36, [0, 0, 1.0]), (48, [0, 0, 0.5])],
        }
    },
    "sit": {
        "description": "坐下",
        "category": "social",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "thigh.L": [(1, [0, 0, 0]), (30, [1.5, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (30, [1.5, 0, 0])],
            "shin.L": [(1, [0, 0, 0]), (30, [-1.5, 0, 0])],
            "shin.R": [(1, [0, 0, 0]), (30, [-1.5, 0, 0])],
            "spine": [(1, [0, 0, 0]), (30, [0.2, 0, 0])],
        }
    },
    "bow": {
        "description": "鞠躬",
        "category": "social",
        "duration": 40,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (15, [0.5, 0, 0]), (25, [0.5, 0, 0]), (40, [0, 0, 0])],
            "spine.001": [(1, [0, 0, 0]), (15, [0.3, 0, 0]), (25, [0.3, 0, 0]), (40, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (15, [0.2, 0, 0]), (25, [0.2, 0, 0]), (40, [0, 0, 0])],
        }
    },
    "salute": {
        "description": "敬礼",
        "category": "social",
        "duration": 35,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (12, [0.8, 0.5, 0]), (25, [0.8, 0.5, 0]), (35, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (12, [1.2, 0, 0]), (25, [1.2, 0, 0]), (35, [0, 0, 0])],
            "spine": [(1, [0, 0, 0]), (12, [0.05, 0, 0]), (25, [0.05, 0, 0]), (35, [0, 0, 0])],
        }
    },
    "point": {
        "description": "指向",
        "category": "social",
        "duration": 25,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (10, [0.3, 0, -0.8]), (25, [0.3, 0, -0.8])],
            "forearm.R": [(1, [0, 0, 0]), (10, [0.2, 0, 0]), (25, [0.2, 0, 0])],
        }
    },
    "pickup": {
        "description": "拾取物品",
        "category": "interaction",
        "duration": 30,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (12, [0.6, 0, 0]), (20, [0.6, 0, 0]), (30, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (12, [0.4, 0, 0]), (20, [0.4, 0, 0]), (30, [0, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (12, [0.4, 0, 0]), (20, [0.4, 0, 0]), (30, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (12, [0.8, 0, 0]), (20, [0.8, 0, 0]), (30, [0, 0, 0])],
        }
    },
    "use_item": {
        "description": "使用物品",
        "category": "interaction",
        "duration": 40,
        "loop": False,
        "keyframes": {
            "upper_arm.R": [(1, [0, 0, 0]), (10, [0.5, 0.3, -0.3]), (25, [0.5, 0.3, -0.3]), (40, [0, 0, 0])],
            "forearm.R": [(1, [0, 0, 0]), (10, [0.8, 0, 0]), (25, [0.8, 0, 0]), (40, [0, 0, 0])],
            "head": [(1, [0, 0, 0]), (10, [0.1, 0, 0]), (25, [0.1, 0, 0]), (40, [0, 0, 0])],
        }
    },
    "open_chest": {
        "description": "开宝箱",
        "category": "interaction",
        "duration": 45,
        "loop": False,
        "keyframes": {
            "spine": [(1, [0, 0, 0]), (15, [0.3, 0, 0]), (30, [0.3, 0, 0]), (45, [0, 0, 0])],
            "upper_arm.L": [(1, [0, 0, 0]), (15, [0.5, 0, 0.5]), (30, [0.3, 0, 0.3]), (45, [0, 0, 0])],
            "upper_arm.R": [(1, [0, 0, 0]), (15, [0.5, 0, -0.5]), (30, [0.3, 0, -0.3]), (45, [0, 0, 0])],
            "thigh.L": [(1, [0, 0, 0]), (15, [0.3, 0, 0]), (30, [0.3, 0, 0]), (45, [0, 0, 0])],
            "thigh.R": [(1, [0, 0, 0]), (15, [0.3, 0, 0]), (30, [0.3, 0, 0]), (45, [0, 0, 0])],
        }
    },
}


def handle_apply(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用预设动画"""
    armature_name = params.get("armature_name")
    preset = params.get("preset", "idle")
    speed = params.get("speed", 1.0)
    loop = params.get("loop", True)
    
    armature_obj = bpy.data.objects.get(armature_name)
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return {
            "success": False,
            "error": {"code": "ARMATURE_NOT_FOUND", "message": f"骨架不存在: {armature_name}"}
        }
    
    preset_config = ANIMATION_PRESETS.get(preset)
    if not preset_config:
        return {
            "success": False,
            "error": {"code": "PRESET_NOT_FOUND", "message": f"预设不存在: {preset}"}
        }
    
    # 创建动作
    action_name = f"{armature_name}_{preset}"
    action = bpy.data.actions.new(name=action_name)
    
    # 关联动作到骨架
    if not armature_obj.animation_data:
        armature_obj.animation_data_create()
    armature_obj.animation_data.action = action
    
    # 进入姿态模式
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # 应用关键帧
    keyframes = preset_config["keyframes"]
    duration = int(preset_config["duration"] / speed)
    
    for bone_name, frames in keyframes.items():
        pose_bone = armature_obj.pose.bones.get(bone_name)
        if not pose_bone:
            continue
        
        for frame, rotation in frames:
            adjusted_frame = int(frame / speed)
            pose_bone.rotation_euler = rotation
            pose_bone.keyframe_insert(data_path="rotation_euler", frame=adjusted_frame)
    
    # 设置循环
    if loop:
        for fcurve in action.fcurves:
            for modifier in fcurve.modifiers:
                fcurve.modifiers.remove(modifier)
            mod = fcurve.modifiers.new(type='CYCLES')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 设置时间线范围
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = duration
    
    return {
        "success": True,
        "data": {
            "preset": preset,
            "action_name": action_name,
            "duration": duration
        }
    }


def handle_action_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建动作"""
    action_name = params.get("action_name")
    armature_name = params.get("armature_name")
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 60)
    
    # 创建动作
    action = bpy.data.actions.new(name=action_name)
    action.frame_range = (frame_start, frame_end)
    
    # 如果指定了骨架，关联动作
    if armature_name:
        armature_obj = bpy.data.objects.get(armature_name)
        if armature_obj and armature_obj.type == 'ARMATURE':
            if not armature_obj.animation_data:
                armature_obj.animation_data_create()
            armature_obj.animation_data.action = action
    
    return {
        "success": True,
        "data": {
            "action_name": action.name
        }
    }


def handle_nla_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加NLA条带"""
    object_name = params.get("object_name")
    action_name = params.get("action_name")
    track_name = params.get("track_name", "NlaTrack")
    start_frame = params.get("start_frame", 1)
    blend_type = params.get("blend_type", "REPLACE")
    scale = params.get("scale", 1.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    action = bpy.data.actions.get(action_name)
    if not action:
        return {
            "success": False,
            "error": {"code": "ACTION_NOT_FOUND", "message": f"动作不存在: {action_name}"}
        }
    
    # 确保有动画数据
    if not obj.animation_data:
        obj.animation_data_create()
    
    # 创建或获取NLA轨道
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    
    # 添加条带
    strip = track.strips.new(action_name, start_frame, action)
    strip.blend_type = blend_type
    strip.scale = scale
    
    return {
        "success": True,
        "data": {
            "track_name": track_name,
            "strip_name": strip.name
        }
    }


def handle_follow_path(params: Dict[str, Any]) -> Dict[str, Any]:
    """路径动画"""
    object_name = params.get("object_name")
    path_name = params.get("path_name")
    duration = params.get("duration", 100)
    follow_rotation = params.get("follow_rotation", True)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    path = bpy.data.objects.get(path_name)
    if not path or path.type != 'CURVE':
        return {
            "success": False,
            "error": {"code": "PATH_NOT_FOUND", "message": f"路径不存在: {path_name}"}
        }
    
    # 添加跟随路径约束
    constraint = obj.constraints.new('FOLLOW_PATH')
    constraint.target = path
    constraint.use_curve_follow = follow_rotation
    
    # 设置路径动画
    path.data.use_path = True
    path.data.path_duration = duration
    
    # 动画化偏移
    constraint.offset_factor = 0
    constraint.keyframe_insert(data_path="offset_factor", frame=1)
    constraint.offset_factor = 1
    constraint.keyframe_insert(data_path="offset_factor", frame=duration)
    
    return {
        "success": True,
        "data": {
            "duration": duration
        }
    }


def handle_bake(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙动画"""
    object_name = params.get("object_name")
    frame_start = params.get("frame_start", 1)
    frame_end = params.get("frame_end", 250)
    bake_types = params.get("bake_types", ["LOCATION", "ROTATION", "SCALE"])
    clear_constraints = params.get("clear_constraints", False)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 如果是骨架，进入姿态模式
    if obj.type == 'ARMATURE':
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=clear_constraints,
            bake_types={'POSE'}
        )
        
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=clear_constraints,
            bake_types={'OBJECT'}
        )
    
    return {
        "success": True,
        "data": {
            "frames_baked": frame_end - frame_start + 1
        }
    }
