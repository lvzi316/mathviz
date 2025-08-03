#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题目可视化 API 服务
FastAPI后端实现 - 支持传统模式(v1)和AI驱动模式(v2)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import os
import json
import time
from datetime import datetime
from text_to_visual import MathProblemVisualizer

# 导入v2 AI驱动的端点
try:
    from backend.api.endpoints import router as v2_router
    V2_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI模块导入失败，仅启用传统模式: {e}")
    V2_AVAILABLE = False

# 创建FastAPI应用
app = FastAPI(
    title="MathViz API",
    description="数学题目可视化API服务 - 支持传统模式(v1)和AI驱动模式(v2)",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含v2 AI驱动的路由（如果可用）
if V2_AVAILABLE:
    app.include_router(v2_router)
    print("✅ AI驱动模式 (v2) 已启用")
else:
    print("⚠️  仅启用传统模式 (v1)")

# 挂载静态文件服务（用于图片）
if not os.path.exists("output"):
    os.makedirs("output")
app.mount("/static", StaticFiles(directory="output"), name="static")

# v1传统模式的数据模型
class ProblemRequest(BaseModel):
    text: str
    problem_type: Optional[str] = "auto"  # "meeting", "chase", "auto"
    user_id: Optional[str] = None

class TaskResponse(BaseModel):
    success: bool
    task_id: str
    estimated_time: int
    message: str

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# 内存存储（生产环境应使用数据库）
tasks = {}
images = {}

# 初始化可视化器
visualizer = MathProblemVisualizer()

def detect_problem_type(text: str) -> str:
    """自动检测题目类型"""
    if "相遇" in text or "相距" in text:
        return "meeting"
    elif "追" in text or "超" in text or "加速" in text:
        return "chase"
    else:
        return "meeting"  # 默认为相遇问题

def process_visualization_task(task_id: str, text: str, problem_type: str):
    """后台处理可视化任务"""
    try:
        # 更新任务状态
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        
        # 检测问题类型
        if problem_type == "auto":
            problem_type = detect_problem_type(text)
        
        tasks[task_id]["progress"] = 30
        
        # 生成图片
        image_id = str(uuid.uuid4())
        output_path = f"output/{image_id}.png"
        
        if problem_type == "meeting":
            img_path, result = visualizer.create_meeting_visualization(text, output_path)
        elif problem_type == "chase":
            img_path, result = visualizer.create_chase_visualization(text, output_path)
        else:
            raise ValueError(f"Unsupported problem type: {problem_type}")
        
        tasks[task_id]["progress"] = 80
        
        # 存储图片信息
        images[image_id] = {
            "id": image_id,
            "task_id": task_id,
            "file_path": img_path,
            "created_at": datetime.now().isoformat()
        }
        
        # 完成任务
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "result": {
                "image_id": image_id,
                "problem_analysis": {
                    "type": problem_type,
                    **result
                }
            },
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        # 任务失败
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e)
        })

@app.post("/api/v1/problems/generate", response_model=TaskResponse)
async def generate_visualization(request: ProblemRequest, background_tasks: BackgroundTasks):
    """提交题目生成可视化图表"""
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    tasks[task_id] = {
        "id": task_id,
        "user_id": request.user_id,
        "problem_text": request.text,
        "problem_type": request.problem_type,
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now().isoformat()
    }
    
    # 添加后台任务
    background_tasks.add_task(
        process_visualization_task, 
        task_id, 
        request.text, 
        request.problem_type
    )
    
    return TaskResponse(
        success=True,
        task_id=task_id,
        estimated_time=30,
        message="题目已提交，正在生成可视化图表..."
    )

@app.get("/api/v1/problems/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """查询任务状态"""
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result=task.get("result"),
        error=task.get("error")
    )

@app.get("/api/v1/images/{image_id}")
async def get_image(image_id: str):
    """获取生成的图片"""
    
    if image_id not in images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_info = images[image_id]
    file_path = image_info["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={image_id}.png"
        }
    )

@app.get("/api/v1/problems/history")
async def get_history(user_id: Optional[str] = None, limit: int = 20, offset: int = 0):
    """获取历史记录"""
    
    # 过滤任务
    filtered_tasks = []
    for task in tasks.values():
        if user_id is None or task.get("user_id") == user_id:
            if task["status"] == "completed":
                filtered_tasks.append(task)
    
    # 排序和分页
    filtered_tasks.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(filtered_tasks)
    page_tasks = filtered_tasks[offset:offset + limit]
    
    return {
        "total": total,
        "problems": page_tasks
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tasks_count": len(tasks),
        "images_count": len(images)
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "MathViz API",
        "version": "2.0.0",
        "description": "数学题目可视化API服务",
        "modes": {
            "v1": "传统规则模式 - /api/v1/*",
            "v2": "AI驱动模式 - /api/v2/*" if V2_AVAILABLE else "未启用 (缺少AI依赖)"
        },
        "docs": "/docs",
        "ai_enabled": V2_AVAILABLE
    }

@app.get("/api/status")
async def get_system_status():
    """系统状态检查"""
    return {
        "system": "MathViz API Server",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "modes": {
            "traditional_v1": True,
            "ai_driven_v2": V2_AVAILABLE
        },
        "v1_stats": {
            "tasks_count": len(tasks),
            "images_count": len(images)
        }
    }

@app.get("/api/v2/images/{image_filename}")
async def get_v2_image(image_filename: str):
    """获取V2 API生成的图片"""
    
    # 确保文件名安全，防止路径遍历攻击
    if ".." in image_filename or "/" in image_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join("output", image_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={image_filename}"
        }
    )

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 检查端口是否可用
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except OSError:
                return False
    
    # 寻找可用端口
    port = 8000
    while not is_port_available(port) and port < 8010:
        port += 1
    
    if port >= 8010:
        print("❌ 无法找到可用端口 (8000-8009)")
        exit(1)
    
    print(f"🚀 启动服务器在端口 {port}")
    print(f"📖 API文档: http://localhost:{port}/docs")
    print(f"🌐 根路径: http://localhost:{port}")
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
