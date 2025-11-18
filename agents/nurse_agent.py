"""
护士 Agent - Agent Hospital 系统
负责分诊(Triage)和医学检查(Medical Examination)
"""
from typing import Dict, List, Optional
from .base_agent import BaseAgent
import json


class NurseAgent(BaseAgent):
    """护士 Agent - 负责分诊和医学检查"""
    
    def __init__(
        self, 
        name: str,
        specialty: str = "综合护理",
        **kwargs
    ):
        """
        初始化护士 Agent
        
        Args:
            name: 护士姓名
            specialty: 专长 (如：分诊护士、检查护士等)
            **kwargs: 传递给基类的其他参数
        """
        role = f"{specialty}护士"
        super().__init__(name=name, role=role, **kwargs)
        
        self.specialty = specialty
        self.departments_knowledge = self._load_departments_knowledge()
    
    def _load_departments_knowledge(self) -> List[Dict]:
        """加载科室知识"""
        try:
            with open('./config/departments.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('departments', [])
        except:
            # 如果无法加载配置，返回默认科室
            return [
                {
                    "name": "心脏科",
                    "keywords": ["胸痛", "心悸", "呼吸困难", "心电图"]
                },
                {
                    "name": "神经科",
                    "keywords": ["头痛", "头晕", "抽搐", "麻木"]
                },
                {
                    "name": "呼吸科",
                    "keywords": ["咳嗽", "咳痰", "气短", "呼吸困难"]
                },
                {
                    "name": "消化科",
                    "keywords": ["腹痛", "腹泻", "便秘", "呕吐"]
                },
                {
                    "name": "肿瘤科",
                    "keywords": ["肿块", "消瘦", "疼痛", "出血"]
                }
            ]
    
    def triage(self, patient_agent) -> Dict:
        """
        分诊 - 根据病人症状推荐就诊科室
        
        Args:
            patient_agent: 病人Agent对象
            
        Returns:
            分诊结果字典
        """
        self.clear_thinking_process()
        self.add_thinking_step(
            "开始分诊",
            f"{self.name} 开始为病人 {patient_agent.name} 进行分诊..."
        )
        
        # 1. 获取病人主诉
        chief_complaint = patient_agent.describe_symptoms()
        
        self.add_thinking_step(
            "收集症状",
            f"病人主诉: {chief_complaint[:100]}..."
        )
        
        # 2. 分析症状，推荐科室
        symptoms_text = " ".join(patient_agent.symptoms)
        
        self.add_thinking_step(
            "分析症状",
            f"正在分析症状: {symptoms_text[:100]}..."
        )
        
        # 计算每个科室的相关度
        department_scores = []
        for dept in self.departments_knowledge:
            score = 0
            matched_keywords = []
            
            for keyword in dept.get('keywords', []):
                if keyword in symptoms_text or keyword in chief_complaint:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                department_scores.append({
                    'department': dept['name'],
                    'score': score,
                    'matched_keywords': matched_keywords
                })
        
        # 按相关度排序
        department_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 3. 使用LLM进行更精确的分诊判断
        if department_scores:
            top_departments = department_scores[:3]
            dept_list = "\n".join([
                f"- {d['department']} (匹配关键词: {', '.join(d['matched_keywords'])})"
                for d in top_departments
            ])
        else:
            dept_list = "未找到明显相关的科室"
        
        prompt = f"""你是一位经验丰富的分诊护士。现在有一位病人来就诊。

病人基本信息：
- 姓名：{patient_agent.name}
- 年龄：{patient_agent.age}岁
- 性别：{patient_agent.gender}

病人主诉：
{chief_complaint}

病人症状列表：
{symptoms_text}

根据初步分析，可能相关的科室：
{dept_list}

请你作为专业的分诊护士：
1. 综合分析病人的症状
2. 推荐最合适的1-2个就诊科室（按优先级排序）
3. 简要说明推荐理由
4. 如果需要，给出初步的就诊建议

请以JSON格式输出，包含以下字段：
{{
    "recommended_departments": ["科室1", "科室2"],
    "reasoning": "推荐理由",
    "suggestions": "就诊建议"
}}
"""
        
        response = self.generate_response(
            prompt,
            system_message="你是一位专业的分诊护士，擅长根据病人症状推荐合适的科室。"
        )
        
        # 解析LLM响应
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                triage_result = json.loads(json_match.group())
            else:
                # 如果没有JSON格式，创建默认结果
                triage_result = {
                    "recommended_departments": [
                        top_departments[0]['department']
                    ] if department_scores else ["综合内科"],
                    "reasoning": response,
                    "suggestions": "请前往推荐科室就诊"
                }
        except:
            # 解析失败，使用关键词匹配结果
            triage_result = {
                "recommended_departments": [
                    d['department'] for d in department_scores[:2]
                ] if department_scores else ["综合内科"],
                "reasoning": response,
                "suggestions": "请前往推荐科室就诊"
            }
        
        self.add_thinking_step(
            "分诊完成",
            f"推荐科室: {', '.join(triage_result['recommended_departments'])}"
        )
        
        # 4. 返回分诊结果
        result = {
            'patient_id': patient_agent.patient_id,
            'patient_name': patient_agent.name,
            'chief_complaint': chief_complaint,
            'recommended_departments': triage_result['recommended_departments'],
            'reasoning': triage_result['reasoning'],
            'suggestions': triage_result.get('suggestions', ''),
            'triage_nurse': self.name,
            'thinking_process': self.get_thinking_process()
        }
        
        return result
    
    def conduct_examination(
        self, 
        patient_agent,
        examination_type: str,
        doctor_order: Dict = None
    ) -> Dict:
        """
        进行医学检查
        
        Args:
            patient_agent: 病人Agent对象
            examination_type: 检查类型（如：血常规、心电图、CT等）
            doctor_order: 医生开具的检查单
            
        Returns:
            检查报告
        """
        self.clear_thinking_process()
        self.add_thinking_step(
            "开始检查",
            f"{self.name} 为病人 {patient_agent.name} 进行{examination_type}检查..."
        )
        
        # 根据病人的真实疾病生成相应的检查结果
        # 这里使用LLM + 医学知识生成合理的检查报告
        
        prompt = f"""你是一位专业的医学检查护士/技师。现在需要为病人生成{examination_type}检查报告。

病人信息：
- 姓名：{patient_agent.name}
- 年龄：{patient_agent.age}岁
- 性别：{patient_agent.gender}
- 实际疾病：{patient_agent.disease}（注意：这是ground truth，用于生成真实的检查结果）

病人症状：
{', '.join(patient_agent.symptoms[:10])}

请生成符合该疾病特征的{examination_type}检查报告。报告应该：
1. 包含该检查项目的常规指标
2. 如果该疾病会影响这些指标，应在报告中体现异常值
3. 使用专业的医学术语
4. 格式清晰，便于医生阅读

请以JSON格式输出，包含以下字段：
{{
    "examination_type": "{examination_type}",
    "findings": "检查发现（描述性文字）",
    "key_indicators": {{
        "指标1": "正常/异常值",
        "指标2": "正常/异常值"
    }},
    "conclusion": "检查结论"
}}

注意：生成的报告应该真实反映病人的疾病状态，帮助医生做出正确诊断。
"""
        
        response = self.generate_response(
            prompt,
            system_message=f"你是一位专业的医学检查技师，负责生成准确的{examination_type}检查报告。"
        )
        
        # 解析报告
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                examination_report = json.loads(json_match.group())
            else:
                examination_report = {
                    "examination_type": examination_type,
                    "findings": response,
                    "key_indicators": {},
                    "conclusion": "请医生根据临床情况综合判断"
                }
        except:
            examination_report = {
                "examination_type": examination_type,
                "findings": response,
                "key_indicators": {},
                "conclusion": "请医生根据临床情况综合判断"
            }
        
        # 添加元数据
        examination_report['patient_id'] = patient_agent.patient_id
        examination_report['patient_name'] = patient_agent.name
        examination_report['examination_nurse'] = self.name
        examination_report['ground_truth_disease'] = patient_agent.disease
        
        # 病人接受检查
        patient_agent.undergo_examination(examination_type, examination_report)
        
        self.add_thinking_step(
            "检查完成",
            f"{examination_type}检查完成，已生成报告"
        )
        
        examination_report['thinking_process'] = self.get_thinking_process()
        
        return examination_report
    
    def provide_nursing_care(self, patient_agent, care_type: str) -> str:
        """
        提供护理服务
        
        Args:
            patient_agent: 病人Agent对象
            care_type: 护理类型
            
        Returns:
            护理记录
        """
        self.add_thinking_step(
            "护理服务",
            f"为病人 {patient_agent.name} 提供{care_type}护理"
        )
        
        care_record = f"""护理记录：
护士：{self.name}
病人：{patient_agent.name}
护理类型：{care_type}
时间：{self._get_current_time()}
状态：护理完成
"""
        
        return care_record
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"护士: {self.name} ({self.specialty})"
    
    def __repr__(self):
        return f"<NurseAgent: {self.name}, {self.specialty}>"
