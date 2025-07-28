#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试脚本来诊断Pydantic问题
"""

def test_pydantic_basic():
    """测试基础Pydantic功能"""
    try:
        from pydantic import BaseModel, Field
        from typing import Dict, Any, Optional
        from enum import Enum
        
        class TestEnum(str, Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"
        
        class TestModel(BaseModel):
            name: str = Field(..., description="测试名称")
            value: int = Field(0, description="测试值")
            data: Optional[Dict[str, Any]] = Field(None, description="测试数据")
            enum_field: TestEnum = Field(TestEnum.VALUE1, description="枚举字段")
        
        # 创建测试实例
        test_instance = TestModel(
            name="测试",
            value=42,
            data={"key": "value"},
            enum_field=TestEnum.VALUE2
        )
        
        print(f"✅ 基础Pydantic测试成功")
        print(f"   模型: {test_instance.name}")
        print(f"   值: {test_instance.value}")
        print(f"   枚举: {test_instance.enum_field}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础Pydantic测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_import():
    """测试模型导入"""
    try:
        from backend.models.schema import ProblemRequest, LLMProvider
        print(f"✅ 模型导入成功")
        
        # 尝试创建实例
        request = ProblemRequest(
            text="这是一个足够长的测试题目，用来验证系统功能",
            llm_provider=LLMProvider.OPENAI
        )
        print(f"✅ 模型实例创建成功: {request.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yaml_import():
    """测试YAML导入"""
    try:
        import yaml
        
        test_data = {
            "test_key": "test_value",
            "test_list": [1, 2, 3],
            "test_dict": {"nested": "value"}
        }
        
        yaml_str = yaml.dump(test_data)
        loaded_data = yaml.safe_load(yaml_str)
        
        print(f"✅ YAML测试成功")
        print(f"   原始: {test_data}")
        print(f"   加载: {loaded_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML测试失败: {e}")
        return False

def main():
    """运行诊断测试"""
    print("🔍 运行诊断测试...\n")
    
    results = []
    
    # 基础测试
    print("1. 测试基础Pydantic功能:")
    results.append(test_pydantic_basic())
    
    print("\n2. 测试YAML功能:")
    results.append(test_yaml_import())
    
    print("\n3. 测试模型导入:")
    results.append(test_models_import())
    
    # 结果汇总
    print("\n" + "="*40)
    print("诊断结果汇总:")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有诊断测试通过！")
    else:
        print("❌ 部分诊断测试失败，需要检查配置")
    
    return passed == total

if __name__ == "__main__":
    main()
