"""
治疗流程可视化组件
"""
import streamlit as st
from datetime import datetime
import time


def treat_single_patient_with_visualization(patient, hospital):
    """单个病人治疗流程，带实时可视化"""
    # 创建治疗流程容器
    st.subheader(f"🏥 正在治疗: {patient.name}")
    st.markdown(f"**真实疾病**: {patient.disease}")
    st.divider()
    
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
        # 步骤1: 疾病发作
        with step1.container():
            st.markdown("🔵 **步骤1: 病例输入** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write(f"**病人姓名**: {patient.name}")
                st.write(f"**年龄**: {patient.age}岁")
                st.write(f"**性别**: {patient.gender}")
                st.write(f"**主诉症状**: {', '.join(patient.symptoms[:5])}")
        time.sleep(0.5)
        
        with step1.container():
            st.markdown("✅ **步骤1: 病例输入** - 已完成")
            with st.expander("查看详情"):
                st.write(f"**病人姓名**: {patient.name}")
                st.write(f"**年龄**: {patient.age}岁")
                st.write(f"**性别**: {patient.gender}")
                st.write(f"**主诉症状**: {', '.join(patient.symptoms[:5])}")
        
        # 步骤2: 分诊
        with step2.container():
            st.markdown("🔵 **步骤2: 智能分诊** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write("护士正在分析症状...")
        
        triage_result = hospital.triage_nurse.triage(patient)
        treatment_record['triage'] = triage_result
        recommended_dept = triage_result['recommended_departments'][0]
        
        with step2.container():
            st.markdown("✅ **步骤2: 智能分诊** - 已完成")
            with st.expander("查看详情"):
                st.success(f"**推荐科室**: {recommended_dept}")
                st.write(f"**分诊理由**: {triage_result.get('reasoning', '基于症状分析')}")
        
        # 步骤3: 挂号
        with step3.container():
            st.markdown("✅ **步骤3: 挂号登记** - 已完成")
            with st.expander("查看详情"):
                st.write(f"已挂号至 **{recommended_dept}**")
        
        # 获取医生
        if recommended_dept not in hospital.doctor_agents:
            recommended_dept = list(hospital.doctor_agents.keys())[0]
        doctor = hospital.doctor_agents[recommended_dept]
        
        # 步骤4: 问诊
        with step4.container():
            st.markdown("🔵 **步骤4: 医生问诊** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write(f"**主治医生**: {doctor.name} ({recommended_dept})")
                st.write("医生正在询问病史和症状...")
        
        examination_types = hospital._determine_examinations(patient, doctor)
        
        with step4.container():
            st.markdown("✅ **步骤4: 医生问诊** - 已完成")
            with st.expander("查看详情"):
                st.write(f"**主治医生**: {doctor.name} ({recommended_dept})")
                st.write(f"**需要检查**: {', '.join(examination_types)}")
        
        # 步骤5: 医学检查
        with step5.container():
            st.markdown("🔵 **步骤5: 医学检查** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write("正在进行各项检查...")
        
        examination_results = {}
        for exam_type in examination_types:
            exam_result = hospital.examination_nurse.conduct_examination(patient, exam_type)
            examination_results[exam_type] = exam_result
        
        treatment_record['examinations'] = examination_results
        
        with step5.container():
            st.markdown("✅ **步骤5: 医学检查** - 已完成")
            with st.expander("查看详情"):
                for exam_type, result in examination_results.items():
                    st.write(f"**{exam_type}**: {result.get('result', '正常')}")
        
        # 步骤6: AI诊断
        with step6.container():
            st.markdown("🔵 **步骤6: AI智能诊断** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write("大模型正在分析病情...")
                st.write("检索相似病例...")
                st.write("应用临床经验...")
        
        diagnosis_result = doctor.diagnose_with_evolution(patient, examination_results)
        treatment_record['diagnosis'] = diagnosis_result
        
        with step6.container():
            st.markdown("✅ **步骤6: AI智能诊断** - 已完成")
            with st.expander("查看详情"):
                diagnosed_disease = diagnosis_result.get('disease', '未知')
                confidence = diagnosis_result.get('confidence', 'unknown')
                st.success(f"**诊断结果**: {diagnosed_disease}")
                st.write(f"**置信度**: {confidence}")
                reasoning = diagnosis_result.get('reasoning', '')
                if reasoning:
                    st.write(f"**诊断依据**: {reasoning[:200]}...")
        
        patient.receive_diagnosis(diagnosis_result)
        
        # 步骤7: 治疗方案
        with step7.container():
            st.markdown("🔵 **步骤7: 制定治疗方案** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write("正在制定治疗方案...")
        
        treatment_plan = diagnosis_result.get('treatment_plan', {})
        patient.receive_treatment(treatment_plan)
        
        with step7.container():
            st.markdown("✅ **步骤7: 制定治疗方案** - 已完成")
            with st.expander("查看详情"):
                medications = treatment_plan.get('medications', [])
                if medications:
                    st.write(f"**处方药物**: {', '.join(medications[:5])}")
                recommendations = treatment_plan.get('recommendations', '')
                if recommendations:
                    # 处理字符串或列表格式
                    if isinstance(recommendations, str):
                        st.write(f"**医嘱**: {recommendations}")
                    elif isinstance(recommendations, list):
                        st.write(f"**医嘱**: {', '.join(recommendations[:3])}")
        
        # 步骤8: 康复评估
        with step8.container():
            st.markdown("🔵 **步骤8: 康复评估** - 进行中...")
            with st.expander("查看详情", expanded=True):
                st.write("评估治疗效果...")
        
        treatment_outcome = patient.evaluate_treatment_outcome()
        treatment_record['outcome'] = treatment_outcome
        
        with step8.container():
            if treatment_outcome['is_recovered']:
                st.markdown("✅ **步骤8: 康复评估** - 已完成")
                with st.expander("查看详情"):
                    st.success("🎉 **治疗成功！病人已康复**")
                    if treatment_outcome['is_diagnosis_correct']:
                        st.success("✅ 诊断正确")
                    else:
                        st.warning(f"⚠️ 诊断有误")
                        st.write(f"错误诊断: {diagnosis_result.get('disease')}")
                        st.write(f"正确诊断: {patient.disease}")
            else:
                st.markdown("⚠️ **步骤8: 康复评估** - 需要复诊")
                with st.expander("查看详情"):
                    st.warning("治疗效果不佳，建议复诊")
                    if treatment_outcome['is_diagnosis_correct']:
                        st.info("诊断正确，但需要调整治疗方案")
                    else:
                        st.error("诊断错误")
                        st.write(f"错误诊断: {diagnosis_result.get('disease')}")
                        st.write(f"正确诊断: {patient.disease}")
        
        # 医生学习
        doctor.learn_from_treatment_outcome(patient, diagnosis_result, treatment_outcome)
        
        # 更新统计
        hospital._update_stats(recommended_dept, treatment_outcome['is_recovered'])
        
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
            st.markdown(f"---")
            st.markdown(f"### 🏥 病人 {i}/{len(patients)}")
            
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
