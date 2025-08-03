#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码沙箱执行器
提供安全的代码执行环境
"""

import os
import sys
import time
import uuid
import tempfile
import subprocess
import threading
import signal
import resource
import json
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager

from backend.models.schema import ExecutionResult
from backend.execution.validator import validate_code_security

class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self, max_memory_mb: int = 512, max_cpu_time: int = 30):
        """
        初始化资源监控器
        
        Args:
            max_memory_mb: 最大内存使用（MB）
            max_cpu_time: 最大CPU时间（秒）
        """
        self.max_memory = max_memory_mb * 1024 * 1024  # 转换为字节
        self.max_cpu_time = max_cpu_time
        self.original_limits = {}
    
    @contextmanager
    def resource_limit(self):
        """设置资源限制的上下文管理器"""
        if sys.platform != "win32":  # Windows不支持resource模块
            try:
                # 保存原始限制
                self.original_limits['memory'] = resource.getrlimit(resource.RLIMIT_AS)
                self.original_limits['cpu'] = resource.getrlimit(resource.RLIMIT_CPU)
                
                # 设置新限制
                resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
                resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time, self.max_cpu_time))
                
                yield
                
            except Exception as e:
                print(f"警告: 无法设置资源限制: {e}")
                yield
            finally:
                # 恢复原始限制
                try:
                    if 'memory' in self.original_limits:
                        resource.setrlimit(resource.RLIMIT_AS, self.original_limits['memory'])
                    if 'cpu' in self.original_limits:
                        resource.setrlimit(resource.RLIMIT_CPU, self.original_limits['cpu'])
                except Exception as e:
                    print(f"警告: 无法恢复资源限制: {e}")
        else:
            # Windows系统直接执行
            yield

class RestrictedExecutor:
    """受限执行器（基于RestrictedPython的轻量级方案）"""
    
    def __init__(self):
        """初始化受限执行器"""
        self.safe_builtins = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'max': max, 'min': min, 'sum': sum, 'all': all, 'any': any,
                'abs': abs, 'round': round, 'pow': pow, 'divmod': divmod,
                'bool': bool, 'complex': complex,
                'print': self._safe_print,
                '__import__': self._safe_import,  # 添加受限的import功能
            }
        }
        
        # 允许的模块列表
        self.allowed_modules = {
            'matplotlib', 'matplotlib.pyplot', 'matplotlib.patches',
            'numpy', 'math', 'statistics', 'json',
            'time', 'datetime', 'random'
        }
        
        self.output_buffer = []
        self.error_buffer = []
    
    def _safe_print(self, *args, **kwargs):
        """安全的print函数"""
        output = ' '.join(str(arg) for arg in args)
        self.output_buffer.append(output)
    
    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """
        受限的import函数
        
        Args:
            name: 模块名
            globals: 全局命名空间
            locals: 局部命名空间
            fromlist: from import列表
            level: 相对导入级别
        
        Returns:
            导入的模块
        """
        # 检查模块是否在允许列表中
        if name not in self.allowed_modules and not any(name.startswith(allowed + '.') for allowed in self.allowed_modules):
            raise ImportError(f"导入模块 '{name}' 被禁止")
        
        # 执行实际导入
        return __import__(name, globals, locals, fromlist, level)
    
    def execute_code(self, code: str, output_path: str, timeout: int = 30) -> ExecutionResult:
        """
        执行代码
        
        Args:
            code: 要执行的代码
            output_path: 输出图片路径
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        # 清空缓冲区
        self.output_buffer.clear()
        self.error_buffer.clear()
        
        try:
            # 1. 代码安全验证
            validation_result = validate_code_security(code)
            if not validation_result.is_valid:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message=f"代码安全验证失败: {'; '.join(validation_result.security_issues)}"
                )
            
            # 2. 准备执行环境
            globals_dict = self.safe_builtins.copy()
            
            # 安全导入允许的模块
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                import numpy as np
                import math
                import re
                import datetime
                import random
                import json
                
                globals_dict.update({
                    'matplotlib': matplotlib,
                    'plt': plt,
                    'np': np,
                    'numpy': np,
                    'math': math,
                    're': re,
                    'datetime': datetime,
                    'random': random,
                    'json': json,
                    'output_path': output_path,
                })
            except ImportError as e:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message=f"导入模块失败: {str(e)}"
                )
            
            # 3. 设置超时和资源限制
            def timeout_handler(signum, frame):
                raise TimeoutError("代码执行超时")
            
            # 4. 执行代码
            try:
                if sys.platform != "win32":
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout)
                
                monitor = ResourceMonitor()
                with monitor.resource_limit():
                    # 编译并执行代码
                    compiled_code = compile(code, '<generated>', 'exec')
                    exec(compiled_code, globals_dict)
                
                # 获取结果
                result_data = globals_dict.get('result', {})
                execution_time = time.time() - start_time
                
                # 检查图片是否生成
                image_generated = os.path.exists(output_path)
                
                return ExecutionResult(
                    success=True,
                    image_path=output_path if image_generated else None,
                    result_data=result_data,
                    execution_time=execution_time,
                    memory_usage=self._get_memory_usage(),
                    output_logs='\n'.join(self.output_buffer)
                )
                
            except TimeoutError:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message="代码执行超时"
                )
            except MemoryError:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message="内存使用超限"
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message=f"代码执行错误: {str(e)}",
                    output_logs='\n'.join(self.output_buffer)
                )
            finally:
                if sys.platform != "win32":
                    signal.alarm(0)  # 取消超时
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                execution_time=time.time() - start_time,
                error_message=f"执行器异常: {str(e)}"
            )
    
    def _get_memory_usage(self) -> float:
        """获取内存使用情况（MB）"""
        try:
            if sys.platform != "win32":
                usage = resource.getrusage(resource.RUSAGE_SELF)
                return usage.ru_maxrss / 1024  # 转换为MB
            else:
                # Windows系统的简单估算
                import psutil
                process = psutil.Process()
                return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

class ProcessSandbox:
    """进程沙箱（更安全但性能较低）"""
    
    def __init__(self):
        """初始化进程沙箱"""
        pass
    
    def execute_code(self, code: str, output_path: str, timeout: int = 30) -> ExecutionResult:
        """
        在独立进程中执行代码
        
        Args:
            code: 要执行的代码
            output_path: 输出图片路径
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 1. 代码安全验证
            validation_result = validate_code_security(code)
            if not validation_result.is_valid:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message=f"代码安全验证失败: {'; '.join(validation_result.security_issues)}"
                )
            
            # 2. 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                # 包装代码
                wrapped_code = f"""
import sys
import os
import json
import traceback

# 设置输出路径
output_path = r"{output_path}"

try:
    # 执行用户代码
{self._indent_code(code, '    ')}
    
    # 保存结果
    if 'result' in locals():
        try:
            result_json = json.dumps(result, ensure_ascii=False, default=str)
            print(f"RESULT:{result_json}")
        except Exception as e:
            print(f"RESULT_ERROR: {str(e)}")
    
    print("SUCCESS: Code executed successfully")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
"""
                temp_file.write(wrapped_code)
                temp_file_path = temp_file.name
            
            # 3. 执行代码
            try:
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.path.dirname(output_path)
                )
                
                execution_time = time.time() - start_time
                
                # 解析输出
                stdout_lines = result.stdout.split('\n')
                result_data = {}
                output_logs = []
                
                for line in stdout_lines:
                    if line.startswith('RESULT:'):
                        try:
                            result_data = json.loads(line[7:])
                        except json.JSONDecodeError:
                            pass
                    elif line.strip():
                        output_logs.append(line)
                
                if result.returncode == 0:
                    return ExecutionResult(
                        success=True,
                        image_path=output_path if os.path.exists(output_path) else None,
                        result_data=result_data,
                        execution_time=execution_time,
                        output_logs='\n'.join(output_logs)
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        execution_time=execution_time,
                        error_message=result.stderr or "未知错误",
                        output_logs='\n'.join(output_logs)
                    )
                    
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message="代码执行超时"
                )
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                execution_time=time.time() - start_time,
                error_message=f"沙箱执行异常: {str(e)}"
            )
    
    def _indent_code(self, code: str, indent: str) -> str:
        """给代码添加缩进"""
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)

class SafeCodeExecutor:
    """安全代码执行器（主接口）"""
    
    def __init__(self, execution_mode: str = "restricted"):
        """
        初始化安全执行器
        
        Args:
            execution_mode: 执行模式（"restricted"或"process"）
        """
        self.execution_mode = execution_mode
        
        if execution_mode == "restricted":
            self.executor = RestrictedExecutor()
        elif execution_mode == "process":
            self.executor = ProcessSandbox()
        else:
            raise ValueError(f"不支持的执行模式: {execution_mode}")
    
    def execute_code(self, code: str, output_path: str, timeout: int = 30) -> ExecutionResult:
        """
        执行代码
        
        Args:
            code: 要执行的代码
            output_path: 输出图片路径
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        return self.executor.execute_code(code, output_path, timeout)
    
    def get_execution_mode(self) -> str:
        """获取当前执行模式"""
        return self.execution_mode

# 全局执行器实例
_default_executor = None

def get_code_executor(execution_mode: str = "restricted") -> SafeCodeExecutor:
    """
    获取代码执行器实例
    
    Args:
        execution_mode: 执行模式
        
    Returns:
        SafeCodeExecutor: 执行器实例
    """
    global _default_executor
    if _default_executor is None or _default_executor.get_execution_mode() != execution_mode:
        _default_executor = SafeCodeExecutor(execution_mode)
    return _default_executor

def execute_visualization_code(code: str, output_path: str, 
                             execution_mode: str = "restricted",
                             timeout: int = 30) -> ExecutionResult:
    """
    便捷的代码执行函数
    
    Args:
        code: 要执行的代码
        output_path: 输出图片路径
        execution_mode: 执行模式
        timeout: 超时时间
        
    Returns:
        ExecutionResult: 执行结果
    """
    executor = get_code_executor(execution_mode)
    return executor.execute_code(code, output_path, timeout)

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
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('测试图表')
plt.legend()
plt.grid(True, alpha=0.3)

# 保存图片
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

# 返回结果
result = {
    'function': 'sin(x)',
    'x_range': [0, 10],
    'points_count': len(x)
}

print(f"图片已保存到: {output_path}")
"""
    
    # 测试受限执行器
    print("测试受限执行器:")
    result = execute_visualization_code(
        test_code, 
        "output/test_restricted.png", 
        execution_mode="restricted"
    )
    
    print(f"成功: {result.success}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    print(f"内存使用: {result.memory_usage:.1f}MB")
    print(f"结果数据: {result.result_data}")
    if result.error_message:
        print(f"错误: {result.error_message}")
    
    # 测试进程沙箱
    print("\n测试进程沙箱:")
    result2 = execute_visualization_code(
        test_code, 
        "output/test_process.png", 
        execution_mode="process"
    )
    
    print(f"成功: {result2.success}")
    print(f"执行时间: {result2.execution_time:.2f}秒")
    print(f"结果数据: {result2.result_data}")
    if result2.error_message:
        print(f"错误: {result2.error_message}")
