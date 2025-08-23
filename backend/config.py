#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
负责管理API密钥和其他配置
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from backend.models.schema import LLMProvider

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 加载环境变量
        load_dotenv()
        
        # API密钥配置
        self.api_keys: Dict[LLMProvider, Optional[str]] = {
            LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY"),
            LLMProvider.CLAUDE: os.getenv("CLAUDE_API_KEY"),
            LLMProvider.QWEN: os.getenv("QWEN_API_KEY"),
            LLMProvider.DEEPSEEK: os.getenv("DEEPSEEK_API_KEY"),
            LLMProvider.GEMINI: os.getenv("GEMINI_API_KEY"),
        }
        
        # Base URL配置
        self.base_urls: Dict[LLMProvider, Optional[str]] = {
            LLMProvider.OPENAI: os.getenv("OPENAI_BASE_URL"),
            LLMProvider.CLAUDE: os.getenv("CLAUDE_BASE_URL"),
            LLMProvider.QWEN: os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
            LLMProvider.DEEPSEEK: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            LLMProvider.GEMINI: os.getenv("GEMINI_BASE_URL"),
        }
        
        # 默认提供商
        default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
        try:
            self.default_provider = LLMProvider(default_provider)
        except ValueError:
            self.default_provider = LLMProvider.OPENAI
        
        # 其他配置
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """
        获取指定提供商的API密钥
        
        Args:
            provider: LLM提供商
            
        Returns:
            Optional[str]: API密钥，如果未配置则返回None
        """
        return self.api_keys.get(provider)
    
    def get_base_url(self, provider: LLMProvider) -> Optional[str]:
        """
        获取指定提供商的Base URL
        
        Args:
            provider: LLM提供商
            
        Returns:
            Optional[str]: Base URL，如果未配置则返回None
        """
        return self.base_urls.get(provider)
    
    def set_api_key(self, provider: LLMProvider, api_key: str):
        """
        设置API密钥
        
        Args:
            provider: LLM提供商
            api_key: API密钥
        """
        self.api_keys[provider] = api_key
    
    def set_base_url(self, provider: LLMProvider, base_url: str):
        """
        设置Base URL
        
        Args:
            provider: LLM提供商
            base_url: Base URL
        """
        self.base_urls[provider] = base_url
    
    def is_provider_configured(self, provider: LLMProvider) -> bool:
        """
        检查提供商是否已配置
        
        Args:
            provider: LLM提供商
            
        Returns:
            bool: 是否已配置
        """
        api_key = self.get_api_key(provider)
        return api_key is not None and api_key.strip() != ""
    
    def get_configured_providers(self) -> list[LLMProvider]:
        """
        获取已配置的提供商列表
        
        Returns:
            list[LLMProvider]: 已配置的提供商列表
        """
        return [
            provider for provider in LLMProvider
            if self.is_provider_configured(provider)
        ]
    
    def get_default_provider(self) -> LLMProvider:
        """
        获取默认提供商
        
        Returns:
            LLMProvider: 默认提供商
        """
        # 如果默认提供商已配置，则返回
        if self.is_provider_configured(self.default_provider):
            return self.default_provider
        
        # 否则返回第一个已配置的提供商
        configured = self.get_configured_providers()
        if configured:
            return configured[0]
        
        # 如果都没配置，返回OpenAI
        return LLMProvider.OPENAI
    
    def validate_config(self) -> Dict[str, bool]:
        """
        验证配置
        
        Returns:
            Dict[str, bool]: 验证结果
        """
        results = {}
        
        # 检查每个提供商的配置
        for provider in LLMProvider:
            results[f"{provider.value}_configured"] = self.is_provider_configured(provider)
        
        # 检查是否至少有一个提供商配置了
        results["has_any_provider"] = len(self.get_configured_providers()) > 0
        
        # 检查默认提供商是否可用
        results["default_provider_available"] = self.is_provider_configured(self.get_default_provider())
        
        return results
    
    def get_config_summary(self) -> Dict[str, any]:
        """
        获取配置摘要
        
        Returns:
            Dict[str, any]: 配置摘要
        """
        configured_providers = self.get_configured_providers()
        
        # 构建提供商配置详情
        provider_details = {}
        for provider in LLMProvider:
            provider_details[provider.value] = {
                "api_key_configured": self.is_provider_configured(provider),
                "base_url": self.get_base_url(provider)
            }
        
        return {
            "environment": self.environment,
            "debug": self.debug,
            "default_provider": self.default_provider.value,
            "configured_providers": [p.value for p in configured_providers],
            "total_configured": len(configured_providers),
            "provider_details": provider_details,
            "validation": self.validate_config()
        }

# 全局配置管理器实例
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    return config_manager
