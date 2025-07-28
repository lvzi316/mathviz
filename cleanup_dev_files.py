#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发文件清理脚本
清理开发过程中生成的临时文件和测试脚本
"""

import os
import shutil
from pathlib import Path

def clean_test_scripts():
    """清理旧的测试脚本"""
    print("🧹 清理测试脚本...")
    
    # 要删除的测试脚本
    old_test_files = [
        "diagnose_test.py",
        "test_ai_system.py", 
        "test_core_functions.py"
    ]
    
    removed_files = []
    for file in old_test_files:
        if os.path.exists(file):
            os.remove(file)
            removed_files.append(file)
            print(f"   ✅ 删除: {file}")
    
    if not removed_files:
        print("   ℹ️ 没有找到旧的测试脚本")
    
    return removed_files

def clean_temporary_outputs():
    """清理临时输出文件"""
    print("🧹 清理临时输出文件...")
    
    # 清理output目录中的临时文件
    output_dir = "output"
    if os.path.exists(output_dir):
        files_to_keep = [
            "meeting_problem.png",  # 保留示例文件
            "chase_problem.png"     # 保留示例文件
        ]
        
        removed_count = 0
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path) and file not in files_to_keep:
                # 删除UUID命名的临时图片和文本文件
                if (len(file.split('.')[0]) == 36 and '-' in file) or file.endswith('.txt'):
                    os.remove(file_path)
                    removed_count += 1
        
        print(f"   ✅ 删除 {removed_count} 个临时输出文件")
        print(f"   ℹ️ 保留示例文件: {', '.join(files_to_keep)}")
    else:
        print("   ℹ️ output目录不存在")

def clean_python_cache():
    """清理Python缓存文件"""
    print("🧹 清理Python缓存...")
    
    cache_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        ".pytest_cache"
    ]
    
    removed_dirs = []
    for root, dirs, files in os.walk("."):
        # 删除__pycache__目录
        if "__pycache__" in dirs:
            cache_dir = os.path.join(root, "__pycache__")
            shutil.rmtree(cache_dir)
            removed_dirs.append(cache_dir)
            dirs.remove("__pycache__")  # 不再遍历已删除的目录
        
        # 删除.pytest_cache目录
        if ".pytest_cache" in dirs:
            cache_dir = os.path.join(root, ".pytest_cache")
            shutil.rmtree(cache_dir)
            removed_dirs.append(cache_dir)
            dirs.remove(".pytest_cache")
    
    if removed_dirs:
        print(f"   ✅ 删除缓存目录: {len(removed_dirs)}个")
    else:
        print("   ℹ️ 没有找到Python缓存文件")

def clean_manim_outputs():
    """清理Manim输出文件"""
    print("🧹 清理Manim输出...")
    
    manim_dirs = ["media", "videos"]
    removed_dirs = []
    
    for dir_name in manim_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            removed_dirs.append(dir_name)
    
    if removed_dirs:
        print(f"   ✅ 删除Manim输出目录: {', '.join(removed_dirs)}")
    else:
        print("   ℹ️ 没有找到Manim输出目录")

def clean_log_files():
    """清理日志文件"""
    print("🧹 清理日志文件...")
    
    log_patterns = ["*.log", "*.out", "*.err"]
    removed_files = []
    
    for pattern in log_patterns:
        import glob
        for file in glob.glob(pattern):
            os.remove(file)
            removed_files.append(file)
    
    if removed_files:
        print(f"   ✅ 删除日志文件: {', '.join(removed_files)}")
    else:
        print("   ℹ️ 没有找到日志文件")

def organize_documentation():
    """整理文档文件"""
    print("📚 整理文档文件...")
    
    # 检查是否有重复的README文件
    readme_files = ["README.md", "README_NEW.md"]
    existing_readmes = [f for f in readme_files if os.path.exists(f)]
    
    if len(existing_readmes) > 1:
        print(f"   ⚠️ 发现多个README文件: {', '.join(existing_readmes)}")
        print("   💡 建议合并为一个统一的README.md")
    
    # 检查临时文档
    temp_docs = ["test.md", "CLEANUP_SUMMARY.md"]
    existing_temp = [f for f in temp_docs if os.path.exists(f)]
    
    if existing_temp:
        print(f"   ℹ️ 发现临时文档: {', '.join(existing_temp)}")
        print("   💡 考虑将内容整合到正式文档中")

def create_gitignore_if_needed():
    """确保.gitignore文件完整"""
    print("📝 检查.gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.venv
env/
venv/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Outputs
output/*.png
output/*.jpg
output/*.txt
!output/meeting_problem.png
!output/chase_problem.png

# Manim
media/
videos/

# Logs
*.log
*.out
*.err

# macOS
.DS_Store

# Temporary files
temp/
tmp/
"""
    
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r", encoding="utf-8") as f:
            existing_content = f.read()
        
        # 检查是否需要更新
        new_lines = [line for line in gitignore_content.strip().split('\n') 
                    if line and not line.startswith('#') and line not in existing_content]
        
        if new_lines:
            print(f"   💡 建议添加到.gitignore: {', '.join(new_lines[:3])}...")
    else:
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print("   ✅ 创建.gitignore文件")

def main():
    """主清理函数"""
    print("🚀 开始清理开发临时文件")
    print("="*50)
    
    # 执行清理任务
    clean_test_scripts()
    clean_temporary_outputs()
    clean_python_cache()
    clean_manim_outputs()
    clean_log_files()
    organize_documentation()
    create_gitignore_if_needed()
    
    print("="*50)
    print("✅ 清理完成！")
    print("\n📋 清理总结:")
    print("  - 删除旧的测试脚本")
    print("  - 清理临时输出文件") 
    print("  - 删除Python缓存")
    print("  - 整理项目结构")
    print("\n💡 新的测试脚本位置: tests/test_system.py")
    print("💡 运行测试: python tests/test_system.py")

if __name__ == "__main__":
    main()
