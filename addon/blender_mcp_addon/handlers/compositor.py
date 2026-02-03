"""
合成器处理器

处理后期合成、颜色校正、特效等命令。
"""

from typing import Any, Dict, List
import bpy


def _ensure_compositor():
    """确保合成器已启用并返回节点树"""
    scene = bpy.context.scene
    
    # 启用合成器节点
    scene.use_nodes = True
    
    # 合成器节点树需要通过 scene.node_tree 访问
    # 但某些版本需要先启用才能访问
    node_tree = getattr(scene, 'node_tree', None)
    
    if node_tree is None:
        # 尝试创建默认设置
        scene.use_nodes = False
        scene.use_nodes = True
        node_tree = getattr(scene, 'node_tree', None)
    
    if node_tree is None:
        raise RuntimeError("无法创建合成器节点树")
    
    return node_tree


def _get_or_create_node(nodes, node_type, name, location=[0, 0]):
    """获取或创建节点"""
    for node in nodes:
        if node.name == name:
            return node
    
    node = nodes.new(type=node_type)
    node.name = name
    node.label = name
    node.location = location
    return node


def handle_enable(params: Dict[str, Any]) -> Dict[str, Any]:
    """启用合成器"""
    enable = params.get("enable", True)
    use_backdrop = params.get("use_backdrop", True)
    
    try:
        scene = bpy.context.scene
        scene.use_nodes = enable
        
        if enable:
            node_tree = _ensure_compositor()
            
            # 确保有基本节点
            nodes = node_tree.nodes
            
            # 渲染层节点
            render_layers = None
            composite = None
            
            for node in nodes:
                if node.type == 'R_LAYERS':
                    render_layers = node
                elif node.type == 'COMPOSITE':
                    composite = node
            
            if not render_layers:
                render_layers = nodes.new('CompositorNodeRLayers')
                render_layers.location = [-200, 0]
            
            if not composite:
                composite = nodes.new('CompositorNodeComposite')
                composite.location = [400, 0]
            
            # 连接
            if not composite.inputs['Image'].is_linked:
                node_tree.links.new(render_layers.outputs['Image'], composite.inputs['Image'])
        
        return {
            "success": True,
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "COMPOSITOR_ERROR", "message": str(e)}
        }


def handle_preset(params: Dict[str, Any]) -> Dict[str, Any]:
    """应用合成器预设"""
    preset = params.get("preset", "color_correction")
    intensity = params.get("intensity", 1.0)
    
    node_tree = _ensure_compositor()
    nodes = node_tree.nodes
    links = node_tree.links
    
    # 找到渲染层和合成输出
    render_layers = None
    composite = None
    
    for node in nodes:
        if node.type == 'R_LAYERS':
            render_layers = node
        elif node.type == 'COMPOSITE':
            composite = node
    
    if not render_layers or not composite:
        return {
            "success": False,
            "error": {"code": "MISSING_NODES", "message": "缺少基本节点"}
        }
    
    # 断开现有连接
    for link in list(links):
        if link.to_socket == composite.inputs['Image']:
            links.remove(link)
    
    last_output = render_layers.outputs['Image']
    
    if preset == "color_correction":
        # 颜色校正
        cc = _get_or_create_node(nodes, 'CompositorNodeColorCorrection', 'ColorCorrection', [200, 0])
        cc.master_saturation = 1.0 + (intensity - 1.0) * 0.2
        cc.master_gain = 1.0 + (intensity - 1.0) * 0.1
        
        links.new(last_output, cc.inputs['Image'])
        last_output = cc.outputs['Image']
        
    elif preset == "bloom":
        # 辉光效果
        glare = _get_or_create_node(nodes, 'CompositorNodeGlare', 'Bloom', [200, 0])
        glare.glare_type = 'FOG_GLOW'
        glare.threshold = 1.0 - intensity * 0.5
        glare.size = int(6 + intensity * 3)
        
        links.new(last_output, glare.inputs['Image'])
        last_output = glare.outputs['Image']
        
    elif preset == "vignette":
        # 暗角
        ellipse = _get_or_create_node(nodes, 'CompositorNodeEllipseMask', 'VignetteMask', [200, 100])
        ellipse.width = 0.8
        ellipse.height = 0.8
        
        blur_node = _get_or_create_node(nodes, 'CompositorNodeBlur', 'VignetteBlur', [200, 0])
        blur_node.size_x = 200
        blur_node.size_y = 200
        
        mix = _get_or_create_node(nodes, 'CompositorNodeMixRGB', 'VignetteMix', [400, 0])
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Fac'].default_value = intensity * 0.5
        
        links.new(ellipse.outputs['Mask'], blur_node.inputs['Image'])
        links.new(last_output, mix.inputs[1])
        links.new(blur_node.outputs['Image'], mix.inputs[2])
        last_output = mix.outputs['Image']
        
    elif preset == "blur":
        # 模糊
        blur_node = _get_or_create_node(nodes, 'CompositorNodeBlur', 'Blur', [200, 0])
        blur_node.filter_type = 'FAST_GAUSS'
        blur_node.size_x = intensity * 10
        blur_node.size_y = intensity * 10
        
        links.new(last_output, blur_node.inputs['Image'])
        last_output = blur_node.outputs['Image']
        
    elif preset == "sharpen":
        # 锐化
        sharpen = _get_or_create_node(nodes, 'CompositorNodeFilter', 'Sharpen', [200, 0])
        sharpen.filter_type = 'SHARPEN'
        sharpen.inputs['Fac'].default_value = intensity
        
        links.new(last_output, sharpen.inputs['Image'])
        last_output = sharpen.outputs['Image']
        
    elif preset == "film_grain":
        # 胶片颗粒（使用噪波）
        # 由于合成器没有直接的胶片颗粒节点，使用混合噪波
        pass
        
    elif preset == "chromatic_aberration":
        # 色差
        lens_distortion = _get_or_create_node(nodes, 'CompositorNodeLensdist', 'ChromaticAberration', [200, 0])
        lens_distortion.use_jitter = False
        lens_distortion.use_fit = True
        lens_distortion.inputs['Dispersion'].default_value = intensity * 0.02
        
        links.new(last_output, lens_distortion.inputs['Image'])
        last_output = lens_distortion.outputs['Image']
    
    # 连接到输出
    links.new(last_output, composite.inputs['Image'])
    
    return {
        "success": True,
        "data": {
            "preset": preset
        }
    }


def handle_color_balance(params: Dict[str, Any]) -> Dict[str, Any]:
    """颜色平衡"""
    shadows = params.get("shadows")
    midtones = params.get("midtones")
    highlights = params.get("highlights")
    
    node_tree = _ensure_compositor()
    nodes = node_tree.nodes
    links = node_tree.links
    
    # 找到渲染层和合成输出
    render_layers = None
    composite = None
    
    for node in nodes:
        if node.type == 'R_LAYERS':
            render_layers = node
        elif node.type == 'COMPOSITE':
            composite = node
    
    if not render_layers or not composite:
        return {
            "success": False,
            "error": {"code": "MISSING_NODES", "message": "缺少基本节点"}
        }
    
    # 创建颜色平衡节点
    cb = _get_or_create_node(nodes, 'CompositorNodeColorBalance', 'ColorBalance', [200, 0])
    cb.correction_method = 'LIFT_GAMMA_GAIN'
    
    if shadows:
        cb.lift = shadows
    if midtones:
        cb.gamma = midtones
    if highlights:
        cb.gain = highlights
    
    # 断开旧连接
    for link in list(links):
        if link.to_socket == composite.inputs['Image']:
            links.remove(link)
    
    # 重新连接
    links.new(render_layers.outputs['Image'], cb.inputs['Image'])
    links.new(cb.outputs['Image'], composite.inputs['Image'])
    
    return {
        "success": True,
        "data": {}
    }


def handle_blur(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加模糊"""
    blur_type = params.get("blur_type", "FAST_GAUSS")
    size_x = params.get("size_x", 10.0)
    size_y = params.get("size_y", 10.0)
    
    node_tree = _ensure_compositor()
    nodes = node_tree.nodes
    links = node_tree.links
    
    # 找到渲染层和合成输出
    render_layers = None
    composite = None
    
    for node in nodes:
        if node.type == 'R_LAYERS':
            render_layers = node
        elif node.type == 'COMPOSITE':
            composite = node
    
    if not render_layers or not composite:
        return {
            "success": False,
            "error": {"code": "MISSING_NODES", "message": "缺少基本节点"}
        }
    
    # 创建模糊节点
    blur = _get_or_create_node(nodes, 'CompositorNodeBlur', 'Blur', [200, 0])
    blur.filter_type = blur_type
    blur.size_x = int(size_x)
    blur.size_y = int(size_y)
    
    # 断开旧连接
    for link in list(links):
        if link.to_socket == composite.inputs['Image']:
            links.remove(link)
    
    # 重新连接
    links.new(render_layers.outputs['Image'], blur.inputs['Image'])
    links.new(blur.outputs['Image'], composite.inputs['Image'])
    
    return {
        "success": True,
        "data": {}
    }


def handle_render_layer(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置渲染层"""
    layer_name = params.get("layer_name", "ViewLayer")
    use_pass_combined = params.get("use_pass_combined", True)
    use_pass_z = params.get("use_pass_z", False)
    use_pass_normal = params.get("use_pass_normal", False)
    use_pass_ao = params.get("use_pass_ao", False)
    
    view_layer = bpy.context.scene.view_layers.get(layer_name)
    if not view_layer:
        return {
            "success": False,
            "error": {"code": "LAYER_NOT_FOUND", "message": f"视图层不存在: {layer_name}"}
        }
    
    view_layer.use_pass_combined = use_pass_combined
    view_layer.use_pass_z = use_pass_z
    view_layer.use_pass_normal = use_pass_normal
    view_layer.use_pass_ambient_occlusion = use_pass_ao
    
    return {
        "success": True,
        "data": {}
    }
