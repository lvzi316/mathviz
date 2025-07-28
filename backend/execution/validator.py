#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码安全验证器
用于检查AI生成的代码是否安全可执行
"""

import ast
import re
import time
from typing import List, Set, Dict, Any, Tuple
from backend.models.schema import CodeValidationResult

class SecurityValidator:
    """代码安全验证器"""
    
    def __init__(self):
        """初始化安全验证器"""
        # 危险函数黑名单
        self.forbidden_functions = {
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input',
            'exit', 'quit', 'reload', 'help',
            'vars', 'locals', 'globals', 'dir',
            'getattr', 'setattr', 'delattr', 'hasattr',
            'callable', 'isinstance', 'issubclass',
            'breakpoint', 'memoryview', 'bytearray',
            'classmethod', 'staticmethod', 'property',
            'super', 'type', 'id', 'hash'
        }
        
        # 危险模块黑名单
        self.forbidden_modules = {
            'os', 'sys', 'subprocess', 'socket', 'urllib',
            'urllib2', 'urllib3', 'requests', 'http', 'httplib',
            'ftplib', 'smtplib', 'email', 'imaplib', 'poplib',
            'pickle', 'marshal', 'shelve', 'dbm', 'gdbm',
            'sqlite3', 'mysql', 'psycopg2', 'pymongo',
            'ctypes', 'cffi', 'gc', 'threading', 'thread',
            'multiprocessing', 'asyncio', 'concurrent',
            'importlib', 'imp', 'pkgutil', 'modulefinder',
            'code', 'codeop', 'ast', 'compiler', 'py_compile',
            'compileall', 'dis', 'pickletools',
            'tempfile', 'shutil', 'glob', 'fnmatch',
            'linecache', 'fileinput', 'filecmp',
            'tarfile', 'zipfile', 'gzip', 'bz2', 'lzma',
            'pty', 'tty', 'grp', 'pwd', 'spwd',
            'platform', 'getpass', 'resource', 'rlcompleter'
        }
        
        # 允许的模块白名单
        self.allowed_modules = {
            'matplotlib', 'matplotlib.pyplot', 'matplotlib.patches',
            'matplotlib.animation', 'matplotlib.figure',
            'matplotlib.axes', 'matplotlib.patches',
            'numpy', 'np',
            'math', 'cmath',
            'datetime', 'time', 'calendar',
            're', 'regex',
            'random',  # 可能用于生成示例数据
            'statistics',  # 统计计算
            'fractions', 'decimal',  # 数学计算
            'collections', 'itertools', 'functools',  # 基础数据结构
            'copy', 'deepcopy',  # 对象复制
            'json',  # 可能用于结果输出
            'warnings'  # 警告控制
        }
        
        # 危险字符串模式
        self.dangerous_patterns = [
            r'__.*__',  # 双下划线方法
            r'\.system\s*\(',  # 系统调用
            r'\.popen\s*\(',   # 进程操作
            r'\.spawn\s*\(',   # 生成进程
            r'eval\s*\(',   # eval调用
            r'exec\s*\(',   # exec调用
            r'import\s+os',  # 导入os
            r'from\s+os\s+import',  # 从os导入
            r'subprocess\.',  # subprocess使用
            r'\.read\s*\(',  # 文件读取
            r'\.write\s*\(',  # 文件写入
            r'\.delete\s*\(',  # 文件删除
            r'\.remove\s*\(',  # 文件删除
            r'\.rmdir\s*\(',  # 目录删除
            r'\.mkdir\s*\(',  # 创建目录
            r'\.chmod\s*\(',  # 修改权限
            r'\.chown\s*\(',  # 修改所有者
            r'http[s]?://',  # URL访问
            r'ftp://',  # FTP访问
            r'file://',  # 文件协议
            r'\.connect\s*\(',  # 网络连接
            r'\.send\s*\(',  # 网络发送
            r'\.recv\s*\(',  # 网络接收
            r'\.listen\s*\(',  # 网络监听
            r'\.bind\s*\(',  # 网络绑定
        ]
        
        # 文件操作相关模式（除了plt.savefig）
        self.file_operation_patterns = [
            r'open\s*\(',
            r'\.open\s*\(',
            r'file\s*\(',
            r'\.file\s*\(',
            r'with\s+open\s*\(',
        ]
    
    def validate_code(self, code: str) -> CodeValidationResult:
        """
        验证代码安全性
        
        Args:
            code: 要验证的代码
            
        Returns:
            CodeValidationResult: 验证结果
        """
        start_time = time.time()
        security_issues = []
        syntax_errors = []
        warnings = []
        
        try:
            # 1. 语法检查
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                syntax_errors.append(f"语法错误: {str(e)}")
                return CodeValidationResult(
                    is_valid=False,
                    security_issues=security_issues,
                    syntax_errors=syntax_errors,
                    warnings=warnings,
                    validation_time=time.time() - start_time
                )
            
            # 2. AST节点安全检查
            ast_issues = self._check_ast_security(tree)
            security_issues.extend(ast_issues)
            
            # 3. 导入检查
            import_issues = self._check_imports(tree)
            security_issues.extend(import_issues)
            
            # 4. 字符串模式检查
            pattern_issues = self._check_dangerous_patterns(code)
            security_issues.extend(pattern_issues)
            
            # 5. 文件操作检查
            file_issues = self._check_file_operations(code)
            security_issues.extend(file_issues)
            
            # 6. 网络访问检查
            network_issues = self._check_network_access(code)
            security_issues.extend(network_issues)
            
            # 7. 代码质量警告
            quality_warnings = self._check_code_quality(code, tree)
            warnings.extend(quality_warnings)
            
            # 8. 必需元素检查
            required_warnings = self._check_required_elements(code)
            warnings.extend(required_warnings)
            
            validation_time = time.time() - start_time
            is_valid = len(security_issues) == 0 and len(syntax_errors) == 0
            
            return CodeValidationResult(
                is_valid=is_valid,
                security_issues=security_issues,
                syntax_errors=syntax_errors,
                warnings=warnings,
                validation_time=validation_time
            )
            
        except Exception as e:
            return CodeValidationResult(
                is_valid=False,
                security_issues=[f"验证过程异常: {str(e)}"],
                syntax_errors=[],
                warnings=[],
                validation_time=time.time() - start_time
            )
    
    def _check_ast_security(self, tree: ast.AST) -> List[str]:
        """检查AST节点的安全性"""
        issues = []
        
        for node in ast.walk(tree):
            # 检查函数调用
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.forbidden_functions:
                        issues.append(f"禁止调用危险函数: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.forbidden_functions:
                        issues.append(f"禁止调用危险方法: {node.func.attr}")
            
            # 检查属性访问
            elif isinstance(node, ast.Attribute):
                if node.attr in self.forbidden_functions:
                    issues.append(f"禁止访问危险属性: {node.attr}")
            
            # 检查名称引用
            elif isinstance(node, ast.Name):
                if node.id in self.forbidden_functions:
                    issues.append(f"禁止引用危险名称: {node.id}")
        
        return issues
    
    def _check_imports(self, tree: ast.AST) -> List[str]:
        """检查导入语句的安全性"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # 获取顶级模块名
                    if module_name in self.forbidden_modules:
                        issues.append(f"禁止导入危险模块: {alias.name}")
                    elif module_name not in self.allowed_modules and alias.name not in self.allowed_modules:
                        issues.append(f"未授权的模块导入: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name in self.forbidden_modules:
                        issues.append(f"禁止从危险模块导入: {node.module}")
                    elif module_name not in self.allowed_modules and node.module not in self.allowed_modules:
                        issues.append(f"未授权的模块导入: {node.module}")
        
        return issues
    
    def _check_dangerous_patterns(self, code: str) -> List[str]:
        """检查危险字符串模式"""
        issues = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                issues.append(f"发现危险代码模式: {pattern}")
        
        return issues
    
    def _check_file_operations(self, code: str) -> List[str]:
        """检查文件操作（除了允许的图片保存）"""
        issues = []
        
        # 检查是否有文件操作
        for pattern in self.file_operation_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                # 获取匹配位置前后的上下文
                start = max(0, match.start() - 50)
                end = min(len(code), match.end() + 50)
                context = code[start:end]
                
                # 检查是否是允许的savefig操作
                if 'savefig' not in context.lower() and 'plt.savefig' not in context.lower():
                    issues.append(f"禁止的文件操作: {match.group()} (位置: {match.start()})")
        
        return issues
    
    def _check_network_access(self, code: str) -> List[str]:
        """检查网络访问"""
        issues = []
        
        network_patterns = [
            r'http[s]?://',
            r'ftp://',
            r'\.connect\s*\(',
            r'\.send\s*\(',
            r'\.recv\s*\(',
            r'\.request\s*\(',
            r'\.get\s*\(',
            r'\.post\s*\(',
            r'socket\.',
            r'urllib\.',
            r'requests\.',
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"禁止的网络访问: {pattern}")
        
        return issues
    
    def _check_code_quality(self, code: str, tree: ast.AST) -> List[str]:
        """检查代码质量"""
        warnings = []
        
        # 检查代码长度
        if len(code) > 10000:
            warnings.append("代码过长，可能影响执行性能")
        elif len(code) < 100:
            warnings.append("代码过短，可能功能不完整")
        
        # 检查循环嵌套深度
        max_depth = self._get_max_nesting_depth(tree)
        if max_depth > 4:
            warnings.append(f"循环/条件嵌套过深 (深度: {max_depth})")
        
        # 检查是否有大量重复代码
        lines = code.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())
        if len(lines) > 50 and len(unique_lines) / len(lines) < 0.7:
            warnings.append("代码重复度较高")
        
        return warnings
    
    def _check_required_elements(self, code: str) -> List[str]:
        """检查必需的代码元素"""
        warnings = []
        
        # 检查是否使用matplotlib
        if 'matplotlib' not in code and 'plt' not in code:
            warnings.append("代码应该使用matplotlib进行可视化")
        
        # 检查是否设置中文字体
        if 'font' not in code.lower() or 'simhei' not in code.lower():
            warnings.append("建议设置中文字体以正确显示中文")
        
        # 检查是否有图片保存
        if 'savefig' not in code.lower():
            warnings.append("代码应该包含图片保存逻辑")
        
        # 检查是否有结果返回
        if 'result' not in code:
            warnings.append("建议定义result变量返回计算结果")
        
        # 检查是否使用Agg后端
        if 'Agg' not in code:
            warnings.append("建议使用matplotlib.use('Agg')设置后端")
        
        return warnings
    
    def _get_max_nesting_depth(self, tree: ast.AST) -> int:
        """获取最大嵌套深度"""
        def get_depth(node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.While, ast.If, ast.With)):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return get_depth(tree)
    
    def get_security_report(self) -> Dict[str, Any]:
        """获取安全配置报告"""
        return {
            "forbidden_functions_count": len(self.forbidden_functions),
            "forbidden_modules_count": len(self.forbidden_modules),
            "allowed_modules_count": len(self.allowed_modules),
            "dangerous_patterns_count": len(self.dangerous_patterns),
            "forbidden_functions": sorted(list(self.forbidden_functions)),
            "forbidden_modules": sorted(list(self.forbidden_modules)),
            "allowed_modules": sorted(list(self.allowed_modules))
        }

# 全局验证器实例
security_validator = SecurityValidator()

def validate_code_security(code: str) -> CodeValidationResult:
    """
    便捷的代码安全验证函数
    
    Args:
        code: 要验证的代码
        
    Returns:
        CodeValidationResult: 验证结果
    """
    return security_validator.validate_code(code)

def get_security_validator() -> SecurityValidator:
    """获取全局安全验证器实例"""
    return security_validator

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

# 解析参数
distance = 480
speed1 = 60
speed2 = 80

# 计算相遇时间
meeting_time = distance / (speed1 + speed2)
meeting_point = speed1 * meeting_time

# 创建图表
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot([0, distance], [0, 0], 'k-', linewidth=2)
ax.plot(meeting_point, 0, 'ro', markersize=10)

# 保存图片
plt.savefig('output/test.png', dpi=300, bbox_inches='tight')
plt.close()

# 返回结果
result = {
    'meeting_time': meeting_time,
    'meeting_point': meeting_point,
    'distance': distance,
    'speed1': speed1,
    'speed2': speed2
}
"""
    
    validator = get_security_validator()
    result = validator.validate_code(test_code)
    
    print(f"验证通过: {result.is_valid}")
    print(f"安全问题: {result.security_issues}")
    print(f"语法错误: {result.syntax_errors}")
    print(f"警告: {result.warnings}")
    print(f"验证时间: {result.validation_time:.3f}秒")
    
    # 测试危险代码
    dangerous_code = """
import os
os.system('rm -rf /')
"""
    
    result2 = validator.validate_code(dangerous_code)
    print(f"\n危险代码验证通过: {result2.is_valid}")
    print(f"危险代码安全问题: {result2.security_issues}")
