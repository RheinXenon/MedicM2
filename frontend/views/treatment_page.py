"""
治疗流程页面
"""
import streamlit as st
from ..components.treatment_flow import generate_and_treat_patient


def render_treatment_page():
    """渲染治疗流程页面"""
    st.subheader("🎯 实时治疗流程可视化")
    
    # 初始化completed_treatments_display
    if 'completed_treatments_display' not in st.session_state:
        st.session_state.completed_treatments_display = []
    
    # 上半部分：正在治疗的实时进度
    st.markdown("### 🔄 实时治疗进度")
    real_time_container = st.container()
    
    with real_time_container:
        # 检查是否需要开始治疗
        if 'start_treatment' in st.session_state and st.session_state.start_treatment:
            st.session_state.start_treatment = False  # 重置标志
            
            # 生成并治疗病人
            hospital = st.session_state.hospital
            patient_gen = st.session_state.patient_gen
            
            # 获取侧边栏的设置
            num_patients = st.session_state.get('num_patients', 1)
            department_filter = st.session_state.get('department_filter', '全部')
            
            result = generate_and_treat_patient(num_patients, department_filter)
        else:
            st.info("👉 请在侧边栏选择病人数量和科室，然后点击‘开始治疗’按钮启动治疗流程")
    
    st.divider()
    
    # 下半部分：已完成的治疗记录
    st.markdown("### 📋 已完成的治疗记录")
    
    if st.session_state.completed_treatments_display:
        st.caption(f"共 {len(st.session_state.completed_treatments_display)} 条记录")
        # 按时间倒序显示（最新的在最上面）
        for record in st.session_state.completed_treatments_display:
            st.markdown(record, unsafe_allow_html=True)
    else:
        st.info("暂无完成的治疗记录")
