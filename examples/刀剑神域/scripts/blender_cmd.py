"""
直接Socket通信工具 - 绕过MCP管道，直接向Blender发送命令
用法: python blender_cmd.py <category> <action> [json_params]
"""
import socket
import json
import sys
import time

def send_command(category, action, params=None, host="127.0.0.1", port=9876):
    """发送命令到Blender MCP Addon"""
    if params is None:
        params = {}
    
    request = {
        "id": f"cmd_{int(time.time()*1000)}",
        "type": "command",
        "category": category,
        "action": action,
        "params": params
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    
    try:
        sock.connect((host, port))
        message = json.dumps(request) + "\n"
        sock.send(message.encode("utf-8"))
        
        # 接收响应
        buffer = ""
        while "\n" not in buffer:
            data = sock.recv(4096)
            if not data:
                break
            buffer += data.decode("utf-8")
        
        if buffer.strip():
            response = json.loads(buffer.strip())
            return response
        return {"error": "No response"}
    finally:
        sock.close()

def execute_python(code):
    """在Blender中执行Python代码"""
    return send_command("system", "execute_python", {"code": code})

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python blender_cmd.py <category> <action> [json_params]")
        sys.exit(1)
    
    category = sys.argv[1]
    action = sys.argv[2]
    params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    
    result = send_command(category, action, params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
