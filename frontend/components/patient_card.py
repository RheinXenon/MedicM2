"""
患者卡片组件
展示单个患者的治疗流程，包含横向进度条和详情展开
"""
import streamlit as st
import streamlit.components.v1 as components
from frontend.components.progress_bar import (
    render_progress_bar,
    render_step_details,
    get_step_status_from_record,
    TREATMENT_STEPS
)


def render_patient_card(patient_index, treatment_record, unique_key):
    """
    渲染患者卡片
    
    Args:
        patient_index: 患者索引（用于显示）
        treatment_record: 治疗记录字典
        unique_key: 唯一键值，用于区分不同的卡片
    """
    # 获取步骤状态
    steps_status = get_step_status_from_record(treatment_record)
    
    # 获取患者信息
    patient_info = treatment_record.get('patient_info', {})
    patient_name = patient_info.get('name', '未知患者')
    
    # 获取治疗结果
    outcome = treatment_record.get('outcome', {})
    is_recovered = outcome.get('is_recovered', False)
    is_diagnosis_correct = outcome.get('is_diagnosis_correct', False)
    
    # 确定结果样式
    if is_recovered:
        result_class = 'result-success'
        result_text = '✅ 治疗成功'
    else:
        result_class = 'result-failed'
        result_text = '❌ 需要复诊'
    
    diagnosis_text = '✅ 诊断正确' if is_diagnosis_correct else '❌ 诊断错误'
    
    # 卡片HTML
    card_html = f'<div class="patient-card">'
    
    # 患者头部信息
    card_html += '<div class="patient-header">'
    card_html += f'<div class="patient-name">👤 {patient_name}</div>'
    card_html += '<div class="patient-result">'
    card_html += f'<span class="{result_class}">{result_text}</span>'
    card_html += f' | {diagnosis_text}'
    card_html += '</div>'
    card_html += '</div>'
    
    # 渲染进度条
    card_html += render_progress_bar(steps_status)
    
    card_html += '</div>'
    
    # 渲染卡片
    components.html(card_html, height=220, scrolling=False)
    
    # 使用expander来展示详情
    with st.expander("🔍 查看详细流程", expanded=False):
        # 创建步骤选择器
        selected_step = st.selectbox(
            "选择步骤查看详情",
            range(len(TREATMENT_STEPS)),
            format_func=lambda x: f"{x+1}. {TREATMENT_STEPS[x]}",
            key=f"step_selector_{unique_key}"
        )
        
        # 显示选中步骤的详情
        step_data = steps_status[selected_step]['data']
        detail_html = render_step_details(selected_step, step_data)
        components.html(detail_html, height=300, scrolling=True)


def render_realtime_patient_card(patient, current_step_index, steps_data):
    """
    渲染实时治疗的患者卡片（用于治疗过程中的实时显示）
    
    Args:
        patient: 患者对象
        current_step_index: 当前步骤索引
        steps_data: 步骤数据列表
    """
    patient_name = patient.name
    
    # 构建步骤状态
    steps_status = []
    for i in range(8):
        if i < current_step_index:
            status = 'completed'
        elif i == current_step_index:
            status = 'running'
        else:
            status = 'pending'
        
        data = steps_data[i] if i < len(steps_data) else {}
        steps_status.append({
            'status': status,
            'data': data
        })
    
    # 卡片HTML
    card_html = f'<div class="patient-card">'
    
    # 患者头部信息
    card_html += '<div class="patient-header">'
    card_html += f'<div class="patient-name">👤 {patient_name}</div>'
    card_html += '<div class="patient-result">'
    card_html += f'<span style="color: #4facfe;">🔄 治疗进行中...</span>'
    card_html += '</div>'
    card_html += '</div>'
    
    # 渲染进度条
    card_html += render_progress_bar(steps_status)
    
    card_html += '</div>'
    
    # 渲染卡片
    components.html(card_html, height=220, scrolling=False)
    
    # 显示当前步骤详情
    if current_step_index >= 0 and current_step_index < len(steps_data):
        step_data = steps_data[current_step_index]
        detail_html = render_step_details(current_step_index, step_data)
        components.html(detail_html, height=300, scrolling=True)
