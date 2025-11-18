"""
治疗流程可视化组件
"""
import streamlit as st
from datetime import datetime
import time


def treat_single_patient_with_visualization(patient, hospital):
    """单个病人治疗流程，带实时可视化"""
    # 创建实时进度显示容器
    progress_container = st.container()
    
    with progress_container:
        st.markdown(f"**🏥 正在治疗**: {patient.name} | **疾病**: {patient.disease}")
    
    # 创建流程步骤的占位符
    step1 = st.empty()
    step2 = st.empty()
    step3 = st.empty()
    step4 = st.empty()
    step5 = st.empty()
    step6 = st.empty()
    step7 = st.empty()
    step8 = st.empty()
    
    treatment_record = {
        'patient_id': patient.patient_id,
        'patient_name': patient.name,
        'ground_truth_disease': patient.disease,
        'events': []
    }
    
    try:
        # 步骤1: 病例输入
        with step1.container():
            st.text("🔵 步骤1: 病例输入...")
        time.sleep(0.2)
        
        step1_info = {
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'symptoms': ', '.join(patient.symptoms[:5])
        }
        
        with step1.container():
            st.text("✅ 步骤1: 病例输入")
        
        # 步骤2: 分诊
        with step2.container():
            st.text("🔵 步骤2: 智能分诊...")
        
        triage_result = hospital.triage_nurse.triage(patient)
        treatment_record['triage'] = triage_result
        recommended_dept = triage_result['recommended_departments'][0]
        
        with step2.container():
            st.text(f"✅ 步骤2: 智能分诊 → {recommended_dept}")
        
        # 步骤3: 挂号
        with step3.container():
            st.text("✅ 步骤3: 挂号登记")
        
        step3_info = recommended_dept
        
        # 获取医生
        if recommended_dept not in hospital.doctor_agents:
            recommended_dept = list(hospital.doctor_agents.keys())[0]
        doctor = hospital.doctor_agents[recommended_dept]
        
        # 步骤4: 问诊
        with step4.container():
            st.text("🔵 步骤4: 医生问诊...")
        
        examination_types = hospital._determine_examinations(patient, doctor)
        
        with step4.container():
            st.text(f"✅ 步骤4: 医生问诊 → {doctor.name}")
        
        # 步骤5: 医学检查
        with step5.container():
            st.text("🔵 步骤5: 医学检查...")
        
        examination_results = {}
        for exam_type in examination_types:
            exam_result = hospital.examination_nurse.conduct_examination(patient, exam_type)
            examination_results[exam_type] = exam_result
        treatment_record['examinations'] = examination_results
        
        with step5.container():
            st.text(f"✅ 步骤5: 医学检查 → {len(examination_results)}项")
        
        # 步骤6: AI诊断
        with step6.container():
            st.text("🔵 步骤6: AI智能诊断...")
        
        diagnosis_result = doctor.diagnose_with_evolution(patient, examination_results)
        treatment_record['diagnosis'] = diagnosis_result
        diagnosed_disease = diagnosis_result.get('disease', '未知')
        
        with step6.container():
            st.text(f"✅ 步骤6: AI智能诊断 → {diagnosed_disease}")
        
        patient.receive_diagnosis(diagnosis_result)
        
        # 步骤7: 治疗方案
        with step7.container():
            st.text("🔵 步骤7: 制定治疗方案...")
        
        treatment_plan = diagnosis_result.get('treatment_plan', {})
        patient.receive_treatment(treatment_plan)
        
        with step7.container():
            st.text("✅ 步骤7: 制定治疗方案")
        
        # 步骤8: 康复评估
        with step8.container():
            st.text("🔵 步骤8: 康复评估...")
        
        treatment_outcome = patient.evaluate_treatment_outcome()
        treatment_record['outcome'] = treatment_outcome
        
        with step8.container():
            if treatment_outcome['is_recovered']:
                st.text("✅ 步骤8: 康复评估 → 治疗成功")
            else:
                st.text("⚠️ 步骤8: 康复评估 → 需要复诊")
        
        # 医生学习
        doctor.learn_from_treatment_outcome(patient, diagnosis_result, treatment_outcome)
        
        # 更新统计
        hospital._update_stats(recommended_dept, treatment_outcome['is_recovered'])
        
        # 清空实时进度显示
        time.sleep(0.3)
        progress_container.empty()
        step1.empty()
        step2.empty()
        step3.empty()
        step4.empty()
        step5.empty()
        step6.empty()
        step7.empty()
        step8.empty()
        
        # 构建治疗结果记录
        is_diagnosis_correct = treatment_outcome['is_diagnosis_correct']
        is_recovered = treatment_outcome['is_recovered']
        
        diagnosis_status = "✅ 诊断正确" if is_diagnosis_correct else "❌ 诊断错误"
        treatment_status = "✅ 治疗成功" if is_recovered else "⚠️ 治疗失败"
        
        # 生成治疗记录HTML
        timestamp = datetime.now().strftime("%H:%M:%S")
        record_html = f"""
<details>
<summary style="cursor: pointer; padding: 8px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 5px;">
    <strong>👤 {patient.name}</strong> | 疾病: {patient.disease} | {diagnosis_status} | {treatment_status} | ⏰ {timestamp}
</summary>
<div style="padding: 10px; margin-left: 20px; border-left: 2px solid #ddd;">
"""
        
        # 添加每个步骤的详情（折叠）
        record_html += f"""
<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤1: 病例输入</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>姓名</strong>: {step1_info['name']}</p>
    <p><strong>年龄</strong>: {step1_info['age']}岁</p>
    <p><strong>性别</strong>: {step1_info['gender']}</p>
    <p><strong>症状</strong>: {step1_info['symptoms']}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤2: 智能分诊</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>推荐科室</strong>: {recommended_dept}</p>
    <p><strong>理由</strong>: {triage_result.get('reasoning', '基于症状分析')}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤3: 挂号登记</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p>已挂号至 <strong>{step3_info}</strong></p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤4: 医生问诊</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>主治医生</strong>: {doctor.name} ({recommended_dept})</p>
    <p><strong>需要检查</strong>: {', '.join(examination_types)}</p>
</div>
</details>

<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤5: 医学检查</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""
        for exam_type, result in examination_results.items():
            record_html += f"<p><strong>{exam_type}</strong>: {result.get('result', '正常')}</p>\n"
        record_html += "</div>\n</details>\n\n"
        
        record_html += f"""
<details style="margin: 5px 0;">
<summary style="cursor: pointer;">✅ 步骤6: AI智能诊断</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
    <p><strong>诊断结果</strong>: {diagnosed_disease}</p>
    <p><strong>置信度</strong>: {diagnosis_result.get('confidence', 'unknown')}</p>
"""
        reasoning = diagnosis_result.get('reasoning', '')
        if reasoning:
            record_html += f"<p><strong>诊断依据</strong>: {reasoning[:200]}...</p>\n"
        record_html += "</div>\n</details>\n\n"
        
        medications = treatment_plan.get('medications', [])
        recommendations = treatment_plan.get('recommendations', '')
        record_html += f"""
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
        record_html += "</div>\n</details>\n\n"
        
        outcome_icon = "✅" if is_recovered else "⚠️"
        record_html += f"""
<details style="margin: 5px 0;">
<summary style="cursor: pointer;">{outcome_icon} 步骤8: 康复评估</summary>
<div style="margin-left: 15px; font-size: 0.9em;">
"""
        if is_recovered:
            record_html += "<p>🎉 <strong>治疗成功！病人已康复</strong></p>\n"
            if is_diagnosis_correct:
                record_html += "<p>✅ 诊断正确</p>\n"
            else:
                record_html += f"<p>⚠️ 诊断有误</p>\n<p>错误诊断: {diagnosed_disease}</p>\n<p>正确诊断: {patient.disease}</p>\n"
        else:
            record_html += "<p>⚠️ 治疗效果不佳，建议复诊</p>\n"
            if is_diagnosis_correct:
                record_html += "<p>诊断正确，但需要调整治疗方案</p>\n"
            else:
                record_html += f"<p>❌ 诊断错误</p>\n<p>错误诊断: {diagnosed_disease}</p>\n<p>正确诊断: {patient.disease}</p>\n"
        record_html += "</div>\n</details>\n"
        
        record_html += "</div>\n</details>\n"
        
        # 将记录添加到session_state（添加到列表开头，最新的在最上面）
        if 'completed_treatments_display' not in st.session_state:
            st.session_state.completed_treatments_display = []
        st.session_state.completed_treatments_display.insert(0, record_html)
        
        treatment_record['success'] = True
        return treatment_record
        
    except Exception as e:
        import traceback
        st.error(f"治疗过程出错: {str(e)}")
        st.code(traceback.format_exc())
        treatment_record['success'] = False
        treatment_record['error'] = str(e)
        return treatment_record


def generate_and_treat_patient(num_patients, department_filter):
    """生成病人并进行治疗"""
    hospital = st.session_state.hospital
    patient_gen = st.session_state.patient_gen
    
    if hospital is None:
        return "⚠️ 请先初始化系统"
    
    try:
        # 生成病人
        if department_filter and department_filter != "全部":
            # 根据科室生成
            dept_keywords = {
                "心脏科": ['胸痛', '心悸', '心脏'],
                "神经科": ['头痛', '头晕', '神经'],
                "肿瘤科": ['肿块', '肿瘤', '癌'],
                "呼吸科": ['咳嗽', '呼吸', '肺'],
                "消化科": ['腹痛', '消化', '胃']
            }.get(department_filter, ['症状'])
            
            patients = patient_gen.generate_patients_by_department(
                dept_keywords, 
                num_patients
            )
        else:
            patients = patient_gen.generate_batch_patients(num_patients)
        
        # 逐个治疗病人，带可视化
        for i, patient in enumerate(patients, 1):
            # 使用可视化治疗
            record = treat_single_patient_with_visualization(patient, hospital)
            
            # 记录到历史
            treatment_record = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'patient': patient.name,
                'disease': patient.disease,
                'department': record.get('triage', {}).get('recommended_departments', ['未知'])[0],
                'success': record.get('outcome', {}).get('is_recovered', False),
                'diagnosis_correct': record.get('outcome', {}).get('is_diagnosis_correct', False)
            }
            st.session_state.treatment_history.append(treatment_record)
            
            # 更新历史统计
            st.session_state.all_time_stats['total_patients'] += 1
            if treatment_record['success']:
                st.session_state.all_time_stats['successful_treatments'] += 1
            else:
                st.session_state.all_time_stats['failed_treatments'] += 1
            if treatment_record['diagnosis_correct']:
                st.session_state.all_time_stats['diagnosis_correct'] += 1
            else:
                st.session_state.all_time_stats['diagnosis_incorrect'] += 1
        
        st.success(f"\n✅ 批量治疗完成！共治疗 {len(patients)} 位病人")
        return "completed"
    
    except Exception as e:
        import traceback
        return f"❌ 治疗过程出错：{str(e)}\n{traceback.format_exc()}"
