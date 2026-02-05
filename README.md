# Blender MCP

[English](#english) | [中文](#中文)

---

## English

### Overview

Blender MCP (Model Context Protocol) enables AI assistants to control Blender directly from IDEs like Cursor, Antigravity, and Windsurf. Create 3D models, characters, animations, and scenes through natural language conversations.

### Features

- **Full Blender Control**: 155+ tools across 43 modules covering all Blender functionality
- **Multi-IDE Support**: Works with Cursor, Antigravity, Windsurf, and any MCP-compatible IDE
- **Complete 3D Pipeline**: Modeling, sculpting, UV mapping, texturing, materials, lighting, animation, rendering
- **Character Creation**: Templates, auto-rigging, facial features, hair systems, clothing
- **Animation System**: Keyframe animation, motion capture import, physics simulation
- **Post-Production**: Compositor nodes, video editing (VSE), 2D animation (Grease Pencil)
- **Game Engine Integration**: Optimized export for Unity, Unreal Engine, and Godot
- **External Software Integration**: Substance Painter, ZBrush/GoZ connectivity
- **VR/AR Support**: VR scene setup, stereo cameras, 360° panorama rendering, AR markers
- **Version Control**: Scene versioning, branching, comparison, and restoration
- **Cloud Rendering**: Render farm integration, job management, progress monitoring
- **Real-time Collaboration**: Session hosting, object locking, state synchronization
- **AI Assistance**: Scene analysis, optimization suggestions, AI-powered texture/material generation

### Quick Start

```bash
# Install MCP server
pip install blender-mcp

# Install Blender addon
python -m blender_mcp install-addon

# Configure your IDE (Cursor example)
# Create .cursor/mcp.json:
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp"]
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

- [Installation Guide](docs/INSTALLATION.md)
- [Quick Start](docs/QUICKSTART.md)
- [API Reference](docs/API_REFERENCE.md)
- [Tutorials](docs/TUTORIALS.md)
- [Architecture](docs/ARCHITECTURE.md)

### Requirements

- Python 3.10+
- Blender 4.0+ (5.0+ recommended)
- MCP-compatible IDE

### License

MIT License

---

## 中文

### 概述

Blender MCP（模型上下文协议）使 AI 助手能够从 Cursor、Antigravity、Windsurf 等 IDE 中直接控制 Blender。通过自然语言对话创建 3D 模型、角色、动画和场景。

### 功能特性

- **完整的 Blender 控制**：155+ 工具，43 个模块，覆盖 Blender 所有功能
- **多 IDE 支持**：支持 Cursor、Antigravity、Windsurf 及任何兼容 MCP 的 IDE
- **完整 3D 流程**：建模、雕刻、UV展开、纹理绘制、材质、灯光、动画、渲染
- **角色创建**：模板、自动绑定、面部特征、毛发系统、服装
- **动画系统**：关键帧动画、动作捕捉导入、物理模拟
- **后期制作**：合成器节点、视频编辑（VSE）、2D动画（油笔）
- **游戏引擎集成**：优化导出到 Unity、Unreal Engine、Godot
- **外部软件集成**：Substance Painter、ZBrush/GoZ 连接
- **VR/AR 支持**：VR 场景配置、立体相机、360° 全景渲染、AR 标记
- **版本控制**：场景版本管理、分支、比较、恢复
- **云渲染**：渲染农场集成、任务管理、进度监控
- **实时协作**：会话托管、对象锁定、状态同步
- **AI 辅助**：场景分析、优化建议、AI 驱动的纹理/材质生成

### 快速开始

```bash
# 安装 MCP 服务器
pip install blender-mcp

# 安装 Blender 插件
python -m blender_mcp install-addon

# 配置 IDE（以 Cursor 为例）
# 创建 .cursor/mcp.json：
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp"]
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

- [安装指南](docs/INSTALLATION.md)
- [快速开始](docs/QUICKSTART.md)
- [API 参考](docs/API_REFERENCE.md)
- [教程](docs/TUTORIALS.md)
- [架构设计](docs/ARCHITECTURE.md)

### 系统要求

- Python 3.10+
- Blender 4.0+（推荐 5.0+）
- 支持 MCP 的 IDE

### 许可证

MIT 许可证

---

## Project Structure / 项目结构

```
blender-mcp/
├── README.md                 # 项目说明
├── pyproject.toml           # Python 项目配置
├── setup.py                 # 安装脚本
├── LICENSE                  # 许可证
├── docs/                    # 文档目录
│   ├── ARCHITECTURE.md      # 架构设计
│   ├── INSTALLATION.md      # 安装指南
│   ├── QUICKSTART.md        # 快速开始
│   ├── API_REFERENCE.md     # API 参考
│   └── TUTORIALS.md         # 教程
├── src/
│   └── blender_mcp/         # MCP 服务器
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py
│       ├── connection.py
│       ├── tools/           # MCP 工具
│       ├── models/          # 数据模型
│       └── utils/           # 工具函数
├── addon/
│   └── blender_mcp_addon/   # Blender 插件
│       ├── __init__.py
│       ├── server.py
│       ├── executor.py
│       ├── handlers/        # 命令处理器
│       ├── operators/       # Blender 操作符
│       ├── panels/          # UI 面板
│       └── utils/           # 工具函数
└── tests/                   # 测试
    ├── test_server.py
    └── test_tools.py
```

## Contributing / 贡献

Contributions are welcome! Please read our contributing guidelines first.

欢迎贡献代码！请先阅读贡献指南。

## Support / 支持

- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share ideas
