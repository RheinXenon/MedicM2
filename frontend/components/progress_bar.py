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


def render_progress_bar(steps_status, current_step_index=-1):
    """
    渲染横向进度条
    
    Args:
        steps_status: 步骤状态列表，每个元素是 {'status': 'pending/running/completed/failed', 'data': {...}}
        current_step_index: 当前选中的步骤索引，用于显示详情
    
    Returns:
        str: 返回HTML字符串
    """
    # 计算进度百分比
    completed_count = sum(1 for step in steps_status if step['status'] in ['completed', 'failed'])
    progress_percent = (completed_count / len(TREATMENT_STEPS)) * 100
    
    # 构建HTML
    html = '<div class="progress-container">'
    
    # 背景线
    html += '<div class="progress-line">'
    html += f'<div class="progress-line-active" style="width: {progress_percent}%;"></div>'
    html += '</div>'
    
    # 步骤节点
    html += '<div class="steps-container">'
    
    for i, step_name in enumerate(TREATMENT_STEPS):
        status = steps_status[i]['status']
        emoji = get_step_emoji(i)
        
        # 节点样式类
        node_class = f"step-node {status}"
        title_class = f"step-title {status}"
        
        # 步骤容器
        html += f'<div class="step" id="step-{i}">'
        
        # 节点
        html += f'<div class="{node_class}">{emoji}</div>'
        
        # 标题
        html += f'<div class="{title_class}">{step_name}</div>'
        
        html += '</div>'
    
    html += '</div>'
    html += '</div>'
    
    return html


def render_step_details(step_index, step_data):
    """
    渲染步骤详情
    
    Args:
        step_index: 步骤索引
        step_data: 步骤数据字典
    """
    step_name = TREATMENT_STEPS[step_index]
    
    html = f'<div class="step-details">'
    html += f'<h4>📋 {step_name} - 详细信息</h4>'
    
    # 根据不同步骤显示不同内容
    if step_index == 0:  # 病例输入
        html += f'<p><strong>患者姓名:</strong> {step_data.get("name", "未知")}</p>'
        html += f'<p><strong>年龄:</strong> {step_data.get("age", "未知")}岁</p>'
        html += f'<p><strong>性别:</strong> {step_data.get("gender", "未知")}</p>'
        symptoms = step_data.get("symptoms", [])
        if symptoms:
            html += f'<p><strong>主诉症状:</strong> {", ".join(symptoms[:5])}</p>'
    
    elif step_index == 1:  # 智能分诊
        html += f'<p><strong>推荐科室:</strong> {step_data.get("department", "未知")}</p>'
        html += f'<p><strong>分诊理由:</strong> {step_data.get("reasoning", "基于症状分析")}</p>'
    
    elif step_index == 2:  # 挂号登记
        html += f'<p><strong>挂号科室:</strong> {step_data.get("department", "未知")}</p>'
        html += f'<p><strong>状态:</strong> 已完成挂号</p>'
    
    elif step_index == 3:  # 医生问诊
        html += f'<p><strong>主治医生:</strong> {step_data.get("doctor_name", "未知")} ({step_data.get("department", "未知")})</p>'
        exams = step_data.get("examinations", [])
        if exams:
            html += f'<p><strong>需要检查:</strong> {", ".join(exams)}</p>'
    
    elif step_index == 4:  # 医学检查
        examinations = step_data.get("results", {})
        if examinations:
            html += '<p><strong>检查结果:</strong></p>'
            for exam_type, result in examinations.items():
                result_text = result.get('result', '正常') if isinstance(result, dict) else str(result)
                html += f'<p>&nbsp;&nbsp;• {exam_type}: {result_text}</p>'
    
    elif step_index == 5:  # AI智能诊断
        html += f'<p><strong>诊断结果:</strong> {step_data.get("disease", "未知")}</p>'
        html += f'<p><strong>置信度:</strong> {step_data.get("confidence", "unknown")}</p>'
        reasoning = step_data.get("reasoning", "")
        if reasoning:
            truncated = reasoning[:200] + "..." if len(reasoning) > 200 else reasoning
            html += f'<p><strong>诊断依据:</strong> {truncated}</p>'
    
    elif step_index == 6:  # 制定治疗方案
        medications = step_data.get("medications", [])
        if medications:
            html += f'<p><strong>处方药物:</strong> {", ".join(medications[:5])}</p>'
        recommendations = step_data.get("recommendations", "")
        if recommendations:
            if isinstance(recommendations, str):
                html += f'<p><strong>医嘱:</strong> {recommendations}</p>'
            elif isinstance(recommendations, list):
                html += f'<p><strong>医嘱:</strong> {", ".join(recommendations[:3])}</p>'
    
    elif step_index == 7:  # 康复评估
        is_recovered = step_data.get("is_recovered", False)
        is_diagnosis_correct = step_data.get("is_diagnosis_correct", False)
        
        if is_recovered:
            html += '<p style="color: #00ff88; font-weight: bold;">🎉 治疗成功！病人已康复</p>'
        else:
            html += '<p style="color: #ffd700; font-weight: bold;">⚠️ 治疗效果不佳，建议复诊</p>'
        
        if is_diagnosis_correct:
            html += '<p style="color: #00ff88;">✅ 诊断正确</p>'
        else:
            html += '<p style="color: #ff6b6b;">❌ 诊断有误</p>'
            html += f'<p><strong>错误诊断:</strong> {step_data.get("diagnosed_disease", "未知")}</p>'
            html += f'<p><strong>正确诊断:</strong> {step_data.get("correct_disease", "未知")}</p>'
    
    html += '</div>'
    
    return html


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
