#!/bin/bash

# MathViz 启动脚本
echo "🚀 启动 MathViz 数学可视化系统..."

# 检查虚拟环境
if [ ! -d "visual_env" ]; then
    echo "创建虚拟环境..."
    python3 -m venv visual_env
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source visual_env/bin/activate

# 安装依赖
echo "安装/更新依赖..."
pip install -r backend/requirements.txt

# 创建输出目录
mkdir -p output

# 启动后端服务
echo "启动后端服务..."
cd backend
python api_server.py
