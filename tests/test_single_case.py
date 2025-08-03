#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个测试用例 - 用于调试
"""

import requests
import json
import time
from datetime import datetime

def test_single_case():
    """测试单个案例"""
    base_url = "http://localhost:8004/api/v2"
    
    print("🚀 开始单个测试用例")
    print("=" * 60)
    
    # 测试用例
    test_data = {
        "text": "甲、乙两地相距300公里，汽车从甲地出发，速度为60公里/小时，求5小时后汽车的位置。",
        "user_id": f"test_{int(time.time())}",
        "llm_provider": "claude",
        "prompt_variant": "default"
    }
    
    print(f"📝 测试题目: {test_data['text']}")
    print(f"🔧 提供商: {test_data['llm_provider']}")
    
    # 1. 生成任务
    print("\n🚀 步骤1: 生成任务")
    try:
        response = requests.post(f"{base_url}/problems/generate", json=test_data, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"   ✅ 任务创建成功: {task_id}")
            print(f"   📊 响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"   ❌ 任务创建失败: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")
        return
    
    # 2. 轮询状态
    print(f"\n🔄 步骤2: 轮询任务状态")
    max_polls = 50
    poll_interval = 3
    
    for i in range(max_polls):
        time.sleep(poll_interval)
        
        try:
            response = requests.get(f"{base_url}/tasks/{task_id}", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                current_status = status_data.get("status")
                progress = status_data.get("progress", 0)
                
                print(f"   轮询 #{i+1}: {current_status} ({progress}%)")
                
                # 显示详细信息
                if status_data.get("ai_analysis"):
                    ai_analysis = status_data["ai_analysis"]
                    print(f"   📋 AI分析:")
                    print(f"      - 题目类型: {ai_analysis.get('problem_type')}")
                    print(f"      - 置信度: {ai_analysis.get('confidence')}")
                    print(f"      - 参数: {ai_analysis.get('parameters')}")
                
                if status_data.get("execution_result"):
                    exec_result = status_data["execution_result"]
                    print(f"   🎯 执行结果:")
                    print(f"      - 成功: {exec_result.get('success')}")
                    print(f"      - 图片路径: {exec_result.get('image_path')}")
                
                if status_data.get("error_message"):
                    print(f"   ❌ 错误信息: {status_data['error_message']}")
                
                # 检查终止条件
                if current_status in ["completed", "failed"]:
                    print(f"\n🏁 任务结束: {current_status}")
                    
                    if current_status == "completed":
                        print("✅ 测试成功！")
                    else:
                        print("❌ 测试失败！")
                        print(f"📄 完整响应: {json.dumps(status_data, ensure_ascii=False, indent=2)}")
                    
                    return status_data
            else:
                print(f"   ⚠️  状态查询失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ⚠️  轮询异常: {str(e)}")
    
    print("⏰ 轮询超时")
    return None

if __name__ == "__main__":
    print(f"🕒 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    result = test_single_case()
    print(f"🕒 结束时间: {datetime.now().strftime('%H:%M:%S')}")
