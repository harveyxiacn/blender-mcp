"""
通过Blender MCP Socket执行刀剑神域角色建模
"""
import socket
import json
import os
import time

def execute_script_in_blender(script_path, timeout=180):
    """通过socket在Blender中执行Python脚本"""
    print(f"\n执行脚本: {script_path}")

    # 读取脚本内容
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 连接到Blender MCP服务器
    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect(('127.0.0.1', 9876))

        # 构建请求
        req = {
            "id": f"sao_build_{int(time.time())}",
            "type": "command",
            "category": "utility",
            "action": "execute_python",
            "params": {"code": code, "timeout": timeout}
        }

        # 发送请求
        s.send((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))

        # 接收响应
        buf = ""
        while "\n" not in buf:
            d = s.recv(8192)
            if not d:
                break
            buf += d.decode("utf-8", errors='replace')

        s.close()

        # 解析响应
        if buf.strip():
            resp = json.loads(buf.strip())
            if resp.get("success"):
                output = resp.get("data", {}).get("output", "")
                print(f"✓ 成功: {os.path.basename(script_path)}")
                if output:
                    print(output)
                return True
            else:
                err = resp.get("error", {})
                print(f"✗ 失败: {err.get('message', '未知错误')}")
                return False
        else:
            print("✗ 无响应")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    finally:
        try:
            s.close()
        except:
            pass

def main():
    print("=" * 60)
    print("刀剑神域角色建模 - Blender MCP执行器")
    print("=" * 60)

    # 脚本目录
    script_dir = os.path.join(os.path.dirname(__file__), "scripts")

    # 要执行的脚本列表
    scripts = [
        "AAA_v2_kirito.py",    # 桐人
        "AAA_v2_asuna.py",     # 亚丝娜
        "AAA_v2_klein.py",     # 克莱因
    ]

    # 执行每个脚本
    success_count = 0
    for script_name in scripts:
        script_path = os.path.join(script_dir, script_name)
        if os.path.exists(script_path):
            if execute_script_in_blender(script_path):
                success_count += 1
            time.sleep(1)  # 等待1秒再执行下一个
        else:
            print(f"✗ 脚本不存在: {script_path}")

    print("\n" + "=" * 60)
    print(f"完成! 成功创建 {success_count}/{len(scripts)} 个角色")
    print("=" * 60)

    # 保存场景
    print("\n保存Blender场景...")
    save_code = '''
import bpy
output_path = r"E:\\Projects\\blender-mcp\\examples\\刀剑神域\\sao_characters.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"场景已保存: {output_path}")
'''
    execute_script_in_blender_inline(save_code)

    print("\n✓ 所有任务完成!")
    print("可以在Blender中打开查看: examples/刀剑神域/sao_characters.blend")

def execute_script_in_blender_inline(code, timeout=60):
    """直接执行代码字符串"""
    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect(('127.0.0.1', 9876))
        req = {
            "id": f"inline_{int(time.time())}",
            "type": "command",
            "category": "utility",
            "action": "execute_python",
            "params": {"code": code, "timeout": timeout}
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
                if output:
                    print(output)
                return True
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False
    finally:
        try:
            s.close()
        except:
            pass

if __name__ == "__main__":
    main()
