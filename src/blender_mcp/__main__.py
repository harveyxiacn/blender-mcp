"""
Blender MCP - 命令行入口点

Usage:
    python -m blender_mcp [OPTIONS]
    
Options:
    --host TEXT         Blender 连接主机 [default: 127.0.0.1]
    --port INTEGER      Blender 连接端口 [default: 9876]
    --transport TEXT    传输方式: stdio, http [default: stdio]
    --http-port INTEGER HTTP 服务端口 [default: 8080]
    --log-level TEXT    日志级别: DEBUG, INFO, WARNING, ERROR [default: INFO]
    --version           显示版本信息
    --help              显示帮助信息
"""

import sys
import os
import signal
import atexit
import asyncio
import logging
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

from blender_mcp import __version__
from blender_mcp.server import BlenderMCPServer
from blender_mcp import config

# 使用 stderr 避免干扰 MCP stdio 通信
console = Console(file=sys.stderr)

# PID 文件路径
_PID_FILE = Path(__file__).parent.parent.parent / ".blender_mcp.pid"


def _get_pid_file() -> Path:
    """获取 PID 文件路径（优先使用临时目录）"""
    import tempfile
    return Path(tempfile.gettempdir()) / "blender_mcp.pid"


def _cleanup_zombie_processes() -> int:
    """清理残留的 blender-mcp 僵尸进程
    
    Returns:
        清理的进程数量
    """
    current_pid = os.getpid()
    killed = 0
    
    # 方法1: 通过 PID 文件清理
    pid_file = _get_pid_file()
    if pid_file.exists():
        try:
            old_pid = int(pid_file.read_text().strip())
            if old_pid != current_pid and _is_blender_mcp_process(old_pid):
                os.kill(old_pid, signal.SIGTERM)
                killed += 1
                console.print(f"[yellow]已终止残留进程 PID={old_pid}[/yellow]", highlight=False)
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass
        try:
            pid_file.unlink()
        except OSError:
            pass
    
    # 方法2: 扫描所有 Python 进程，找到 blender-mcp 相关的
    if sys.platform == "win32":
        killed += _cleanup_windows(current_pid)
    else:
        killed += _cleanup_unix(current_pid)
    
    return killed


def _is_blender_mcp_process(pid: int) -> bool:
    """检查指定 PID 是否是 blender-mcp 进程"""
    try:
        if sys.platform == "win32":
            import subprocess
            result = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/value"],
                capture_output=True, text=True, timeout=5
            )
            return "blender-mcp" in result.stdout or "blender_mcp" in result.stdout
        else:
            cmdline_path = f"/proc/{pid}/cmdline"
            if os.path.exists(cmdline_path):
                with open(cmdline_path, "r") as f:
                    cmdline = f.read()
                return "blender-mcp" in cmdline or "blender_mcp" in cmdline
    except Exception:
        pass
    return False


def _cleanup_windows(current_pid: int) -> int:
    """Windows 平台清理僵尸进程"""
    killed = 0
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "process", "where", "Name='python.exe'", "get", "ProcessId,CommandLine", "/value"],
            capture_output=True, text=True, timeout=10
        )
        
        # 解析 WMIC 输出
        entries = result.stdout.split("\n\n")
        pid = None
        cmdline = ""
        
        for entry in entries:
            for line in entry.strip().split("\n"):
                line = line.strip()
                if line.startswith("CommandLine="):
                    cmdline = line[len("CommandLine="):]
                elif line.startswith("ProcessId="):
                    try:
                        pid = int(line[len("ProcessId="):])
                    except ValueError:
                        pid = None
            
            if pid and pid != current_pid and ("blender-mcp" in cmdline or "blender_mcp" in cmdline):
                try:
                    os.kill(pid, signal.SIGTERM)
                    killed += 1
                    console.print(f"[yellow]已终止残留进程 PID={pid}[/yellow]", highlight=False)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
            
            pid = None
            cmdline = ""
    except Exception:
        pass
    return killed


def _cleanup_unix(current_pid: int) -> int:
    """Unix/macOS 平台清理僵尸进程"""
    killed = 0
    try:
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "blender.mcp"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                pid = int(line.strip())
                if pid != current_pid:
                    os.kill(pid, signal.SIGTERM)
                    killed += 1
                    console.print(f"[yellow]已终止残留进程 PID={pid}[/yellow]", highlight=False)
            except (ValueError, ProcessLookupError, PermissionError, OSError):
                pass
    except Exception:
        pass
    return killed


def _write_pid_file():
    """写入当前进程 PID 文件"""
    try:
        pid_file = _get_pid_file()
        pid_file.write_text(str(os.getpid()))
    except OSError:
        pass


def _remove_pid_file():
    """删除 PID 文件"""
    try:
        pid_file = _get_pid_file()
        if pid_file.exists():
            pid_file.unlink()
    except OSError:
        pass


def setup_logging(level: str) -> None:
    """配置日志系统（输出到 stderr，避免干扰 MCP stdio）"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )


@click.group(invoke_without_command=True)
@click.option("--host", default=config.BLENDER_HOST, help="Blender 连接主机")
@click.option("--port", default=config.BLENDER_PORT, help="Blender 连接端口")
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "http"]), help="传输方式")
@click.option("--http-port", default=config.MCP_HTTP_PORT, help="HTTP 服务端口")
@click.option("--log-level", default=config.LOG_LEVEL, type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="日志级别")
@click.version_option(version=__version__, prog_name="blender-mcp")
@click.pass_context
def main(
    ctx: click.Context,
    host: str,
    port: int,
    transport: str,
    http_port: int,
    log_level: str
) -> None:
    """Blender MCP - AI 助手的 Blender 控制接口
    
    通过 MCP 协议让 AI 助手能够直接控制 Blender，
    支持创建 3D 模型、角色、动画和场景。
    """
    if ctx.invoked_subcommand is None:
        setup_logging(log_level)
        
        # === 启动前清理僵尸进程 ===
        killed = _cleanup_zombie_processes()
        if killed > 0:
            console.print(f"[yellow]已清理 {killed} 个残留进程[/yellow]")
        
        # === 写入 PID 文件 + 注册退出钩子 ===
        _write_pid_file()
        atexit.register(_remove_pid_file)
        
        server = BlenderMCPServer(
            blender_host=host,
            blender_port=port
        )
        
        try:
            if transport == "stdio":
                # stdio 模式：stdout 用于 MCP 协议，日志输出到 stderr
                console.print(f"[green]启动 Blender MCP 服务器 (stdio 模式)[/green]")
                console.print(f"[dim]Blender 连接: {host}:{port} | PID: {os.getpid()}[/dim]")
                server.run_stdio()  # 同步调用
            else:
                console.print(f"[green]启动 Blender MCP 服务器 (HTTP 模式)[/green]")
                console.print(f"[dim]HTTP 端口: {http_port}[/dim]")
                console.print(f"[dim]Blender 连接: {host}:{port} | PID: {os.getpid()}[/dim]")
                server.run_http(http_port)  # 同步调用
        except KeyboardInterrupt:
            console.print("\n[yellow]服务器已停止[/yellow]")
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            sys.exit(1)
        finally:
            _remove_pid_file()


@main.command()
@click.option("--blender-path", default=None, help="Blender 安装路径")
@click.option("--force", is_flag=True, help="强制重新安装")
def install_addon(blender_path: Optional[str], force: bool) -> None:
    """安装 Blender 插件
    
    自动检测 Blender 安装路径并安装 MCP 插件。
    """
    from blender_mcp.installer import install_blender_addon
    
    try:
        result = install_blender_addon(blender_path, force)
        if result:
            console.print("[green]✓ Blender 插件安装成功！[/green]")
            console.print("[dim]请重启 Blender 并在偏好设置中启用插件[/dim]")
        else:
            console.print("[yellow]插件已存在，使用 --force 强制重新安装[/yellow]")
    except Exception as e:
        console.print(f"[red]安装失败: {e}[/red]")
        sys.exit(1)


@main.command()
def check() -> None:
    """检查 Blender 连接状态"""
    from blender_mcp.connection import BlenderConnection
    
    console.print("[dim]检查 Blender 连接...[/dim]")
    
    async def do_check():
        conn = BlenderConnection()
        try:
            await conn.connect()
            info = await conn.get_blender_info()
            console.print("[green]✓ Blender 连接正常[/green]")
            console.print(f"  版本: {info.get('version', '未知')}")
            console.print(f"  场景: {info.get('scene', '未知')}")
            await conn.disconnect()
        except Exception as e:
            console.print(f"[red]✗ 连接失败: {e}[/red]")
            console.print("[dim]请确保 Blender 正在运行且 MCP 插件已启用[/dim]")
    
    asyncio.run(do_check())


if __name__ == "__main__":
    main()
