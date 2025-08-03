#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API密钥设置工具
"""

import os
import sys
from backend.models.schema import LLMProvider
from backend.config import get_config_manager

def set_api_keys_interactive():
    """交互式设置API密钥"""
    print("🔑 API密钥配置工具")
    print("=" * 50)
    
    config_manager = get_config_manager()
    
    # OpenAI API密钥
    print("\n📝 设置OpenAI API密钥:")
    current_openai = config_manager.get_api_key(LLMProvider.OPENAI)
    if current_openai:
        print(f"   当前: {current_openai[:10]}...")
    
    openai_key = input("   请输入OpenAI API密钥 (留空跳过): ").strip()
    if openai_key:
        config_manager.set_api_key(LLMProvider.OPENAI, openai_key)
        print("   ✅ OpenAI API密钥已设置")
    
    # Claude API密钥
    print("\n📝 设置Claude API密钥:")
    current_claude = config_manager.get_api_key(LLMProvider.CLAUDE)
    if current_claude:
        print(f"   当前: {current_claude[:10]}...")
    
    claude_key = input("   请输入Claude API密钥 (留空跳过): ").strip()
    if claude_key:
        config_manager.set_api_key(LLMProvider.CLAUDE, claude_key)
        print("   ✅ Claude API密钥已设置")
    
    # 显示配置摘要
    print("\n📊 配置摘要:")
    summary = config_manager.get_config_summary()
    print(f"   已配置提供商: {', '.join(summary['configured_providers'])}")
    print(f"   默认提供商: {summary['default_provider']}")
    print(f"   总计配置: {summary['total_configured']}")
    
    return summary

def create_env_file(openai_key: str = None, claude_key: str = None):
    """创建.env文件"""
    env_content = """# AI模型API密钥配置
# 请替换为你的实际API密钥

"""
    
    if openai_key:
        env_content += f"OPENAI_API_KEY={openai_key}\n"
    else:
        env_content += "OPENAI_API_KEY=sk-your-openai-api-key-here\n"
    
    if claude_key:
        env_content += f"CLAUDE_API_KEY={claude_key}\n"
    else:
        env_content += "CLAUDE_API_KEY=sk-ant-your-claude-api-key-here\n"
    
    env_content += """
# 默认LLM提供商 (openai, claude, qwen)
DEFAULT_LLM_PROVIDER=openai

# 其他配置
ENVIRONMENT=development
DEBUG=true
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env文件已创建")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "interactive":
            set_api_keys_interactive()
        elif command == "create-env":
            create_env_file()
        elif command == "status":
            config_manager = get_config_manager()
            summary = config_manager.get_config_summary()
            print("📊 当前配置状态:")
            print(f"   已配置提供商: {', '.join(summary['configured_providers']) if summary['configured_providers'] else '无'}")
            print(f"   默认提供商: {summary['default_provider']}")
            print(f"   验证结果: {summary['validation']}")
        else:
            print("❌ 未知命令")
            print_usage()
    else:
        print_usage()

def print_usage():
    """打印使用说明"""
    print("""
🔑 API密钥设置工具

使用方法:
    python setup_api_keys.py interactive    # 交互式设置API密钥
    python setup_api_keys.py create-env     # 创建.env文件模板
    python setup_api_keys.py status         # 查看当前配置状态

注意事项:
1. API密钥可以通过环境变量或.env文件设置
2. 支持OpenAI和Claude两种模型
3. 设置后重启服务器生效
    """)

if __name__ == "__main__":
    main()
