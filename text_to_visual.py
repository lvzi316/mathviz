#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学题目文字转可视化图片工具
支持行程问题的自动可视化生成
"""

import matplotlib
matplotlib.use('Agg')  # 使用无GUI后端
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
import re
from PIL import Image, ImageDraw, ImageFont
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MathProblemVisualizer:
    def __init__(self):
        self.fig_size = (12, 8)
        self.colors = {
            'car1': '#FF6B6B',  # 红色
            'car2': '#4ECDC4',  # 青色
            'road': '#95A5A6',  # 灰色
            'text': '#2C3E50'   # 深蓝色
        }
    
    def parse_meeting_problem(self, text):
        """解析相遇问题的参数"""
        # 提取距离
        distance_match = re.search(r'相距(\d+)公里', text)
        distance = int(distance_match.group(1)) if distance_match else 480
        
        # 提取第一个速度
        speed1_match = re.search(r'速度为(\d+)公里/小时', text)
        speed1 = int(speed1_match.group(1)) if speed1_match else 60
        
        # 提取第二个速度
        speeds = re.findall(r'(\d+)公里/小时', text)
        speed2 = int(speeds[1]) if len(speeds) > 1 else 80
        
        return distance, speed1, speed2
    
    def create_meeting_visualization(self, text, output_path="output/meeting_problem.png"):
        """生成相遇问题可视化图片"""
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        distance, speed1, speed2 = self.parse_meeting_problem(text)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.fig_size)
        
        # 上图：场景示意图
        ax1.set_xlim(0, distance)
        ax1.set_ylim(-2, 4)
        ax1.set_title('相遇问题场景图', fontsize=16, fontweight='bold')
        
        # 绘制道路
        road = patches.Rectangle((0, 0), distance, 0.5, 
                               facecolor=self.colors['road'], alpha=0.3)
        ax1.add_patch(road)
        
        # 绘制起点和终点
        ax1.plot(0, 0.25, 'o', markersize=15, color=self.colors['car1'], label=f'甲地 (车1: {speed1}km/h)')
        ax1.plot(distance, 0.25, 's', markersize=15, color=self.colors['car2'], label=f'乙地 (车2: {speed2}km/h)')
        
        # 计算相遇时间和地点
        meeting_time = distance / (speed1 + speed2)
        meeting_point = speed1 * meeting_time
        
        # 绘制相遇点
        ax1.plot(meeting_point, 0.25, '*', markersize=20, color='gold', 
                label=f'相遇点 ({meeting_point:.1f}km)')
        
        # 添加箭头表示运动方向
        ax1.arrow(50, 1.5, 100, 0, head_width=0.2, head_length=20, 
                 fc=self.colors['car1'], ec=self.colors['car1'])
        ax1.arrow(distance-50, 1.5, -100, 0, head_width=0.2, head_length=20, 
                 fc=self.colors['car2'], ec=self.colors['car2'])
        
        ax1.text(distance/2, 2.5, f'总距离: {distance}km', ha='center', fontsize=14, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        
        ax1.set_xlabel('距离 (公里)', fontsize=12)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 下图：位置-时间图
        time_points = np.linspace(0, meeting_time * 1.2, 100)
        pos1 = speed1 * time_points  # 车1的位置
        pos2 = distance - speed2 * time_points  # 车2的位置
        
        ax2.plot(pos1, time_points, color=self.colors['car1'], linewidth=3, 
                label=f'车1轨迹 ({speed1}km/h)')
        ax2.plot(pos2, time_points, color=self.colors['car2'], linewidth=3, 
                label=f'车2轨迹 ({speed2}km/h)')
        
        # 标记相遇点
        ax2.plot(meeting_point, meeting_time, '*', markersize=15, color='gold')
        ax2.axvline(x=meeting_point, color='red', linestyle='--', alpha=0.7)
        ax2.axhline(y=meeting_time, color='red', linestyle='--', alpha=0.7)
        
        # 添加时间标注
        ax2.text(meeting_point + distance*0.05, meeting_time, 
                f'{meeting_time:.2f}h', ha='left', va='center', 
                fontsize=12, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
        
        # 添加位置标注
        ax2.text(meeting_point, meeting_time - meeting_time*0.1, 
                f'{meeting_point:.0f}km', ha='center', va='top', 
                fontsize=12, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
        
        ax2.set_xlabel('位置 (公里)', fontsize=12)
        ax2.set_ylabel('时间 (小时)', fontsize=12)
        ax2.set_title('位置-时间变化图', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, distance)
        ax2.set_ylim(0, meeting_time * 1.2)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path, {
            'meeting_time': meeting_time,
            'meeting_point': meeting_point,
            'distance': distance,
            'speed1': speed1,
            'speed2': speed2
        }
    
    def create_chase_visualization(self, text, output_path="output/chase_problem.png"):
        """生成追及问题可视化图片"""
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 简化的追及问题参数提取
        speeds = re.findall(r'(\d+)公里/小时', text)
        speed1 = int(speeds[0]) if len(speeds) > 0 else 90  # 客车
        speed2 = int(speeds[1]) if len(speeds) > 1 else 60  # 货车初速度
        speed3 = int(speeds[2]) if len(speeds) > 2 else 75  # 货车加速后
        
        lead_time = 2  # 客车领先时间
        lead_distance = speed1 * lead_time  # 领先距离
        
        # 计算追及时间
        if speed3 > speed1:
            chase_time = lead_distance / (speed3 - speed1)
            can_chase = True
        else:
            chase_time = 10  # 设置一个合理的显示时间
            can_chase = False
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # 设置不同时间点进行展示
        if can_chase:
            time_snapshots = [0, lead_time, lead_time + chase_time/2, lead_time + chase_time]
        else:
            time_snapshots = [0, lead_time, lead_time + 3, lead_time + 6]
        
        # 计算最大位置用于设置x轴范围
        max_pos = max(speed1 * time_snapshots[-1], 
                     speed2 * lead_time + speed3 * (time_snapshots[-1] - lead_time)) * 1.1
        
        # 绘制时间快照
        for i, t in enumerate(time_snapshots):
            y_pos = 3 - i * 0.7  # 从上往下排列
            
            # 计算两车位置
            if t <= lead_time:
                pos1 = speed1 * t
                pos2 = speed2 * t
                stage_label = f"货车未加速"
            else:
                pos1 = speed1 * t
                pos2 = speed2 * lead_time + speed3 * (t - lead_time)
                stage_label = f"货车已加速"
            
            # 绘制数轴
            ax.plot([0, max_pos], [y_pos, y_pos], 'k-', linewidth=1, alpha=0.3)
            
            # 标记起点
            ax.plot(0, y_pos, '|', markersize=10, color='black')
            ax.text(-max_pos*0.05, y_pos, '起点', ha='right', va='center', fontsize=10)
            
            # 大字体显示时间
            ax.text(-max_pos*0.25, y_pos, f'T = {t:.1f}h', ha='center', va='center', 
                   fontsize=14, fontweight='bold', 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
            
            # 小字体显示阶段状态
            ax.text(-max_pos*0.15, y_pos, stage_label, ha='right', va='center', 
                   fontsize=10, style='italic', color='gray')
            
            # 绘制客车位置
            ax.plot(pos1, y_pos, 'o', markersize=12, color=self.colors['car1'], 
                   label='客车' if i == 0 else "")
            ax.text(pos1, y_pos + 0.15, f'客车\n{pos1:.0f}km', ha='center', va='bottom', 
                   fontsize=9, color=self.colors['car1'], fontweight='bold')
            
            # 绘制货车位置
            ax.plot(pos2, y_pos, 's', markersize=12, color=self.colors['car2'], 
                   label='货车' if i == 0 else "")
            ax.text(pos2, y_pos - 0.15, f'货车\n{pos2:.0f}km', ha='center', va='top', 
                   fontsize=9, color=self.colors['car2'], fontweight='bold')
            
            # 如果是追及时刻，标记特殊
            if can_chase and i == len(time_snapshots) - 1 and abs(pos1 - pos2) < 5:
                ax.plot(pos1, y_pos, '*', markersize=20, color='gold')
                ax.text(pos1, y_pos + 0.35, '追及点!', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold', color='red')
            elif not can_chase and i == len(time_snapshots) - 1:
                ax.text(max_pos * 0.5, y_pos + 0.35, '货车无法追上客车', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold', color='red')
        
        # 绘制速度信息
        ax.text(max_pos * 0.7, 3.5, f'客车速度: {speed1} km/h (恒定)', 
               fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['car1'], alpha=0.3))
        ax.text(max_pos * 0.7, 3.2, f'货车速度: {speed2} km/h → {speed3} km/h', 
               fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['car2'], alpha=0.3))
        
        # 设置图表属性
        ax.set_xlim(-max_pos*0.3, max_pos)
        ax.set_ylim(-0.5, 4)
        ax.set_xlabel('位置 (公里)', fontsize=14)
        ax.set_title('追及问题一维轨迹图 - 时间进程展示', fontsize=16, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_yticks([])  # 隐藏y轴刻度
        
        # 添加时间轴说明
        ax.text(-max_pos*0.25, 3.7, '时间轴', ha='center', va='center', 
               fontsize=12, fontweight='bold', style='italic')
        
        # 添加位置刻度
        for x in range(0, int(max_pos), 100):
            ax.axvline(x=x, color='gray', linestyle=':', alpha=0.5)
            ax.text(x, -0.3, f'{x}km', ha='center', va='top', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path, {'chase_time': chase_time if can_chase else None, 
                            'chase_point': pos1 if can_chase else None, 
                            'can_chase': can_chase}

def main():
    """主函数：演示文字转可视化功能"""
    visualizer = MathProblemVisualizer()
    
    # 测试相遇问题
    meeting_text = """甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；
    同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？"""
    
    print("正在生成相遇问题可视化...")
    img_path, result = visualizer.create_meeting_visualization(meeting_text)
    print(f"✅ 相遇问题图片已生成: {img_path}")
    print(f"📊 计算结果: {result}")
    
    # 测试追及问题
    chase_text = """一辆客车和一辆货车同时从同一地点出发，同向而行。客车速度为90公里/小时，
    货车速度为60公里/小时。客车先行2小时后，货车才开始加速，速度提高到120公里/小时。"""
    
    print("\n正在生成追及问题可视化...")
    img_path2, result2 = visualizer.create_chase_visualization(chase_text)
    print(f"✅ 追及问题图片已生成: {img_path2}")
    print(f"📊 计算结果: {result2}")

if __name__ == "__main__":
    main()
