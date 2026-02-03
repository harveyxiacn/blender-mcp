"""
物理模拟处理器

处理布料、刚体、粒子系统等物理模拟命令。
"""

from typing import Any, Dict
import bpy


# 布料预设配置
CLOTH_PRESETS = {
    "cotton": {
        "mass": 0.3,
        "air_damping": 1.0,
        "tension_stiffness": 15,
        "compression_stiffness": 15,
        "shear_stiffness": 15,
        "bending_stiffness": 0.5,
    },
    "silk": {
        "mass": 0.15,
        "air_damping": 1.0,
        "tension_stiffness": 5,
        "compression_stiffness": 5,
        "shear_stiffness": 5,
        "bending_stiffness": 0.05,
    },
    "leather": {
        "mass": 0.4,
        "air_damping": 1.0,
        "tension_stiffness": 80,
        "compression_stiffness": 80,
        "shear_stiffness": 80,
        "bending_stiffness": 15,
    },
    "denim": {
        "mass": 0.4,
        "air_damping": 1.0,
        "tension_stiffness": 40,
        "compression_stiffness": 40,
        "shear_stiffness": 40,
        "bending_stiffness": 10,
    },
    "rubber": {
        "mass": 0.3,
        "air_damping": 1.0,
        "tension_stiffness": 15,
        "compression_stiffness": 15,
        "shear_stiffness": 15,
        "bending_stiffness": 25,
    },
}


def handle_cloth_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加布料模拟"""
    object_name = params.get("object_name")
    preset = params.get("preset", "cotton")
    pin_group = params.get("pin_group")
    collision_quality = params.get("collision_quality", 2)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 选择对象
    bpy.context.view_layer.objects.active = obj
    
    # 添加布料修改器
    cloth_mod = obj.modifiers.new(name="Cloth", type='CLOTH')
    cloth = cloth_mod.settings
    
    # 应用预设
    preset_config = CLOTH_PRESETS.get(preset, CLOTH_PRESETS["cotton"])
    cloth.mass = preset_config["mass"]
    cloth.air_damping = preset_config["air_damping"]
    cloth.tension_stiffness = preset_config["tension_stiffness"]
    cloth.compression_stiffness = preset_config["compression_stiffness"]
    cloth.shear_stiffness = preset_config["shear_stiffness"]
    cloth.bending_stiffness = preset_config["bending_stiffness"]
    
    # 碰撞设置
    cloth.collision_settings.collision_quality = collision_quality
    
    # 固定组
    if pin_group and pin_group in obj.vertex_groups:
        cloth.vertex_group_mass = pin_group
    
    return {
        "success": True,
        "data": {
            "preset": preset
        }
    }


def handle_rigid_body_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加刚体"""
    object_name = params.get("object_name")
    body_type = params.get("body_type", "ACTIVE")
    shape = params.get("shape", "CONVEX_HULL")
    mass = params.get("mass", 1.0)
    friction = params.get("friction", 0.5)
    bounciness = params.get("bounciness", 0.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    # 确保有刚体世界
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # 选择对象
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 添加刚体
    bpy.ops.rigidbody.object_add()
    
    # 设置属性
    obj.rigid_body.type = body_type
    obj.rigid_body.collision_shape = shape
    obj.rigid_body.mass = mass
    obj.rigid_body.friction = friction
    obj.rigid_body.restitution = bounciness
    
    return {
        "success": True,
        "data": {
            "body_type": body_type,
            "shape": shape
        }
    }


def handle_collision_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加碰撞体"""
    object_name = params.get("object_name")
    damping = params.get("damping", 0.0)
    thickness = params.get("thickness", 0.02)
    friction = params.get("friction", 0.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 添加碰撞修改器
    collision_mod = obj.modifiers.new(name="Collision", type='COLLISION')
    collision = collision_mod.settings
    
    collision.damping = damping
    collision.thickness_outer = thickness
    collision.friction_factor = friction
    
    return {
        "success": True,
        "data": {}
    }


def handle_particles_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """创建粒子系统"""
    object_name = params.get("object_name")
    particle_type = params.get("particle_type", "EMITTER")
    count = params.get("count", 1000)
    lifetime = params.get("lifetime", 50.0)
    emit_from = params.get("emit_from", "FACE")
    velocity_normal = params.get("velocity_normal", 1.0)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 添加粒子系统
    obj.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
    particle_system = obj.particle_systems[-1]
    settings = particle_system.settings
    
    # 设置属性
    settings.type = particle_type
    settings.count = count
    settings.lifetime = lifetime
    settings.emit_from = emit_from
    settings.normal_factor = velocity_normal
    
    return {
        "success": True,
        "data": {
            "particle_system": particle_system.name,
            "count": count
        }
    }


def handle_force_field_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加力场"""
    force_type = params.get("force_type", "WIND")
    location = params.get("location", [0, 0, 0])
    strength = params.get("strength", 1.0)
    flow = params.get("flow", 0.0)
    
    # 创建空对象作为力场
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    force_obj = bpy.context.active_object
    force_obj.name = f"ForceField_{force_type}"
    
    # 添加力场
    bpy.ops.object.forcefield_toggle()
    force_obj.field.type = force_type
    force_obj.field.strength = strength
    force_obj.field.flow = flow
    
    return {
        "success": True,
        "data": {
            "force_field_name": force_obj.name,
            "force_type": force_type
        }
    }


def handle_soft_body_add(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加软体"""
    object_name = params.get("object_name")
    mass = params.get("mass", 1.0)
    friction = params.get("friction", 0.5)
    goal_strength = params.get("goal_strength", 0.7)
    
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "MESH_NOT_FOUND", "message": f"网格不存在: {object_name}"}
        }
    
    # 添加软体修改器
    soft_body_mod = obj.modifiers.new(name="Softbody", type='SOFT_BODY')
    soft_body = soft_body_mod.settings
    
    soft_body.mass = mass
    soft_body.friction = friction
    soft_body.goal_default = goal_strength
    
    return {
        "success": True,
        "data": {}
    }
