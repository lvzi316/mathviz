# 云端部署指南

## 部署架构
- **前端**: Vercel (免费额度)
- **后端**: Railway (免费额度每月500小时)
- **图片存储**: 本地文件系统 (可升级到AWS S3)

## 部署步骤

### 1. Railway 后端部署

```bash
# 登录Railway
npm install -g @railway/cli
railway login

# 部署后端
railway create
railway up
```

**配置环境变量:**
- `ENVIRONMENT=production`
- `MATPLOTLIB_BACKEND=Agg`
- `PORT=8000` (Railway会自动设置)

### 2. Vercel 前端部署

```bash
# 安装Vercel CLI
npm install -g vercel

# 部署前端
vercel --prod
```

**注意事项:**
- 需要修改 `vercel.json` 中的Railway域名
- 替换 `your-railway-app.railway.app` 为实际Railway域名

### 3. 域名配置

**Railway后端会提供:**
- 自动生成的域名: `your-app-name.railway.app`
- 支持自定义域名

**Vercel前端会提供:**
- 自动生成的域名: `your-app-name.vercel.app`
- 支持自定义域名

## 成本分析

### 免费额度
- **Railway**: 每月500小时免费 (约20天)
- **Vercel**: 无限制静态部署
- **总成本**: $0/月 (在免费额度内)

### 付费升级
- **Railway Pro**: $5/月 (无限制使用)
- **Vercel Pro**: $20/月 (更多功能)
- **AWS S3**: ~$1-5/月 (图片存储)

## 技术可行性

✅ **高度可行的原因:**
1. FastAPI完全支持Railway部署
2. 静态前端完美适配Vercel
3. 已配置好Docker和环境变量
4. API经过完整测试验证

✅ **已解决的问题:**
1. CORS跨域配置
2. matplotlib无头模式
3. 端口和环境配置
4. Docker容器化

⚠️ **需要注意:**
1. Railway免费额度有时间限制
2. 大量图片可能需要外部存储
3. 需要配置正确的域名映射

## 部署后验证

1. 检查Railway后端: `https://your-app.railway.app/api/v1/health`
2. 检查Vercel前端: `https://your-app.vercel.app`
3. 测试完整流程: 提交问题 → 生成图片 → 显示结果

## 总结

这个云端部署方案**完全可行**，技术栈匹配度很高，成本控制在合理范围内。建议先使用免费额度进行部署和测试，根据实际使用情况再考虑升级付费计划。
