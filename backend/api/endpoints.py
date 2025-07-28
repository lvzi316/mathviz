#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI驱动的数学可视化API端点
"""

import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse

from backend.models.schema import (
    ProblemRequest, TaskResponse, TaskInfo, HealthStatus,
    LLMProvider, ProcessingMode, TaskStatus,
    AIAnalysisResult, ExecutionResult
)
from backend.ai_service import get_code_generator, get_llm_manager
from backend.execution import get_sandbox_manager

# 创建路由器
router = APIRouter(prefix="/api/v2", tags=["AI Math Visualization"])

# 任务存储（生产环境应使用Redis或数据库）
task_storage: Dict[str, TaskInfo] = {}

# 配置存储
config_storage = {
    "api_keys": {},
    "default_provider": LLMProvider.OPENAI,
    "default_execution_mode": "restricted",
    "max_concurrent_tasks": 10
}

async def process_ai_visualization_task(task_id: str, request: ProblemRequest):
    """
    处理AI可视化任务的后台函数
    
    Args:
        task_id: 任务ID
        request: 请求参数
    """
    try:
        # 更新任务状态：开始AI分析
        update_task_status(task_id, TaskStatus.AI_ANALYZING, 10)
        
        # 1. 调用AI生成代码
        code_generator = get_code_generator()
        ai_result = await code_generator.generate_visualization_code(
            problem_text=request.text,
            output_path=f"output/{task_id}.png",
            provider=request.llm_provider,
            template_variant=request.prompt_variant
        )
        
        # 检查AI生成是否成功
        if ai_result.confidence < 0.1:  # 置信度太低
            update_task_status(task_id, TaskStatus.FAILED, 0, 
                             error="AI分析失败：生成的代码质量不符合要求")
            return
        
        # 更新任务状态：代码验证中
        update_task_status(task_id, TaskStatus.CODE_VALIDATING, 40, ai_analysis=ai_result)
        
        # 2. 在沙箱中执行代码
        sandbox_manager = get_sandbox_manager()
        sandbox_result = sandbox_manager.execute_code_safely(
            code=ai_result.visualization_code,
            output_path=f"output/{task_id}.png",
            execution_mode=config_storage["default_execution_mode"],
            timeout=30
        )
        
        if not sandbox_result["overall_success"]:
            update_task_status(task_id, TaskStatus.FAILED, 0,
                             error=f"代码执行失败: {sandbox_result['error_message']}")
            return
        
        # 更新任务状态：完成
        execution_result = sandbox_result["execution_result"]
        update_task_status(task_id, TaskStatus.COMPLETED, 100, 
                         ai_analysis=ai_result, execution_result=execution_result)
        
    except Exception as e:
        update_task_status(task_id, TaskStatus.FAILED, 0, error=f"任务处理异常: {str(e)}")

def update_task_status(task_id: str, status: TaskStatus, progress: int,
                      ai_analysis: Optional[AIAnalysisResult] = None,
                      execution_result: Optional[ExecutionResult] = None,
                      error: Optional[str] = None):
    """更新任务状态"""
    if task_id in task_storage:
        task_info = task_storage[task_id]
        task_info.status = status
        task_info.progress = progress
        task_info.updated_at = datetime.now().isoformat()
        
        if ai_analysis:
            task_info.ai_analysis = ai_analysis
        if execution_result:
            task_info.execution_result = execution_result
        if error:
            task_info.error_message = error

@router.post("/problems/generate", response_model=TaskResponse)
async def generate_visualization(request: ProblemRequest, background_tasks: BackgroundTasks):
    """
    生成数学题目可视化（支持AI和传统模式）
    
    Args:
        request: 问题请求
        background_tasks: 后台任务管理器
        
    Returns:
        TaskResponse: 任务响应
    """
    # 检查并发任务数量
    active_tasks = sum(1 for task in task_storage.values() 
                      if task.status in [TaskStatus.PENDING, TaskStatus.AI_ANALYZING, 
                                       TaskStatus.CODE_VALIDATING, TaskStatus.EXECUTING])
    
    if active_tasks >= config_storage["max_concurrent_tasks"]:
        raise HTTPException(status_code=429, detail="服务器繁忙，请稍后重试")
    
    # 创建任务
    task_id = str(uuid.uuid4())
    task_info = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        progress=0,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        processing_mode=request.processing_mode,
        llm_provider=request.llm_provider if request.processing_mode == ProcessingMode.AI else None
    )
    
    task_storage[task_id] = task_info
    
    # 添加后台任务
    if request.processing_mode == ProcessingMode.AI:
        # 检查API密钥
        llm_manager = get_llm_manager()
        if request.llm_provider not in llm_manager.get_available_providers():
            raise HTTPException(status_code=400, detail=f"未配置{request.llm_provider.value}的API密钥")
        
        background_tasks.add_task(process_ai_visualization_task, task_id, request)
        estimated_time = 15
    else:
        # 传统模式处理（兼容旧接口）
        from text_to_visual import MathProblemVisualizer
        
        async def process_traditional_task():
            try:
                update_task_status(task_id, TaskStatus.EXECUTING, 50)
                
                visualizer = MathProblemVisualizer()
                if "相遇" in request.text:
                    img_path, result = visualizer.create_meeting_visualization(
                        request.text, f"output/{task_id}.png"
                    )
                elif "追及" in request.text:
                    img_path, result = visualizer.create_chase_visualization(
                        request.text, f"output/{task_id}.png"
                    )
                else:
                    # 默认使用相遇问题处理
                    img_path, result = visualizer.create_meeting_visualization(
                        request.text, f"output/{task_id}.png"
                    )
                
                execution_result = ExecutionResult(
                    success=True,
                    image_path=img_path,
                    result_data=result,
                    execution_time=2.0,
                    memory_usage=50.0,
                    output_logs="传统模式处理完成"
                )
                
                update_task_status(task_id, TaskStatus.COMPLETED, 100, 
                                 execution_result=execution_result)
                
            except Exception as e:
                update_task_status(task_id, TaskStatus.FAILED, 0, 
                                 error=f"传统模式处理失败: {str(e)}")
        
        background_tasks.add_task(process_traditional_task)
        estimated_time = 5
    
    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="任务已创建，正在处理中...",
        estimated_time=estimated_time
    )

@router.get("/tasks/{task_id}", response_model=TaskInfo)
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        TaskInfo: 任务信息
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task_storage[task_id]

@router.get("/tasks")
async def list_tasks(limit: int = 10, status: Optional[TaskStatus] = None):
    """
    列出任务
    
    Args:
        limit: 返回数量限制
        status: 状态过滤
        
    Returns:
        list: 任务列表
    """
    tasks = list(task_storage.values())
    
    if status:
        tasks = [task for task in tasks if task.status == status]
    
    # 按创建时间倒序排列
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    return tasks[:limit]

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    
    Args:
        task_id: 任务ID
    """
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del task_storage[task_id]
    return {"message": "任务已删除"}

@router.post("/config/api-key")
async def set_api_key(provider: LLMProvider, api_key: str):
    """
    设置API密钥
    
    Args:
        provider: 模型提供商
        api_key: API密钥
    """
    config_storage["api_keys"][provider] = api_key
    
    # 更新LLM管理器
    llm_manager = get_llm_manager()
    llm_manager.set_api_key(provider, api_key)
    
    return {"message": f"{provider.value}的API密钥已设置"}

@router.get("/config")
async def get_config():
    """获取当前配置"""
    return {
        "configured_providers": list(config_storage["api_keys"].keys()),
        "default_provider": config_storage["default_provider"],
        "default_execution_mode": config_storage["default_execution_mode"],
        "max_concurrent_tasks": config_storage["max_concurrent_tasks"]
    }

@router.post("/config")
async def update_config(
    default_provider: Optional[LLMProvider] = None,
    default_execution_mode: Optional[str] = None,
    max_concurrent_tasks: Optional[int] = None
):
    """更新配置"""
    if default_provider:
        config_storage["default_provider"] = default_provider
    if default_execution_mode:
        config_storage["default_execution_mode"] = default_execution_mode
    if max_concurrent_tasks:
        config_storage["max_concurrent_tasks"] = max_concurrent_tasks
    
    return {"message": "配置已更新"}

@router.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    # 任务统计
    task_stats = {
        "total_tasks": len(task_storage),
        "pending_tasks": sum(1 for task in task_storage.values() if task.status == TaskStatus.PENDING),
        "processing_tasks": sum(1 for task in task_storage.values() 
                              if task.status in [TaskStatus.AI_ANALYZING, TaskStatus.CODE_VALIDATING, TaskStatus.EXECUTING]),
        "completed_tasks": sum(1 for task in task_storage.values() if task.status == TaskStatus.COMPLETED),
        "failed_tasks": sum(1 for task in task_storage.values() if task.status == TaskStatus.FAILED)
    }
    
    # AI生成统计
    code_generator = get_code_generator()
    ai_stats = code_generator.get_generation_stats()
    
    # 沙箱统计
    sandbox_manager = get_sandbox_manager()
    sandbox_stats = sandbox_manager.get_sandbox_stats()
    
    return {
        "task_stats": task_stats,
        "ai_generation_stats": ai_stats,
        "sandbox_stats": sandbox_stats,
        "system_config": {
            "configured_providers": len(config_storage["api_keys"]),
            "max_concurrent_tasks": config_storage["max_concurrent_tasks"]
        }
    }

@router.get("/health", response_model=HealthStatus)
async def health_check():
    """健康检查"""
    active_tasks = sum(1 for task in task_storage.values() 
                      if task.status in [TaskStatus.PENDING, TaskStatus.AI_ANALYZING, 
                                       TaskStatus.CODE_VALIDATING, TaskStatus.EXECUTING])
    
    total_processed = len([task for task in task_storage.values() 
                          if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]])
    
    # 计算平均处理时间
    completed_tasks = [task for task in task_storage.values() if task.status == TaskStatus.COMPLETED]
    avg_time = 0.0
    if completed_tasks:
        total_time = 0.0
        count = 0
        for task in completed_tasks:
            if task.ai_analysis:
                total_time += task.ai_analysis.processing_time
                count += 1
            if task.execution_result:
                total_time += task.execution_result.execution_time
                count += 1
        avg_time = total_time / count if count > 0 else 0.0
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        active_tasks=active_tasks,
        total_processed=total_processed,
        avg_processing_time=avg_time
    )

@router.post("/test/connection/{provider}")
async def test_llm_connection(provider: LLMProvider):
    """测试LLM连接"""
    llm_manager = get_llm_manager()
    
    if provider not in llm_manager.get_available_providers():
        raise HTTPException(status_code=400, detail=f"未配置{provider.value}的API密钥")
    
    try:
        success = await llm_manager.test_connection(provider)
        return {"success": success, "message": f"{provider.value}连接{'成功' if success else '失败'}"}
    except Exception as e:
        return {"success": False, "message": f"连接测试异常: {str(e)}"}

# 导出路由器
__all__ = ['router']
