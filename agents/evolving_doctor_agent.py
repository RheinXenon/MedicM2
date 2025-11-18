"""
可进化的医生 Agent - Agent Hospital 系统
集成医疗病例库和经验库，能够从治疗中不断学习和进化
"""
from typing import Dict, List, Optional
from .base_agent import BaseAgent
from knowledge.medical_case_base import MedicalCaseBase
from knowledge.experience_base import ExperienceBase
from utils.prompt_templates import DOCTOR_DIAGNOSIS_TEMPLATE


class EvolvingDoctorAgent(BaseAgent):
    """
    可进化的医生 Agent
    根据论文 "Agent Hospital" 中的 MedAgent-Zero 方法实现
    """
    
    def __init__(
        self,
        department_info: Dict,
        retriever,
        case_base: MedicalCaseBase,
        experience_base: ExperienceBase,
        **kwargs
    ):
        """
        初始化可进化医生 Agent
        
        Args:
            department_info: 科室信息字典
            retriever: 知识检索器
            case_base: 医疗病例库
            experience_base: 经验库
            **kwargs: 传递给基类的其他参数
        """
        name = f"{department_info['name']}医生"
        role = department_info['description']
        
        super().__init__(name=name, role=role, **kwargs)
        
        self.department_id = department_info['id']
        self.department_name = department_info['name']
        self.department_name_en = department_info['name_en']
        self.specialties = department_info['specialties']
        self.keywords = department_info['keywords']
        self.retriever = retriever
        
        # 核心组件：病例库和经验库
        self.case_base = case_base
        self.experience_base = experience_base
        
        # 统计信息
        self.stats = {
            'total_patients_treated': 0,
            'successful_treatments': 0,
            'failed_treatments': 0,
            'correct_diagnoses': 0,
            'incorrect_diagnoses': 0
        }
    
    def diagnose_with_evolution(
        self,
        patient_agent,
        examination_results: Dict = None
    ) -> Dict:
        """
        诊断病人并记录结果用于进化
        
        Args:
            patient_agent: 病人Agent对象
            examination_results: 医学检查结果
            
        Returns:
            诊断结果
        """
        self.clear_thinking_process()
        self.add_thinking_step(
            "开始诊断",
            f"{self.name} 开始对病人 {patient_agent.name} 进行诊断..."
        )
        
        # 1. 收集病人信息
        symptoms = patient_agent.symptoms
        medical_history = patient_agent.medical_history
        
        self.add_thinking_step(
            "信息收集",
            f"症状数: {len(symptoms)}, 病史条目: {len(medical_history)}"
        )
        
        # 2. 从病例库检索相似案例
        self.add_thinking_step(
            "检索病例库",
            "正在查找相似的成功案例..."
        )
        
        similar_cases = self.case_base.retrieve_similar_cases(
            query_symptoms=symptoms,
            query_history=medical_history,
            department=self.department_name,
            top_k=3
        )
        
        self.add_thinking_step(
            "病例库检索结果",
            f"找到 {len(similar_cases)} 个相似案例"
        )
        
        # 3. 从经验库检索适用规则
        self.add_thinking_step(
            "检索经验库",
            "正在查找适用的经验规则..."
        )
        
        applicable_rules = self.experience_base.retrieve_applicable_rules(
            symptoms=symptoms,
            medical_history=medical_history,
            department=self.department_name,
            top_k=3
        )
        
        self.add_thinking_step(
            "经验库检索结果",
            f"找到 {len(applicable_rules)} 条适用规则"
        )
        
        # 4. 从知识库检索专业知识
        self.add_thinking_step(
            "检索知识库",
            "正在从医学知识库检索相关内容..."
        )
        
        query = " ".join(symptoms[:5])
        retrieved_docs = self.retriever.retrieve(
            query=query,
            department_id=self.department_id,
            top_k=3
        )
        
        knowledge_context = self.retriever.format_retrieved_knowledge(retrieved_docs)
        
        # 5. 构建诊断提示词
        self.add_thinking_step(
            "综合分析",
            "整合病例库、经验库和知识库的信息进行诊断..."
        )
        
        # 格式化病例参考
        case_references = self._format_case_references(similar_cases)
        
        # 格式化经验规则
        rule_references = self.experience_base.format_rules_for_reference(
            applicable_rules
        )
        
        # 格式化检查结果
        examination_text = self._format_examination_results(examination_results)
        
        # 构建完整提示词
        prompt = f"""你是一位{self.department_name}的专科医生，正在为病人进行诊断。

【病人信息】
年龄：{patient_agent.age}岁
性别：{patient_agent.gender}
主诉症状：{', '.join(symptoms[:10])}
既往病史：{', '.join(medical_history) if medical_history else '无'}

【医学检查结果】
{examination_text}

【参考：相似成功案例】
{case_references}

【参考：经验规则】
{rule_references}

【参考：专业知识】
{knowledge_context}

请根据以上信息进行诊断。你的诊断应包括：
1. 最可能的疾病诊断
2. 诊断依据和推理过程
3. 鉴别诊断（如有必要）
4. 推荐的治疗方案
5. 置信度评估（高/中/低）

请以JSON格式输出：
{{
    "disease": "疾病名称",
    "diagnosis_reasoning": "诊断推理过程",
    "differential_diagnosis": ["鉴别诊断1", "鉴别诊断2"],
    "treatment_plan": {{
        "medications": ["药物1", "药物2"],
        "procedures": ["治疗措施1", "治疗措施2"],
        "recommendations": "其他建议"
    }},
    "confidence": "high/medium/low",
    "key_factors": ["关键诊断因素1", "关键诊断因素2"]
}}
"""
        
        # 6. 生成诊断
        system_message = f"你是一位专业的{self.department_name}医生，擅长{self.department_name_en}领域的疾病诊断和治疗。"
        
        response = self.generate_response(prompt, system_message)
        
        # 7. 解析诊断结果
        diagnosis_result = self._parse_diagnosis_response(response)
        
        # 8. 添加元数据
        diagnosis_result['doctor_name'] = self.name
        diagnosis_result['department'] = self.department_name
        diagnosis_result['patient_id'] = patient_agent.patient_id
        diagnosis_result['used_similar_cases'] = len(similar_cases) > 0
        diagnosis_result['used_experience_rules'] = len(applicable_rules) > 0
        diagnosis_result['similar_cases_count'] = len(similar_cases)
        diagnosis_result['applied_rules_count'] = len(applicable_rules)
        
        # 记录应用的规则ID（用于后续反馈）
        diagnosis_result['applied_rule_ids'] = [
            rule['rule_id'] for rule in applicable_rules
        ]
        
        self.add_thinking_step(
            "诊断完成",
            f"诊断为: {diagnosis_result.get('disease', '未知')}"
        )
        
        diagnosis_result['thinking_process'] = self.get_thinking_process()
        
        return diagnosis_result
    
    def learn_from_treatment_outcome(
        self,
        patient_agent,
        diagnosis_result: Dict,
        treatment_outcome: Dict
    ):
        """
        从治疗结果中学习
        
        Args:
            patient_agent: 病人Agent对象
            diagnosis_result: 诊断结果
            treatment_outcome: 治疗结果
        """
        self.stats['total_patients_treated'] += 1
        
        is_recovered = treatment_outcome['is_recovered']
        is_diagnosis_correct = treatment_outcome['is_diagnosis_correct']
        
        # 更新统计
        if is_diagnosis_correct:
            self.stats['correct_diagnoses'] += 1
        else:
            self.stats['incorrect_diagnoses'] += 1
        
        if is_recovered:
            self.stats['successful_treatments'] += 1
            
            # 成功案例：添加到病例库
            self._add_successful_case_to_base(
                patient_agent,
                diagnosis_result,
                treatment_outcome
            )
            
            # 更新应用规则的成功记录
            if 'applied_rule_ids' in diagnosis_result:
                for rule_id in diagnosis_result['applied_rule_ids']:
                    self.experience_base.record_rule_application(
                        rule_id,
                        success=True
                    )
        else:
            self.stats['failed_treatments'] += 1
            
            # 失败案例：生成经验规则
            if not is_diagnosis_correct:
                self._learn_from_failure(
                    patient_agent,
                    diagnosis_result,
                    treatment_outcome
                )
            
            # 更新应用规则的失败记录
            if 'applied_rule_ids' in diagnosis_result:
                for rule_id in diagnosis_result['applied_rule_ids']:
                    self.experience_base.record_rule_application(
                        rule_id,
                        success=False
                    )
    
    def _add_successful_case_to_base(
        self,
        patient_agent,
        diagnosis_result: Dict,
        treatment_outcome: Dict
    ):
        """将成功案例添加到病例库"""
        case_data = {
            'patient_info': {
                'age': patient_agent.age,
                'gender': patient_agent.gender,
                'patient_id': patient_agent.patient_id
            },
            'symptoms': patient_agent.symptoms,
            'medical_history': patient_agent.medical_history,
            'examination_results': patient_agent.examination_reports,
            'diagnosis': {
                'disease': diagnosis_result.get('disease'),
                'reasoning': diagnosis_result.get('diagnosis_reasoning'),
                'confidence': diagnosis_result.get('confidence')
            },
            'treatment': diagnosis_result.get('treatment_plan', {}),
            'outcome': 'successful',
            'department': self.department_name,
            'doctor_name': self.name,
            'ground_truth_disease': patient_agent.disease
        }
        
        case_id = self.case_base.add_case(case_data)
        
        self.add_thinking_step(
            "学习成功案例",
            f"案例 {case_id} 已添加到病例库"
        )
    
    def _learn_from_failure(
        self,
        patient_agent,
        diagnosis_result: Dict,
        treatment_outcome: Dict
    ):
        """从失败中学习，生成经验规则"""
        failed_case = {
            'case_id': f"FAILED_{patient_agent.patient_id}",
            'patient_info': {
                'age': patient_agent.age,
                'gender': patient_agent.gender
            },
            'symptoms': patient_agent.symptoms,
            'medical_history': patient_agent.medical_history,
            'department': self.department_name
        }
        
        correct_diagnosis = patient_agent.disease
        wrong_diagnosis = diagnosis_result.get('disease', '未知')
        
        self.add_thinking_step(
            "反思失败案例",
            f"错误诊断为 {wrong_diagnosis}，实际为 {correct_diagnosis}"
        )
        
        # 使用LLM生成经验规则
        rule_id = self.experience_base.generate_rule_from_failure(
            failed_case,
            correct_diagnosis,
            wrong_diagnosis,
            llm_generator=self  # 传递自己作为LLM生成器
        )
        
        if rule_id:
            self.add_thinking_step(
                "生成经验规则",
                f"规则 {rule_id} 已添加到经验库"
            )
    
    def _format_case_references(self, cases: List[Dict]) -> str:
        """格式化病例参考"""
        if not cases:
            return "暂无相似成功案例"
        
        text_parts = []
        for i, case in enumerate(cases, 1):
            similarity = case.get('similarity_score', 0)
            diagnosis = case.get('diagnosis', {})
            
            text_parts.append(f"""
案例 {i} (相似度: {similarity:.2f}):
- 病人: {case['patient_info']['age']}岁, {case['patient_info']['gender']}
- 主要症状: {', '.join(case['symptoms'][:5])}
- 诊断: {diagnosis.get('disease', '未记录')}
- 治疗结果: 成功康复
""")
        
        return "\n".join(text_parts)
    
    def _format_examination_results(
        self,
        examination_results: Dict
    ) -> str:
        """格式化检查结果"""
        if not examination_results:
            return "暂无检查结果"
        
        text_parts = []
        for exam_type, result in examination_results.items():
            text_parts.append(f"\n{exam_type}:")
            if isinstance(result, dict):
                if 'findings' in result:
                    text_parts.append(f"  发现: {result['findings']}")
                if 'conclusion' in result:
                    text_parts.append(f"  结论: {result['conclusion']}")
            else:
                text_parts.append(f"  {result}")
        
        return "\n".join(text_parts)
    
    def _parse_diagnosis_response(self, response: str) -> Dict:
        """解析诊断响应"""
        try:
            import re
            import json
            
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                diagnosis = json.loads(json_match.group())
            else:
                # 如果没有JSON，创建默认结构
                diagnosis = {
                    'disease': '需进一步检查',
                    'diagnosis_reasoning': response,
                    'differential_diagnosis': [],
                    'treatment_plan': {
                        'medications': [],
                        'procedures': [],
                        'recommendations': response
                    },
                    'confidence': 'low',
                    'key_factors': []
                }
            
            return diagnosis
            
        except Exception as e:
            print(f"解析诊断响应失败: {e}")
            return {
                'disease': '解析错误',
                'diagnosis_reasoning': response,
                'differential_diagnosis': [],
                'treatment_plan': {},
                'confidence': 'low',
                'key_factors': []
            }
    
    def get_stats(self) -> Dict:
        """获取医生的统计信息"""
        stats = dict(self.stats)
        
        # 计算诊断准确率
        total_diagnoses = stats['correct_diagnoses'] + stats['incorrect_diagnoses']
        if total_diagnoses > 0:
            stats['diagnosis_accuracy'] = stats['correct_diagnoses'] / total_diagnoses
        else:
            stats['diagnosis_accuracy'] = 0
        
        # 计算治疗成功率
        total_treatments = stats['successful_treatments'] + stats['failed_treatments']
        if total_treatments > 0:
            stats['treatment_success_rate'] = stats['successful_treatments'] / total_treatments
        else:
            stats['treatment_success_rate'] = 0
        
        return stats
    
    def __str__(self):
        stats = self.get_stats()
        return (
            f"{self.name} - {self.department_name}\n"
            f"治疗病人数: {stats['total_patients_treated']}, "
            f"诊断准确率: {stats['diagnosis_accuracy']:.2%}, "
            f"治疗成功率: {stats['treatment_success_rate']:.2%}"
        )
    
    def __repr__(self):
        return f"<EvolvingDoctorAgent: {self.name}, {self.department_name}>"
