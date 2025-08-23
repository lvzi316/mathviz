#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek客户端实现
支持DeepSeek API（OpenAI兼容格式）
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

class DeepSeekClient(BaseLLMClient):
    """DeepSeek客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, base_url, **kwargs)
        
        if openai is None:
            raise ImportError("请安装openai库: pip install openai")
        
        # DeepSeek使用自己的API端点
        api_base = base_url or "https://api.deepseek.com/v1"
        
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        # 从环境变量读取默认模型
        env_model = os.getenv("DEEPSEEK_DEFAULT_MODEL")
        if env_model:
            return env_model
        return "deepseek-v3.1"
    
    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        return [
            "deepseek-v3.1",
            "deepseek-r1"
        ]
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成DeepSeek completion"""
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
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
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
