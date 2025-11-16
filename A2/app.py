"""
智能多模态医疗诊断系统 - Streamlit 前端
"""
import streamlit as st
import json
import time
from datetime import datetime
from medical_system import MedicalDiagnosisSystem

# 页面配置
st.set_page_config(
    page_title="智能医疗诊断系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3498db;
        padding-left: 10px;
    }
    .dept-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .relevant-dept {
        border-color: #28a745;
        background-color: #d4edda;
    }
    .irrelevant-dept {
        border-color: #6c757d;
        background-color: #f8f9fa;
    }
    .thinking-step {
        border-left: 3px solid #17a2b8;
        padding-left: 15px;
        margin: 10px 0;
        background-color: #e7f3f8;
        border-radius: 5px;
        padding: 10px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_system():
    """初始化医疗诊断系统"""
    if 'system' not in st.session_state:
        with st.spinner('正在初始化医疗诊断系统...'):
            try:
                st.session_state.system = MedicalDiagnosisSystem()
                st.session_state.initialized = True
                st.success('✓ 系统初始化成功！')
            except Exception as e:
                st.error(f'系统初始化失败: {str(e)}')
                st.session_state.initialized = False


def render_thinking_process(thinking_steps, title="思考过程"):
    """渲染思考过程"""
    with st.expander(f"🧠 {title}", expanded=False):
        for i, step in enumerate(thinking_steps):
            st.markdown(f"""
            <div class="thinking-step">
                <strong>步骤 {i+1}: {step['step_name']}</strong><br>
                {step['content']}<br>
                <small style="color: #666;">
                    {datetime.fromtimestamp(step['timestamp']).strftime('%H:%M:%S')}
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            # 如果有元数据，显示
            if step.get('metadata'):
                with st.expander("查看详细信息", expanded=False):
                    st.json(step['metadata'])


def render_department_diagnosis(diag):
    """渲染单个科室的诊断"""
    is_relevant = diag.get('is_relevant', False)
    dept_class = "relevant-dept" if is_relevant else "irrelevant-dept"
    
    st.markdown(f'<div class="dept-card {dept_class}">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### {diag['department']}")
    
    with col2:
        relevance = diag.get('relevance_score', 0)
        st.metric("相关度", f"{relevance:.2%}")
    
    with col3:
        confidence = diag.get('confidence', 'unknown')
        confidence_emoji = {'high': '🟢', 'medium': '🟡', 'low': '⚪'}.get(confidence, '⚪')
        st.metric("置信度", f"{confidence_emoji} {confidence}")
    
    # 诊断内容
    st.markdown("#### 诊断意见")
    st.markdown(diag['diagnosis'])
    
    # 检索的知识
    if is_relevant and 'retrieved_knowledge' in diag:
        with st.expander("📚 参考的专业知识", expanded=False):
            for i, doc in enumerate(diag['retrieved_knowledge'][:3], 1):
                st.markdown(f"**知识片段 {i}:**")
                st.text(doc.get('content', '')[:300] + '...')
                st.caption(f"来源: {doc.get('metadata', {}).get('source', 'unknown')}")
                st.divider()
    
    # 思考过程
    if 'thinking_process' in diag:
        render_thinking_process(
            diag['thinking_process'], 
            f"{diag['department']}的思考过程"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-header">🏥 智能多模态医疗诊断系统</div>', 
                unsafe_allow_html=True)
    
    # 初始化系统
    initialize_system()
    
    if not st.session_state.get('initialized', False):
        st.error('系统未能正确初始化，请检查配置文件和依赖。')
        return
    
    # 侧边栏 - 病例输入
    with st.sidebar:
        st.markdown("## 📋 病例信息输入")
        
        st.markdown("### 基本信息")
        age = st.number_input("年龄", min_value=0, max_value=120, value=55)
        gender = st.selectbox("性别", ["男", "女"])
        chief_complaint = st.text_area(
            "主诉", 
            value="持续胸痛3天，伴有呼吸困难",
            height=80
        )
        
        st.markdown("### 临床表现")
        symptoms_text = st.text_area(
            "症状（每行一个）",
            value="胸部中央压榨性疼痛\n疼痛放射到左臂和下颌\n呼吸急促\n大汗淋漓\n恶心",
            height=150
        )
        
        st.markdown("### 既往史")
        history_text = st.text_area(
            "既往史（每行一个）",
            value="高血压10年\n糖尿病5年\n吸烟史30年\n高脂血症",
            height=120
        )
        
        st.markdown("### 生命体征")
        col1, col2 = st.columns(2)
        with col1:
            bp = st.text_input("血压", "160/95 mmHg")
            hr = st.text_input("心率", "102次/分")
            temp = st.text_input("体温", "37.2°C")
        with col2:
            spo2 = st.text_input("血氧", "94%")
            rr = st.text_input("呼吸", "22次/分")
        
        st.markdown("---")
        
        # 开始诊断按钮
        if st.button("🔍 开始诊断", type="primary", use_container_width=True):
            # 构建病例数据
            case_data = {
                "patient_info": {
                    "age": age,
                    "gender": gender,
                    "chief_complaint": chief_complaint
                },
                "symptoms": [s.strip() for s in symptoms_text.split('\n') if s.strip()],
                "medical_history": [h.strip() for h in history_text.split('\n') if h.strip()],
                "vital_signs": {
                    "血压": bp,
                    "心率": hr,
                    "体温": temp,
                    "血氧饱和度": spo2,
                    "呼吸频率": rr
                }
            }
            
            st.session_state.case_data = case_data
            st.session_state.start_diagnosis = True
    
    # 主内容区域
    if st.session_state.get('start_diagnosis', False):
        # 清除开始标志
        st.session_state.start_diagnosis = False
        
        # 显示病例摘要
        st.markdown('<div class="section-header">📝 病例摘要</div>', unsafe_allow_html=True)
        
        case_data = st.session_state.case_data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("患者年龄", f"{case_data['patient_info']['age']}岁")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("性别", case_data['patient_info']['gender'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("症状数量", len(case_data['symptoms']))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.info(f"**主诉:** {case_data['patient_info']['chief_complaint']}")
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message, progress):
            status_text.text(message)
            progress_bar.progress(progress)
        
        # 执行诊断
        try:
            with st.spinner('正在进行诊断...'):
                start_time = time.time()
                result = st.session_state.system.diagnose(
                    case_data,
                    include_images=False,
                    progress_callback=update_progress
                )
                end_time = time.time()
            
            # 清除进度条
            progress_bar.empty()
            status_text.empty()
            
            # 保存结果
            st.session_state.diagnosis_result = result
            st.session_state.diagnosis_time = end_time - start_time
            
            st.success(f'✓ 诊断完成！用时 {end_time - start_time:.2f} 秒')
            
        except Exception as e:
            st.error(f'诊断过程出错: {str(e)}')
            import traceback
            st.text(traceback.format_exc())
    
    # 显示诊断结果
    if 'diagnosis_result' in st.session_state:
        result = st.session_state.diagnosis_result
        
        # 统计信息
        st.markdown('<div class="section-header">📊 诊断统计</div>', unsafe_allow_html=True)
        
        relevant_depts = [d for d in result['department_diagnoses'] if d.get('is_relevant', False)]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("参与科室", len(result['department_diagnoses']))
        
        with col2:
            st.metric("相关科室", len(relevant_depts))
        
        with col3:
            st.metric("诊断用时", f"{st.session_state.diagnosis_time:.2f}秒")
        
        with col4:
            st.metric("置信度", "HIGH" if len(relevant_depts) >= 2 else "MEDIUM")
        
        # 各科室详细诊断
        st.markdown('<div class="section-header">🏥 各科室诊断详情</div>', unsafe_allow_html=True)
        
        # 创建标签页
        tabs = st.tabs(["相关科室", "所有科室"])
        
        with tabs[0]:
            if relevant_depts:
                for diag in relevant_depts:
                    render_department_diagnosis(diag)
            else:
                st.warning("未发现明显相关的科室")
        
        with tabs[1]:
            for diag in result['department_diagnoses']:
                render_department_diagnosis(diag)
        
        # 会诊报告
        st.markdown('<div class="section-header">📋 多学科会诊报告</div>', unsafe_allow_html=True)
        
        consultation = result['consultation']
        
        # 参与科室
        if consultation['participating_departments']:
            st.info(f"**参与会诊科室:** {', '.join(consultation['participating_departments'])}")
        
        # 会诊报告内容
        st.markdown("### 详细会诊报告")
        st.markdown(consultation['consultation_report'])
        
        # 会诊专家的思考过程
        if 'thinking_process' in consultation:
            render_thinking_process(
                consultation['thinking_process'],
                "会诊专家的思考过程"
            )
        
        # 下载报告
        st.markdown('<div class="section-header">💾 导出报告</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 生成JSON报告
            json_report = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 下载完整报告 (JSON)",
                data=json_report,
                file_name=f"diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # 生成文本报告
            text_report = result['summary']
            st.download_button(
                label="📥 下载摘要报告 (TXT)",
                data=text_report,
                file_name=f"diagnosis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


if __name__ == "__main__":
    main()
