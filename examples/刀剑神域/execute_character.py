"""
执行单个角色建模脚本
"""
import socket
import json
import time
import sys

def execute_character_script(script_path):
    """执行角色建模脚本"""
    print(f"\nExecuting: {script_path}")

    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        s = socket.socket()
        s.settimeout(180)
        s.connect(('127.0.0.1', 9876))

        req = {
            "id": f"build_{int(time.time())}",
            "type": "command",
            "category": "utility",
            "action": "execute_python",
            "params": {"code": code, "timeout": 180}
        }

        s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

        buf = ""
        while "\n" not in buf:
            d = s.recv(8192)
            if not d:
                break
            buf += d.decode("utf-8", errors='replace')

        s.close()

        if buf.strip():
            resp = json.loads(buf.strip())
            if resp.get("success"):
                output = resp.get("data", {}).get("output", "")
                print("SUCCESS!")
                if output:
                    print(output)
                return True
            else:
                err = resp.get("error", {})
                print(f"FAILED: {err.get('message', 'Unknown')}")
                return False
        else:
            print("No response")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python execute_character.py <script_path>")
        sys.exit(1)

    script_path = sys.argv[1]
    success = execute_character_script(script_path)
    sys.exit(0 if success else 1)
