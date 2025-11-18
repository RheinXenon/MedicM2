"""
医院系统初始化和管理函数
"""
import streamlit as st
import os
import json
from datetime import datetime


def initialize_hospital():
    """初始化医院系统（带实时进度显示）"""
    # 设置初始化状态
    st.session_state.initializing = True
    
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
        st.session_state.initializing = False
        
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
        st.session_state.initializing = False
        st.session_state.initialized = False
        import traceback
        error_detail = traceback.format_exc()
        return False, f"❌ 初始化失败：{str(e)}\n\n详细错误：\n```\n{error_detail}\n```"


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
