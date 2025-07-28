#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务模块
包含大模型客户端、Prompt模板管理和代码生成器
"""

from .llm_client import (
    BaseLLMClient,
    OpenAIClient,
    ClaudeClient,
    QwenClient,
    LLMClientFactory,
    LLMManager,
    get_llm_manager
)

from .prompt_templates import (
    PromptTemplateManager,
    get_prompt_manager,
    render_prompt,
    get_model_config_for_provider
)

from .code_generator import (
    CodeGenerator,
    get_code_generator
)

__all__ = [
    # LLM客户端
    'BaseLLMClient',
    'OpenAIClient', 
    'ClaudeClient',
    'QwenClient',
    'LLMClientFactory',
    'LLMManager',
    'get_llm_manager',
    
    # Prompt模板
    'PromptTemplateManager',
    'get_prompt_manager',
    'render_prompt',
    'get_model_config_for_provider',
    
    # 代码生成器
    'CodeGenerator',
    'get_code_generator'
]
