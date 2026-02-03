"""
资产管理处理器

处理Blender资产库管理命令。
"""

from typing import Any, Dict
import bpy
import os


def handle_mark(params: Dict[str, Any]) -> Dict[str, Any]:
    """标记为资产"""
    object_name = params.get("object_name")
    asset_type = params.get("asset_type", "OBJECT")
    description = params.get("description", "")
    tags = params.get("tags", [])
    
    try:
        if asset_type == "OBJECT":
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {
                    "success": False,
                    "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
                }
            
            obj.asset_mark()
            
            if description:
                obj.asset_data.description = description
            
            for tag in tags:
                obj.asset_data.tags.new(tag)
            
            return {
                "success": True,
                "data": {
                    "name": obj.name,
                    "type": "OBJECT"
                }
            }
        
        elif asset_type == "MATERIAL":
            mat = bpy.data.materials.get(object_name)
            if not mat:
                return {
                    "success": False,
                    "error": {"code": "MATERIAL_NOT_FOUND", "message": f"材质不存在: {object_name}"}
                }
            
            mat.asset_mark()
            
            if description:
                mat.asset_data.description = description
            
            for tag in tags:
                mat.asset_data.tags.new(tag)
            
            return {
                "success": True,
                "data": {
                    "name": mat.name,
                    "type": "MATERIAL"
                }
            }
        
        elif asset_type == "WORLD":
            world = bpy.data.worlds.get(object_name)
            if not world:
                return {
                    "success": False,
                    "error": {"code": "WORLD_NOT_FOUND", "message": f"世界不存在: {object_name}"}
                }
            
            world.asset_mark()
            
            return {
                "success": True,
                "data": {
                    "name": world.name,
                    "type": "WORLD"
                }
            }
        
        return {
            "success": False,
            "error": {"code": "INVALID_TYPE", "message": f"不支持的资产类型: {asset_type}"}
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "ASSET_MARK_ERROR", "message": str(e)}
        }


def handle_catalog(params: Dict[str, Any]) -> Dict[str, Any]:
    """目录操作"""
    action = params.get("action", "LIST")
    catalog_name = params.get("catalog_name")
    parent_catalog = params.get("parent_catalog")
    
    try:
        if action == "LIST":
            # 列出所有资产
            assets = {
                "objects": [],
                "materials": [],
                "worlds": []
            }
            
            for obj in bpy.data.objects:
                if obj.asset_data:
                    assets["objects"].append({
                        "name": obj.name,
                        "description": obj.asset_data.description if obj.asset_data else ""
                    })
            
            for mat in bpy.data.materials:
                if mat.asset_data:
                    assets["materials"].append({
                        "name": mat.name,
                        "description": mat.asset_data.description if mat.asset_data else ""
                    })
            
            for world in bpy.data.worlds:
                if world.asset_data:
                    assets["worlds"].append({
                        "name": world.name
                    })
            
            return {
                "success": True,
                "data": assets
            }
        
        elif action == "CREATE":
            # Blender的资产目录需要通过资产浏览器创建
            return {
                "success": True,
                "data": {
                    "note": "Catalog creation requires Asset Browser. Use Blender UI."
                }
            }
        
        elif action == "DELETE":
            return {
                "success": True,
                "data": {
                    "note": "Catalog deletion requires Asset Browser. Use Blender UI."
                }
            }
        
        return {
            "success": False,
            "error": {"code": "INVALID_ACTION", "message": f"未知操作: {action}"}
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CATALOG_ERROR", "message": str(e)}
        }


def handle_import(params: Dict[str, Any]) -> Dict[str, Any]:
    """导入资产"""
    filepath = params.get("filepath")
    asset_name = params.get("asset_name")
    link = params.get("link", False)
    
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error": {"code": "FILE_NOT_FOUND", "message": f"文件不存在: {filepath}"}
        }
    
    try:
        # 使用 bpy.ops.wm.append 或 link
        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            # 尝试导入对象
            if asset_name in data_from.objects:
                data_to.objects = [asset_name]
            # 尝试导入材质
            elif asset_name in data_from.materials:
                data_to.materials = [asset_name]
            # 尝试导入集合
            elif asset_name in data_from.collections:
                data_to.collections = [asset_name]
            else:
                return {
                    "success": False,
                    "error": {"code": "ASSET_NOT_FOUND", "message": f"资产不存在: {asset_name}"}
                }
        
        # 链接到场景
        for obj in data_to.objects:
            if obj:
                bpy.context.collection.objects.link(obj)
        
        for coll in data_to.collections:
            if coll:
                bpy.context.scene.collection.children.link(coll)
        
        return {
            "success": True,
            "data": {
                "asset_name": asset_name,
                "linked": link
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "IMPORT_ERROR", "message": str(e)}
        }


def handle_search(params: Dict[str, Any]) -> Dict[str, Any]:
    """搜索资产"""
    query = params.get("query", "").lower()
    asset_type = params.get("asset_type")
    
    try:
        results = []
        
        if not asset_type or asset_type == "OBJECT":
            for obj in bpy.data.objects:
                if obj.asset_data and query in obj.name.lower():
                    results.append({
                        "name": obj.name,
                        "type": "OBJECT",
                        "description": obj.asset_data.description if obj.asset_data else ""
                    })
        
        if not asset_type or asset_type == "MATERIAL":
            for mat in bpy.data.materials:
                if mat.asset_data and query in mat.name.lower():
                    results.append({
                        "name": mat.name,
                        "type": "MATERIAL",
                        "description": mat.asset_data.description if mat.asset_data else ""
                    })
        
        if not asset_type or asset_type == "WORLD":
            for world in bpy.data.worlds:
                if world.asset_data and query in world.name.lower():
                    results.append({
                        "name": world.name,
                        "type": "WORLD"
                    })
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "count": len(results)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "SEARCH_ERROR", "message": str(e)}
        }


def handle_preview(params: Dict[str, Any]) -> Dict[str, Any]:
    """生成资产预览图"""
    object_name = params.get("object_name")
    
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {
            "success": False,
            "error": {"code": "OBJECT_NOT_FOUND", "message": f"对象不存在: {object_name}"}
        }
    
    try:
        if not obj.asset_data:
            return {
                "success": False,
                "error": {"code": "NOT_ASSET", "message": "对象未标记为资产"}
            }
        
        # 生成预览
        obj.asset_generate_preview()
        
        return {
            "success": True,
            "data": {
                "name": obj.name,
                "preview_generated": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "PREVIEW_ERROR", "message": str(e)}
        }


def handle_clear(params: Dict[str, Any]) -> Dict[str, Any]:
    """清除资产标记"""
    object_name = params.get("object_name")
    
    # 尝试在不同数据块中查找
    data_block = None
    
    if object_name in bpy.data.objects:
        data_block = bpy.data.objects[object_name]
    elif object_name in bpy.data.materials:
        data_block = bpy.data.materials[object_name]
    elif object_name in bpy.data.worlds:
        data_block = bpy.data.worlds[object_name]
    
    if not data_block:
        return {
            "success": False,
            "error": {"code": "NOT_FOUND", "message": f"未找到: {object_name}"}
        }
    
    try:
        if data_block.asset_data:
            data_block.asset_clear()
            
            return {
                "success": True,
                "data": {
                    "name": object_name,
                    "cleared": True
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "name": object_name,
                    "note": "Not an asset"
                }
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CLEAR_ERROR", "message": str(e)}
        }
