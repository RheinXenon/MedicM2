"""
患者卡片组件
展示单个患者的治疗流程，包含横向进度条和详情展开
"""
import streamlit as st
import streamlit.components.v1 as components
import json
from frontend.components.progress_bar import (
    render_step_details_data,
    get_step_status_from_record,
    TREATMENT_STEPS
)


def render_patient_card(patient_index, treatment_record, unique_key):
    """
    渲染患者卡片 - 默认收起状态，点击节点展开详情
    
    Args:
        patient_index: 患者索引（用于显示）
        treatment_record: 治疗记录字典
        unique_key: 唯一键值，用于区分不同的卡片
    """
    # 获取步骤状态
    steps_status = get_step_status_from_record(treatment_record)
    
    # 获取患者信息
    patient_info = treatment_record.get('patient_info', {})
    patient_name = patient_info.get('name', '未知患者')
    
    # 获取治疗结果
    outcome = treatment_record.get('outcome', {})
    is_recovered = outcome.get('is_recovered', False)
    is_diagnosis_correct = outcome.get('is_diagnosis_correct', False)
    
    # 确定结果样式
    if is_recovered:
        result_class = 'result-success'
        result_text = '✅ 治疗成功'
    else:
        result_class = 'result-failed'
        result_text = '❌ 需要复诊'
    
    diagnosis_text = '✅ 诊断正确' if is_diagnosis_correct else '❌ 诊断错误'
    
    # 生成完整的HTML（包含JavaScript交互）
    card_html = generate_interactive_card_html(
        unique_key,
        patient_name,
        result_text,
        result_class,
        diagnosis_text,
        steps_status
    )
    
    # 渲染卡片，高度可以动态调整
    components.html(card_html, height=600, scrolling=False)


def generate_interactive_card_html(card_id, patient_name, result_text, result_class, diagnosis_text, steps_status):
    """
    生成带有JavaScript交互的患者卡片HTML
    """
    from frontend.styles.custom_css import get_step_emoji
    
    # 转换步骤数据为JSON（用于JavaScript）
    steps_data_json = json.dumps([{
        'status': step['status'],
        'data': step['data']
    } for step in steps_status], ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {get_card_styles()}
        </style>
    </head>
    <body>
        <div class="patient-card" id="card_{card_id}">
            <!-- 患者头部信息 -->
            <div class="patient-header">
                <div class="patient-name">👤 {patient_name}</div>
                <div class="patient-result-container">
                    <span class="{result_class}">{result_text}</span>
                    <span class="diagnosis-text">{diagnosis_text}</span>
                </div>
            </div>
            
            <!-- 横向进度条 -->
            <div class="progress-container">
                <div class="progress-line">
                    <div class="progress-line-active" id="progress_active_{card_id}"></div>
                </div>
                
                <div class="steps-container">
                    {generate_step_nodes(card_id, steps_status)}
                </div>
            </div>
            
            <!-- 详情区域（默认隐藏） -->
            <div class="details-container" id="details_{card_id}" style="display: none;">
                <div class="details-content" id="details_content_{card_id}"></div>
            </div>
        </div>
        
        <script>
            {generate_javascript_code(card_id, steps_status)}
        </script>
    </body>
    </html>
    """
    
    return html


def generate_step_nodes(card_id, steps_status):
    """生成步骤节点HTML"""
    from frontend.styles.custom_css import get_step_emoji
    
    html = ""
    for i, step in enumerate(steps_status):
        status = step['status']
        emoji = get_step_emoji(i)
        step_name = TREATMENT_STEPS[i]
        
        html += f"""
        <div class="step" onclick="toggleStepDetails('{card_id}', {i})">
            <div class="step-node {status}" id="node_{card_id}_{i}">
                <span class="step-emoji">{emoji}</span>
            </div>
            <div class="step-title {status}">{step_name}</div>
        </div>
        """
    
    return html


def generate_javascript_code(card_id, steps_status):
    """生成JavaScript交互代码"""
    steps_data_json = json.dumps([step['data'] for step in steps_status], ensure_ascii=False)
    
    # 计算进度百分比
    completed_count = sum(1 for step in steps_status if step['status'] in ['completed', 'failed'])
    progress_percent = (completed_count / len(TREATMENT_STEPS)) * 100
    
    js = f"""
        // 步骤数据
        const stepsData_{card_id} = {steps_data_json};
        let currentOpenStep_{card_id} = -1;
        
        // 初始化进度条
        const progressActive = document.getElementById('progress_active_{card_id}');
        progressActive.style.width = '{progress_percent}%';
        
        // 切换步骤详情
        function toggleStepDetails(cardId, stepIndex) {{
            const detailsContainer = document.getElementById('details_' + cardId);
            const detailsContent = document.getElementById('details_content_' + cardId);
            
            // 如果点击的是当前打开的步骤，则关闭
            if (currentOpenStep_{card_id} === stepIndex) {{
                detailsContainer.style.display = 'none';
                currentOpenStep_{card_id} = -1;
                // 移除所有节点的active样式
                for (let i = 0; i < 8; i++) {{
                    const node = document.getElementById('node_' + cardId + '_' + i);
                    if (node) node.classList.remove('active');
                }}
                return;
            }}
            
            // 显示详情容器
            detailsContainer.style.display = 'block';
            currentOpenStep_{card_id} = stepIndex;
            
            // 更新节点active状态
            for (let i = 0; i < 8; i++) {{
                const node = document.getElementById('node_' + cardId + '_' + i);
                if (node) {{
                    if (i === stepIndex) {{
                        node.classList.add('active');
                    }} else {{
                        node.classList.remove('active');
                    }}
                }}
            }}
            
            // 渲染步骤详情
            const stepData = stepsData_{card_id}[stepIndex];
            detailsContent.innerHTML = renderStepDetails(stepIndex, stepData);
            
            // 添加展开动画
            detailsContainer.style.animation = 'slideDown 0.3s ease';
        }}
        
        // 渲染步骤详情内容
        function renderStepDetails(stepIndex, stepData) {{
            const stepNames = {json.dumps(TREATMENT_STEPS, ensure_ascii=False)};
            const stepName = stepNames[stepIndex];
            
            let html = '<h4>📋 ' + stepName + ' - 详细信息</h4>';
            
            {generate_step_details_rendering_js()}
            
            return html;
        }}
    """
    
    return js


def generate_step_details_rendering_js():
    """生成步骤详情渲染的JavaScript代码"""
    return """
            // 根据不同步骤显示不同内容
            if (stepIndex === 0) {  // 病例输入
                html += '<p><strong>患者姓名:</strong> ' + (stepData.name || '未知') + '</p>';
                html += '<p><strong>年龄:</strong> ' + (stepData.age || '未知') + '岁</p>';
                html += '<p><strong>性别:</strong> ' + (stepData.gender || '未知') + '</p>';
                if (stepData.symptoms && stepData.symptoms.length > 0) {
                    html += '<p><strong>主诉症状:</strong> ' + stepData.symptoms.slice(0, 5).join(', ') + '</p>';
                }
            } else if (stepIndex === 1) {  // 智能分诊
                html += '<p><strong>推荐科室:</strong> ' + (stepData.department || '未知') + '</p>';
                html += '<p><strong>分诊理由:</strong> ' + (stepData.reasoning || '基于症状分析') + '</p>';
            } else if (stepIndex === 2) {  // 挂号登记
                html += '<p><strong>挂号科室:</strong> ' + (stepData.department || '未知') + '</p>';
                html += '<p><strong>状态:</strong> 已完成挂号</p>';
            } else if (stepIndex === 3) {  // 医生问诊
                html += '<p><strong>主治医生:</strong> ' + (stepData.doctor_name || '未知') + ' (' + (stepData.department || '未知') + ')</p>';
                if (stepData.examinations && stepData.examinations.length > 0) {
                    html += '<p><strong>需要检查:</strong> ' + stepData.examinations.join(', ') + '</p>';
                }
            } else if (stepIndex === 4) {  // 医学检查
                if (stepData.results) {
                    html += '<p><strong>检查结果:</strong></p>';
                    for (const [examType, result] of Object.entries(stepData.results)) {
                        const resultText = typeof result === 'object' ? (result.result || '正常') : String(result);
                        html += '<p>&nbsp;&nbsp;• ' + examType + ': ' + resultText + '</p>';
                    }
                }
            } else if (stepIndex === 5) {  // AI智能诊断
                html += '<p><strong>诊断结果:</strong> ' + (stepData.disease || '未知') + '</p>';
                html += '<p><strong>置信度:</strong> ' + (stepData.confidence || 'unknown') + '</p>';
                if (stepData.reasoning) {
                    const truncated = stepData.reasoning.length > 200 ? stepData.reasoning.substring(0, 200) + '...' : stepData.reasoning;
                    html += '<p><strong>诊断依据:</strong> ' + truncated + '</p>';
                }
            } else if (stepIndex === 6) {  // 制定治疗方案
                if (stepData.medications && stepData.medications.length > 0) {
                    html += '<p><strong>处方药物:</strong> ' + stepData.medications.slice(0, 5).join(', ') + '</p>';
                }
                if (stepData.recommendations) {
                    const recText = typeof stepData.recommendations === 'string' 
                        ? stepData.recommendations 
                        : stepData.recommendations.slice(0, 3).join(', ');
                    html += '<p><strong>医嘱:</strong> ' + recText + '</p>';
                }
            } else if (stepIndex === 7) {  // 康复评估
                if (stepData.is_recovered) {
                    html += '<p style="color: #00ff88; font-weight: bold;">🎉 治疗成功！病人已康复</p>';
                } else {
                    html += '<p style="color: #ffd700; font-weight: bold;">⚠️ 治疗效果不佳，建议复诊</p>';
                }
                
                if (stepData.is_diagnosis_correct) {
                    html += '<p style="color: #00ff88;">✅ 诊断正确</p>';
                } else {
                    html += '<p style="color: #ff6b6b;">❌ 诊断有误</p>';
                    html += '<p><strong>错误诊断:</strong> ' + (stepData.diagnosed_disease || '未知') + '</p>';
                    html += '<p><strong>正确诊断:</strong> ' + (stepData.correct_disease || '未知') + '</p>';
                }
            }
    """


def get_card_styles():
    """获取卡片样式CSS"""
    from frontend.styles.custom_css import get_custom_css_inline
    return get_custom_css_inline()


def render_realtime_patient_card(patient, current_step_index, steps_data):
    """
    渲染实时治疗的患者卡片（用于治疗过程中的实时显示）
    
    Args:
        patient: 患者对象
        current_step_index: 当前步骤索引
        steps_data: 步骤数据列表
    """
    patient_name = patient.name
    
    # 构建步骤状态
    steps_status = []
    for i in range(8):
        if i < current_step_index:
            status = 'completed'
        elif i == current_step_index:
            status = 'running'
        else:
            status = 'pending'
        
        data = steps_data[i] if i < len(steps_data) else {}
        steps_status.append({
            'status': status,
            'data': data
        })
    
    # 生成交互式卡片
    card_html = generate_interactive_card_html(
        f"realtime_{patient.patient_id}",
        patient_name,
        "🔄 治疗进行中...",
        "result-running",
        "",
        steps_status
    )
    
    # 渲染卡片
    components.html(card_html, height=600, scrolling=False)
