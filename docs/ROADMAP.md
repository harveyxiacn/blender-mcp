# Blender MCP 工具扩展路线图

## 概述

基于实际测试（Q版樊振东 + 巴黎奥运场景），我们识别出以下需要扩展的功能领域，以让 AI 通过 MCP 在 Blender 中创造更丰富的内容。

---

## 一、当前功能状态

### 已实现的工具（50+）
| 类别 | 工具数量 | 状态 |
|------|---------|------|
| 场景管理 | 6 | ✅ 完成 |
| 对象操作 | 10 | ✅ 完成 |
| 网格建模 | 9 | ✅ 完成 |
| 材质系统 | 6 | ✅ 完成 |
| 灯光系统 | 4 | ✅ 完成 |
| 相机控制 | 4 | ✅ 完成 |
| 动画系统 | 6 | ✅ 完成 |
| 角色创建 | 4 | ⚠️ 基础 |
| 骨骼绑定 | 6 | ⚠️ 基础 |
| 渲染输出 | 4 | ✅ 完成 |
| 实用工具 | 7 | ✅ 完成 |

### 测试结果
- 总测试: 134
- 通过: 133 (99.3%)
- 失败: 1 (已修复)

---

## 二、需要扩展的新工具

### 1. 角色系统增强 (Character System)

#### 1.1 预设角色模板
```
blender_character_create_from_template
- 输入: template_name, customizations
- 模板类型:
  - chibi (Q版/SD)
  - realistic (写实)
  - stylized (风格化)
  - anime (动漫)
  - mascot (吉祥物)
```

#### 1.2 面部系统
```
blender_character_face_create
- 创建可控的面部表情系统
- 眼睛、眉毛、嘴巴形状键

blender_character_face_set_expression
- 表情预设: happy, sad, angry, surprised, neutral
- 自定义表情参数

blender_character_face_add_blend_shapes
- 添加混合变形（用于动画）
```

#### 1.3 服装系统
```
blender_character_clothing_add
- 衣服类型: shirt, pants, jacket, dress, uniform
- 自动适配角色体型

blender_character_clothing_customize
- 颜色、图案、装饰品
```

#### 1.4 发型系统
```
blender_character_hair_create
- 发型模板: short, long, ponytail, braided
- 粒子毛发或网格毛发

blender_character_hair_style
- 颜色、光泽度、蓬松度
```

### 2. 骨骼绑定增强 (Rigging System)

#### 2.1 自动绑定
```
blender_rig_auto_setup
- 自动为人形角色创建骨骼
- 支持: humanoid, quadruped, bird, fish

blender_rig_auto_weight
- 自动权重绑定
- 智能权重优化
```

#### 2.2 面部绑定
```
blender_rig_face_setup
- 面部骨骼系统
- 眼球追踪控制
- 嘴型控制

blender_rig_add_face_control
- 添加面部控制器
- 表情驱动器
```

#### 2.3 IK/FK 切换
```
blender_rig_ik_fk_setup
- 为四肢设置 IK/FK 切换
- 极向量控制

blender_rig_ik_fk_switch
- 运行时切换 IK/FK
```

### 3. 动画系统增强 (Animation System)

#### 3.1 动作库
```
blender_animation_action_create
- 创建独立动作

blender_animation_action_library_add
- 添加动作到库
- 标签和分类

blender_animation_action_library_apply
- 从库中应用动作到角色
```

#### 3.2 预设动画
```
blender_animation_preset_apply
- 预设动画:
  - walk (行走循环)
  - run (跑步循环)
  - idle (待机)
  - jump (跳跃)
  - attack (攻击)
  - celebrate (庆祝)
  - wave (挥手)
```

#### 3.3 动画混合
```
blender_animation_nla_add_strip
- NLA 条带管理

blender_animation_blend_actions
- 混合多个动作
- 权重控制
```

#### 3.4 路径动画
```
blender_animation_follow_path
- 沿路径移动

blender_animation_path_create
- 创建运动路径
```

### 4. 高级建模工具 (Advanced Modeling)

#### 4.1 雕刻模式
```
blender_sculpt_brush
- 雕刻笔刷操作
- 笔刷类型: draw, smooth, grab, inflate

blender_sculpt_remesh
- 重新网格化
- 体素/四边面
```

#### 4.2 布尔运算增强
```
blender_modeling_boolean_batch
- 批量布尔运算
- 更复杂的形状组合
```

#### 4.3 曲线建模
```
blender_curve_create
- 贝塞尔曲线、NURBS

blender_curve_to_mesh
- 曲线转网格

blender_curve_profile
- 沿曲线挤出轮廓
```

### 5. 物理模拟 (Physics Simulation)

#### 5.1 布料模拟
```
blender_physics_cloth_add
- 添加布料模拟
- 衣服物理

blender_physics_cloth_settings
- 布料属性设置
```

#### 5.2 刚体物理
```
blender_physics_rigid_body_add
- 刚体物理

blender_physics_collision_add
- 碰撞体
```

#### 5.3 粒子系统
```
blender_particles_create
- 粒子发射器

blender_particles_hair
- 毛发粒子

blender_particles_force_field
- 力场效果
```

### 6. 场景增强 (Scene Enhancement)

#### 6.1 环境预设
```
blender_scene_environment_preset
- 预设环境:
  - studio (摄影棚)
  - outdoor_day (户外白天)
  - outdoor_night (户外夜晚)
  - indoor (室内)
  - stadium (体育场)
```

#### 6.2 程序化生成
```
blender_scene_scatter
- 物体散布（草、树、石头）

blender_scene_array_generate
- 阵列生成（观众席、建筑）
```

#### 6.3 HDRI 环境
```
blender_scene_hdri_setup
- HDRI 环境贴图设置
- 旋转、强度控制
```

### 7. Unity 集成 (Unity Integration)

#### 7.1 导出工具
```
blender_export_fbx
- FBX 导出（优化 Unity 设置）
- 动画烘焙
- 材质导出

blender_export_gltf
- glTF 导出
- 更好的 web 兼容性

blender_export_unity_package
- 直接导出为 Unity 包
```

#### 7.2 Unity 预设
```
blender_unity_setup_character
- 设置角色为 Unity Humanoid
- 骨骼命名规范

blender_unity_setup_animation
- 动画导出设置
- 循环设置
```

#### 7.3 LOD 生成
```
blender_unity_generate_lod
- 生成 LOD 级别
- 简化网格
```

### 8. 资产管理 (Asset Management)

#### 8.1 资产库
```
blender_asset_save
- 保存资产到库

blender_asset_load
- 从库加载资产

blender_asset_link
- 链接外部资产
```

#### 8.2 资产标记
```
blender_asset_tag
- 添加标签

blender_asset_search
- 搜索资产
```

### 9. 批量处理 (Batch Processing)

```
blender_batch_apply_material
- 批量应用材质

blender_batch_transform
- 批量变换

blender_batch_rename
- 批量重命名

blender_batch_export
- 批量导出
```

### 10. AI 辅助功能 (AI Assistance)

```
blender_ai_suggest_material
- 根据描述建议材质

blender_ai_auto_uv
- 智能 UV 展开

blender_ai_auto_rig
- 智能骨骼绑定

blender_ai_pose_match
- 姿势匹配参考图
```

---

## 三、实现优先级

### Phase 1 - 高优先级 (1-2周)
1. ✅ 角色模板系统
2. ✅ 预设动画库
3. ✅ Unity FBX 导出
4. ✅ 自动权重绑定

### Phase 2 - 中优先级 (2-4周)
1. 面部表情系统
2. 服装系统
3. 物理模拟基础
4. 批量处理工具

### Phase 3 - 低优先级 (1-2月)
1. 高级雕刻工具
2. 程序化生成
3. AI 辅助功能
4. 完整 Unity 集成

---

## 四、技术实现建议

### 1. 模块化架构
```
blender_mcp/
├── tools/
│   ├── character/
│   │   ├── templates.py
│   │   ├── face.py
│   │   ├── clothing.py
│   │   └── hair.py
│   ├── rigging/
│   │   ├── auto_rig.py
│   │   ├── face_rig.py
│   │   └── ik_fk.py
│   ├── animation/
│   │   ├── library.py
│   │   ├── presets.py
│   │   └── nla.py
│   ├── export/
│   │   ├── unity.py
│   │   └── web.py
│   └── ai/
│       └── assistant.py
```

### 2. 预设数据存储
- JSON 格式的角色模板
- 动画库 (.blend 文件)
- 材质预设库

### 3. Unity 集成方案
- 使用 FBX 作为主要交换格式
- 实现 Unity 命名规范转换
- 支持 Humanoid 骨骼映射

---

## 五、下一步行动

1. **立即**: 实现角色模板系统
2. **本周**: 添加预设动画库
3. **下周**: Unity 导出优化
4. **持续**: 收集用户反馈，迭代改进

---

## 六、参考资源

- [Blender Python API](https://docs.blender.org/api/current/)
- [Unity FBX Import](https://docs.unity3d.com/Manual/FBXImporter-Model.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
