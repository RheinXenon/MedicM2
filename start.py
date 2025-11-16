"""
启动智能医疗诊断系统可视化界面的快捷脚本
"""
import os
import sys
import subprocess
import warnings


# 禁用所有警告
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'


if __name__ == '__main__':
    # 确保在项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Streamlit应用路径
    app_path = 'app.py'
    
    print("=" * 60)
    print("🏥 正在启动智能医疗诊断系统...")
    print("=" * 60)
    print("\n📌 使用说明:")
    print("  1. 浏览器会自动打开可视化界面")
    print("  2. 如果没有自动打开，请访问: http://localhost:8501")
    print("  3. 按 Ctrl+C 可以停止服务器\n")
    print("=" * 60)
    
    # 运行streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', app_path,
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ 已停止医疗诊断系统服务器")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 请确保已安装依赖:")
        print("   pip install -r requirements.txt")
