"""
MCP 通信服务器

在 Blender 中运行的 Socket 服务器，接收并处理 MCP 命令。
"""

import json
import socket
import threading
import traceback
from typing import Any, Dict, Optional, Callable

import bpy

from .executor import CommandExecutor


class MCPServer:
    """MCP Socket 服务器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.executor = CommandExecutor()
        self.clients: list = []
    
    def start(self) -> bool:
        """启动服务器"""
        if self.running:
            return True
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)  # 允许定期检查停止信号
            
            self.running = True
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()
            
            print(f"[MCP] 服务器已启动: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"[MCP] 启动服务器失败: {e}")
            self.running = False
            return False
    
    def stop(self):
        """停止服务器"""
        self.running = False
        
        # 关闭所有客户端连接
        for client in self.clients:
            try:
                client.close()
            except Exception:
                pass
        self.clients.clear()
        
        # 关闭服务器 socket
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
        
        # 等待线程结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        print("[MCP] 服务器已停止")
    
    def _server_loop(self):
        """服务器主循环"""
        while self.running and self.socket:
            try:
                client_socket, address = self.socket.accept()
                print(f"[MCP] 客户端连接: {address}")
                
                self.clients.append(client_socket)
                
                # 为每个客户端创建处理线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[MCP] 接受连接错误: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address):
        """处理客户端连接"""
        buffer = ""
        
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    buffer += data.decode("utf-8")
                    
                    # 处理完整的 JSON 消息（以换行符分隔）
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            response = self._process_message(line)
                            response_json = json.dumps(response) + "\n"
                            client_socket.send(response_json.encode("utf-8"))
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[MCP] 处理消息错误: {e}")
                    traceback.print_exc()
                    break
                    
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            
            print(f"[MCP] 客户端断开: {address}")
    
    def _process_message(self, message: str) -> Dict[str, Any]:
        """处理收到的消息"""
        try:
            request = json.loads(message)
            request_id = request.get("id", "unknown")
            msg_type = request.get("type")
            
            if msg_type == "command":
                category = request.get("category", "")
                action = request.get("action", "")
                params = request.get("params", {})
                
                # 在主线程中执行 Blender 操作
                result = self._execute_in_main_thread(category, action, params)
                
                return {
                    "id": request_id,
                    **result
                }
            
            else:
                return {
                    "id": request_id,
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_MESSAGE_TYPE",
                        "message": f"未知的消息类型: {msg_type}"
                    }
                }
                
        except json.JSONDecodeError as e:
            return {
                "id": "unknown",
                "success": False,
                "error": {
                    "code": "INVALID_JSON",
                    "message": f"无效的 JSON: {e}"
                }
            }
        except Exception as e:
            return {
                "id": "unknown",
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
    
    def _execute_in_main_thread(
        self,
        category: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """在 Blender 主线程中执行命令"""
        result_container = {"result": None, "done": False}
        
        def execute():
            try:
                result_container["result"] = self.executor.execute(
                    category, action, params
                )
            except Exception as e:
                result_container["result"] = {
                    "success": False,
                    "error": {
                        "code": "EXECUTION_ERROR",
                        "message": str(e)
                    }
                }
            finally:
                result_container["done"] = True
        
        # 使用 bpy.app.timers 在主线程中执行
        bpy.app.timers.register(execute, first_interval=0)
        
        # 等待执行完成
        import time
        timeout = 30.0  # 30 秒超时
        start_time = time.time()
        
        while not result_container["done"]:
            if time.time() - start_time > timeout:
                return {
                    "success": False,
                    "error": {
                        "code": "TIMEOUT",
                        "message": "命令执行超时"
                    }
                }
            time.sleep(0.01)
        
        return result_container["result"]


# 全局服务器实例
_server: Optional[MCPServer] = None


def start_server(port: int = 9876) -> bool:
    """启动 MCP 服务器"""
    global _server
    
    if _server and _server.running:
        return True
    
    _server = MCPServer(port=port)
    return _server.start()


def stop_server():
    """停止 MCP 服务器"""
    global _server
    
    if _server:
        _server.stop()
        _server = None


def is_running() -> bool:
    """检查服务器是否运行中"""
    return _server is not None and _server.running


def get_port() -> int:
    """获取当前端口"""
    return _server.port if _server else 9876
