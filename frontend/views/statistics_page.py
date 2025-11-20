"""
统计页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render_statistics_page():
    """渲染统计页面 - 显示所有历史记录的完整统计"""
    st.title("📊 医院统计分析")
    
    # 获取记录管理器
    records_manager = st.session_state.get('records_manager')
    
    if not records_manager:
        st.warning("记录管理器未初始化")
        return
    
    # 检查是否有记录
    total_records = records_manager.get_total_count()
    
    if total_records == 0:
        st.info("📭 暂无历史治疗记录，开始治疗后将显示统计数据")
        return
    
    # ========== 1. 全局总体统计 ==========
    st.markdown("### 📈 全局总体统计")
    global_stats = records_manager.get_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "总治疗人次",
            f"{global_stats['total_records']:,}",
            help="历史以来所有治疗记录数"
        )
    
    with col2:
        st.metric(
            "治疗成功率",
            f"{global_stats['treatment_success_rate']:.1f}%",
            help="治愈病人占总病人数的比例"
        )
    
    with col3:
        st.metric(
            "诊断准确率",
            f"{global_stats['diagnosis_accuracy']:.1f}%",
            help="正确诊断占总诊断数的比例"
        )
    
    with col4:
        st.metric(
            "成功治疗",
            f"{global_stats['successful_treatments']:,}",
            delta=f"+{global_stats['successful_treatments']}"
        )
    
    with col5:
        st.metric(
            "治疗失败",
            f"{global_stats['failed_treatments']:,}",
            delta=f"{global_stats['failed_treatments']}",
            delta_color="inverse"
        )
    
    st.divider()
    
    # ========== 2. 按科室统计 ==========
    st.markdown("### 🏥 各科室表现")
    
    dept_stats = records_manager.get_stats_by_department()
    
    if dept_stats:
        # 转换为DataFrame
        dept_df = pd.DataFrame.from_dict(dept_stats, orient='index')
        dept_df = dept_df.reset_index()
        dept_df.columns = ['科室', '总病人数', '成功治疗', '失败治疗', '诊断正确', '诊断错误', '诊断准确率', '治疗成功率']
        dept_df = dept_df.sort_values('总病人数', ascending=False)
        
        # 显示表格
        st.dataframe(
            dept_df[['科室', '总病人数', '诊断准确率', '治疗成功率', '成功治疗', '失败治疗']].style.format({
                '诊断准确率': '{:.1f}%',
                '治疗成功率': '{:.1f}%'
            }).background_gradient(subset=['诊断准确率', '治疗成功率'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
        
        # 图表展示
        col1, col2 = st.columns(2)
        
        with col1:
            # 科室治疗量柱状图
            fig1 = px.bar(
                dept_df,
                x='科室',
                y='总病人数',
                title='各科室治疗量',
                color='总病人数',
                color_continuous_scale='Blues',
                text='总病人数'
            )
            fig1.update_traces(textposition='outside')
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 科室成功率对比雷达图
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatterpolar(
                r=dept_df['诊断准确率'].tolist(),
                theta=dept_df['科室'].tolist(),
                fill='toself',
                name='诊断准确率'
            ))
            
            fig2.add_trace(go.Scatterpolar(
                r=dept_df['治疗成功率'].tolist(),
                theta=dept_df['科室'].tolist(),
                fill='toself',
                name='治疗成功率'
            ))
            
            fig2.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title='各科室准确率对比',
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("暂无科室统计数据")
    
    st.divider()
    
    # ========== 3. 疾病分布 ==========
    st.markdown("### 🦠 疾病分布统计")
    
    disease_dist = records_manager.get_disease_distribution()
    
    if disease_dist:
        # 取前10个最常见疾病
        top_diseases = dict(list(disease_dist.items())[:10])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 疾病分布饼图
            disease_df = pd.DataFrame(list(top_diseases.items()), columns=['疾病', '数量'])
            
            fig3 = px.pie(
                disease_df,
                values='数量',
                names='疾病',
                title='Top 10 常见疾病分布',
                hole=0.4
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 疾病排行榜")
            for i, (disease, count) in enumerate(list(disease_dist.items())[:10], 1):
                percentage = (count / total_records) * 100
                st.markdown(f"""
                <div style='background-color: #f0f2f6; padding: 10px; margin: 5px 0; border-radius: 5px;'>
                    <strong>{i}. {disease}</strong><br>
                    治疗次数: {count} ({percentage:.1f}%)
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无疾病统计数据")
    
    st.divider()
    
    # ========== 4. 时间趋势分析 ==========
    st.markdown("### 📅 近30天治疗趋势")
    
    time_series = records_manager.get_time_series_stats(days=30)
    
    if time_series:
        ts_df = pd.DataFrame(time_series)
        
        if not ts_df.empty:
            # 计算成功率
            ts_df['success_rate'] = (ts_df['successful'] / ts_df['total'] * 100).fillna(0)
            ts_df['diagnosis_rate'] = (ts_df['diagnosis_correct'] / ts_df['total'] * 100).fillna(0)
            
            # 双轴折线图
            fig4 = go.Figure()
            
            # 治疗数量（柱状图）
            fig4.add_trace(go.Bar(
                x=ts_df['date'],
                y=ts_df['total'],
                name='治疗数量',
                marker_color='lightblue',
                yaxis='y'
            ))
            
            # 成功率折线
            fig4.add_trace(go.Scatter(
                x=ts_df['date'],
                y=ts_df['success_rate'],
                name='治疗成功率',
                line=dict(color='green', width=3),
                yaxis='y2'
            ))
            
            # 诊断准确率折线
            fig4.add_trace(go.Scatter(
                x=ts_df['date'],
                y=ts_df['diagnosis_rate'],
                name='诊断准确率',
                line=dict(color='orange', width=3),
                yaxis='y2'
            ))
            
            fig4.update_layout(
                title='每日治疗量与成功率趋势',
                xaxis=dict(title='日期'),
                yaxis=dict(
                    title='治疗数量',
                    side='left'
                ),
                yaxis2=dict(
                    title='成功率 (%)',
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig4, use_container_width=True)
            
            # 显示统计摘要
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_daily = ts_df['total'].mean()
                st.metric("日均治疗量", f"{avg_daily:.1f}")
            
            with col2:
                avg_success = ts_df['success_rate'].mean()
                st.metric("平均成功率", f"{avg_success:.1f}%")
            
            with col3:
                avg_diagnosis = ts_df['diagnosis_rate'].mean()
                st.metric("平均诊断率", f"{avg_diagnosis:.1f}%")
        else:
            st.info("近30天内暂无数据")
    else:
        st.info("暂无时间序列数据")
    
    st.divider()
    
    # ========== 5. 最近治疗记录摘要 ==========
    st.markdown("### 🕐 最近治疗记录")
    
    recent_records = records_manager.get_recent_records_summary(limit=20)
    
    if recent_records:
        recent_df = pd.DataFrame(recent_records)
        recent_df['治疗结果'] = recent_df['is_recovered'].apply(lambda x: '✅ 成功' if x else '❌ 失败')
        recent_df['诊断结果'] = recent_df['is_diagnosis_correct'].apply(lambda x: '✅ 正确' if x else '❌ 错误')
        
        display_df = recent_df[['timestamp', 'patient_name', 'disease', 'department', '诊断结果', '治疗结果']]
        display_df.columns = ['时间', '病人', '疾病', '科室', '诊断', '治疗']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无最近治疗记录")
