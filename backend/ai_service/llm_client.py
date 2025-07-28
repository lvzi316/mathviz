#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型客户端
支持多个主流LLM提供商
"""

import json
import time
import asyncio
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# 导入各个模型的客户端库
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import requests
except ImportError:
    requests = None

from backend.models.schema import LLMProvider, LLMResponse
from backend.ai_service.prompt_templates import get_prompt_manager, get_model_config_for_provider

class BaseLLMClient(ABC):
    """大模型客户端基类"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.extra_config = kwargs
    
    @abstractmethod
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """
        生成completion
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            config: 模型配置
            
        Returns:
            LLMResponse: 响应结果
        """
        pass

class OpenAIClient(BaseLLMClient):
    """OpenAI客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        
        if openai is None:
            raise ImportError("请安装openai库: pip install openai")
        
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成OpenAI completion"""
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=config.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.get("temperature", 0.3),
                max_tokens=config.get("max_tokens", 2000),
                response_format={"type": "json_object"}  # 强制JSON格式
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                success=True,
                content=response.choices[0].message.content,
                usage_stats={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return LLMResponse(
                success=False,
                content="",
                response_time=response_time,
                error_message=str(e)
            )

class ClaudeClient(BaseLLMClient):
    """Claude客户端"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        
        if anthropic is None:
            raise ImportError("请安装anthropic库: pip install anthropic")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成Claude completion"""
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=config.get("model", "claude-3-sonnet-20240229"),
                max_tokens=config.get("max_tokens", 2000),
                temperature=config.get("temperature", 0.3),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                success=True,
                content=response.content[0].text,
                usage_stats={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return LLMResponse(
                success=False,
                content="",
                response_time=response_time,
                error_message=str(e)
            )

class QwenClient(BaseLLMClient):
    """通义千问客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/api/v1", **kwargs):
        super().__init__(api_key, **kwargs)
        
        if requests is None:
            raise ImportError("请安装requests库: pip install requests")
        
        self.base_url = base_url
    
    async def generate_completion(self, system_prompt: str, user_prompt: str, 
                                config: Dict[str, Any]) -> LLMResponse:
        """生成通义千问completion"""
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": config.get("model", "qwen-max"),
                "input": {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                },
                "parameters": {
                    "temperature": config.get("temperature", 0.3),
                    "max_tokens": config.get("max_tokens", 2000),
                    "result_format": "json_object"
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
                return LLMResponse(
                    success=True,
                    content=result["output"]["text"],
                    usage_stats={
                        "input_tokens": result["usage"]["input_tokens"],
                        "output_tokens": result["usage"]["output_tokens"],
                        "total_tokens": result["usage"]["total_tokens"]
                    },
                    response_time=response_time
                )
            else:
                return LLMResponse(
                    success=False,
                    content="",
                    response_time=response_time,
                    error_message=f"API调用失败: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return LLMResponse(
                success=False,
                content="",
                response_time=response_time,
                error_message=str(e)
            )

class LLMClientFactory:
    """LLM客户端工厂"""
    
    _clients: Dict[LLMProvider, BaseLLMClient] = {}
    
    @classmethod
    def create_client(cls, provider: LLMProvider, api_key: str, **kwargs) -> BaseLLMClient:
        """
        创建LLM客户端
        
        Args:
            provider: 提供商
            api_key: API密钥
            **kwargs: 其他配置
            
        Returns:
            BaseLLMClient: 客户端实例
        """
        if provider == LLMProvider.OPENAI:
            return OpenAIClient(api_key, **kwargs)
        elif provider == LLMProvider.CLAUDE:
            return ClaudeClient(api_key, **kwargs)
        elif provider == LLMProvider.QWEN:
            return QwenClient(api_key, **kwargs)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
    
    @classmethod
    def get_or_create_client(cls, provider: LLMProvider, api_key: str, **kwargs) -> BaseLLMClient:
        """
        获取或创建客户端（带缓存）
        
        Args:
            provider: 提供商
            api_key: API密钥
            **kwargs: 其他配置
            
        Returns:
            BaseLLMClient: 客户端实例
        """
        if provider not in cls._clients:
            cls._clients[provider] = cls.create_client(provider, api_key, **kwargs)
        
        return cls._clients[provider]

class LLMManager:
    """LLM管理器"""
    
    def __init__(self):
        """初始化LLM管理器"""
        self.api_keys: Dict[LLMProvider, str] = {}
        self.prompt_manager = get_prompt_manager()
    
    def set_api_key(self, provider: LLMProvider, api_key: str):
        """
        设置API密钥
        
        Args:
            provider: 提供商
            api_key: API密钥
        """
        self.api_keys[provider] = api_key
    
    async def generate_visualization_code(self, problem_text: str, output_path: str,
                                        provider: LLMProvider = LLMProvider.OPENAI,
                                        template_name: str = "math_visualization",
                                        variant: str = "default") -> LLMResponse:
        """
        生成可视化代码
        
        Args:
            problem_text: 题目文本
            output_path: 输出路径
            provider: 模型提供商
            template_name: 模板名称
            variant: 模板变体
            
        Returns:
            LLMResponse: 生成结果
        """
        if provider not in self.api_keys:
            return LLMResponse(
                success=False,
                content="",
                error_message=f"未设置{provider.value}的API密钥"
            )
        
        try:
            # 获取prompt模板
            template = self.prompt_manager.get_template(template_name, variant)
            user_prompt = self.prompt_manager.render_user_prompt(
                template_name, variant,
                problem_text=problem_text,
                output_path=output_path
            )
            
            # 获取模型配置
            model_config = self.prompt_manager.get_model_config(template_name, provider)
            
            # 创建客户端
            client = LLMClientFactory.get_or_create_client(
                provider, 
                self.api_keys[provider]
            )
            
            # 生成completion
            response = await client.generate_completion(
                system_prompt=template.system_prompt,
                user_prompt=user_prompt,
                config=model_config
            )
            
            return response
            
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                error_message=f"生成失败: {str(e)}"
            )
    
    def get_available_providers(self) -> list[LLMProvider]:
        """获取已配置的提供商列表"""
        return list(self.api_keys.keys())
    
    async def test_connection(self, provider: LLMProvider) -> bool:
        """
        测试连接
        
        Args:
            provider: 提供商
            
        Returns:
            bool: 连接是否成功
        """
        try:
            response = await self.generate_visualization_code(
                problem_text="测试题目：1+1=?",
                output_path="test.png",
                provider=provider,
                variant="simple_mode"
            )
            return response.success
        except Exception:
            return False

# 全局LLM管理器
llm_manager = LLMManager()

def get_llm_manager() -> LLMManager:
    """获取全局LLM管理器"""
    return llm_manager

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        manager = get_llm_manager()
        
        # 设置API密钥（请替换为实际密钥）
        manager.set_api_key(LLMProvider.OPENAI, "your-openai-api-key")
        
        # 测试生成
        response = await manager.generate_visualization_code(
            problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
            output_path="output/test.png"
        )
        
        print(f"成功: {response.success}")
        if response.success:
            print(f"内容: {response.content[:200]}...")
            print(f"用量: {response.usage_stats}")
        else:
            print(f"错误: {response.error_message}")
    
    asyncio.run(test())
