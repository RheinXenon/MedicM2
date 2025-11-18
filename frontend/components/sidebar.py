"""
侧边栏组件
"""
import streamlit as st
from ..utils.hospital_manager import initialize_hospital, save_current_state, clear_knowledge_bases


def render_sidebar():
    """渲染侧边栏控制面板"""
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 显示系统状态
        if st.session_state.initialized:
            st.success("✅ 系统已初始化")
        else:
            st.warning("⚠️ 系统未初始化")
        
        # 初始化按钮
        if st.button("🚀 初始化系统", type="primary", use_container_width=True):
            # 不使用 spinner，因为 initialize_hospital() 内部有详细的进度显示
            success, message = initialize_hospital()
            if success:
                st.success(message)
            else:
                st.error(message)
        
        st.divider()
        
        # 治疗设置
        st.subheader("生成并治疗病人")
        num_patients = st.number_input(
            "病人数量", 
            min_value=1, 
            max_value=1000, 
            value=1, 
            step=1, 
            key='num_patients', 
            help="输入要治疗的病人数量（1-1000）"
        )
        department_filter = st.selectbox(
            "科室筛选",
            ["全部", "心脏科", "神经科", "肿瘤科", "呼吸科", "消化科"],
            key='department_filter'
        )
        
        if st.button("🏥 开始治疗", type="primary", use_container_width=True):
            if not st.session_state.initialized:
                st.warning("⚠️ 请先初始化系统")
            else:
                st.session_state.start_treatment = True
        
        st.divider()
        
        # 系统管理
        st.subheader("系统管理")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存", use_container_width=True):
                message = save_current_state()
                if "成功" in message:
                    st.success(message)
                else:
                    st.error(message)
        
        with col2:
            if st.button("🗑️ 清空", use_container_width=True):
                message = clear_knowledge_bases()
                if "成功" in message:
                    st.success(message)
                else:
                    st.error(message)
