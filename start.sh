#!/bin/bash
# 项目启动脚本

echo "🚀 启动 MathViz 应用"

# 检查虚拟环境
if [ ! -d "visual_env" ]; then
    echo "❌ 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

# 激活虚拟环境
source visual_env/bin/activate

# 安装后端依赖
echo "📦 安装后端依赖..."
pip install -r requirements.txt

# 创建输出目录
mkdir -p output

# 启动后端服务
echo "🌐 启动后端API服务..."
echo "API文档地址: http://localhost:8000/docs"
echo "前端地址: 打开 frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务"

python api_server.py
