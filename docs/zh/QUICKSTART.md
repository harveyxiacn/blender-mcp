# Blender MCP 快速开始指南

## 简介

5 分钟内上手 Blender MCP，通过与 AI 自然语言对话控制 Blender。

## 前置条件

- 已安装 Blender 4.0+（[下载地址](https://www.blender.org/download/)），推荐 5.0+
- Python 3.10+
- 支持 MCP 的 IDE（Cursor、Windsurf 等）

## 安装

### 1. 安装 MCP 服务器

```bash
# 使用 uv（推荐）
uv pip install blender-mcp

# 或使用 pip
pip install blender-mcp
```

### 2. 安装 Blender 插件

```bash
# 自动安装
python -m blender_mcp install-addon

# 或手动打包
python build_addon.py
# 然后在 Blender 中：编辑 → 偏好设置 → 插件 → 安装 → 选择 dist/blender_mcp_addon.zip
```

### 3. 配置 IDE

**Cursor** — 创建 `.cursor/mcp.json`：
```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/blender-mcp", "blender-mcp"]
    }
  }
}
```

**Windsurf** — 通过 MCP 设置面板添加，使用相同的 command 和 args。

### 4. 启动 Blender

打开 Blender，按 N 键打开侧边栏，找到 "MCP" 面板，确认服务状态为 "运行中"。

## 第一个示例

在 IDE 中向 AI 助手发送：

```
请在 Blender 中创建一个简单的场景：
1. 删除默认的立方体
2. 创建一个球体
3. 给球体添加红色金属材质
4. 添加一个点光源照亮场景
```

AI 将自动调用 Blender MCP 工具完成这些操作。

## Skill 系统（按需加载工具）

Blender MCP 使用 **Skill 系统** 高效管理 200+ 工具。启动时只加载约 31 个核心工具，其余按需加载。

```
AI: list_skills()                    → 查看 11 个可用 Skill 组
AI: activate_skill("modeling")       → 加载 38 个建模工具
AI:（执行建模任务）
AI: deactivate_skill("modeling")     → 卸载释放上下文
AI: activate_skill("materials")      → 加载 17 个材质工具
```

### 可用 Skills

| Skill | 工具数 | 说明 |
|-------|--------|------|
| modeling | ~38 | 网格编辑、修改器、曲线、UV映射 |
| materials | ~17 | 标准和程序化材质（67种预设）、磨损效果 |
| style | ~8 | 像素风→3A级风格预设、描边、烘焙 |
| character | ~23 | 角色模板、骨骼绑定、自动绑定 |
| animation | ~17 | 关键帧、动画预设、时间线 |
| scene_setup | ~18 | 灯光、相机、世界环境、渲染设置 |
| physics | ~18 | 刚体、布料、流体、约束 |
| batch_assets | ~11 | 批量操作、资产管理 |
| advanced_3d | ~32 | 节点编辑、合成器、雕刻、纹理绘制 |
| sport_character | ~7 | 运动角色建模 |
| training | ~11 | 交互式 Blender 学习课程 |

## 常用命令示例

### 创建对象
```
在 Blender 中创建一个圆柱体，位置在 (2, 0, 0)
```

### 修改材质
```
将 Cube 的材质改为蓝色玻璃效果
```

### 创建动画
```
为 Sphere 创建一个上下跳动的动画，持续 60 帧
```

### 设置渲染
```
设置渲染分辨率为 1920x1080，使用 Cycles 引擎，渲染一张图片
```

## 常见问题

### 无法连接到 Blender？
1. 确保 Blender 正在运行
2. MCP 插件已启用
3. 服务状态显示 "运行中"

### 命令执行失败？
1. 查看 Blender 系统控制台的错误信息
2. 查看 IDE 终端的 MCP 服务器日志

### 启用详细日志
```bash
python -m blender_mcp --log-level DEBUG
```

## 下一步

- [安装指南](./INSTALLATION.md) — 详细安装说明
- [架构设计](./ARCHITECTURE.md) — 系统设计与内部机制
- [API 参考](./API_REFERENCE.md) — 完整工具文档
- [教程](./TUTORIALS.md) — 手把手项目指南
- [Skill 系统指南](./MCP_SKILL_SYSTEM_GUIDE.md) — 动态工具加载
- [贡献指南](./CONTRIBUTING.md) — 如何参与贡献
