# Blender MCP

[English](#english) | [中文](#中文)

---

## English

### Overview

Blender MCP (Model Context Protocol) enables AI assistants to control Blender directly from IDEs like Cursor, Antigravity, and Windsurf. Create 3D models, characters, animations, and scenes through natural language conversations.

### Features

- **Full Blender Control**: Scene management, object manipulation, modeling, materials, lighting, animation, and rendering
- **Multi-IDE Support**: Works with Cursor, Antigravity, Windsurf, and any MCP-compatible IDE
- **Character Creation**: Build humanoid meshes with facial features and rigging
- **Animation System**: Keyframe animation with various interpolation types
- **Rendering**: Support for Cycles, EEVEE, and EEVEE Next

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

- **完整的 Blender 控制**：场景管理、对象操作、建模、材质、灯光、动画和渲染
- **多 IDE 支持**：支持 Cursor、Antigravity、Windsurf 及任何兼容 MCP 的 IDE
- **角色创建**：构建人形网格、面部特征和骨骼绑定
- **动画系统**：关键帧动画，支持多种插值类型
- **渲染支持**：支持 Cycles、EEVEE 和 EEVEE Next

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
