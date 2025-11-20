"""
治疗流程页面
"""
import streamlit as st
from ..components.treatment_flow import generate_and_treat_patient


def render_records_content_only(container_placeholder=None):
    """只渲染记录内容，不渲染翻页按钮（用于占位符动态更新）
    
    Args:
        container_placeholder: 占位符
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


def render_pagination_controls():
    """渲染翻页控件（独立函数，不在占位符内）"""
    records_manager = st.session_state.get('records_manager')
    if not records_manager:
        return
    
    total_records = records_manager.get_total_count()
    if total_records == 0:
        return
    
    records_per_page = st.session_state.get('records_per_page', 10)
    current_page = st.session_state.get('records_page', 0)
    total_pages = (total_records + records_per_page - 1) // records_per_page
    
    # 确保当前页码在有效范围内
    if current_page >= total_pages:
        current_page = total_pages - 1
        st.session_state.records_page = current_page
    if current_page < 0:
        current_page = 0
        st.session_state.records_page = current_page
    
    st.divider()
    
    # 翻页控制按钮
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
    
    with col1:
        if st.button("⬅️ 上一页", disabled=(current_page == 0), use_container_width=True, key="prev_page"):
            st.session_state.records_page = max(0, current_page - 1)
            st.rerun()
    
    with col2:
        st.markdown(f"""<div style='text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; border-radius: 8px; font-weight: bold;'>
            第 {current_page + 1} / {total_pages} 页
        </div>""", unsafe_allow_html=True)
    
    with col3:
        if st.button("下一页 ➡️", disabled=(current_page >= total_pages - 1), use_container_width=True, key="next_page"):
            st.session_state.records_page = min(total_pages - 1, current_page + 1)
            st.rerun()


def _build_record_html(record):
    """从JSON记录构建显示HTML - 显示所有详细信息"""
    # 基本信息
    patient_name = record.get('patient_name', '未知')
    patient_id = record.get('patient_id', '未知')
    disease = record.get('ground_truth_disease', '未知')
    timestamp = record.get('timestamp', '未知时间')

    outcome = record.get('outcome', {})
    is_diagnosis_correct = outcome.get('is_diagnosis_correct', False)
    is_recovered = outcome.get('is_recovered', False)

    diagnosis_status = "✅ 诊断正确" if is_diagnosis_correct else "❌ 诊断错误"
    treatment_status = "✅ 治疗成功" if is_recovered else "⚠️ 治疗失败"

    # 获取详细信息
    triage = record.get('triage', {})
    recommended_depts = triage.get('recommended_departments', ['未知'])
    recommended_dept = recommended_depts[0] if recommended_depts else '未知'
    triage_reasoning = triage.get('reasoning', '基于症状分析')
    triage_severity = triage.get('severity', '未知')

    diagnosis = record.get('diagnosis', {})
    diagnosed_disease = diagnosis.get('disease', '未知')
    confidence = diagnosis.get('confidence', 'unknown')
    reasoning = diagnosis.get('reasoning', '')
    differential_diagnosis = diagnosis.get('differential_diagnosis', [])

    examinations = record.get('examinations', {})
    treatment_plan = diagnosis.get('treatment_plan', {})
    medications = treatment_plan.get('medications', [])
    recommendations = treatment_plan.get('recommendations', '')
    precautions = treatment_plan.get('precautions', [])
    follow_up = treatment_plan.get('follow_up', '')

    # 构建HTML
    record_html = f"""
<details>
<summary style="cursor: pointer; padding: 8px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 5px;">
    <strong>👤 {patient_name}</strong> | 疾病: {disease} | {diagnosis_status} | {treatment_status} | ⏰ {timestamp}
</summary>
<div style="padding: 10px; margin-left: 20px; border-left: 2px solid #ddd;">

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤1: 病例输入（完整信息）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>患者ID</strong>: {patient_id}</p>
    <p><strong>姓名</strong>: {patient_name}</p>
    <p><strong>真实疾病</strong>: {disease}</p>
"""

    # 优先从triage中提取患者信息（新数据）
    patient_age = None
    patient_gender = None
    patient_symptoms = []
    patient_history = []

    if 'patient_age' in triage:
        patient_age = triage['patient_age']
    if 'patient_gender' in triage:
        patient_gender = triage['patient_gender']
    if 'symptoms' in triage:
        patient_symptoms = triage['symptoms']
    if 'medical_history' in triage:
        patient_history = triage['medical_history']

    # 如果triage中没有，尝试从patient_profile中获取（兼容旧数据）
    if 'patient_profile' in record:
        profile = record['patient_profile']
        if not patient_age and 'age' in profile:
            patient_age = profile['age']
        if not patient_gender and 'gender' in profile:
            patient_gender = profile['gender']
        if not patient_symptoms and 'symptoms' in profile:
            patient_symptoms = profile['symptoms']
        if not patient_history and 'medical_history' in profile:
            patient_history = profile['medical_history']

    # 显示患者基本信息
    if patient_age:
        record_html += f"    <p><strong>年龄</strong>: {patient_age}岁</p>\n"
    if patient_gender:
        record_html += f"    <p><strong>性别</strong>: {patient_gender}</p>\n"

    # 显示完整的症状列表（分行显示，更清晰）
    if patient_symptoms:
        if isinstance(patient_symptoms, list) and patient_symptoms:
            record_html += f"    <p><strong>症状列表</strong>（共{len(patient_symptoms)}个）:</p>\n"
            record_html += "    <div style='background-color: #fff3cd; padding: 10px; margin: 5px 0; border-left: 3px solid #ffc107;'>\n"
            for i, symptom in enumerate(patient_symptoms, 1):
                record_html += f"        <p style='margin: 2px 0;'>{i}. {symptom}</p>\n"
            record_html += "    </div>\n"
        elif isinstance(patient_symptoms, str):
            record_html += f"    <p><strong>症状</strong>: {patient_symptoms}</p>\n"

    # 显示既往病史
    if patient_history:
        if isinstance(patient_history, list) and patient_history:
            record_html += f"    <p><strong>既往病史</strong>:</p>\n"
            record_html += "    <div style='background-color: #f0f8ff; padding: 10px; margin: 5px 0; border-left: 3px solid #007bff;'>\n"
            for h in patient_history:
                record_html += f"        <p style='margin: 2px 0;'>• {h}</p>\n"
            record_html += "    </div>\n"
        elif patient_history:
            record_html += f"    <p><strong>既往病史</strong>: {patient_history}</p>\n"
    else:
        record_html += "    <p><strong>既往病史</strong>: 无特殊病史</p>\n"

    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤2: 智能分诊（完整分析）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""

    # 显示患者主诉
    chief_complaint = triage.get('chief_complaint', '')
    if chief_complaint:
        record_html += "    <p><strong>患者主诉</strong>:</p>\n"
        record_html += f"    <div style='background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 3px solid #28a745; white-space: pre-wrap; word-wrap: break-word;'>{chief_complaint}</div>\n"

    # 显示推荐科室
    if len(recommended_depts) > 1:
        record_html += f"    <p><strong>推荐科室</strong>: {', '.join(recommended_depts)}</p>\n"
    else:
        record_html += f"    <p><strong>推荐科室</strong>: {recommended_dept}</p>\n"

    # 显示严重程度
    if triage_severity and triage_severity != '未知':
        record_html += f"    <p><strong>严重程度</strong>: {triage_severity}</p>\n"

    # 显示分诊理由（完整显示，不截断）
    if triage_reasoning:
        record_html += "    <p><strong>分诊理由</strong>:</p>\n"
        record_html += f"    <div style='background-color: #e7f3ff; padding: 10px; margin: 5px 0; white-space: pre-wrap; word-wrap: break-word;'>{triage_reasoning}</div>\n"

    # 显示建议
    triage_suggestions = triage.get('suggestions', '')
    if triage_suggestions:
        record_html += "    <p><strong>就诊建议</strong>:</p>\n"
        record_html += f"    <div style='background-color: #fff3cd; padding: 10px; margin: 5px 0; white-space: pre-wrap;'>{triage_suggestions}</div>\n"

    # 添加分诊的症状分析
    if 'symptom_analysis' in triage:
        record_html += f"    <p><strong>症状分析</strong>: {triage['symptom_analysis']}</p>\n"

    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤3: 挂号登记</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p>已挂号至 <strong>""" + recommended_dept + """</strong></p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤4: 医生问诊（需要检查项目）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""

    if examinations:
        record_html += f"    <p><strong>需要检查项目</strong>: {', '.join(examinations.keys())}</p>\n"
        record_html += f"    <p><strong>检查项目数量</strong>: {len(examinations)}项</p>\n"
    else:
        record_html += "    <p><strong>无需额外检查</strong></p>\n"

    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤5: 医学检查（完整结果）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""

    if examinations:
        for exam_type, exam_data in examinations.items():
            record_html += f"    <div style='background-color: #f9f9f9; padding: 8px; margin: 5px 0; border-left: 3px solid #4CAF50;'>\n"
            record_html += f"        <p><strong>🔬 {exam_type}</strong></p>\n"

            if isinstance(exam_data, dict):
                if 'result' in exam_data:
                    record_html += f"        <p><strong>结果</strong>: {exam_data['result']}</p>\n"
                if 'details' in exam_data:
                    record_html += f"        <p><strong>详情</strong>: {exam_data['details']}</p>\n"
                if 'abnormal_findings' in exam_data:
                    findings = exam_data['abnormal_findings']
                    if findings:
                        record_html += f"        <p><strong>异常发现</strong>: {findings}</p>\n"
                if 'interpretation' in exam_data:
                    record_html += f"        <p><strong>解读</strong>: {exam_data['interpretation']}</p>\n"
                # 显示所有其他键值
                for key, value in exam_data.items():
                    if key not in ['result', 'details', 'abnormal_findings', 'interpretation']:
                        record_html += f"        <p><strong>{key}</strong>: {value}</p>\n"
            else:
                record_html += f"        <p>{exam_data}</p>\n"

            record_html += "    </div>\n"
    else:
        record_html += "    <p>无检查记录</p>\n"

    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤6: 医生诊断（完整诊断依据）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>诊断结果</strong>: """ + diagnosed_disease + """</p>
    <p><strong>置信度</strong>: """ + str(confidence) + """</p>
"""

    # 显示完整的诊断依据（不截断）
    if reasoning:
        # 将长文本分段显示
        record_html += f"    <p><strong>诊断依据</strong>:</p>\n"
        record_html += f"    <div style='background-color: #f9f9f9; padding: 10px; margin: 5px 0; white-space: pre-wrap; word-wrap: break-word;'>{reasoning}</div>\n"

    # 显示鉴别诊断
    if differential_diagnosis:
        record_html += "    <p><strong>鉴别诊断</strong>:</p>\n"
        if isinstance(differential_diagnosis, list):
            for dd in differential_diagnosis:
                if isinstance(dd, dict):
                    dd_name = dd.get('disease', dd.get('name', '未知'))
                    dd_prob = dd.get('probability', dd.get('likelihood', ''))
                    record_html += f"    <p style='margin-left: 15px;'>• {dd_name}"
                    if dd_prob:
                        record_html += f" (可能性: {dd_prob})"
                    record_html += "</p>\n"
                else:
                    record_html += f"    <p style='margin-left: 15px;'>• {dd}</p>\n"
        else:
            record_html += f"    <p>{differential_diagnosis}</p>\n"

    # 显示诊断过程中的其他信息
    for key in ['analysis', 'clinical_findings', 'laboratory_findings']:
        if key in diagnosis and diagnosis[key]:
            record_html += f"    <p><strong>{key.replace('_', ' ').title()}</strong>: {diagnosis[key]}</p>\n"

    record_html += """</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤7: 治疗方案（完整方案）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""

    # 显示所有处方药物（不限制数量）
    if medications:
        record_html += "    <p><strong>处方药物</strong>:</p>\n"
        if isinstance(medications, list):
            for i, med in enumerate(medications, 1):
                if isinstance(med, dict):
                    med_name = med.get('name', med.get('medication', ''))
                    med_dosage = med.get('dosage', '')
                    med_frequency = med.get('frequency', '')
                    med_duration = med.get('duration', '')

                    record_html += f"    <p style='margin-left: 15px;'>{i}. <strong>{med_name}</strong>"
                    if med_dosage:
                        record_html += f" - 剂量: {med_dosage}"
                    if med_frequency:
                        record_html += f" - 频率: {med_frequency}"
                    if med_duration:
                        record_html += f" - 疗程: {med_duration}"
                    record_html += "</p>\n"
                else:
                    record_html += f"    <p style='margin-left: 15px;'>{i}. {med}</p>\n"
        else:
            record_html += f"    <p>{medications}</p>\n"

    # 显示完整的医嘱
    if recommendations:
        record_html += "    <p><strong>医嘱建议</strong>:</p>\n"
        if isinstance(recommendations, list):
            for rec in recommendations:
                record_html += f"    <p style='margin-left: 15px;'>• {rec}</p>\n"
        else:
            record_html += f"    <div style='background-color: #f9f9f9; padding: 10px; margin: 5px 0; white-space: pre-wrap;'>{recommendations}</div>\n"

    # 显示注意事项
    if precautions:
        record_html += "    <p><strong>注意事项</strong>:</p>\n"
        if isinstance(precautions, list):
            for prec in precautions:
                record_html += f"    <p style='margin-left: 15px;'>• {prec}</p>\n"
        else:
            record_html += f"    <p>{precautions}</p>\n"

    # 显示随访计划
    if follow_up:
        record_html += f"    <p><strong>随访计划</strong>: {follow_up}</p>\n"

    # 显示治疗方案中的其他信息
    for key in ['therapy', 'lifestyle_changes', 'diet_recommendations']:
        if key in treatment_plan and treatment_plan[key]:
            record_html += f"    <p><strong>{key.replace('_', ' ').title()}</strong>: {treatment_plan[key]}</p>\n"

    outcome_icon = "✅" if is_recovered else "⚠️"
    record_html += f"""</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">{outcome_icon} 步骤8: 康复评估（详细结果）</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""

    if is_recovered:
        record_html += "    <p>🎉 <strong>治疗成功！病人已康复</strong></p>\n"
        if is_diagnosis_correct:
            record_html += "    <p>✅ 诊断正确</p>\n"
        else:
            record_html += f"    <p>⚠️ 诊断有误</p>\n"
            record_html += f"    <p><strong>错误诊断</strong>: {diagnosed_disease}</p>\n"
            record_html += f"    <p><strong>正确诊断</strong>: {disease}</p>\n"
    else:
        record_html += "    <p>⚠️ 治疗效果不佳，建议复诊</p>\n"
        if is_diagnosis_correct:
            record_html += "    <p>✅ 诊断正确，但需要调整治疗方案</p>\n"
        else:
            record_html += f"    <p>❌ 诊断错误</p>\n"
            record_html += f"    <p><strong>错误诊断</strong>: {diagnosed_disease}</p>\n"
            record_html += f"    <p><strong>正确诊断</strong>: {disease}</p>\n"

    # 显示康复评估的详细信息
    if 'recovery_details' in outcome:
        record_html += f"    <p><strong>康复详情</strong>: {outcome['recovery_details']}</p>\n"
    if 'satisfaction' in outcome:
        record_html += f"    <p><strong>患者满意度</strong>: {outcome['satisfaction']}</p>\n"
    if 'side_effects' in outcome:
        effects = outcome['side_effects']
        if effects:
            record_html += f"    <p><strong>副作用</strong>: {effects}</p>\n"

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
    
    # 创建已完成记录的占位符，用于动态更新（只包含记录内容）
    completed_records_placeholder = st.empty()
    
    # 【关键】先渲染一次历史记录内容，确保占位符始终有内容
    render_records_content_only(completed_records_placeholder)
    
    # 翻页控件放在占位符外部（固定位置，避免重复渲染）
    render_pagination_controls()
    
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
