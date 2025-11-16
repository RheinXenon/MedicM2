"""
专科医生 Agent
"""
from typing import Dict, List
from .base_agent import BaseAgent
from utils.prompt_templates import DOCTOR_DIAGNOSIS_TEMPLATE, CASE_INFO_TEMPLATE


class DoctorAgent(BaseAgent):
    """专科医生 Agent"""
    
    def __init__(
        self, 
        department_info: Dict,
        retriever,
        **kwargs
    ):
        """
        初始化专科医生 Agent
        
        Args:
            department_info: 科室信息字典
            retriever: 知识检索器
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
    
    def is_relevant(self, case_data: Dict) -> tuple[bool, float]:
        """
        判断病例是否与本科室相关
        
        Args:
            case_data: 病例数据
            
        Returns:
            (是否相关, 相关度分数)
        """
        # 提取病例中的所有文本信息
        case_text = self._extract_case_text(case_data)
        case_text_lower = case_text.lower()
        
        # 计算关键词匹配度
        keyword_matches = sum(
            1 for keyword in self.keywords 
            if keyword.lower() in case_text_lower
        )
        
        relevance_score = keyword_matches / len(self.keywords) if self.keywords else 0
        
        # 如果相关度超过阈值，认为相关
        is_relevant = relevance_score > 0.1 or keyword_matches >= 2
        
        return is_relevant, relevance_score
    
    def _extract_case_text(self, case_data: Dict) -> str:
        """提取病例中的所有文本信息"""
        text_parts = []
        
        # 患者信息
        if 'patient_info' in case_data:
            info = case_data['patient_info']
            if 'chief_complaint' in info:
                text_parts.append(info['chief_complaint'])
        
        # 症状
        if 'symptoms' in case_data:
            if isinstance(case_data['symptoms'], list):
                text_parts.extend(case_data['symptoms'])
            else:
                text_parts.append(str(case_data['symptoms']))
        
        # 既往史
        if 'medical_history' in case_data:
            if isinstance(case_data['medical_history'], list):
                text_parts.extend(case_data['medical_history'])
            else:
                text_parts.append(str(case_data['medical_history']))
        
        # 图像分析摘要
        if 'image_summary' in case_data:
            text_parts.append(case_data['image_summary'])
        
        return ' '.join(text_parts)
    
    def diagnose(self, case_data: Dict) -> Dict:
        """
        对病例进行诊断
        
        Args:
            case_data: 病例数据
            
        Returns:
            诊断结果字典
        """
        # 1. 检查相关性
        is_relevant, relevance_score = self.is_relevant(case_data)
        
        if not is_relevant:
            return {
                'department': self.department_name,
                'department_id': self.department_id,
                'is_relevant': False,
                'relevance_score': relevance_score,
                'diagnosis': f"根据病例描述，暂未发现明显的{self.department_name}相关症状和体征。",
                'confidence': 'low'
            }
        
        # 2. 格式化病例信息
        case_text = self._format_case_info(case_data)
        
        # 3. 检索相关知识
        query = self._generate_retrieval_query(case_data)
        retrieved_docs = self.retriever.retrieve(
            query=query,
            department_id=self.department_id,
            top_k=5
        )
        knowledge_context = self.retriever.format_retrieved_knowledge(retrieved_docs)
        
        # 4. 构建诊断提示词
        prompt = DOCTOR_DIAGNOSIS_TEMPLATE.format(
            department_name=self.department_name,
            specialties='、'.join(self.specialties[:5]),
            case_info=case_text,
            knowledge_context=knowledge_context
        )
        
        # 5. 生成诊断
        system_message = f"你是一位专业的{self.department_name}医生，擅长{self.department_name_en}领域的疾病诊断和治疗。"
        
        diagnosis_text = self.generate_response(prompt, system_message)
        
        # 6. 返回结果
        return {
            'department': self.department_name,
            'department_id': self.department_id,
            'is_relevant': True,
            'relevance_score': relevance_score,
            'diagnosis': diagnosis_text,
            'confidence': self._assess_confidence(relevance_score),
            'retrieved_knowledge': retrieved_docs
        }
    
    def _format_case_info(self, case_data: Dict) -> str:
        """格式化病例信息"""
        # 患者信息
        patient_info = case_data.get('patient_info', {})
        age = patient_info.get('age', '未知')
        gender = patient_info.get('gender', '未知')
        chief_complaint = patient_info.get('chief_complaint', '未提供')
        
        # 症状
        symptoms = case_data.get('symptoms', [])
        if isinstance(symptoms, list):
            symptoms_text = '\n'.join(f"- {s}" for s in symptoms)
        else:
            symptoms_text = str(symptoms)
        
        # 既往史
        medical_history = case_data.get('medical_history', [])
        if isinstance(medical_history, list):
            history_text = '\n'.join(f"- {h}" for h in medical_history)
        else:
            history_text = str(medical_history)
        
        # 生命体征
        vital_signs = case_data.get('vital_signs', {})
        if vital_signs:
            vital_signs_text = '\n'.join(
                f"- {k}: {v}" for k, v in vital_signs.items()
            )
        else:
            vital_signs_text = "未提供"
        
        # 其他信息（如图像分析）
        additional_info = ""
        if 'image_summary' in case_data and case_data['image_summary']:
            additional_info = case_data['image_summary']
        
        # 使用模板格式化
        formatted_text = CASE_INFO_TEMPLATE.format(
            age=age,
            gender=gender,
            chief_complaint=chief_complaint,
            symptoms=symptoms_text,
            medical_history=history_text,
            vital_signs=vital_signs_text,
            additional_info=additional_info
        )
        
        return formatted_text
    
    def _generate_retrieval_query(self, case_data: Dict) -> str:
        """生成用于知识检索的查询"""
        query_parts = []
        
        # 主诉
        if 'patient_info' in case_data and 'chief_complaint' in case_data['patient_info']:
            query_parts.append(case_data['patient_info']['chief_complaint'])
        
        # 主要症状（取前3个）
        if 'symptoms' in case_data:
            symptoms = case_data['symptoms']
            if isinstance(symptoms, list):
                query_parts.extend(symptoms[:3])
            else:
                query_parts.append(str(symptoms))
        
        return ' '.join(query_parts)
    
    def _assess_confidence(self, relevance_score: float) -> str:
        """评估诊断置信度"""
        if relevance_score > 0.5:
            return 'high'
        elif relevance_score > 0.3:
            return 'medium'
        else:
            return 'low'
