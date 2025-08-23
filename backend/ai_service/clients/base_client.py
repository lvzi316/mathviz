#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM客户端基类
提供所有LLM客户端的通用接口和功能
"""

import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from backend.models.schema import LLMResponse

class BaseLLMClient(ABC):
    """大模型客户端基类"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            base_url: 自定义API地址
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.base_url = base_url
        self.extra_config = kwargs
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.api_key:
            raise ValueError("API密钥不能为空")
    
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
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        获取默认模型名称
        
        Returns:
            str: 默认模型名称
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> list[str]:
        """
        获取支持的模型列表
        
        Returns:
            list[str]: 支持的模型列表
        """
        pass
    
    def _build_full_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """构建完整的prompt"""
        return f"System: {system_prompt}\n\nUser: {user_prompt}"
    
    def _build_error_response(self, error: Exception, system_prompt: str, 
                            user_prompt: str, response_time: float) -> LLMResponse:
        """构建错误响应"""
        return LLMResponse(
            success=False,
            content="",
            response_time=response_time,
            error_message=str(error),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            full_prompt=self._build_full_prompt(system_prompt, user_prompt)
        )
    
    def _build_success_response(self, content: str, usage_stats: Dict[str, Any],
                              system_prompt: str, user_prompt: str, 
                              response_time: float) -> LLMResponse:
        """构建成功响应"""
        return LLMResponse(
            success=True,
            content=content,
            usage_stats=usage_stats,
            response_time=response_time,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            full_prompt=self._build_full_prompt(system_prompt, user_prompt)
        )
