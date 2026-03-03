"""
Blender 连接模块

管理与 Blender 插件的 Socket 通信，支持自动重连和心跳检测。
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9876
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
HEARTBEAT_INTERVAL = 15.0
HEARTBEAT_TIMEOUT = 5.0
RECONNECT_BACKOFF_BASE = 1.0
RECONNECT_BACKOFF_MAX = 30.0
READ_BUFFER_SIZE = 65536


class BlenderConnectionError(Exception):
    """Blender 连接错误"""
    pass


class BlenderConnection:
    """Blender Socket 连接管理器
    
    负责：
    - 建立和维护与 Blender 插件的 Socket 连接
    - 发送命令和接收响应
    - 心跳检测和自动重连
    """
    
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_reconnect: bool = True,
        heartbeat_interval: float = HEARTBEAT_INTERVAL,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.auto_reconnect = auto_reconnect
        self.heartbeat_interval = heartbeat_interval
        
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._lock = asyncio.Lock()
        
        self._pending_requests: dict[str, asyncio.Future] = {}
        self._read_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        self._last_activity: float = 0.0
        self._reconnect_count: int = 0
        self._total_commands: int = 0
        self._failed_commands: int = 0
    
    @property
    def connected(self) -> bool:
        return self._connected and self._writer is not None
    
    @property
    def stats(self) -> dict[str, Any]:
        """连接统计信息"""
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "reconnect_count": self._reconnect_count,
            "total_commands": self._total_commands,
            "failed_commands": self._failed_commands,
            "pending_requests": len(self._pending_requests),
            "last_activity": self._last_activity,
        }
    
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
                    self._last_activity = time.monotonic()
                    
                    self._read_task = asyncio.create_task(self._read_responses())
                    
                    if self.heartbeat_interval > 0:
                        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                    
                    logger.info("Blender 连接成功")
                    return
                    
                except asyncio.TimeoutError:
                    logger.warning(f"连接超时 (尝试 {attempt + 1})")
                except ConnectionRefusedError:
                    logger.warning(f"连接被拒绝 (尝试 {attempt + 1})")
                except Exception as e:
                    logger.warning(f"连接失败: {e} (尝试 {attempt + 1})")
                
                if attempt < self.max_retries - 1:
                    backoff = min(
                        RECONNECT_BACKOFF_BASE * (2 ** attempt),
                        RECONNECT_BACKOFF_MAX
                    )
                    await asyncio.sleep(backoff)
            
            raise BlenderConnectionError(
                f"无法连接到 Blender ({self.host}:{self.port})，"
                "请确保 Blender 正在运行且 MCP 插件已启用"
            )
    
    async def disconnect(self) -> None:
        """断开连接"""
        async with self._lock:
            await self._cleanup()
            logger.info("Blender 连接已断开")

    async def _cleanup(self) -> None:
        """清理连接资源（调用方需持有 _lock）"""
        self._connected = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
        
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
        
        for future in self._pending_requests.values():
            if not future.done():
                future.set_exception(BlenderConnectionError("连接已断开"))
        self._pending_requests.clear()

    async def _reconnect(self) -> bool:
        """尝试重新连接（不持锁调用）"""
        if not self.auto_reconnect:
            return False
        
        logger.info("尝试自动重连...")
        self._reconnect_count += 1
        
        async with self._lock:
            await self._cleanup()
        
        try:
            await self.connect()
            return True
        except BlenderConnectionError:
            logger.warning("自动重连失败")
            return False
    
    async def _heartbeat_loop(self) -> None:
        """定期发送心跳检测连接存活"""
        while self._connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if not self._connected:
                    break
                
                idle = time.monotonic() - self._last_activity
                if idle < self.heartbeat_interval:
                    continue
                
                request_id = f"heartbeat-{uuid.uuid4().hex[:8]}"
                request = {
                    "id": request_id,
                    "type": "command",
                    "category": "system",
                    "action": "get_info",
                    "params": {}
                }
                
                future: asyncio.Future = asyncio.get_running_loop().create_future()
                self._pending_requests[request_id] = future
                
                message = json.dumps(request) + "\n"
                if self._writer is None:
                    break
                self._writer.write(message.encode("utf-8"))
                await self._writer.drain()
                
                await asyncio.wait_for(future, timeout=HEARTBEAT_TIMEOUT)
                self._last_activity = time.monotonic()
                logger.debug("心跳正常")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"心跳失败: {e}")
                if self._connected:
                    asyncio.create_task(self._reconnect())
                break
    
    async def _read_responses(self) -> None:
        """持续读取响应"""
        buffer = ""
        
        while self._connected and self._reader:
            try:
                data = await self._reader.read(READ_BUFFER_SIZE)
                if not data:
                    logger.warning("连接已关闭")
                    break
                
                buffer += data.decode("utf-8", errors="replace")
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            response = json.loads(line)
                            self._last_activity = time.monotonic()
                            await self._handle_response(response)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 解析错误: {e}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"读取响应错误: {e}")
                break
        
        self._connected = False
        if self._pending_requests:
            error = BlenderConnectionError("连接已断开")
            for future in list(self._pending_requests.values()):
                if not future.done():
                    future.set_exception(error)
            self._pending_requests.clear()
        
        if self.auto_reconnect:
            asyncio.create_task(self._reconnect())
    
    async def _handle_response(self, response: dict[str, Any]) -> None:
        """处理响应消息"""
        request_id = response.get("id")
        
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests.pop(request_id)
            if not future.done():
                future.set_result(response)
        else:
            logger.debug(f"收到未匹配的响应: {response}")
    
    async def send_command(
        self,
        category: str,
        action: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """发送命令并等待响应，失败时自动重连重试
        
        Args:
            category: 命令类别
            action: 具体操作
            params: 操作参数
            
        Returns:
            响应结果
        """
        self._total_commands += 1
        
        for attempt in range(2):
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
            
            future: asyncio.Future = asyncio.get_running_loop().create_future()
            self._pending_requests[request_id] = future
            
            try:
                message = json.dumps(request) + "\n"
                if self._writer is None:
                    raise BlenderConnectionError("连接不可用")
                self._writer.write(message.encode("utf-8"))
                await self._writer.drain()
                
                logger.debug(f"发送命令: {category}.{action}")
                
                response = await asyncio.wait_for(future, timeout=self.timeout)
                self._last_activity = time.monotonic()
                
                return response
                
            except asyncio.TimeoutError:
                self._pending_requests.pop(request_id, None)
                self._failed_commands += 1
                raise BlenderConnectionError(f"命令超时: {category}.{action}")
            except BlenderConnectionError:
                self._pending_requests.pop(request_id, None)
                self._failed_commands += 1
                raise
            except Exception as e:
                self._pending_requests.pop(request_id, None)
                if self._connected:
                    try:
                        await self.disconnect()
                    except Exception:
                        pass
                
                if attempt == 0 and self.auto_reconnect:
                    logger.info(f"命令失败，尝试重连: {e}")
                    continue
                
                self._failed_commands += 1
                raise BlenderConnectionError(f"命令失败: {e}")
        
        self._failed_commands += 1
        raise BlenderConnectionError(f"命令最终失败: {category}.{action}")
    
    async def get_blender_info(self) -> dict[str, Any]:
        """获取 Blender 信息"""
        result = await self.send_command("system", "get_info", {})
        return result.get("data", {})
