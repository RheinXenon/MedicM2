"""
数据处理和统计工具函数
"""
import streamlit as st
import pandas as pd


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
