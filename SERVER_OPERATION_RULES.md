# 服务器操作规范 (Server Operation Rules)

## 🎯 核心规则

### Rule 1: 服务器状态检查
**在每次重启服务器前，务必检查服务器是否在后台运行**

```bash
# 检查API服务器进程
ps aux | grep "python api_server.py" | grep -v grep

# 如果有进程在运行，先停止它
ps aux | grep "python api_server.py" | grep -v grep | awk '{print $2}' | xargs kill
```

### Rule 2: 后台运行模式
**每次重启服务器使用后台运行模式**

```bash
# 标准后台启动命令
cd /Users/chaopan/Documents/Code/mathviz
source visual_env/bin/activate
nohup python api_server.py > server.log 2>&1 &

# 确认启动成功
sleep 3 && tail -10 server.log
```

### Rule 3: 实时日志监控
**总是用一个新的终端来实时显示服务器日志**

```bash
# 实时日志监控命令
cd /Users/chaopan/Documents/Code/mathviz
tail -f server.log
```

## 📋 标准操作流程

### 启动/重启服务器的完整流程：

1. **检查当前状态**
   ```bash
   ps aux | grep "python api_server.py" | grep -v grep
   ```

2. **停止现有服务器（如果需要）**
   ```bash
   ps aux | grep "python api_server.py" | grep -v grep | awk '{print $2}' | xargs kill
   ```

3. **后台启动新服务器**
   ```bash
   cd /Users/chaopan/Documents/Code/mathviz
   source visual_env/bin/activate
   nohup python api_server.py > server.log 2>&1 &
   ```

4. **验证启动成功**
   ```bash
   sleep 3 && tail -10 server.log
   ```

5. **启动实时日志监控**
   ```bash
   tail -f server.log
   ```

## 🚨 注意事项

- **端口冲突**: 如果8001端口被占用，服务器会自动切换到8002
- **前端配置**: 确保前端的 `API_BASE_V2` 与服务器实际端口一致
- **日志文件**: 始终检查 `server.log` 获取详细的错误信息
- **进程ID**: 记录服务器启动时的进程ID便于后续管理

## 🔄 当前状态检查清单

每次操作前检查：
- [ ] 服务器进程状态
- [ ] 服务器运行端口
- [ ] 前端API配置是否匹配
- [ ] 日志监控是否开启

## 📝 操作记录模板

```
操作时间: [时间戳]
操作类型: [启动/重启/停止]
服务器端口: [8001/8002/其他]
进程ID: [PID]
状态: [成功/失败]
备注: [其他说明]
```

---
**创建时间**: 2025-08-30 10:35
**适用项目**: mathviz 数学可视化系统
**维护者**: GitHub Copilot
