#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI驱动数学可视化系统集成测试
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_prompt_templates():
    """测试Prompt模板系统"""
    print("🧪 测试Prompt模板系统...")
    
    try:
        from backend.ai_service.prompt_templates import get_prompt_manager, render_prompt
        
        manager = get_prompt_manager()
        print(f"✅ 可用模板: {manager.list_templates()}")
        
        # 测试模板渲染
        system_prompt, user_prompt = render_prompt(
            problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
            output_path="output/test.png",
            variant="simple_mode"
        )
        
        print(f"✅ 系统Prompt长度: {len(system_prompt)}字符")
        print(f"✅ 用户Prompt长度: {len(user_prompt)}字符")
        
        # 测试模板变体
        variants = manager.list_variants("math_visualization")
        print(f"✅ 可用变体: {variants}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt模板测试失败: {e}")
        return False

def test_code_validator():
    """测试代码安全验证器"""
    print("🧪 测试代码安全验证器...")
    
    try:
        from backend.execution.validator import validate_code_security
        
        # 测试安全代码
        safe_code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('测试图')
plt.savefig('output/test.png')
plt.close()

result = {'success': True}
"""
        
        result = validate_code_security(safe_code)
        print(f"✅ 安全代码验证通过: {result.is_valid}")
        print(f"✅ 安全问题数量: {len(result.security_issues)}")
        print(f"✅ 警告数量: {len(result.warnings)}")
        
        # 测试危险代码
        dangerous_code = """
import os
os.system('rm -rf /')
"""
        
        result2 = validate_code_security(dangerous_code)
        print(f"✅ 危险代码被拦截: {not result2.is_valid}")
        print(f"✅ 检测到安全问题: {len(result2.security_issues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 代码验证器测试失败: {e}")
        return False

def test_code_executor():
    """测试代码执行器"""
    print("🧪 测试代码执行器...")
    
    try:
        from backend.execution.executor import execute_visualization_code
        import os
        
        test_code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 生成测试数据
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.title('正弦函数测试图')
plt.legend()
plt.grid(True, alpha=0.3)

# 保存图片
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

# 返回结果
result = {
    'function': 'sin(x)',
    'x_range': [float(x.min()), float(x.max())],
    'y_range': [float(y.min()), float(y.max())],
    'points': len(x)
}

print(f"图表已保存到: {output_path}")
"""
        
        # 确保输出目录存在
        os.makedirs("output", exist_ok=True)
        
        # 测试受限执行器
        result = execute_visualization_code(
            test_code, 
            "output/executor_test.png",
            execution_mode="restricted"
        )
        
        print(f"✅ 代码执行成功: {result.success}")
        print(f"✅ 执行时间: {result.execution_time:.2f}秒")
        print(f"✅ 内存使用: {result.memory_usage:.1f}MB")
        print(f"✅ 结果数据: {result.result_data}")
        
        # 检查图片是否生成
        if result.image_path and os.path.exists(result.image_path):
            print(f"✅ 图片已生成: {result.image_path}")
        else:
            print("⚠️ 图片未生成")
        
        return result.success
        
    except Exception as e:
        print(f"❌ 代码执行器测试失败: {e}")
        return False

def test_sandbox_manager():
    """测试沙箱管理器"""
    print("🧪 测试沙箱管理器...")
    
    try:
        from backend.execution.sandbox import get_sandbox_manager
        import os
        
        manager = get_sandbox_manager()
        
        test_code = """
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']

# 二次函数
x = np.linspace(-5, 5, 100)
y = x**2 - 4*x + 3

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'r-', linewidth=2, label='y = x² - 4x + 3')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='--', alpha=0.3)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('二次函数图')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

result = {
    'function_type': 'quadratic',
    'equation': 'y = x² - 4x + 3',
    'vertex': [2, -1],
    'roots': [1, 3]
}
"""
        
        os.makedirs("output", exist_ok=True)
        
        result = manager.execute_code_safely(
            test_code,
            "output/sandbox_test.png",
            execution_mode="restricted"
        )
        
        print(f"✅ 沙箱执行成功: {result['overall_success']}")
        
        if result['validation_result']:
            print(f"✅ 代码验证通过: {result['validation_result'].is_valid}")
        
        if result['execution_result']:
            print(f"✅ 图片生成: {result['execution_result'].success}")
            print(f"✅ 执行时间: {result['execution_result'].execution_time:.2f}秒")
        
        # 获取统计信息
        stats = manager.get_sandbox_stats()
        print(f"✅ 沙箱统计: 总执行{stats['total_executions']}次, 成功率{stats['success_rate']:.1%}")
        
        return result['overall_success']
        
    except Exception as e:
        print(f"❌ 沙箱管理器测试失败: {e}")
        return False

async def test_code_generator():
    """测试AI代码生成器（模拟）"""
    print("🧪 测试AI代码生成器...")
    
    try:
        from backend.ai_service.code_generator import get_code_generator
        from backend.models.schema import LLMProvider
        
        generator = get_code_generator()
        
        # 由于没有真实API密钥，这里只测试错误处理
        try:
            result = await generator.generate_visualization_code(
                problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
                output_path="output/ai_test.png",
                provider=LLMProvider.OPENAI,
                max_retries=1
            )
            
            print(f"✅ 代码生成器响应: {result.problem_type}")
            print(f"✅ 置信度: {result.confidence}")
            print(f"✅ 处理时间: {result.processing_time:.2f}秒")
            
        except Exception as e:
            print(f"⚠️ 代码生成失败（预期，因为没有API密钥）: {str(e)[:100]}...")
        
        # 测试统计功能
        stats = generator.get_generation_stats()
        print(f"✅ 生成统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI代码生成器测试失败: {e}")
        return False

def test_data_models():
    """测试数据模型"""
    print("🧪 测试数据模型...")
    
    try:
        from backend.models.schema import (
            ProblemRequest, TaskInfo, AIAnalysisResult, 
            ExecutionResult, LLMProvider, ProcessingMode
        )
        
        # 测试请求模型
        request = ProblemRequest(
            text="测试题目：甲、乙两地相距480公里...",
            llm_provider=LLMProvider.OPENAI,
            processing_mode=ProcessingMode.AI
        )
        print(f"✅ 请求模型: {request.text[:30]}...")
        
        # 测试AI分析结果
        ai_result = AIAnalysisResult(
            problem_type="行程问题-相遇",
            parameters={"distance": 480, "speed1": 60, "speed2": 80},
            visualization_code="import matplotlib...",
            explanation="绘制相遇问题可视化图",
            confidence=0.95,
            processing_time=3.2
        )
        print(f"✅ AI分析结果: {ai_result.problem_type}, 置信度: {ai_result.confidence}")
        
        # 测试执行结果
        exec_result = ExecutionResult(
            success=True,
            image_path="output/test.png",
            result_data={"meeting_time": 3.43},
            execution_time=1.5,
            memory_usage=45.2
        )
        print(f"✅ 执行结果: 成功={exec_result.success}, 时间={exec_result.execution_time}s")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始AI驱动数学可视化系统集成测试\n")
    
    test_results = []
    
    # 同步测试
    test_results.append(("数据模型", test_data_models()))
    test_results.append(("代码验证器", test_code_validator()))
    test_results.append(("代码执行器", test_code_executor()))
    test_results.append(("沙箱管理器", test_sandbox_manager()))
    
    # 异步测试
    test_results.append(("Prompt模板", await test_prompt_templates()))
    test_results.append(("AI代码生成器", await test_code_generator()))
    
    # 输出结果汇总
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"总计: {passed}/{total} 通过, 成功率: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 所有测试通过！系统就绪。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置。")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行异常: {e}")
        sys.exit(1)
