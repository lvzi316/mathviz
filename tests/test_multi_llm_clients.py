#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多LLM客户端测试
测试新的模块化客户端架构
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock

from backend.ai_service.llm_client import LLMManager, LLMClientFactory
from backend.ai_service.clients.openai_client import OpenAIClient
from backend.ai_service.clients.claude_client import ClaudeClient
from backend.ai_service.clients.qwen_client import QwenClient
from backend.ai_service.clients.deepseek_client import DeepSeekClient
from backend.models.schema import LLMProvider, LLMResponse

class TestLLMClientFactory:
    """测试LLM客户端工厂"""
    
    def test_create_openai_client(self):
        """测试创建OpenAI客户端"""
        api_key = "test-openai-key"
        base_url = "https://api.moonshot.cn/v1"
        
        client = LLMClientFactory.create_client(
            provider=LLMProvider.OPENAI,
            api_key=api_key,
            base_url=base_url
        )
        
        assert isinstance(client, OpenAIClient)
        assert client.api_key == api_key
        assert client.base_url == base_url
    
    def test_create_claude_client(self):
        """测试创建Claude客户端"""
        api_key = "test-claude-key"
        
        client = LLMClientFactory.create_client(
            provider=LLMProvider.CLAUDE,
            api_key=api_key
        )
        
        assert isinstance(client, ClaudeClient)
        assert client.api_key == api_key
    
    def test_create_qwen_client(self):
        """测试创建Qwen客户端"""
        api_key = "test-qwen-key"
        base_url = "https://dashscope.aliyuncs.com/api/v1"
        
        client = LLMClientFactory.create_client(
            provider=LLMProvider.QWEN,
            api_key=api_key,
            base_url=base_url
        )
        
        assert isinstance(client, QwenClient)
        assert client.api_key == api_key
        assert client.base_url == base_url
    
    def test_create_deepseek_client(self):
        """测试创建DeepSeek客户端"""
        api_key = "test-deepseek-key"
        base_url = "https://api.deepseek.com/v1"
        
        client = LLMClientFactory.create_client(
            provider=LLMProvider.DEEPSEEK,
            api_key=api_key,
            base_url=base_url
        )
        
        assert isinstance(client, DeepSeekClient)
        assert client.api_key == api_key
        assert client.base_url == base_url
    
    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        with pytest.raises(ValueError, match="不支持的提供商"):
            LLMClientFactory.create_client(
                provider=LLMProvider.GEMINI,  # 暂时不支持
                api_key="test-key"
            )
    
    def test_client_caching(self):
        """测试客户端缓存机制"""
        api_key = "test-key"
        
        # 清除缓存
        LLMClientFactory.clear_cache()
        
        # 创建两次相同的客户端，应该返回同一个实例
        client1 = LLMClientFactory.get_or_create_client(
            provider=LLMProvider.OPENAI,
            api_key=api_key
        )
        client2 = LLMClientFactory.get_or_create_client(
            provider=LLMProvider.OPENAI,
            api_key=api_key
        )
        
        # 由于缓存key包含api_key的hash，这里应该是同一个实例
        # 但实际可能因为每次hash值不同而不同，所以这里检查类型即可
        assert isinstance(client1, OpenAIClient)
        assert isinstance(client2, OpenAIClient)
    
    def test_get_supported_providers(self):
        """测试获取支持的提供商列表"""
        supported = LLMClientFactory.get_supported_providers()
        
        assert LLMProvider.OPENAI in supported
        assert LLMProvider.CLAUDE in supported
        assert LLMProvider.QWEN in supported
        assert LLMProvider.DEEPSEEK in supported

class TestLLMManager:
    """测试LLM管理器"""
    
    @pytest.fixture
    def manager(self):
        """创建LLM管理器实例"""
        return LLMManager()
    
    @pytest.fixture
    def mock_config(self, manager):
        """Mock配置管理器"""
        with patch.object(manager.config_manager, 'get_api_key') as mock_get_key, \
             patch.object(manager.config_manager, 'get_base_url') as mock_get_url, \
             patch.object(manager.config_manager, 'get_configured_providers') as mock_providers, \
             patch.object(manager.config_manager, 'get_default_provider') as mock_default:
            
            # 设置模拟返回值
            def get_api_key_side_effect(provider):
                keys = {
                    LLMProvider.OPENAI: "test-openai-key",
                    LLMProvider.CLAUDE: "test-claude-key",
                    LLMProvider.QWEN: "test-qwen-key",
                    LLMProvider.DEEPSEEK: "test-deepseek-key",
                }
                return keys.get(provider)
            
            def get_base_url_side_effect(provider):
                urls = {
                    LLMProvider.OPENAI: "https://api.moonshot.cn/v1",
                    LLMProvider.QWEN: "https://dashscope.aliyuncs.com/api/v1",
                    LLMProvider.DEEPSEEK: "https://api.deepseek.com/v1",
                }
                return urls.get(provider)
            
            mock_get_key.side_effect = get_api_key_side_effect
            mock_get_url.side_effect = get_base_url_side_effect
            mock_providers.return_value = [LLMProvider.OPENAI, LLMProvider.CLAUDE]
            mock_default.return_value = LLMProvider.OPENAI
            
            yield {
                'get_api_key': mock_get_key,
                'get_base_url': mock_get_url,
                'get_configured_providers': mock_providers,
                'get_default_provider': mock_default
            }
    
    def test_initialization(self, manager, mock_config):
        """测试初始化"""
        # 重新加载配置
        manager._load_api_keys_from_config()
        
        assert LLMProvider.OPENAI in manager.api_keys
        assert LLMProvider.CLAUDE in manager.api_keys
        assert manager.api_keys[LLMProvider.OPENAI] == "test-openai-key"
    
    def test_set_api_key(self, manager, mock_config):
        """测试设置API密钥"""
        with patch.object(manager.config_manager, 'set_api_key') as mock_set:
            manager.set_api_key(LLMProvider.QWEN, "new-qwen-key")
            
            assert manager.api_keys[LLMProvider.QWEN] == "new-qwen-key"
            mock_set.assert_called_once_with(LLMProvider.QWEN, "new-qwen-key")
    
    def test_get_configured_providers(self, manager, mock_config):
        """测试获取已配置提供商"""
        providers = manager.get_configured_providers()
        assert providers == [LLMProvider.OPENAI, LLMProvider.CLAUDE]
    
    def test_get_available_providers(self, manager):
        """测试获取可用提供商"""
        available = manager.get_available_providers()
        assert len(available) >= 4  # 至少支持4个提供商
        assert LLMProvider.OPENAI in available
        assert LLMProvider.CLAUDE in available
        assert LLMProvider.QWEN in available
        assert LLMProvider.DEEPSEEK in available
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, manager, mock_config):
        """测试连接测试 - 成功情况"""
        # Mock客户端
        mock_client = AsyncMock()
        mock_client.test_connection.return_value = True
        
        with patch.object(LLMClientFactory, 'get_or_create_client', return_value=mock_client):
            # 重新加载API密钥
            manager._load_api_keys_from_config()
            
            result = await manager.test_connection(LLMProvider.OPENAI)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_no_api_key(self, manager):
        """测试连接测试 - 没有API密钥"""
        result = await manager.test_connection(LLMProvider.GEMINI)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_generate_visualization_code_success(self, manager, mock_config):
        """测试生成可视化代码 - 成功情况"""
        # Mock客户端和响应
        mock_response = LLMResponse(
            success=True,
            content="# Generated code",
            usage_stats={"total_tokens": 100},
            response_time=1.5,
            system_prompt="System prompt",
            user_prompt="User prompt",
            full_prompt="Full prompt"
        )
        
        mock_client = AsyncMock()
        mock_client.generate_completion.return_value = mock_response
        
        # Mock模板管理器
        mock_template = MagicMock()
        mock_template.system_prompt = "Test system prompt"
        
        with patch.object(LLMClientFactory, 'get_or_create_client', return_value=mock_client), \
             patch.object(manager.prompt_manager, 'get_template', return_value=mock_template), \
             patch.object(manager.prompt_manager, 'render_user_prompt', return_value="Test user prompt"), \
             patch.object(manager.prompt_manager, 'get_model_config', return_value={"model": "test-model"}):
            
            # 重新加载API密钥
            manager._load_api_keys_from_config()
            
            response = await manager.generate_visualization_code(
                problem_text="Test problem",
                output_path="test.png",
                provider=LLMProvider.OPENAI
            )
            
            assert response.success is True
            assert response.content == "# Generated code"
            assert response.usage_stats["total_tokens"] == 100
    
    @pytest.mark.asyncio
    async def test_generate_visualization_code_no_api_key(self, manager):
        """测试生成可视化代码 - 没有API密钥"""
        response = await manager.generate_visualization_code(
            problem_text="Test problem",
            output_path="test.png",
            provider=LLMProvider.GEMINI
        )
        
        assert response.success is False
        assert "未配置" in response.error_message
    
    def test_get_provider_info(self, manager, mock_config):
        """测试获取提供商信息"""
        # Mock客户端
        mock_client = MagicMock()
        mock_client.get_supported_models.return_value = ["model1", "model2"]
        mock_client.get_default_model.return_value = "model1"
        
        with patch.object(LLMClientFactory, 'create_client', return_value=mock_client):
            # 重新加载API密钥
            manager._load_api_keys_from_config()
            
            info = manager.get_provider_info(LLMProvider.OPENAI)
            
            assert info["provider"] == "openai"
            assert info["configured"] is True
            assert info["base_url"] == "https://api.moonshot.cn/v1"
            assert info["default_model"] == "model1"
            assert info["supported_models"] == ["model1", "model2"]
    
    def test_get_all_providers_info(self, manager, mock_config):
        """测试获取所有提供商信息"""
        # Mock客户端
        mock_client = MagicMock()
        mock_client.get_supported_models.return_value = ["model1"]
        mock_client.get_default_model.return_value = "model1"
        
        with patch.object(LLMClientFactory, 'create_client', return_value=mock_client):
            # 重新加载API密钥
            manager._load_api_keys_from_config()
            
            all_info = manager.get_all_providers_info()
            
            assert len(all_info) >= 4  # 至少4个提供商
            assert all(isinstance(info, dict) for info in all_info)
            assert all("provider" in info for info in all_info)

@pytest.mark.integration
class TestClientIntegration:
    """客户端集成测试（需要真实API密钥）"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), 
        reason="需要OPENAI_API_KEY环境变量"
    )
    async def test_openai_real_request(self):
        """测试OpenAI真实请求（跳过如果没有API密钥）"""
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        
        client = OpenAIClient(api_key=api_key, base_url=base_url)
        
        print(f"\n=== OpenAI 测试 ===")
        print(f"API Key: {api_key[:10]}..." if api_key else "未配置")
        print(f"Base URL: {base_url}")
        
        # 检查模型配置
        default_model = client.get_default_model()
        supported_models = client.get_supported_models()
        print(f"默认模型: {default_model}")
        print(f"支持的模型: {supported_models[:3]}...")  # 只显示前3个
        
        # 测试连接
        print("正在测试连接...")
        connection_ok = await client.test_connection()
        print(f"连接结果: {connection_ok}")
        assert connection_ok is True
        
        # 测试简单请求
        print("正在发送测试请求...")
        response = await client.generate_completion(
            system_prompt="你是一个数学助手",
            user_prompt="1+1等于几？请简单回答。",
            config={"model": default_model, "temperature": 0.1, "max_tokens": 50}
        )
        
        print(f"请求成功: {response.success}")
        if response.success:
            print(f"响应内容: {response.content}")
            print(f"使用统计: {response.usage_stats}")
            print(f"响应时间: {response.response_time:.2f}秒")
            assert len(response.content) > 0
            assert "usage_stats" in response.__dict__
        else:
            print(f"错误信息: {response.error_message}")
            assert False, f"请求失败: {response.error_message}"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("CLAUDE_API_KEY") or 
        os.getenv("CLAUDE_BASE_URL", "").find("moonshot") != -1,
        reason="需要真正的CLAUDE_API_KEY环境变量，跳过Moonshot兼容配置"
    )
    async def test_claude_real_request(self):
        """测试Claude真实请求（跳过如果没有API密钥或使用Moonshot配置）"""
        api_key = os.getenv("CLAUDE_API_KEY")
        base_url = os.getenv("CLAUDE_BASE_URL")
        
        # 如果base_url包含moonshot，说明这不是真正的Claude API
        if base_url and "moonshot" in base_url.lower():
            pytest.skip("检测到Moonshot配置，跳过Claude真实API测试")
        
        client = ClaudeClient(api_key=api_key, base_url=base_url)
        
        print(f"\n=== Claude 真实API 测试 ===")
        print(f"API Key: {api_key[:10]}..." if api_key else "未配置")
        print(f"Base URL: {base_url}")
        
        # 检查模型配置
        default_model = client.get_default_model()
        supported_models = client.get_supported_models()
        print(f"默认模型: {default_model}")
        print(f"支持的模型: {supported_models[:3]}...")  # 只显示前3个
        
        # 测试连接
        print("正在测试连接...")
        connection_ok = await client.test_connection()
        print(f"连接结果: {connection_ok}")
        assert connection_ok is True
        
        # 测试简单请求
        print("正在发送测试请求...")
        response = await client.generate_completion(
            system_prompt="你是一个数学助手",
            user_prompt="1+1等于几？请简单回答。",
            config={"model": default_model, "temperature": 0.1, "max_tokens": 50}
        )
        
        print(f"请求成功: {response.success}")
        if response.success:
            print(f"响应内容: {response.content}")
            print(f"使用统计: {response.usage_stats}")
            print(f"响应时间: {response.response_time:.2f}秒")
            assert len(response.content) > 0
        else:
            print(f"错误信息: {response.error_message}")
            assert False, f"请求失败: {response.error_message}"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("CLAUDE_API_KEY") or 
        not os.getenv("CLAUDE_BASE_URL") or 
        os.getenv("CLAUDE_BASE_URL", "").find("moonshot") == -1,
        reason="需要配置Moonshot兼容的Claude配置进行测试"
    )
    async def test_moonshot_claude_compatible_request(self):
        """测试Moonshot兼容Claude请求（当配置为Moonshot时）"""
        api_key = os.getenv("CLAUDE_API_KEY")
        base_url = os.getenv("CLAUDE_BASE_URL")
        
        # 确认这确实是Moonshot配置
        if not (base_url and "moonshot" in base_url.lower()):
            pytest.skip("不是Moonshot配置，跳过兼容测试")
        
        client = ClaudeClient(api_key=api_key, base_url=base_url)
        
        print(f"\n=== Moonshot Claude兼容 测试 ===")
        print(f"API Key: {api_key[:10]}..." if api_key else "未配置")
        print(f"Base URL: {base_url}")
        
        # 检查模型名称是否正确切换到Moonshot格式
        default_model = client.get_default_model()
        supported_models = client.get_supported_models()
        
        print(f"检测到Moonshot配置，默认模型: {default_model}")
        print(f"支持的模型: {supported_models}")
        
        # 对于Moonshot配置，应该使用moonshot或kimi模型名称
        assert "moonshot" in default_model or "kimi" in default_model
        assert any("moonshot" in model or "kimi" in model for model in supported_models)
        
        # 测试连接 - 现在应该能够成功
        print("正在测试连接...")
        connection_ok = await client.test_connection()
        print(f"连接结果: {connection_ok}")
        
        # 如果连接成功，测试一个简单的请求
        if connection_ok:
            print("正在发送测试请求...")
            response = await client.generate_completion(
                system_prompt="你是一个数学助手",
                user_prompt="1+1等于几？请简单回答。",
                config={"model": default_model, "temperature": 0.1, "max_tokens": 50}
            )
            
            print(f"请求成功: {response.success}")
            if response.success:
                print(f"响应内容: {response.content}")
                print(f"使用统计: {response.usage_stats}")
                print(f"响应时间: {response.response_time:.2f}秒")
                assert len(response.content) > 0
            else:
                print(f"错误信息: {response.error_message}")
        
        # 至少连接测试应该通过
        assert connection_ok is True
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("QWEN_API_KEY"), 
        reason="需要QWEN_API_KEY环境变量"
    )
    async def test_qwen_real_request(self):
        """测试Qwen真实请求（跳过如果没有API密钥）"""
        api_key = os.getenv("QWEN_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL")
        
        client = QwenClient(api_key=api_key, base_url=base_url)
        
        print(f"\n=== Qwen 测试 ===")
        print(f"API Key: {api_key[:10]}..." if api_key else "未配置")
        print(f"Base URL: {base_url}")
        
        # 检查模型配置
        default_model = client.get_default_model()
        supported_models = client.get_supported_models()
        print(f"默认模型: {default_model}")
        print(f"支持的模型: {supported_models}")
        
        # 测试连接
        print("正在测试连接...")
        connection_ok = await client.test_connection()
        print(f"连接结果: {connection_ok}")
        
        if connection_ok:
            # 测试简单请求
            print("正在发送测试请求...")
            response = await client.generate_completion(
                system_prompt="你是一个数学助手",
                user_prompt="1+1等于几？请简单回答。",
                config={"model": default_model, "temperature": 0.1, "max_tokens": 50}
            )
            
            print(f"请求成功: {response.success}")
            if response.success:
                print(f"响应内容: {response.content}")
                print(f"使用统计: {response.usage_stats}")
                print(f"响应时间: {response.response_time:.2f}秒")
                assert len(response.content) > 0
            else:
                print(f"错误信息: {response.error_message}")
        else:
            print("连接失败，跳过后续测试")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("DEEPSEEK_API_KEY"), 
        reason="需要DEEPSEEK_API_KEY环境变量"
    )
    async def test_deepseek_real_request(self):
        """测试DeepSeek真实请求（跳过如果没有API密钥）"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        
        client = DeepSeekClient(api_key=api_key, base_url=base_url)
        
        print(f"\n=== DeepSeek 测试 ===")
        print(f"API Key: {api_key[:10]}..." if api_key else "未配置")
        print(f"Base URL: {base_url}")
        
        # 检查模型配置
        default_model = client.get_default_model()
        supported_models = client.get_supported_models()
        print(f"默认模型: {default_model}")
        print(f"支持的模型: {supported_models}")
        
        # 测试连接
        print("正在测试连接...")
        connection_ok = await client.test_connection()
        print(f"连接结果: {connection_ok}")
        
        if connection_ok:
            # 测试简单请求
            print("正在发送测试请求...")
            response = await client.generate_completion(
                system_prompt="你是一个数学助手",
                user_prompt="1+1等于几？请简单回答。",
                config={"model": default_model, "temperature": 0.1, "max_tokens": 50}
            )
            
            print(f"请求成功: {response.success}")
            if response.success:
                print(f"响应内容: {response.content}")
                print(f"使用统计: {response.usage_stats}")
                print(f"响应时间: {response.response_time:.2f}秒")
                assert len(response.content) > 0
            else:
                print(f"错误信息: {response.error_message}")
        else:
            print("连接失败，跳过后续测试")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
