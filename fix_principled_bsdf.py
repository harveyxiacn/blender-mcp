"""
修复所有handler文件中的Principled BSDF节点查找问题
Fix Principled BSDF node lookup for Blender 5.0 compatibility
"""

import os
import re

# 需要修复的文件和模式
files_to_fix = [
    "addon/blender_mcp_addon/handlers/material.py",
    "addon/blender_mcp_addon/handlers/character.py",
    "addon/blender_mcp_addon/handlers/ai_generation.py",
    "addon/blender_mcp_addon/handlers/vr_ar.py",
    "addon/blender_mcp_addon/handlers/substance.py",
    "addon/blender_mcp_addon/handlers/zbrush.py",
    "addon/blender_mcp_addon/handlers/character_template.py",
]

# 辅助函数代码
helper_function = '''
def get_principled_bsdf(nodes):
    """获取Principled BSDF节点，兼容不同Blender版本"""
    # 先尝试按名称查找
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        return bsdf
    # 再按类型查找
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    return None

'''

def fix_file(filepath):
    """修复单个文件"""
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 检查是否已经有辅助函数
    if 'def get_principled_bsdf' not in content:
        # 在import bpy后添加辅助函数
        import_pattern = r'(import bpy\n)'
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, r'\1\n' + helper_function, content, count=1)
    
    # 替换所有的 nodes.get("Principled BSDF") 为 get_principled_bsdf(nodes)
    patterns = [
        (r'(\w+)\.node_tree\.nodes\.get\("Principled BSDF"\)', r'get_principled_bsdf(\1.node_tree.nodes)'),
        (r'nodes\.get\("Principled BSDF"\)', r'get_principled_bsdf(nodes)'),
        (r'nodes\["Principled BSDF"\]', r'get_principled_bsdf(nodes)'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已修复: {filepath}")
        return True
    else:
        print(f"无需修复: {filepath}")
        return False


def main():
    print("="*60)
    print("修复 Principled BSDF 节点查找问题")
    print("="*60)
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{len(files_to_fix)} 个文件")


if __name__ == "__main__":
    main()
