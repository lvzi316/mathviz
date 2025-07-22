# Manim 动画目录

这个目录包含用于生成数学问题动画的Manim相关文件。

## 文件说明

### 1. simple_manim_test.py
- **用途**: 简化版的Manim测试脚本
- **状态**: 基本可用
- **功能**: 
  - SimpleMeetingScene: 相遇问题动画
  - SimpleChaseScene: 追及问题动画

### 2. minimal_manim.py
- **用途**: 最小化的Manim功能测试
- **状态**: 可用
- **功能**: 基础动画测试

### 3. manim_test.py
- **用途**: 完整版Manim动画脚本
- **状态**: 功能丰富但可能需要调试
- **功能**: 完整的数学问题动画场景

### 4. MANIM_GUIDE.md
- **用途**: Manim安装和使用指南
- **内容**: 详细的安装步骤和常见问题解决

## 使用方法

### 激活环境
```bash
# 从主目录激活虚拟环境
cd ..
source visual_env/bin/activate
cd manim_animation
```

### 运行动画
```bash
# 简单测试
manimgl minimal_manim.py MinimalTest -w

# 相遇问题动画
manimgl simple_manim_test.py SimpleMeetingScene -w

# 追及问题动画
manimgl simple_manim_test.py SimpleChaseScene -w
```

### 常用参数
- `-w`: 生成视频文件
- `-s`: 只保存最后一帧
- `-l`: 低质量渲染
- `-m`: 中等质量渲染
- `--hd`: 高清渲染

## 输出位置

生成的视频文件会保存在：
- 当前目录或指定的输出目录
- 通常是 `.mp4` 格式

## 注意事项

1. **依赖要求**: 确保已安装 manimgl 和 ffmpeg
2. **字体问题**: 可能需要调整中文字体设置
3. **性能**: 动画渲染可能需要较长时间
4. **实验性**: 这些脚本还在持续改进中

## 故障排除

如果遇到问题，请参考：
1. `MANIM_GUIDE.md` - 详细的安装和配置指南
2. 主目录的 `README.md` - 项目整体说明
3. 考虑使用主目录的 `text_to_visual.py` 作为稳定的替代方案
