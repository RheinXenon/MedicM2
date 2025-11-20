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
- **病例库总案例数：** {sum(len(cb) for cb in hospital.department_case_bases.values())}
- **经验库总规则数：** {sum(len(eb) for eb in hospital.department_experience_bases.values())}

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
    
    # 聚合所有科室的病例库统计
    total_cases = 0
    dept_stats = {}
    
    for dept_id, case_base in hospital.department_case_bases.items():
        stats = case_base.get_stats()
        count = stats.get('total_cases', 0)
        total_cases += count
        
        # 找到科室名称
        dept_name = next(
            (d['name'] for d in hospital.departments if d['id'] == dept_id),
            dept_id
        )
        if count > 0:
            dept_stats[dept_name] = count
    
    md = f"""## 📚 病例库详情

**总案例数：** {total_cases}

### 各科室案例分布
"""
    
    if dept_stats:
        for dept, count in sorted(dept_stats.items(), key=lambda x: x[1], reverse=True):
            md += f"- **{dept}：** {count} 个案例\n"
    else:
        md += "暂无案例\n"
    
    return md


def get_experience_base_info():
    """获取经验库信息"""
    hospital = st.session_state.hospital
    
    if hospital is None:
        return "请先初始化系统"
    
    # 聚合所有科室的经验库统计
    total_rules = 0
    total_success = 0
    total_failed = 0
    dept_stats = {}
    
    for dept_id, exp_base in hospital.department_experience_bases.items():
        stats = exp_base.get_stats()
        count = stats.get('total_rules', 0)
        total_rules += count
        total_success += stats.get('successful_applications', 0)
        total_failed += stats.get('failed_applications', 0)
        
        # 找到科室名称
        dept_name = next(
            (d['name'] for d in hospital.departments if d['id'] == dept_id),
            dept_id
        )
        if count > 0:
            dept_stats[dept_name] = count
    
    md = f"""## 🧠 经验库详情

**总规则数：** {total_rules}
**成功应用：** {total_success} 次
**失败应用：** {total_failed} 次

### 各科室规则分布
"""
    
    if dept_stats:
        for dept, count in sorted(dept_stats.items(), key=lambda x: x[1], reverse=True):
            md += f"- **{dept}：** {count} 条规则\n"
    else:
        md += "暂无规则\n"
    
    return md
