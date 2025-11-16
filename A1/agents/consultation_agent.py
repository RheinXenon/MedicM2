"""
会诊 Agent - 综合各科室意见给出最终诊断
"""
import os
from typing import Dict, List
from .base_agent import BaseAgent
from utils.prompt_templates import CONSULTATION_SUMMARY_TEMPLATE, CASE_INFO_TEMPLATE


class ConsultationAgent(BaseAgent):
    """会诊专家 Agent"""
    
    def __init__(self, **kwargs):
        """初始化会诊 Agent"""
        name = "会诊专家"
        role = "综合各科室意见，给出最终诊断和治疗方案"
        
        # 会诊 Agent 使用更低的温度以确保更准确的结论
        temperature = float(os.getenv("CONSULTATION_TEMPERATURE", 0.3))
        
        super().__init__(
            name=name, 
            role=role, 
            temperature=temperature,
            **kwargs
        )
    
    def consult(
        self, 
        case_data: Dict, 
        department_diagnoses: List[Dict]
    ) -> Dict:
        """
        进行会诊，综合各科室意见
        
        Args:
            case_data: 病例数据
            department_diagnoses: 各科室的诊断结果列表
            
        Returns:
            会诊结果字典
        """
        # 1. 格式化病例信息
        case_text = self._format_case_info(case_data)
        
        # 2. 格式化各科室诊断意见
        diagnoses_text = self._format_department_diagnoses(department_diagnoses)
        
        # 3. 构建会诊提示词
        prompt = CONSULTATION_SUMMARY_TEMPLATE.format(
            case_info=case_text,
            department_diagnoses=diagnoses_text
        )
        
        # 4. 生成会诊报告
        system_message = (
            "你是一位经验丰富的会诊专家，擅长综合分析各科室意见，"
            "给出准确的诊断结论和合理的治疗方案。你的决策基于循证医学，"
            "考虑全面，表述清晰专业。"
        )
        
        consultation_report = self.generate_response(prompt, system_message)
        
        # 5. 分析参与科室
        relevant_departments = [
            d for d in department_diagnoses 
            if d.get('is_relevant', False)
        ]
        
        # 6. 返回结果
        return {
            'consultation_report': consultation_report,
            'participating_departments': [
                d['department'] for d in relevant_departments
            ],
            'total_departments_consulted': len(relevant_departments),
            'all_diagnoses': department_diagnoses,
            'case_summary': case_text
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
    
    def _format_department_diagnoses(self, diagnoses: List[Dict]) -> str:
        """格式化各科室诊断意见"""
        formatted_text = ""
        
        # 先处理相关的科室
        relevant_diagnoses = [d for d in diagnoses if d.get('is_relevant', False)]
        irrelevant_diagnoses = [d for d in diagnoses if not d.get('is_relevant', False)]
        
        # 相关科室的详细意见
        if relevant_diagnoses:
            formatted_text += "=== 相关科室诊断意见 ===\n\n"
            
            for i, diag in enumerate(relevant_diagnoses, 1):
                formatted_text += f"### {i}. {diag['department']} ###\n"
                formatted_text += f"相关度评分: {diag.get('relevance_score', 0):.2f}\n"
                formatted_text += f"诊断置信度: {diag.get('confidence', 'unknown')}\n\n"
                formatted_text += f"{diag['diagnosis']}\n\n"
                formatted_text += "-" * 80 + "\n\n"
        
        # 不相关科室的简要说明
        if irrelevant_diagnoses:
            formatted_text += "=== 其他科室意见 ===\n\n"
            
            for diag in irrelevant_diagnoses:
                formatted_text += f"- {diag['department']}: {diag['diagnosis']}\n"
            
            formatted_text += "\n"
        
        return formatted_text
    
    def generate_summary(self, consultation_result: Dict) -> str:
        """
        生成简明的会诊摘要
        
        Args:
            consultation_result: 会诊结果
            
        Returns:
            会诊摘要文本
        """
        summary = "=" * 80 + "\n"
        summary += "多学科会诊报告摘要\n"
        summary += "=" * 80 + "\n\n"
        
        summary += f"参与科室: {', '.join(consultation_result['participating_departments'])}\n"
        summary += f"会诊科室数: {consultation_result['total_departments_consulted']}\n\n"
        
        summary += "=" * 80 + "\n"
        summary += "详细会诊报告\n"
        summary += "=" * 80 + "\n\n"
        
        summary += consultation_result['consultation_report']
        
        return summary
