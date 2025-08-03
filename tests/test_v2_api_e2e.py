#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2 API 完整E2E测试脚本
测试从问题生成到结果获取的完整流程
"""

import sys
import os
import asyncio
import time
import json
from typing import Dict, Any, Optional
import aiohttp
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class V2ApiE2ETester:
    """V2 API E2E测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8002/api/v2"):
        """
        初始化测试器
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = None
        self.test_results = []
        self.start_time = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (INFO, WARN, ERROR, SUCCESS)
            message: 日志消息
            data: 额外数据
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix_map = {
            "INFO": "ℹ️",
            "WARN": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "DEBUG": "🔍"
        }
        prefix = prefix_map.get(level, "📝")
        
        print(f"[{timestamp}] {prefix} {message}")
        if data:
            print(f"    📊 数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    async def test_config_endpoint(self) -> bool:
        """测试配置端点"""
        self.log("INFO", "🔧 测试配置端点...")
        
        try:
            async with self.session.get(f"{self.base_url}/config") as response:
                if response.status == 200:
                    config_data = await response.json()
                    self.log("SUCCESS", "配置端点响应正常", {
                        "configured_providers": config_data.get("configured_providers", []),
                        "default_provider": config_data.get("default_provider")
                    })
                    return True
                else:
                    self.log("ERROR", f"配置端点响应异常: {response.status}")
                    return False
        except Exception as e:
            self.log("ERROR", f"配置端点请求失败: {str(e)}")
            return False
    
    async def generate_problem(self, test_case: Dict[str, Any]) -> Optional[str]:
        """
        生成问题请求
        
        Args:
            test_case: 测试用例
            
        Returns:
            Optional[str]: 任务ID，失败返回None
        """
        self.log("INFO", f"🚀 开始生成问题: {test_case['name']}")
        
        try:
            payload = {
                "text": test_case["text"],
                "user_id": f"e2e_test_{int(time.time())}",
                "llm_provider": test_case.get("llm_provider", "claude"),
                "prompt_variant": test_case.get("prompt_variant", "default")
            }
            
            self.log("DEBUG", "发送生成请求", payload)
            
            async with self.session.post(
                f"{self.base_url}/problems/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                self.log("DEBUG", f"响应状态: {response.status}, 内容: {response_text[:200]}")
                
                if response.status == 200:
                    result = await response.json()
                    task_id = result.get("task_id")
                    
                    if task_id:
                        self.log("SUCCESS", f"任务创建成功: {task_id}", {
                            "estimated_time": result.get("estimated_time"),
                            "status": result.get("status"),
                            "message": result.get("message")
                        })
                        return task_id
                    else:
                        self.log("ERROR", "响应中缺少task_id", result)
                        return None
                else:
                    self.log("ERROR", f"生成请求失败: {response.status} - {response_text}")
                    return None
                    
        except Exception as e:
            self.log("ERROR", f"生成请求异常: {str(e)}")
            return None
    
    async def poll_task_status(self, task_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """
        轮询任务状态直到完成或失败
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            Dict[str, Any]: 最终任务状态
        """
        self.log("INFO", f"🔄 开始轮询任务状态: {task_id}")
        
        start_time = time.time()
        poll_count = 0
        last_status = None
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            
            try:
                async with self.session.get(f"{self.base_url}/tasks/{task_id}") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        current_status = status_data.get("status")
                        progress = status_data.get("progress", 0)
                        
                        # 只在状态变化时记录详细日志
                        if current_status != last_status:
                            self.log("INFO", f"状态更新: {current_status} ({progress}%)", {
                                "task_id": task_id,
                                "poll_count": poll_count,
                                "elapsed_time": f"{time.time() - start_time:.1f}s"
                            })
                            last_status = current_status
                        else:
                            # 简化日志，避免过多输出
                            print(f"    ⏳ 轮询 #{poll_count}: {current_status} ({progress}%)")
                        
                        # 检查终止条件
                        if current_status in ["completed", "failed"]:
                            final_status = {
                                "status": current_status,
                                "data": status_data,
                                "total_time": time.time() - start_time,
                                "poll_count": poll_count
                            }
                            
                            if current_status == "completed":
                                self.log("SUCCESS", f"任务完成: {task_id}", {
                                    "总耗时": f"{final_status['total_time']:.1f}秒",
                                    "轮询次数": poll_count,
                                    "最终进度": progress
                                })
                            else:
                                error_msg = status_data.get("error_message", "未知错误")
                                self.log("ERROR", f"任务失败: {task_id}", {
                                    "错误信息": error_msg,
                                    "总耗时": f"{final_status['total_time']:.1f}秒",
                                    "轮询次数": poll_count
                                })
                            
                            return final_status
                    else:
                        self.log("WARN", f"状态查询失败: {response.status}")
                        
            except Exception as e:
                self.log("WARN", f"轮询异常: {str(e)}")
            
            # 等待间隔（根据轮询次数调整）
            wait_time = min(2 + poll_count * 0.1, 5)  # 2-5秒之间
            await asyncio.sleep(wait_time)
        
        # 超时
        self.log("ERROR", f"任务轮询超时: {task_id}", {
            "max_wait_time": max_wait_time,
            "total_polls": poll_count
        })
        
        return {
            "status": "timeout",
            "data": {"error_message": f"轮询超时 ({max_wait_time}s)"},
            "total_time": time.time() - start_time,
            "poll_count": poll_count
        }
    
    async def validate_result(self, task_data: Dict[str, Any]) -> bool:
        """
        验证任务结果
        
        Args:
            task_data: 任务数据
            
        Returns:
            bool: 验证是否通过
        """
        self.log("INFO", "🔍 验证任务结果...")
        
        try:
            # 检查基本字段
            required_fields = ["task_id", "status", "created_at", "updated_at"]
            for field in required_fields:
                if field not in task_data:
                    self.log("ERROR", f"缺少必需字段: {field}")
                    return False
            
            # 检查AI分析结果
            ai_analysis = task_data.get("ai_analysis")
            if ai_analysis:
                self.log("SUCCESS", "包含AI分析结果", {
                    "problem_type": ai_analysis.get("problem_type"),
                    "confidence": ai_analysis.get("confidence"),
                    "processing_time": ai_analysis.get("processing_time")
                })
            else:
                self.log("WARN", "缺少AI分析结果")
            
            # 检查执行结果
            execution_result = task_data.get("execution_result")
            if execution_result:
                self.log("SUCCESS", "包含执行结果", {
                    "success": execution_result.get("success"),
                    "image_path": execution_result.get("image_path"),
                    "execution_time": execution_result.get("execution_time")
                })
                
                # 检查图片是否生成
                image_path = execution_result.get("image_path")
                if image_path and os.path.exists(image_path):
                    self.log("SUCCESS", f"图片文件存在: {image_path}")
                else:
                    self.log("WARN", f"图片文件不存在: {image_path}")
            else:
                self.log("WARN", "缺少执行结果")
            
            return True
            
        except Exception as e:
            self.log("ERROR", f"结果验证异常: {str(e)}")
            return False
    
    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个测试用例
        
        Args:
            test_case: 测试用例
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        test_start_time = time.time()
        
        self.log("INFO", f"🧪 开始测试用例: {test_case['name']}")
        self.log("INFO", f"题目内容: {test_case['text'][:50]}...")
        
        result = {
            "test_case": test_case["name"],
            "success": False,
            "task_id": None,
            "total_time": 0,
            "error": None,
            "stages": {}
        }
        
        try:
            # 阶段1: 生成问题
            self.log("INFO", "📝 阶段1: 生成问题")
            stage1_start = time.time()
            
            task_id = await self.generate_problem(test_case)
            if not task_id:
                result["error"] = "问题生成失败"
                return result
            
            result["task_id"] = task_id
            result["stages"]["generate"] = {
                "success": True,
                "time": time.time() - stage1_start
            }
            
            # 阶段2: 轮询状态
            self.log("INFO", "🔄 阶段2: 轮询任务状态")
            stage2_start = time.time()
            
            poll_result = await self.poll_task_status(task_id, max_wait_time=test_case.get("timeout", 300))
            
            result["stages"]["polling"] = {
                "success": poll_result["status"] == "completed",
                "time": time.time() - stage2_start,
                "poll_count": poll_result["poll_count"],
                "final_status": poll_result["status"]
            }
            
            if poll_result["status"] != "completed":
                result["error"] = f"任务未成功完成: {poll_result['status']}"
                return result
            
            # 阶段3: 验证结果
            self.log("INFO", "✅ 阶段3: 验证结果")
            stage3_start = time.time()
            
            validation_success = await self.validate_result(poll_result["data"])
            
            result["stages"]["validation"] = {
                "success": validation_success,
                "time": time.time() - stage3_start
            }
            
            if not validation_success:
                result["error"] = "结果验证失败"
                return result
            
            # 测试成功
            result["success"] = True
            self.log("SUCCESS", f"✨ 测试用例完成: {test_case['name']}")
            
        except Exception as e:
            result["error"] = f"测试异常: {str(e)}"
            self.log("ERROR", f"测试用例异常: {str(e)}")
        
        finally:
            result["total_time"] = time.time() - test_start_time
        
        return result
    
    def get_test_cases(self) -> list[Dict[str, Any]]:
        """获取测试用例"""
        return [
            {
                "name": "简单数学问题",
                "text": "甲、乙两地相距300公里，汽车从甲地出发，速度为60公里/小时，求5小时后汽车的位置。",
                "llm_provider": "claude",
                "timeout": 180
            },
            {
                "name": "相遇问题",
                "text": "甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？",
                "llm_provider": "claude",
                "timeout": 240
            },
            {
                "name": "追及问题",
                "text": "一辆客车和一辆货车同时从同一地点出发，同向而行。客车速度为90公里/小时，货车速度为60公里/小时。客车什么时候能追上货车？",
                "llm_provider": "claude",
                "timeout": 240
            },
            {
                "name": "复杂应用题",
                "text": "小明骑自行车从家出发，先以12公里/小时的速度骑行30分钟，然后休息10分钟，接着以15公里/小时的速度继续骑行20分钟到达图书馆。求小明从家到图书馆的总距离。",
                "llm_provider": "claude",
                "timeout": 300
            }
        ]
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.start_time = time.time()
        
        self.log("INFO", "🚀 开始V2 API E2E测试")
        print("=" * 80)
        
        # 测试配置
        config_ok = await self.test_config_endpoint()
        if not config_ok:
            self.log("ERROR", "配置检查失败，终止测试")
            return
        
        print()
        
        # 获取测试用例
        test_cases = self.get_test_cases()
        self.log("INFO", f"📋 准备运行 {len(test_cases)} 个测试用例")
        
        # 运行测试
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'─' * 60}")
            self.log("INFO", f"🔥 测试 {i}/{len(test_cases)}")
            
            test_result = await self.run_single_test(test_case)
            self.test_results.append(test_result)
            
            # 简单的结果反馈
            if test_result["success"]:
                self.log("SUCCESS", f"测试通过 ({test_result['total_time']:.1f}s)")
            else:
                self.log("ERROR", f"测试失败: {test_result['error']}")
            
            # 测试间隔
            if i < len(test_cases):
                await asyncio.sleep(2)
        
        # 生成测试报告
        await self.generate_report()
    
    async def generate_report(self):
        """生成测试报告"""
        print(f"\n{'=' * 80}")
        self.log("INFO", "📊 生成测试报告")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        total_time = time.time() - self.start_time
        
        print(f"\n📈 总体统计:")
        print(f"  • 总测试数: {total_tests}")
        print(f"  • 成功数: {successful_tests} ✅")
        print(f"  • 失败数: {failed_tests} ❌")
        print(f"  • 成功率: {(successful_tests/total_tests*100):.1f}%")
        print(f"  • 总耗时: {total_time:.1f}秒")
        
        print(f"\n📋 详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"  {status_icon} {result['test_case']} ({result['total_time']:.1f}s)")
            
            if result["task_id"]:
                print(f"    └─ 任务ID: {result['task_id']}")
            
            if not result["success"] and result["error"]:
                print(f"    └─ 错误: {result['error']}")
            
            # 显示阶段信息
            for stage_name, stage_info in result["stages"].items():
                stage_icon = "✅" if stage_info["success"] else "❌"
                print(f"    └─ {stage_name}: {stage_icon} ({stage_info['time']:.1f}s)")
        
        print(f"\n🏁 E2E测试完成！")
        
        # 保存详细报告到文件
        report_file = f"e2e_test_report_{int(time.time())}.json"
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests/total_tests*100,
                "total_time": total_time,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.log("INFO", f"📄 详细报告已保存: {report_file}")

async def main():
    """主函数"""
    async with V2ApiE2ETester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    # 设置asyncio的事件循环策略（macOS兼容性）
    if sys.platform == 'darwin':
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    asyncio.run(main())
