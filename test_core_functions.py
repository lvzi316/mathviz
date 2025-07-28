#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证核心功能的简化测试
"""

def test_basic_code_execution():
    """测试基础代码执行功能"""
    print("🧪 测试基础代码执行...")
    
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        import os
        
        # 确保输出目录存在
        os.makedirs("output", exist_ok=True)
        
        # 直接执行测试代码
        test_code = """
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

plt.savefig('output/direct_test.png', dpi=300, bbox_inches='tight')
plt.close()

result = {'success': True, 'function': 'sin(x)'}
"""
        
        # 直接执行
        globals_dict = {'output_path': 'output/direct_test.png'}
        exec(test_code, globals_dict)
        
        # 检查结果
        if os.path.exists('output/direct_test.png'):
            print("✅ 直接代码执行成功，图片已生成")
            return True
        else:
            print("❌ 直接代码执行失败，图片未生成")
            return False
            
    except Exception as e:
        print(f"❌ 直接代码执行异常: {e}")
        return False

def test_prompt_rendering():
    """测试prompt模板渲染"""
    print("🧪 测试Prompt渲染...")
    
    try:
        from backend.ai_service.prompt_templates import render_prompt
        
        system_prompt, user_prompt = render_prompt(
            problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
            output_path="output/test.png"
        )
        
        print(f"✅ 系统Prompt: {len(system_prompt)}字符")
        print(f"✅ 用户Prompt: {len(user_prompt)}字符")
        
        # 检查关键内容
        if "数学题目可视化专家" in system_prompt and "480公里" in user_prompt:
            print("✅ Prompt内容正确")
            return True
        else:
            print("❌ Prompt内容不正确")
            return False
            
    except Exception as e:
        print(f"❌ Prompt渲染失败: {e}")
        return False

def test_code_validation():
    """测试代码安全验证"""
    print("🧪 测试代码验证...")
    
    try:
        from backend.execution.validator import validate_code_security
        
        # 测试安全代码
        safe_code = """
import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.figure()
plt.plot(x, y)
plt.savefig('output/test.png')
plt.close()
result = {'success': True}
"""
        
        result = validate_code_security(safe_code)
        
        if result.is_valid:
            print("✅ 安全代码验证通过")
        else:
            print(f"❌ 安全代码验证失败: {result.security_issues}")
            
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
        print(f"❌ 代码验证失败: {e}")
        return False

def main():
    """运行核心功能验证"""
    print("🚀 验证AI数学可视化系统核心功能\n")
    
    tests = [
        ("基础代码执行", test_basic_code_execution),
        ("Prompt模板渲染", test_prompt_rendering), 
        ("代码安全验证", test_code_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{test_name}:")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # 汇总结果
    print("="*50)
    print("核心功能验证结果:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    total = len(results)
    print("="*50)
    print(f"总计: {passed}/{total} 通过, 成功率: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 核心功能验证全部通过！")
        print("📝 系统基础架构就绪，可以开始集成LLM API")
    elif passed >= total * 0.7:
        print("✅ 大部分核心功能正常，系统基本可用")
    else:
        print("⚠️ 多个核心功能异常，需要进一步检查")

if __name__ == "__main__":
    main()
