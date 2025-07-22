# 数学题目可视化应用设计文档

## 项目概述

### 项目名称
MathViz - 数学题目可视化应用

### 项目描述
一个将中文数学应用题（特别是行程问题）转换为可视化图表的Web应用。用户输入文字描述的数学题目，系统自动解析并生成清晰的可视化图表，帮助学生更好地理解题目。

### 核心功能
- 文字题目解析和参数提取
- 自动生成高质量可视化图表
- 异步图片生成和存储
- 实时查询生成状态
- 响应式前端界面

---

## 技术架构

### 整体架构
```
前端 (React/Vue) ↔ 后端API (FastAPI/Flask) ↔ 队列系统 (Redis/Celery) ↔ 存储 (云存储)
```

### 后端技术选型

#### 推荐方案：FastAPI + Python
**优势**:
- 基于现有的matplotlib可视化代码，无需重写
- FastAPI性能优异，自动生成API文档
- 原生支持异步处理
- 类型注解和数据验证
- 易于部署和扩展

**技术栈**:
- **Web框架**: FastAPI
- **图像生成**: matplotlib + numpy (复用现有代码)
- **异步队列**: Celery + Redis
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **文件存储**: AWS S3 / 阿里云OSS / 腾讯云COS
- **部署**: Docker + Docker Compose

#### 备选方案：Node.js + Python微服务
**技术栈**:
- **主服务**: Node.js + Express
- **图像服务**: Python + Flask (专门处理图像生成)
- **消息队列**: Redis + Bull
- **数据库**: MongoDB
- **文件存储**: 云存储服务

### 前端技术选型

#### 推荐方案：React + TypeScript
**优势**:
- 生态丰富，组件库成熟
- TypeScript提供类型安全
- 移动端兼容性好
- 开发效率高

**技术栈**:
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design / Material-UI
- **状态管理**: Zustand / Redux Toolkit
- **HTTP客户端**: Axios
- **图片预览**: react-image-gallery
- **移动端适配**: 响应式设计

#### 备选方案：Vue.js + TypeScript
**技术栈**:
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus / Vuetify
- **状态管理**: Pinia
- **HTTP客户端**: Axios

---

## API接口设计

### 1. 题目提交接口

```http
POST /api/v1/problems/generate
```

**请求体**:
```json
{
  "text": "甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？",
  "problem_type": "meeting", // "meeting" | "chase" | "auto"
  "user_id": "optional_user_id"
}
```

**响应**:
```json
{
  "success": true,
  "task_id": "uuid-task-id-12345",
  "estimated_time": 30, // 预计完成时间(秒)
  "message": "题目已提交，正在生成可视化图表..."
}
```

### 2. 任务状态查询接口

```http
GET /api/v1/problems/status/{task_id}
```

**响应**:
```json
{
  "task_id": "uuid-task-id-12345",
  "status": "completed", // "pending" | "processing" | "completed" | "failed"
  "progress": 100, // 进度百分比
  "result": {
    "image_id": "img-uuid-67890",
    "problem_analysis": {
      "type": "meeting",
      "distance": 480,
      "speed1": 60,
      "speed2": 80,
      "meeting_time": 3.43,
      "meeting_point": 205.7
    }
  },
  "error": null // 如果失败，包含错误信息
}
```

### 3. 图片获取接口

```http
GET /api/v1/images/{image_id}
```

**响应**: 直接返回图片文件（PNG格式）

**HTTP Headers**:
```
Content-Type: image/png
Cache-Control: public, max-age=86400
```

### 4. 历史记录接口

```http
GET /api/v1/problems/history?user_id={user_id}&limit=20&offset=0
```

**响应**:
```json
{
  "total": 45,
  "problems": [
    {
      "task_id": "uuid-task-id-12345",
      "text": "题目文本...",
      "image_id": "img-uuid-67890",
      "created_at": "2025-07-19T10:30:00Z",
      "problem_analysis": {...}
    }
  ]
}
```

---

## 数据库设计

### 主要表结构

```sql
-- 任务表
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100),
    problem_text TEXT NOT NULL,
    problem_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    image_id VARCHAR(36),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 图片表
CREATE TABLE images (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) REFERENCES tasks(id),
    file_path VARCHAR(500),
    cloud_url VARCHAR(500),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 问题分析结果表
CREATE TABLE problem_analysis (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(36) REFERENCES tasks(id),
    problem_type VARCHAR(20),
    parameters JSONB, -- 存储解析出的参数
    solution JSONB    -- 存储计算结果
);
```

---

## 云平台部署方案

### 1. Vercel + Railway (推荐 - 最佳性价比)

**部署架构**:
- **前端**: Vercel (免费额度充足)
- **后端**: Railway (支持Docker，$5/月起)
- **数据库**: Railway PostgreSQL
- **文件存储**: AWS S3 / Cloudflare R2
- **队列**: Railway Redis

**优势**:
- 部署简单，Git自动部署
- 成本低，初期几乎免费
- 性能良好，全球CDN
- 开发体验佳

**预估成本**: $5-15/月

### 2. AWS (企业级 - 功能最全)

**部署架构**:
- **前端**: AWS S3 + CloudFront
- **后端**: AWS Elastic Beanstalk / ECS
- **数据库**: AWS RDS (PostgreSQL)
- **文件存储**: AWS S3
- **队列**: AWS SQS + Lambda

**优势**:
- 企业级可靠性
- 功能最丰富
- 扩展性强
- 全球化部署

**预估成本**: $20-50/月（根据使用量）

### 3. 腾讯云 (国内优选 - 本土化)

**部署架构**:
- **前端**: 腾讯云COS + CDN
- **后端**: 云托管 CloudBase / CVM
- **数据库**: 云数据库PostgreSQL
- **文件存储**: 对象存储COS
- **队列**: 消息队列CMQ

**优势**:
- 国内访问速度快
- 中文文档和支持
- 价格相对友好
- 合规性好

**预估成本**: ¥100-300/月

---

## 实施计划

### 第一阶段：MVP开发 (2-3周)
1. **后端基础框架** (3-4天)
   - FastAPI项目搭建
   - 基础API接口
   - 数据库设计和ORM

2. **图像生成服务** (4-5天)
   - 复用现有matplotlib代码
   - 异步任务队列
   - 文件存储服务

3. **前端开发** (5-7天)
   - React项目搭建
   - 题目提交页面
   - 图片展示页面
   - 状态查询功能

4. **集成测试** (2-3天)
   - API联调
   - 端到端测试
   - 性能优化

### 第二阶段：功能完善 (1-2周)
- 用户系统
- 历史记录
- 题目类型扩展
- 移动端优化

### 第三阶段：生产部署 (1周)
- 云平台部署
- 监控和日志
- 性能优化
- 安全配置

---

## 成本估算

### 开发成本
- **初期开发**: 3-6周
- **维护更新**: 每月1-2天

### 运营成本 (月)
- **Vercel方案**: $5-15
- **AWS方案**: $20-50
- **腾讯云方案**: ¥100-300

### 流量预估
- **图片生成**: 每张图片2-5秒处理时间
- **存储需求**: 每张图片约500KB-2MB
- **并发处理**: 建议支持10-50个并发任务

---

## 技术亮点

1. **复用现有代码**: 基于已验证的matplotlib可视化引擎
2. **异步处理**: 支持高并发图片生成
3. **响应式设计**: 支持桌面和移动端
4. **云原生**: 容器化部署，易于扩展
5. **成本优化**: 按需扩展，最小成本启动

---

## 风险评估与应对

### 技术风险
- **图片生成性能**: 通过队列系统和缓存机制解决
- **并发处理**: 容器化部署，水平扩展
- **中文字体**: 云端字体配置，确保渲染质量

### 业务风险
- **用户增长**: 弹性架构，按需扩展
- **成本控制**: 多云部署策略，成本监控

### 解决方案
- 完善的监控和告警系统
- 自动化CI/CD流水线
- 数据备份和灾难恢复计划
