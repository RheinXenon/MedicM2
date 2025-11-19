"""
治疗流程可视化组件
"""
import streamlit as st
from datetime import datetime
import time


def treat_single_patient_with_visualization(patient, hospital, real_time_placeholder):
    """单个病人治疗流程，带实时可视化"""
    # 使用传入的占位符创建实时进度显示容器
    with real_time_placeholder.container():
        st.markdown(f"**🏥 正在治疗**: {patient.name} | **疾病**: {patient.disease}")
        
        # 创建流程步骤的占位符（在容器内部）
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
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
            st.text("🔵 步骤6: 医生诊断...")
        
        diagnosis_result = doctor.diagnose_with_evolution(patient, examination_results)
        treatment_record['diagnosis'] = diagnosis_result
        diagnosed_disease = diagnosis_result.get('disease', '未知')
        
        with step6.container():
            st.text(f"✅ 步骤6: 医生诊断 → {diagnosed_disease}")
        
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
        
        # 清空实时进度显示（通过清空占位符）
        time.sleep(0.3)
        real_time_placeholder.empty()
        
        treatment_record['success'] = True
        
        # 保存记录到JSON文件
        if 'records_manager' in st.session_state:
            st.session_state.records_manager.save_record(treatment_record)
        
        return treatment_record
        
    except Exception as e:
        import traceback
        st.error(f"治疗过程出错: {str(e)}")
        st.code(traceback.format_exc())
        treatment_record['success'] = False
        treatment_record['error'] = str(e)
        return treatment_record


def generate_and_treat_patient(num_patients, department_filter, real_time_placeholder, completed_records_placeholder):
    """生成病人并进行治疗（支持暂停/继续/终止）
    
    Args:
        num_patients: 病人数量
        department_filter: 科室筛选
        real_time_placeholder: 实时进度占位符
        completed_records_placeholder: 已完成记录占位符，用于动态更新
    """
    hospital = st.session_state.hospital
    patient_gen = st.session_state.patient_gen
    
    if hospital is None:
        return "⚠️ 请先初始化系统"
    
    try:
        # 如果是开始新的治疗，生成病人列表
        if st.session_state.treatment_control == 'start':
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
            
            # 保存病人列表和初始化索引
            st.session_state.patients_to_treat = patients
            st.session_state.current_patient_index = 0
            st.session_state.total_patients_to_treat = len(patients)
        
        # 如果是继续治疗，使用已保存的病人列表
        elif st.session_state.treatment_control == 'resume':
            patients = st.session_state.patients_to_treat
        else:
            return "completed"
        
        # 逐个治疗病人，带可视化
        start_index = st.session_state.current_patient_index
        for i in range(start_index, len(patients)):
            # 检查控制信号
            if st.session_state.treatment_control == 'pause':
                st.session_state.current_patient_index = i
                with real_time_placeholder.container():
                    st.warning(f"⏸️ 治疗已暂停，当前进度：{i}/{len(patients)}")
                return "paused"
            
            if st.session_state.treatment_control == 'stop':
                st.session_state.current_patient_index = 0
                st.session_state.patients_to_treat = []
                with real_time_placeholder.container():
                    st.error(f"⏹️ 治疗已终止，已完成：{i}/{len(patients)}")
                return "stopped"
            
            patient = patients[i]
            
            # 使用可视化治疗，传递实时进度占位符
            record = treat_single_patient_with_visualization(patient, hospital, real_time_placeholder)
            
            # 立即更新已完成记录显示（动态更新）
            if completed_records_placeholder:
                from ..views.treatment_page import render_completed_records_with_pagination
                render_completed_records_with_pagination(completed_records_placeholder)
            
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
            
            # 更新当前索引
            st.session_state.current_patient_index = i + 1
        
        # 治疗完成，清空病人列表
        st.session_state.patients_to_treat = []
        st.session_state.current_patient_index = 0
        st.success(f"\n✅ 批量治疗完成！共治疗 {len(patients)} 位病人")
        return "completed"
    
    except Exception as e:
        import traceback
        return f"❌ 治疗过程出错：{str(e)}\n{traceback.format_exc()}"
