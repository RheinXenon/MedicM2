"""
Agent Hospital 启动脚本
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" " * 20 + "🏥 Agent Hospital 启动")
    print("=" * 70)
    print("\n启动 Streamlit 可视化界面（模块化版本）...")
    print("请稍候...\n")
    
    # 获取frontend/app.py的绝对路径
    frontend_app_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "frontend", 
        "app.py"
    )
    
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            frontend_app_path,
            "--server.port=8501",
            "--server.address=127.0.0.1"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n\n启动失败: {e}")
