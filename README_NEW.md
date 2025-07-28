# 🧮 MathViz - 数学题目可视化系统

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个智能的数学应用题可视化系统，能够将中文描述的数学问题自动转换为直观的图表和动画。

## ✨ 功能特点

- 🤖 **智能解析**：自动识别和解析中文数学应用题
- 📊 **图表生成**：生成精美的可视化图表
- 🎯 **多题型支持**：支持相遇问题、追及问题等
- 🌐 **Web界面**：现代化的Web前端界面
- 🚀 **API服务**：RESTful API，支持异步处理
- 🐳 **容器化**：支持Docker部署
- ☁️ **云端部署**：支持Railway、Render等平台

## 🎬 演示

### 相遇问题示例
```
甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；
同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？
```

### 追及问题示例
```
一辆客车和一辆货车同时从同一地点出发，同向而行。客车速度为90公里/小时，
货车速度为60公里/小时。客车先行2小时后，货车才开始加速，速度提高到120公里/小时。
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- pip 或 conda

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/YOUR_USERNAME/mathviz.git
cd mathviz
```

2. **创建虚拟环境**
```bash
python -m venv visual_env
source visual_env/bin/activate  # macOS/Linux
# 或
visual_env\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动后端服务**
```bash
python api_server.py
```

5. **打开前端界面**
```bash
# 在浏览器中打开
open frontend/index.html
```

## 📁 项目结构

```
mathviz/
├── 📄 README.md              # 项目说明
├── 📄 requirements.txt       # Python依赖
├── 🐍 api_server.py          # FastAPI后端服务
├── 🐍 text_to_visual.py      # 核心可视化模块
├── 🐍 simple_visual.py       # 文本可视化工具
├── 📁 frontend/              # 前端文件
│   └── 📄 index.html         # Web界面
├── 📁 output/                # 生成的图片
├── 📁 manim_animation/       # 动画生成模块
├── 🐳 Dockerfile            # Docker配置
├── 🐳 docker-compose.yml    # Docker Compose配置
├── ⚙️ railway.toml          # Railway部署配置
├── ⚙️ vercel.json           # Vercel部署配置
└── 📁 docs/                 # 文档文件
```

## 🔧 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 服务器配置
PORT=8000
ENVIRONMENT=development

# CORS配置
CORS_ORIGINS=http://localhost:3000,https://*.vercel.app

# 可视化配置
MATPLOTLIB_BACKEND=Agg
```

### API端点

- `GET /` - 根路径，返回API信息
- `GET /api/v1/health` - 健康检查
- `POST /api/v1/problems/generate` - 提交题目生成任务
- `GET /api/v1/problems/status/{task_id}` - 查询任务状态
- `GET /api/v1/images/{image_id}` - 获取生成的图片
- `GET /api/v1/problems/history` - 获取历史记录
- `GET /docs` - API文档（Swagger UI）

## 🐳 Docker部署

### 本地Docker运行

```bash
# 构建镜像
docker build -t mathviz .

# 运行容器
docker run -p 8000:8000 mathviz
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## ☁️ 云端部署

### Railway部署

1. 连接GitHub仓库到Railway
2. 设置环境变量：
   - `ENVIRONMENT=production`
   - `MATPLOTLIB_BACKEND=Agg`
3. 自动部署完成

### Vercel + Railway架构

- **前端**：部署到Vercel
- **后端**：部署到Railway
- **成本**：$5/月起（Railway Hobby计划）

详细部署指南请参考：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 测试

```bash
# 运行后端测试
curl -X POST "http://localhost:8000/api/v1/problems/generate" \
  -H "Content-Type: application/json" \
  -d '{"text": "小明和小红从相距100米的两点同时出发，相向而行。小明速度为5米/秒，小红速度为3米/秒，问多少秒后两人相遇？", "problem_type": "meeting"}'

# 检查健康状态
curl http://localhost:8000/api/v1/health
```

## 🛠️ 开发指南

### 添加新题型

1. 在 `text_to_visual.py` 中添加新的解析方法
2. 在 `api_server.py` 中更新题型检测逻辑
3. 在前端添加相应的UI选项

### 自定义可视化

1. 修改 `MathProblemVisualizer` 类
2. 调整图表样式和布局
3. 添加新的图表类型

## 🤝 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目基于MIT许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [matplotlib](https://matplotlib.org/) - Python绘图库
- [Manim](https://github.com/ManimCommunity/manim) - 数学动画引擎

## 📞 联系方式

- 项目链接：[https://github.com/YOUR_USERNAME/mathviz](https://github.com/YOUR_USERNAME/mathviz)
- 问题反馈：[Issues](https://github.com/YOUR_USERNAME/mathviz/issues)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
