#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI代码生成器
负责协调LLM调用和结果处理
"""

import json
import time
import uuid
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

from backend.models.schema import (
    LLMProvider, AIAnalysisResult, LLMResponse, LLMInteraction, ErrorDetails
)
from backend.ai_service.llm_client import get_llm_manager

class CodeGenerator:
    """AI代码生成器"""
    
    def __init__(self):
        """初始化代码生成器"""
        self.llm_manager = get_llm_manager()
        self.generation_history = []
    
    async def generate_visualization_code(self, 
                                        problem_text: str,
                                        output_path: str,
                                        provider: LLMProvider = LLMProvider.OPENAI,
                                        template_variant: str = "default",
                                        max_retries: int = 3) -> tuple[AIAnalysisResult, Optional[ErrorDetails]]:
        """
        生成可视化代码
        
        Args:
            problem_text: 题目文本
            output_path: 输出路径
            provider: LLM提供商
            template_variant: 模板变体
            max_retries: 最大重试次数
            
        Returns:
            tuple[AIAnalysisResult, Optional[ErrorDetails]]: 分析结果和错误详情
        """
        start_time = time.time()
        generation_id = str(uuid.uuid4())
        last_error_details = None
        
        for attempt in range(max_retries):
            try:
                # 调用LLM生成代码
                llm_response = await self.llm_manager.generate_visualization_code(
                    problem_text=problem_text,
                    output_path=output_path,
                    provider=provider,
                    template_name="math_visualization",
                    variant=template_variant
                )
                
                if not llm_response.success:
                    # API调用失败
                    last_error_details = ErrorDetails(
                        error_type="api_error",
                        error_message=llm_response.error_message or "API调用失败",
                        api_response=llm_response.content if llm_response.content else None,
                        generated_code=None,
                        stack_trace=None,
                        validation_errors=None,
                        execution_logs=None,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    if attempt == max_retries - 1:
                        # 最后一次尝试失败，返回错误结果
                        return self._create_error_result(
                            f"LLM调用失败: {llm_response.error_message}",
                            time.time() - start_time
                        ), last_error_details
                    continue
                
                # 解析LLM响应
                parsed_result = self._parse_llm_response(llm_response.content)
                
                if parsed_result is None:
                    # JSON解析失败
                    last_error_details = ErrorDetails(
                        error_type="json_parse_error",
                        error_message="无法解析LLM响应为有效JSON格式",
                        api_response=llm_response.content,
                        generated_code=None,
                        stack_trace=traceback.format_exc(),
                        validation_errors=["JSON格式错误"],
                        execution_logs=None,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    if attempt == max_retries - 1:
                        return self._create_error_result(
                            "无法解析LLM响应为有效JSON格式",
                            time.time() - start_time
                        ), last_error_details
                    continue
                
                # 验证结果完整性
                validation_result = self._validate_generation_result(parsed_result)
                
                if not validation_result["valid"]:
                    # 验证失败
                    generated_code = parsed_result.get("visualization_code", "")
                    last_error_details = ErrorDetails(
                        error_type="validation_error",
                        error_message=f"生成结果验证失败: {validation_result['error']}",
                        api_response=llm_response.content,
                        generated_code=generated_code if generated_code else None,
                        stack_trace=None,
                        validation_errors=[validation_result['error']],
                        execution_logs=None,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    if attempt == max_retries - 1:
                        return self._create_error_result(
                            f"生成结果验证失败: {validation_result['error']}",
                            time.time() - start_time
                        ), last_error_details
                    continue
                
                # 直接设置固定置信度（通过验证的代码都认为是可信的）
                confidence = 0.8  # 通过基本验证的代码给予高置信度
                
                # 创建成功结果
                result = AIAnalysisResult(
                    problem_type=parsed_result.get("problem_type", "未知"),
                    parameters=parsed_result.get("parameters", {}),
                    visualization_code=parsed_result.get("visualization_code", ""),
                    explanation=parsed_result.get("explanation", ""),
                    confidence=confidence,
                    processing_time=time.time() - start_time,
                    llm_interaction=LLMInteraction(
                        system_prompt=llm_response.system_prompt or "",
                        user_prompt=llm_response.user_prompt or "",
                        full_prompt=llm_response.full_prompt or "",
                        response_content=llm_response.content,
                        usage_stats=llm_response.usage_stats or {},
                        response_time=llm_response.response_time,
                        timestamp=datetime.now().isoformat()
                    ) if llm_response else None
                )
                
                # 记录生成历史
                self._record_generation(generation_id, problem_text, provider, result, llm_response)
                
                return result, None  # 成功时返回None作为错误详情
                
            except Exception as e:
                # 程序异常
                last_error_details = ErrorDetails(
                    error_type="exception",
                    error_message=f"代码生成异常: {str(e)}",
                    api_response=None,
                    generated_code=None,
                    stack_trace=traceback.format_exc(),
                    validation_errors=None,
                    execution_logs=None,
                    timestamp=datetime.now().isoformat()
                )
                
                if attempt == max_retries - 1:
                    return self._create_error_result(
                        f"代码生成异常: {str(e)}",
                        time.time() - start_time
                    ), last_error_details
                continue
        
        # 所有重试都失败了
        if last_error_details is None:
            last_error_details = ErrorDetails(
                error_type="max_retries_exceeded",
                error_message=f"代码生成失败，已重试{max_retries}次",
                api_response=None,
                generated_code=None,
                stack_trace=None,
                validation_errors=None,
                execution_logs=None,
                timestamp=datetime.now().isoformat()
            )
        
        return self._create_error_result(
            f"代码生成失败，已重试{max_retries}次",
            time.time() - start_time
        ), last_error_details
    
    def _parse_llm_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析LLM响应
        
        Args:
            content: LLM响应内容
            
        Returns:
            Optional[Dict[str, Any]]: 解析后的字典，失败返回None
        """
        try:
            # 尝试直接解析JSON
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                # 尝试提取JSON部分
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                # 查找JSON对象
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                
                return None
            except Exception:
                return None
    
    def _validate_generation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证生成结果
        
        Args:
            result: 生成结果
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        required_fields = ["problem_type", "parameters", "visualization_code", "explanation"]
        
        for field in required_fields:
            if field not in result:
                return {"valid": False, "error": f"缺少必需字段: {field}"}
        
        # 验证代码非空
        if not result["visualization_code"].strip():
            return {"valid": False, "error": "可视化代码不能为空"}
        
        # 验证代码包含基本要素
        code = result["visualization_code"]
        if "matplotlib" not in code:
            return {"valid": False, "error": "代码必须使用matplotlib"}
        
        if "plt.savefig" not in code and "savefig" not in code:
            return {"valid": False, "error": "代码必须包含图片保存逻辑"}
        
        return {"valid": True}
    
    def _create_error_result(self, error_message: str, processing_time: float) -> AIAnalysisResult:
        """
        创建错误结果
        
        Args:
            error_message: 错误信息
            processing_time: 处理时间
            
        Returns:
            AIAnalysisResult: 错误结果
        """
        return AIAnalysisResult(
            problem_type="错误",
            parameters={},
            visualization_code=f"# 代码生成失败\n# 错误: {error_message}",
            explanation=f"代码生成失败: {error_message}",
            confidence=0.0,
            processing_time=processing_time
        )
    
    def _record_generation(self, generation_id: str, problem_text: str, 
                          provider: LLMProvider, result: AIAnalysisResult,
                          llm_response: LLMResponse):
        """
        记录生成历史
        
        Args:
            generation_id: 生成ID
            problem_text: 题目文本
            provider: 提供商
            result: 生成结果
            llm_response: LLM响应
        """
        record = {
            "id": generation_id,
            "timestamp": time.time(),
            "problem_text": problem_text[:100] + "..." if len(problem_text) > 100 else problem_text,
            "provider": provider.value,
            "success": result.confidence > 0,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "tokens_used": llm_response.usage_stats.get("total_tokens", 0)
        }
        
        self.generation_history.append(record)
        
        # 保持历史记录在合理大小
        if len(self.generation_history) > 1000:
            self.generation_history = self.generation_history[-500:]
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        获取生成统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.generation_history:
            return {
                "total_generations": 0,
                "success_rate": 0.0,
                "avg_confidence": 0.0,
                "avg_processing_time": 0.0,
                "total_tokens": 0
            }
        
        total = len(self.generation_history)
        successful = sum(1 for record in self.generation_history if record["success"])
        
        return {
            "total_generations": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_confidence": sum(record["confidence"] for record in self.generation_history) / total,
            "avg_processing_time": sum(record["processing_time"] for record in self.generation_history) / total,
            "total_tokens": sum(record["tokens_used"] for record in self.generation_history),
            "provider_distribution": self._get_provider_distribution()
        }
    
    def _get_provider_distribution(self) -> Dict[str, int]:
        """获取提供商使用分布"""
        distribution = {}
        for record in self.generation_history:
            provider = record["provider"]
            distribution[provider] = distribution.get(provider, 0) + 1
        return distribution
    
    def get_recent_generations(self, limit: int = 10) -> list:
        """
        获取最近的生成记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            list: 生成记录列表
        """
        return sorted(
            self.generation_history, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:limit]

# 全局代码生成器实例
code_generator = CodeGenerator()

def get_code_generator() -> CodeGenerator:
    """获取全局代码生成器实例"""
    return code_generator

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        generator = get_code_generator()
        
        # 测试生成
        result = await generator.generate_visualization_code(
            problem_text="甲、乙两地相距480公里，两车相向而行，速度分别为60和80公里/小时，求相遇时间。",
            output_path="output/test.png",
            provider=LLMProvider.OPENAI
        )
        
        print(f"题目类型: {result.problem_type}")
        print(f"置信度: {result.confidence}")
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"参数: {result.parameters}")
        print(f"说明: {result.explanation}")
        print(f"代码长度: {len(result.visualization_code)}字符")
        
        # 打印统计信息
        stats = generator.get_generation_stats()
        print(f"\n统计信息: {stats}")
    
    # 注意：需要先设置API密钥才能运行测试
    # asyncio.run(test())
