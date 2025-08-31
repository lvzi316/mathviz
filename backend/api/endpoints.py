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
    TaskStatus, LLMProvider, ProcessingMode, AIAnalysisResult, 
    ExecutionResult, ErrorDetails
)
from backend.ai_service import get_code_generator, get_llm_manager
from backend.execution import get_sandbox_manager
from backend.config import get_config_manager

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
        print(f"🚀 [TASK-{task_id}] 开始处理AI可视化任务")
        print(f"📝 [TASK-{task_id}] 题目内容: {request.text}")
        print(f"🔧 [TASK-{task_id}] LLM提供商: {request.llm_provider}")
        print(f"📋 [TASK-{task_id}] 模板变体: {request.prompt_variant}")
        
        # 更新任务状态：开始AI分析
        update_task_status(task_id, TaskStatus.AI_ANALYZING, 10)
        print(f"📊 [TASK-{task_id}] 状态更新: AI_ANALYZING (10%)")
        
        # 1. 调用AI生成代码
        print(f"🤖 [TASK-{task_id}] 开始调用LLM生成代码...")
        code_generator = get_code_generator()
        
        try:
            ai_result, error_details = await code_generator.generate_visualization_code(
                problem_text=request.text,
                output_path=f"output/{task_id}.png",
                provider=request.llm_provider,
                template_variant=request.prompt_variant
            )
            
            print(f"✅ [TASK-{task_id}] LLM代码生成完成!")
            print(f"📈 [TASK-{task_id}] 置信度: {ai_result.confidence:.2f}")
            print(f"⏱️  [TASK-{task_id}] 处理时间: {ai_result.processing_time:.2f}秒")
            print(f"🏷️  [TASK-{task_id}] 题目类型: {ai_result.problem_type}")
            print(f"📐 [TASK-{task_id}] 参数: {ai_result.parameters}")
            print(f"💬 [TASK-{task_id}] 说明: {ai_result.explanation[:100]}...")
            print(f"📝 [TASK-{task_id}] 代码长度: {len(ai_result.visualization_code)} 字符")
            
            # 如果有错误详情，记录它们
            if error_details:
                print(f"⚠️  [TASK-{task_id}] 有错误详情: {error_details.error_type} - {error_details.error_message}")
            
            # 添加详细的LLM交互调试信息
            if hasattr(ai_result, 'llm_interaction') and ai_result.llm_interaction:
                llm_interaction = ai_result.llm_interaction
                print(f"🔍 [TASK-{task_id}] LLM交互详情:")
                print(f"   响应时间: {llm_interaction.response_time:.2f}秒")
                print(f"   系统提示词长度: {len(llm_interaction.system_prompt)} 字符")
                print(f"   用户提示词长度: {len(llm_interaction.user_prompt)} 字符")
                print(f"   LLM响应长度: {len(llm_interaction.response_content)} 字符")
                print(f"   LLM响应前100字符: {llm_interaction.response_content[:100]}...")
                if llm_interaction.usage_stats:
                    print(f"   Token使用: {llm_interaction.usage_stats}")
        except Exception as llm_error:
            error_msg = f"LLM调用异常: {str(llm_error)}"
            print(f"💥 [TASK-{task_id}] {error_msg}")
            print(f"🔍 [TASK-{task_id}] 异常类型: {type(llm_error).__name__}")
            import traceback
            traceback.print_exc()
            
            # 创建异常错误详情
            exception_error_details = ErrorDetails(
                error_type="exception",
                error_message=error_msg,
                api_response=None,
                generated_code=None,
                stack_trace=traceback.format_exc(),
                validation_errors=None,
                execution_logs=None,
                timestamp=datetime.now().isoformat()
            )
            
            update_task_status(
                task_id, 
                TaskStatus.API_ERROR, 
                0, 
                error=error_msg,
                error_details=exception_error_details,
                failure_type="api_error"
            )
            return
        
        # 检查AI生成是否成功（临时降低置信度阈值用于调试）
        print(f"🔍 [TASK-{task_id}] 检查置信度: {ai_result.confidence} (阈值: 0.05)")
        if ai_result.confidence < 0.05:  # 临时降低阈值用于调试
            error_msg = f"AI分析失败：生成的代码质量不符合要求 (置信度: {ai_result.confidence:.2f})"
            print(f"❌ [TASK-{task_id}] {error_msg}")
            
            # 调试信息：即使失败也显示生成的内容
            print(f"🔍 [TASK-{task_id}] 调试 - 失败的生成结果:")
            print(f"   题目类型: {ai_result.problem_type}")
            print(f"   参数: {ai_result.parameters}")
            print(f"   说明: {ai_result.explanation}")
            print(f"   代码前200字符: {ai_result.visualization_code[:200]}...")
            
            # 如果有error_details，使用AI_ANALYSIS_FAILED状态；否则使用通用FAILED状态
            status_to_use = TaskStatus.AI_ANALYSIS_FAILED if error_details else TaskStatus.FAILED
            update_task_status(
                task_id, 
                status_to_use, 
                0, 
                error=error_msg,
                error_details=error_details,
                failure_type="ai_analysis_failed"
            )
            return
        
        # 更新任务状态：代码验证中
        update_task_status(task_id, TaskStatus.CODE_VALIDATING, 40, ai_analysis=ai_result)
        print(f"📊 [TASK-{task_id}] 状态更新: CODE_VALIDATING (40%)")
        
        # 2. 在沙箱中执行代码
        print(f"🏃 [TASK-{task_id}] 开始在沙箱中执行代码...")
        print(f"🔒 [TASK-{task_id}] 执行模式: {config_storage['default_execution_mode']}")
        
        sandbox_manager = get_sandbox_manager()
        sandbox_result = sandbox_manager.execute_code_safely(
            code=ai_result.visualization_code,
            output_path=f"output/{task_id}.png",
            execution_mode=config_storage["default_execution_mode"],
            timeout=30
        )
        
        print(f"🏁 [TASK-{task_id}] 沙箱执行完成!")
        print(f"📊 [TASK-{task_id}] 执行结果: {sandbox_result.get('overall_success', False)}")
        
        if not sandbox_result["overall_success"]:
            error_msg = f"代码执行失败: {sandbox_result['error_message']}"
            print(f"❌ [TASK-{task_id}] {error_msg}")
            print(f"🔍 [TASK-{task_id}] 详细错误信息: {sandbox_result}")
            
            # 创建代码执行失败的错误详情
            execution_error_details = ErrorDetails(
                error_type="code_execution_failed",
                error_message=error_msg,
                api_response=None,
                generated_code=ai_result.visualization_code,  # 保存生成的代码
                stack_trace=sandbox_result.get('error_message', ''),
                validation_errors=sandbox_result.get('validation_result', {}).get('syntax_errors', []),
                execution_logs=sandbox_result.get('execution_result', {}).get('output_logs', '') if sandbox_result.get('execution_result') else '',
                timestamp=datetime.now().isoformat()
            )
            
            update_task_status(
                task_id, 
                TaskStatus.CODE_EXECUTION_FAILED, 
                0, 
                error=error_msg,
                error_details=execution_error_details,
                failure_type="code_execution_failed"
            )
            return
        
        # 更新任务状态：完成
        execution_result = sandbox_result["execution_result"]
        update_task_status(task_id, TaskStatus.COMPLETED, 100, 
                         ai_analysis=ai_result, execution_result=execution_result)
        
        print(f"🎉 [TASK-{task_id}] 任务完成!")
        print(f"🖼️  [TASK-{task_id}] 图片路径: {execution_result.image_path}")
        print(f"⏱️  [TASK-{task_id}] 执行时间: {execution_result.execution_time:.2f}秒")
        
    except Exception as e:
        error_msg = f"任务处理异常: {str(e)}"
        print(f"💥 [TASK-{task_id}] {error_msg}")
        print(f"🔍 [TASK-{task_id}] 异常详情: {type(e).__name__}: {e}")
        import traceback
        print(f"📚 [TASK-{task_id}] 堆栈跟踪:")
        traceback.print_exc()
        update_task_status(task_id, TaskStatus.FAILED, 0, error=error_msg)

def update_task_status(task_id: str, status: TaskStatus, progress: int,
                      ai_analysis: Optional[AIAnalysisResult] = None,
                      execution_result: Optional[ExecutionResult] = None,
                      error: Optional[str] = None,
                      error_details: Optional[ErrorDetails] = None,
                      failure_type: Optional[str] = None,
                      llm_interaction: Optional[Dict[str, Any]] = None):
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
        if error_details:
            task_info.error_details = error_details
        if failure_type:
            task_info.failure_type = failure_type
        if llm_interaction:
            from ..models.schema import LLMInteraction
            task_info.llm_interaction = LLMInteraction(**llm_interaction)

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
    try:
        print(f"🔍 [API] 收到请求: {request}")
        
        # 检查并发任务数量
        active_tasks = sum(1 for task in task_storage.values() 
                          if task.status in [TaskStatus.PENDING, TaskStatus.AI_ANALYZING, 
                                           TaskStatus.CODE_VALIDATING, TaskStatus.EXECUTING])
        
        if active_tasks >= config_storage["max_concurrent_tasks"]:
            print(f"❌ [API] 任务数超限: {active_tasks}/{config_storage['max_concurrent_tasks']}")
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
        print(f"✅ [API] 创建任务: {task_id}, 模式: {request.processing_mode}")
        
        # 添加后台任务
        if request.processing_mode == ProcessingMode.AI:
            # 检查API密钥
            print(f"🔑 [API] 检查API密钥配置, 提供商: {request.llm_provider}")
            llm_manager = get_llm_manager()
            available_providers = llm_manager.get_available_providers()
            print(f"🔍 [API] 可用提供商: {available_providers}")
            
            if request.llm_provider not in available_providers:
                error_msg = f"未配置{request.llm_provider.value}的API密钥"
                print(f"❌ [API] {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)
            
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
        
        print(f"✅ [API] 任务创建成功: {task_id}")
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，正在处理中...",
            estimated_time=estimated_time
        )
        
    except HTTPException as e:
        print(f"❌ [API] HTTP异常: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        print(f"💥 [API] 未预期异常: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

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
    # 更新配置管理器
    config_manager = get_config_manager()
    config_manager.set_api_key(provider, api_key)
    
    # 更新LLM管理器
    llm_manager = get_llm_manager()
    llm_manager.set_api_key(provider, api_key)
    
    return {"message": f"{provider.value}的API密钥已设置"}

@router.post("/config/base-url")
async def set_base_url(provider: LLMProvider, base_url: str):
    """
    设置Base URL
    
    Args:
        provider: 模型提供商
        base_url: Base URL
    """
    # 更新配置管理器
    config_manager = get_config_manager()
    config_manager.set_base_url(provider, base_url)
    
    return {"message": f"{provider.value}的Base URL已设置为: {base_url}"}

@router.get("/config")
async def get_config():
    """获取当前配置"""
    config_manager = get_config_manager()
    llm_manager = get_llm_manager()
    
    return {
        "configured_providers": [p.value for p in config_manager.get_configured_providers()],
        "default_provider": config_manager.get_default_provider().value,
        "default_execution_mode": config_storage["default_execution_mode"],
        "max_concurrent_tasks": config_storage["max_concurrent_tasks"],
        "config_summary": config_manager.get_config_summary()
    }

@router.post("/config")
async def update_config(
    default_provider: Optional[LLMProvider] = None,
    default_execution_mode: Optional[str] = None,
    max_concurrent_tasks: Optional[int] = None
):
    """更新配置"""
    config_manager = get_config_manager()
    
    if default_provider:
        config_manager.default_provider = default_provider
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


@router.post("/test/error/{error_type}")
async def test_error_scenario(error_type: str):
    """
    测试错误场景的端点
    error_type: api_error, ai_analysis_failed, code_execution_failed
    """
    import uuid
    from datetime import datetime
    
    task_id = f"test_error_{uuid.uuid4().hex[:8]}"
    
    # 先创建任务
    task_info = TaskInfo(
        task_id=task_id,
        status=TaskStatus.PENDING,
        progress=0,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        processing_mode=ProcessingMode.AI
    )
    task_storage[task_id] = task_info
    
    # 创建不同类型的错误详情
    if error_type == "api_error":
        error_details = ErrorDetails(
            error_type="api_error",
            error_message="API调用失败: 无效的API密钥",
            api_response='{"error": {"type": "invalid_api_key", "message": "Invalid API key provided", "code": "invalid_api_key"}}',
            timestamp=datetime.now().isoformat()
        )
        update_task_status(task_id, TaskStatus.API_ERROR, 0, error_details=error_details)
        
    elif error_type == "ai_analysis_failed":
        error_details = ErrorDetails(
            error_type="ai_analysis_failed", 
            error_message="LLM生成的代码格式不正确",
            api_response='{"choices": [{"message": {"content": "这是一个无效的代码响应，缺少必要的Python代码块"}}]}',
            validation_errors=[
                "缺少必要的import语句",
                "函数定义不完整", 
                "代码块格式错误",
                "未找到有效的matplotlib绘图代码"
            ],
            timestamp=datetime.now().isoformat()
        )
        update_task_status(task_id, TaskStatus.AI_ANALYSIS_FAILED, 0, error_details=error_details)
        
    elif error_type == "code_execution_failed":
        error_details = ErrorDetails(
            error_type="code_execution_failed",
            error_message="代码执行过程中发生错误",
            generated_code='''import matplotlib.pyplot as plt
import numpy as np

# 这段代码会导致错误
x = np.linspace(-10, 10, 100)
y = x ** 2
plt.plot(x, y)
plt.title("函数 y = x²的图像")
plt.xlabel("x")
plt.ylabel("y")
plt.save_fig("invalid_method.png")  # 错误的方法名
plt.show()''',
            stack_trace='''Traceback (most recent call last):
  File "/tmp/temp_math_viz_abc123.py", line 10, in <module>
    plt.save_fig("invalid_method.png")
AttributeError: module 'matplotlib.pyplot' has no attribute 'save_fig'
Did you mean: 'savefig'?''',
            execution_logs='''开始执行代码...
导入matplotlib.pyplot模块成功
导入numpy模块成功
生成数据点成功: x范围[-10, 10], 100个点
绘制曲线成功
设置标题成功: "函数 y = x²的图像"
设置x轴标签成功: "x"
设置y轴标签成功: "y"
尝试保存图片...
错误: 'save_fig' 方法不存在，应该使用 'savefig'
执行失败!''',
            timestamp=datetime.now().isoformat()
        )
        update_task_status(task_id, TaskStatus.CODE_EXECUTION_FAILED, 0, error_details=error_details)
        
    else:
        return {"error": f"不支持的错误类型: {error_type}"}
    
    return {
        "task_id": task_id,
        "error_type": error_type,
        "message": f"已创建{error_type}类型的测试错误场景",
        "task_url": f"/api/v2/tasks/{task_id}"
    }

# 导出路由器
__all__ = ['router']
