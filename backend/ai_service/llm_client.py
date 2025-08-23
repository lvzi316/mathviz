#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型客户端管理器
使用新的模块化客户端架构
"""

import time
from typing import Dict, Any, Optional, List

from backend.models.schema import LLMProvider, LLMResponse
from backend.ai_service.prompt_templates import get_prompt_manager
from backend.config import get_config_manager

# 导入所有客户端
from backend.ai_service.clients.base_client import BaseLLMClient
from backend.ai_service.clients.openai_client import OpenAIClient
from backend.ai_service.clients.claude_client import ClaudeClient
from backend.ai_service.clients.qwen_client import QwenClient
from backend.ai_service.clients.deepseek_client import DeepSeekClient

class LLMClientFactory:
    """LLM客户端工厂"""
    
    _clients: Dict[LLMProvider, BaseLLMClient] = {}
    
    @classmethod
    def create_client(cls, provider: LLMProvider, api_key: str, base_url: Optional[str] = None, **kwargs) -> BaseLLMClient:
        """
        创建LLM客户端
        
        Args:
            provider: 提供商
            api_key: API密钥
            base_url: API基础URL
            **kwargs: 其他配置
            
        Returns:
            BaseLLMClient: 客户端实例
        """
        if provider == LLMProvider.OPENAI:
            return OpenAIClient(api_key=api_key, base_url=base_url, **kwargs)
        elif provider == LLMProvider.CLAUDE:
            return ClaudeClient(api_key=api_key, base_url=base_url, **kwargs)
        elif provider == LLMProvider.QWEN:
            return QwenClient(api_key=api_key, base_url=base_url, **kwargs)
        elif provider == LLMProvider.DEEPSEEK:
            return DeepSeekClient(api_key=api_key, base_url=base_url, **kwargs)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
    
    @classmethod
    def get_or_create_client(cls, provider: LLMProvider, api_key: str, 
                           base_url: Optional[str] = None, **kwargs) -> BaseLLMClient:
        """
        获取或创建客户端（带缓存）
        
        Args:
            provider: 提供商
            api_key: API密钥
            base_url: API基础URL
            **kwargs: 其他配置
            
        Returns:
            BaseLLMClient: 客户端实例
        """
        # 创建缓存key，包含provider和关键配置
        cache_key = f"{provider.value}_{hash((api_key, base_url))}"
        
        if cache_key not in cls._clients:
            cls._clients[cache_key] = cls.create_client(provider, api_key, base_url, **kwargs)
        
        return cls._clients[cache_key]
    
    @classmethod
    def clear_cache(cls):
        """清除客户端缓存"""
        cls._clients.clear()
    
    @classmethod
    def get_supported_providers(cls) -> List[LLMProvider]:
        """获取支持的提供商列表"""
        return [
            LLMProvider.OPENAI,
            LLMProvider.CLAUDE,
            LLMProvider.QWEN,
            LLMProvider.DEEPSEEK
        ]

class LLMManager:
    """LLM管理器 - 统一管理所有LLM客户端"""
    
    def __init__(self):
        """初始化LLM管理器"""
        self.config_manager = get_config_manager()
        self.prompt_manager = get_prompt_manager()
        
        # 从配置管理器加载API密钥
        self.api_keys: Dict[LLMProvider, str] = {}
        self._load_api_keys_from_config()
    
    def _load_api_keys_from_config(self):
        """从配置管理器加载API密钥"""
        for provider in LLMProvider:
            api_key = self.config_manager.get_api_key(provider)
            if api_key:
                self.api_keys[provider] = api_key
    
    def set_api_key(self, provider: LLMProvider, api_key: str):
        """
        设置API密钥
        
        Args:
            provider: 提供商
            api_key: API密钥
        """
        self.api_keys[provider] = api_key
        # 同时更新配置管理器
        self.config_manager.set_api_key(provider, api_key)
        # 清除缓存，强制重新创建客户端
        LLMClientFactory.clear_cache()
    
    def get_configured_providers(self) -> List[LLMProvider]:
        """获取已配置的提供商列表"""
        return self.config_manager.get_configured_providers()
    
    def get_default_provider(self) -> LLMProvider:
        """获取默认提供商"""
        return self.config_manager.get_default_provider()
    
    def get_available_providers(self) -> List[LLMProvider]:
        """获取可用的提供商列表（包括支持但未配置的）"""
        return LLMClientFactory.get_supported_providers()
    
    async def test_connection(self, provider: LLMProvider) -> bool:
        """
        测试提供商连接
        
        Args:
            provider: 提供商
            
        Returns:
            bool: 连接是否成功
        """
        if provider not in self.api_keys:
            return False
        
        try:
            # 获取base URL配置
            base_url = self.config_manager.get_base_url(provider)
            
            # 创建客户端
            client = LLMClientFactory.get_or_create_client(
                provider=provider, 
                api_key=self.api_keys[provider],
                base_url=base_url
            )
            
            # 使用客户端的测试连接方法
            return await client.test_connection()
            
        except Exception as e:
            print(f"测试连接失败 - {provider.value}: {str(e)}")
            return False
    
    async def generate_visualization_code(self, problem_text: str, output_path: str,
                                        provider: Optional[LLMProvider] = None,
                                        template_name: str = "math_visualization",
                                        variant: str = "default") -> LLMResponse:
        """
        生成可视化代码
        
        Args:
            problem_text: 题目文本
            output_path: 输出路径
            provider: 模型提供商（如果不指定则使用默认）
            template_name: 模板名称
            variant: 模板变体
            
        Returns:
            LLMResponse: 生成结果
        """
        # 确定使用的提供商
        if provider is None:
            provider = self.get_default_provider()
        
        # 检查API密钥
        if provider not in self.api_keys:
            return LLMResponse(
                success=False,
                content="",
                error_message=f"未配置{provider.value}的API密钥，请在环境变量中设置或通过API配置",
                system_prompt="",
                user_prompt="",
                full_prompt=""
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
            
            # 获取base URL配置
            base_url = self.config_manager.get_base_url(provider)
            
            # 创建客户端
            client = LLMClientFactory.get_or_create_client(
                provider=provider, 
                api_key=self.api_keys[provider],
                base_url=base_url
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
                error_message=f"生成失败: {str(e)}",
                system_prompt="",
                user_prompt="",
                full_prompt=""
            )
    
    def get_provider_info(self, provider: LLMProvider) -> Dict[str, Any]:
        """
        获取提供商信息
        
        Args:
            provider: 提供商
            
        Returns:
            Dict[str, Any]: 提供商信息
        """
        try:
            # 获取base URL配置
            base_url = self.config_manager.get_base_url(provider)
            
            # 创建临时客户端以获取支持的模型
            if provider in self.api_keys:
                client = LLMClientFactory.create_client(
                    provider=provider,
                    api_key=self.api_keys[provider],
                    base_url=base_url
                )
                
                supported_models = client.get_supported_models()
                default_model = client.get_default_model()
            else:
                supported_models = []
                default_model = "未配置"
            
            return {
                "provider": provider.value,
                "configured": provider in self.api_keys,
                "base_url": base_url,
                "default_model": default_model,
                "supported_models": supported_models
            }
            
        except Exception as e:
            return {
                "provider": provider.value,
                "configured": provider in self.api_keys,
                "base_url": base_url,
                "default_model": "获取失败",
                "supported_models": [],
                "error": str(e)
            }
    
    def get_all_providers_info(self) -> List[Dict[str, Any]]:
        """获取所有提供商信息"""
        return [
            self.get_provider_info(provider) 
            for provider in self.get_available_providers()
        ]

# 全局LLM管理器实例
llm_manager = LLMManager()

def get_llm_manager() -> LLMManager:
    """获取全局LLM管理器"""
    return llm_manager

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        manager = get_llm_manager()
        
        print("可用提供商:", [p.value for p in manager.get_available_providers()])
        print("已配置提供商:", [p.value for p in manager.get_configured_providers()])
        
        # 获取所有提供商信息
        providers_info = manager.get_all_providers_info()
        for info in providers_info:
            print(f"\n{info['provider']}:")
            print(f"  已配置: {info['configured']}")
            print(f"  默认模型: {info['default_model']}")
            print(f"  支持的模型: {info['supported_models'][:3]}...")  # 只显示前3个
        
        # 如果有配置的提供商，测试生成
        configured = manager.get_configured_providers()
        if configured:
            provider = configured[0]
            print(f"\n使用 {provider.value} 测试生成...")
            
            response = await manager.generate_visualization_code(
                problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
                output_path="output/test.png",
                provider=provider
            )
            
            print(f"成功: {response.success}")
            if response.success:
                print(f"内容: {response.content[:200]}...")
                print(f"用量: {response.usage_stats}")
            else:
                print(f"错误: {response.error_message}")
        else:
            print("\n没有配置的提供商，请设置API密钥")
    
    asyncio.run(test())
