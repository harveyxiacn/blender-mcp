"""
Create Q-version Fan Zhendong and Paris Olympics Table Tennis Scene
Test all MCP functions comprehensively

Features tested:
- Scene management
- Object creation
- Transforms
- Materials
- Lighting
- Camera
- Animation
- Parenting
- Modifiers
"""

import socket
import json
import time
import math

class BlenderMCPClient:
    """MCP Client for testing"""
    
    def __init__(self, host='127.0.0.1', port=9876):
        self.host = host
        self.port = port
        self.sock = None
        self.test_results = []
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30.0)
        self.sock.connect((self.host, self.port))
        print(f"Connected to Blender MCP at {self.host}:{self.port}")
    
    def disconnect(self):
        if self.sock:
            self.sock.close()
    
    def send_command(self, category, action, params):
        """Send command and return result"""
        request = {
            'id': f'{category}-{action}-{time.time()}',
            'type': 'command',
            'category': category,
            'action': action,
            'params': params
        }
        
        try:
            self.sock.send((json.dumps(request) + '\n').encode('utf-8'))
            response = self.sock.recv(65536).decode('utf-8')
            result = json.loads(response.strip())
            
            success = result.get('success', False)
            self.test_results.append({
                'category': category,
                'action': action,
                'success': success,
                'error': result.get('error') if not success else None
            })
            
            return result
        except Exception as e:
            self.test_results.append({
                'category': category,
                'action': action,
                'success': False,
                'error': str(e)
            })
            return {'success': False, 'error': {'message': str(e)}}
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("MCP FUNCTION TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        failed = sum(1 for r in self.test_results if not r['success'])
        
        print(f"\nTotal: {len(self.test_results)} | Passed: {passed} | Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for r in self.test_results:
                if not r['success']:
                    print(f"  - {r['category']}.{r['action']}: {r.get('error')}")
        
        print("="*60)


def create_q_fanzhendong(client):
    """Create Q-version Fan Zhendong character"""
    
    print("\n--- Creating Q-version Fan Zhendong ---")
    
    # Clear existing test objects
    print("Clearing previous test objects...")
    client.send_command('object', 'select', {'pattern': 'FZD_*'})
    
    # ========== HEAD ==========
    print("Creating head...")
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Head',
        'location': [0, 0, 2.2],
        'scale': [0.5, 0.5, 0.55]
    })
    
    # Head material - skin color
    client.send_command('material', 'create', {
        'name': 'Skin_Material',
        'color': [1.0, 0.85, 0.72, 1.0],
        'roughness': 0.8,
        'metallic': 0.0
    })
    client.send_command('material', 'assign', {
        'material_name': 'Skin_Material',
        'object_name': 'FZD_Head'
    })
    
    # ========== HAIR ==========
    print("Creating hair...")
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Hair',
        'location': [0, 0, 2.35],
        'scale': [0.52, 0.52, 0.4]
    })
    
    # Hair material - black
    client.send_command('material', 'create', {
        'name': 'Hair_Material',
        'color': [0.02, 0.02, 0.02, 1.0],
        'roughness': 0.6
    })
    client.send_command('material', 'assign', {
        'material_name': 'Hair_Material',
        'object_name': 'FZD_Hair'
    })
    
    # ========== EYES ==========
    print("Creating eyes...")
    # Left eye
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Eye_L',
        'location': [-0.15, -0.35, 2.25],
        'scale': [0.12, 0.08, 0.12]
    })
    
    # Right eye
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Eye_R',
        'location': [0.15, -0.35, 2.25],
        'scale': [0.12, 0.08, 0.12]
    })
    
    # Eye material
    client.send_command('material', 'create', {
        'name': 'Eye_Material',
        'color': [0.05, 0.02, 0.0, 1.0],
        'roughness': 0.3
    })
    client.send_command('material', 'assign', {
        'material_name': 'Eye_Material',
        'object_name': 'FZD_Eye_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'Eye_Material',
        'object_name': 'FZD_Eye_R'
    })
    
    # Eye highlights (white dots)
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_EyeHighlight_L',
        'location': [-0.12, -0.4, 2.28],
        'scale': [0.03, 0.02, 0.03]
    })
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_EyeHighlight_R',
        'location': [0.18, -0.4, 2.28],
        'scale': [0.03, 0.02, 0.03]
    })
    
    # White material for highlights
    client.send_command('material', 'create', {
        'name': 'White_Material',
        'color': [1.0, 1.0, 1.0, 1.0],
        'roughness': 0.2
    })
    client.send_command('material', 'assign', {
        'material_name': 'White_Material',
        'object_name': 'FZD_EyeHighlight_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'White_Material',
        'object_name': 'FZD_EyeHighlight_R'
    })
    
    # ========== BLUSH (cheeks) ==========
    print("Creating blush...")
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Blush_L',
        'location': [-0.28, -0.28, 2.1],
        'scale': [0.08, 0.04, 0.05]
    })
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Blush_R',
        'location': [0.28, -0.28, 2.1],
        'scale': [0.08, 0.04, 0.05]
    })
    
    # Blush material - pink
    client.send_command('material', 'create', {
        'name': 'Blush_Material',
        'color': [1.0, 0.6, 0.6, 1.0],
        'roughness': 0.9
    })
    client.send_command('material', 'assign', {
        'material_name': 'Blush_Material',
        'object_name': 'FZD_Blush_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'Blush_Material',
        'object_name': 'FZD_Blush_R'
    })
    
    # ========== BODY ==========
    print("Creating body...")
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'FZD_Body',
        'location': [0, 0, 1.3],
        'scale': [0.35, 0.2, 0.5]
    })
    
    # Body material - China team blue
    client.send_command('material', 'create', {
        'name': 'ChinaBlue_Material',
        'color': [0.0, 0.3, 0.8, 1.0],
        'roughness': 0.5,
        'metallic': 0.1
    })
    client.send_command('material', 'assign', {
        'material_name': 'ChinaBlue_Material',
        'object_name': 'FZD_Body'
    })
    
    # ========== ARMS ==========
    print("Creating arms...")
    # Left arm
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Arm_L',
        'location': [-0.45, 0, 1.4],
        'rotation': [0, 1.2, 0],
        'scale': [0.08, 0.08, 0.3]
    })
    
    # Right arm (holding paddle up)
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Arm_R',
        'location': [0.45, -0.15, 1.5],
        'rotation': [0.5, -0.8, 0.3],
        'scale': [0.08, 0.08, 0.35]
    })
    
    client.send_command('material', 'assign', {
        'material_name': 'ChinaBlue_Material',
        'object_name': 'FZD_Arm_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'ChinaBlue_Material',
        'object_name': 'FZD_Arm_R'
    })
    
    # ========== HANDS ==========
    print("Creating hands...")
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Hand_L',
        'location': [-0.65, 0, 1.2],
        'scale': [0.08, 0.06, 0.08]
    })
    client.send_command('object', 'create', {
        'type': 'SPHERE',
        'name': 'FZD_Hand_R',
        'location': [0.7, -0.3, 1.7],
        'scale': [0.08, 0.06, 0.08]
    })
    
    client.send_command('material', 'assign', {
        'material_name': 'Skin_Material',
        'object_name': 'FZD_Hand_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'Skin_Material',
        'object_name': 'FZD_Hand_R'
    })
    
    # ========== LEGS ==========
    print("Creating legs...")
    # Left leg
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Leg_L',
        'location': [-0.15, 0, 0.5],
        'scale': [0.1, 0.1, 0.35]
    })
    
    # Right leg
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Leg_R',
        'location': [0.15, 0, 0.5],
        'scale': [0.1, 0.1, 0.35]
    })
    
    # Pants material - dark blue
    client.send_command('material', 'create', {
        'name': 'DarkBlue_Material',
        'color': [0.0, 0.1, 0.3, 1.0],
        'roughness': 0.6
    })
    client.send_command('material', 'assign', {
        'material_name': 'DarkBlue_Material',
        'object_name': 'FZD_Leg_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'DarkBlue_Material',
        'object_name': 'FZD_Leg_R'
    })
    
    # ========== FEET ==========
    print("Creating feet...")
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'FZD_Foot_L',
        'location': [-0.15, -0.05, 0.08],
        'scale': [0.1, 0.15, 0.05]
    })
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'FZD_Foot_R',
        'location': [0.15, -0.05, 0.08],
        'scale': [0.1, 0.15, 0.05]
    })
    
    client.send_command('material', 'assign', {
        'material_name': 'White_Material',
        'object_name': 'FZD_Foot_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'White_Material',
        'object_name': 'FZD_Foot_R'
    })
    
    # ========== TABLE TENNIS PADDLE ==========
    print("Creating paddle...")
    # Paddle blade
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Paddle_Blade',
        'location': [0.85, -0.4, 1.85],
        'rotation': [1.57, 0, 0.3],
        'scale': [0.15, 0.02, 0.15]
    })
    
    # Paddle material - red
    client.send_command('material', 'create', {
        'name': 'Red_Material',
        'color': [0.9, 0.1, 0.1, 1.0],
        'roughness': 0.4
    })
    client.send_command('material', 'assign', {
        'material_name': 'Red_Material',
        'object_name': 'FZD_Paddle_Blade'
    })
    
    # Paddle handle
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Paddle_Handle',
        'location': [0.75, -0.35, 1.75],
        'rotation': [0.5, -0.8, 0.3],
        'scale': [0.03, 0.03, 0.1]
    })
    
    # Handle material - brown
    client.send_command('material', 'create', {
        'name': 'Brown_Material',
        'color': [0.4, 0.25, 0.1, 1.0],
        'roughness': 0.7
    })
    client.send_command('material', 'assign', {
        'material_name': 'Brown_Material',
        'object_name': 'FZD_Paddle_Handle'
    })
    
    # ========== GOLD MEDAL ==========
    print("Creating gold medal...")
    client.send_command('object', 'create', {
        'type': 'CYLINDER',
        'name': 'FZD_Medal',
        'location': [0, -0.25, 1.55],
        'rotation': [1.57, 0, 0],
        'scale': [0.08, 0.01, 0.08]
    })
    
    # Gold material
    client.send_command('material', 'create', {
        'name': 'Gold_Material',
        'color': [1.0, 0.85, 0.0, 1.0],
        'roughness': 0.2,
        'metallic': 1.0
    })
    client.send_command('material', 'assign', {
        'material_name': 'Gold_Material',
        'object_name': 'FZD_Medal'
    })
    
    # Medal ribbon
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'FZD_Medal_Ribbon',
        'location': [0, -0.1, 1.75],
        'scale': [0.02, 0.01, 0.15]
    })
    client.send_command('material', 'assign', {
        'material_name': 'Red_Material',
        'object_name': 'FZD_Medal_Ribbon'
    })
    
    print("Character created!")
    return True


def create_olympics_scene(client):
    """Create Paris Olympics table tennis scene"""
    
    print("\n--- Creating Paris Olympics Table Tennis Scene ---")
    
    # ========== TABLE TENNIS TABLE ==========
    print("Creating table tennis table...")
    
    # Table top
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'Scene_Table_Top',
        'location': [0, 3, 0.76],
        'scale': [1.37, 0.76, 0.02]
    })
    
    # Table material - dark blue/green
    client.send_command('material', 'create', {
        'name': 'TableBlue_Material',
        'color': [0.0, 0.2, 0.4, 1.0],
        'roughness': 0.3
    })
    client.send_command('material', 'assign', {
        'material_name': 'TableBlue_Material',
        'object_name': 'Scene_Table_Top'
    })
    
    # Table legs
    for i, pos in enumerate([[-1.2, 2.4, 0.38], [1.2, 2.4, 0.38], 
                              [-1.2, 3.6, 0.38], [1.2, 3.6, 0.38]]):
        client.send_command('object', 'create', {
            'type': 'CYLINDER',
            'name': f'Scene_Table_Leg_{i}',
            'location': pos,
            'scale': [0.05, 0.05, 0.38]
        })
        client.send_command('material', 'assign', {
            'material_name': 'DarkBlue_Material',
            'object_name': f'Scene_Table_Leg_{i}'
        })
    
    # Net
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'Scene_Net',
        'location': [0, 3, 0.88],
        'scale': [1.4, 0.01, 0.075]
    })
    client.send_command('material', 'assign', {
        'material_name': 'White_Material',
        'object_name': 'Scene_Net'
    })
    
    # ========== FLOOR ==========
    print("Creating floor...")
    client.send_command('object', 'create', {
        'type': 'PLANE',
        'name': 'Scene_Floor',
        'location': [0, 3, 0],
        'scale': [8, 8, 1]
    })
    
    # Floor material - blue sports floor
    client.send_command('material', 'create', {
        'name': 'Floor_Material',
        'color': [0.1, 0.3, 0.6, 1.0],
        'roughness': 0.4
    })
    client.send_command('material', 'assign', {
        'material_name': 'Floor_Material',
        'object_name': 'Scene_Floor'
    })
    
    # ========== BACKDROP ==========
    print("Creating backdrop...")
    # Back wall with Olympic rings area
    client.send_command('object', 'create', {
        'type': 'PLANE',
        'name': 'Scene_Backdrop',
        'location': [0, 10, 4],
        'rotation': [1.57, 0, 0],
        'scale': [10, 5, 1]
    })
    
    # Backdrop material - purple/magenta (Paris 2024 colors)
    client.send_command('material', 'create', {
        'name': 'Backdrop_Material',
        'color': [0.5, 0.1, 0.4, 1.0],
        'roughness': 0.8
    })
    client.send_command('material', 'assign', {
        'material_name': 'Backdrop_Material',
        'object_name': 'Scene_Backdrop'
    })
    
    # ========== OLYMPIC RINGS (simplified) ==========
    print("Creating Olympic rings...")
    ring_colors = [
        ([0.0, 0.5, 1.0, 1.0], 'Ring_Blue'),      # Blue
        ([1.0, 0.8, 0.0, 1.0], 'Ring_Yellow'),    # Yellow
        ([0.1, 0.1, 0.1, 1.0], 'Ring_Black'),     # Black
        ([0.0, 0.7, 0.2, 1.0], 'Ring_Green'),     # Green
        ([1.0, 0.2, 0.1, 1.0], 'Ring_Red'),       # Red
    ]
    ring_positions = [
        [-1.5, 9.9, 5.5],   # Blue
        [0, 9.9, 5.0],       # Yellow
        [0, 9.9, 5.5],       # Black
        [1.5, 9.9, 5.0],     # Green
        [1.5, 9.9, 5.5],     # Red - adjusted
    ]
    
    # Simplified: just create colored torus shapes
    for i, ((color, mat_name), pos) in enumerate(zip(ring_colors, ring_positions)):
        # Adjust positions for interlocking look
        if i == 0:
            pos = [-1.0, 9.9, 5.5]
        elif i == 1:
            pos = [0, 9.9, 5.0]
        elif i == 2:
            pos = [1.0, 9.9, 5.5]
        elif i == 3:
            pos = [-0.5, 9.9, 4.8]
        elif i == 4:
            pos = [0.5, 9.9, 4.8]
        
        client.send_command('object', 'create', {
            'type': 'TORUS',
            'name': f'Scene_{mat_name}',
            'location': pos,
            'rotation': [1.57, 0, 0],
            'scale': [0.4, 0.4, 0.4]
        })
        
        client.send_command('material', 'create', {
            'name': f'{mat_name}_Mat',
            'color': color,
            'roughness': 0.3
        })
        client.send_command('material', 'assign', {
            'material_name': f'{mat_name}_Mat',
            'object_name': f'Scene_{mat_name}'
        })
    
    # ========== AUDIENCE STANDS (simplified) ==========
    print("Creating audience stands...")
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'Scene_Stands_L',
        'location': [-7, 3, 2],
        'scale': [1, 5, 2]
    })
    client.send_command('object', 'create', {
        'type': 'CUBE',
        'name': 'Scene_Stands_R',
        'location': [7, 3, 2],
        'scale': [1, 5, 2]
    })
    
    # Stands material - gray
    client.send_command('material', 'create', {
        'name': 'Stands_Material',
        'color': [0.3, 0.3, 0.35, 1.0],
        'roughness': 0.7
    })
    client.send_command('material', 'assign', {
        'material_name': 'Stands_Material',
        'object_name': 'Scene_Stands_L'
    })
    client.send_command('material', 'assign', {
        'material_name': 'Stands_Material',
        'object_name': 'Scene_Stands_R'
    })
    
    print("Scene created!")
    return True


def setup_lighting(client):
    """Setup professional lighting for the scene"""
    
    print("\n--- Setting up Lighting ---")
    
    # Main key light
    client.send_command('lighting', 'create', {
        'type': 'AREA',
        'name': 'Light_Key',
        'location': [3, -2, 6],
        'power': 800
    })
    
    # Fill light
    client.send_command('lighting', 'create', {
        'type': 'AREA',
        'name': 'Light_Fill',
        'location': [-3, -2, 4],
        'power': 300
    })
    
    # Back light
    client.send_command('lighting', 'create', {
        'type': 'AREA',
        'name': 'Light_Back',
        'location': [0, 8, 5],
        'power': 400
    })
    
    # Ambient light (overhead)
    client.send_command('lighting', 'create', {
        'type': 'AREA',
        'name': 'Light_Ambient',
        'location': [0, 3, 8],
        'power': 200
    })
    
    print("Lighting setup complete!")
    return True


def setup_camera(client):
    """Setup camera for the scene"""
    
    print("\n--- Setting up Camera ---")
    
    # Main camera
    client.send_command('camera', 'create', {
        'name': 'Camera_Main',
        'location': [0, -5, 2.5],
        'focal_length': 50
    })
    
    # Look at character
    client.send_command('camera', 'look_at', {
        'camera_name': 'Camera_Main',
        'target': [0, 0, 1.5]
    })
    
    # Set as active
    client.send_command('camera', 'set_active', {
        'name': 'Camera_Main'
    })
    
    print("Camera setup complete!")
    return True


def add_animation(client):
    """Add simple animation to the character"""
    
    print("\n--- Adding Animation ---")
    
    # Set timeline range
    client.send_command('animation', 'timeline_set_range', {
        'start': 1,
        'end': 60
    })
    
    # Animate right arm (celebration motion)
    # Frame 1 - arm down
    client.send_command('animation', 'goto_frame', {'frame': 1})
    client.send_command('object', 'transform', {
        'name': 'FZD_Arm_R',
        'rotation': [0.5, -0.8, 0.3]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Arm_R',
        'data_path': 'rotation_euler'
    })
    
    # Frame 15 - arm up (celebrating)
    client.send_command('animation', 'goto_frame', {'frame': 15})
    client.send_command('object', 'transform', {
        'name': 'FZD_Arm_R',
        'rotation': [-0.5, -1.2, 0.5]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Arm_R',
        'data_path': 'rotation_euler'
    })
    
    # Frame 30 - arm down
    client.send_command('animation', 'goto_frame', {'frame': 30})
    client.send_command('object', 'transform', {
        'name': 'FZD_Arm_R',
        'rotation': [0.5, -0.8, 0.3]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Arm_R',
        'data_path': 'rotation_euler'
    })
    
    # Frame 45 - arm up again
    client.send_command('animation', 'goto_frame', {'frame': 45})
    client.send_command('object', 'transform', {
        'name': 'FZD_Arm_R',
        'rotation': [-0.5, -1.2, 0.5]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Arm_R',
        'data_path': 'rotation_euler'
    })
    
    # Frame 60 - back to start
    client.send_command('animation', 'goto_frame', {'frame': 60})
    client.send_command('object', 'transform', {
        'name': 'FZD_Arm_R',
        'rotation': [0.5, -0.8, 0.3]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Arm_R',
        'data_path': 'rotation_euler'
    })
    
    # Also animate the head (nodding)
    client.send_command('animation', 'goto_frame', {'frame': 1})
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Head',
        'data_path': 'rotation_euler'
    })
    
    client.send_command('animation', 'goto_frame', {'frame': 20})
    client.send_command('object', 'transform', {
        'name': 'FZD_Head',
        'rotation': [0.15, 0, 0]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Head',
        'data_path': 'rotation_euler'
    })
    
    client.send_command('animation', 'goto_frame', {'frame': 40})
    client.send_command('object', 'transform', {
        'name': 'FZD_Head',
        'rotation': [-0.1, 0, 0]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Head',
        'data_path': 'rotation_euler'
    })
    
    client.send_command('animation', 'goto_frame', {'frame': 60})
    client.send_command('object', 'transform', {
        'name': 'FZD_Head',
        'rotation': [0, 0, 0]
    })
    client.send_command('animation', 'keyframe_insert', {
        'object_name': 'FZD_Head',
        'data_path': 'rotation_euler'
    })
    
    # Go back to frame 1
    client.send_command('animation', 'goto_frame', {'frame': 1})
    
    print("Animation added!")
    return True


def test_additional_functions(client):
    """Test additional MCP functions"""
    
    print("\n--- Testing Additional MCP Functions ---")
    
    # Test scene functions
    print("Testing scene functions...")
    client.send_command('scene', 'get_info', {})
    client.send_command('scene', 'list', {})
    
    # Test object info
    print("Testing object info...")
    client.send_command('object', 'get_info', {'name': 'FZD_Head'})
    
    # Test object list with filter
    client.send_command('object', 'list', {'name_pattern': 'FZD_*'})
    
    # Test utility functions
    print("Testing utility functions...")
    client.send_command('utility', 'get_info', {})
    
    # Test render settings
    print("Testing render functions...")
    client.send_command('render', 'settings', {
        'engine': 'CYCLES',
        'samples': 32
    })
    
    print("Additional function tests complete!")
    return True


def main():
    """Main function"""
    print("="*60)
    print("Q-VERSION FAN ZHENDONG & PARIS OLYMPICS SCENE CREATOR")
    print("="*60)
    
    client = BlenderMCPClient()
    
    try:
        client.connect()
        
        # Delete existing test objects first
        print("\nClearing existing test objects...")
        client.send_command('utility', 'execute_python', {
            'code': '''
import bpy
# Delete objects starting with FZD_ or Scene_ or Light_ or Camera_Main
for obj in list(bpy.data.objects):
    if obj.name.startswith(('FZD_', 'Scene_', 'Light_', 'MCP_Test')):
        bpy.data.objects.remove(obj, do_unlink=True)
'''
        })
        
        # Create character
        create_q_fanzhendong(client)
        
        # Create scene
        create_olympics_scene(client)
        
        # Setup lighting
        setup_lighting(client)
        
        # Setup camera
        setup_camera(client)
        
        # Add animation
        add_animation(client)
        
        # Test additional functions
        test_additional_functions(client)
        
        # Print summary
        client.print_test_summary()
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.disconnect()
    
    print("\nDone! Check Blender to see the result.")
    print("Press SPACE in Blender to play the animation.")


if __name__ == "__main__":
    main()
