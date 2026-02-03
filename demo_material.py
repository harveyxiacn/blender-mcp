"""Demo: Add red material to the test sphere"""
import socket
import json

def send_command(sock, category, action, params):
    request = {
        'id': f'{category}-{action}',
        'type': 'command',
        'category': category,
        'action': action,
        'params': params
    }
    sock.send((json.dumps(request) + '\n').encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    return json.loads(response.strip())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10.0)
sock.connect(('127.0.0.1', 9876))

print('1. Creating red material...')
result = send_command(sock, 'material', 'create', {
    'name': 'Red_Metal',
    'color': [1.0, 0.1, 0.1, 1.0],
    'metallic': 0.8,
    'roughness': 0.2
})
print(f"   Result: {result.get('success')}")

print('2. Assigning material to sphere...')
result = send_command(sock, 'material', 'assign', {
    'material_name': 'Red_Metal',
    'object_name': 'MCP_Test_Sphere'
})
print(f"   Result: {result.get('success')}")

print('3. Creating a light for better view...')
result = send_command(sock, 'lighting', 'create', {
    'type': 'AREA',
    'name': 'MCP_Test_Light',
    'location': [3, -3, 5],
    'power': 500
})
print(f"   Result: {result.get('success')}")

sock.close()
print('\nDone! Check Blender to see the red metallic sphere.')
