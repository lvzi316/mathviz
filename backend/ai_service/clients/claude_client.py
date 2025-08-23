#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude客户端实现
支持Anthropic Claude API
"""

import time
import os
from typing import Dict, Any, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from .base_client import BaseLLMClient
from backend.models.schema import LLMResponse

class ClaudeClient(BaseLLMClient):
    """Claude客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, base_url, **kwargs)
        
        if anthropic is None:
            raise ImportError("请安装anthropic库: pip install anthropic")
        
        # 构建客户端参数
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = anthropic.AsyncAnthropic(**client_kwargs)
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        # 从环境变量读取默认模型
        env_model = os.getenv("CLAUDE_DEFAULT_MODEL")
        if env_model:
            return env_model
            
        # 如果是Moonshot的Claude兼容API，使用Moonshot的模型名称
        if self.base_url and "moonshot" in self.base_url.lower():
            return "kimi-k2-0711-preview"  # Moonshot的默认模型
        return "claude-3-5-sonnet-20241022"
    
    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        # 如果是Moonshot的Claude兼容API，返回Moonshot支持的模型
        if self.base_url and "moonshot" in self.base_url.lower():
            return [
                "kimi-k2-0711-preview",
                "moonshot-v1-8k",
                "moonshot-v1-32k", 
                "moonshot-v1-128k"
            ]
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022", 
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成Claude completion"""
        start_time = time.time()
        
        try:
            model = config.get("model", self.get_default_model())
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=config.get("max_tokens", 2000),
                temperature=config.get("temperature", 0.3),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_time = time.time() - start_time
            
            usage_stats = {}
            if response.usage:
                usage_stats = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            
            return self._build_success_response(
                content=response.content[0].text,
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
            # 使用适当的默认模型进行连接测试
            default_model = self.get_default_model()
            await self.client.messages.create(
                model=default_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            print(f"Claude客户端连接测试失败: {str(e)}")
            return False
