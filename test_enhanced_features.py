#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Features Test Script

Tests the new features in Blender MCP:
1. Enhanced character system (face shape keys, expressions)
2. Enhanced clothing system (multiple clothing types, cloth simulation)
3. Enhanced hair system (16 hairstyle presets)
4. Enhanced cloth physics (17 cloth presets, auto-pinning)
5. Extended animation presets (35+ game character animations)
"""

import asyncio
import json
import sys
import io
from pathlib import Path

# Set stdout encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


class TestResult:
    """测试结果"""
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, test_name: str):
        self.passed += 1
        print(f"  [PASS] {test_name}")
    
    def fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  [FAIL] {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{self.name}: {self.passed}/{total} 通过")
        if self.errors:
            print("  失败的测试:")
            for name, error in self.errors:
                print(f"    - {name}: {error}")
        return self.failed == 0


def test_character_system():
    """测试角色系统"""
    print("\n=== 测试角色系统 ===")
    result = TestResult("角色系统")
    
    # 测试体型枚举
    try:
        from blender_mcp.tools.character import BodyType, Gender, HairStyle, ClothingType, OutfitStyle, Expression
        
        # 测试体型
        assert len(BodyType) == 4, "应该有4种体型"
        result.success("体型枚举")
        
        # 测试性别
        assert len(Gender) == 3, "应该有3种性别"
        result.success("性别枚举")
        
        # 测试发型 - 现在有16种
        assert len(HairStyle) >= 16, f"应该至少有16种发型，实际: {len(HairStyle)}"
        result.success("发型枚举")
        
        # 测试服装类型 - 现在有19种
        assert len(ClothingType) >= 19, f"应该至少有19种服装，实际: {len(ClothingType)}"
        result.success("服装类型枚举")
        
        # 测试套装风格 - 8种
        assert len(OutfitStyle) == 8, f"应该有8种套装风格，实际: {len(OutfitStyle)}"
        result.success("套装风格枚举")
        
        # 测试表情 - 8种
        assert len(Expression) == 8, f"应该有8种表情，实际: {len(Expression)}"
        result.success("表情枚举")
        
    except ImportError as e:
        result.fail("导入模块", str(e))
    except AssertionError as e:
        result.fail("枚举验证", str(e))
    except Exception as e:
        result.fail("未知错误", str(e))
    
    # 测试输入模型
    try:
        from blender_mcp.tools.character import (
            CharacterCreateHumanoidInput,
            CharacterAddFaceFeaturesInput,
            CharacterSetExpressionInput,
            CharacterAddHairInput,
            CharacterAddClothingInput,
            CharacterCreateOutfitInput
        )
        
        # 测试创建角色输入
        input1 = CharacterCreateHumanoidInput(
            name="TestChar",
            height=1.75,
            body_type=BodyType.MUSCULAR,
            gender=Gender.MALE,
            create_face_rig=True
        )
        assert input1.create_face_rig == True
        result.success("角色创建输入模型")
        
        # 测试面部特征输入 - 22个参数
        input2 = CharacterAddFaceFeaturesInput(
            character_name="TestChar",
            eye_size=1.2,
            eye_distance=1.0,
            eye_height=1.1,
            nose_length=0.9,
            mouth_width=1.1,
            jaw_width=1.05,
            cheekbone_height=1.1,
            forehead_height=0.95
        )
        result.success("面部特征输入模型")
        
        # 测试表情输入
        input3 = CharacterSetExpressionInput(
            character_name="TestChar",
            expression=Expression.SMILE,
            intensity=0.8
        )
        result.success("表情设置输入模型")
        
        # 测试头发输入
        input4 = CharacterAddHairInput(
            character_name="TestChar",
            hair_style=HairStyle.ANCIENT_MALE,
            hair_density=1.2,
            use_dynamics=True
        )
        result.success("头发添加输入模型")
        
        # 测试服装输入
        input5 = CharacterAddClothingInput(
            character_name="TestChar",
            clothing_type=ClothingType.ROBE,
            color=[0.8, 0.2, 0.2],
            use_cloth_simulation=True
        )
        result.success("服装添加输入模型")
        
        # 测试套装输入
        input6 = CharacterCreateOutfitInput(
            character_name="TestChar",
            outfit_style=OutfitStyle.WARRIOR,
            color_scheme="GOLD"
        )
        result.success("套装创建输入模型")
        
    except Exception as e:
        result.fail("输入模型测试", str(e))
    
    return result.summary()


def test_hair_presets():
    """测试发型预设"""
    print("\n=== 测试发型预设 ===")
    result = TestResult("发型预设")
    
    # 发型列表
    expected_hair_styles = [
        "BALD", "BUZZ", "SHORT", "MEDIUM", "LONG", "VERY_LONG",
        "PONYTAIL", "BUN", "BRAIDS", "MOHAWK", "AFRO", "CURLY", "WAVY",
        "ANCIENT_MALE", "ANCIENT_FEMALE", "TOPKNOT"
    ]
    
    try:
        from blender_mcp.tools.character import HairStyle
        
        for style in expected_hair_styles:
            try:
                hs = HairStyle(style)
                result.success(f"发型 {style}")
            except ValueError:
                result.fail(f"发型 {style}", "不存在")
        
    except Exception as e:
        result.fail("发型预设测试", str(e))
    
    return result.summary()


def test_clothing_types():
    """测试服装类型"""
    print("\n=== 测试服装类型 ===")
    result = TestResult("服装类型")
    
    # 服装类型列表
    expected_clothing = [
        "SHIRT", "T_SHIRT", "PANTS", "SHORTS", "JACKET", "COAT",
        "DRESS", "SKIRT", "ROBE", "HANFU_TOP", "HANFU_BOTTOM",
        "ARMOR_CHEST", "ARMOR_FULL", "CAPE", "SHOES", "BOOTS",
        "GLOVES", "HAT", "HELMET"
    ]
    
    try:
        from blender_mcp.tools.character import ClothingType
        
        for clothing in expected_clothing:
            try:
                ct = ClothingType(clothing)
                result.success(f"服装 {clothing}")
            except ValueError:
                result.fail(f"服装 {clothing}", "不存在")
        
    except Exception as e:
        result.fail("服装类型测试", str(e))
    
    return result.summary()


def test_physics_presets():
    """测试物理预设"""
    print("\n=== 测试布料物理预设 ===")
    result = TestResult("布料物理")
    
    # 预期的布料预设
    expected_presets = [
        "cotton", "silk", "leather", "denim", "rubber",
        "linen", "velvet", "chiffon", "wool", "satin",
        "chainmail", "cape_heavy", "cape_light", "flag", "paper",
        "hanfu_outer", "hanfu_inner", "ribbon"
    ]
    
    try:
        # 读取物理处理器文件检查预设
        handler_path = Path(__file__).parent / "addon" / "blender_mcp_addon" / "handlers" / "physics.py"
        with open(handler_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for preset in expected_presets:
            if f'"{preset}"' in content or f"'{preset}'" in content:
                result.success(f"布料预设 {preset}")
            else:
                result.fail(f"布料预设 {preset}", "在文件中未找到")
        
    except Exception as e:
        result.fail("布料预设测试", str(e))
    
    return result.summary()


def test_animation_presets():
    """测试动画预设"""
    print("\n=== 测试动画预设 ===")
    result = TestResult("动画预设")
    
    # 预期的动画预设（按类别）
    expected_animations = {
        "basic": ["idle", "idle_combat"],
        "locomotion": ["walk", "run", "sprint", "jump", "double_jump", "land", "dodge_roll", "dodge_back"],
        "combat": ["attack", "attack_combo_1", "attack_combo_2", "attack_combo_3", "attack_heavy", 
                   "attack_spin", "attack_uppercut", "block", "parry", 
                   "hit_light", "hit_heavy", "knockdown", "getup", "death"],
        "skill": ["cast_spell", "cast_fireball", "cast_heal", "charge_power", "release_power"],
        "social": ["wave", "celebrate", "dance", "sit", "bow", "salute", "point"],
        "interaction": ["pickup", "use_item", "open_chest"]
    }
    
    try:
        # 读取动画处理器文件
        handler_path = Path(__file__).parent / "addon" / "blender_mcp_addon" / "handlers" / "animation_preset.py"
        with open(handler_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        total_animations = 0
        for category, animations in expected_animations.items():
            for anim in animations:
                if f'"{anim}"' in content:
                    result.success(f"[{category}] {anim}")
                    total_animations += 1
                else:
                    result.fail(f"[{category}] {anim}", "未找到")
        
        print(f"\n  总计: {total_animations} 个动画预设")
        
    except Exception as e:
        result.fail("动画预设测试", str(e))
    
    return result.summary()


def test_face_shape_keys():
    """测试面部形态键"""
    print("\n=== 测试面部形态键配置 ===")
    result = TestResult("面部形态键")
    
    # 预期的面部参数
    expected_face_params = [
        # 眼睛
        "eye_size", "eye_distance", "eye_height", "eye_tilt", "eye_depth",
        # 鼻子
        "nose_length", "nose_width", "nose_height", "nose_tip",
        # 嘴巴
        "mouth_width", "mouth_height", "lip_thickness_upper", "lip_thickness_lower",
        # 下巴和脸型
        "jaw_width", "jaw_height", "chin_length", "cheekbone_height", "cheekbone_width",
        # 额头
        "forehead_height", "forehead_width",
        # 耳朵
        "ear_size", "ear_position"
    ]
    
    try:
        # 读取角色处理器文件
        handler_path = Path(__file__).parent / "addon" / "blender_mcp_addon" / "handlers" / "character.py"
        with open(handler_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for param in expected_face_params:
            if f'"{param}"' in content:
                result.success(f"面部参数 {param}")
            else:
                result.fail(f"面部参数 {param}", "未找到")
        
    except Exception as e:
        result.fail("面部形态键测试", str(e))
    
    return result.summary()


def test_expressions():
    """测试面部表情"""
    print("\n=== 测试面部表情预设 ===")
    result = TestResult("面部表情")
    
    # 预期的表情
    expected_expressions = [
        "neutral", "smile", "sad", "angry",
        "surprised", "fear", "disgust", "contempt"
    ]
    
    try:
        # 读取角色处理器文件
        handler_path = Path(__file__).parent / "addon" / "blender_mcp_addon" / "handlers" / "character.py"
        with open(handler_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for expr in expected_expressions:
            if f'"{expr}"' in content:
                result.success(f"表情 {expr}")
            else:
                result.fail(f"表情 {expr}", "未找到")
        
    except Exception as e:
        result.fail("表情测试", str(e))
    
    return result.summary()


def test_outfit_styles():
    """测试套装风格"""
    print("\n=== 测试套装风格 ===")
    result = TestResult("套装风格")
    
    # 预期的套装风格及其包含的服装
    expected_outfits = {
        "CASUAL": ["T_SHIRT", "PANTS", "SHOES"],
        "FORMAL": ["SHIRT", "PANTS", "SHOES"],
        "WARRIOR": ["ARMOR_CHEST", "PANTS", "BOOTS", "GLOVES"],
        "MAGE": ["ROBE", "BOOTS", "GLOVES", "HAT"],
        "HANFU": ["HANFU_TOP", "HANFU_BOTTOM", "SHOES"],
        "ANCIENT_WARRIOR": ["ARMOR_FULL", "BOOTS", "HELMET"],
        "NOBLE": ["JACKET", "PANTS", "BOOTS", "CAPE"],
        "DANCER": ["DRESS", "SHOES"],
    }
    
    try:
        # 读取角色处理器文件
        handler_path = Path(__file__).parent / "addon" / "blender_mcp_addon" / "handlers" / "character.py"
        with open(handler_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for outfit, items in expected_outfits.items():
            if f'"{outfit}"' in content:
                result.success(f"套装 {outfit} ({len(items)}件)")
            else:
                result.fail(f"套装 {outfit}", "未找到")
        
    except Exception as e:
        result.fail("套装风格测试", str(e))
    
    return result.summary()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Blender MCP 增强功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行各项测试
    results.append(("角色系统", test_character_system()))
    results.append(("发型预设", test_hair_presets()))
    results.append(("服装类型", test_clothing_types()))
    results.append(("布料物理", test_physics_presets()))
    results.append(("动画预设", test_animation_presets()))
    results.append(("面部形态键", test_face_shape_keys()))
    results.append(("面部表情", test_expressions()))
    results.append(("套装风格", test_outfit_styles()))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
