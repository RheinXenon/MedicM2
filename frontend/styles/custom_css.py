"""
自定义CSS样式
为横向进度条和患者卡片提供现代化的样式
"""

def get_custom_css():
    """返回自定义CSS样式"""
    return """
    <style>
    /* 患者卡片样式 */
    .patient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .patient-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
    }
    
    .patient-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }
    
    .patient-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        color: white;
    }
    
    .patient-name {
        font-size: 1.5em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .patient-result {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .result-success {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #00ff88;
    }
    
    .result-failed {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff;
    }
    
    .result-revisit {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #fff;
    }
    
    /* 横向进度条容器 */
    .progress-container {
        position: relative;
        padding: 40px 0;
        margin: 30px 0;
    }
    
    /* 进度条背景线 */
    .progress-line {
        position: absolute;
        top: 50%;
        left: 5%;
        right: 5%;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
        transform: translateY(-50%);
    }
    
    /* 进度条进度线 */
    .progress-line-active {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        border-radius: 2px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.5);
    }
    
    /* 步骤容器 */
    .steps-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 2;
        padding: 0 3%;
    }
    
    /* 单个步骤 */
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        transition: all 0.3s ease;
        flex: 1;
        max-width: 120px;
    }
    
    .step:hover {
        transform: scale(1.05);
    }
    
    /* 步骤节点 */
    .step-node {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2em;
        font-weight: bold;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* 未完成状态 */
    .step-node.pending {
        background: rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.5);
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 完成状态 */
    .step-node.completed {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
        color: white;
        border: 3px solid #00ff88;
        animation: pulse-success 2s infinite;
    }
    
    /* 进行中状态 */
    .step-node.running {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: 3px solid #4facfe;
        animation: pulse-running 1.5s infinite;
    }
    
    /* 失败状态 */
    .step-node.failed {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        border: 3px solid #ff6b6b;
        animation: shake 0.5s;
    }
    
    /* 步骤标题 */
    .step-title {
        margin-top: 12px;
        font-size: 0.75em;
        text-align: center;
        color: white;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        line-height: 1.2;
        max-width: 100%;
        word-wrap: break-word;
    }
    
    .step-title.completed {
        color: #00ff88;
        font-weight: bold;
    }
    
    .step-title.failed {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    /* 详情区域 */
    .step-details {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        color: white;
        animation: slideDown 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .step-details h4 {
        margin-top: 0;
        color: #00c6ff;
        font-size: 1.2em;
        margin-bottom: 15px;
    }
    
    .step-details p {
        margin: 8px 0;
        line-height: 1.6;
    }
    
    .step-details strong {
        color: #00ff88;
    }
    
    /* 动画效果 */
    @keyframes pulse-success {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7);
        }
        50% {
            box-shadow: 0 0 0 10px rgba(0, 255, 136, 0);
        }
    }
    
    @keyframes pulse-running {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(79, 172, 254, 0.7);
        }
        50% {
            box-shadow: 0 0 0 10px rgba(79, 172, 254, 0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 响应式设计 */
    @media (max-width: 1200px) {
        .step-title {
            font-size: 0.7em;
        }
        .step-node {
            width: 40px;
            height: 40px;
            font-size: 1em;
        }
    }
    
    @media (max-width: 768px) {
        .step-title {
            font-size: 0.65em;
        }
        .step-node {
            width: 35px;
            height: 35px;
            font-size: 0.9em;
        }
        .patient-card {
            padding: 15px;
        }
    }
    </style>
    """


def get_step_emoji(step_index):
    """获取每个步骤的图标"""
    emojis = {
        0: "📝",  # 病例输入
        1: "🎯",  # 智能分诊
        2: "📋",  # 挂号登记
        3: "👨‍⚕️",  # 医生问诊
        4: "🔬",  # 医学检查
        5: "🧠",  # AI智能诊断
        6: "💊",  # 制定治疗方案
        7: "🎉"   # 康复评估
    }
    return emojis.get(step_index, "●")
