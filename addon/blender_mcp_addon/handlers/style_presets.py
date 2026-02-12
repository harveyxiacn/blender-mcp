"""
风格预设处理器

处理风格环境设置、描边效果、烘焙工作流等操作。
"""

from typing import Any, Dict
import bpy
import os
import math


# ==================== 风格配置数据 ====================

STYLE_CONFIGS = {
    "PIXEL": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "FLAT",
        "texture_filter": "Closest",
        "color_management": "Standard",
        "film_transparent": False,
        "samples": 16,
        "tips": (
            "像素/体素风格建模建议:\n"
            "1. 使用Cube作为基本单元，通过Array修改器排列\n"
            "2. 图元参数: segments=4~8 (低段数)\n"
            "3. 材质: 纯色Flat材质，关闭Smooth Shading\n"
            "4. 纹理: 使用Closest(最近邻)插值，保持像素锐边\n"
            "5. 相机: 使用正交投影(Orthographic)\n"
            "6. 灯光: 简单方向光，关闭阴影或使用硬阴影"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Flat Shading",
            "纹理过滤": "Closest (最近邻)",
            "推荐面数": "50-500面",
            "纹理分辨率": "16×16 ~ 64×64",
        }
    },
    "LOW_POLY": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "FLAT",
        "texture_filter": "Linear",
        "color_management": "Standard",
        "film_transparent": False,
        "samples": 32,
        "tips": (
            "Low Poly风格建模建议:\n"
            "1. 图元参数: segments=6~12, subdivisions=1\n"
            "2. 使用Flat Shading，不使用细分曲面\n"
            "3. 着色: 使用顶点色(Vertex Color)或简单纯色材质\n"
            "4. 三角面可接受，保持几何简洁\n"
            "5. 场景: 大量使用Array和Mirror修改器\n"
            "6. 推荐使用blender_vertex_color工具为面着色"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Flat Shading",
            "纹理过滤": "Linear",
            "推荐面数": "200-2000面",
            "纹理分辨率": "无纹理/纯色",
        }
    },
    "STYLIZED": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Standard",
        "film_transparent": False,
        "samples": 64,
        "tips": (
            "风格化建模建议:\n"
            "1. 使用细分曲面(SubSurf) level=1~2\n"
            "2. 用倒角(Bevel)加支撑环保持轮廓\n"
            "3. 材质: 使用ColorRamp渐变色+Shader to RGB\n"
            "4. 场景: Geometry Nodes散布植被/装饰\n"
            "5. 适度夸张比例，圆润化转角\n"
            "6. 可加描边(blender_outline_effect)"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Smooth Shading",
            "纹理过滤": "Linear",
            "推荐面数": "2K-10K面",
            "纹理分辨率": "128-512",
        }
    },
    "TOON": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Standard",
        "film_transparent": False,
        "samples": 64,
        "tips": (
            "卡通/赛璐璐风格建模建议:\n"
            "1. 使用Shader to RGB + ColorRamp(Constant)实现Cel Shading\n"
            "2. 必须加描边: blender_outline_effect(method=SOLIDIFY)\n"
            "3. 阴影分2-3层: 亮色/暗色/最暗色\n"
            "4. 高光用锐利的ColorRamp带\n"
            "5. 边缘光(Fresnel)增加轮廓感\n"
            "6. 材质: 使用blender_create_toon_material或blender_procedural_material"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Smooth Shading + Cel Shading",
            "描边": "推荐Solidify翻转法线",
            "推荐面数": "3K-15K面",
            "纹理分辨率": "512-1K",
        }
    },
    "HAND_PAINTED": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Standard",
        "film_transparent": False,
        "samples": 64,
        "tips": (
            "手绘风格建模建议:\n"
            "1. UV展开质量极重要！使用Smart UV Project + 手动调整\n"
            "2. 材质: 仅Diffuse(Base Color)，无PBR数据通道\n"
            "3. 纹理绘制: 先烘焙AO到纹理作为暗化基础\n"
            "4. 手绘阴影/高光直接画在Diffuse贴图上\n"
            "5. 低饱和度阴影 + 高饱和度高光\n"
            "6. 使用blender_texture_paint系列工具"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Smooth Shading",
            "材质模式": "Diffuse Only (无PBR)",
            "推荐面数": "5K-30K面",
            "纹理分辨率": "1K-2K",
        }
    },
    "SEMI_REALISTIC": {
        "render_engine": "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Filmic",
        "film_transparent": False,
        "samples": 128,
        "tips": (
            "半写实风格建模建议:\n"
            "1. 使用细分曲面level=2 + 支撑环/折痕边\n"
            "2. 良好的四边形拓扑(Quad-dominant)\n"
            "3. 材质: 简化PBR(Base Color + Normal + Roughness)\n"
            "4. 法线贴图: 从高模烘焙或使用程序化凹凸\n"
            "5. 自动平滑角度30°~45°\n"
            "6. 可用blender_bake_maps烘焙法线/AO"
        ),
        "settings_applied": {
            "渲染引擎": "EEVEE",
            "着色方式": "Smooth + Auto Smooth",
            "色彩管理": "Filmic",
            "推荐面数": "10K-50K面",
            "纹理分辨率": "1K-2K",
        }
    },
    "PBR_REALISTIC": {
        "render_engine": "CYCLES",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Filmic",
        "film_transparent": False,
        "samples": 256,
        "tips": (
            "PBR写实风格建模建议:\n"
            "1. 高模雕刻 → 低模重拓扑 → 法线烘焙\n"
            "2. 完整PBR: BaseColor/Normal/Roughness/Metallic/AO/Displacement\n"
            "3. 使用blender_procedural_material获取程序化PBR预设\n"
            "4. 添加磨损效果: edge_wear通过Pointiness/曲率\n"
            "5. 使用blender_bake_maps烘焙全套贴图\n"
            "6. LOD: 使用blender_lod_generate创建多级细节"
        ),
        "settings_applied": {
            "渲染引擎": "Cycles",
            "着色方式": "Smooth + Auto Smooth",
            "色彩管理": "Filmic",
            "推荐面数": "30K-100K面",
            "纹理分辨率": "2K-4K",
        }
    },
    "AAA": {
        "render_engine": "CYCLES",
        "shading": "SMOOTH",
        "texture_filter": "Linear",
        "color_management": "Filmic",
        "film_transparent": False,
        "samples": 512,
        "tips": (
            "3A/影视级建模建议:\n"
            "1. 高精度雕刻(多分辨率Multires) → QuadriFlow重拓扑\n"
            "2. UDIM多瓦片UV(如需超高分辨率)\n"
            "3. 全套PBR贴图 + Displacement置换\n"
            "4. 皮肤: SSS次表面散射 + 毛孔细节\n"
            "5. 毛发: Hair Curves系统\n"
            "6. 眼球/牙齿: 专项材质\n"
            "7. 布料: 物理模拟烘焙\n"
            "8. 使用blender_bake_maps烘焙高→低全套贴图"
        ),
        "settings_applied": {
            "渲染引擎": "Cycles",
            "着色方式": "Smooth + Adaptive Subdivision",
            "色彩管理": "Filmic",
            "推荐面数": "100K-10M面(雕刻)",
            "纹理分辨率": "4K-8K + UDIM",
        }
    },
}


def handle_setup(params: Dict[str, Any]) -> Dict[str, Any]:
    """设置风格环境"""
    style = params.get("style", "LOW_POLY")
    apply_to_scene = params.get("apply_to_scene", True)
    apply_to_objects = params.get("apply_to_objects", [])

    config = STYLE_CONFIGS.get(style)
    if not config:
        return {
            "success": False,
            "error": {"code": "UNKNOWN_STYLE", "message": f"未知风格: {style}"}
        }

    scene = bpy.context.scene
    extra_applied = []

    if apply_to_scene:
        # 设置渲染引擎
        try:
            scene.render.engine = config["render_engine"]
        except Exception:
            if "EEVEE" in config["render_engine"]:
                try:
                    scene.render.engine = "BLENDER_EEVEE"
                except Exception:
                    pass

        # 设置采样
        if hasattr(scene, 'eevee') and "EEVEE" in scene.render.engine:
            scene.eevee.taa_render_samples = config["samples"]
        elif scene.render.engine == "CYCLES":
            scene.cycles.samples = config["samples"]
            # Cycles去噪
            if style in ("PBR_REALISTIC", "AAA", "SEMI_REALISTIC"):
                scene.cycles.use_denoising = True
                try:
                    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
                except Exception:
                    pass
                extra_applied.append("去噪: OpenImageDenoise")

        # 色彩管理
        scene.view_settings.view_transform = config.get("color_management", "Standard")

        # EEVEE特性 (Bloom/AO/SSR)
        if hasattr(scene, 'eevee') and "EEVEE" in scene.render.engine:
            eevee = scene.eevee
            if style in ("STYLIZED", "TOON"):
                # 风格化/卡通: 可选Bloom，关AO
                if hasattr(eevee, 'use_bloom'):
                    eevee.use_bloom = True
                    eevee.bloom_threshold = 0.8
                    eevee.bloom_intensity = 0.1
                    extra_applied.append("辉光(Bloom): 开启(低强度)")
                if hasattr(eevee, 'use_gtao'):
                    eevee.use_gtao = False
                    extra_applied.append("AO: 关闭(保持Cel风格)")
            elif style in ("SEMI_REALISTIC",):
                if hasattr(eevee, 'use_gtao'):
                    eevee.use_gtao = True
                    extra_applied.append("AO: 开启")
                if hasattr(eevee, 'use_ssr'):
                    eevee.use_ssr = True
                    extra_applied.append("屏幕空间反射: 开启")
            elif style in ("PIXEL", "LOW_POLY"):
                if hasattr(eevee, 'use_bloom'):
                    eevee.use_bloom = False
                if hasattr(eevee, 'use_gtao'):
                    eevee.use_gtao = False
                if hasattr(eevee, 'use_ssr'):
                    eevee.use_ssr = False

        # 像素风格: 设置活动摄像机为正交
        if style == "PIXEL":
            cam = scene.camera
            if cam and cam.type == 'CAMERA':
                cam.data.type = 'ORTHO'
                cam.data.ortho_scale = 10.0
                extra_applied.append("摄像机: 正交投影(Orthographic)")

        # 透明胶片
        scene.render.film_transparent = config.get("film_transparent", False)

    # 对指定对象应用着色和纹理设置
    for obj_name in apply_to_objects:
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.type == 'MESH':
            # 着色方式
            if config["shading"] == "FLAT":
                for poly in obj.data.polygons:
                    poly.use_smooth = False
            else:
                for poly in obj.data.polygons:
                    poly.use_smooth = True

            # 像素风格: 设置已有材质的纹理插值为Closest
            if style == "PIXEL" and obj.data.materials:
                for mat in obj.data.materials:
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                node.interpolation = 'Closest'
                extra_applied.append(f"{obj_name}: 纹理插值→Closest")

    return {
        "success": True,
        "data": {
            "style": style,
            "tips": config["tips"],
            "settings_applied": config["settings_applied"],
            "extra_applied": extra_applied
        }
    }


def handle_outline(params: Dict[str, Any]) -> Dict[str, Any]:
    """添加描边效果"""
    object_name = params.get("object_name")
    method = params.get("method", "SOLIDIFY")
    thickness = params.get("thickness", 0.02)
    color = params.get("color", [0, 0, 0])

    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "INVALID_OBJECT", "message": f"对象不存在或不是网格: {object_name}"}
        }

    try:
        if method == "SOLIDIFY":
            # 创建描边材质
            outline_mat_name = f"{object_name}_Outline"
            outline_mat = bpy.data.materials.get(outline_mat_name)
            if not outline_mat:
                outline_mat = bpy.data.materials.new(name=outline_mat_name)
                outline_mat.use_nodes = True
                outline_mat.use_backface_culling = True
                # 设置为纯色
                nodes = outline_mat.node_tree.nodes
                bsdf = None
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        bsdf = node
                        break
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = (*color[:3], 1.0)
                    if 'Emission Color' in bsdf.inputs:
                        bsdf.inputs['Emission Color'].default_value = (*color[:3], 1.0)
                    elif 'Emission' in bsdf.inputs:
                        bsdf.inputs['Emission'].default_value = (*color[:3], 1.0)

            # 添加到材质槽
            if outline_mat_name not in [ms.material.name for ms in obj.material_slots if ms.material]:
                obj.data.materials.append(outline_mat)

            outline_slot = len(obj.material_slots) - 1

            # 添加Solidify修改器
            mod = obj.modifiers.new(name="Outline", type='SOLIDIFY')
            mod.thickness = -thickness  # 负值=向外
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.material_offset = outline_slot
            mod.offset = 1.0  # 仅向外

        elif method == "FREESTYLE":
            scene = bpy.context.scene
            # 启用Freestyle
            scene.render.use_freestyle = True
            # 设置Freestyle线条
            view_layer = bpy.context.view_layer
            if hasattr(view_layer, 'freestyle_settings'):
                fs = view_layer.freestyle_settings
                if len(fs.linesets) == 0:
                    ls = fs.linesets.new("OutlineSet")
                else:
                    ls = fs.linesets[0]
                ls.linestyle.thickness = thickness * 100  # Freestyle uses pixel units
                ls.linestyle.color = color[:3] if len(color) >= 3 else (0, 0, 0)

        elif method == "GREASE_PENCIL":
            # 使用Line Art修改器(Blender 3.0+)
            bpy.ops.object.gpencil_add(type='LRT_COLLECTION')
            gp_obj = bpy.context.active_object
            if gp_obj and gp_obj.type == 'GPENCIL':
                gp_obj.name = f"{object_name}_LineArt"
                # 设置Line Art修改器
                for mod in gp_obj.grease_pencil_modifiers:
                    if mod.type == 'GP_LINEART':
                        mod.source_type = 'OBJECT'
                        mod.source_object = obj
                        mod.thickness = int(thickness * 100)
                        break

        else:
            return {
                "success": False,
                "error": {"code": "UNKNOWN_METHOD", "message": f"未知描边方法: {method}"}
            }

    except Exception as e:
        return {
            "success": False,
            "error": {"code": "OUTLINE_FAILED", "message": str(e)}
        }

    return {"success": True, "data": {"method": method, "thickness": thickness}}


def handle_bake_maps(params: Dict[str, Any]) -> Dict[str, Any]:
    """烘焙贴图（高模→低模）"""
    high_poly_name = params.get("high_poly")
    low_poly_name = params.get("low_poly")
    maps = params.get("maps", ["NORMAL", "AO"])
    resolution = params.get("resolution", 2048)
    cage_extrusion = params.get("cage_extrusion", 0.1)
    output_dir = params.get("output_dir")
    margin = params.get("margin", 16)

    high_obj = bpy.data.objects.get(high_poly_name)
    low_obj = bpy.data.objects.get(low_poly_name)

    if not high_obj or high_obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "INVALID_OBJECT", "message": f"高模不存在或不是网格: {high_poly_name}"}
        }
    if not low_obj or low_obj.type != 'MESH':
        return {
            "success": False,
            "error": {"code": "INVALID_OBJECT", "message": f"低模不存在或不是网格: {low_poly_name}"}
        }

    # 切换到Cycles（烘焙需要）
    scene = bpy.context.scene
    original_engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64

    # 确定输出目录
    if not output_dir:
        blend_path = bpy.data.filepath
        if blend_path:
            output_dir = os.path.dirname(blend_path)
        else:
            output_dir = os.path.expanduser("~")

    baked_maps = []

    try:
        # 确保低模有材质
        if len(low_obj.data.materials) == 0:
            mat = bpy.data.materials.new(name=f"{low_poly_name}_BakeMat")
            mat.use_nodes = True
            low_obj.data.materials.append(mat)

        mat = low_obj.data.materials[0]
        if not mat.use_nodes:
            mat.use_nodes = True

        nodes = mat.node_tree.nodes

        for map_type in maps:
            # 创建烘焙用图像
            img_name = f"{low_poly_name}_{map_type}"
            img = bpy.data.images.get(img_name)
            if img:
                bpy.data.images.remove(img)

            is_data = map_type != "DIFFUSE"
            img = bpy.data.images.new(
                name=img_name,
                width=resolution,
                height=resolution,
                alpha=False,
                float_buffer=is_data,
            )
            if is_data:
                img.colorspace_settings.name = 'Non-Color'

            # 创建图像纹理节点
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.image = img
            tex_node.name = f"Bake_{map_type}"
            tex_node.label = f"Bake {map_type}"

            # 选择该节点为active
            for n in nodes:
                n.select = False
            tex_node.select = True
            nodes.active = tex_node

            # 设置烘焙参数
            scene.render.bake.use_selected_to_active = True
            scene.render.bake.cage_extrusion = cage_extrusion
            scene.render.bake.margin = margin

            # 选择对象
            bpy.ops.object.select_all(action='DESELECT')
            high_obj.select_set(True)
            low_obj.select_set(True)
            bpy.context.view_layer.objects.active = low_obj

            # 执行烘焙
            bake_type_map = {
                "NORMAL": "NORMAL",
                "AO": "AO",
                "DIFFUSE": "DIFFUSE",
                "ROUGHNESS": "ROUGHNESS",
                "COMBINED": "COMBINED",
                "CURVATURE": "NORMAL",  # 曲率通过后处理
            }
            blender_bake_type = bake_type_map.get(map_type, "NORMAL")

            if map_type == "DIFFUSE":
                scene.render.bake.use_pass_direct = False
                scene.render.bake.use_pass_indirect = False
                scene.render.bake.use_pass_color = True

            bpy.ops.object.bake(type=blender_bake_type)

            # 保存图像
            output_path = os.path.join(output_dir, f"{img_name}.png")
            img.filepath_raw = output_path
            img.file_format = 'PNG'
            img.save()

            baked_maps.append({"type": map_type, "path": output_path, "resolution": resolution})

            # 清理节点
            nodes.remove(tex_node)

    except Exception as e:
        scene.render.engine = original_engine
        return {
            "success": False,
            "error": {"code": "BAKE_FAILED", "message": str(e)}
        }

    # 恢复渲染引擎
    scene.render.engine = original_engine

    return {"success": True, "data": {"baked_maps": baked_maps}}
