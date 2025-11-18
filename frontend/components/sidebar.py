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
        elif st.session_state.initializing:
            st.info("🔄 系统初始化中...")
        else:
            st.warning("⚠️ 系统未初始化")
        
        # 初始化按钮 - 已初始化或正在初始化时禁用
        button_disabled = st.session_state.initialized or st.session_state.initializing
        if st.button("🚀 初始化系统", type="primary", use_container_width=True, disabled=button_disabled):
            # 先设置状态标志，让按钮立即禁用
            st.session_state.initializing = True
            st.rerun()
        
        # 检测初始化状态并执行初始化
        if st.session_state.initializing and not st.session_state.initialized:
            # 不使用 spinner，因为 initialize_hospital() 内部有详细的进度显示
            success, message = initialize_hospital()
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()
        
        st.divider()
        
        # 治疗设置
        st.subheader("治疗参数设置")
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
        
        st.divider()
        
        # 治疗控制台
        st.subheader("🎮 治疗控制台")
        
        # 获取当前状态
        treatment_status = st.session_state.treatment_status
        is_initialized = st.session_state.initialized
        
        # 按钮状态逻辑
        start_disabled = not is_initialized or treatment_status in ['running', 'paused']
        pause_disabled = treatment_status != 'running'
        resume_disabled = treatment_status != 'paused'
        stop_disabled = treatment_status not in ['running', 'paused']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ 开始", type="primary", use_container_width=True, disabled=start_disabled):
                if not is_initialized:
                    st.warning("⚠️ 请先初始化系统")
                else:
                    st.session_state.treatment_control = 'start'
                    st.session_state.treatment_status = 'running'
                    st.rerun()
            
            if st.button("⏸️ 暂停", use_container_width=True, disabled=pause_disabled):
                st.session_state.treatment_control = 'pause'
                st.session_state.treatment_status = 'paused'
        
        with col2:
            if st.button("▶️ 继续", use_container_width=True, disabled=resume_disabled):
                st.session_state.treatment_control = 'resume'
                st.session_state.treatment_status = 'running'
            
            if st.button("⏹️ 终止", use_container_width=True, disabled=stop_disabled):
                st.session_state.treatment_control = 'stop'
                st.session_state.treatment_status = 'stopped'
        
        # 显示当前状态
        status_text = {
            'idle': '⚪ 空闲',
            'running': '🟢 运行中',
            'paused': '🟡 已暂停',
            'stopped': '🔴 已终止'
        }
        st.caption(f"当前状态: {status_text.get(treatment_status, '未知')}")
        
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
