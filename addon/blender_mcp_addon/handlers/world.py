"""
世界/环境处理器

处理Blender世界和环境设置命令。
"""

from typing import Any, Dict
import bpy
import os


def _ensure_world():
    """确保有活动的世界"""
    if not bpy.context.scene.world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    return bpy.context.scene.world


def handle_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建新世界"""
    name = params.get("name", "World")
    use_nodes = params.get("use_nodes", True)
    
    try:
        world = bpy.data.worlds.new(name)
        world.use_nodes = use_nodes
        
        # 设置为当前场景的世界
        bpy.context.scene.world = world
        
        return {
            "success": True,
            "data": {
                "world_name": world.name,
                "use_nodes": use_nodes
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "WORLD_CREATE_ERROR", "message": str(e)}
        }


def handle_background(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置世界背景"""
    color = params.get("color")
    strength = params.get("strength", 1.0)
    use_sky_texture = params.get("use_sky_texture", False)
    
    try:
        world = _ensure_world()
        world.use_nodes = True
        
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # 清除现有节点
        nodes.clear()
        
        # 创建输出节点
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (300, 0)
        
        # 创建背景节点
        background = nodes.new('ShaderNodeBackground')
        background.location = (0, 0)
        background.inputs['Strength'].default_value = strength
        
        if color:
            background.inputs['Color'].default_value = color[:3] + [1.0] if len(color) == 3 else color[:4]
        
        if use_sky_texture:
            # 添加天空纹理
            sky = nodes.new('ShaderNodeTexSky')
            sky.location = (-300, 0)
            links.new(sky.outputs['Color'], background.inputs['Color'])
        
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return {
            "success": True,
            "data": {
                "world_name": world.name,
                "color": color,
                "strength": strength
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "BACKGROUND_ERROR", "message": str(e)}
        }


def handle_hdri(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置HDRI环境"""
    hdri_path = params.get("hdri_path")
    strength = params.get("strength", 1.0)
    rotation = params.get("rotation", 0.0)
    
    if not os.path.exists(hdri_path):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"HDRI文件不存在: {hdri_path}"}
        }
    
    try:
        world = _ensure_world()
        world.use_nodes = True
        
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # 清除现有节点
        nodes.clear()
        
        # 创建节点
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (300, 0)
        
        background = nodes.new('ShaderNodeBackground')
        background.location = (0, 0)
        background.inputs['Strength'].default_value = strength
        
        env_tex = nodes.new('ShaderNodeTexEnvironment')
        env_tex.location = (-300, 0)
        
        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-500, 0)
        mapping.inputs['Rotation'].default_value[2] = rotation
        
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-700, 0)
        
        # 加载HDRI
        image = bpy.data.images.load(hdri_path)
        env_tex.image = image
        
        # 连接节点
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        links.new(env_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return {
            "success": True,
            "data": {
                "world_name": world.name,
                "hdri": hdri_path,
                "strength": strength
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "HDRI_ERROR", "message": str(e)}
        }


def handle_sky(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置程序化天空"""
    sky_type = params.get("sky_type", "NISHITA")
    sun_elevation = params.get("sun_elevation", 0.785)
    sun_rotation = params.get("sun_rotation", 0.0)
    air_density = params.get("air_density", 1.0)
    dust_density = params.get("dust_density", 0.0)
    ozone_density = params.get("ozone_density", 1.0)
    
    try:
        world = _ensure_world()
        world.use_nodes = True
        
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # 清除现有节点
        nodes.clear()
        
        # 创建节点
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (300, 0)
        
        background = nodes.new('ShaderNodeBackground')
        background.location = (0, 0)
        
        sky = nodes.new('ShaderNodeTexSky')
        sky.location = (-300, 0)
        sky.sky_type = sky_type
        
        if sky_type == 'NISHITA':
            sky.sun_elevation = sun_elevation
            sky.sun_rotation = sun_rotation
            sky.air_density = air_density
            sky.dust_density = dust_density
            sky.ozone_density = ozone_density
        elif sky_type in ['PREETHAM', 'HOSEK_WILKIE']:
            sky.sun_direction[0] = 0
            sky.sun_direction[1] = 0
            sky.sun_direction[2] = 1
        
        # 连接节点
        links.new(sky.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return {
            "success": True,
            "data": {
                "world_name": world.name,
                "sky_type": sky_type
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SKY_ERROR", "message": str(e)}
        }


def handle_fog(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置体积雾"""
    use_fog = params.get("use_fog", True)
    density = params.get("density", 0.01)
    color = params.get("color", [0.5, 0.6, 0.7])
    anisotropy = params.get("anisotropy", 0.0)
    
    try:
        world = _ensure_world()
        world.use_nodes = True
        
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # 找到输出节点
        output = None
        for node in nodes:
            if node.type == 'OUTPUT_WORLD':
                output = node
                break
        
        if not output:
            output = nodes.new('ShaderNodeOutputWorld')
            output.location = (300, 0)
        
        if use_fog:
            # 创建体积散射节点
            volume = nodes.new('ShaderNodeVolumeScatter')
            volume.location = (0, -200)
            volume.inputs['Color'].default_value = color[:3] + [1.0]
            volume.inputs['Density'].default_value = density
            volume.inputs['Anisotropy'].default_value = anisotropy
            
            links.new(volume.outputs['Volume'], output.inputs['Volume'])
        else:
            # 断开体积连接
            for link in output.inputs['Volume'].links:
                links.remove(link)
        
        return {
            "success": True,
            "data": {
                "use_fog": use_fog,
                "density": density
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "FOG_ERROR", "message": str(e)}
        }


def handle_ambient_occlusion(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置环境光遮蔽"""
    use_ao = params.get("use_ao", True)
    distance = params.get("distance", 1.0)
    factor = params.get("factor", 1.0)
    
    try:
        world = _ensure_world()
        
        # 环境光遮蔽是渲染设置
        scene = bpy.context.scene
        
        # Cycles
        if scene.render.engine == 'CYCLES':
            world.light_settings.use_ambient_occlusion = use_ao
            world.light_settings.ao_factor = factor
            world.light_settings.distance = distance
        
        # EEVEE
        elif scene.render.engine in ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']:
            scene.eevee.use_gtao = use_ao
            scene.eevee.gtao_distance = distance
            scene.eevee.gtao_factor = factor
        
        return {
            "success": True,
            "data": {
                "use_ao": use_ao,
                "distance": distance,
                "factor": factor
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "AO_ERROR", "message": str(e)}
        }
