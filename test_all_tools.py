"""
Comprehensive test for all Blender MCP tools
Tests all new implemented features
"""

import socket
import json
import time


class MCPTester:
    def __init__(self, host='127.0.0.1', port=9876):
        self.host = host
        self.port = port
        self.sock = None
        self.results = []
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30.0)
        self.sock.connect((self.host, self.port))
        print(f"Connected to Blender MCP at {self.host}:{self.port}")
    
    def disconnect(self):
        if self.sock:
            self.sock.close()
    
    def cmd(self, category, action, params=None):
        """Send command and return result"""
        request = {
            'id': f'{category}-{action}-{time.time()}',
            'type': 'command',
            'category': category,
            'action': action,
            'params': params or {}
        }
        
        try:
            self.sock.send((json.dumps(request) + '\n').encode('utf-8'))
            response = self.sock.recv(65536).decode('utf-8')
            result = json.loads(response.strip())
            
            success = result.get('success', False)
            self.results.append({
                'test': f'{category}.{action}',
                'success': success,
                'error': result.get('error', {}).get('message') if not success else None
            })
            
            return success, result
        except Exception as e:
            self.results.append({
                'test': f'{category}.{action}',
                'success': False,
                'error': str(e)
            })
            return False, {'error': str(e)}
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r['success'])
        failed = sum(1 for r in self.results if not r['success'])
        
        print(f"\nTotal: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['error']}")
        
        print("="*60)
        return passed, failed


def clear_scene(tester):
    """Clear test objects"""
    print("\n--- Clearing scene ---")
    tester.cmd('utility', 'execute_python', {
        'code': '''
import bpy
for obj in list(bpy.data.objects):
    if obj.name not in ['Camera', 'Light']:
        bpy.data.objects.remove(obj, do_unlink=True)
'''
    })


def test_character_templates(tester):
    """Test character template tools"""
    print("\n--- Testing Character Templates ---")
    
    # Create chibi character
    tester.cmd('character_template', 'create', {
        'template': 'chibi',
        'name': 'TestChar',
        'height': 1.5,
        'location': [0, 0, 0]
    })
    
    # Add hair
    tester.cmd('character_template', 'hair_create', {
        'character_name': 'TestChar',
        'hair_style': 'short',
        'color': [0.05, 0.03, 0.02, 1.0]
    })
    
    # Add clothing
    tester.cmd('character_template', 'clothing_add', {
        'character_name': 'TestChar',
        'clothing_type': 'sportswear',
        'color': [0.0, 0.3, 0.8, 1.0]
    })
    
    # Add accessory (medal)
    tester.cmd('character_template', 'accessory_add', {
        'character_name': 'TestChar',
        'accessory_type': 'medal'
    })
    
    # Set expression
    tester.cmd('character_template', 'face_expression', {
        'character_name': 'TestChar',
        'expression': 'happy',
        'intensity': 0.8
    })


def test_auto_rig(tester):
    """Test auto rigging tools"""
    print("\n--- Testing Auto Rig ---")
    
    # Auto setup rig
    tester.cmd('auto_rig', 'setup', {
        'character_name': 'TestChar',
        'rig_type': 'simple',
        'auto_weight': False
    })


def test_animation_presets(tester):
    """Test animation preset tools"""
    print("\n--- Testing Animation Presets ---")
    
    # Create action
    tester.cmd('animation_preset', 'action_create', {
        'action_name': 'TestAction',
        'frame_start': 1,
        'frame_end': 60
    })


def test_physics(tester):
    """Test physics tools"""
    print("\n--- Testing Physics ---")
    
    # Create test object
    tester.cmd('object', 'create', {
        'type': 'SPHERE',
        'name': 'PhysicsSphere',
        'location': [3, 0, 3]
    })
    
    # Add rigid body
    tester.cmd('physics', 'rigid_body_add', {
        'object_name': 'PhysicsSphere',
        'body_type': 'ACTIVE',
        'shape': 'SPHERE',
        'mass': 1.0
    })
    
    # Create ground for collision
    tester.cmd('object', 'create', {
        'type': 'PLANE',
        'name': 'PhysicsGround',
        'location': [3, 0, 0],
        'scale': [5, 5, 1]
    })
    
    # Add passive rigid body
    tester.cmd('physics', 'rigid_body_add', {
        'object_name': 'PhysicsGround',
        'body_type': 'PASSIVE',
        'shape': 'BOX'
    })
    
    # Add force field
    tester.cmd('physics', 'force_field_add', {
        'force_type': 'WIND',
        'location': [3, -3, 1],
        'strength': 5.0
    })


def test_scene_advanced(tester):
    """Test scene advanced tools"""
    print("\n--- Testing Scene Advanced ---")
    
    # Environment preset
    tester.cmd('scene_advanced', 'environment_preset', {
        'preset': 'stadium',
        'intensity': 0.8
    })
    
    # Ground plane
    tester.cmd('scene_advanced', 'ground_plane', {
        'size': 20.0,
        'material_preset': 'wood',
        'location': [0, 0, 0]
    })


def test_batch(tester):
    """Test batch tools"""
    print("\n--- Testing Batch Tools ---")
    
    # Create multiple test objects
    for i in range(3):
        tester.cmd('object', 'create', {
            'type': 'CUBE',
            'name': f'BatchTest_{i}',
            'location': [-3 + i, 5, 0.5]
        })
    
    # Batch transform
    tester.cmd('batch', 'transform', {
        'pattern': 'BatchTest_*',
        'scale_factor': [0.5, 0.5, 0.5]
    })
    
    # Batch rename
    tester.cmd('batch', 'rename', {
        'pattern': 'BatchTest_*',
        'new_name': 'Cube',
        'numbering': True
    })


def test_curves(tester):
    """Test curve tools"""
    print("\n--- Testing Curves ---")
    
    # Create bezier curve
    tester.cmd('curves', 'create', {
        'curve_type': 'BEZIER',
        'name': 'TestCurve',
        'points': [[0, -3, 0], [1, -3, 1], [2, -3, 0], [3, -3, 1]],
        'location': [0, 0, 0]
    })
    
    # Create spiral
    tester.cmd('curves', 'spiral', {
        'name': 'TestSpiral',
        'turns': 3,
        'radius': 0.5,
        'height': 2,
        'location': [-3, -3, 0]
    })
    
    # Create text
    tester.cmd('curves', 'text', {
        'text': 'MCP',
        'name': 'TestText',
        'font_size': 0.5,
        'extrude': 0.1,
        'location': [0, -5, 0]
    })


def test_export(tester):
    """Test export tools"""
    print("\n--- Testing Export ---")
    
    # We'll just test that the commands work
    # Not actually exporting to avoid file system issues
    # tester.cmd('export', 'fbx', {'filepath': 'test.fbx', 'selected_only': True})


def main():
    print("="*60)
    print("BLENDER MCP COMPREHENSIVE TEST")
    print("="*60)
    
    tester = MCPTester()
    
    try:
        tester.connect()
        
        # Clear scene first
        clear_scene(tester)
        
        # Run all tests
        test_character_templates(tester)
        test_auto_rig(tester)
        test_animation_presets(tester)
        test_physics(tester)
        test_scene_advanced(tester)
        test_batch(tester)
        test_curves(tester)
        
        # Print summary
        passed, failed = tester.print_summary()
        
        print(f"\nTest completed! Check Blender to see the results.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.disconnect()


if __name__ == "__main__":
    main()
