"""
快速启动脚本 - 用于快速测试系统
"""
import os
import sys


def check_environment():
    """检查环境配置"""
    print("=" * 80)
    print("环境检查")
    print("=" * 80)
    
    # 检查 .env 文件
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        print("   请复制 .env.example 为 .env 并配置 API Key")
        return False
    
    # 检查 API Key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY 未配置")
        print("   请在 .env 文件中设置你的 OpenAI API Key")
        return False
    
    print("✓ .env 文件配置正确")
    
    # 检查必要的目录
    required_dirs = ['config', 'knowledge_base', 'agents', 'rag', 'utils']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 目录不存在: {dir_name}")
            return False
    
    print("✓ 项目结构完整")
    
    # 检查依赖包
    try:
        import openai
        import chromadb
        import langchain
        from PIL import Image
        print("✓ 依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {str(e)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    print("\n环境检查通过！\n")
    return True


def run_quick_test():
    """运行快速测试"""
    print("=" * 80)
    print("快速测试")
    print("=" * 80)
    print()
    
    print("正在初始化系统...")
    
    try:
        from main import MedicalDiagnosisSystem
        from example_cases import CASE_ACS
        
        # 初始化系统
        system = MedicalDiagnosisSystem()
        
        print("\n" + "=" * 80)
        print("运行示例病例：急性冠脉综合征")
        print("=" * 80)
        
        # 显示病例信息
        print("\n【病例信息】")
        print(f"年龄: {CASE_ACS['patient_info']['age']}")
        print(f"性别: {CASE_ACS['patient_info']['gender']}")
        print(f"主诉: {CASE_ACS['patient_info']['chief_complaint']}")
        print(f"\n主要症状:")
        for symptom in CASE_ACS['symptoms'][:3]:
            print(f"  - {symptom}")
        
        # 执行诊断
        result = system.diagnose(CASE_ACS, include_images=False)
        
        # 打印结果
        print("\n" + "=" * 80)
        print("【诊断结果】")
        print("=" * 80)
        system.print_diagnosis(result)
        
        # 保存结果
        output_file = "./quick_test_result.json"
        system.save_diagnosis(result, output_file)
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        print(f"\n详细结果已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 80)
    print("智能多模态医疗诊断系统 - 快速启动")
    print("=" * 80)
    print("\n选项：")
    print("1. 环境检查")
    print("2. 运行快速测试")
    print("3. 运行所有示例")
    print("4. 查看使用指南")
    print("5. 退出")
    
    choice = input("\n请选择 (1-5): ").strip()
    return choice


def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 80)
    print("使用指南")
    print("=" * 80)
    print("""
【快速开始】

1. 配置 API Key
   - 编辑 .env 文件
   - 设置 OPENAI_API_KEY=你的API密钥

2. 安装依赖
   pip install -r requirements.txt

3. 运行示例
   python run_examples.py

【主要文件】

- main.py              : 主程序入口
- run_examples.py      : 运行示例病例
- example_cases.py     : 示例病例数据
- USAGE.md            : 详细使用文档
- README.md           : 项目说明

【系统组件】

- agents/             : 医生和会诊 Agent
- rag/                : RAG 知识库系统
- utils/              : 工具函数
- knowledge_base/     : 医学知识库
- config/             : 配置文件

【更多信息】

详细文档请查看 USAGE.md 和 README.md
    """)


def main():
    """主函数"""
    # 确保在正确的目录
    if not os.path.exists('main.py'):
        print("错误: 请在 A1 目录下运行此脚本")
        sys.exit(1)
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            check_environment()
            input("\n按回车键继续...")
        
        elif choice == '2':
            if check_environment():
                run_quick_test()
            input("\n按回车键继续...")
        
        elif choice == '3':
            if check_environment():
                print("\n正在运行所有示例...")
                os.system('python run_examples.py all')
            input("\n按回车键继续...")
        
        elif choice == '4':
            show_usage_guide()
            input("\n按回车键继续...")
        
        elif choice == '5':
            print("\n感谢使用！再见！")
            break
        
        else:
            print("\n无效的选择，请重试")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()
