"""
运行示例病例的脚本
"""
import sys
from main import MedicalDiagnosisSystem
from example_cases import ALL_CASES, list_cases


def run_single_case(system, case_name, case_data):
    """运行单个病例"""
    print("\n" + "=" * 80)
    print(f"病例: {case_name}")
    print("=" * 80)
    
    # 显示病例信息
    print("\n病例信息：")
    patient_info = case_data.get('patient_info', {})
    print(f"- 年龄: {patient_info.get('age', '未知')}")
    print(f"- 性别: {patient_info.get('gender', '未知')}")
    print(f"- 主诉: {patient_info.get('chief_complaint', '未提供')}")
    
    # 执行诊断
    result = system.diagnose(case_data, include_images=False)
    
    # 打印结果
    print("\n" + "=" * 80)
    print("诊断结果")
    print("=" * 80 + "\n")
    system.print_diagnosis(result)
    
    # 保存结果
    filename = f"./diagnosis_{case_name.replace(' ', '_')}.json"
    system.save_diagnosis(result, filename)
    
    return result


def run_all_cases(system):
    """运行所有示例病例"""
    results = {}
    
    for case_name, case_data in ALL_CASES.items():
        try:
            result = run_single_case(system, case_name, case_data)
            results[case_name] = result
        except Exception as e:
            print(f"\n错误: 处理病例 '{case_name}' 时出错: {str(e)}")
            continue
    
    print("\n" + "=" * 80)
    print(f"所有病例诊断完成，共处理 {len(results)} 个病例")
    print("=" * 80)
    
    return results


def interactive_mode(system):
    """交互模式"""
    while True:
        print("\n" + "=" * 80)
        print("智能多模态医疗诊断系统 - 交互模式")
        print("=" * 80)
        print("\n可用命令：")
        print("1. 查看示例病例列表")
        print("2. 诊断指定病例")
        print("3. 诊断所有病例")
        print("4. 退出")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            list_cases()
        
        elif choice == '2':
            list_cases()
            case_num = input("\n请输入病例编号: ").strip()
            
            try:
                case_num = int(case_num)
                case_names = list(ALL_CASES.keys())
                
                if 1 <= case_num <= len(case_names):
                    case_name = case_names[case_num - 1]
                    case_data = ALL_CASES[case_name]
                    run_single_case(system, case_name, case_data)
                else:
                    print("无效的病例编号")
            
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '3':
            confirm = input("\n确认要诊断所有病例吗？(y/n): ").strip().lower()
            if confirm == 'y':
                run_all_cases(system)
        
        elif choice == '4':
            print("\n感谢使用！再见！")
            break
        
        else:
            print("无效的选择，请重试")


def main():
    """主函数"""
    print("正在初始化系统...")
    system = MedicalDiagnosisSystem()
    
    if len(sys.argv) > 1:
        # 命令行模式
        case_name = ' '.join(sys.argv[1:])
        
        if case_name.lower() == 'all':
            run_all_cases(system)
        elif case_name in ALL_CASES:
            run_single_case(system, case_name, ALL_CASES[case_name])
        else:
            print(f"未找到病例: {case_name}")
            list_cases()
    else:
        # 交互模式
        interactive_mode(system)


if __name__ == "__main__":
    main()
