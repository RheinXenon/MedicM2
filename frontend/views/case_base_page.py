"""
病例库页面
"""
import streamlit as st
from ..utils.data_utils import get_case_base_info


def render_case_base_page():
    """渲染病例库页面"""
    st.subheader("病例库详情")
    case_info = get_case_base_info()
    st.markdown(case_info)
    
    st.divider()
    
    # 显示详细病例
    st.markdown("### 🔍 查看具体病例")
    
    hospital = st.session_state.hospital
    if hospital and len(hospital.case_base) > 0:
        # 按科室筛选
        dept_filter = st.selectbox(
            "选择科室",
            ["全部"] + list(hospital.case_base.department_index.keys()),
            key="case_dept_filter"
        )
        
        # 获取病例
        if dept_filter == "全部":
            cases = hospital.case_base.cases[:20]  # 最多显示20个
        else:
            cases = hospital.case_base.retrieve_by_department(dept_filter, limit=20)
        
        if cases:
            st.write(f"共找到 {len(cases)} 个相关病例（最多显示20个）")
            
            for i, case in enumerate(cases, 1):
                with st.expander(f"病例 {i}: {case.get('diagnosis', {}).get('disease', '未知')} - {case.get('department', '未知科室')}"):
                    patient_info = case.get('patient_info', {})
                    st.write(f"**病例 ID:** {case.get('case_id', '未知')}")
                    st.write(f"**时间:** {case.get('timestamp', '未知')[:19]}")
                    st.write(f"**年龄:** {patient_info.get('age', '未知')}岁")
                    st.write(f"**性别:** {patient_info.get('gender', '未知')}")
                    
                    symptoms = case.get('symptoms', [])
                    st.write(f"**症状:** {', '.join(symptoms[:10]) if symptoms else '无'}")
                    
                    diagnosis = case.get('diagnosis', {})
                    st.write(f"**诊断结果:** {diagnosis.get('disease', '未知')}")
                    st.write(f"**置信度:** {diagnosis.get('confidence', '未知')}")
                    
                    if 'reasoning' in diagnosis:
                        st.write(f"**诊断依据:** {diagnosis['reasoning'][:200]}...")
                    
                    treatment = case.get('treatment', {})
                    if 'medications' in treatment:
                        st.write(f"**药物:** {', '.join(treatment['medications'][:5])}")
        else:
            st.info("该科室暂无病例")
    else:
        st.info("病例库为空，请先治疗病人")
    
    st.divider()
    if st.button("🔄 刷新病例库", key="refresh_case"):
        st.rerun()
