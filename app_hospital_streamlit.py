"""
Agent Hospital 可视化前端
基于 Streamlit 实现的实时模拟医院可视化界面
"""
import streamlit as st
import os
import sys
import json
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入前端组件
from frontend.styles.custom_css import get_custom_css
from frontend.components.patient_card import render_patient_card

# 延迟导入：只在点击初始化按钮时才导入重型模块
# 这样可以大幅加快页面首次加载速度
# from simulation.agent_hospital import AgentHospital
# from simulation.patient_generator import PatientGenerator


# 页面配置
st.set_page_config(
    page_title="Agent Hospital - 模拟医院系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# 初始化 session state
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
if 'completed_treatments' not in st.session_state:
    # 存储已完成治疗的详细记录，用于展示
    st.session_state.completed_treatments = []


def initialize_hospital():
    """初始化医院系统（带实时进度显示）"""
    # 创建进度显示容器
    progress_container = st.empty()
    status_container = st.empty()
    
    try:
        # 步骤1: 导入模块
        with progress_container.container():
            st.info("🔄 步骤 1/3: 正在导入系统模块...")
        
        # 延迟导入 - 只在这里才真正加载
        from simulation.agent_hospital import AgentHospital
        from simulation.patient_generator import PatientGenerator
        
        with progress_container.container():
            st.success("✅ 步骤 1/3: 系统模块导入完成")
        
        # 步骤2: 加载数据集
        with progress_container.container():
            st.success("✅ 步骤 1/3: 系统模块导入完成")
            st.info("🔄 步骤 2/3: 正在加载疾病数据集...")
        
        st.session_state.patient_gen = PatientGenerator()
        
        with progress_container.container():
            st.success("✅ 步骤 1/3: 系统模块导入完成")
            st.success(f"✅ 步骤 2/3: 数据集加载完成 ({len(st.session_state.patient_gen)} 种疾病)")
        
        # 步骤3: 初始化医院系统
        with progress_container.container():
            st.success("✅ 步骤 1/3: 系统模块导入完成")
            st.success(f"✅ 步骤 2/3: 数据集加载完成 ({len(st.session_state.patient_gen)} 种疾病)")
            st.info("🔄 步骤 3/3: 正在初始化医院系统（加载知识库、创建医生团队）...")
        
        st.session_state.hospital = AgentHospital()
        st.session_state.initialized = True
        
        # 全部完成
        progress_container.empty()
        
        status = f"""✅ **Agent Hospital 初始化成功！**

**系统信息：**
- 科室数量：{len(st.session_state.hospital.departments)}
- 医生数量：{len(st.session_state.hospital.doctor_agents)}
- 数据集疾病：{len(st.session_state.patient_gen)} 种

**科室列表：**
{', '.join([dept['name'] for dept in st.session_state.hospital.departments])}

**病例库：** {len(st.session_state.hospital.case_base)} 个案例
**经验库：** {len(st.session_state.hospital.experience_base)} 条规则
"""
        return True, status
    
    except Exception as e:
        progress_container.empty()
        import traceback
        error_detail = traceback.format_exc()
        return False, f"❌ 初始化失败：{str(e)}\n\n详细错误：\n```\n{error_detail}\n```"


def display_treatment_step(step_name, status, details=None, icon="🔄"):
    """显示治疗流程的一个步骤"""
    if status == "pending":
        st.markdown(f"⚪ **{step_name}** - 等待中")
    elif status == "running":
        st.markdown(f"🔵 **{step_name}** - 进行中...")
        if details:
            with st.expander("查看详情", expanded=True):
                st.write(details)
    elif status == "completed":
        st.markdown(f"✅ **{step_name}** - 已完成")
        if details:
            with st.expander("查看详情"):
                st.write(details)
    elif status == "error":
        st.markdown(f"❌ **{step_name}** - 失败")
        if details:
            with st.expander("查看详情"):
                st.error(details)


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
        import time
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
        
        # 添加完整的患者信息和部门信息
        treatment_record['patient_info'] = {
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'symptoms': patient.symptoms,
            'disease': patient.disease
        }
        treatment_record['department'] = recommended_dept
        treatment_record['doctor_name'] = doctor.name
        treatment_record['treatment'] = treatment_plan
        
        return treatment_record
        
    except Exception as e:
        import traceback
        st.error(f"治疗过程出错: {str(e)}")
        st.code(traceback.format_exc())
        treatment_record['success'] = False
        treatment_record['error'] = str(e)
        return treatment_record


def treat_single_patient_with_card(patient, hospital):
    """
    单个病人治疗流程，使用新的卡片形式展示
    静默执行治疗，不显示过程，完成后返回结构化数据
    """
    treatment_record = {
        'patient_id': patient.patient_id,
        'patient_name': patient.name,
        'ground_truth_disease': patient.disease,
        'events': []
    }
    
    try:
        # 步骤1: 病例输入
        treatment_record['patient_info'] = {
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'symptoms': patient.symptoms,
            'disease': patient.disease
        }
        
        # 步骤2: 分诊
        triage_result = hospital.triage_nurse.triage(patient)
        treatment_record['triage'] = triage_result
        recommended_dept = triage_result['recommended_departments'][0]
        
        # 获取医生
        if recommended_dept not in hospital.doctor_agents:
            recommended_dept = list(hospital.doctor_agents.keys())[0]
        doctor = hospital.doctor_agents[recommended_dept]
        
        treatment_record['department'] = recommended_dept
        treatment_record['doctor_name'] = doctor.name
        
        # 步骤4: 问诊
        examination_types = hospital._determine_examinations(patient, doctor)
        
        # 步骤5: 医学检查
        examination_results = {}
        for exam_type in examination_types:
            exam_result = hospital.examination_nurse.conduct_examination(patient, exam_type)
            examination_results[exam_type] = exam_result
        
        treatment_record['examinations'] = examination_results
        
        # 步骤6: AI诊断
        diagnosis_result = doctor.diagnose_with_evolution(patient, examination_results)
        treatment_record['diagnosis'] = diagnosis_result
        
        patient.receive_diagnosis(diagnosis_result)
        
        # 步骤7: 治疗方案
        treatment_plan = diagnosis_result.get('treatment_plan', {})
        patient.receive_treatment(treatment_plan)
        treatment_record['treatment'] = treatment_plan
        
        # 步骤8: 康复评估
        treatment_outcome = patient.evaluate_treatment_outcome()
        treatment_record['outcome'] = treatment_outcome
        
        # 医生学习
        doctor.learn_from_treatment_outcome(patient, diagnosis_result, treatment_outcome)
        
        # 更新统计
        hospital._update_stats(recommended_dept, treatment_outcome['is_recovered'])
        
        treatment_record['success'] = True
        return treatment_record
        
    except Exception as e:
        import traceback
        treatment_record['success'] = False
        treatment_record['error'] = str(e)
        treatment_record['error_trace'] = traceback.format_exc()
        return treatment_record


def treat_single_patient_with_realtime_card(patient, hospital, card_container):
    """
    单个病人治疗流程，带实时卡片更新
    在治疗过程中动态更新进度条状态
    """
    from frontend.components.patient_card import generate_interactive_card_html
    
    treatment_record = {
        'patient_id': patient.patient_id,
        'patient_name': patient.name,
        'ground_truth_disease': patient.disease,
        'events': []
    }
    
    # 初始化步骤数据
    steps_data = [{} for _ in range(8)]
    card_id = f"realtime_{patient.patient_id}"
    
    def update_card(current_step, steps_status):
        """更新卡片显示"""
        card_html = generate_interactive_card_html(
            card_id,
            patient.name,
            "🔄 治疗进行中...",
            "result-running",
            "",
            steps_status
        )
        with card_container:
            components.html(card_html, height=400, scrolling=False)
    
    try:
        # 步骤1: 病例输入
        steps_status = []
        steps_status.append({'status': 'running', 'data': {}})
        for _ in range(7):
            steps_status.append({'status': 'pending', 'data': {}})
        update_card(0, steps_status)
        
        treatment_record['patient_info'] = {
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'symptoms': patient.symptoms,
            'disease': patient.disease
        }
        steps_data[0] = treatment_record['patient_info']
        steps_status[0] = {'status': 'completed', 'data': steps_data[0]}
        update_card(0, steps_status)
        
        # 步骤2: 分诊
        steps_status[1] = {'status': 'running', 'data': {}}
        update_card(1, steps_status)
        
        triage_result = hospital.triage_nurse.triage(patient)
        treatment_record['triage'] = triage_result
        recommended_dept = triage_result['recommended_departments'][0]
        
        steps_data[1] = {
            'department': recommended_dept,
            'reasoning': triage_result.get('reasoning', '基于症状分析')
        }
        steps_status[1] = {'status': 'completed', 'data': steps_data[1]}
        update_card(1, steps_status)
        
        # 步骤3: 挂号登记
        steps_status[2] = {'status': 'running', 'data': {}}
        update_card(2, steps_status)
        
        if recommended_dept not in hospital.doctor_agents:
            recommended_dept = list(hospital.doctor_agents.keys())[0]
        doctor = hospital.doctor_agents[recommended_dept]
        
        treatment_record['department'] = recommended_dept
        treatment_record['doctor_name'] = doctor.name
        
        steps_data[2] = {'department': recommended_dept}
        steps_status[2] = {'status': 'completed', 'data': steps_data[2]}
        update_card(2, steps_status)
        
        # 步骤4: 问诊
        steps_status[3] = {'status': 'running', 'data': {}}
        update_card(3, steps_status)
        
        examination_types = hospital._determine_examinations(patient, doctor)
        
        steps_data[3] = {
            'doctor_name': doctor.name,
            'department': recommended_dept,
            'examinations': examination_types
        }
        steps_status[3] = {'status': 'completed', 'data': steps_data[3]}
        update_card(3, steps_status)
        
        # 步骤5: 医学检查
        steps_status[4] = {'status': 'running', 'data': {}}
        update_card(4, steps_status)
        
        examination_results = {}
        for exam_type in examination_types:
            exam_result = hospital.examination_nurse.conduct_examination(patient, exam_type)
            examination_results[exam_type] = exam_result
        
        treatment_record['examinations'] = examination_results
        steps_data[4] = {'results': examination_results}
        steps_status[4] = {'status': 'completed', 'data': steps_data[4]}
        update_card(4, steps_status)
        
        # 步骤6: AI诊断
        steps_status[5] = {'status': 'running', 'data': {}}
        update_card(5, steps_status)
        
        diagnosis_result = doctor.diagnose_with_evolution(patient, examination_results)
        treatment_record['diagnosis'] = diagnosis_result
        patient.receive_diagnosis(diagnosis_result)
        
        steps_data[5] = diagnosis_result
        steps_status[5] = {'status': 'completed', 'data': steps_data[5]}
        update_card(5, steps_status)
        
        # 步骤7: 治疗方案
        steps_status[6] = {'status': 'running', 'data': {}}
        update_card(6, steps_status)
        
        treatment_plan = diagnosis_result.get('treatment_plan', {})
        patient.receive_treatment(treatment_plan)
        treatment_record['treatment'] = treatment_plan
        
        steps_data[6] = treatment_plan
        steps_status[6] = {'status': 'completed', 'data': steps_data[6]}
        update_card(6, steps_status)
        
        # 步骤8: 康复评估
        steps_status[7] = {'status': 'running', 'data': {}}
        update_card(7, steps_status)
        
        treatment_outcome = patient.evaluate_treatment_outcome()
        treatment_record['outcome'] = treatment_outcome
        
        # 医生学习
        doctor.learn_from_treatment_outcome(patient, diagnosis_result, treatment_outcome)
        
        # 更新统计
        hospital._update_stats(recommended_dept, treatment_outcome['is_recovered'])
        
        # 确定最终状态
        is_recovered = treatment_outcome.get('is_recovered', False)
        is_diagnosis_correct = treatment_outcome.get('is_diagnosis_correct', False)
        
        steps_data[7] = {
            'is_recovered': is_recovered,
            'is_diagnosis_correct': is_diagnosis_correct,
            'diagnosed_disease': diagnosis_result.get('disease', '未知'),
            'correct_disease': patient.disease
        }
        
        final_status = 'completed' if is_recovered else 'failed'
        steps_status[7] = {'status': final_status, 'data': steps_data[7]}
        
        # 最终更新 - 显示完整的治疗结果
        if is_recovered:
            result_text = '✅ 治疗成功'
            result_class = 'result-success'
        else:
            result_text = '❌ 需要复诊'
            result_class = 'result-failed'
        
        diagnosis_text = '✅ 诊断正确' if is_diagnosis_correct else '❌ 诊断错误'
        
        final_card_html = generate_interactive_card_html(
            card_id,
            patient.name,
            result_text,
            result_class,
            diagnosis_text,
            steps_status
        )
        with card_container:
            components.html(final_card_html, height=600, scrolling=False)
        
        treatment_record['success'] = True
        return treatment_record
        
    except Exception as e:
        import traceback
        treatment_record['success'] = False
        treatment_record['error'] = str(e)
        treatment_record['error_trace'] = traceback.format_exc()
        
        # 显示错误状态
        steps_status[min(len(steps_status)-1, 5)] = {'status': 'failed', 'data': {'error': str(e)}}
        update_card(5, steps_status)
        
        return treatment_record


def generate_and_treat_patient(num_patients, department_filter):
    """生成病人并进行治疗（使用卡片形式展示，支持实时更新）"""
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
        
        # 显示总体进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 创建一个实时卡片显示区域（只显示当前正在治疗的患者）
        realtime_card_container = st.empty()
        
        # 逐个治疗病人（实时显示卡片）
        completed_records = []
        for i, patient in enumerate(patients, 1):
            status_text.text(f"正在治疗第 {i}/{len(patients)} 位患者：{patient.name}...")
            
            # 使用实时卡片治疗函数（使用同一个容器，这样每次都会替换之前的内容）
            record = treat_single_patient_with_realtime_card(patient, hospital, realtime_card_container)
            completed_records.append(record)
            
            # 更新进度条
            progress_bar.progress(i / len(patients))
            
            # 记录到历史
            treatment_record = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'patient': patient.name,
                'disease': patient.disease,
                'department': record.get('department', '未知'),
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
        
        # 清除进度条和实时卡片容器
        progress_bar.empty()
        status_text.empty()
        realtime_card_container.empty()
        
        # 保存完成的治疗记录
        st.session_state.completed_treatments = completed_records
        
        st.success(f"✅ 批量治疗完成！共治疗 {len(patients)} 位病人")
        
        # 显示所有患者卡片
        st.markdown("---")
        st.subheader("📋 治疗结果总览")
        
        for i, record in enumerate(completed_records):
            render_patient_card(i + 1, record, f"patient_{i}_{datetime.now().timestamp()}")
            st.markdown("<br>", unsafe_allow_html=True)
        
        return "completed"
    
    except Exception as e:
        import traceback
        return f"❌ 治疗过程出错：{str(e)}\n{traceback.format_exc()}"


def get_hospital_stats():
    """获取医院统计信息"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    stats = hospital.stats
    
    total = stats['total_patients']
    if total == 0:
        return "暂无治疗记录"
    
    success_rate = (stats['successful_treatments'] / total) * 100
    
    md = f"""## 📊 医院统计信息

### 总体数据
- **总治疗病人数：** {total}
- **成功治疗：** {stats['successful_treatments']} ({success_rate:.1f}%)
- **治疗失败：** {stats['failed_treatments']}

### 知识库
- **病例库案例数：** {len(hospital.case_base)}
- **经验库规则数：** {len(hospital.experience_base)}

### 各科室医生表现
"""
    
    for dept_name, doctor in hospital.doctor_agents.items():
        doctor_stats = doctor.get_stats()
        if doctor_stats['total_patients_treated'] > 0:
            md += f"""
**{dept_name}**
- 治疗病人：{doctor_stats['total_patients_treated']}
- 诊断准确率：{doctor_stats['diagnosis_accuracy']:.1%}
- 治疗成功率：{doctor_stats['treatment_success_rate']:.1%}
"""
    
    return md


def get_evolution_chart():
    """获取医生进化图表"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return None
    
    data = []
    for dept_name, doctor in hospital.doctor_agents.items():
        stats = doctor.get_stats()
        if stats['total_patients_treated'] > 0:
            data.append({
                '科室': dept_name,
                '治疗病人数': stats['total_patients_treated'],
                '诊断准确率': stats['diagnosis_accuracy'] * 100,
                '治疗成功率': stats['treatment_success_rate'] * 100
            })
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    return df


def get_treatment_timeline():
    """获取治疗时间线"""
    if not st.session_state.treatment_history:
        return None
    
    # 只显示最近20条
    recent = st.session_state.treatment_history[-20:]
    
    df = pd.DataFrame(recent)
    df['结果'] = df.apply(
        lambda x: '✅成功' if x['success'] else '❌失败', 
        axis=1
    )
    df['诊断'] = df.apply(
        lambda x: '✅正确' if x['diagnosis_correct'] else '❌错误', 
        axis=1
    )
    
    return df[['time', 'patient', 'disease', 'department', '诊断', '结果']]


def get_case_base_info():
    """获取病例库信息"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    stats = hospital.case_base.get_stats()
    
    md = f"""## 📚 病例库详情

**总案例数：** {stats['total_cases']}
**成功案例：** {stats['successful_cases']}

### 各科室案例分布
"""
    
    for dept, count in stats['by_department'].items():
        md += f"- **{dept}：** {count} 个案例\n"
    
    return md


def get_experience_base_info():
    """获取经验库信息"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    stats = hospital.experience_base.get_stats()
    
    md = f"""## 🧠 经验库详情

**总规则数：** {stats['total_rules']}
**成功应用：** {stats['successful_applications']} 次
**失败应用：** {stats['failed_applications']} 次

### 各科室规则分布
"""
    
    for dept, count in stats['by_department'].items():
        md += f"- **{dept}：** {count} 条规则\n"
    
    return md


def clear_knowledge_bases():
    """清空知识库"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    try:
        hospital.case_base.clear()
        hospital.experience_base.clear()
        return "✅ 知识库已清空"
    except Exception as e:
        return f"❌ 清空失败：{str(e)}"


def save_current_state():
    """保存当前状态"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    try:
        output_dir = "./simulation_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"hospital_state_{timestamp}.json")
        
        # 保存医院记录
        hospital.save_records(output_path)
        
        # 保存历史统计数据
        stats_path = os.path.join(output_dir, f"all_time_stats_{timestamp}.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump({
                'all_time_stats': st.session_state.all_time_stats,
                'treatment_history': st.session_state.treatment_history,
                'timestamp': timestamp
            }, f, ensure_ascii=False, indent=2)
        
        return f"✅ 状态已保存至：{output_path}\n✅ 历史统计已保存至：{stats_path}"
    except Exception as e:
        return f"❌ 保存失败：{str(e)}"


# =============================================================================
# 主界面
# =============================================================================

st.title("🏥 Agent Hospital - 可进化的模拟医院系统")
st.markdown("""
基于论文 **"Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents"** 实现

观察医生Agent如何从治疗中学习和进化 🚀

💡 **提示**：首次使用请点击侧边栏的「初始化系统」按钮
""")

# 侧边栏 - 控制面板
with st.sidebar:
    st.header("🎛️ 控制面板")
    
    # 显示系统状态
    if st.session_state.initialized:
        st.success("✅ 系统已初始化")
    else:
        st.warning("⚠️ 系统未初始化")
    
    # 初始化按钮
    if st.button("🚀 初始化系统", type="primary", use_container_width=True):
        # 不使用 spinner，因为 initialize_hospital() 内部有详细的进度显示
        success, message = initialize_hospital()
        if success:
            st.success(message)
        else:
            st.error(message)
    
    st.divider()
    
    # 治疗设置
    st.subheader("生成并治疗病人")
    num_patients = st.number_input("病人数量", min_value=1, max_value=1000, value=1, step=1, key='num_patients', help="输入要治疗的病人数量（1-1000）")
    department_filter = st.selectbox(
        "科室筛选",
        ["全部", "心脏科", "神经科", "肿瘤科", "呼吸科", "消化科"],
        key='department_filter'
    )
    
    if st.button("🏥 开始治疗", type="primary", use_container_width=True):
        if not st.session_state.initialized:
            st.warning("⚠️ 请先初始化系统")
        else:
            st.session_state.start_treatment = True
    
    st.divider()
    
    # 系统管理
    st.subheader("系统管理")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存", use_container_width=True):
            message = save_current_state()
            if "成功" in message:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        if st.button("🗑️ 清空", use_container_width=True):
            message = clear_knowledge_bases()
            if "成功" in message:
                st.success(message)
            else:
                st.error(message)

# 主内容区域
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 治疗流程", 
    "📊 统计", 
    "📚 病例库", 
    "🧠 经验库", 
    "📖 使用说明"
])

with tab1:
    st.subheader("🎯 患者治疗流程展示")
    st.markdown("""
    **现代化的横向进度条展示，包含8个关键步骤：**
    
    📝 病例输入 → 🎯 智能分诊 → 📋 挂号登记 → 👨‍⚕️ 医生问诊 → 🔬 医学检查 → 🧠 AI智能诊断 → 💊 治疗方案 → 🎉 康复评估
    
    - ✅ 完成的步骤显示为绿色，失败的步骤显示为红色
    - 🔍 点击卡片下方的"查看详细流程"可展开每个步骤的详细信息
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
    
    # 显示历史治疗记录
    if st.session_state.completed_treatments:
        st.markdown("---")
        st.subheader("📋 本次治疗记录")
        
        # 添加筛选选项
        col1, col2 = st.columns([3, 1])
        with col1:
            show_all = st.checkbox("显示所有记录", value=False, key="show_all_records")
        with col2:
            if st.button("🗑️ 清空记录", key="clear_records"):
                st.session_state.completed_treatments = []
                st.rerun()
        
        records_to_show = st.session_state.completed_treatments if show_all else st.session_state.completed_treatments[-10:]
        
        if not show_all and len(st.session_state.completed_treatments) > 10:
            st.info(f"显示最近 10 条记录，共 {len(st.session_state.completed_treatments)} 条记录")
        
        for i, record in enumerate(records_to_show):
            render_patient_card(i + 1, record, f"history_patient_{i}_{record.get('patient_id', i)}")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("👉 请在侧边栏选择病人数量和科室，然后点击'开始治疗'按钮启动治疗流程")

with tab2:
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

with tab3:
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

with tab4:
    st.subheader("经验库详情")
    exp_info = get_experience_base_info()
    st.markdown(exp_info)
    
    st.divider()
    
    # 显示详细规则
    st.markdown("### 🔍 查看具体规则")
    
    hospital = st.session_state.hospital
    if hospital and len(hospital.experience_base) > 0:
        # 按科室筛选
        dept_filter = st.selectbox(
            "选择科室",
            ["全部"] + list(hospital.experience_base.department_index.keys()),
            key="exp_dept_filter"
        )
        
        # 获取规则
        if dept_filter == "全部":
            rules = hospital.experience_base.rules[:20]  # 最多显示20个
        else:
            rule_ids = hospital.experience_base.department_index.get(dept_filter, [])[:20]
            rules = [hospital.experience_base.rule_index[rid] for rid in rule_ids]
        
        if rules:
            st.write(f"共找到 {len(rules)} 条相关规则（最多显示20条）")
            
            for i, rule in enumerate(rules, 1):
                # 计算成功率
                success_rate = (rule['success_count'] / rule['application_count']) if rule['application_count'] > 0 else 0
                confidence = rule.get('confidence', 0)
                
                status_icon = "✅" if rule['status'] == 'active' else "⚠️"
                
                with st.expander(f"{status_icon} 规则 {i}: {rule.get('disease', '未知')} - {rule.get('department', '未知科室')} (置信度: {confidence:.2f})"):
                    st.write(f"**规则 ID:** {rule.get('rule_id', '未知')}")
                    st.write(f"**创建时间:** {rule.get('timestamp', '未知')[:19]}")
                    st.write(f"**状态:** {rule['status']}")
                    st.write(f"**应用次数:** {rule['application_count']}")
                    st.write(f"**成功次数:** {rule['success_count']}")
                    st.write(f"**成功率:** {success_rate:.1%}")
                    
                    st.write(f"**规则内容:**")
                    st.info(rule.get('rule_content', '无'))
                    
                    st.write(f"**推荐行动:**")
                    st.write(rule.get('recommendation', '无'))
                    
                    if 'reasoning' in rule:
                        st.write(f"**规则依据:**")
                        st.write(rule['reasoning'])
                    
                    if 'trigger_conditions' in rule:
                        st.write(f"**触发条件:**")
                        trigger = rule['trigger_conditions']
                        if 'symptoms' in trigger:
                            st.write(f"- 症状: {', '.join(trigger['symptoms'])}")
                        if 'age_range' in trigger:
                            st.write(f"- 年龄范围: {trigger['age_range']}")
                    
                    if 'source_case' in rule:
                        st.write(f"**来源案例:**")
                        source = rule['source_case']
                        st.write(f"- 错误诊断: {source.get('wrong_diagnosis', '未知')}")
                        st.write(f"- 正确诊断: {source.get('correct_diagnosis', '未知')}")
        else:
            st.info("该科室暂无规则")
    else:
        st.info("经验库为空，当医生出现误诊时会自动生成规则")
    
    st.divider()
    if st.button("🔄 刷新经验库", key="refresh_exp"):
        st.rerun()

with tab5:
    st.markdown("""
## 使用指南

### 1️⃣ 初始化系统
点击侧边栏的"初始化系统"按钮，系统将：
- 加载5个科室的医生Agent
- 加载CMeIEV2数据集（715种疾病）
- 初始化病例库和经验库

### 2️⃣ 开始治疗
1. 输入病人数量（1-1000）✨ **支持大批量测试**
2. 选择科室筛选（可选）
3. 点击"开始治疗"
4. **新界面**：治疗完成后，所有患者以现代化的卡片形式展示 🎨

### 3️⃣ 横向进度条功能 ✨ **全新设计**
每位患者的治疗流程以精美的横向进度条展示：

**8个步骤节点：**
- 📝 病例输入
- 🎯 智能分诊
- 📋 挂号登记
- 👨‍⚕️ 医生问诊
- 🔬 医学检查
- 🧠 AI智能诊断
- 💊 制定治疗方案
- 🎉 康复评估

**交互特性：**
- ✅ 完成的步骤显示为绿色，带有脉冲动画
- ❌ 失败的步骤显示为红色，带有抖动动画
- ⚪ 未执行的步骤显示为灰色
- 🔍 点击"查看详细流程"展开，可选择任意步骤查看详情
- 🎨 渐变背景和现代化卡片设计

### 4️⃣ 观察进化
- **治疗流程** - 横向进度条实时展示 ✨ **新UI设计**
  - 每位患者独立卡片展示
  - 点击展开查看详细信息
  - 支持显示所有历史记录
- **统计** - 查看历史以来所有病人的统计数据
  - 历史总体统计：所有治疗过的病人数据
  - 当前系统统计：本次session的数据
  - 医生表现和治疗时间线
- **病例库** - 查看积累的成功案例
  - 按科室筛选病例
  - 查看每个病例的详细信息
- **经验库** - 查看从失败中学到的规则
  - 按科室筛选规则
  - 查看规则内容、触发条件、应用效果

### 5️⃣ 验证学习效果
多次运行治疗，观察：
- 诊断准确率逐渐提升
- 病例库和经验库持续增长
- 治疗成功率改善
- 历史统计数据持续累积

### 6️⃣ 保存和管理
- 点击"保存"按钮保存当前状态
  - 保存医院治疗记录
  - 保存历史统计数据
- 点击"清空"按钮清空知识库
- 保存的文件位于 `./simulation_results` 目录

### 💡 提示
- 病例库和经验库会持久化保存
- 历史统计数据在保存后可持久化
- 重启系统后继续使用已有知识
- 可以清空知识库重新训练
- 支持大批量病人治疗（最多1000人）
- **新增**：前端组件模块化，位于 `frontend/` 目录 ✨

### ⚙️ 技术栈
- **前端框架：** Streamlit + HTML/CSS
- **UI组件：** 自定义组件（frontend/components）
- **样式系统：** 自定义CSS（frontend/styles）
- **AI引擎：** OpenAI API
- **知识库：** ChromaDB
- **数据集：** CMeIEV2 医学数据集

### 📁 项目结构
```
MedicM2/
├── frontend/              # 前端组件（新增）✨
│   ├── components/        # UI组件
│   │   ├── progress_bar.py   # 进度条组件
│   │   └── patient_card.py   # 患者卡片组件
│   └── styles/            # 样式文件
│       └── custom_css.py     # 自定义CSS
├── simulation/            # 医院模拟系统
├── agents/                # 医疗Agent
├── knowledge/             # 知识库
└── app_hospital_streamlit.py  # 主应用
```
""")

# 页脚
st.divider()
st.caption("Agent Hospital - 基于可进化医疗Agent的模拟医院系统 | Powered by Streamlit")
