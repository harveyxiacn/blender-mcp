"""
Comprehensive test for ALL Blender MCP tools
Tests every implemented tool module
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
        self.category_stats = {}
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30.0)
        self.sock.connect((self.host, self.port))
        print(f"[OK] Connected to Blender MCP at {self.host}:{self.port}")
    
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
        
        test_name = f'{category}.{action}'
        
        try:
            self.sock.send((json.dumps(request) + '\n').encode('utf-8'))
            
            # Read response
            data = b''
            while b'\n' not in data:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                data += chunk
            
            response = data.decode('utf-8').strip()
            result = json.loads(response)
            
            success = result.get('success', False)
            error_msg = result.get('error', {}).get('message') if not success else None
            
            self.results.append({
                'test': test_name,
                'success': success,
                'error': error_msg
            })
            
            # Update category stats
            if category not in self.category_stats:
                self.category_stats[category] = {'passed': 0, 'failed': 0}
            
            if success:
                self.category_stats[category]['passed'] += 1
                print(f"  [OK] {test_name}")
            else:
                self.category_stats[category]['failed'] += 1
                print(f"  [FAIL] {test_name}: {error_msg}")
            
            return success, result
        except Exception as e:
            self.results.append({
                'test': test_name,
                'success': False,
                'error': str(e)
            })
            if category not in self.category_stats:
                self.category_stats[category] = {'passed': 0, 'failed': 0}
            self.category_stats[category]['failed'] += 1
            print(f"  [FAIL] {test_name}: {e}")
            return False, {'error': str(e)}
    
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY BY CATEGORY")
        print("="*70)
        
        total_passed = 0
        total_failed = 0
        
        for category, stats in sorted(self.category_stats.items()):
            passed = stats['passed']
            failed = stats['failed']
            total = passed + failed
            total_passed += passed
            total_failed += failed
            status = "[OK]" if failed == 0 else "[FAIL]"
            print(f"  {status} {category}: {passed}/{total} passed")
        
        print("-"*70)
        print(f"TOTAL: {total_passed}/{total_passed + total_failed} tests passed")
        
        if total_failed > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['error']}")
        
        print("="*70)
        return total_passed, total_failed


def clear_scene(tester):
    """Clear scene for testing"""
    print("\n[SETUP] Clearing scene...")
    tester.cmd('utility', 'execute_python', {
        'code': '''
import bpy
# Delete all objects except camera and light
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
# Clear orphan data
bpy.ops.outliner.orphans_purge(do_recursive=True)
'''
    })


def test_scene_tools(tester):
    """Test scene management tools"""
    print("\n--- Testing SCENE tools ---")
    tester.cmd('scene', 'get_info', {})
    tester.cmd('scene', 'set_frame_range', {'start': 1, 'end': 250})


def test_object_tools(tester):
    """Test object tools"""
    print("\n--- Testing OBJECT tools ---")
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'TestCube', 'location': [0, 0, 0]})
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'TestSphere', 'location': [3, 0, 0]})
    tester.cmd('object', 'create', {'type': 'CYLINDER', 'name': 'TestCylinder', 'location': [-3, 0, 0]})
    tester.cmd('object', 'transform', {'name': 'TestCube', 'location': [0, 0, 1]})
    tester.cmd('object', 'list', {'limit': 10})
    tester.cmd('object', 'duplicate', {'name': 'TestCube', 'new_name': 'TestCubeCopy'})


def test_material_tools(tester):
    """Test material tools"""
    print("\n--- Testing MATERIAL tools ---")
    tester.cmd('material', 'create', {'name': 'TestMaterial', 'color': [1, 0, 0, 1]})
    tester.cmd('material', 'assign', {'material_name': 'TestMaterial', 'object_name': 'TestCube'})
    tester.cmd('material', 'list', {})


def test_lighting_tools(tester):
    """Test lighting tools"""
    print("\n--- Testing LIGHTING tools ---")
    tester.cmd('lighting', 'create', {'type': 'POINT', 'name': 'TestLight', 'location': [5, 5, 5]})
    tester.cmd('lighting', 'create', {'type': 'SUN', 'name': 'TestSun', 'location': [0, 0, 10]})
    tester.cmd('lighting', 'set_energy', {'name': 'TestLight', 'energy': 100})


def test_camera_tools(tester):
    """Test camera tools"""
    print("\n--- Testing CAMERA tools ---")
    tester.cmd('camera', 'create', {'name': 'TestCamera', 'location': [7, -7, 5]})
    tester.cmd('camera', 'look_at', {'camera_name': 'TestCamera', 'target': [0, 0, 0]})
    tester.cmd('camera', 'set_active', {'name': 'TestCamera'})


def test_animation_tools(tester):
    """Test animation tools"""
    print("\n--- Testing ANIMATION tools ---")
    tester.cmd('animation', 'keyframe_insert', {
        'object_name': 'TestCube',
        'data_path': 'location',
        'frame': 1
    })
    tester.cmd('animation', 'goto_frame', {'frame': 50})
    tester.cmd('object', 'transform', {'name': 'TestCube', 'location': [0, 5, 1]})
    tester.cmd('animation', 'keyframe_insert', {
        'object_name': 'TestCube',
        'data_path': 'location',
        'frame': 50
    })
    tester.cmd('animation', 'timeline_set_range', {'start': 1, 'end': 100})


def test_character_template_tools(tester):
    """Test character template tools"""
    print("\n--- Testing CHARACTER_TEMPLATE tools ---")
    tester.cmd('character_template', 'create', {
        'template': 'chibi',
        'name': 'TestChar',
        'height': 1.5,
        'location': [10, 0, 0]
    })
    tester.cmd('character_template', 'hair_create', {
        'character_name': 'TestChar',
        'hair_style': 'short',
        'color': [0.1, 0.05, 0.02, 1.0]
    })
    tester.cmd('character_template', 'clothing_add', {
        'character_name': 'TestChar',
        'clothing_type': 'sportswear',
        'color': [0.2, 0.4, 0.8, 1.0]
    })
    tester.cmd('character_template', 'accessory_add', {
        'character_name': 'TestChar',
        'accessory_type': 'medal'
    })
    tester.cmd('character_template', 'face_expression', {
        'character_name': 'TestChar',
        'expression': 'happy',
        'intensity': 0.8
    })


def test_auto_rig_tools(tester):
    """Test auto rig tools"""
    print("\n--- Testing AUTO_RIG tools ---")
    tester.cmd('auto_rig', 'setup', {
        'character_name': 'TestChar',
        'rig_type': 'simple',
        'auto_weight': False
    })


def test_animation_preset_tools(tester):
    """Test animation preset tools"""
    print("\n--- Testing ANIMATION_PRESET tools ---")
    tester.cmd('animation_preset', 'action_create', {
        'action_name': 'TestAction',
        'frame_start': 1,
        'frame_end': 60
    })


def test_physics_tools(tester):
    """Test physics tools"""
    print("\n--- Testing PHYSICS tools ---")
    # Create objects for physics
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'PhysBall', 'location': [-10, 0, 5]})
    tester.cmd('object', 'create', {'type': 'PLANE', 'name': 'PhysGround', 'location': [-10, 0, 0], 'scale': [5, 5, 1]})
    
    tester.cmd('physics', 'rigid_body_add', {
        'object_name': 'PhysBall',
        'body_type': 'ACTIVE',
        'mass': 1.0
    })
    tester.cmd('physics', 'rigid_body_add', {
        'object_name': 'PhysGround',
        'body_type': 'PASSIVE'
    })
    tester.cmd('physics', 'force_field_add', {
        'force_type': 'WIND',
        'location': [-10, -5, 2],
        'strength': 5.0
    })


def test_scene_advanced_tools(tester):
    """Test scene advanced tools"""
    print("\n--- Testing SCENE_ADVANCED tools ---")
    tester.cmd('scene_advanced', 'environment_preset', {
        'preset': 'studio',
        'intensity': 0.8
    })
    tester.cmd('scene_advanced', 'ground_plane', {
        'size': 20.0,
        'material_preset': 'concrete',
        'location': [0, 0, -0.5]
    })


def test_batch_tools(tester):
    """Test batch tools"""
    print("\n--- Testing BATCH tools ---")
    # Create test objects
    for i in range(3):
        tester.cmd('object', 'create', {'type': 'CUBE', 'name': f'BatchObj_{i}', 'location': [20 + i*2, 0, 0]})
    
    tester.cmd('batch', 'transform', {
        'pattern': 'BatchObj_*',
        'scale_factor': [0.5, 0.5, 0.5]
    })
    tester.cmd('batch', 'rename', {
        'pattern': 'BatchObj_*',
        'new_name': 'RenamedObj',
        'numbering': True
    })


def test_curves_tools(tester):
    """Test curves tools"""
    print("\n--- Testing CURVES tools ---")
    tester.cmd('curves', 'create', {
        'curve_type': 'BEZIER',
        'name': 'TestCurve',
        'points': [[0, -10, 0], [2, -10, 2], [4, -10, 0], [6, -10, 2]],
        'location': [0, 0, 0]
    })
    tester.cmd('curves', 'spiral', {
        'name': 'TestSpiral',
        'turns': 3,
        'radius': 0.5,
        'height': 2,
        'location': [-5, -10, 0]
    })
    tester.cmd('curves', 'text', {
        'text': 'MCP',
        'name': 'TestText',
        'font_size': 1.0,
        'extrude': 0.1,
        'location': [0, -15, 0]
    })
    tester.cmd('curves', 'circle', {
        'name': 'TestCircle',
        'radius': 1.0,
        'location': [5, -10, 0]
    })


def test_uv_tools(tester):
    """Test UV mapping tools"""
    print("\n--- Testing UV tools ---")
    tester.cmd('uv', 'smart_project', {
        'object_name': 'TestCube',
        'angle_limit': 66.0,
        'island_margin': 0.02
    })
    tester.cmd('uv', 'unwrap', {
        'object_name': 'TestSphere',
        'method': 'ANGLE_BASED'
    })


def test_nodes_tools(tester):
    """Test node system tools"""
    print("\n--- Testing NODES tools ---")
    tester.cmd('nodes', 'shader_preset', {
        'material_name': 'GlassMaterial',
        'preset': 'glass',
        'color': [0.8, 0.9, 1.0, 1.0]
    })
    tester.cmd('nodes', 'shader_preset', {
        'material_name': 'MetalMaterial',
        'preset': 'metal',
        'color': [0.9, 0.8, 0.2, 1.0]
    })
    tester.cmd('nodes', 'geonodes_add', {
        'object_name': 'TestCylinder',
        'modifier_name': 'TestGeoNodes'
    })


def test_compositor_tools(tester):
    """Test compositor tools"""
    print("\n--- Testing COMPOSITOR tools ---")
    tester.cmd('compositor', 'enable', {'enable': True})
    tester.cmd('compositor', 'preset', {
        'preset': 'color_correction',
        'intensity': 1.0
    })
    tester.cmd('compositor', 'render_layer', {
        'layer_name': 'ViewLayer',
        'use_pass_z': True
    })


def test_vse_tools(tester):
    """Test video sequence editor tools"""
    print("\n--- Testing VSE tools ---")
    tester.cmd('vse', 'add_text', {
        'text': 'Hello MCP!',
        'channel': 1,
        'start_frame': 1,
        'duration': 50,
        'font_size': 80
    })


def test_sculpt_tools(tester):
    """Test sculpting tools"""
    print("\n--- Testing SCULPT tools ---")
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'SculptSphere', 'location': [25, 0, 0]})
    tester.cmd('sculpt', 'mode', {'object_name': 'SculptSphere', 'enable': True})
    tester.cmd('sculpt', 'set_brush', {'brush_type': 'DRAW', 'radius': 50, 'strength': 0.5})
    tester.cmd('sculpt', 'symmetry', {'use_x': True, 'use_y': False, 'use_z': False})
    tester.cmd('sculpt', 'mode', {'object_name': 'SculptSphere', 'enable': False})


def test_texture_paint_tools(tester):
    """Test texture painting tools"""
    print("\n--- Testing TEXTURE_PAINT tools ---")
    tester.cmd('texture_paint', 'create', {
        'name': 'TestTexture',
        'width': 512,
        'height': 512,
        'color': [0.5, 0.5, 0.5, 1.0]
    })
    tester.cmd('texture_paint', 'set_brush', {
        'brush_type': 'DRAW',
        'color': [1.0, 0.0, 0.0],
        'radius': 30
    })


def test_gpencil_tools(tester):
    """Test grease pencil tools"""
    print("\n--- Testing GPENCIL tools ---")
    # 创建油笔并获取实际名称
    success, result = tester.cmd('gpencil', 'create', {'name': 'TestGPencil', 'location': [30, 0, 0]})
    gpencil_name = result.get('data', {}).get('object_name', 'TestGPencil') if success else 'TestGPencil'
    
    tester.cmd('gpencil', 'layer', {'gpencil_name': gpencil_name, 'action': 'ADD', 'layer_name': 'TestLayer'})
    tester.cmd('gpencil', 'material', {
        'gpencil_name': gpencil_name,
        'name': 'GPMat',
        'stroke_color': [0, 0, 1, 1]
    })
    tester.cmd('gpencil', 'draw', {
        'gpencil_name': gpencil_name,
        'layer_name': 'GP_Layer',  # Blender 5.0 默认图层名
        'points': [[30, 0, 0], [31, 1, 0], [32, 0, 0]],
        'line_width': 10
    })


def test_simulation_tools(tester):
    """Test simulation tools (fluid, smoke, ocean)"""
    print("\n--- Testing SIMULATION tools ---")
    # 创建域对象
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'SimDomain', 'location': [35, 0, 2], 'scale': [2, 2, 2]})
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'SimFlow', 'location': [35, 0, 3], 'scale': [0.3, 0.3, 0.3]})
    tester.cmd('object', 'create', {'type': 'PLANE', 'name': 'OceanPlane', 'location': [40, 0, 0], 'scale': [3, 3, 1]})
    
    tester.cmd('simulation', 'fluid_domain', {
        'object_name': 'SimDomain',
        'domain_type': 'LIQUID',
        'resolution': 32
    })
    tester.cmd('simulation', 'fluid_flow', {
        'object_name': 'SimFlow',
        'flow_type': 'INFLOW'
    })
    tester.cmd('simulation', 'ocean', {
        'object_name': 'OceanPlane',
        'resolution': 5,
        'spatial_size': 20
    })


def test_hair_tools(tester):
    """Test hair/fur tools"""
    print("\n--- Testing HAIR tools ---")
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'HairSphere', 'location': [45, 0, 0]})
    
    tester.cmd('hair', 'add', {
        'object_name': 'HairSphere',
        'name': 'TestHair',
        'hair_length': 0.2,
        'hair_count': 500
    })
    tester.cmd('hair', 'settings', {
        'object_name': 'HairSphere',
        'hair_length': 0.3
    })
    tester.cmd('hair', 'children', {
        'object_name': 'HairSphere',
        'child_type': 'INTERPOLATED',
        'child_count': 5
    })
    tester.cmd('hair', 'material', {
        'object_name': 'HairSphere',
        'color': [0.2, 0.1, 0.05, 1.0]
    })


def test_assets_tools(tester):
    """Test asset management tools"""
    print("\n--- Testing ASSETS tools ---")
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'AssetCube', 'location': [50, 0, 0]})
    
    tester.cmd('assets', 'mark', {
        'object_name': 'AssetCube',
        'description': 'Test asset',
        'tags': ['test']
    })
    tester.cmd('assets', 'catalog', {'action': 'LIST'})
    tester.cmd('assets', 'search', {'query': 'asset'})
    tester.cmd('assets', 'preview', {'object_name': 'AssetCube'})
    tester.cmd('assets', 'clear', {'object_name': 'AssetCube'})


def test_addons_tools(tester):
    """Test addon management tools"""
    print("\n--- Testing ADDONS tools ---")
    tester.cmd('addons', 'list', {})
    tester.cmd('addons', 'info', {'addon_name': 'blender_mcp_addon'})


def test_world_tools(tester):
    """Test world/environment tools"""
    print("\n--- Testing WORLD tools ---")
    tester.cmd('world', 'create', {'name': 'TestWorld', 'use_nodes': True})
    tester.cmd('world', 'background', {'color': [0.1, 0.2, 0.4], 'strength': 1.0})
    tester.cmd('world', 'sky', {'sky_type': 'NISHITA', 'sun_elevation': 0.5})
    tester.cmd('world', 'fog', {'use_fog': True, 'density': 0.005})
    tester.cmd('world', 'ambient_occlusion', {'use_ao': True, 'distance': 1.0})


def test_constraints_tools(tester):
    """Test constraint tools"""
    print("\n--- Testing CONSTRAINTS tools ---")
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'ConstraintCube', 'location': [55, 0, 0]})
    tester.cmd('object', 'create', {'type': 'EMPTY', 'name': 'ConstraintTarget', 'location': [55, 2, 0]})
    
    tester.cmd('constraints', 'copy_location', {
        'object_name': 'ConstraintCube',
        'target': 'ConstraintTarget',
        'influence': 0.5
    })
    tester.cmd('constraints', 'copy_rotation', {
        'object_name': 'ConstraintCube',
        'target': 'ConstraintTarget'
    })
    tester.cmd('constraints', 'track_to', {
        'object_name': 'ConstraintCube',
        'target': 'ConstraintTarget'
    })
    tester.cmd('constraints', 'limit', {
        'object_name': 'ConstraintCube',
        'limit_type': 'LOCATION',
        'min_x': -5,
        'max_x': 5
    })
    tester.cmd('constraints', 'list', {'object_name': 'ConstraintCube'})


def test_preferences_tools(tester):
    """Test preferences tools"""
    print("\n--- Testing PREFERENCES tools ---")
    tester.cmd('preferences', 'get', {'category': 'view', 'key': 'show_splash'})
    tester.cmd('preferences', 'viewport', {'show_floor': True, 'show_axis_z': True})
    tester.cmd('preferences', 'system', {'undo_steps': 64})


def test_external_tools(tester):
    """Test external integration tools"""
    print("\n--- Testing EXTERNAL tools ---")
    # 创建测试对象
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'ExportCube', 'location': [60, 0, 0]})
    
    # 测试批量导出（使用临时目录）
    import tempfile
    import os
    temp_dir = tempfile.mkdtemp()
    
    tester.cmd('external', 'batch_export', {
        'output_dir': temp_dir,
        'format': 'FBX',
        'separate_files': True,
        'objects': ['ExportCube']
    })


def test_ai_assist_tools(tester):
    """Test AI assist tools"""
    print("\n--- Testing AI_ASSIST tools ---")
    tester.cmd('ai_assist', 'describe_scene', {'detail_level': 'medium'})
    tester.cmd('ai_assist', 'scene_statistics', {'include_hidden': False})
    tester.cmd('ai_assist', 'list_issues', {})
    
    # 创建测试对象并分析
    tester.cmd('object', 'create', {'type': 'SPHERE', 'name': 'AnalyzeSphere', 'location': [65, 0, 0]})
    tester.cmd('ai_assist', 'analyze_object', {'object_name': 'AnalyzeSphere'})
    tester.cmd('ai_assist', 'auto_material', {
        'object_name': 'AnalyzeSphere',
        'description': 'metal gold',
        'style': 'realistic'
    })
    tester.cmd('ai_assist', 'suggest_optimization', {'target': 'performance'})


def test_versioning_tools(tester):
    """Test versioning tools"""
    print("\n--- Testing VERSIONING tools ---")
    tester.cmd('versioning', 'init', {})
    tester.cmd('versioning', 'save', {'name': 'test_v1', 'description': 'Test version'})
    tester.cmd('versioning', 'list', {'branch': 'main'})
    tester.cmd('versioning', 'branches', {})


def test_ai_generation_tools(tester):
    """Test AI generation tools"""
    print("\n--- Testing AI_GENERATION tools ---")
    tester.cmd('ai_generation', 'config', {'provider': 'local'})
    tester.cmd('object', 'create', {'type': 'CUBE', 'name': 'AIGenCube', 'location': [70, 0, 0]})
    tester.cmd('ai_generation', 'material_from_text', {
        'description': 'rusty metal',
        'object_name': 'AIGenCube'
    })


def test_vr_ar_tools(tester):
    """Test VR/AR tools"""
    print("\n--- Testing VR_AR tools ---")
    tester.cmd('vr_ar', 'setup', {'xr_runtime': 'OPENXR', 'floor_height': 0})
    tester.cmd('vr_ar', 'camera', {'camera_type': 'stereo', 'ipd': 0.064})
    tester.cmd('vr_ar', 'ar_marker', {'marker_name': 'TestMarker', 'marker_type': 'image', 'size': 0.1})


def test_substance_tools(tester):
    """Test Substance tools"""
    print("\n--- Testing SUBSTANCE tools ---")
    tester.cmd('substance', 'detect', {})


def test_zbrush_tools(tester):
    """Test ZBrush tools"""
    print("\n--- Testing ZBRUSH tools ---")
    tester.cmd('zbrush', 'detect', {})


def test_cloud_render_tools(tester):
    """Test cloud render tools"""
    print("\n--- Testing CLOUD_RENDER tools ---")
    tester.cmd('cloud_render', 'setup', {'service': 'local'})
    tester.cmd('cloud_render', 'discover', {})
    tester.cmd('cloud_render', 'estimate', {
        'frame_count': 100,
        'samples': 128,
        'resolution_x': 1920,
        'resolution_y': 1080
    })


def test_collaboration_tools(tester):
    """Test collaboration tools"""
    print("\n--- Testing COLLABORATION tools ---")
    tester.cmd('collaboration', 'status', {})
    tester.cmd('collaboration', 'host', {'session_name': 'TestSession', 'port': 9877})
    tester.cmd('collaboration', 'users', {})
    tester.cmd('collaboration', 'leave', {})


def test_render_tools(tester):
    """Test render tools"""
    print("\n--- Testing RENDER tools ---")
    tester.cmd('render', 'set_engine', {'engine': 'CYCLES'})
    tester.cmd('render', 'set_resolution', {'width': 1920, 'height': 1080})
    tester.cmd('render', 'set_samples', {'samples': 32})


def test_utility_tools(tester):
    """Test utility tools"""
    print("\n--- Testing UTILITY tools ---")
    tester.cmd('utility', 'execute_python', {
        'code': 'print("Hello from MCP!")'
    })
    tester.cmd('utility', 'get_blender_version', {})


def main():
    print("="*70)
    print("BLENDER MCP COMPREHENSIVE TEST - ALL MODULES")
    print("="*70)
    
    tester = MCPTester()
    
    try:
        tester.connect()
        
        # Clear scene
        clear_scene(tester)
        
        # Test all modules
        test_scene_tools(tester)
        test_object_tools(tester)
        test_material_tools(tester)
        test_lighting_tools(tester)
        test_camera_tools(tester)
        test_animation_tools(tester)
        test_render_tools(tester)
        test_utility_tools(tester)
        
        # Extended modules
        test_character_template_tools(tester)
        test_auto_rig_tools(tester)
        test_animation_preset_tools(tester)
        test_physics_tools(tester)
        test_scene_advanced_tools(tester)
        test_batch_tools(tester)
        test_curves_tools(tester)
        test_uv_tools(tester)
        test_nodes_tools(tester)
        test_compositor_tools(tester)
        test_vse_tools(tester)
        test_sculpt_tools(tester)
        test_texture_paint_tools(tester)
        test_gpencil_tools(tester)
        
        # New modules
        test_simulation_tools(tester)
        test_hair_tools(tester)
        test_assets_tools(tester)
        test_addons_tools(tester)
        test_world_tools(tester)
        test_constraints_tools(tester)
        test_preferences_tools(tester)
        test_external_tools(tester)
        test_ai_assist_tools(tester)
        test_versioning_tools(tester)
        test_ai_generation_tools(tester)
        test_vr_ar_tools(tester)
        test_substance_tools(tester)
        test_zbrush_tools(tester)
        test_cloud_render_tools(tester)
        test_collaboration_tools(tester)
        
        # Print summary
        passed, failed = tester.print_summary()
        
        print(f"\nTest completed! Check Blender to see the results.")
        
        return passed, failed
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1
    finally:
        tester.disconnect()


if __name__ == "__main__":
    passed, failed = main()
    exit(0 if failed == 0 else 1)
