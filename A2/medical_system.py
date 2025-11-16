"""
智能多模态医疗诊断系统 - 核心系统类
"""
import os
import json
from typing import Dict, List
from dotenv import load_dotenv

# 导入模块
from rag.vector_store import VectorStore
from rag.retriever import KnowledgeRetriever
from agents.doctor_agent import DoctorAgent
from agents.consultation_agent import ConsultationAgent
from utils.multimodal import MultimodalProcessor
from utils.prompt_templates import IMAGE_ANALYSIS_TEMPLATE

load_dotenv()


class MedicalDiagnosisSystem:
    """智能多模态医疗诊断系统"""
    
    def __init__(self, config_path: str = "./config/departments.json"):
        """
        初始化诊断系统
        
        Args:
            config_path: 科室配置文件路径
        """
        # 加载科室配置
        self.departments = self._load_departments(config_path)
        
        # 初始化向量存储
        self.vector_store = VectorStore(persist_directory="./chroma_db")
        
        # 初始化知识库（使用A1的知识库）
        knowledge_base_path = "../A1/knowledge_base"
        if os.path.exists(knowledge_base_path):
            self.vector_store.initialize_all_departments(
                knowledge_base_path, 
                self.departments
            )
        
        # 初始化检索器
        self.retriever = KnowledgeRetriever(self.vector_store)
        
        # 初始化医生 Agents
        self.doctor_agents = []
        for dept in self.departments:
            agent = DoctorAgent(
                department_info=dept,
                retriever=self.retriever
            )
            self.doctor_agents.append(agent)
        
        # 初始化会诊 Agent
        self.consultation_agent = ConsultationAgent()
        
        # 初始化多模态处理器
        self.multimodal_processor = MultimodalProcessor()
        
        self.is_initialized = True
    
    def _load_departments(self, config_path: str) -> List[Dict]:
        """加载科室配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config['departments']
    
    def diagnose(
        self, 
        case_data: Dict,
        include_images: bool = True,
        progress_callback=None
    ) -> Dict:
        """
        对病例进行诊断
        
        Args:
            case_data: 病例数据字典
            include_images: 是否处理图像数据
            progress_callback: 进度回调函数
            
        Returns:
            完整的诊断结果
        """
        if progress_callback:
            progress_callback("开始诊断流程...", 0)
        
        # 1. 处理多模态输入（如果有图像）
        if include_images and 'images' in case_data and case_data['images']:
            if progress_callback:
                progress_callback("正在分析医学影像...", 5)
            
            enhanced_case = self.multimodal_processor.prepare_case_with_images(
                case_data,
                IMAGE_ANALYSIS_TEMPLATE
            )
        else:
            enhanced_case = case_data
        
        # 2. 各科室医生独立诊断
        if progress_callback:
            progress_callback("正在进行多科室诊断...", 10)
        
        department_diagnoses = []
        total_agents = len(self.doctor_agents)
        
        for i, agent in enumerate(self.doctor_agents):
            if progress_callback:
                progress = 10 + int((i + 1) / total_agents * 60)
                progress_callback(f"[{i+1}/{total_agents}] {agent.name} 正在诊断...", progress)
            
            diagnosis = agent.diagnose(enhanced_case)
            department_diagnoses.append(diagnosis)
        
        # 3. 会诊汇总
        if progress_callback:
            progress_callback("正在进行会诊汇总...", 80)
        
        consultation_result = self.consultation_agent.consult(
            enhanced_case,
            department_diagnoses
        )
        
        # 4. 组合最终结果
        if progress_callback:
            progress_callback("生成最终报告...", 95)
        
        final_result = {
            'case_data': enhanced_case,
            'department_diagnoses': department_diagnoses,
            'consultation': consultation_result,
            'summary': self.consultation_agent.generate_summary(consultation_result)
        }
        
        if progress_callback:
            progress_callback("诊断完成!", 100)
        
        return final_result
    
    def get_department_names(self) -> List[str]:
        """获取所有科室名称"""
        return [dept['name'] for dept in self.departments]
    
    def save_diagnosis(self, result: Dict, output_path: str):
        """
        保存诊断结果到文件
        
        Args:
            result: 诊断结果字典
            output_path: 输出文件路径
        """
        # 将结果转换为可序列化的格式
        serializable_result = {
            'case_data': result['case_data'],
            'department_diagnoses': result['department_diagnoses'],
            'consultation': result['consultation'],
            'summary': result['summary']
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
