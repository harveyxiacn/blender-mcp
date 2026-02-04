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
import asyncio
import logging
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from blender_mcp import __version__
from blender_mcp.server import BlenderMCPServer

# 使用 stderr 避免干扰 MCP stdio 通信
console = Console(file=sys.stderr)


def setup_logging(level: str) -> None:
    """配置日志系统（输出到 stderr，避免干扰 MCP stdio）"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )


@click.group(invoke_without_command=True)
@click.option("--host", default="127.0.0.1", help="Blender 连接主机")
@click.option("--port", default=9876, help="Blender 连接端口")
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "http"]), help="传输方式")
@click.option("--http-port", default=8080, help="HTTP 服务端口")
@click.option("--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="日志级别")
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
        
        server = BlenderMCPServer(
            blender_host=host,
            blender_port=port
        )
        
        try:
            if transport == "stdio":
                # stdio 模式：stdout 用于 MCP 协议，日志输出到 stderr
                console.print(f"[green]启动 Blender MCP 服务器 (stdio 模式)[/green]")
                console.print(f"[dim]Blender 连接: {host}:{port}[/dim]")
                asyncio.run(server.run_stdio())
            else:
                console.print(f"[green]启动 Blender MCP 服务器 (HTTP 模式)[/green]")
                console.print(f"[dim]HTTP 端口: {http_port}[/dim]")
                console.print(f"[dim]Blender 连接: {host}:{port}[/dim]")
                asyncio.run(server.run_http(http_port))
        except KeyboardInterrupt:
            console.print("\n[yellow]服务器已停止[/yellow]")
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            sys.exit(1)


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
