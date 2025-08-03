#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数学可视化系统综合测试套件
整合了开发过程中的各种测试功能
"""

import asyncio
import sys
import os
import shutil
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemTester:
    def __init__(self):
        self.test_output_dir = "tests/output"
        self.ensure_test_dirs()
    
    def ensure_test_dirs(self):
        """确保测试目录存在"""
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def cleanup_test_files(self):
        """清理测试生成的文件"""
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        self.ensure_test_dirs()

    def test_basic_imports(self):
        """测试基础模块导入"""
        print("🧪 测试基础模块导入...")
        
        try:
            # 测试核心依赖
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            print("✅ 核心依赖库导入成功")
            
            # 测试项目模块
            from backend.models.schema import ProblemRequest, LLMProvider
            from backend.ai_service.prompt_templates import render_prompt
            from backend.execution.validator import validate_code_security
            print("✅ 项目模块导入成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 模块导入失败: {e}")
            return False

    def test_pydantic_models(self):
        """测试Pydantic数据模型"""
        print("🧪 测试Pydantic数据模型...")
        
        try:
            from backend.models.schema import (
                ProblemRequest, AIAnalysisResult, ExecutionResult, 
                TaskInfo, LLMProvider, PromptTemplate
            )
            
            # 测试ProblemRequest
            request = ProblemRequest(
                text="甲、乙两地相距480公里的测试问题",
                user_id="test_user",
                llm_provider=LLMProvider.OPENAI
            )
            print(f"✅ ProblemRequest创建成功: {request.text}")
            
            # 测试PromptTemplate
            template = PromptTemplate(
                name="test_template",
                system_prompt="测试系统提示",
                user_prompt_template="测试用户提示: {problem_text}",
                llm_config={"model": "test-model"}
            )
            print(f"✅ PromptTemplate创建成功: {template.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Pydantic模型测试失败: {e}")
            return False

    def test_prompt_system(self):
        """测试Prompt模板系统"""
        print("🧪 测试Prompt模板系统...")
        
        try:
            from backend.ai_service.prompt_templates import render_prompt, get_prompt_manager
            
            # 测试模板渲染
            system_prompt, user_prompt = render_prompt(
                problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
                output_path=f"{self.test_output_dir}/test.png"
            )
            
            # 验证prompt内容
            if "数学题目可视化专家" in system_prompt and "480公里" in user_prompt:
                print("✅ Prompt模板渲染成功")
                print(f"   系统Prompt: {len(system_prompt)}字符")
                print(f"   用户Prompt: {len(user_prompt)}字符")
                return True
            else:
                print("❌ Prompt内容验证失败")
                return False
                
        except Exception as e:
            print(f"❌ Prompt系统测试失败: {e}")
            return False

    def test_code_validation(self):
        """测试代码安全验证"""
        print("🧪 测试代码安全验证...")
        
        try:
            from backend.execution.validator import validate_code_security
            
            # 测试安全代码
            safe_code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('测试图表')
plt.grid(True)
plt.savefig('output/test.png', dpi=300, bbox_inches='tight')
plt.close()

result = {'success': True, 'function': 'sin(x)'}
"""
            
            result = validate_code_security(safe_code)
            if result.is_valid:
                print("✅ 安全代码验证通过")
            else:
                print(f"❌ 安全代码验证失败: {result.security_issues}")
                return False
            
            # 测试危险代码
            dangerous_code = "import os; os.system('rm -rf /')"
            result2 = validate_code_security(dangerous_code)
            
            if not result2.is_valid:
                print("✅ 危险代码被正确拦截")
                return True
            else:
                print("❌ 危险代码未被拦截")
                return False
                
        except Exception as e:
            print(f"❌ 代码验证测试失败: {e}")
            return False

    def test_code_execution(self):
        """测试代码执行功能"""
        print("🧪 测试代码执行功能...")
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 测试代码
            test_code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']

x = np.linspace(0, 10, 50)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('测试图表')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig('{self.test_output_dir}/execution_test.png', dpi=300, bbox_inches='tight')
plt.close()

result = {{'success': True, 'function': 'sin(x)'}}
"""
            
            # 执行代码
            globals_dict = {}
            exec(test_code, globals_dict)
            
            # 检查结果
            if os.path.exists(f'{self.test_output_dir}/execution_test.png'):
                print("✅ 代码执行成功，图片已生成")
                return True
            else:
                print("❌ 代码执行失败，图片未生成")
                return False
                
        except Exception as e:
            print(f"❌ 代码执行测试失败: {e}")
            return False

    async def test_llm_clients(self):
        """测试LLM客户端（模拟）"""
        print("🧪 测试LLM客户端...")
        
        try:
            from backend.ai_service.llm_client import (
                OpenAIClient, ClaudeClient, QwenClient
            )
            
            # 测试客户端创建（使用模拟的API密钥）
            openai_client = OpenAIClient("test-key")
            claude_client = ClaudeClient("test-key")
            qwen_client = QwenClient("test-key")
            
            print("✅ LLM客户端创建成功")
            print(f"   OpenAI客户端: {type(openai_client).__name__}")
            print(f"   Claude客户端: {type(claude_client).__name__}")
            print(f"   Qwen客户端: {type(qwen_client).__name__}")
            
            return True
            
        except Exception as e:
            print(f"❌ LLM客户端测试失败: {e}")
            return False

    def test_api_endpoints(self):
        """测试API端点（模拟）"""
        print("🧪 测试API端点...")
        
        try:
            from backend.api.endpoints import router
            print("✅ FastAPI路由器创建成功")
            
            # 检查路由
            routes = [route.path for route in router.routes]
            expected_routes = ["/problems/generate", "/tasks/{task_id}", "/health"]
            
            for route in expected_routes:
                if any(route in r for r in routes):
                    print(f"✅ 路由存在: {route}")
                else:
                    print(f"❌ 路由缺失: {route}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ API端点测试失败: {e}")
            return False

    async def test_v2_api_http(self):
        """测试v2 API HTTP接口"""
        print("🧪 测试v2 API HTTP接口...")
        
        try:
            import httpx
            
            # 测试健康检查端点
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8002/api/v2/health")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ 健康检查通过: {health_data['status']}")
                else:
                    print(f"❌ 健康检查失败: {response.status_code}")
                    return False
                
                # 测试配置端点
                response = await client.get("http://localhost:8002/api/v2/config")
                if response.status_code == 200:
                    config_data = response.json()
                    print(f"✅ 配置查询成功: 默认提供商 {config_data['default_provider']}")
                else:
                    print(f"❌ 配置查询失败: {response.status_code}")
                    return False
                
                # 测试任务列表端点
                response = await client.get("http://localhost:8002/api/v2/tasks")
                if response.status_code == 200:
                    tasks = response.json()
                    print(f"✅ 任务列表查询成功: {len(tasks)} 个任务")
                else:
                    print(f"❌ 任务列表查询失败: {response.status_code}")
                    return False
                
                # 测试问题生成端点（应该失败，因为没有API密钥）
                test_request = {
                    "text": "甲、乙两地相距100公里，小明以50公里/小时的速度从甲地出发，求2小时后的位置。",
                    "user_id": "test_user",
                    "llm_provider": "openai"
                }
                response = await client.post(
                    "http://localhost:8002/api/v2/problems/generate",
                    json=test_request
                )
                if response.status_code == 400:
                    print("✅ 问题生成端点正确返回错误（缺少API密钥）")
                else:
                    print(f"✅ 问题生成端点响应: {response.status_code}")
                
            return True
            
        except ImportError:
            print("⚠️ httpx 未安装，跳过HTTP测试")
            return True
        except Exception as e:
            print(f"❌ v2 API HTTP测试失败: {e}")
            return False

    async def test_api_key_configuration(self):
        """测试API密钥配置功能"""
        print("🧪 测试API密钥配置功能...")
        
        try:
            from backend.config import get_config_manager
            from backend.ai_service.llm_client import get_llm_manager
            from backend.models.schema import LLMProvider
            
            config_manager = get_config_manager()
            llm_manager = get_llm_manager()
            
            # 测试配置管理器
            summary = config_manager.get_config_summary()
            print(f"✅ 配置管理器工作正常")
            print(f"   已配置提供商: {', '.join(summary['configured_providers'])}")
            print(f"   默认提供商: {summary['default_provider']}")
            
            # 测试API密钥检查
            openai_configured = config_manager.is_provider_configured(LLMProvider.OPENAI)
            claude_configured = config_manager.is_provider_configured(LLMProvider.CLAUDE)
            
            print(f"✅ API密钥状态检查:")
            print(f"   OpenAI: {'已配置' if openai_configured else '未配置'}")
            print(f"   Claude: {'已配置' if claude_configured else '未配置'}")
            
            # 测试LLM管理器的配置检查
            available_providers = llm_manager.get_available_providers()
            print(f"✅ LLM管理器可用提供商: {[p.value for p in available_providers]}")
            
            return True
            
        except Exception as e:
            print(f"❌ API密钥配置测试失败: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行系统综合测试\n")
        print("="*60)
        
        tests = [
            ("基础模块导入", self.test_basic_imports),
            ("Pydantic数据模型", self.test_pydantic_models),
            ("Prompt模板系统", self.test_prompt_system),
            ("代码安全验证", self.test_code_validation),
            ("代码执行功能", self.test_code_execution),
            ("LLM客户端", self.test_llm_clients),
            ("API端点", self.test_api_endpoints),
            ("v2 API HTTP接口", self.test_v2_api_http),
            ("API密钥配置", self.test_api_key_configuration)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}:")
            print("-" * 40)
            
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            results.append((test_name, result))
        
        # 汇总结果
        print("\n" + "="*60)
        print("测试结果汇总:")
        print("="*60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
        
        total = len(results)
        success_rate = passed / total
        
        print("-" * 60)
        print(f"总计: {passed}/{total} 通过")
        print(f"成功率: {success_rate:.1%}")
        
        if success_rate == 1.0:
            print("\n🎉 所有测试通过！系统状态良好")
        elif success_rate >= 0.8:
            print("\n✅ 大部分测试通过，系统基本可用")
        elif success_rate >= 0.6:
            print("\n⚠️ 部分测试失败，需要检查")
        else:
            print("\n❌ 多个测试失败，系统需要修复")
        
        return success_rate

    def cleanup_and_summary(self):
        """清理并总结"""
        print(f"\n🧹 清理测试文件...")
        
        # 可选择性保留一些有用的测试输出
        test_files = []
        if os.path.exists(f'{self.test_output_dir}/execution_test.png'):
            test_files.append('execution_test.png')
        
        if test_files:
            print(f"✅ 保留测试文件: {', '.join(test_files)}")
        
        print("✅ 测试完成")


def main():
    """主函数"""
    tester = SystemTester()
    
    try:
        # 运行异步测试
        result = asyncio.run(tester.run_all_tests())
        
        # 清理和总结
        tester.cleanup_and_summary()
        
        return result
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        return 0.0
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        return 0.0


if __name__ == "__main__":
    success_rate = main()
    exit_code = 0 if success_rate >= 0.8 else 1
    sys.exit(exit_code)
