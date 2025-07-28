#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class LLMProvider(str, Enum):
    """大模型提供商"""
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    GEMINI = "gemini"

class ProcessingMode(str, Enum):
    """处理模式"""
    TRADITIONAL = "traditional"
    AI = "ai"

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    AI_ANALYZING = "ai_analyzing"
    CODE_VALIDATING = "code_validating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProblemRequest(BaseModel):
    """题目处理请求"""
    text: str = Field(..., description="题目文本", min_length=10, max_length=2000)
    user_id: Optional[str] = Field(None, description="用户ID")
    llm_provider: LLMProvider = Field(LLMProvider.OPENAI, description="大模型提供商")
    processing_mode: ProcessingMode = Field(ProcessingMode.AI, description="处理模式")
    prompt_variant: str = Field("default", description="Prompt变体")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？",
                "user_id": "user123",
                "llm_provider": "openai",
                "processing_mode": "ai",
                "prompt_variant": "detailed_mode"
            }
        }
    }

class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    problem_type: str = Field(..., description="题目类型")
    parameters: Dict[str, Any] = Field(..., description="提取的参数")
    visualization_code: str = Field(..., description="可视化代码")
    explanation: str = Field(..., description="可视化思路说明")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="AI分析的置信度")
    processing_time: float = Field(0.0, description="处理时间（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "problem_type": "行程问题-相遇",
                "parameters": {
                    "distance": 480,
                    "speed1": 60,
                    "speed2": 80
                },
                "visualization_code": "import matplotlib.pyplot as plt\n# ... 完整代码 ...",
                "explanation": "绘制相遇问题的场景图和位置-时间图",
                "confidence": 0.95,
                "processing_time": 3.2
            }
        }
    }

class ExecutionResult(BaseModel):
    """代码执行结果"""
    success: bool = Field(..., description="执行是否成功")
    image_path: Optional[str] = Field(None, description="生成的图片路径")
    result_data: Optional[Dict[str, Any]] = Field(None, description="计算结果数据")
    execution_time: float = Field(0.0, description="执行时间（秒）")
    memory_usage: float = Field(0.0, description="内存使用（MB）")
    error_message: Optional[str] = Field(None, description="错误信息")
    output_logs: str = Field("", description="执行日志")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "image_path": "output/abc123.png",
                "result_data": {
                    "meeting_time": 3.43,
                    "meeting_point": 205.7,
                    "distance": 480,
                    "speed1": 60,
                    "speed2": 80
                },
                "execution_time": 1.5,
                "memory_usage": 45.2,
                "error_message": None,
                "output_logs": "图片已保存到指定路径"
            }
        }
    }

class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(0, ge=0, le=100, description="进度百分比")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    processing_mode: ProcessingMode = Field(..., description="处理模式")
    llm_provider: Optional[LLMProvider] = Field(None, description="使用的大模型")
    
    # 结果数据
    ai_analysis: Optional[AIAnalysisResult] = Field(None, description="AI分析结果")
    execution_result: Optional[ExecutionResult] = Field(None, description="执行结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_abc123",
                "status": "completed",
                "progress": 100,
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:05Z",
                "processing_mode": "ai",
                "llm_provider": "openai"
            }
        }
    }

class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="初始状态")
    message: str = Field(..., description="响应消息")
    estimated_time: int = Field(..., description="预估处理时间（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": "task_abc123",
                "status": "pending",
                "message": "任务已创建，正在处理中...",
                "estimated_time": 10
            }
        }
    }

class CodeValidationResult(BaseModel):
    """代码验证结果"""
    is_valid: bool = Field(..., description="代码是否有效")
    security_issues: List[str] = Field(default_factory=list, description="安全问题列表")
    syntax_errors: List[str] = Field(default_factory=list, description="语法错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    validation_time: float = Field(0.0, description="验证时间（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "is_valid": True,
                "security_issues": [],
                "syntax_errors": [],
                "warnings": ["使用了大量内存"],
                "validation_time": 0.5
            }
        }
    }

class PromptTemplate(BaseModel):
    """Prompt模板"""
    system_prompt: str = Field(..., description="系统提示词")
    user_prompt_template: str = Field(..., description="用户提示词模板")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="模型配置")
    
class LLMResponse(BaseModel):
    """大模型响应"""
    success: bool = Field(..., description="调用是否成功")
    content: str = Field(..., description="响应内容")
    usage_stats: Dict[str, Any] = Field(default_factory=dict, description="使用统计")
    response_time: float = Field(0.0, description="响应时间（秒）")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "content": '{"problem_type": "行程问题-相遇", ...}',
                "usage_stats": {
                    "prompt_tokens": 150,
                    "completion_tokens": 300,
                    "total_tokens": 450
                },
                "response_time": 2.5,
                "error_message": None
            }
        }
    }

class SystemConfig(BaseModel):
    """系统配置"""
    max_concurrent_tasks: int = Field(10, description="最大并发任务数")
    max_execution_time: int = Field(30, description="最大执行时间（秒）")
    max_memory_usage: int = Field(512, description="最大内存使用（MB）")
    allowed_file_extensions: List[str] = Field(default_factory=lambda: [".png", ".jpg", ".svg"], description="允许的文件扩展名")
    sandbox_enabled: bool = Field(True, description="是否启用沙箱")
    
class HealthStatus(BaseModel):
    """健康状态"""
    status: str = Field(..., description="服务状态")
    timestamp: str = Field(..., description="检查时间")
    version: str = Field(..., description="版本号")
    active_tasks: int = Field(0, description="活跃任务数")
    total_processed: int = Field(0, description="总处理数量")
    avg_processing_time: float = Field(0.0, description="平均处理时间")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T10:00:00Z",
                "version": "2.0.0",
                "active_tasks": 3,
                "total_processed": 1250,
                "avg_processing_time": 5.2
            }
        }
    }
