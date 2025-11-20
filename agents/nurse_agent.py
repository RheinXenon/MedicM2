"""
护士 Agent - Agent Hospital 系统
负责分诊(Triage)和医学检查(Medical Examination)
"""
from typing import Dict, List, Optional
from .base_agent import BaseAgent
from utils.prompt_templates import NURSE_TRIAGE_TEMPLATE, NURSE_EXAMINATION_TEMPLATE
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
        
        # 构建科室别名映射表
        self.department_alias_map = self._build_alias_map()
        
        # 分诊统计
        self.triage_stats = {
            'total_triages': 0,
            'out_of_range_count': 0,  # 越界次数
            'fallback_count': 0  # 回退到关键词匹配的次数
        }
    
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
                    "id": "cardiology",
                    "name": "心脏科",
                    "keywords": ["胸痛", "心悸", "呼吸困难", "心电图"],
                    "department_aliases": ["心内科"]
                },
                {
                    "id": "neurology",
                    "name": "神经科",
                    "keywords": ["头痛", "头晕", "抽搐", "麻木"],
                    "department_aliases": ["神经内科"]
                },
                {
                    "id": "pulmonology",
                    "name": "呼吸科",
                    "keywords": ["咳嗽", "咳痰", "气短", "呼吸困难"],
                    "department_aliases": ["呼吸内科"]
                },
                {
                    "id": "gastroenterology",
                    "name": "消化科",
                    "keywords": ["腹痛", "腹泻", "便秘", "呕吐"],
                    "department_aliases": ["消化内科"]
                },
                {
                    "id": "oncology",
                    "name": "肿瘤科",
                    "keywords": ["肿块", "消瘦", "疼痛", "出血"],
                    "department_aliases": ["肿瘤内科"]
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
        
        # 构建可用科室列表（用于LLM约束）
        available_depts = "\n".join([
            f"- {dept['name']} ({dept.get('name_en', '')})"
            for dept in self.departments_knowledge
        ])
        
        # 使用提示词模板
        prompt = NURSE_TRIAGE_TEMPLATE.format(
            patient_name=patient_agent.name,
            patient_age=patient_agent.age,
            patient_gender=patient_agent.gender,
            chief_complaint=chief_complaint,
            symptoms_text=symptoms_text,
            available_departments_list=available_depts,
            department_list=dept_list
        )
        
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
                    ] if department_scores else [self.departments_knowledge[0]['name']],
                    "reasoning": response,
                    "suggestions": "请前往推荐科室就诊"
                }
        except:
            # 解析失败，使用关键词匹配结果
            triage_result = {
                "recommended_departments": [
                    d['department'] for d in department_scores[:2]
                ] if department_scores else [self.departments_knowledge[0]['name']],
                "reasoning": response,
                "suggestions": "请前往推荐科室就诊"
            }
        
        # 合法性校验和别名映射
        self.triage_stats['total_triages'] += 1
        validated_depts = []
        
        for dept_name in triage_result.get('recommended_departments', []):
            # 尝试映射别名到标准名称
            mapped_dept = self._map_department_name(dept_name)
            
            if mapped_dept:
                validated_depts.append(mapped_dept)
            else:
                # 越界：推荐了不存在的科室
                self.triage_stats['out_of_range_count'] += 1
                self.add_thinking_step(
                    "科室越界",
                    f"LLM推荐的科室 '{dept_name}' 不在配置中，将回退到关键词匹配"
                )
        
        # 如果所有推荐都无效，使用关键词匹配结果
        if not validated_depts:
            self.triage_stats['fallback_count'] += 1
            if department_scores:
                validated_depts = [department_scores[0]['department']]
            else:
                validated_depts = [self.departments_knowledge[0]['name']]
            
            self.add_thinking_step(
                "回退到关键词匹配",
                f"使用关键词匹配结果: {validated_depts[0]}"
            )
        
        triage_result['recommended_departments'] = validated_depts
        
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
        
        # 使用提示词模板
        prompt = NURSE_EXAMINATION_TEMPLATE.format(
            examination_type=examination_type,
            patient_name=patient_agent.name,
            patient_age=patient_agent.age,
            patient_gender=patient_agent.gender,
            patient_disease=patient_agent.disease,
            symptoms=', '.join(patient_agent.symptoms[:10])
        )
        
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
    
    def _build_alias_map(self) -> Dict[str, str]:
        """构建科室别名到标准名称的映射"""
        alias_map = {}
        for dept in self.departments_knowledge:
            standard_name = dept['name']
            # 标准名称映射到自己
            alias_map[standard_name] = standard_name
            alias_map[standard_name.lower()] = standard_name
            
            # 添加所有别名
            for alias in dept.get('department_aliases', []):
                alias_map[alias] = standard_name
                alias_map[alias.lower()] = standard_name
        
        return alias_map
    
    def _map_department_name(self, dept_name: str) -> Optional[str]:
        """映射科室名称（包括别名）到标准名称"""
        # 尝试直接匹配
        if dept_name in self.department_alias_map:
            return self.department_alias_map[dept_name]
        
        # 尝试小写匹配
        if dept_name.lower() in self.department_alias_map:
            return self.department_alias_map[dept_name.lower()]
        
        # 尝试模糊匹配
        for alias, standard in self.department_alias_map.items():
            if dept_name in alias or alias in dept_name:
                return standard
        
        return None
    
    def get_triage_stats(self) -> Dict:
        """获取分诊统计信息"""
        stats = dict(self.triage_stats)
        if stats['total_triages'] > 0:
            stats['out_of_range_rate'] = stats['out_of_range_count'] / stats['total_triages']
            stats['fallback_rate'] = stats['fallback_count'] / stats['total_triages']
        else:
            stats['out_of_range_rate'] = 0.0
            stats['fallback_rate'] = 0.0
        return stats
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"护士: {self.name} ({self.specialty})"
    
    def __repr__(self):
        return f"<NurseAgent: {self.name}, {self.specialty}>"
