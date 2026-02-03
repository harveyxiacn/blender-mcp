# Blender MCP 扩展路线图

本文档详细规划了让 AI 通过 MCP 全面操控 Blender 所需的所有工具模块。

## 当前已实现的工具类别

### 基础工具 (12个类别)
1. **scene** - 场景管理（新建、保存、加载）
2. **object** - 对象管理（创建、删除、变换、复制）
3. **modeling** - 网格建模（挤出、细分、修改器）
4. **material** - 材质系统（创建、编辑、分配）
5. **lighting** - 灯光系统（各类型灯光）
6. **camera** - 相机系统（创建、设置、动画）
7. **animation** - 动画系统（关键帧、时间线）
8. **character** - 角色创建（基础）
9. **rigging** - 骨骼绑定（基础）
10. **render** - 渲染设置（输出、引擎）
11. **utility** - 实用工具（Python执行、信息查询）
12. **export** - 导出功能（FBX、glTF、OBJ）

### 新增扩展工具 (7个类别)
13. **character_template** - 角色模板（Q版、写实、动漫风格）
14. **auto_rig** - 自动骨骼绑定
15. **animation_preset** - 预设动画库
16. **physics** - 物理模拟（布料、刚体、粒子）
17. **scene_advanced** - 场景增强（环境、程序化生成）
18. **batch** - 批量处理
19. **curves** - 曲线建模

---

## 待实现的工具类别

### 第一优先级 - 核心创作能力

#### 1. sculpting（雕刻工具）
让 AI 能够进行数字雕刻创作。

```python
工具列表:
- blender_sculpt_brush_stroke    # 执行笔刷笔触
- blender_sculpt_set_brush       # 设置笔刷类型（clay, grab, smooth, inflate等）
- blender_sculpt_remesh          # 重新网格化
- blender_sculpt_mask            # 蒙版操作
- blender_sculpt_multires        # 多分辨率细分
- blender_sculpt_symmetry        # 对称设置
```

#### 2. uv_mapping（UV展开）
让 AI 能够创建和编辑 UV 贴图。

```python
工具列表:
- blender_uv_unwrap              # 自动UV展开
- blender_uv_project             # 投影展开（平面、圆柱、球面、立方体）
- blender_uv_pack                # UV打包优化
- blender_uv_seam_mark           # 标记接缝
- blender_uv_transform           # UV变换
- blender_uv_pin                 # 固定UV顶点
```

#### 3. texture_painting（纹理绘制）
让 AI 能够直接在模型上绘制纹理。

```python
工具列表:
- blender_texture_paint_stroke   # 绘制笔触
- blender_texture_paint_fill     # 填充颜色
- blender_texture_paint_project  # 投影绘制
- blender_texture_paint_clone    # 克隆绘制
- blender_texture_new            # 创建新纹理
- blender_texture_bake           # 烘焙纹理
```

#### 4. nodes（节点系统）
让 AI 能够创建和编辑节点网络。

```python
工具列表:
- blender_node_add               # 添加节点
- blender_node_connect           # 连接节点
- blender_node_disconnect        # 断开连接
- blender_node_set_value         # 设置节点值
- blender_node_group_create      # 创建节点组
- blender_node_arrange           # 自动排列节点
# 支持的节点类型：
# - Shader Nodes（着色器）
# - Geometry Nodes（几何节点）
# - Compositor Nodes（合成器）
```

### 第二优先级 - 高级功能

#### 5. geometry_nodes（几何节点）
让 AI 能够使用程序化建模。

```python
工具列表:
- blender_geonodes_create        # 创建几何节点修改器
- blender_geonodes_add_node      # 添加几何节点
- blender_geonodes_connect       # 连接节点
- blender_geonodes_set_input     # 设置输入参数
- blender_geonodes_preset        # 应用预设（程序化草地、石头、建筑等）
```

#### 6. compositor（合成器）
让 AI 能够进行后期合成。

```python
工具列表:
- blender_compositor_enable      # 启用合成器
- blender_compositor_add_node    # 添加合成节点
- blender_compositor_connect     # 连接节点
- blender_compositor_preset      # 应用预设（色彩校正、模糊、辉光等）
- blender_compositor_render_layer # 管理渲染层
```

#### 7. video_editing（视频编辑）
让 AI 能够进行视频剪辑。

```python
工具列表:
- blender_vse_add_strip          # 添加视频/音频/图像条带
- blender_vse_cut                # 剪切条带
- blender_vse_transform          # 变换条带（位置、缩放）
- blender_vse_effect             # 添加效果（转场、文字）
- blender_vse_audio              # 音频操作
- blender_vse_render             # 渲染视频
```

#### 8. grease_pencil（油笔/2D动画）
让 AI 能够创建2D动画和手绘效果。

```python
工具列表:
- blender_gpencil_draw           # 绘制笔触
- blender_gpencil_layer          # 图层管理
- blender_gpencil_frame          # 帧管理
- blender_gpencil_modifier       # 油笔修改器
- blender_gpencil_material       # 油笔材质
- blender_gpencil_convert        # 转换为网格/曲线
```

### 第三优先级 - 专业工具

#### 9. simulation（高级模拟）
更完整的模拟系统。

```python
工具列表:
- blender_sim_fluid              # 流体模拟
- blender_sim_smoke              # 烟雾/火焰模拟
- blender_sim_ocean              # 海洋模拟
- blender_sim_dynamic_paint      # 动态绘制
- blender_sim_molecular          # 分子模拟（插件）
```

#### 10. hair_fur（毛发系统）
专业的毛发创建和模拟。

```python
工具列表:
- blender_hair_add               # 添加毛发系统
- blender_hair_groom             # 梳理毛发
- blender_hair_length            # 设置长度
- blender_hair_density           # 设置密度
- blender_hair_dynamics          # 毛发动力学
- blender_hair_material          # 毛发材质
```

#### 11. mocap（动作捕捉）
动作捕捉数据处理。

```python
工具列表:
- blender_mocap_import           # 导入动捕数据（BVH、FBX）
- blender_mocap_retarget         # 重定向到骨骼
- blender_mocap_clean            # 清理噪点
- blender_mocap_blend            # 混合动作
```

#### 12. asset_management（资产管理）
资产库管理。

```python
工具列表:
- blender_asset_mark             # 标记为资产
- blender_asset_catalog          # 目录管理
- blender_asset_import           # 从库导入
- blender_asset_link             # 链接资产
- blender_asset_search           # 搜索资产
```

### 第四优先级 - 集成与自动化

#### 13. addons（插件管理）
管理和使用 Blender 插件。

```python
工具列表:
- blender_addon_enable           # 启用插件
- blender_addon_disable          # 禁用插件
- blender_addon_install          # 安装插件
- blender_addon_list             # 列出插件
```

#### 14. preferences（偏好设置）
配置 Blender 设置。

```python
工具列表:
- blender_pref_get               # 获取设置
- blender_pref_set               # 设置偏好
- blender_pref_keymap            # 快捷键设置
- blender_pref_theme             # 主题设置
```

#### 15. external_integration（外部集成）
与外部工具集成。

```python
工具列表:
- blender_unity_export           # Unity 导出优化
- blender_unreal_export          # Unreal 导出优化
- blender_godot_export           # Godot 导出
- blender_substance_link         # Substance 连接
- blender_zbrush_link            # ZBrush 连接
```

#### 16. ai_assist（AI辅助功能）
AI特化的辅助工具。

```python
工具列表:
- blender_ai_describe_scene      # 描述当前场景
- blender_ai_suggest_improvement # 建议改进
- blender_ai_auto_material       # 根据描述自动创建材质
- blender_ai_reference_image     # 参考图像分析
- blender_ai_style_transfer      # 风格迁移
```

---

## 工具实现优先级矩阵

| 优先级 | 类别 | 重要性 | 复杂度 | 用户价值 |
|--------|------|--------|--------|----------|
| P0 | sculpting | 高 | 中 | 高 |
| P0 | uv_mapping | 高 | 中 | 高 |
| P0 | texture_painting | 高 | 中 | 高 |
| P0 | nodes | 高 | 高 | 极高 |
| P1 | geometry_nodes | 高 | 高 | 极高 |
| P1 | compositor | 中 | 中 | 中 |
| P1 | video_editing | 中 | 中 | 中 |
| P1 | grease_pencil | 中 | 中 | 高 |
| P2 | simulation | 中 | 高 | 中 |
| P2 | hair_fur | 中 | 高 | 中 |
| P2 | mocap | 低 | 中 | 低 |
| P2 | asset_management | 中 | 低 | 中 |
| P3 | addons | 低 | 低 | 中 |
| P3 | preferences | 低 | 低 | 低 |
| P3 | external_integration | 中 | 中 | 高 |
| P3 | ai_assist | 高 | 高 | 极高 |

---

## Blender Python API 覆盖率目标

### 当前覆盖的 bpy 模块
- `bpy.data` - 数据访问 ✅
- `bpy.context` - 上下文 ✅
- `bpy.ops.mesh` - 网格操作 ✅ (部分)
- `bpy.ops.object` - 对象操作 ✅
- `bpy.ops.material` - 材质操作 ✅
- `bpy.ops.anim` - 动画操作 ✅ (部分)
- `bpy.ops.render` - 渲染操作 ✅
- `bpy.ops.export_scene` - 导出 ✅
- `bpy.ops.rigidbody` - 刚体 ✅
- `bpy.ops.cloth` - 布料 ✅
- `bpy.ops.particle` - 粒子 ✅
- `bpy.ops.curve` - 曲线 ✅
- `bpy.ops.armature` - 骨架 ✅

### 待覆盖的 bpy 模块
- `bpy.ops.sculpt` - 雕刻 ⏳
- `bpy.ops.uv` - UV编辑 ⏳
- `bpy.ops.paint` - 绘制 ⏳
- `bpy.ops.node` - 节点 ⏳
- `bpy.ops.gpencil` - 油笔 ⏳
- `bpy.ops.sequencer` - 视频序列 ⏳
- `bpy.ops.fluid` - 流体 ⏳
- `bpy.ops.ptcache` - 缓存 ⏳
- `bpy.ops.wm` - 窗口管理 ⏳

---

## 实现建议

### 短期目标（1-2周）
1. 实现 **uv_mapping** 工具 - UV展开是纹理工作的基础
2. 实现 **nodes** 工具 - 节点系统是Blender的核心
3. 完善现有工具的错误处理

### 中期目标（1个月）
4. 实现 **geometry_nodes** - 程序化建模能力
5. 实现 **sculpting** - 雕刻能力
6. 实现 **texture_painting** - 纹理绘制

### 长期目标（3个月）
7. 实现所有 P1 和 P2 级别工具
8. 实现 **ai_assist** 工具
9. 全面的测试和文档

---

## 总结

完整实现后，AI 将能够：

1. **创建任意3D模型** - 从基础几何体到复杂角色
2. **制作完整动画** - 骨骼动画、物理模拟、动作捕捉
3. **渲染专业图像** - 材质、灯光、后期合成
4. **制作完整视频** - 剪辑、特效、输出
5. **程序化生成** - 几何节点、散布、阵列
6. **资产管理** - 组织、复用、导出
7. **外部集成** - 与游戏引擎、其他DCC工具协作

这将使 AI IDE 成为一个强大的 3D 创作助手，能够根据用户的自然语言描述完成几乎所有 Blender 操作。
