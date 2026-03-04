# Blender MCP

[English](#english) | [中文](#中文)

---

## English

### Overview

Blender MCP (Model Context Protocol) enables AI assistants to control Blender directly from IDEs like Cursor, Windsurf, and Claude Desktop. Create 3D models, characters, animations, and scenes through natural language conversations.

### Features

- **200+ Tools**: Comprehensive Blender control across 26 modules
- **Skill System**: On-demand tool loading — only ~31 tools at startup, load more as needed (saves 70% context)
- **Multi-IDE Support**: Works with Cursor, Windsurf, Claude Desktop, and any MCP-compatible IDE
- **Complete 3D Pipeline**: Modeling, sculpting, UV mapping, texturing, materials, lighting, animation, rendering
- **67 Procedural Material Presets**: Metal, wood, stone, fabric, nature, skin, effects, toon
- **8 Style Presets**: Pixel art → AAA realistic, one-click configuration
- **Character Creation**: Templates, auto-rigging, facial features, hair systems
- **Animation System**: Keyframe animation, presets, physics simulation
- **Game Engine Export**: Optimized export for Unity, Unreal Engine, and Godot (glTF/FBX/OBJ)
- **45 Modifier Types**: Full parametric modeling support
- **High-to-Low Poly Baking**: Normal, AO, curvature, and more

### Quick Start

```bash
# Clone and install
git clone https://github.com/harveyxiacn/blender-mcp.git
cd blender-mcp
uv sync

# Install Blender addon
python build_addon.py
# Then in Blender: Edit → Preferences → Add-ons → Install → select dist/blender_mcp_addon.zip

# Configure your IDE (Cursor/Windsurf)
# Create .cursor/mcp.json:
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/blender-mcp", "blender-mcp"]
    }
  }
}
```

### Manual Addon Installation

If you need to install the addon manually:

```bash
# Build the addon zip file
python build_addon.py

# Output: dist/blender_mcp_addon.zip
```

Then in Blender:
1. Edit → Preferences → Add-ons
2. Click "Install..."
3. Select `dist/blender_mcp_addon.zip`
4. Enable "Blender MCP" addon

### Hot Reload (For Developers)

The addon supports hot reload for development:

1. Open Blender → Edit → Preferences → Add-ons → Blender MCP
2. Set "Dev Source Path" to your local addon source directory (e.g., `E:\Projects\blender-mcp\addon\blender_mcp_addon`)
3. Use the "Hot Reload" button in the MCP panel (View3D → Sidebar → MCP → Developer Tools) or in Preferences
4. Changes are applied immediately without restarting Blender

### Documentation

| Document | English | 中文 |
|----------|---------|------|
| Quick Start | [QUICKSTART](docs/en/QUICKSTART.md) | [快速开始](docs/zh/QUICKSTART.md) |
| Installation | [INSTALLATION](docs/en/INSTALLATION.md) | [安装指南](docs/zh/INSTALLATION.md) |
| Architecture | [ARCHITECTURE](docs/en/ARCHITECTURE.md) | [架构设计](docs/zh/ARCHITECTURE.md) |
| API Reference | [API_REFERENCE](docs/en/API_REFERENCE.md) | [API 参考](docs/zh/API_REFERENCE.md) |
| Tutorials | [TUTORIALS](docs/en/TUTORIALS.md) | [教程](docs/zh/TUTORIALS.md) |
| Skill System Guide | [MCP_SKILL_SYSTEM_GUIDE](docs/en/MCP_SKILL_SYSTEM_GUIDE.md) | [Skill 系统指南](docs/zh/MCP_SKILL_SYSTEM_GUIDE.md) |
| Contributing | [CONTRIBUTING](docs/en/CONTRIBUTING.md) | [贡献指南](docs/zh/CONTRIBUTING.md) |
| Changelog | [CHANGELOG](docs/en/CHANGELOG.md) | [更新日志](docs/zh/CHANGELOG.md) |
| Roadmap | [ROADMAP](docs/en/ROADMAP.md) | [路线图](docs/zh/ROADMAP.md) |

### Requirements

- Python 3.10+
- Blender 4.0+ (5.0+ recommended)
- MCP-compatible IDE (Cursor, Windsurf, Claude Desktop)

### License

MIT License

---

## 中文

### 概述

Blender MCP（模型上下文协议）使 AI 助手能够从 Cursor、Windsurf、Claude Desktop 等 IDE 中直接控制 Blender。通过自然语言对话创建 3D 模型、角色、动画和场景。

### 功能特性

- **200+ 工具**：26 个模块全面覆盖 Blender 功能
- **Skill 系统**：按需加载工具——启动仅 ~31 个工具，按需加载更多（节省 70% 上下文）
- **多 IDE 支持**：支持 Cursor、Windsurf、Claude Desktop 及任何兼容 MCP 的 IDE
- **完整 3D 流程**：建模、雕刻、UV展开、纹理绘制、材质、灯光、动画、渲染
- **67 种程序化材质预设**：金属、木纹、石材、织物、自然、皮肤、特效、卡通
- **8 种风格预设**：像素风→3A写实，一键配置
- **角色创建**：模板、自动绑定、面部特征、毛发系统
- **动画系统**：关键帧动画、预设、物理模拟
- **游戏引擎导出**：优化导出到 Unity、Unreal Engine、Godot（glTF/FBX/OBJ）
- **45 种修改器类型**：完整参数化建模支持
- **高低模烘焙**：法线、AO、曲率等贴图烘焙

### 快速开始

```bash
# 克隆并安装
git clone https://github.com/harveyxiacn/blender-mcp.git
cd blender-mcp
uv sync

# 安装 Blender 插件
python build_addon.py
# 然后在 Blender 中：编辑 → 偏好设置 → 插件 → 安装 → 选择 dist/blender_mcp_addon.zip

# 配置 IDE（Cursor/Windsurf）
# 创建 .cursor/mcp.json：
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/blender-mcp", "blender-mcp"]
    }
  }
}
```

### 手动安装插件

如需手动安装插件：

```bash
# 打包插件 zip 文件
python build_addon.py

# 输出: dist/blender_mcp_addon.zip
```

然后在 Blender 中：
1. 编辑 → 偏好设置 → 插件
2. 点击「安装...」
3. 选择 `dist/blender_mcp_addon.zip`
4. 启用「Blender MCP」插件

### 热更新（开发者功能）

插件支持热更新，方便开发调试：

1. 打开 Blender → 编辑 → 偏好设置 → 插件 → Blender MCP
2. 设置「开发源代码目录」为本地源码目录（如 `E:\Projects\blender-mcp\addon\blender_mcp_addon`）
3. 在 MCP 面板中使用「热更新」按钮（视图3D → 侧边栏 → MCP → 开发者工具）或在偏好设置中使用
4. 修改代码后无需重启 Blender 即可生效

### 文档

| 文档 | English | 中文 |
|------|---------|------|
| 快速开始 | [QUICKSTART](docs/en/QUICKSTART.md) | [快速开始](docs/zh/QUICKSTART.md) |
| 安装指南 | [INSTALLATION](docs/en/INSTALLATION.md) | [安装指南](docs/zh/INSTALLATION.md) |
| 架构设计 | [ARCHITECTURE](docs/en/ARCHITECTURE.md) | [架构设计](docs/zh/ARCHITECTURE.md) |
| API 参考 | [API_REFERENCE](docs/en/API_REFERENCE.md) | [API 参考](docs/zh/API_REFERENCE.md) |
| 教程 | [TUTORIALS](docs/en/TUTORIALS.md) | [教程](docs/zh/TUTORIALS.md) |
| Skill 系统 | [MCP_SKILL_SYSTEM_GUIDE](docs/en/MCP_SKILL_SYSTEM_GUIDE.md) | [Skill 系统指南](docs/zh/MCP_SKILL_SYSTEM_GUIDE.md) |
| 贡献指南 | [CONTRIBUTING](docs/en/CONTRIBUTING.md) | [贡献指南](docs/zh/CONTRIBUTING.md) |
| 更新日志 | [CHANGELOG](docs/en/CHANGELOG.md) | [更新日志](docs/zh/CHANGELOG.md) |
| 路线图 | [ROADMAP](docs/en/ROADMAP.md) | [路线图](docs/zh/ROADMAP.md) |

### 系统要求

- Python 3.10+
- Blender 4.0+（推荐 5.0+）
- 支持 MCP 的 IDE（Cursor、Windsurf、Claude Desktop）

### 许可证

MIT 许可证

---

## Project Structure / 项目结构

```
blender-mcp/
├── README.md                 # Project README
├── pyproject.toml            # Python project config
├── build_addon.py            # Addon build script
├── LICENSE                   # MIT License
├── docs/
│   ├── en/                   # English documentation
│   └── zh/                   # 中文文档
├── src/blender_mcp/          # MCP Server
│   ├── server.py             # Main server class
│   ├── connection.py         # Blender TCP connection
│   ├── skill_manager.py      # Dynamic skill system
│   ├── tools_config.py       # Tool profile config
│   └── tools/                # MCP tool modules (26+)
│       ├── skills.py         # Skill meta-tools
│       ├── scene.py          # Scene management
│       ├── object.py         # Object operations
│       ├── modeling.py       # Mesh editing
│       └── ...               # More modules
├── addon/blender_mcp_addon/  # Blender Addon
│   ├── server.py             # TCP server
│   ├── executor.py           # Command dispatcher
│   ├── handlers/             # Blender API handlers
│   ├── operators/            # Blender operators
│   └── panels/               # UI panels
```

## Contributing / 贡献

Contributions are welcome! Please read our [Contributing Guide](docs/en/CONTRIBUTING.md).

欢迎贡献代码！请阅读[贡献指南](docs/zh/CONTRIBUTING.md)。

## Support / 支持

- **GitHub Issues**: Report bugs or request features / 报告 Bug 或提交功能需求
- **Discussions**: Ask questions and share ideas / 提问和分享想法

