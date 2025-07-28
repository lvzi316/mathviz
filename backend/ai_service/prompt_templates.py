#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt模板管理器
支持YAML格式的参数化prompt模板
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from backend.models.schema import PromptTemplate, LLMProvider

class PromptTemplateManager:
    """Prompt模板管理器"""
    
    def __init__(self, templates_dir: str = "prompts"):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板文件目录
        """
        self.templates_dir = Path(templates_dir)
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板文件"""
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"模板目录不存在: {self.templates_dir}")
        
        for template_file in self.templates_dir.glob("*.yaml"):
            template_name = template_file.stem
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                self.templates_cache[template_name] = template_data
                print(f"✅ 已加载模板: {template_name}")
            except Exception as e:
                print(f"❌ 加载模板失败 {template_file}: {e}")
    
    def get_template(self, template_name: str = "math_visualization", 
                    variant: str = "default") -> PromptTemplate:
        """
        获取指定的模板
        
        Args:
            template_name: 模板名称
            variant: 模板变体（default, simple_mode, detailed_mode等）
            
        Returns:
            PromptTemplate: 模板对象
        """
        if template_name not in self.templates_cache:
            raise ValueError(f"模板不存在: {template_name}")
        
        template_data = self.templates_cache[template_name]
        
        # 根据变体选择不同的prompt
        if variant != "default" and "variants" in template_data:
            if variant in template_data["variants"]:
                variant_data = template_data["variants"][variant]
                system_prompt = variant_data.get("system_prompt", template_data["system_prompt"])
                user_prompt_template = variant_data.get("user_prompt_template", template_data["user_prompt_template"])
            else:
                raise ValueError(f"模板变体不存在: {variant}")
        else:
            system_prompt = template_data["system_prompt"]
            user_prompt_template = template_data["user_prompt_template"]
        
        return PromptTemplate(
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            llm_config=template_data.get("model_configs", {})
        )
    
    def render_user_prompt(self, template_name: str = "math_visualization",
                          variant: str = "default", **kwargs) -> str:
        """
        渲染用户prompt
        
        Args:
            template_name: 模板名称
            variant: 模板变体
            **kwargs: 模板参数
            
        Returns:
            str: 渲染后的prompt
        """
        template = self.get_template(template_name, variant)
        
        try:
            return template.user_prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"模板参数缺失: {e}")
    
    def get_model_config(self, template_name: str = "math_visualization",
                        provider: LLMProvider = LLMProvider.OPENAI) -> Dict[str, Any]:
        """
        获取模型配置
        
        Args:
            template_name: 模板名称
            provider: 模型提供商
            
        Returns:
            Dict[str, Any]: 模型配置
        """
        if template_name not in self.templates_cache:
            raise ValueError(f"模板不存在: {template_name}")
        
        template_data = self.templates_cache[template_name]
        model_configs = template_data.get("model_configs", {})
        
        return model_configs.get(provider.value, {
            "temperature": 0.3,
            "max_tokens": 2000
        })
    
    def get_examples(self, template_name: str = "math_visualization") -> list:
        """
        获取示例数据
        
        Args:
            template_name: 模板名称
            
        Returns:
            list: 示例列表
        """
        if template_name not in self.templates_cache:
            return []
        
        template_data = self.templates_cache[template_name]
        return template_data.get("examples", [])
    
    def validate_template(self, template_name: str, test_params: Dict[str, Any]) -> bool:
        """
        验证模板是否能正确渲染
        
        Args:
            template_name: 模板名称
            test_params: 测试参数
            
        Returns:
            bool: 是否验证通过
        """
        try:
            template = self.get_template(template_name)
            template.user_prompt_template.format(**test_params)
            return True
        except Exception as e:
            print(f"模板验证失败: {e}")
            return False
    
    def list_templates(self) -> list:
        """
        列出所有可用模板
        
        Returns:
            list: 模板名称列表
        """
        return list(self.templates_cache.keys())
    
    def list_variants(self, template_name: str) -> list:
        """
        列出模板的所有变体
        
        Args:
            template_name: 模板名称
            
        Returns:
            list: 变体名称列表
        """
        if template_name not in self.templates_cache:
            return []
        
        template_data = self.templates_cache[template_name]
        variants = ["default"]
        if "variants" in template_data:
            variants.extend(list(template_data["variants"].keys()))
        
        return variants
    
    def reload_templates(self):
        """重新加载所有模板"""
        self.templates_cache.clear()
        self._load_templates()
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        获取模板信息
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict[str, Any]: 模板信息
        """
        if template_name not in self.templates_cache:
            raise ValueError(f"模板不存在: {template_name}")
        
        template_data = self.templates_cache[template_name]
        
        return {
            "name": template_name,
            "variants": self.list_variants(template_name),
            "model_configs": list(template_data.get("model_configs", {}).keys()),
            "examples_count": len(template_data.get("examples", [])),
            "has_system_prompt": bool(template_data.get("system_prompt")),
            "has_user_template": bool(template_data.get("user_prompt_template"))
        }

# 全局模板管理器实例
prompt_manager = PromptTemplateManager()

def get_prompt_manager() -> PromptTemplateManager:
    """获取全局prompt管理器实例"""
    return prompt_manager

# 便捷函数
def render_prompt(problem_text: str, output_path: str, 
                 template_name: str = "math_visualization",
                 variant: str = "default") -> tuple[str, str]:
    """
    便捷的prompt渲染函数
    
    Args:
        problem_text: 题目文本
        output_path: 输出路径
        template_name: 模板名称
        variant: 模板变体
        
    Returns:
        tuple[str, str]: (system_prompt, user_prompt)
    """
    manager = get_prompt_manager()
    template = manager.get_template(template_name, variant)
    user_prompt = manager.render_user_prompt(
        template_name, variant,
        problem_text=problem_text,
        output_path=output_path
    )
    
    return template.system_prompt, user_prompt

def get_model_config_for_provider(provider: LLMProvider, 
                                template_name: str = "math_visualization") -> Dict[str, Any]:
    """
    获取指定提供商的模型配置
    
    Args:
        provider: 模型提供商
        template_name: 模板名称
        
    Returns:
        Dict[str, Any]: 模型配置
    """
    manager = get_prompt_manager()
    return manager.get_model_config(template_name, provider)

if __name__ == "__main__":
    # 测试代码
    manager = PromptTemplateManager()
    
    print("可用模板:", manager.list_templates())
    
    # 测试模板渲染
    system_prompt, user_prompt = render_prompt(
        problem_text="甲、乙两地相距480公里，两车相向而行...",
        output_path="output/test.png",
        variant="simple_mode"
    )
    
    print("\n系统Prompt:")
    print(system_prompt[:200] + "...")
    
    print("\n用户Prompt:")
    print(user_prompt[:200] + "...")
    
    # 测试模型配置
    config = get_model_config_for_provider(LLMProvider.OPENAI)
    print(f"\nOpenAI配置: {config}")
