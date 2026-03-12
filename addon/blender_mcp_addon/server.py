"""
MCP Communication Server

A socket server running inside Blender that receives and processes MCP commands.
"""

import json
import socket
import threading
import traceback
from typing import Any, Dict, Optional

import bpy

from .executor import CommandExecutor


class MCPServer:
    """MCP Socket Server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.executor = CommandExecutor()
        self.clients: list = []
    
    def start(self) -> bool:
        """Start the server"""
        if self.running:
            return True
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)  # Allow periodic checking of stop signal
            
            self.running = True
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()
            
            print(f"[MCP] Server started: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"[MCP] Failed to start server: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except Exception:
                pass
        self.clients.clear()
        
        # Close the server socket
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
        
        # Wait for the thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        print("[MCP] Server stopped")
    
    def _server_loop(self):
        """Server main loop"""
        while self.running and self.socket:
            try:
                client_socket, address = self.socket.accept()
                print(f"[MCP] Client connected: {address}")
                
                self.clients.append(client_socket)
                
                # Create a handler thread for each client
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
                    print(f"[MCP] Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle a client connection"""
        buffer = ""
        
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    buffer += data.decode("utf-8")
                    
                    # Process complete JSON messages (delimited by newlines)
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            response = self._process_message(line)
                            response_json = json.dumps(response) + "\n"
                            client_socket.send(response_json.encode("utf-8"))
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[MCP] Error processing message: {e}")
                    traceback.print_exc()
                    break
                    
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            
            print(f"[MCP] Client disconnected: {address}")
    
    def _process_message(self, message: str) -> Dict[str, Any]:
        """Process a received message"""
        try:
            request = json.loads(message)
            request_id = request.get("id", "unknown")
            msg_type = request.get("type")
            
            if msg_type == "command":
                category = request.get("category", "")
                action = request.get("action", "")
                params = request.get("params", {})
                
                # Execute Blender operations in the main thread
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
                        "message": f"Unknown message type: {msg_type}"
                    }
                }
                
        except json.JSONDecodeError as e:
            return {
                "id": "unknown",
                "success": False,
                "error": {
                    "code": "INVALID_JSON",
                    "message": f"Invalid JSON: {e}"
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
        """Execute a command in Blender's main thread"""
        import time
        
        done_event = threading.Event()
        result_container: Dict[str, Any] = {"result": None}
        raw_timeout = params.get("timeout", 30.0)
        try:
            timeout = float(raw_timeout)
        except (TypeError, ValueError):
            timeout = 30.0
        timeout = max(1.0, min(timeout, 3600.0))
        
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
                done_event.set()
        
        bpy.app.timers.register(execute, first_interval=0)
        
        if not done_event.wait(timeout=timeout):
            return {
                "success": False,
                "error": {
                    "code": "TIMEOUT",
                    "message": "Command execution timed out"
                }
            }
        
        return result_container["result"]


# Global server instance
_server: Optional[MCPServer] = None


def start_server(host: str = "127.0.0.1", port: int = 9876) -> bool:
    """Start the MCP server"""
    global _server
    
    if _server and _server.running:
        return True
    
    _server = MCPServer(host=host, port=port)
    return _server.start()


def stop_server():
    """Stop the MCP server"""
    global _server
    
    if _server:
        _server.stop()
        _server = None


def is_running() -> bool:
    """Check if the server is running"""
    return _server is not None and _server.running


def get_port() -> int:
    """Get the current port"""
    return _server.port if _server else 9876
