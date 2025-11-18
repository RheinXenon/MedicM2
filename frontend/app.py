"""
Agent Hospital 可视化前端
基于 Streamlit 实现的实时模拟医院可视化界面（模块化版本）
"""
import streamlit as st
import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入模块
from frontend.state.session_state import init_session_state
from frontend.components.sidebar import render_sidebar
from frontend.views.treatment_page import render_treatment_page
from frontend.views.statistics_page import render_statistics_page
from frontend.views.case_base_page import render_case_base_page
from frontend.views.experience_base_page import render_experience_base_page
from frontend.views.usage_guide_page import render_usage_guide_page


# 页面配置
st.set_page_config(
    page_title="Agent Hospital - 模拟医院系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 初始化 session state
init_session_state()


# 主界面标题
st.title("🏥 Agent Hospital - 可进化的模拟医院系统")
st.markdown("""
基于论文 **"Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents"** 实现

观察医生Agent如何从治疗中学习和进化 🚀

💡 **提示**：首次使用请点击侧边栏的「初始化系统」按钮
""")


# 渲染侧边栏
render_sidebar()


# 主内容区域 - 标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 治疗流程", 
    "📊 统计", 
    "📚 病例库", 
    "🧠 经验库", 
    "📖 使用说明"
])

with tab1:
    render_treatment_page()

with tab2:
    render_statistics_page()

with tab3:
    render_case_base_page()

with tab4:
    render_experience_base_page()

with tab5:
    render_usage_guide_page()


# 页脚
st.divider()
st.caption("Agent Hospital - 基于可进化医疗Agent的模拟医院系统 | Powered by Streamlit")
