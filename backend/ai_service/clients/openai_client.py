#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI客户端实现
支持OpenAI API和兼容的API（如Moonshot）
"""

import time
import os
from typing import Dict, Any, Optional

try:
    import openai
except ImportError:
    openai = None

from .base_client import BaseLLMClient
from backend.models.schema import LLMResponse

class OpenAIClient(BaseLLMClient):
    """OpenAI客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, base_url, **kwargs)
        
        if openai is None:
            raise ImportError("请安装openai库: pip install openai")
        
        # 构建客户端参数
        client_kwargs = {
            "api_key": api_key
        }
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = openai.AsyncOpenAI(**client_kwargs)
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        # 从环境变量读取默认模型
        env_model = os.getenv("OPENAI_DEFAULT_MODEL")
        if env_model:
            return env_model
            
        # 根据base_url自动检测
        if self.base_url and "moonshot" in self.base_url:
            return "kimi-k2-0711-preview"
        return "gpt-3.5-turbo"
    
    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        if self.base_url and "moonshot" in self.base_url:
            return [
                "kimi-k2-0711-preview",
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k"
            ]
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成OpenAI completion"""
        start_time = time.time()
        
        try:
            model = config.get("model", self.get_default_model())
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.get("temperature", 0.3),
                max_tokens=config.get("max_tokens", 2000)
            )
            
            response_time = time.time() - start_time
            
            usage_stats = {}
            if response.usage:
                usage_stats = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return self._build_success_response(
                content=response.choices[0].message.content,
                usage_stats=usage_stats,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return self._build_error_response(e, system_prompt, user_prompt, response_time)
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            await self.client.chat.completions.create(
                model=self.get_default_model(),
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
