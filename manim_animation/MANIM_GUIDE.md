# Manim 测试脚本使用指南

## 🎯 功能说明

这个脚本使用Manim创建数学行程问题的动画演示，包括：
- **相遇问题动画**：展示两车相向而行的完整过程
- **追及问题动画**：展示后车追赶前车的动态过程

## 📦 安装Manim

### 方法1: 使用pip安装 (推荐)
```bash
# 在虚拟环境中安装
pip install manim

# 或者安装社区版
pip install manim-community
```

### 方法2: 使用conda安装
```bash
conda install -c conda-forge manim
```

### 依赖要求
Manim需要以下系统依赖：
- **macOS**: 
  ```bash
  brew install ffmpeg
  brew install --cask mactex  # 用于LaTeX支持
  ```
- **Ubuntu/Debian**:
  ```bash
  sudo apt install ffmpeg
  sudo apt install texlive-full
  ```

## 🚀 使用方法

### 1. 基本运行
```bash
# 生成低质量预览 (快速)
manim -pql manim_test.py MeetingProblemScene

# 生成高质量视频
manim -pqh manim_test.py MeetingProblemScene

# 生成追及问题动画
manim -pql manim_test.py ChaseProblemScene
```

### 2. 参数说明
- `-p`: 自动播放生成的视频
- `-q`: 质量设置
  - `l`: 低质量 (480p, 快速渲染)
  - `m`: 中等质量 (720p)
  - `h`: 高质量 (1080p)
  - `k`: 4K质量 (2160p)

### 3. 输出文件
默认输出位置：`./media/videos/manim_test/`

## 🎬 动画特色功能

### 相遇问题动画包含：
1. **场景构建**：道路、起点终点标记
2. **车辆创建**：不同颜色和形状的车辆
3. **运动动画**：实时显示两车运动过程
4. **时间显示**：动态更新的时间计数器
5. **相遇标记**：黄色星星标记相遇点
6. **结果展示**：相遇时间和地点信息

### 追及问题动画包含：
1. **分阶段展示**：清楚区分货车加速前后
2. **速度变化**：动态显示货车加速过程
3. **追及标记**：成功追及时的特殊效果
4. **失败处理**：当无法追及时的说明

## 🔧 自定义配置

### 修改动画参数
```python
# 在manim_test.py中修改这些参数：
config.pixel_height = 720    # 视频高度
config.pixel_width = 1280    # 视频宽度  
config.frame_rate = 30       # 帧率

# 动画时长
animation_duration = 4       # 秒
```

### 修改颜色主题
```python
self.colors = {
    'car1': RED,      # 第一辆车颜色
    'car2': BLUE,     # 第二辆车颜色
    'road': GRAY,     # 道路颜色
    'meeting_point': YELLOW  # 相遇点颜色
}
```

## 📊 与matplotlib版本对比

| 特性 | **Manim版本** | **Matplotlib版本** |
|------|-------------|------------------|
| 输出格式 | 🎥 动画视频 (MP4) | 📸 静态图片 (PNG) |
| 视觉效果 | 🌟 动态流畅 | 📊 清晰静态 |
| 文件大小 | 📈 较大 (几MB) | 📉 较小 (几KB) |
| 渲染时间 | ⏱️ 较长 (分钟级) | ⚡ 快速 (秒级) |
| 教学效果 | 🎯 过程展示 | 📋 结果展示 |
| 学习成本 | 📚 需要学习Manim | 🎓 相对简单 |

## 🚀 快速测试

```bash
# 1. 激活虚拟环境
source visual_env/bin/activate

# 2. 安装manim
pip install manim

# 3. 测试运行
python manim_test.py

# 4. 渲染动画
manim -pql manim_test.py MeetingProblemScene
```

## 💡 故障排除

### 常见问题：

1. **LaTeX错误**：
   ```bash
   # 安装完整LaTeX支持
   brew install --cask mactex  # macOS
   ```

2. **ffmpeg错误**：
   ```bash
   # 安装视频处理库
   brew install ffmpeg  # macOS
   ```

3. **导入错误**：
   ```bash
   # 确认安装正确版本
   pip install manim-community
   ```

4. **内存不足**：
   ```bash
   # 使用低质量渲染
   manim -pql --low_quality manim_test.py MeetingProblemScene
   ```

## 🎨 扩展建议

1. **添加更多题型**：流水行船、环形跑道等
2. **交互控制**：暂停、回放、速度控制
3. **多语言支持**：英文版本动画
4. **3D效果**：使用Manim的3D功能
5. **声音配音**：添加解说音轨

这个Manim版本提供了比静态图表更丰富的视觉体验，特别适合制作教学视频！
