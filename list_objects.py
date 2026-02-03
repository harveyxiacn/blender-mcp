import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10.0)
sock.connect(('127.0.0.1', 9876))

request = {
    'id': 'list-1',
    'type': 'command',
    'category': 'object',
    'action': 'list',
    'params': {'limit': 100}
}

sock.send((json.dumps(request) + '\n').encode('utf-8'))

# Read response in chunks
response = ""
while True:
    chunk = sock.recv(65536).decode('utf-8')
    response += chunk
    if '\n' in response:
        break

result = json.loads(response.strip())

print('Objects in scene:')
for obj in result.get('data', {}).get('objects', []):
    print(f"  {obj['name']} ({obj['type']})")

print(f"\nTotal objects: {result.get('data', {}).get('total', 0)}")
sock.close()
