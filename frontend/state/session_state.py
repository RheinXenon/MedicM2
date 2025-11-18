"""
Session State 初始化和管理
"""
import streamlit as st


def init_session_state():
    """初始化所有 session state 变量"""
    if 'hospital' not in st.session_state:
        st.session_state.hospital = None
    if 'patient_gen' not in st.session_state:
        st.session_state.patient_gen = None
    if 'treatment_history' not in st.session_state:
        st.session_state.treatment_history = []
    if 'all_time_stats' not in st.session_state:
        # 历史统计数据（持久化）
        st.session_state.all_time_stats = {
            'total_patients': 0,
            'successful_treatments': 0,
            'failed_treatments': 0,
            'diagnosis_correct': 0,
            'diagnosis_incorrect': 0
        }
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'current_treatment' not in st.session_state:
        st.session_state.current_treatment = None
    if 'treatment_steps' not in st.session_state:
        st.session_state.treatment_steps = []
