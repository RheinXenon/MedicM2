"""
治疗流程页面
"""
import streamlit as st
from ..components.treatment_flow import generate_and_treat_patient


def render_completed_records_with_pagination(container_placeholder=None):
    """渲染已完成的治疗记录（带分页）
    
    Args:
        container_placeholder: 可选的占位符，用于动态更新显示
    """
    # 获取记录管理器
    records_manager = st.session_state.get('records_manager')
    
    # 如果有占位符，使用占位符容器，否则直接渲染
    if container_placeholder:
        ctx = container_placeholder.container()
    else:
        ctx = st.container()
    
    with ctx:
        if not records_manager:
            st.info("暂无完成的治疗记录")
            return
        
        # 获取总记录数
        total_records = records_manager.get_total_count()
        
        if total_records == 0:
            st.info("暂无完成的治疗记录")
            return
        
        # 获取分页参数
        records_per_page = st.session_state.get('records_per_page', 10)
        current_page = st.session_state.get('records_page', 0)
        
        # 计算总页数
        total_pages = (total_records + records_per_page - 1) // records_per_page
        
        # 确保当前页码在有效范围内
        if current_page >= total_pages:
            current_page = total_pages - 1
            st.session_state.records_page = current_page
        if current_page < 0:
            current_page = 0
            st.session_state.records_page = current_page
        
        # 获取当前页的记录
        offset = current_page * records_per_page
        page_records = records_manager.get_records(limit=records_per_page, offset=offset)
        
        # 显示记录总数信息
        st.markdown(f"""<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
            <strong>📊 记录统计：</strong>共 {total_records} 条记录 | 当前显示第 {current_page + 1} 页（共 {total_pages} 页）
        </div>""", unsafe_allow_html=True)
        
        # 显示当前页的记录
        for record in page_records:
            # 从JSON记录构建显示HTML
            record_html = _build_record_html(record)
            st.markdown(record_html, unsafe_allow_html=True)
        
        st.divider()
        
        # 翻页控制按钮（移到底部，优化UI）
        st.markdown("""<style>
            div.stButton > button {
                width: 100%;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
            }
            div.stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        </style>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        # 使用动态key避免在占位符模式下的key冲突
        key_suffix = "_placeholder" if container_placeholder else ""
        
        with col1:
            if st.button("⬅️ 上一页", disabled=(current_page == 0), use_container_width=True, key=f"prev_page{key_suffix}"):
                st.session_state.records_page = max(0, current_page - 1)
                st.rerun()
        
        with col2:
            st.markdown(f"""<div style='text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 8px; font-weight: bold;'>
                第 {current_page + 1} / {total_pages} 页
            </div>""", unsafe_allow_html=True)
        
        with col3:
            if st.button("下一页 ➡️", disabled=(current_page >= total_pages - 1), use_container_width=True, key=f"next_page{key_suffix}"):
                st.session_state.records_page = min(total_pages - 1, current_page + 1)
                st.rerun()


def _build_record_html(record):
    """从JSON记录构建显示HTML"""
    patient_name = record.get('patient_name', '未知')
    disease = record.get('ground_truth_disease', '未知')
    timestamp = record.get('timestamp', '未知时间')
    
    outcome = record.get('outcome', {})
    is_diagnosis_correct = outcome.get('is_diagnosis_correct', False)
    is_recovered = outcome.get('is_recovered', False)
    
    diagnosis_status = "✅ 诊断正确" if is_diagnosis_correct else "❌ 诊断错误"
    treatment_status = "✅ 治疗成功" if is_recovered else "⚠️ 治疗失败"
    
    # 获取详细信息
    triage = record.get('triage', {})
    recommended_dept = triage.get('recommended_departments', ['未知'])[0] if triage.get('recommended_departments') else '未知'
    
    diagnosis = record.get('diagnosis', {})
    diagnosed_disease = diagnosis.get('disease', '未知')
    confidence = diagnosis.get('confidence', 'unknown')
    reasoning = diagnosis.get('reasoning', '')
    
    examinations = record.get('examinations', {})
    treatment_plan = diagnosis.get('treatment_plan', {})
    medications = treatment_plan.get('medications', [])
    recommendations = treatment_plan.get('recommendations', '')
    
    # 构建HTML
    record_html = f"""
<details>
<summary style="cursor: pointer; padding: 8px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 5px;">
    <strong>👤 {patient_name}</strong> | 疾病: {disease} | {diagnosis_status} | {treatment_status} | ⏰ {timestamp}
</summary>
<div style="padding: 10px; margin-left: 20px; border-left: 2px solid #ddd;">

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤1: 病例输入</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>姓名</strong>: {patient_name}</p>
    <p><strong>疾病</strong>: {disease}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤2: 智能分诊</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>推荐科室</strong>: {recommended_dept}</p>
    <p><strong>理由</strong>: {triage.get('reasoning', '基于症状分析')}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤3: 挂号登记</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p>已挂号至 <strong>{recommended_dept}</strong></p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤4: 医生问诊</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>需要检查</strong>: {', '.join(examinations.keys()) if examinations else '无'}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤5: 医学检查</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""
    
    for exam_type, result in examinations.items():
        record_html += f"<p><strong>{exam_type}</strong>: {result.get('result', '正常')}</p>\n"
    
    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤6: 医生诊断</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>诊断结果</strong>: """ + diagnosed_disease + """</p>
    <p><strong>置信度</strong>: """ + str(confidence) + """</p>
"""
    
    if reasoning:
        record_html += f"<p><strong>诊断依据</strong>: {reasoning[:200]}...</p>\n"
    
    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤7: 治疗方案</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""
    
    if medications:
        record_html += f"<p><strong>处方药物</strong>: {', '.join(medications[:5])}</p>\n"
    if recommendations:
        if isinstance(recommendations, str):
            record_html += f"<p><strong>医嘱</strong>: {recommendations}</p>\n"
        elif isinstance(recommendations, list):
            record_html += f"<p><strong>医嘱</strong>: {', '.join(recommendations[:3])}</p>\n"
    
    outcome_icon = "✅" if is_recovered else "⚠️"
    record_html += f"""</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">{outcome_icon} 步骤8: 康复评估</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""
    
    if is_recovered:
        record_html += "<p>🎉 <strong>治疗成功！病人已康复</strong></p>\n"
        if is_diagnosis_correct:
            record_html += "<p>✅ 诊断正确</p>\n"
        else:
            record_html += f"<p>⚠️ 诊断有误</p>\n<p>错误诊断: {diagnosed_disease}</p>\n<p>正确诊断: {disease}</p>\n"
    else:
        record_html += "<p>⚠️ 治疗效果不佳，建议复诊</p>\n"
        if is_diagnosis_correct:
            record_html += "<p>诊断正确，但需要调整治疗方案</p>\n"
        else:
            record_html += f"<p>❌ 诊断错误</p>\n<p>错误诊断: {diagnosed_disease}</p>\n<p>正确诊断: {disease}</p>\n"
    
    record_html += """</div>
</details>

</div>
</details>
"""
    
    return record_html


def render_treatment_page():
    """渲染治疗流程页面"""
    # 实时治疗进度标题和占位符
    st.markdown("### 🎯 实时治疗流程")
    real_time_placeholder = st.empty()
    
    st.divider()
    
    # 下半部分：已完成的治疗记录
    st.markdown("### 📋 已完成的治疗记录")
    
    # 创建已完成记录的占位符，用于动态更新
    completed_records_placeholder = st.empty()
    
    # 【关键】先渲染一次历史记录，确保占位符始终有内容
    render_completed_records_with_pagination(completed_records_placeholder)
    
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
        
        # 调用治疗函数，传递占位符以实现动态更新
        result = generate_and_treat_patient(
            num_patients, 
            department_filter,
            real_time_placeholder,
            completed_records_placeholder
        )
        
        # 治疗完成后重置状态并刷新页面
        if result == "completed":
            st.session_state.treatment_status = 'idle'
            st.session_state.treatment_control = None
            st.rerun()
        elif result == "stopped":
            st.session_state.treatment_status = 'idle'
            st.session_state.treatment_control = None
            st.rerun()
    else:
        # 显示提示信息
        with real_time_placeholder.container():
            if treatment_status == 'idle':
                st.info("👉 请在侧边栏设置病人数量和科室，然后点击'开始'按钮启动治疗流程")
            elif treatment_status == 'paused':
                st.warning("⏸️ 治疗已暂停，点击'继续'按钮恢复治疗")
            elif treatment_status == 'stopped':
                st.error("⏹️ 治疗已终止")
