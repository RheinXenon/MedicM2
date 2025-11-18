"""
治疗流程页面
"""
import streamlit as st
from ..components.treatment_flow import generate_and_treat_patient


def render_treatment_page():
    """渲染治疗流程页面"""
    st.subheader("🎯 实时治疗流程可视化")
    st.markdown("""
    该界面将实时展示每个病人的完整治疗流程，包括：
    1. 📝 **病例输入** - 病人基本信息和症状
    2. 🎯 **智能分诊** - AI护士分析症状并推荐科室
    3. 📝 **挂号登记** - 完成就诊登记
    4. 👨‍⚕️ **医生问诊** - 主治医生询问病史并安排检查
    5. 🔬 **医学检查** - 进行各项医学检验
    6. 🧠 **AI智能诊断** - 大模型分析病情并给出诊断
    7. 💊 **治疗方案** - 制定个性化治疗方案
    8. 🎉 **康复评估** - 评估治疗效果
    """)
    st.divider()
    
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
        st.info("👉 请在侧边栏选择病人数量和科室，然后点击'开始治疗'按钮启动治疗流程")
