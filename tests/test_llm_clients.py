#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OpenAI和Claude客户端的generate_completion功能
"""

import sys
import os
import asyncio
import json
import time
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ai_service.llm_client import OpenAIClient, ClaudeClient
from backend.config import get_config_manager
from backend.models.schema import LLMProvider

class ClientTester:
    """客户端测试类"""
    
    def __init__(self):
        """初始化测试器"""
        self.config_manager = get_config_manager()
        self.test_results = {}
    
    def get_test_prompts(self) -> Dict[str, Dict[str, str]]:
        """获取测试提示词"""
        return {
            "simple_math": {
                "system": "你是一个数学问题分析专家。请分析用户提供的数学题目，并以JSON格式返回分析结果。",
                "user": """请分析以下数学题目：

甲、乙两地相距300公里，汽车从甲地出发，速度为60公里/小时，求5小时后汽车的位置。

请返回JSON格式的分析结果，包含以下字段：
{
  "problem_type": "题目类型",
  "parameters": {
    "distance": "距离",
    "speed": "速度", 
    "time": "时间"
  },
  "solution": "解题思路",
  "answer": "答案"
}"""
            },
            "visualization_task": {
                "system": "你是一个数学可视化代码生成专家。请根据数学题目生成Python可视化代码，返回JSON格式结果。",
                "user": """请为以下数学题目生成可视化代码：

两个相向而行的车辆，甲车速度60km/h，乙车速度80km/h，初始距离480km，求相遇时间和位置。

请返回JSON格式，包含：
{
  "problem_type": "相遇问题",
  "parameters": {"speed1": 60, "speed2": 80, "distance": 480},
  "visualization_code": "Python matplotlib代码",
  "explanation": "可视化说明"
}"""
            }
        }
    
    def get_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取模型配置"""
        return {
            "openai": {
                "model": "kimi-k2-0711-preview",  # 使用Moonshot的模型
                "temperature": 0.3,
                "max_tokens": 2000
            },
            "claude": {
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    
    async def test_openai_client(self) -> Dict[str, Any]:
        """测试OpenAI客户端"""
        print("🔍 测试OpenAI客户端...")
        
        # 获取配置
        api_key = self.config_manager.get_api_key(LLMProvider.OPENAI)
        base_url = self.config_manager.get_base_url(LLMProvider.OPENAI)
        
        if not api_key:
            return {"success": False, "error": "未配置OpenAI API密钥"}
        
        try:
            # 创建客户端
            client = OpenAIClient(api_key=api_key, base_url=base_url)
            
            # 获取测试数据
            prompts = self.get_test_prompts()
            config = self.get_model_configs()["openai"]
            
            results = {}
            
            for test_name, prompt_data in prompts.items():
                print(f"  📝 测试场景: {test_name}")
                
                start_time = time.time()
                response = await client.generate_completion(
                    system_prompt=prompt_data["system"],
                    user_prompt=prompt_data["user"],
                    config=config
                )
                test_time = time.time() - start_time
                
                if response.success:
                    try:
                        # 尝试解析JSON响应
                        content_json = json.loads(response.content)
                        results[test_name] = {
                            "success": True,
                            "response_time": test_time,
                            "content": content_json,
                            "usage": response.usage_stats
                        }
                        print(f"    ✅ 成功 ({test_time:.2f}s)")
                    except json.JSONDecodeError:
                        results[test_name] = {
                            "success": False,
                            "error": "响应不是有效的JSON格式",
                            "raw_content": response.content[:200] + "..."
                        }
                        print(f"    ⚠️ JSON解析失败")
                else:
                    results[test_name] = {
                        "success": False,
                        "error": response.error_message
                    }
                    print(f"    ❌ 失败: {response.error_message}")
            
            return {
                "success": True,
                "client_info": {
                    "base_url": base_url,
                    "model": config["model"]
                },
                "test_results": results
            }
            
        except Exception as e:
            return {"success": False, "error": f"客户端创建失败: {str(e)}"}
    
    async def test_claude_client(self) -> Dict[str, Any]:
        """测试Claude客户端"""
        print("🔍 测试Claude客户端...")
        
        # 获取配置
        api_key = self.config_manager.get_api_key(LLMProvider.CLAUDE)
        base_url = self.config_manager.get_base_url(LLMProvider.CLAUDE)
        
        if not api_key:
            return {"success": False, "error": "未配置Claude API密钥"}
        
        try:
            # 创建客户端
            client = ClaudeClient(api_key=api_key, base_url=base_url)
            
            # 获取测试数据
            prompts = self.get_test_prompts()
            config = self.get_model_configs()["claude"]
            
            results = {}
            
            for test_name, prompt_data in prompts.items():
                print(f"  📝 测试场景: {test_name}")
                
                start_time = time.time()
                response = await client.generate_completion(
                    system_prompt=prompt_data["system"],
                    user_prompt=prompt_data["user"],
                    config=config
                )
                test_time = time.time() - start_time
                
                if response.success:
                    try:
                        # 尝试解析JSON响应
                        content_json = json.loads(response.content)
                        results[test_name] = {
                            "success": True,
                            "response_time": test_time,
                            "content": content_json,
                            "usage": response.usage_stats
                        }
                        print(f"    ✅ 成功 ({test_time:.2f}s)")
                    except json.JSONDecodeError:
                        results[test_name] = {
                            "success": False,
                            "error": "响应不是有效的JSON格式",
                            "raw_content": response.content[:200] + "..."
                        }
                        print(f"    ⚠️ JSON解析失败")
                else:
                    results[test_name] = {
                        "success": False,
                        "error": response.error_message
                    }
                    print(f"    ❌ 失败: {response.error_message}")
            
            return {
                "success": True,
                "client_info": {
                    "base_url": base_url,
                    "model": config["model"]
                },
                "test_results": results
            }
            
        except Exception as e:
            return {"success": False, "error": f"客户端创建失败: {str(e)}"}
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始LLM客户端测试")
        print("=" * 50)
        
        # 显示配置信息
        config_summary = self.config_manager.get_config_summary()
        print("📋 当前配置:")
        for provider, details in config_summary["provider_details"].items():
            if details["api_key_configured"]:
                print(f"  • {provider}: ✅ (Base URL: {details['base_url'] or 'Default'})")
            else:
                print(f"  • {provider}: ❌")
        print()
        
        # 测试OpenAI客户端
        if config_summary["provider_details"]["openai"]["api_key_configured"]:
            openai_result = await self.test_openai_client()
            self.test_results["openai"] = openai_result
            print()
        else:
            print("⏭️ 跳过OpenAI测试（未配置API密钥）\n")
        
        # 测试Claude客户端
        if config_summary["provider_details"]["claude"]["api_key_configured"]:
            claude_result = await self.test_claude_client()
            self.test_results["claude"] = claude_result
            print()
        else:
            print("⏭️ 跳过Claude测试（未配置API密钥）\n")
        
        # 显示测试总结
        self.print_test_summary()
    
    def print_test_summary(self):
        """打印测试总结"""
        print("📊 测试总结")
        print("=" * 50)
        
        for provider, result in self.test_results.items():
            if result["success"]:
                print(f"\n🎯 {provider.upper()} 客户端:")
                print(f"  Base URL: {result['client_info']['base_url']}")
                print(f"  模型: {result['client_info']['model']}")
                
                for test_name, test_result in result["test_results"].items():
                    if test_result["success"]:
                        print(f"  ✅ {test_name}: {test_result['response_time']:.2f}s")
                        if "usage" in test_result:
                            usage = test_result["usage"]
                            print(f"     Token使用: {usage.get('total_tokens', 'N/A')}")
                    else:
                        print(f"  ❌ {test_name}: {test_result['error']}")
            else:
                print(f"\n❌ {provider.upper()} 客户端: {result['error']}")
        
        print("\n🏁 测试完成！")

async def main():
    """主函数"""
    tester = ClientTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
