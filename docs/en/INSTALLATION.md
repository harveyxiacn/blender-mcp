# Blender MCP Installation Guide

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Install MCP Server](#2-install-mcp-server)
3. [Install Blender Addon](#3-install-blender-addon)
4. [IDE Configuration](#4-ide-configuration)
5. [Verify Installation](#5-verify-installation)
6. [Troubleshooting](#6-troubleshooting)

## 1. System Requirements

### 1.1 Software Requirements

| Software | Minimum | Recommended |
|----------|---------|-------------|
| Python | 3.10 | 3.12+ |
| Blender | 4.0 | 5.0+ |
| uv / pip | latest | latest |

### 1.2 Supported Operating Systems

- Windows 10/11 (x64)
- macOS 12+ (Intel / Apple Silicon)
- Linux (Ubuntu 20.04+, Fedora 36+)

### 1.3 Supported IDEs

- **Cursor** — Full MCP support
- **Windsurf** — Full MCP support
- **Claude Desktop** — MCP support via config
- Any IDE implementing the [Model Context Protocol](https://modelcontextprotocol.io/)

## 2. Install MCP Server

### Option A: Using uv (Recommended)

```bash
# Install from source
git clone https://github.com/your-username/blender-mcp.git
cd blender-mcp
uv sync
```

### Option B: Using pip

```bash
pip install blender-mcp
```

### Option C: Development Install

```bash
git clone https://github.com/your-username/blender-mcp.git
cd blender-mcp
pip install -e ".[dev]"
```

## 3. Install Blender Addon

### 3.1 Auto Install

```bash
python -m blender_mcp install-addon
```

### 3.2 Manual Install

```bash
# Build the addon zip
python build_addon.py
# Output: dist/blender_mcp_addon.zip
```

Then in Blender:
1. **Edit → Preferences → Add-ons**
2. Click **Install...**
3. Select `dist/blender_mcp_addon.zip`
4. Enable **Blender MCP** addon
5. The MCP panel appears in the 3D Viewport sidebar (press N)

### 3.3 Hot Reload (Development)

For developers who modify the addon frequently:

1. Open Blender → Edit → Preferences → Add-ons → Blender MCP
2. Set **Dev Source Path** to your local addon directory
   (e.g., `E:\Projects\blender-mcp\addon\blender_mcp_addon`)
3. Use the **Hot Reload** button in the MCP panel (3D Viewport → Sidebar → MCP → Developer Tools)
4. Changes take effect immediately without restarting Blender

## 4. IDE Configuration

### 4.1 Cursor

Create `.cursor/mcp.json` in your project root:

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

1. Open Settings → MCP Servers
2. Add a new Custom MCP server:
   - **Command**: `uv`
   - **Arguments**: `run --directory /path/to/blender-mcp blender-mcp`
3. Enable the server

### 4.3 Claude Desktop

Edit `claude_desktop_config.json`:

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

### 4.4 Tool Profile Configuration

Edit `src/blender_mcp/tools_config.py` to set the tool loading strategy:

```python
# "skill"   — ~31 core tools + on-demand loading (recommended)
# "minimal" — ~30 core tools only
# "focused" — ~82 tools (static)
# "standard"— ~146 tools
# "full"    — ~319 tools (all features)
TOOL_PROFILE = "skill"
```

## 5. Verify Installation

### 5.1 Check Server

```bash
# Verify the MCP server starts
uv run blender-mcp
# Should output: "Blender MCP server started"
```

### 5.2 Check Blender Addon

1. Open Blender
2. Press N to open the sidebar
3. Click the "MCP" tab
4. Verify server status shows **Running**

### 5.3 Test Connection

In your IDE, ask the AI:

```
List all objects in the current Blender scene
```

If you get a list of objects (e.g., Camera, Light, Cube), the connection is working.

## 6. Troubleshooting

### Connection Failed

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Connection refused" | Blender addon not running | Enable addon, check MCP panel |
| "Module not found" | Package not installed | Run `uv sync` or `pip install -e .` |
| "Port in use" | Another instance running | Close duplicate Blender/server instances |
| Server starts but no tools | Wrong profile or import error | Check `tools_config.py`, run with `--log-level DEBUG` |

### Addon Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| MCP panel missing | Addon not enabled | Edit → Preferences → Add-ons → Enable Blender MCP |
| "Failed to register" | Blender version too old | Update to Blender 4.0+ |
| Hot reload not working | Wrong source path | Verify Dev Source Path in addon preferences |

### Debug Mode

```bash
# Run server with debug logging
python -m blender_mcp --log-level DEBUG

# Check Blender console
# Window → Toggle System Console (Windows)
# Or launch Blender from terminal (macOS/Linux)
```
