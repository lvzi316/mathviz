# MathViz 多LLM客户端架构

## 概述

MathViz现已支持多个主流大语言模型(LLM)提供商，包括OpenAI、Claude、Qwen(通义千问)和DeepSeek。通过模块化的客户端架构，系统能够轻松扩展支持更多的LLM提供商。

## 支持的LLM提供商

### 1. OpenAI / Moonshot
- **推荐提供商**：Moonshot（兼容OpenAI接口的国产模型）
- **支持模型**：
  - `moonshot-v1-8k`（推荐）
  - `moonshot-v1-32k` 
  - `moonshot-v1-128k`
  - 以及所有OpenAI官方模型（如果使用OpenAI API）
- **配置示例**：
  ```bash
  OPENAI_API_KEY=sk-your-moonshot-api-key-here
  OPENAI_BASE_URL=https://api.moonshot.cn/v1
  OPENAI_DEFAULT_MODEL=moonshot-v1-8k
  ```

### 2. Anthropic Claude
- **支持模型**：
  - `claude-3-5-sonnet-20241022`（推荐）
  - `claude-3-5-haiku-20241022`
  - `claude-3-opus-20240229`
- **配置示例**：
  ```bash
  CLAUDE_API_KEY=sk-ant-your-claude-api-key-here
  CLAUDE_DEFAULT_MODEL=claude-3-5-sonnet-20241022
  ```

### 3. 阿里云通义千问 (Qwen)
- **支持模型**：
  - `qwen-max`（推荐）
  - `qwen-plus`
  - `qwen-turbo`
- **配置示例**：
  ```bash
  QWEN_API_KEY=sk-your-qwen-api-key-here
  QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1
  QWEN_DEFAULT_MODEL=qwen-max
  ```

### 4. DeepSeek
- **支持模型**：
  - `deepseek-chat`（推荐）
  - `deepseek-coder`
- **配置示例**：
  ```bash
  DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
  DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
  DEEPSEEK_DEFAULT_MODEL=deepseek-chat
  ```

## 架构设计

### 模块化客户端架构
```
backend/ai_service/clients/
├── __init__.py              # 客户端模块初始化
├── base_client.py           # 抽象基类
├── openai_client.py         # OpenAI/Moonshot客户端
├── claude_client.py         # Claude客户端
├── qwen_client.py           # Qwen客户端
└── deepseek_client.py       # DeepSeek客户端
```

### 核心组件

#### 1. BaseLLMClient (抽象基类)
定义了所有LLM客户端必须实现的接口：
- `generate_completion()`: 生成文本完成
- `test_connection()`: 测试连接
- `get_default_model()`: 获取默认模型
- `get_supported_models()`: 获取支持的模型列表

#### 2. LLMClientFactory (工厂类)
负责创建和管理LLM客户端实例：
- 支持客户端缓存
- 统一的客户端创建接口
- 支持的提供商管理

#### 3. LLMManager (管理器)
统一管理所有LLM相关操作：
- 配置管理集成
- 多提供商支持
- 连接测试
- 代码生成

## 配置管理

### 环境变量配置
复制`.env.example`为`.env`并填入相应的API密钥：

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

### 配置验证
系统启动时会自动验证配置：

```python
from backend.config import get_config_manager

config = get_config_manager()

# 检查配置状态
summary = config.get_config_summary()
print(f"已配置提供商: {summary['configured_providers']}")
print(f"默认提供商: {summary['default_provider']}")
```

## API使用

### V2 API端点
新的V2 API支持指定LLM提供商：

```bash
POST /api/v2/problems/generate
{
    "text": "甲、乙两地相距480公里，两车相向而行...",
    "user_id": "demo_user",
    "llm_provider": "qwen",           # 指定使用通义千问
    "processing_mode": "ai",
    "prompt_variant": "default"
}
```

支持的`llm_provider`值：
- `openai` - OpenAI/Moonshot
- `claude` - Anthropic Claude  
- `qwen` - 阿里云通义千问
- `deepseek` - DeepSeek

### 前端集成
前端现已支持LLM提供商选择：

```html
<select id="llmProvider">
    <option value="openai">OpenAI / Moonshot</option>
    <option value="claude">Claude</option>
    <option value="qwen">通义千问 (Qwen)</option>
    <option value="deepseek">DeepSeek</option>
</select>
```

## 开发指南

### 添加新的LLM提供商

1. **创建客户端类**：
   ```python
   # backend/ai_service/clients/new_provider_client.py
   from .base_client import BaseLLMClient
   
   class NewProviderClient(BaseLLMClient):
       def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
           super().__init__(api_key, base_url, **kwargs)
           # 初始化客户端
       
       async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                   config: Dict[str, Any]) -> LLMResponse:
           # 实现生成逻辑
           pass
       
       # ... 其他必需方法
   ```

2. **更新模型枚举**：
   ```python
   # backend/models/schema.py
   class LLMProvider(str, Enum):
       OPENAI = "openai"
       CLAUDE = "claude"
       QWEN = "qwen"
       DEEPSEEK = "deepseek"
       NEW_PROVIDER = "new_provider"  # 添加新提供商
   ```

3. **更新工厂类**：
   ```python
   # backend/ai_service/llm_client.py
   def create_client(cls, provider: LLMProvider, api_key: str, ...):
       if provider == LLMProvider.NEW_PROVIDER:
           return NewProviderClient(api_key, **kwargs)
       # ... 其他提供商
   ```

4. **更新配置管理**：
   ```python
   # backend/config.py
   self.api_keys: Dict[LLMProvider, Optional[str]] = {
       # ... 现有提供商
       LLMProvider.NEW_PROVIDER: os.getenv("NEW_PROVIDER_API_KEY"),
   }
   ```

### 测试

运行完整的测试套件：

```bash
# 单元测试
python -m pytest tests/test_multi_llm_clients.py -v

# 集成测试（需要真实API密钥）
OPENAI_API_KEY=your-key python -m pytest tests/test_multi_llm_clients.py::TestClientIntegration -v
```

### 调试模式

启用调试模式查看详细日志：

```bash
# 设置环境变量
export DEBUG=true

# 或在.env文件中设置
DEBUG=true
```

## 最佳实践

### 1. API密钥管理
- 使用环境变量存储API密钥
- 不要将API密钥提交到版本控制
- 为不同环境使用不同的API密钥

### 2. 提供商选择
- **Moonshot**: 国产模型，访问稳定，价格便宜，推荐日常使用
- **Claude**: 推理能力强，适合复杂数学问题
- **Qwen**: 中文理解好，适合中文数学题
- **DeepSeek**: 代码生成能力强，适合复杂可视化需求

### 3. 错误处理
- 系统自动降级到备用提供商
- 详细的错误日志和用户提示
- 连接超时和重试机制

### 4. 性能优化
- 客户端实例缓存
- 异步请求处理
- 合理的超时设置

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误：未配置xxx的API密钥
   解决：检查.env文件中的API密钥设置
   ```

2. **网络连接问题**
   ```
   错误：连接超时
   解决：检查网络连接，可能需要代理或VPN
   ```

3. **模型不支持**
   ```
   错误：不支持的模型
   解决：检查配置的模型名称是否正确
   ```

### 日志查看
启用DEBUG模式查看详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新日志

### v2.0.0 (2024-08-23)
- ✅ 新增模块化LLM客户端架构
- ✅ 支持OpenAI/Moonshot、Claude、Qwen、DeepSeek
- ✅ 统一的配置管理系统
- ✅ 完整的测试覆盖
- ✅ 前端多LLM选择支持
- ✅ 详细的文档和示例

---

如需帮助或反馈，请提交Issue或联系维护团队。
