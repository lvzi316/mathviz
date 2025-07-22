#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化Manim测试
测试基本动画功能
"""

from manimlib import *
import numpy as np

class MinimalTest(Scene):
    def construct(self):
        """最简单的动画测试"""
        # 创建文本
        title = Text("简单测试", font_size=72)
        title.to_edge(UP)
        
        # 创建圆形
        circle = Circle(radius=1, color=BLUE)
        
        # 动画效果
        self.play(Write(title))
        self.play(ShowCreation(circle))
        self.play(circle.animate.shift(RIGHT * 2))
        self.play(circle.animate.shift(DOWN * 1))
        self.play(FadeOut(circle), FadeOut(title))
        
        # 显示完成信息
        done_text = Text("✅ Manim工作正常!", font_size=48, color=GREEN)
        self.play(Write(done_text))
        self.wait(2)

if __name__ == "__main__":
    print("🎬 最小化Manim测试")
    print("运行命令: manimgl minimal_manim.py MinimalTest")
