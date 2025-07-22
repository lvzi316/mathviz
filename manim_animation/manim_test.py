#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Manim创建数学题目动画的测试脚本
支持相遇问题和追及问题的动画可视化
"""

from manim import *
import re
import numpy as np

# 配置
config.pixel_height = 720
config.pixel_width = 1280
config.frame_rate = 30

class MathProblemAnimator:
    def __init__(self):
        self.colors = {
            'car1': RED,
            'car2': BLUE, 
            'road': GRAY,
            'meeting_point': YELLOW
        }
    
    def parse_meeting_problem(self, text):
        """解析相遇问题的参数"""
        distance_match = re.search(r'相距(\d+)公里', text)
        distance = int(distance_match.group(1)) if distance_match else 480
        
        speed1_match = re.search(r'速度为(\d+)公里/小时', text)
        speed1 = int(speed1_match.group(1)) if speed1_match else 60
        
        speeds = re.findall(r'(\d+)公里/小时', text)
        speed2 = int(speeds[1]) if len(speeds) > 1 else 80
        
        return distance, speed1, speed2
    
    def parse_chase_problem(self, text):
        """解析追及问题的参数"""
        speeds = re.findall(r'(\d+)公里/小时', text)
        speed1 = int(speeds[0]) if len(speeds) > 0 else 90  # 客车
        speed2 = int(speeds[1]) if len(speeds) > 1 else 60  # 货车初速度
        speed3 = int(speeds[2]) if len(speeds) > 2 else 120  # 货车加速后
        
        lead_time = 2  # 客车领先时间
        return speed1, speed2, speed3, lead_time

class MeetingProblemScene(Scene):
    """相遇问题动画场景"""
    
    def __init__(self, problem_text, **kwargs):
        super().__init__(**kwargs)
        self.animator = MathProblemAnimator()
        self.distance, self.speed1, self.speed2 = self.animator.parse_meeting_problem(problem_text)
        self.meeting_time = self.distance / (self.speed1 + self.speed2)
        self.meeting_point = self.speed1 * self.meeting_time
    
    def construct(self):
        # 标题
        title = Text("相遇问题动画演示", font_size=48, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # 创建道路
        road_length = 10  # 屏幕单位
        road = Line(LEFT * road_length/2, RIGHT * road_length/2, color=GRAY, stroke_width=8)
        road.shift(DOWN * 1)
        
        # 创建地点标记
        start_point = Dot(LEFT * road_length/2 + DOWN * 1, color=self.animator.colors['car1'], radius=0.1)
        end_point = Dot(RIGHT * road_length/2 + DOWN * 1, color=self.animator.colors['car2'], radius=0.1)
        
        # 地点标签
        start_label = Text("甲地", font_size=24).next_to(start_point, DOWN)
        end_label = Text("乙地", font_size=24).next_to(end_point, DOWN)
        
        # 距离标注
        distance_label = Text(f"总距离: {self.distance}公里", font_size=32, color=BLUE)
        distance_label.next_to(road, UP, buff=0.5)
        
        self.play(
            Create(road),
            Create(start_point),
            Create(end_point),
            Write(start_label),
            Write(end_label),
            Write(distance_label)
        )
        self.wait(1)
        
        # 创建车辆
        car1 = Circle(radius=0.15, color=self.animator.colors['car1'], fill_opacity=0.8)
        car1.move_to(start_point.get_center() + UP * 0.3)
        
        car2 = Square(side_length=0.3, color=self.animator.colors['car2'], fill_opacity=0.8)
        car2.move_to(end_point.get_center() + UP * 0.3)
        
        # 车辆标签
        car1_label = Text(f"车1: {self.speed1}km/h", font_size=20, color=self.animator.colors['car1'])
        car1_label.next_to(car1, UP, buff=0.2)
        
        car2_label = Text(f"车2: {self.speed2}km/h", font_size=20, color=self.animator.colors['car2'])
        car2_label.next_to(car2, UP, buff=0.2)
        
        self.play(
            Create(car1),
            Create(car2),
            Write(car1_label),
            Write(car2_label)
        )
        self.wait(1)
        
        # 计算相遇点在屏幕上的位置
        meeting_screen_pos = LEFT * road_length/2 + RIGHT * road_length * (self.meeting_point / self.distance)
        meeting_screen_pos += DOWN * 1 + UP * 0.3
        
        # 创建时间显示
        time_display = DecimalNumber(0, num_decimal_places=2)
        time_display.add_updater(lambda m: m.set_value(self.meeting_time * self.car1_progress))
        time_text = Text("时间: ", font_size=24)
        time_unit = Text(" 小时", font_size=24)
        time_group = VGroup(time_text, time_display, time_unit).arrange(RIGHT)
        time_group.to_edge(UP + LEFT)
        
        self.play(Write(time_group))
        
        # 动画参数
        self.car1_progress = 0
        animation_duration = 4  # 动画持续时间（秒）
        
        # 运动动画
        def update_car1(mob):
            progress = self.car1_progress
            current_pos = LEFT * road_length/2 + RIGHT * road_length * progress * (self.meeting_point / self.distance)
            current_pos += DOWN * 1 + UP * 0.3
            mob.move_to(current_pos)
            car1_label.next_to(mob, UP, buff=0.2)
        
        def update_car2(mob):
            progress = self.car1_progress
            current_pos = RIGHT * road_length/2 - RIGHT * road_length * progress * ((self.distance - self.meeting_point) / self.distance)
            current_pos += DOWN * 1 + UP * 0.3
            mob.move_to(current_pos)
            car2_label.next_to(mob, UP, buff=0.2)
        
        car1.add_updater(update_car1)
        car2.add_updater(update_car2)
        
        # 执行运动动画
        self.play(
            UpdateFunction(lambda dt: setattr(self, 'car1_progress', 
                          min(1.0, getattr(self, 'car1_progress', 0) + dt / animation_duration))),
            run_time=animation_duration,
            rate_func=linear
        )
        
        # 清除更新器
        car1.clear_updaters()
        car2.clear_updaters()
        time_display.clear_updaters()
        
        # 标记相遇点
        meeting_star = Star(color=YELLOW, fill_opacity=0.8)
        meeting_star.move_to(meeting_screen_pos)
        
        meeting_text = Text("相遇!", font_size=36, color=YELLOW)
        meeting_text.next_to(meeting_star, UP, buff=0.5)
        
        self.play(
            Create(meeting_star),
            Write(meeting_text)
        )
        
        # 显示结果
        result_text = VGroup(
            Text(f"相遇时间: {self.meeting_time:.2f} 小时", font_size=24),
            Text(f"相遇地点: 距离甲地 {self.meeting_point:.1f} 公里", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT)
        result_text.to_edge(DOWN + RIGHT)
        
        self.play(Write(result_text))
        self.wait(3)

class ChaseProblemScene(Scene):
    """追及问题动画场景"""
    
    def __init__(self, problem_text, **kwargs):
        super().__init__(**kwargs)
        self.animator = MathProblemAnimator()
        self.speed1, self.speed2, self.speed3, self.lead_time = self.animator.parse_chase_problem(problem_text)
        
        # 计算追及参数
        lead_distance = self.speed1 * self.lead_time
        if self.speed3 > self.speed1:
            self.chase_time = lead_distance / (self.speed3 - self.speed1)
            self.can_chase = True
        else:
            self.chase_time = 10
            self.can_chase = False
    
    def construct(self):
        # 标题
        title = Text("追及问题动画演示", font_size=48, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # 创建道路
        road_length = 12
        road = Line(LEFT * road_length/2, RIGHT * road_length/2, color=GRAY, stroke_width=8)
        road.shift(DOWN * 1)
        
        # 起点标记
        start_point = Dot(LEFT * road_length/2 + DOWN * 1, color=GREEN, radius=0.1)
        start_label = Text("起点", font_size=24).next_to(start_point, DOWN)
        
        self.play(
            Create(road),
            Create(start_point),
            Write(start_label)
        )
        self.wait(1)
        
        # 创建车辆
        car1 = Circle(radius=0.15, color=self.animator.colors['car1'], fill_opacity=0.8)
        car1.move_to(start_point.get_center() + UP * 0.5)
        
        car2 = Square(side_length=0.3, color=self.animator.colors['car2'], fill_opacity=0.8)
        car2.move_to(start_point.get_center() + UP * 0.1)
        
        # 车辆标签
        car1_label = Text(f"客车: {self.speed1}km/h", font_size=20, color=self.animator.colors['car1'])
        car1_label.next_to(car1, UP, buff=0.2)
        
        car2_label = Text(f"货车: {self.speed2}→{self.speed3}km/h", font_size=20, color=self.animator.colors['car2'])
        car2_label.next_to(car2, DOWN, buff=0.2)
        
        self.play(
            Create(car1),
            Create(car2),
            Write(car1_label),
            Write(car2_label)
        )
        self.wait(1)
        
        # 时间显示
        current_time = ValueTracker(0)
        time_display = always_redraw(lambda: DecimalNumber(current_time.get_value(), num_decimal_places=1))
        time_text = Text("时间: ", font_size=24)
        time_unit = Text(" 小时", font_size=24)
        time_group = VGroup(time_text, time_display, time_unit).arrange(RIGHT)
        time_group.to_edge(UP + LEFT)
        
        self.play(Write(time_group))
        
        # 阶段1: 客车领先
        stage1_text = Text("阶段1: 客车先行", font_size=24, color=YELLOW)
        stage1_text.to_edge(DOWN + LEFT)
        self.play(Write(stage1_text))
        
        # 阶段1动画 (2小时)
        lead_distance_screen = road_length * 0.3  # 在屏幕上的领先距离
        
        self.play(
            car1.animate.shift(RIGHT * lead_distance_screen),
            car2.animate.shift(RIGHT * lead_distance_screen * (self.speed2 / self.speed1)),
            current_time.animate.set_value(self.lead_time),
            run_time=3,
            rate_func=linear
        )
        
        car1_label.next_to(car1, UP, buff=0.2)
        car2_label.next_to(car2, DOWN, buff=0.2)
        
        # 阶段2: 货车加速
        stage2_text = Text("阶段2: 货车加速追赶", font_size=24, color=ORANGE)
        self.play(Transform(stage1_text, stage2_text))
        
        # 更新货车标签
        new_car2_label = Text(f"货车: {self.speed3}km/h (加速!)", font_size=20, color=ORANGE)
        self.play(Transform(car2_label, new_car2_label))
        
        if self.can_chase:
            # 追及动画
            chase_duration = 4  # 动画时长
            
            # 计算最终位置
            final_position = car1.get_center() + RIGHT * road_length * 0.4
            
            self.play(
                car1.animate.move_to(final_position),
                car2.animate.move_to(final_position + DOWN * 0.4),
                current_time.animate.set_value(self.lead_time + self.chase_time),
                run_time=chase_duration,
                rate_func=linear
            )
            
            # 追及成功标记
            success_star = Star(color=YELLOW, fill_opacity=0.8)
            success_star.move_to(final_position + UP * 0.8)
            
            success_text = Text("追及成功!", font_size=36, color=YELLOW)
            success_text.next_to(success_star, UP, buff=0.5)
            
            self.play(
                Create(success_star),
                Write(success_text)
            )
            
            # 显示结果
            result_text = VGroup(
                Text(f"追及时间: {self.chase_time:.2f} 小时", font_size=24),
                Text(f"总用时: {self.lead_time + self.chase_time:.2f} 小时", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT)
            result_text.to_edge(DOWN + RIGHT)
            
            self.play(Write(result_text))
        
        else:
            # 无法追及的情况
            self.play(
                car1.animate.shift(RIGHT * 3),
                car2.animate.shift(RIGHT * 2),
                current_time.animate.set_value(self.lead_time + 5),
                run_time=3
            )
            
            fail_text = Text("货车无法追上客车", font_size=36, color=RED)
            fail_text.to_edge(DOWN + RIGHT)
            self.play(Write(fail_text))
        
        self.wait(3)

def create_meeting_animation(problem_text, output_path="meeting_animation.mp4"):
    """创建相遇问题动画"""
    scene = MeetingProblemScene(problem_text)
    scene.render()
    return output_path

def create_chase_animation(problem_text, output_path="chase_animation.mp4"):
    """创建追及问题动画"""
    scene = ChaseProblemScene(problem_text)
    scene.render()
    return output_path

def main():
    """主函数：演示Manim动画功能"""
    print("🎬 开始生成Manim动画...")
    
    # 测试相遇问题
    meeting_text = """甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；
    同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？"""
    
    print("\n📹 正在生成相遇问题动画...")
    print("⚠️  注意：首次运行可能需要较长时间...")
    
    try:
        # 创建相遇问题场景并渲染
        scene1 = MeetingProblemScene(meeting_text)
        print("✅ 相遇问题动画准备完成")
        
        # 测试追及问题
        chase_text = """一辆客车和一辆货车同时从同一地点出发，同向而行。客车速度为90公里/小时，
        货车速度为60公里/小时。客车先行2小时后，货车才开始加速，速度提高到120公里/小时。"""
        
        print("\n📹 正在生成追及问题动画...")
        scene2 = ChaseProblemScene(chase_text)
        print("✅ 追及问题动画准备完成")
        
        print("\n🎉 所有动画场景创建成功!")
        print("💡 要渲染动画，请运行:")
        print("   manim -pql manim_test.py MeetingProblemScene")
        print("   manim -pql manim_test.py ChaseProblemScene")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 请确保已安装manim: pip install manim")

if __name__ == "__main__":
    main()
