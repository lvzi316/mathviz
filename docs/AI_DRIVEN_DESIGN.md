# 基于大模型的通用数学题目可视化系统设计方案

## 📋 方案概述

### 当前系统的局限性
1. **题型局限**：只支持相遇问题和追及问题
2. **硬编码严重**：参数提取、计算逻辑、可视化样式都是硬编码
3. **扩展困难**：新增题型需要大量代码修改
4. **智能化程度低**：无法处理复杂或变体题目

### 新设计核心思想
**将"规则驱动"改为"AI驱动"**：用大模型理解题目并生成可视化代码，系统负责安全执行和渲染。

---

## 🏗️ 系统架构设计

### 整体架构流程
```
用户输入题目 → 大模型分析 → 生成可视化代码 → 代码验证 → 安全执行 → 图片渲染 → 返回结果
```

### 详细架构图
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   前端界面      │    │    后端API       │    │   大模型服务     │
│                 │    │                  │    │                 │
│ • 题目输入      │◄──►│ • 请求处理       │◄──►│ • 题目理解      │
│ • 图片展示      │    │ • 任务管理       │    │ • 代码生成      │
│ • 进度跟踪      │    │ • 代码执行       │    │ • 参数提取      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   代码执行环境   │
                       │                 │
                       │ • 沙箱执行      │
                       │ • 安全验证      │
                       │ • 图片生成      │
                       └─────────────────┘
```

---

## 🧠 大模型集成方案

### 模型选择策略
1. **主要选择**：
   - OpenAI GPT-4/GPT-3.5-turbo
   - Claude-3 (Anthropic)
   - 通义千问 (本土化)

2. **备选方案**：
   - Google Gemini
   - 百度文心一言
   - 讯飞星火

### Prompt工程设计

#### 系统Prompt模板
```python
SYSTEM_PROMPT = """
你是一个数学题目可视化专家。给定一个中文数学应用题，你需要：

1. 理解题目类型和核心概念
2. 提取关键参数
3. 生成Python可视化代码

输出格式要求：
{
  "problem_type": "题目类型分类",
  "parameters": {参数字典},
  "visualization_code": "Python代码字符串",
  "explanation": "可视化思路说明"
}

代码要求：
- 使用matplotlib
- 代码自包含，包含所有必要的import
- 变量名清晰，注释详细
- 生成图片保存到指定路径
- 返回计算结果字典

安全限制：
- 只允许使用：matplotlib, numpy, math, datetime
- 禁止文件操作（除保存图片）
- 禁止网络访问
- 禁止执行外部命令
"""
```

#### 用户Prompt模板
```python
def generate_user_prompt(problem_text: str, output_path: str) -> str:
    return f"""
题目：{problem_text}

请生成可视化代码，图片保存到：{output_path}

示例输出格式：
{{
  "problem_type": "行程问题-相遇",
  "parameters": {{
    "distance": 480,
    "speed1": 60,
    "speed2": 80
  }},
  "visualization_code": "import matplotlib.pyplot as plt\\n...",
  "explanation": "绘制相遇问题的场景图和位置-时间图"
}}
"""
```

---

## 🔧 技术实现设计

### 1. 新增模块结构

```
backend/
├── ai_service/
│   ├── __init__.py
│   ├── llm_client.py          # 大模型客户端
│   ├── prompt_templates.py    # Prompt模板
│   └── code_generator.py      # 代码生成器
├── execution/
│   ├── __init__.py
│   ├── sandbox.py             # 代码沙箱
│   ├── validator.py           # 代码验证器
│   └── executor.py            # 安全执行器
├── models/
│   ├── __init__.py
│   └── schema.py              # 数据模型
└── api/
    ├── __init__.py
    └── endpoints.py           # API端点
```

### 2. 核心类设计

#### LLM客户端
```python
class LLMClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider  # "openai", "claude", "qwen"
        self.client = self._init_client(provider, api_key)
    
    async def generate_visualization_code(self, problem_text: str) -> dict:
        """调用大模型生成可视化代码"""
        pass
    
    def _build_prompt(self, problem_text: str) -> str:
        """构建完整的prompt"""
        pass
```

#### 代码沙箱
```python
class CodeSandbox:
    def __init__(self):
        self.allowed_modules = ['matplotlib', 'numpy', 'math', 'datetime']
        self.restricted_functions = ['open', 'exec', 'eval', '__import__']
    
    def validate_code(self, code: str) -> bool:
        """验证代码安全性"""
        pass
    
    def execute_code(self, code: str, output_path: str) -> dict:
        """在沙箱中安全执行代码"""
        pass
```

### 3. API接口修改

#### 新的数据模型
```python
class ProblemRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    llm_provider: Optional[str] = "openai"  # 允许用户选择模型
    advanced_mode: bool = False  # 是否使用AI模式

class AIAnalysisResult(BaseModel):
    problem_type: str
    parameters: Dict[str, Any]
    visualization_code: str
    explanation: str
    confidence: float  # AI分析的置信度

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    ai_analysis: Optional[AIAnalysisResult] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

---

## 🔄 处理流程设计

### 1. 智能题目处理流程

```python
async def process_ai_visualization_task(task_id: str, text: str, llm_provider: str):
    """AI驱动的可视化任务处理流程"""
    
    try:
        # 1. 更新任务状态
        update_task_status(task_id, "ai_analyzing", 10)
        
        # 2. 调用大模型分析题目
        llm_client = LLMClient(llm_provider)
        ai_result = await llm_client.generate_visualization_code(text)
        
        update_task_status(task_id, "code_validating", 30)
        
        # 3. 验证生成的代码
        sandbox = CodeSandbox()
        if not sandbox.validate_code(ai_result['visualization_code']):
            raise SecurityError("Generated code failed security check")
        
        update_task_status(task_id, "executing", 60)
        
        # 4. 执行代码生成图片
        image_id = str(uuid.uuid4())
        output_path = f"output/{image_id}.png"
        
        execution_result = sandbox.execute_code(
            ai_result['visualization_code'], 
            output_path
        )
        
        update_task_status(task_id, "completed", 100, {
            "image_id": image_id,
            "ai_analysis": ai_result,
            "execution_result": execution_result
        })
        
    except Exception as e:
        update_task_status(task_id, "failed", 0, error=str(e))
```

### 2. 兼容性处理

```python
@app.post("/api/v1/problems/generate")
async def generate_visualization(request: ProblemRequest, background_tasks: BackgroundTasks):
    """支持传统模式和AI模式的统一接口"""
    
    task_id = str(uuid.uuid4())
    
    if request.advanced_mode:
        # 使用AI模式
        background_tasks.add_task(
            process_ai_visualization_task,
            task_id, request.text, request.llm_provider
        )
    else:
        # 使用传统模式（向后兼容）
        background_tasks.add_task(
            process_traditional_visualization_task,
            task_id, request.text
        )
    
    return TaskResponse(
        task_id=task_id,
        mode="ai" if request.advanced_mode else "traditional"
    )
```

---

## 🛡️ 安全性设计

### 1. 代码安全验证
```python
class SecurityValidator:
    def __init__(self):
        self.forbidden_imports = [
            'os', 'sys', 'subprocess', 'socket', 'urllib',
            'requests', 'pickle', 'eval', 'exec'
        ]
        self.allowed_imports = [
            'matplotlib', 'numpy', 'math', 'datetime', 're'
        ]
    
    def validate_imports(self, code: str) -> bool:
        """验证import语句"""
        pass
    
    def validate_function_calls(self, code: str) -> bool:
        """验证函数调用"""
        pass
    
    def scan_malicious_patterns(self, code: str) -> bool:
        """扫描恶意代码模式"""
        pass
```

### 2. 资源限制
```python
class ResourceLimiter:
    def __init__(self):
        self.max_execution_time = 30  # 秒
        self.max_memory_usage = 512   # MB
        self.max_output_size = 10     # MB
    
    def execute_with_limits(self, code: str) -> dict:
        """在资源限制下执行代码"""
        pass
```

---

## 💡 前端界面改进

### 1. 新增AI模式切换
```javascript
// 模式切换组件
const ModeSelector = () => {
  return (
    <div className="mode-selector">
      <label>
        <input type="radio" name="mode" value="traditional" />
        传统模式（快速）
      </label>
      <label>
        <input type="radio" name="mode" value="ai" />
        AI模式（智能）
      </label>
    </div>
  );
};
```

### 2. 大模型选择
```javascript
const LLMSelector = ({ visible }) => {
  return visible ? (
    <select name="llm_provider">
      <option value="openai">OpenAI GPT</option>
      <option value="claude">Claude</option>
      <option value="qwen">通义千问</option>
    </select>
  ) : null;
};
```

### 3. AI分析结果展示
```javascript
const AIAnalysisDisplay = ({ analysis }) => {
  return (
    <div className="ai-analysis">
      <h4>🤖 AI分析结果</h4>
      <p><strong>题目类型：</strong>{analysis.problem_type}</p>
      <p><strong>关键参数：</strong>{JSON.stringify(analysis.parameters)}</p>
      <p><strong>可视化思路：</strong>{analysis.explanation}</p>
      <p><strong>置信度：</strong>{(analysis.confidence * 100).toFixed(1)}%</p>
    </div>
  );
};
```

---

## 📊 成本与性能分析

### 1. API调用成本
- **OpenAI GPT-4**: ~$0.03-0.06/题目
- **GPT-3.5-turbo**: ~$0.002-0.004/题目
- **Claude**: ~$0.015-0.075/题目
- **通义千问**: ~¥0.01-0.05/题目

### 2. 性能预估
- **AI分析时间**: 2-8秒
- **代码执行时间**: 1-3秒
- **总处理时间**: 3-12秒
- **并发处理**: 建议限制在10个并发AI请求

### 3. 优化策略
- **缓存机制**: 相似题目复用分析结果
- **模型降级**: 简单题目使用便宜模型
- **批处理**: 多题目批量处理
- **预生成**: 常见题型预生成模板

---

## 🚀 实施计划

### 阶段1：基础架构 (1-2周)
1. 设计和实现LLM客户端
2. 构建代码沙箱和安全验证
3. 修改API接口支持双模式

### 阶段2：AI集成 (1-2周)
1. 集成OpenAI API
2. 设计和优化Prompt
3. 实现代码生成和执行流程

### 阶段3：前端改进 (1周)
1. 添加模式选择界面
2. 实现AI分析结果展示
3. 优化用户体验

### 阶段4：测试与优化 (1周)
1. 全面测试各种题型
2. 性能优化和安全加固
3. 成本控制和监控

---

## ❓ 待确认问题

1. **大模型选择**：优先集成哪个模型？
2. **成本控制**：每月AI调用预算是多少？
3. **安全级别**：代码执行的安全要求有多严格？
4. **性能要求**：可接受的最大响应时间？
5. **功能范围**：除了数学题，是否考虑其他学科？

---

## 🎯 预期效果

### 系统能力提升
- ✅ 支持任意类型的数学应用题
- ✅ 自动理解题目语义和结构
- ✅ 生成个性化的可视化方案
- ✅ 无需硬编码新题型

### 用户体验改善
- 🎨 更丰富的可视化样式
- 🧠 更智能的题目理解
- 📈 更准确的参数提取
- 🔄 更快的功能迭代

这个设计方案如何？你觉得哪些部分需要调整或补充？
