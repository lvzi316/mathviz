#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙箱管理器
统一管理不同类型的沙箱执行环境
"""

from typing import Dict, Any, Optional
from backend.models.schema import ExecutionResult, CodeValidationResult
from backend.execution.validator import get_security_validator
from backend.execution.executor import get_code_executor

class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self):
        """初始化沙箱管理器"""
        self.validator = get_security_validator()
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "validation_failures": 0,
            "execution_failures": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0
        }
    
    def execute_code_safely(self, code: str, output_path: str,
                           execution_mode: str = "restricted",
                           timeout: int = 30,
                           validate_first: bool = True) -> Dict[str, Any]:
        """
        安全执行代码
        
        Args:
            code: 要执行的代码
            output_path: 输出路径
            execution_mode: 执行模式
            timeout: 超时时间
            validate_first: 是否先进行安全验证
            
        Returns:
            Dict[str, Any]: 包含验证和执行结果的完整响应
        """
        self.execution_stats["total_executions"] += 1
        
        response = {
            "validation_result": None,
            "execution_result": None,
            "overall_success": False,
            "error_message": None
        }
        
        try:
            # 1. 代码安全验证
            if validate_first:
                validation_result = self.validator.validate_code(code)
                response["validation_result"] = validation_result
                
                if not validation_result.is_valid:
                    self.execution_stats["validation_failures"] += 1
                    self.execution_stats["failed_executions"] += 1
                    response["error_message"] = f"代码安全验证失败: {'; '.join(validation_result.security_issues)}"
                    return response
            
            # 2. 执行代码
            executor = get_code_executor(execution_mode)
            execution_result = executor.execute_code(code, output_path, timeout)
            response["execution_result"] = execution_result
            
            # 3. 更新统计信息
            self.execution_stats["total_execution_time"] += execution_result.execution_time
            
            if execution_result.success:
                self.execution_stats["successful_executions"] += 1
                response["overall_success"] = True
            else:
                self.execution_stats["execution_failures"] += 1
                self.execution_stats["failed_executions"] += 1
                response["error_message"] = execution_result.error_message
            
            # 更新平均执行时间
            self.execution_stats["avg_execution_time"] = (
                self.execution_stats["total_execution_time"] / 
                self.execution_stats["total_executions"]
            )
            
            return response
            
        except Exception as e:
            self.execution_stats["failed_executions"] += 1
            response["error_message"] = f"沙箱管理器异常: {str(e)}"
            return response
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """获取沙箱统计信息"""
        stats = self.execution_stats.copy()
        
        # 计算成功率
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
            stats["validation_failure_rate"] = stats["validation_failures"] / stats["total_executions"]
            stats["execution_failure_rate"] = stats["execution_failures"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
            stats["validation_failure_rate"] = 0.0
            stats["execution_failure_rate"] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        for key in self.execution_stats:
            self.execution_stats[key] = 0 if isinstance(self.execution_stats[key], int) else 0.0
    
    def get_security_report(self) -> Dict[str, Any]:
        """获取安全配置报告"""
        return self.validator.get_security_report()

# 全局沙箱管理器实例
_sandbox_manager = None

def get_sandbox_manager() -> SandboxManager:
    """获取全局沙箱管理器实例"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager

def execute_code_in_sandbox(code: str, output_path: str, **kwargs) -> Dict[str, Any]:
    """
    便捷的沙箱执行函数
    
    Args:
        code: 要执行的代码
        output_path: 输出路径
        **kwargs: 其他参数
        
    Returns:
        Dict[str, Any]: 执行结果
    """
    manager = get_sandbox_manager()
    return manager.execute_code_safely(code, output_path, **kwargs)

if __name__ == "__main__":
    # 测试代码
    test_code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 测试数据
x = np.linspace(0, 10, 50)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'r-', linewidth=2, label='sin(x)')
plt.xlabel('X轴')
plt.ylabel('Y轴')  
plt.title('正弦函数图')
plt.legend()
plt.grid(True, alpha=0.3)

# 保存图片
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

# 返回结果
result = {
    'function_type': 'trigonometric',
    'function_name': 'sin(x)',
    'x_range': [float(x.min()), float(x.max())],
    'y_range': [float(y.min()), float(y.max())],
    'points_count': len(x)
}

print(f"成功生成图表，保存到: {output_path}")
"""
    
    manager = get_sandbox_manager()
    
    # 测试安全代码
    print("测试安全代码执行:")
    result = manager.execute_code_safely(
        test_code, 
        "output/sandbox_test.png",
        execution_mode="restricted"
    )
    
    print(f"整体成功: {result['overall_success']}")
    if result['validation_result']:
        print(f"验证通过: {result['validation_result'].is_valid}")
        print(f"警告数量: {len(result['validation_result'].warnings)}")
    
    if result['execution_result']:
        print(f"执行成功: {result['execution_result'].success}")
        print(f"执行时间: {result['execution_result'].execution_time:.2f}秒")
        print(f"结果数据: {result['execution_result'].result_data}")
    
    if result['error_message']:
        print(f"错误信息: {result['error_message']}")
    
    # 打印统计信息
    print(f"\n沙箱统计: {manager.get_sandbox_stats()}")
    
    # 测试危险代码
    print("\n测试危险代码:")
    dangerous_code = """
import os
os.system('echo "尝试系统调用"')
"""
    
    result2 = manager.execute_code_safely(dangerous_code, "output/danger.png")
    print(f"危险代码整体成功: {result2['overall_success']}")
    print(f"错误信息: {result2['error_message']}")
    
    print(f"\n最终统计: {manager.get_sandbox_stats()}")
