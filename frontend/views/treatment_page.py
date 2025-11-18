"""
治疗流程页面
"""
import streamlit as st
from ..components.treatment_flow import generate_and_treat_patient


def render_treatment_page():
    """渲染治疗流程页面"""
    # 初始化completed_treatments_display
    if 'completed_treatments_display' not in st.session_state:
        st.session_state.completed_treatments_display = []
    
    # 实时治疗进度标题和占位符
    st.markdown("### 🎯 实时治疗流程")
    real_time_placeholder = st.empty()
    
    st.divider()
    
    # 下半部分：已完成的治疗记录
    st.markdown("### 📋 已完成的治疗记录")
    completed_records_placeholder = st.empty()
    
    # 获取当前状态
    treatment_status = st.session_state.treatment_status
    
    # 检查是否需要开始/继续治疗
    if st.session_state.treatment_control in ['start', 'resume']:
        # 生成并治疗病人
        hospital = st.session_state.hospital
        patient_gen = st.session_state.patient_gen
        
        # 获取侧边栏的设置
        num_patients = st.session_state.get('num_patients', 1)
        department_filter = st.session_state.get('department_filter', '全部')
        
        # 传递占位符给治疗函数
        result = generate_and_treat_patient(
            num_patients, 
            department_filter,
            real_time_placeholder,
            completed_records_placeholder
        )
        
        # 治疗完成后重置状态
        if result == "completed":
            st.session_state.treatment_status = 'idle'
            st.session_state.treatment_control = None
        elif result == "stopped":
            st.session_state.treatment_status = 'idle'
            st.session_state.treatment_control = None
    else:
        # 显示提示信息
        with real_time_placeholder.container():
            if treatment_status == 'idle':
                st.info("👉 请在侧边栏设置病人数量和科室，然后点击'开始'按钮启动治疗流程")
            elif treatment_status == 'paused':
                st.warning("⏸️ 治疗已暂停，点击'继续'按钮恢复治疗")
            elif treatment_status == 'stopped':
                st.error("⏹️ 治疗已终止")
        
        # 显示已完成的记录
        with completed_records_placeholder.container():
            if st.session_state.completed_treatments_display:
                st.caption(f"共 {len(st.session_state.completed_treatments_display)} 条记录")
                # 按时间倒序显示（最新的在最上面）
                for record in st.session_state.completed_treatments_display:
                    st.markdown(record, unsafe_allow_html=True)
            else:
                st.info("暂无完成的治疗记录")
