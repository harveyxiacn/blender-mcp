# Blender MCP 安装指南

## 目录

1. [系统要求](#1-系统要求)
2. [安装 MCP 服务器](#2-安装-mcp-服务器)
3. [安装 Blender 插件](#3-安装-blender-插件)
4. [IDE 配置](#4-ide-配置)
5. [验证安装](#5-验证安装)
6. [故障排除](#6-故障排除)

## 1. 系统要求

### 1.1 软件要求

| 软件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.10 | 3.12+ |
| Blender | 4.0 | 5.0+ |
| uv / pip | 最新版 | 最新版 |

### 1.2 支持的操作系统

- Windows 10/11 (x64)
- macOS 12+（Intel / Apple Silicon）
- Linux（Ubuntu 20.04+、Fedora 36+）

### 1.3 支持的 IDE

- **Cursor** — 完整 MCP 支持
- **Windsurf** — 完整 MCP 支持
- **Claude Desktop** — 通过配置文件支持 MCP
- 任何实现了 [Model Context Protocol](https://modelcontextprotocol.io/) 的 IDE

## 2. 安装 MCP 服务器

### 方式 A：使用 uv（推荐）

```bash
# 从源码安装
git clone https://github.com/your-username/blender-mcp.git
cd blender-mcp
uv sync
```

### 方式 B：使用 pip

```bash
pip install blender-mcp
```

### 方式 C：开发安装

```bash
git clone https://github.com/your-username/blender-mcp.git
cd blender-mcp
pip install -e ".[dev]"
```

## 3. 安装 Blender 插件

### 3.1 自动安装

```bash
python -m blender_mcp install-addon
```

### 3.2 手动安装

```bash
# 打包插件
python build_addon.py
# 输出：dist/blender_mcp_addon.zip
```

然后在 Blender 中：
1. **编辑 → 偏好设置 → 插件**
2. 点击 **安装...**
3. 选择 `dist/blender_mcp_addon.zip`
4. 启用 **Blender MCP** 插件
5. MCP 面板出现在 3D 视口侧边栏（按 N 键）

### 3.3 热更新（开发用）

开发者频繁修改插件时使用：

1. 打开 Blender → 编辑 → 偏好设置 → 插件 → Blender MCP
2. 设置 **开发源代码目录** 为本地插件目录
   （如 `E:\Projects\blender-mcp\addon\blender_mcp_addon`）
3. 在 MCP 面板中使用 **热更新** 按钮（3D 视口 → 侧边栏 → MCP → 开发者工具）
4. 修改代码后无需重启 Blender 即可生效

## 4. IDE 配置

### 4.1 Cursor

在项目根目录创建 `.cursor/mcp.json`：

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

### 4.2 Windsurf

1. 打开设置 → MCP Servers
2. 添加新的 Custom MCP 服务器：
   - **Command**: `uv`
   - **Arguments**: `run --directory /path/to/blender-mcp blender-mcp`
3. 启用服务器

### 4.3 Claude Desktop

编辑 `claude_desktop_config.json`：

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

### 4.4 工具 Profile 配置

编辑 `src/blender_mcp/tools_config.py` 设置工具加载策略：

```python
# "skill"   — ~31 个核心工具 + 按需加载（推荐）
# "minimal" — ~30 个核心工具
# "focused" — ~82 个工具（静态）
# "standard"— ~146 个工具
# "full"    — ~319 个工具（所有功能）
TOOL_PROFILE = "skill"
```

## 5. 验证安装

### 5.1 检查服务器

```bash
# 验证 MCP 服务器启动
uv run blender-mcp
# 应输出："Blender MCP server started"
```

### 5.2 检查 Blender 插件

1. 打开 Blender
2. 按 N 键打开侧边栏
3. 点击 "MCP" 标签页
4. 确认服务状态显示 **运行中**

### 5.3 测试连接

在 IDE 中问 AI：

```
列出当前 Blender 场景中的所有对象
```

如果返回了对象列表（如 Camera、Light、Cube），说明连接正常。

## 6. 故障排除

### 连接问题

| 症状 | 原因 | 解决方案 |
|------|------|---------|
| "Connection refused" | Blender 插件未运行 | 启用插件，检查 MCP 面板 |
| "Module not found" | 包未安装 | 运行 `uv sync` 或 `pip install -e .` |
| "Port in use" | 另一个实例在运行 | 关闭重复的 Blender/服务器实例 |
| 服务器启动但无工具 | Profile 错误或导入错误 | 检查 `tools_config.py`，用 `--log-level DEBUG` 运行 |

### 插件问题

| 症状 | 原因 | 解决方案 |
|------|------|---------|
| MCP 面板不显示 | 插件未启用 | 编辑 → 偏好设置 → 插件 → 启用 Blender MCP |
| "Failed to register" | Blender 版本过旧 | 更新到 Blender 4.0+ |
| 热更新无效 | 源路径错误 | 检查插件偏好设置中的开发源代码目录 |

### 调试模式

```bash
# 以调试日志运行服务器
python -m blender_mcp --log-level DEBUG

# 查看 Blender 控制台
# 窗口 → 切换系统控制台（Windows）
# 或从终端启动 Blender（macOS/Linux）
```
