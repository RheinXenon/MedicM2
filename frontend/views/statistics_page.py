"""
统计页面
"""
import streamlit as st
from ..utils.data_utils import get_hospital_stats, get_evolution_chart, get_treatment_timeline


def render_statistics_page():
    """渲染统计页面"""
    st.subheader("医院统计信息")
    
    # 显示历史统计数据
    st.markdown("### 📈 历史总体统计")
    all_stats = st.session_state.all_time_stats
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总病人数", all_stats['total_patients'])
    with col2:
        success_rate = (all_stats['successful_treatments'] / all_stats['total_patients'] * 100) if all_stats['total_patients'] > 0 else 0
        st.metric("治疗成功率", f"{success_rate:.1f}%")
    with col3:
        diagnosis_rate = (all_stats['diagnosis_correct'] / all_stats['total_patients'] * 100) if all_stats['total_patients'] > 0 else 0
        st.metric("诊断准确率", f"{diagnosis_rate:.1f}%")
    with col4:
        st.metric("成功治疗", all_stats['successful_treatments'])
    
    st.divider()
    
    # 显示当前系统统计
    st.markdown("### 🏯 当前系统统计")
    stats_md = get_hospital_stats()
    st.markdown(stats_md)
    
    st.divider()
    
    # 显示图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("医生表现")
        evolution_df = get_evolution_chart()
        if evolution_df is not None:
            st.dataframe(evolution_df, use_container_width=True, hide_index=True)
            
            # 添加柱状图
            st.bar_chart(evolution_df.set_index('科室')[['诊断准确率', '治疗成功率']])
        else:
            st.info("暂无数据")
    
    with col2:
        st.subheader("治疗时间线")
        timeline_df = get_treatment_timeline()
        if timeline_df is not None:
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无治疗记录")
