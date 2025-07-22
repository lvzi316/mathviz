# MathViz - 数学题目可视化应用

## 项目概述
MathViz是一个将中文数学应用题（特别是行程问题）转换为可视化图表的Web应用。用户输入文字描述的数学题目，系统自动解析并生成清晰的可视化图表，帮助学生更好地理解题目。

## 功能特性

### ✨ 核心功能
- 🔍 **智能解析**: 自动解析中文数学题目参数
- 📊 **可视化生成**: 生成高质量的图表和图像
- 🌐 **Web界面**: 友好的用户界面，支持桌面和移动端
- ⚡ **异步处理**: 后台异步生成图表，实时状态更新
- 📱 **响应式设计**: 完美适配各种设备屏幕

### 📚 支持的题目类型
- **相遇问题**: 两个物体相向运动的问题
- **追及问题**: 一个物体追赶另一个物体的问题
- **更多类型**: 持续扩展中...

## 技术架构

### 后端 (FastAPI)
- **框架**: FastAPI + Python
- **图像生成**: matplotlib + numpy
- **异步处理**: BackgroundTasks
- **API文档**: 自动生成Swagger文档

### 前端 (HTML/JS)
- **界面**: 现代化的响应式设计
- **交互**: 原生JavaScript，无框架依赖
- **体验**: 实时状态更新，进度条显示

## 快速开始

### 方式一：本地开发运行

#### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd mathapp

# 确保已有Python虚拟环境（从之前的步骤）
source visual_env/bin/activate
```

#### 2. 安装依赖
```bash
# 安装后端依赖
pip install -r requirements.txt
```

#### 3. 启动应用
```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动后端
python api_server.py
```

#### 4. 访问应用
- **前端界面**: 打开 `frontend/index.html`
- **API文档**: http://localhost:8000/docs
- **API根路径**: http://localhost:8000

### 方式二：Docker部署

#### 1. 使用Docker Compose（推荐）
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 2. 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000

#### 3. 单独构建Docker镜像
```bash
# 构建后端镜像
docker build -t mathviz-api .

# 运行容器
docker run -p 8000:8000 -v $(pwd)/output:/app/output mathviz-api
```

## API文档

### 主要接口

#### 1. 提交题目生成图表
```http
POST /api/v1/problems/generate
```

**请求示例**:
```json
{
  "text": "甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？",
  "problem_type": "auto",
  "user_id": "demo_user"
}
```

#### 2. 查询任务状态
```http
GET /api/v1/problems/status/{task_id}
```

#### 3. 获取生成的图片
```http
GET /api/v1/images/{image_id}
```

详细的API文档可在运行后访问 http://localhost:8000/docs 查看。

## 项目结构

```
mathapp/
├── 📄 README.md                # 项目说明
├── 📄 DESIGN_DOCUMENT.md       # 设计文档
├── 🐍 api_server.py            # FastAPI后端服务
├── 🐍 text_to_visual.py        # 核心可视化引擎
├── 📄 requirements.txt         # Python依赖
├── 🚀 start.sh                 # 启动脚本
├── 📄 Dockerfile               # Docker配置
├── 📄 docker-compose.yml       # Docker Compose配置
├── 📄 nginx.conf               # Nginx配置
├── 📁 frontend/                # 前端代码
│   └── 🌐 index.html          # 主页面
├── 📁 output/                  # 生成的图片存储
├── 📁 manim_animation/         # Manim动画相关（可选）
├── 📁 visual_env/              # Python虚拟环境
└── 📄 test.md                  # 测试题目
```

## 使用示例

### 相遇问题示例
**输入题目**:
```
甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；
同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？
```

**生成结果**:
- 📊 场景示意图：显示两地、车辆、运动方向
- 📈 位置-时间图：展示运动轨迹和相遇点
- 📋 分析结果：相遇时间、相遇地点等数据

### 追及问题示例
**输入题目**:
```
一辆客车和一辆货车同时从同一地点出发，同向而行。客车速度为90公里/小时，
货车速度为60公里/小时。客车先行2小时后，货车才开始加速，速度提高到120公里/小时。
```

**生成结果**:
- 📊 时间进程图：显示不同时刻的位置
- 📈 一维轨迹图：展示追及过程
- 📋 分析结果：是否能追上、追及时间等

## 部署指南

### 云平台推荐

#### 1. Vercel + Railway (性价比之选)
- **前端**: 部署到Vercel (免费)
- **后端**: 部署到Railway ($5/月起)
- **总成本**: $5-15/月

#### 2. AWS (企业级)
- **服务**: ECS + S3 + CloudFront + RDS
- **总成本**: $20-50/月

#### 3. 腾讯云 (国内优选)
- **服务**: 云托管 + COS + CDN + 云数据库
- **总成本**: ¥100-300/月

### 部署步骤
1. 构建Docker镜像
2. 上传到云平台
3. 配置环境变量
4. 设置域名和SSL证书
5. 配置监控和日志

详细部署指南请参考 `DESIGN_DOCUMENT.md`。

## 开发指南

### 本地开发
```bash
# 启动开发服务器
python api_server.py

# 前端开发
# 直接编辑 frontend/index.html
# 在浏览器中打开文件即可预览
```

### 添加新功能
1. **后端**: 在 `api_server.py` 中添加新的API端点
2. **可视化**: 在 `text_to_visual.py` 中扩展可视化类型
3. **前端**: 在 `frontend/index.html` 中添加新的交互功能

### 测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest tests/
```

## 常见问题

### Q: 图片生成失败怎么办？
A: 检查题目格式是否正确，确保包含必要的数值信息（距离、速度等）。

### Q: 如何添加新的题目类型？
A: 在 `text_to_visual.py` 中添加新的解析和可视化方法，然后在API中注册新类型。

### Q: 前端无法连接后端？
A: 确保后端服务正常运行，检查API地址配置，注意CORS设置。

### Q: Docker部署问题？
A: 确保Docker和Docker Compose正确安装，检查端口是否被占用。

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License

## 更新日志

- **v1.0.0**: 初始版本，支持相遇和追及问题可视化
- **v1.1.0**: 添加Web界面和API服务
- **v1.2.0**: 添加Docker支持和部署配置

---

## 联系我们

如有问题或建议，请通过以下方式联系：
- 📧 Email: [your-email]
- 🐛 Issues: [GitHub Issues]
- 📖 文档: [项目Wiki]
