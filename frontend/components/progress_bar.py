"""
横向进度条组件
展示8个步骤的治疗流程
"""
import streamlit as st
from frontend.styles.custom_css import get_step_emoji


# 定义8个步骤
TREATMENT_STEPS = [
    "病例输入",
    "智能分诊",
    "挂号登记",
    "医生问诊",
    "医学检查",
    "AI智能诊断",
    "制定治疗方案",
    "康复评估"
]


def render_step_details_data(step_index, step_data):
    """
    将步骤详情数据结构化返回（用于JavaScript渲染）
    
    Args:
        step_index: 步骤索引
        step_data: 步骤数据字典
    
    Returns:
        dict: 结构化的步骤详情数据
    """
    return step_data


def get_step_status_from_record(treatment_record):
    """
    从治疗记录中提取步骤状态
    
    Args:
        treatment_record: 治疗记录字典
    
    Returns:
        list: 步骤状态列表
    """
    steps_status = []
    
    # 步骤1: 病例输入
    patient_info = treatment_record.get('patient_info', {})
    steps_status.append({
        'status': 'completed',
        'data': patient_info
    })
    
    # 步骤2: 智能分诊
    triage = treatment_record.get('triage', {})
    if triage:
        dept = triage.get('recommended_departments', ['未知'])[0] if triage.get('recommended_departments') else '未知'
        steps_status.append({
            'status': 'completed',
            'data': {
                'department': dept,
                'reasoning': triage.get('reasoning', '基于症状分析')
            }
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤3: 挂号登记
    if triage:
        dept = triage.get('recommended_departments', ['未知'])[0] if triage.get('recommended_departments') else '未知'
        steps_status.append({
            'status': 'completed',
            'data': {'department': dept}
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤4: 医生问诊
    examinations = treatment_record.get('examinations', {})
    if examinations:
        steps_status.append({
            'status': 'completed',
            'data': {
                'doctor_name': treatment_record.get('doctor_name', '未知'),
                'department': treatment_record.get('department', '未知'),
                'examinations': list(examinations.keys())
            }
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤5: 医学检查
    if examinations:
        steps_status.append({
            'status': 'completed',
            'data': {'results': examinations}
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤6: AI智能诊断
    diagnosis = treatment_record.get('diagnosis', {})
    if diagnosis:
        steps_status.append({
            'status': 'completed',
            'data': diagnosis
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤7: 制定治疗方案
    treatment = treatment_record.get('treatment', {})
    if treatment:
        steps_status.append({
            'status': 'completed',
            'data': treatment
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    # 步骤8: 康复评估
    outcome = treatment_record.get('outcome', {})
    if outcome:
        # 判断是成功还是失败
        is_recovered = outcome.get('is_recovered', False)
        is_diagnosis_correct = outcome.get('is_diagnosis_correct', False)
        
        status = 'completed' if is_recovered else 'failed'
        
        steps_status.append({
            'status': status,
            'data': {
                'is_recovered': is_recovered,
                'is_diagnosis_correct': is_diagnosis_correct,
                'diagnosed_disease': diagnosis.get('disease', '未知'),
                'correct_disease': patient_info.get('disease', '未知')
            }
        })
    else:
        steps_status.append({'status': 'pending', 'data': {}})
    
    return steps_status
