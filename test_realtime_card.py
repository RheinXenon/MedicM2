"""
测试实时卡片更新功能
验证treat_single_patient_with_realtime_card函数是否正常工作
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必要的导入"""
    try:
        from frontend.components.patient_card import generate_interactive_card_html
        print("✅ generate_interactive_card_html 导入成功")
        
        import streamlit.components.v1 as components
        print("✅ streamlit.components.v1 导入成功")
        
        from frontend.components.progress_bar import TREATMENT_STEPS
        print("✅ TREATMENT_STEPS 导入成功")
        print(f"   步骤数量: {len(TREATMENT_STEPS)}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_card_generation():
    """测试卡片HTML生成"""
    try:
        from frontend.components.patient_card import generate_interactive_card_html
        
        # 创建测试数据
        steps_status = []
        for i in range(8):
            if i < 3:
                status = 'completed'
            elif i == 3:
                status = 'running'
            else:
                status = 'pending'
            
            steps_status.append({
                'status': status,
                'data': {'test': f'step_{i}'}
            })
        
        # 生成HTML
        html = generate_interactive_card_html(
            "test_card",
            "测试患者",
            "🔄 治疗进行中...",
            "result-running",
            "",
            steps_status
        )
        
        if html and '<div class="patient-card"' in html:
            print("✅ 卡片HTML生成成功")
            print(f"   HTML长度: {len(html)} 字符")
            return True
        else:
            print("❌ 卡片HTML生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 卡片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试实时卡片更新功能")
    print("=" * 60 + "\n")
    
    print("测试 1: 导入检查")
    test1 = test_imports()
    
    print("\n测试 2: 卡片生成检查")
    test2 = test_card_generation()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")
    print("=" * 60 + "\n")
