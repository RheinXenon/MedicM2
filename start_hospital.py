"""
Agent Hospital 启动脚本
"""
import subprocess
import sys

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" " * 20 + "🏥 Agent Hospital 启动")
    print("=" * 70)
    print("\n启动 Streamlit 可视化界面...")
    print("请稍候...\n")
    
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "app_hospital_streamlit.py",
            "--server.port=8501",
            "--server.address=127.0.0.1"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n\n启动失败: {e}")
