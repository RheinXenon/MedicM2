"""
Agent Hospital 可视化前端
基于 Gradio 实现的实时模拟医院可视化界面
"""
import gradio as gr
import os
import sys
import json
from datetime import datetime
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator


# 全局变量
hospital = None
patient_gen = None
treatment_history = []


def initialize_hospital():
    """初始化医院系统"""
    global hospital, patient_gen
    
    try:
        hospital = AgentHospital()
        patient_gen = PatientGenerator()
        
        status = f"""✅ **Agent Hospital 初始化成功！**

**系统信息：**
- 科室数量：{len(hospital.departments)}
- 医生数量：{len(hospital.doctor_agents)}
- 数据集疾病：{len(patient_gen)} 种

**科室列表：**
{', '.join([dept['name'] for dept in hospital.departments])}

**病例库：** {len(hospital.case_base)} 个案例
**经验库：** {len(hospital.experience_base)} 条规则
"""
        return status, get_hospital_stats()
    
    except Exception as e:
        return f"❌ 初始化失败：{str(e)}", ""


def generate_and_treat_patient(num_patients, department_filter):
    """生成病人并进行治疗"""
    global hospital, patient_gen, treatment_history
    
    if hospital is None:
        return "⚠️ 请先初始化系统", "", "", ""
    
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
        
        # 批量治疗
        log = f"🏥 开始治疗 {len(patients)} 位病人...\n\n"
        
        for i, patient in enumerate(patients, 1):
            log += f"【病人 {i}/{len(patients)}】\n"
            log += f"姓名：{patient.name}\n"
            log += f"疾病：{patient.disease}\n"
            
            # 治疗
            record = hospital.simulate_patient_treatment(patient, verbose=False)
            
            # 记录到历史
            treatment_history.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'patient': patient.name,
                'disease': patient.disease,
                'department': record.get('triage', {}).get('recommended_departments', ['未知'])[0],
                'success': record.get('outcome', {}).get('is_recovered', False),
                'diagnosis_correct': record.get('outcome', {}).get('is_diagnosis_correct', False)
            })
            
            # 显示结果
            outcome = record.get('outcome', {})
            if outcome.get('is_recovered'):
                log += "结果：✅ 治疗成功\n"
            else:
                log += "结果：❌ 治疗失败\n"
            
            if outcome.get('is_diagnosis_correct'):
                log += "诊断：✅ 正确\n"
            else:
                log += f"诊断：❌ 错误 (诊断为: {record.get('diagnosis', {}).get('disease', '未知')})\n"
            
            log += "-" * 50 + "\n\n"
        
        log += f"\n✅ 批量治疗完成！"
        
        # 更新统计
        stats = get_hospital_stats()
        evolution = get_evolution_chart()
        timeline = get_treatment_timeline()
        
        return log, stats, evolution, timeline
    
    except Exception as e:
        import traceback
        return f"❌ 治疗过程出错：{str(e)}\n{traceback.format_exc()}", "", "", ""


def get_hospital_stats():
    """获取医院统计信息"""
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
    if not treatment_history:
        return None
    
    # 只显示最近20条
    recent = treatment_history[-20:]
    
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


# 创建 Gradio 界面
with gr.Blocks(title="Agent Hospital - 模拟医院系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# 🏥 Agent Hospital - 可进化的模拟医院系统
    
基于论文 **"Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents"** 实现
    
观察医生Agent如何从治疗中学习和进化 🚀
""")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 🎛️ 控制面板")
            
            init_btn = gr.Button("🚀 初始化系统", variant="primary", size="lg")
            
            gr.Markdown("### 生成并治疗病人")
            num_patients = gr.Slider(
                minimum=1, 
                maximum=20, 
                value=5, 
                step=1, 
                label="病人数量"
            )
            department_filter = gr.Dropdown(
                choices=["全部", "心脏科", "神经科", "肿瘤科", "呼吸科", "消化科"],
                value="全部",
                label="科室筛选"
            )
            treat_btn = gr.Button("🏥 开始治疗", variant="primary")
            
            gr.Markdown("### 系统管理")
            with gr.Row():
                save_btn = gr.Button("💾 保存状态")
                clear_btn = gr.Button("🗑️ 清空知识库", variant="stop")
        
        with gr.Column(scale=2):
            gr.Markdown("## 📝 治疗日志")
            treatment_log = gr.Textbox(
                label="实时治疗过程",
                lines=15,
                max_lines=20,
                interactive=False
            )
            
            system_status = gr.Textbox(
                label="系统状态",
                lines=5,
                interactive=False
            )
    
    with gr.Tabs():
        with gr.Tab("📊 实时统计"):
            stats_display = gr.Markdown("请先初始化系统")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 医生表现")
                    evolution_df = gr.Dataframe(
                        headers=['科室', '治疗病人数', '诊断准确率', '治疗成功率'],
                        label="各科室医生统计"
                    )
                
                with gr.Column():
                    gr.Markdown("### 治疗时间线")
                    timeline_df = gr.Dataframe(
                        headers=['time', 'patient', 'disease', 'department', '诊断', '结果'],
                        label="最近治疗记录"
                    )
        
        with gr.Tab("📚 病例库"):
            case_base_info = gr.Markdown("请先初始化系统")
            refresh_case_btn = gr.Button("🔄 刷新")
        
        with gr.Tab("🧠 经验库"):
            exp_base_info = gr.Markdown("请先初始化系统")
            refresh_exp_btn = gr.Button("🔄 刷新")
        
        with gr.Tab("📖 使用说明"):
            gr.Markdown("""
## 使用指南

### 1️⃣ 初始化系统
点击"初始化系统"按钮，系统将：
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
""")
    
    # 事件绑定
    init_btn.click(
        fn=initialize_hospital,
        outputs=[system_status, stats_display]
    )
    
    treat_btn.click(
        fn=generate_and_treat_patient,
        inputs=[num_patients, department_filter],
        outputs=[treatment_log, stats_display, evolution_df, timeline_df]
    )
    
    save_btn.click(
        fn=save_current_state,
        outputs=[system_status]
    )
    
    clear_btn.click(
        fn=clear_knowledge_bases,
        outputs=[system_status]
    )
    
    refresh_case_btn.click(
        fn=get_case_base_info,
        outputs=[case_base_info]
    )
    
    refresh_exp_btn.click(
        fn=get_experience_base_info,
        outputs=[exp_base_info]
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" " * 15 + "Agent Hospital Web UI")
    print("=" * 60)
    print("\n正在启动可视化界面...")
    print("请在浏览器中访问显示的URL\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
