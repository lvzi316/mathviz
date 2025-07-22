#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Manim测试脚本
用于验证Manim基本功能
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
    print("✅ ManimGL导入成功")
except ImportError as e:
    print(f"❌ ManimGL导入失败: {e}")
    print("💡 请运行: pip install manimgl")
    MANIM_AVAILABLE = False

import re

def parse_meeting_problem(text):
    """解析相遇问题的参数"""
    distance_match = re.search(r'相距(\d+)公里', text)
    distance = int(distance_match.group(1)) if distance_match else 480
    
    speed1_match = re.search(r'速度为(\d+)公里/小时', text)
    speed1 = int(speed1_match.group(1)) if speed1_match else 60
    
    speeds = re.findall(r'(\d+)公里/小时', text)
    speed2 = int(speeds[1]) if len(speeds) > 1 else 80
    
    return distance, speed1, speed2

if MANIM_AVAILABLE:
    class SimpleMeetingScene(Scene):
        """简化的相遇问题场景"""
        
        def construct(self):
            # 基本测试
            title = Text("Manim测试 - 相遇问题", font_size=48)
            self.play(Write(title))
            self.wait(1)
            
            # 创建简单的道路
            road = Line(LEFT * 4, RIGHT * 4, stroke_width=6, color=GREY)
            self.play(ShowCreation(road))
            
            # 创建两个车辆
            car1 = Circle(radius=0.2, color=RED, fill_opacity=0.8)
            car1.move_to(LEFT * 4)
            
            car2 = Square(side_length=0.4, color=BLUE, fill_opacity=0.8)
            car2.move_to(RIGHT * 4)
            
            self.play(ShowCreation(car1), ShowCreation(car2))
            self.wait(1)
            
            # 简单的相遇动画
            meeting_point = ORIGIN
            self.play(
                car1.animate.move_to(meeting_point + UP * 0.3),
                car2.animate.move_to(meeting_point + DOWN * 0.3),
                run_time=3
            )
            
            # 相遇标记
            star = RegularPolygon(5, color=YELLOW, fill_opacity=0.8)
            star.move_to(meeting_point)
            self.play(ShowCreation(star))
            
            meeting_text = Text("相遇!", font_size=36, color=YELLOW)
            meeting_text.move_to(UP * 2)
            self.play(Write(meeting_text))
            
            self.wait(2)

    class SimpleChaseScene(Scene):
        """简化的追及问题场景"""
        
        def construct(self):
            # 标题
            title = Text("Manim测试 - 追及问题", font_size=48)
            self.play(Write(title))
            self.wait(1)
            
            # 道路
            road = Line(LEFT * 5, RIGHT * 5, stroke_width=6, color=GREY)
            self.play(ShowCreation(road))
            
            # 车辆
            car1 = Circle(radius=0.2, color=RED, fill_opacity=0.8)  # 客车
            car2 = Square(side_length=0.4, color=BLUE, fill_opacity=0.8)  # 货车
            
            start_pos = LEFT * 5
            car1.move_to(start_pos + UP * 0.3)
            car2.move_to(start_pos + DOWN * 0.3)
            
            self.play(ShowCreation(car1), ShowCreation(car2))
            self.wait(1)
            
            # 阶段1: 客车先行
            stage1_text = Text("阶段1: 客车先行", font_size=24)
            stage1_text.to_edge(UP)
            self.play(Write(stage1_text))
            
            # 客车先移动
            self.play(
                car1.animate.shift(RIGHT * 2),
                car2.animate.shift(RIGHT * 1),
                run_time=2
            )
            
            # 阶段2: 货车加速追赶
            stage2_text = Text("阶段2: 货车加速追赶", font_size=24)
            self.play(Transform(stage1_text, stage2_text))
            
            # 追及动画
            final_pos = RIGHT * 3
            self.play(
                car1.animate.move_to(final_pos + UP * 0.3),
                car2.animate.move_to(final_pos + DOWN * 0.3),
                run_time=3
            )
            
            # 追及成功
            success_star = RegularPolygon(5, color=YELLOW, fill_opacity=0.8)
            success_star.move_to(final_pos)
            self.play(ShowCreation(success_star))
            
            success_text = Text("追及成功!", font_size=36, color=YELLOW)
            success_text.move_to(DOWN * 2)
            self.play(Write(success_text))
            
            self.wait(2)

def test_manim_installation():
    """测试Manim安装和基本功能"""
    print("🔍 测试Manim安装状态...")
    
    if not MANIM_AVAILABLE:
        print("❌ Manim未安装或导入失败")
        return False
    
    try:
        # 测试基本类的可用性
        test_scene = Scene()
        test_text = Text("测试")
        test_circle = Circle()
        print("✅ Manim基本类可用")
        
        # 测试题目解析
        meeting_text = """甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；
        同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？"""
        
        distance, speed1, speed2 = parse_meeting_problem(meeting_text)
        print(f"✅ 题目解析成功: 距离={distance}km, 速度1={speed1}km/h, 速度2={speed2}km/h")
        
        return True
        
    except Exception as e:
        print(f"❌ Manim测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎬 Manim简化测试脚本")
    print("=" * 50)
    
    # 测试安装
    if test_manim_installation():
        print("\n🎉 Manim测试通过!")
        print("\n📋 可用的场景类:")
        print("   - SimpleMeetingScene  (简化相遇问题)")
        print("   - SimpleChaseScene    (简化追及问题)")
        
        print("\n🚀 运行动画命令:")
        print("   manimgl simple_manim_test.py SimpleMeetingScene")
        print("   manimgl simple_manim_test.py SimpleChaseScene")
        
        print("\n💡 ManimGL使用说明:")
        print("   - 直接运行: manimgl file.py ClassName")
        print("   - 交互模式: 可以实时预览和调试")
        print("   - 高质量输出: 自动保存MP4文件")
        
    else:
        print("\n❌ Manim测试失败")
        print("\n🔧 解决方案:")
        print("1. 安装manimgl: pip install manimgl")
        print("2. 或安装社区版: pip install manim-community")
        print("3. 检查系统依赖:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu: sudo apt install ffmpeg")

if __name__ == "__main__":
    main()
