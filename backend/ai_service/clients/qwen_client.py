#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen客户端实现
支持阿里云通义千问API
"""

import time
import os
import asyncio
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    requests = None

try:
    import openai
except ImportError:
    openai = None

from .base_client import BaseLLMClient
from backend.models.schema import LLMResponse

class QwenClient(BaseLLMClient):
    """通义千问客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, base_url, **kwargs)
        
        self.base_url = base_url or "https://dashscope.aliyuncs.com/api/v1"
        
        # 检测是否使用OpenAI兼容模式
        self.is_compatible_mode = "compatible-mode" in self.base_url
        
        if self.is_compatible_mode:
            if openai is None:
                raise ImportError("使用兼容模式需要安装openai库: pip install openai")
            
            # 使用OpenAI客户端进行兼容模式调用
            self.openai_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            if requests is None:
                raise ImportError("请安装requests库: pip install requests")
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        # 从环境变量读取默认模型
        env_model = os.getenv("QWEN_DEFAULT_MODEL")
        if env_model:
            return env_model
        return "qwen3-coder-plus"
    
    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        return [
            "qwen-plus",
            "qwen3-coder-plus",
        ]
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成Qwen completion"""
        start_time = time.time()
        
        try:
            model = config.get("model", self.get_default_model())
            
            if self.is_compatible_mode:
                # 使用OpenAI兼容模式
                response = await self.openai_client.chat.completions.create(
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
            else:
                # 使用原生Qwen API
                return await self._generate_native_completion(
                    system_prompt, user_prompt, config, model, start_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return self._build_error_response(e, system_prompt, user_prompt, response_time)
    
    async def _generate_native_completion(self, system_prompt: str, user_prompt: str, 
                                        config: Dict[str, Any], model: str, start_time: float) -> LLMResponse:
        """使用原生Qwen API生成completion"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            },
            "parameters": {
                "temperature": config.get("temperature", 0.3),
                "max_tokens": config.get("max_tokens", 2000),
                "result_format": "message"
            }
        }
        
        # 使用asyncio运行同步请求
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=60
            )
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("output") and result["output"].get("choices"):
                content = result["output"]["choices"][0]["message"]["content"]
                usage_stats = {}
                if "usage" in result:
                    usage_stats = {
                        "input_tokens": result["usage"].get("input_tokens", 0),
                        "output_tokens": result["usage"].get("output_tokens", 0), 
                        "total_tokens": result["usage"].get("total_tokens", 0)
                    }
                
                return self._build_success_response(
                    content=content,
                    usage_stats=usage_stats,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_time=response_time
                )
            else:
                raise Exception(f"API响应格式错误: {result}")
        else:
            raise Exception(f"API请求失败: {response.status_code} - {response.text}")
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            print(f"测试Qwen连接 - API Key: {self.api_key[:10]}...")
            print(f"测试Qwen连接 - Base URL: {self.base_url}")
            print(f"兼容模式: {self.is_compatible_mode}")
            
            response = await self.generate_completion("你是一个助手", "测试", {"max_tokens": 1})
            print(f"测试响应: success={response.success}")
            if not response.success:
                print(f"测试错误: {response.error_message}")
            return response.success
        except Exception as e:
            print(f"测试异常: {str(e)}")
            return False
