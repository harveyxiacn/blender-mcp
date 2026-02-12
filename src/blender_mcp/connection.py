"""
Blender 连接模块

管理与 Blender 插件的 Socket 通信。
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BlenderConnectionError(Exception):
    """Blender 连接错误"""
    pass


class BlenderConnection:
    """Blender Socket 连接管理器
    
    负责：
    - 建立和维护与 Blender 插件的 Socket 连接
    - 发送命令和接收响应
    - 处理连接错误和重连
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9876,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """初始化连接
        
        Args:
            host: Blender 插件服务器主机
            port: Blender 插件服务器端口
            timeout: 命令超时时间（秒）
            max_retries: 最大重试次数
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._lock = asyncio.Lock()
        
        # 待处理的请求
        self._pending_requests: dict[str, asyncio.Future] = {}
        
        # 响应读取任务
        self._read_task: Optional[asyncio.Task] = None
    
    @property
    def connected(self) -> bool:
        """是否已连接"""
        return self._connected and self._writer is not None
    
    async def connect(self) -> None:
        """建立连接"""
        async with self._lock:
            if self._connected:
                return
            
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"连接 Blender: {self.host}:{self.port} (尝试 {attempt + 1}/{self.max_retries})")
                    
                    self._reader, self._writer = await asyncio.wait_for(
                        asyncio.open_connection(self.host, self.port),
                        timeout=5.0
                    )
                    
                    self._connected = True
                    
                    # 启动响应读取任务
                    self._read_task = asyncio.create_task(self._read_responses())
                    
                    logger.info("Blender 连接成功")
                    return
                    
                except asyncio.TimeoutError:
                    logger.warning(f"连接超时 (尝试 {attempt + 1})")
                except ConnectionRefusedError:
                    logger.warning(f"连接被拒绝 (尝试 {attempt + 1})")
                except Exception as e:
                    logger.warning(f"连接失败: {e} (尝试 {attempt + 1})")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1.0)
            
            raise BlenderConnectionError(
                f"无法连接到 Blender ({self.host}:{self.port})，"
                "请确保 Blender 正在运行且 MCP 插件已启用"
            )
    
    async def disconnect(self) -> None:
        """断开连接"""
        async with self._lock:
            self._connected = False
            
            if self._read_task:
                self._read_task.cancel()
                try:
                    await self._read_task
                except asyncio.CancelledError:
                    pass
                self._read_task = None
            
            if self._writer:
                self._writer.close()
                try:
                    await self._writer.wait_closed()
                except Exception:
                    pass
                self._writer = None
            
            self._reader = None
            
            # 取消所有待处理的请求
            for future in self._pending_requests.values():
                if not future.done():
                    future.set_exception(BlenderConnectionError("连接已断开"))
            self._pending_requests.clear()
            
            logger.info("Blender 连接已断开")
    
    async def _read_responses(self) -> None:
        """持续读取响应"""
        buffer = ""
        
        while self._connected and self._reader:
            try:
                data = await self._reader.read(4096)
                if not data:
                    logger.warning("连接已关闭")
                    break
                
                buffer += data.decode("utf-8")
                
                # 处理完整的 JSON 消息
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            response = json.loads(line)
                            await self._handle_response(response)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 解析错误: {e}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"读取响应错误: {e}")
                break
        
        # 连接断开，标记所有待处理请求为失败
        self._connected = False
        if self._pending_requests:
            error = BlenderConnectionError("连接已断开")
            for future in list(self._pending_requests.values()):
                if not future.done():
                    future.set_exception(error)
            self._pending_requests.clear()
    
    async def _handle_response(self, response: dict[str, Any]) -> None:
        """处理响应消息"""
        request_id = response.get("id")
        
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests.pop(request_id)
            if not future.done():
                future.set_result(response)
        else:
            # 可能是服务器推送的消息
            logger.debug(f"收到未匹配的响应: {response}")
    
    async def send_command(
        self,
        category: str,
        action: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """发送命令并等待响应
        
        Args:
            category: 命令类别
            action: 具体操作
            params: 操作参数
            
        Returns:
            响应结果
        """
        if not self.connected:
            await self.connect()
        
        request_id = str(uuid.uuid4())
        
        request = {
            "id": request_id,
            "type": "command",
            "category": category,
            "action": action,
            "params": params
        }
        
        # 创建 Future 等待响应
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            # 发送请求
            message = json.dumps(request) + "\n"
            if self._writer is None:
                raise BlenderConnectionError("连接不可用")
            self._writer.write(message.encode("utf-8"))
            await self._writer.drain()
            
            logger.debug(f"发送命令: {category}.{action}")
            
            # 等待响应
            response = await asyncio.wait_for(future, timeout=self.timeout)
            
            return response
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise BlenderConnectionError(f"命令超时: {category}.{action}")
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            # 写入/读取失败后主动清理连接，避免后续请求复用坏连接
            if self._connected:
                try:
                    await self.disconnect()
                except Exception:
                    pass
            raise BlenderConnectionError(f"命令失败: {e}")
    
    async def get_blender_info(self) -> dict[str, Any]:
        """获取 Blender 信息"""
        result = await self.send_command("system", "get_info", {})
        return result.get("data", {})
