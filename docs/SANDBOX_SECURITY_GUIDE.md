# 沙箱隔离执行详细设计指南

## 📚 沙箱概念与原理

### 什么是沙箱（Sandbox）？

沙箱是一种安全机制，用于在受限环境中执行不受信任的代码，防止恶意代码对系统造成损害。在我们的项目中，由于需要执行AI生成的Python代码，沙箱隔离变得尤为重要。

### 沙箱的安全威胁模型

**潜在威胁：**
1. **文件系统攻击**：删除/修改重要文件
2. **网络攻击**：发送恶意请求或数据泄露
3. **系统调用攻击**：执行系统命令
4. **资源耗尽**：消耗CPU/内存导致DoS
5. **权限提升**：获取更高系统权限

**防护目标：**
- 限制文件访问权限
- 阻止网络连接
- 控制资源使用
- 禁止危险系统调用
- 隔离执行环境

---

## 🔐 Python代码沙箱实现方案

### 方案1：RestrictedPython（推荐用于原型）

```python
# sandbox/restricted_executor.py
from RestrictedPython import compile_restricted, safe_globals
import ast
import sys
from io import StringIO
import matplotlib
matplotlib.use('Agg')  # 确保无GUI后端

class SafeCodeExecutor:
    def __init__(self):
        # 定义允许的模块和函数
        self.safe_builtins = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float,
                'list': list, 'dict': dict, 'tuple': tuple,
                'range': range, 'enumerate': enumerate,
                'max': max, 'min': min, 'sum': sum,
                'abs': abs, 'round': round, 'pow': pow,
                'print': self.safe_print,  # 自定义print函数
            }
        }
        
        # 允许的模块导入白名单
        self.allowed_modules = {
            'matplotlib.pyplot': 'plt',
            'matplotlib.patches': 'patches',
            'numpy': 'np',
            'math': 'math',
            'datetime': 'datetime',
            're': 're',  # 用于文本解析
        }
        
        self.output_buffer = StringIO()
    
    def safe_print(self, *args, **kwargs):
        """安全的print函数，输出到缓冲区"""
        print(*args, file=self.output_buffer, **kwargs)
    
    def validate_imports(self, code: str) -> bool:
        """验证代码中的import语句是否安全"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.allowed_modules:
                            raise SecurityError(f"禁止导入模块: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module not in self.allowed_modules:
                        raise SecurityError(f"禁止从模块导入: {node.module}")
            return True
        except SyntaxError:
            raise SecurityError("代码语法错误")
    
    def execute_code(self, code: str, output_path: str, timeout=30) -> dict:
        """在受限环境中执行代码"""
        try:
            # 1. 验证导入
            self.validate_imports(code)
            
            # 2. 编译受限代码
            byte_code = compile_restricted(code, '<string>', 'exec')
            if byte_code is None:
                raise SecurityError("代码编译失败，可能包含危险操作")
            
            # 3. 准备执行环境
            globals_dict = self.safe_builtins.copy()
            
            # 安全导入允许的模块
            import matplotlib.pyplot as plt
            import numpy as np
            import math
            import re
            
            globals_dict.update({
                'plt': plt,
                'np': np,
                'math': math,
                're': re,
                'output_path': output_path,  # 传递输出路径
            })
            
            # 4. 执行代码（带超时控制）
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("代码执行超时")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                exec(byte_code, globals_dict)
                result = globals_dict.get('result', {})
                return {
                    'success': True,
                    'result': result,
                    'output': self.output_buffer.getvalue()
                }
            finally:
                signal.alarm(0)  # 取消超时
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': self.output_buffer.getvalue()
            }

class SecurityError(Exception):
    pass
```

### 方案2：Docker容器沙箱（推荐用于生产）

```python
# sandbox/docker_executor.py
import docker
import tempfile
import os
import json
from pathlib import Path

class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image_name = "python-sandbox:latest"
        
        # 确保沙箱镜像存在
        self.build_sandbox_image()
    
    def build_sandbox_image(self):
        """构建沙箱Docker镜像"""
        dockerfile_content = """
FROM python:3.11-slim

# 安装必要的包
RUN pip install matplotlib numpy

# 创建非root用户
RUN useradd -m -u 1000 sandbox

# 设置工作目录
WORKDIR /app
RUN chown sandbox:sandbox /app

# 切换到非root用户
USER sandbox

# 设置matplotlib后端
ENV MPLBACKEND=Agg

CMD ["python", "/app/script.py"]
"""
        
        # 创建临时目录构建镜像
        with tempfile.TemporaryDirectory() as temp_dir:
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            try:
                self.client.images.build(
                    path=temp_dir,
                    tag=self.image_name,
                    rm=True
                )
                print(f"✅ 沙箱镜像构建成功: {self.image_name}")
            except docker.errors.BuildError as e:
                print(f"❌ 镜像构建失败: {e}")
    
    def execute_code(self, code: str, output_path: str, timeout=30) -> dict:
        """在Docker容器中执行代码"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 准备代码文件
                script_path = Path(temp_dir) / "script.py"
                output_dir = Path(temp_dir) / "output"
                output_dir.mkdir()
                
                # 包装代码
                wrapped_code = f"""
import os
import json
import sys
import traceback

# 设置输出路径
output_path = "/app/output/{Path(output_path).name}"

try:
{self.indent_code(code, '    ')}
    
    # 保存结果
    if 'result' in locals():
        with open('/app/output/result.json', 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("SUCCESS: Code executed successfully")
    
except Exception as e:
    error_info = {{
        'error': str(e),
        'traceback': traceback.format_exc()
    }}
    with open('/app/output/error.json', 'w') as f:
        json.dump(error_info, f, ensure_ascii=False, indent=2)
    print(f"ERROR: {{str(e)}}")
    sys.exit(1)
"""
                
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(wrapped_code)
                
                # 运行容器
                container = self.client.containers.run(
                    self.image_name,
                    volumes={
                        str(script_path): {'bind': '/app/script.py', 'mode': 'ro'},
                        str(output_dir): {'bind': '/app/output', 'mode': 'rw'}
                    },
                    working_dir='/app',
                    user='sandbox',
                    network_mode='none',  # 禁用网络
                    mem_limit='512m',     # 限制内存
                    cpu_period=100000,    # CPU限制
                    cpu_quota=50000,      # 50% CPU
                    detach=True,
                    remove=True
                )
                
                # 等待容器完成
                result = container.wait(timeout=timeout)
                logs = container.logs().decode('utf-8')
                
                # 读取结果
                result_file = output_dir / "result.json"
                error_file = output_dir / "error.json"
                
                if result['StatusCode'] == 0 and result_file.exists():
                    with open(result_file, 'r', encoding='utf-8') as f:
                        execution_result = json.load(f)
                    
                    # 复制生成的图片到目标位置
                    generated_image = output_dir / Path(output_path).name
                    if generated_image.exists():
                        import shutil
                        shutil.copy2(generated_image, output_path)
                    
                    return {
                        'success': True,
                        'result': execution_result,
                        'logs': logs
                    }
                else:
                    error_info = {}
                    if error_file.exists():
                        with open(error_file, 'r', encoding='utf-8') as f:
                            error_info = json.load(f)
                    
                    return {
                        'success': False,
                        'error': error_info.get('error', 'Unknown error'),
                        'traceback': error_info.get('traceback', ''),
                        'logs': logs
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"沙箱执行失败: {str(e)}",
                'logs': ''
            }
    
    def indent_code(self, code: str, indent: str) -> str:
        """给代码添加缩进"""
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
```

---

## 🛡️ 安全策略配置

### 1. 代码审查策略

```python
# sandbox/code_validator.py
import ast
import re
from typing import List, Set

class CodeValidator:
    def __init__(self):
        # 危险函数黑名单
        self.dangerous_functions = {
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input',
            'exit', 'quit', 'reload', 'help',
            'vars', 'locals', 'globals', 'dir',
            'getattr', 'setattr', 'delattr', 'hasattr',
            'callable', 'isinstance', 'issubclass',
        }
        
        # 危险模块黑名单
        self.dangerous_modules = {
            'os', 'sys', 'subprocess', 'socket', 'urllib',
            'requests', 'http', 'ftplib', 'smtplib',
            'pickle', 'marshal', 'shelve', 'dbm',
            'sqlite3', 'mysql', 'psycopg2',
            'ctypes', 'cffi', 'gc', 'threading',
            'multiprocessing', 'asyncio',
        }
        
        # 危险字符串模式
        self.dangerous_patterns = [
            r'__.*__',  # 双下划线方法
            r'\.system\(',  # 系统调用
            r'\.popen\(',   # 进程操作
            r'\.spawn\(',   # 生成进程
            r'eval\s*\(',   # eval调用
            r'exec\s*\(',   # exec调用
        ]
    
    def validate_code(self, code: str) -> tuple[bool, List[str]]:
        """验证代码安全性"""
        issues = []
        
        try:
            # 1. 语法检查
            tree = ast.parse(code)
            
            # 2. AST节点检查
            for node in ast.walk(tree):
                # 检查函数调用
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.dangerous_functions:
                            issues.append(f"危险函数调用: {node.func.id}")
                
                # 检查属性访问
                elif isinstance(node, ast.Attribute):
                    if node.attr in self.dangerous_functions:
                        issues.append(f"危险属性访问: {node.attr}")
                
                # 检查导入
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.dangerous_modules:
                            issues.append(f"危险模块导入: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.dangerous_modules:
                        issues.append(f"危险模块导入: {node.module}")
            
            # 3. 正则表达式检查
            for pattern in self.dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    issues.append(f"危险代码模式: {pattern}")
            
            return len(issues) == 0, issues
            
        except SyntaxError as e:
            return False, [f"语法错误: {str(e)}"]
```

### 2. 资源限制配置

```python
# sandbox/resource_monitor.py
import resource
import time
import threading
from contextlib import contextmanager

class ResourceMonitor:
    def __init__(self, max_memory_mb=512, max_cpu_time=30):
        self.max_memory = max_memory_mb * 1024 * 1024  # 转换为字节
        self.max_cpu_time = max_cpu_time
    
    @contextmanager
    def resource_limit(self):
        """设置资源限制的上下文管理器"""
        # 保存原始限制
        original_memory = resource.getrlimit(resource.RLIMIT_AS)
        original_cpu = resource.getrlimit(resource.RLIMIT_CPU)
        
        try:
            # 设置新限制
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
            resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time, self.max_cpu_time))
            
            yield
            
        finally:
            # 恢复原始限制
            resource.setrlimit(resource.RLIMIT_AS, original_memory)
            resource.setrlimit(resource.RLIMIT_CPU, original_cpu)
    
    def monitor_execution(self, func, *args, **kwargs):
        """监控函数执行的资源使用"""
        start_time = time.time()
        start_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        
        try:
            with self.resource_limit():
                result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            
            return {
                'success': True,
                'result': result,
                'execution_time': end_time - start_time,
                'memory_used': end_memory - start_memory
            }
            
        except MemoryError:
            return {'success': False, 'error': '内存使用超限'}
        except OSError as e:
            if 'CPU time limit exceeded' in str(e):
                return {'success': False, 'error': 'CPU时间超限'}
            raise
```

---

## 📖 推荐学习资料

### 1. Python沙箱技术

**RestrictedPython官方文档**
- 官网：https://restrictedpython.readthedocs.io/
- GitHub：https://github.com/plone/RestrictedPython
- 特点：轻量级、易集成、适合Python代码限制

**PyPy Sandbox（已废弃但概念重要）**
- 文档：https://doc.pypy.org/en/latest/sandbox.html
- 论文：《PyPy's Approach to Virtual Machine Construction》

### 2. 容器安全

**Docker安全最佳实践**
- 官方指南：https://docs.docker.com/engine/security/
- OWASP容器安全：https://owasp.org/www-project-container-security/

**gVisor（Google的容器沙箱）**
- 官网：https://gvisor.dev/
- 原理：用户态内核，更强的隔离性

### 3. 系统安全

**Linux Capabilities**
- 手册：https://man7.org/linux/man-pages/man7/capabilities.7.html
- 教程：https://blog.container-solutions.com/linux-capabilities-why-they-exist-and-how-they-work

**seccomp-bpf**
- 内核文档：https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt
- 实践指南：https://www.redhat.com/sysadmin/seccomp

### 4. 学术研究

**沙箱技术综述论文**
```
1. "A Survey of Software-based Control Flow Integrity" (2017)
2. "Sandboxing in Linux: From Smartphone to Cloud" (2019)  
3. "Container Security: Issues, Challenges, and the Road Ahead" (2020)
```

**代码执行安全**
```
1. "CodeJail: A Platform for Dynamic Analysis of Untrusted Code" (2014)
2. "Bolt: On the Expressiveness of Profile-guided Binary Sandboxing" (2017)
```

---

## 🔧 实际集成示例

### 在我们项目中的使用

```python
# ai_service.py (修改后的版本)
from sandbox.docker_executor import DockerSandbox
from sandbox.code_validator import CodeValidator

class AICodeGenerator:
    def __init__(self):
        self.sandbox = DockerSandbox()
        self.validator = CodeValidator()
    
    async def generate_and_execute(self, problem_text: str, output_path: str):
        """生成并安全执行可视化代码"""
        try:
            # 1. 生成代码
            code = await self.generate_visualization_code(problem_text)
            
            # 2. 安全验证
            is_safe, issues = self.validator.validate_code(code)
            if not is_safe:
                return {
                    'success': False,
                    'error': f'代码安全检查失败: {"; ".join(issues)}'
                }
            
            # 3. 沙箱执行
            result = self.sandbox.execute_code(code, output_path, timeout=30)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'代码生成或执行失败: {str(e)}'
            }
```

这个详细的沙箱设计涵盖了多层防护策略，既适合快速原型开发（RestrictedPython），也适合生产环境（Docker）。您觉得哪个方面需要更深入的解释？
