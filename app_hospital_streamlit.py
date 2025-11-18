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

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator


# 页面配置
st.set_page_config(
    page_title="Agent Hospital - 模拟医院系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 初始化 session state
if 'hospital' not in st.session_state:
    st.session_state.hospital = None
if 'patient_gen' not in st.session_state:
    st.session_state.patient_gen = None
if 'treatment_history' not in st.session_state:
    st.session_state.treatment_history = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'current_treatment' not in st.session_state:
    st.session_state.current_treatment = None
if 'treatment_steps' not in st.session_state:
    st.session_state.treatment_steps = []


def initialize_hospital():
    """初始化医院系统"""
    try:
        st.session_state.hospital = AgentHospital()
        st.session_state.patient_gen = PatientGenerator()
        st.session_state.initialized = True
        
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
        return False, f"❌ 初始化失败：{str(e)}"


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
                recommendations = treatment_plan.get('recommendations', [])
                if recommendations:
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
            st.session_state.treatment_history.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'patient': patient.name,
                'disease': patient.disease,
                'department': record.get('triage', {}).get('recommended_departments', ['未知'])[0],
                'success': record.get('outcome', {}).get('is_recovered', False),
                'diagnosis_correct': record.get('outcome', {}).get('is_diagnosis_correct', False)
            })
        
        st.success(f"\n✅ 批量治疗完成！共治疗 {len(patients)} 位病人")
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
        
        hospital.save_records(output_path)
        
        return f"✅ 状态已保存至：{output_path}"
    except Exception as e:
        return f"❌ 保存失败：{str(e)}"


# =============================================================================
# 主界面
# =============================================================================

st.title("🏥 Agent Hospital - 可进化的模拟医院系统")
st.markdown("""
基于论文 **"Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents"** 实现

观察医生Agent如何从治疗中学习和进化 🚀
""")

# 侧边栏 - 控制面板
with st.sidebar:
    st.header("🎛️ 控制面板")
    
    # 初始化按钮
    if st.button("🚀 初始化系统", type="primary", use_container_width=True):
        with st.spinner("正在初始化..."):
            success, message = initialize_hospital()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.divider()
    
    # 治疗设置
    st.subheader("生成并治疗病人")
    num_patients = st.slider("病人数量", min_value=1, max_value=20, value=1, step=1, key='num_patients')
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
    "📊 实时统计", 
    "📚 病例库", 
    "🧠 经验库", 
    "📖 使用说明"
])

with tab1:
    st.subheader("🎯 实时治疗流程可视化")
    st.markdown("""
    该界面将实时展示每个病人的完整治疗流程，包括：
    1. 📝 **病例输入** - 病人基本信息和症状
    2. 🎯 **智能分诊** - AI护士分析症状并推荐科室
    3. 📝 **挂号登记** - 完成就诊登记
    4. 👨‍⚕️ **医生问诊** - 主治医生询问病史并安排检查
    5. 🔬 **医学检查** - 进行各项医学检验
    6. 🧠 **AI智能诊断** - 大模型分析病情并给出诊断
    7. 💊 **治疗方案** - 制定个性化治疗方案
    8. 🎉 **康复评估** - 评估治疗效果
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
    else:
        st.info("👉 请在侧边栏选择病人数量和科室，然后点击'开始治疗'按钮启动治疗流程")

with tab2:
    st.subheader("医院统计信息")
    
    # 显示统计
    stats_md = get_hospital_stats()
    st.markdown(stats_md)
    
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
    
    if st.button("🔄 刷新病例库", key="refresh_case"):
        st.rerun()

with tab4:
    st.subheader("经验库详情")
    exp_info = get_experience_base_info()
    st.markdown(exp_info)
    
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
1. 选择病人数量（1-20）
2. 选择科室筛选（可选）
3. 点击"开始治疗"
4. 观察实时治疗日志和统计信息

### 3️⃣ 观察进化
- **实时统计** - 查看各科室医生的表现
- **病例库** - 查看积累的成功案例
- **经验库** - 查看从失败中学到的规则

### 4️⃣ 验证学习效果
多次运行治疗，观察：
- 诊断准确率逐渐提升
- 病例库和经验库持续增长
- 治疗成功率改善

### 💡 提示
- 病例库和经验库会持久化保存
- 重启系统后继续使用已有知识
- 可以清空知识库重新训练

### ⚙️ 技术栈
- **前端框架：** Streamlit
- **AI引擎：** OpenAI API
- **知识库：** ChromaDB
- **数据集：** CMeIEV2 医学数据集
""")

# 页脚
st.divider()
st.caption("Agent Hospital - 基于可进化医疗Agent的模拟医院系统 | Powered by Streamlit")
