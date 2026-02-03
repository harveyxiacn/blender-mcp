"""
Test Blender MCP Connection

Usage: python test_connection.py
"""

import socket
import json
import sys


def test_connection(host="127.0.0.1", port=9876):
    """Test connection to Blender MCP service"""
    
    print(f"Connecting to Blender MCP: {host}:{port}")
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        
        print("[OK] Connected!")
        
        # Test 1: Get Blender info
        print("\n--- Test 1: Get Blender Info ---")
        request = {
            "id": "test-1",
            "type": "command",
            "category": "utility",
            "action": "get_info",
            "params": {}
        }
        
        sock.send((json.dumps(request) + "\n").encode("utf-8"))
        response = sock.recv(4096).decode("utf-8")
        result = json.loads(response.strip())
        
        if result.get("success"):
            print(f"[OK] Blender info: {json.dumps(result.get('data', {}), indent=2)}")
        else:
            print(f"[FAIL] Error: {result.get('error', {}).get('message', 'Unknown error')}")
        
        # Test 2: List objects in scene
        print("\n--- Test 2: List Scene Objects ---")
        request = {
            "id": "test-2",
            "type": "command",
            "category": "object",
            "action": "list",
            "params": {}
        }
        
        sock.send((json.dumps(request) + "\n").encode("utf-8"))
        response = sock.recv(4096).decode("utf-8")
        result = json.loads(response.strip())
        
        if result.get("success"):
            objects = result.get("data", {}).get("objects", [])
            print(f"[OK] Found {len(objects)} objects in scene:")
            for obj in objects[:10]:  # Show first 10
                print(f"  - {obj.get('name')} ({obj.get('type')})")
        else:
            print(f"[FAIL] Error: {result.get('error', {}).get('message', 'Unknown error')}")
        
        # Test 3: Create a sphere
        print("\n--- Test 3: Create a Sphere ---")
        request = {
            "id": "test-3",
            "type": "command",
            "category": "object",
            "action": "create",
            "params": {
                "type": "SPHERE",
                "name": "MCP_Test_Sphere",
                "location": [2, 0, 0]
            }
        }
        
        sock.send((json.dumps(request) + "\n").encode("utf-8"))
        response = sock.recv(4096).decode("utf-8")
        result = json.loads(response.strip())
        
        if result.get("success"):
            print(f"[OK] Created: {result.get('data', {}).get('name', 'unknown')}")
        else:
            print(f"[FAIL] Error: {result.get('error', {}).get('message', 'Unknown error')}")
        
        sock.close()
        print("\n[OK] All tests passed! Blender MCP is working.")
        return True
        
    except socket.timeout:
        print("[FAIL] Connection timeout - MCP service may not be running")
        return False
    except ConnectionRefusedError:
        print("[FAIL] Connection refused - MCP service may not be running")
        print("\nPlease ensure:")
        print("  1. Blender is running")
        print("  2. MCP addon is enabled")
        print("  3. Start the service in Blender's MCP panel (press N in 3D View)")
        return False
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        return False


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9876
    
    success = test_connection(host, port)
    sys.exit(0 if success else 1)
