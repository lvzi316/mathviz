# AI驱动数学可视化系统使用指南

## 📋 概述

本系统已成功从传统的规则驱动模式升级为AI驱动模式，支持通过大语言模型（LLM）自动理解数学题目并生成可视化代码。

## 🏗️ 系统架构

```
用户输入题目 → AI分析生成代码 → 安全验证 → 沙箱执行 → 图片生成 → 返回结果
```

### 核心组件

1. **AI服务模块** (`backend/ai_service/`)
   - `llm_client.py`: 支持OpenAI、Claude、通义千问等多个LLM提供商
   - `prompt_templates.py`: YAML格式的参数化Prompt模板管理
   - `code_generator.py`: AI代码生成器，支持重试和置信度评估

2. **执行模块** (`backend/execution/`)
   - `validator.py`: 代码安全验证器，多层防护
   - `executor.py`: 支持受限执行和进程沙箱两种模式
   - `sandbox.py`: 沙箱管理器，统一管理执行环境

3. **数据模型** (`backend/models/`)
   - `schema.py`: 完整的数据模型定义，支持类型检查

4. **API接口** (`backend/api/`)
   - `endpoints.py`: 新的v2 API，兼容传统模式

5. **Prompt模板** (`prompts/`)
   - `math_visualization.yaml`: 支持多种变体的YAML模板

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements-ai.txt

# 根据需要安装LLM客户端
pip install openai anthropic  # OpenAI和Claude
```

### 2. 配置API密钥

```python
# 通过API设置
import requests

# 设置OpenAI API密钥
requests.post("http://localhost:8000/api/v2/config/api-key", 
              params={"provider": "openai", "api_key": "your-api-key"})

# 设置Claude API密钥  
requests.post("http://localhost:8000/api/v2/config/api-key",
              params={"provider": "claude", "api_key": "your-api-key"})
```

### 3. 运行集成测试

```bash
python test_ai_system.py
```

### 4. 启动服务

```bash
# 更新api_server.py以包含新的路由
uvicorn api_server:app --reload --port 8000
```

## 📝 API使用指南

### 新的v2 API端点

#### 1. 生成可视化（支持AI模式）

```python
import requests

# AI模式请求
response = requests.post("http://localhost:8000/api/v2/problems/generate", 
                        json={
                            "text": "甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
                            "processing_mode": "ai",
                            "llm_provider": "openai",
                            "prompt_variant": "detailed_mode"
                        })

task_id = response.json()["task_id"]
```

#### 2. 查询任务状态

```python
# 轮询任务状态
import time

while True:
    status_response = requests.get(f"http://localhost:8000/api/v2/tasks/{task_id}")
    status_data = status_response.json()
    
    if status_data["status"] == "completed":
        print("✅ 任务完成!")
        print(f"AI分析: {status_data['ai_analysis']}")
        print(f"执行结果: {status_data['execution_result']}")
        break
    elif status_data["status"] == "failed":
        print(f"❌ 任务失败: {status_data['error_message']}")
        break
    
    print(f"进度: {status_data['progress']}%")
    time.sleep(2)
```

#### 3. 兼容传统模式

```python
# 传统模式请求（向后兼容）
response = requests.post("http://localhost:8000/api/v2/problems/generate",
                        json={
                            "text": "甲、乙两地相距480公里，两车相向而行...",
                            "processing_mode": "traditional"
                        })
```

### 系统管理API

```python
# 获取系统统计
stats = requests.get("http://localhost:8000/api/v2/stats").json()

# 健康检查
health = requests.get("http://localhost:8000/api/v2/health").json()

# 测试LLM连接
test_result = requests.post("http://localhost:8000/api/v2/test/connection/openai").json()
```

## 🎨 Prompt模板自定义

### 创建新的模板变体

编辑 `prompts/math_visualization.yaml`:

```yaml
variants:
  my_custom_mode:
    system_prompt: |
      你是一个专业的数学可视化专家...
      
    user_prompt_template: |
      题目：{problem_text}
      输出路径：{output_path}
      
      请生成专业的可视化代码...
```

### 使用自定义模板

```python
response = requests.post("http://localhost:8000/api/v2/problems/generate",
                        json={
                            "text": "数学题目...",
                            "processing_mode": "ai", 
                            "prompt_variant": "my_custom_mode"
                        })
```

## 🛡️ 安全配置

### 代码安全验证

系统默认开启多层安全验证：

1. **模块导入限制**: 只允许matplotlib、numpy、math等安全模块
2. **函数调用检查**: 禁止eval、exec、os.system等危险函数
3. **文件操作限制**: 除了保存图片外禁止其他文件操作
4. **网络访问阻断**: 禁止所有网络请求
5. **资源使用限制**: 限制内存和CPU使用

### 自定义安全策略

```python
from backend.execution.validator import get_security_validator

validator = get_security_validator()

# 添加允许的模块
validator.allowed_modules.add('scipy')

# 查看安全报告
report = validator.get_security_report()
print(report)
```

## 📊 监控和调试

### 1. 实时监控

```python
# 获取详细统计
stats = requests.get("http://localhost:8000/api/v2/stats").json()

print(f"任务统计: {stats['task_stats']}")
print(f"AI生成统计: {stats['ai_generation_stats']}")  
print(f"沙箱统计: {stats['sandbox_stats']}")
```

### 2. 日志调试

```python
# 查看任务详情
task_detail = requests.get(f"http://localhost:8000/api/v2/tasks/{task_id}").json()

if task_detail["execution_result"]:
    print(f"执行日志: {task_detail['execution_result']['output_logs']}")
    print(f"错误信息: {task_detail['execution_result']['error_message']}")
```

### 3. 性能优化

```python
# 配置并发限制
requests.post("http://localhost:8000/api/v2/config", 
              json={"max_concurrent_tasks": 20})

# 选择更快的执行模式
requests.post("http://localhost:8000/api/v2/config",
              json={"default_execution_mode": "restricted"})  # 比process模式更快
```

## 🔧 故障排除

### 常见问题

1. **API密钥未设置**
   ```
   错误: 未配置openai的API密钥
   解决: 通过/api/v2/config/api-key设置API密钥
   ```

2. **代码安全验证失败**
   ```
   错误: 代码安全验证失败: 禁止导入危险模块: os
   解决: 检查AI生成的代码，确保只使用允许的模块
   ```

3. **执行超时**
   ```
   错误: 代码执行超时
   解决: 优化生成的代码或增加timeout参数
   ```

4. **内存不足**
   ```
   错误: 内存使用超限
   解决: 减少数据规模或增加内存限制
   ```

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试单个组件
from backend.execution.sandbox import get_sandbox_manager
manager = get_sandbox_manager()
result = manager.execute_code_safely(test_code, "output/debug.png")
print(result)
```

## 📈 扩展和定制

### 1. 添加新的LLM提供商

```python
# 在backend/ai_service/llm_client.py中添加新的客户端类
class NewLLMClient(BaseLLMClient):
    async def generate_completion(self, system_prompt, user_prompt, config):
        # 实现新的LLM API调用
        pass
```

### 2. 自定义沙箱执行器

```python
# 在backend/execution/executor.py中添加新的执行器
class CustomExecutor:
    def execute_code(self, code, output_path, timeout):
        # 实现自定义执行逻辑
        pass
```

### 3. 扩展数据模型

```python
# 在backend/models/schema.py中添加新的模型
class CustomRequest(BaseModel):
    # 添加新的请求字段
    pass
```

## 📚 参考资料

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Pydantic文档](https://docs.pydantic.dev/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Anthropic Claude API文档](https://docs.anthropic.com/)
- [RestrictedPython文档](https://restrictedpython.readthedocs.io/)

## 🤝 贡献指南

1. 运行测试: `python test_ai_system.py`
2. 代码格式化: `black backend/`
3. 类型检查: `mypy backend/`
4. 提交代码前确保所有测试通过

---

🎉 **系统已就绪！** 您现在可以使用AI驱动的数学可视化功能了。
