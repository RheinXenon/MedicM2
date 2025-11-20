"""
经验库页面
"""
import streamlit as st
from ..utils.data_utils import get_experience_base_info


def render_experience_base_page():
    """渲染经验库页面"""
    st.subheader("经验库详情")
    exp_info = get_experience_base_info()
    st.markdown(exp_info)
    
    st.divider()
    
    # 显示详细规则
    st.markdown("### 🔍 查看具体规则")
    
    hospital = st.session_state.hospital
    if hospital:
        # 收集所有有规则的科室
        dept_options = []
        dept_id_to_name = {}
        
        for dept_id, exp_base in hospital.department_experience_bases.items():
            # 安全获取规则数量
            try:
                rule_count = len(exp_base.rules) if hasattr(exp_base, 'rules') else 0
            except:
                rule_count = 0
            
            if rule_count > 0:
                dept_name = next(
                    (d['name'] for d in hospital.departments if d['id'] == dept_id),
                    dept_id
                )
                dept_options.append(dept_name)
                dept_id_to_name[dept_name] = dept_id
        
        if dept_options:
            # 按科室筛选
            dept_filter = st.selectbox(
                "选择科室",
                ["全部"] + sorted(dept_options),
                key="exp_dept_filter"
            )
            
            # 获取规则
            rules = []
            if dept_filter == "全部":
                # 收集所有科室的规则（最多20条）
                for exp_base in hospital.department_experience_bases.values():
                    try:
                        if hasattr(exp_base, 'rules') and isinstance(exp_base.rules, list):
                            rules.extend(exp_base.rules)
                            if len(rules) >= 20:
                                break
                    except Exception as e:
                        st.warning(f"读取规则时出错: {e}")
                        continue
                rules = rules[:20]
            else:
                # 获取特定科室的规则
                dept_id = dept_id_to_name[dept_filter]
                exp_base = hospital.department_experience_bases.get(dept_id)
                if exp_base and hasattr(exp_base, 'rules') and isinstance(exp_base.rules, list):
                    rules = exp_base.rules[:20]
                else:
                    rules = []
            
            if rules:
                st.write(f"共找到 {len(rules)} 条相关规则（最多显示20条）")
                
                for i, rule in enumerate(rules, 1):
                    # 计算成功率
                    success_rate = (rule['success_count'] / rule['application_count']) if rule['application_count'] > 0 else 0
                    confidence = rule.get('confidence', 0)
                    
                    status_icon = "✅" if rule['status'] == 'active' else "⚠️"
                    
                    with st.expander(f"{status_icon} 规则 {i}: {rule.get('disease', '未知')} - {rule.get('department', '未知科室')} (置信度: {confidence:.2f})"):
                        st.write(f"**规则 ID:** {rule.get('rule_id', '未知')}")
                        st.write(f"**创建时间:** {rule.get('timestamp', '未知')[:19]}")
                        st.write(f"**状态:** {rule['status']}")
                        st.write(f"**应用次数:** {rule['application_count']}")
                        st.write(f"**成功次数:** {rule['success_count']}")
                        st.write(f"**成功率:** {success_rate:.1%}")
                        
                        st.write(f"**规则内容:**")
                        st.info(rule.get('rule_content', '无'))
                        
                        st.write(f"**推荐行动:**")
                        st.write(rule.get('recommendation', '无'))
                        
                        if 'reasoning' in rule:
                            st.write(f"**规则依据:**")
                            st.write(rule['reasoning'])
                        
                        if 'trigger_conditions' in rule:
                            st.write(f"**触发条件:**")
                            trigger = rule['trigger_conditions']
                            if 'symptoms' in trigger:
                                st.write(f"- 症状: {', '.join(trigger['symptoms'])}")
                            if 'age_range' in trigger:
                                st.write(f"- 年龄范围: {trigger['age_range']}")
                        
                        if 'source_case' in rule:
                            st.write(f"**来源案例:**")
                            source = rule['source_case']
                            st.write(f"- 错误诊断: {source.get('wrong_diagnosis', '未知')}")
                            st.write(f"- 正确诊断: {source.get('correct_diagnosis', '未知')}")
            else:
                st.info("该科室暂无规则")
        else:
            st.info("经验库为空，当医生出现误诊时会自动生成规则")
    else:
        st.info("请先初始化系统")
    
    st.divider()
    if st.button("🔄 刷新经验库", key="refresh_exp"):
        st.rerun()
