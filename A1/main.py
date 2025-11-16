"""
智能多模态医疗诊断系统 - 主程序
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
        print("=" * 80)
        print("智能多模态医疗诊断系统")
        print("=" * 80)
        print()
        
        # 加载科室配置
        self.departments = self._load_departments(config_path)
        print(f"✓ 已加载 {len(self.departments)} 个科室配置")
        
        # 初始化向量存储
        self.vector_store = VectorStore(persist_directory="./chroma_db")
        
        # 初始化知识库
        knowledge_base_path = "./knowledge_base"
        self.vector_store.initialize_all_departments(
            knowledge_base_path, 
            self.departments
        )
        
        # 初始化检索器
        self.retriever = KnowledgeRetriever(self.vector_store)
        print("✓ 知识检索系统已就绪")
        
        # 初始化医生 Agents
        self.doctor_agents = []
        for dept in self.departments:
            agent = DoctorAgent(
                department_info=dept,
                retriever=self.retriever
            )
            self.doctor_agents.append(agent)
        print(f"✓ 已初始化 {len(self.doctor_agents)} 个专科医生 Agent")
        
        # 初始化会诊 Agent
        self.consultation_agent = ConsultationAgent()
        print("✓ 会诊系统已就绪")
        
        # 初始化多模态处理器
        self.multimodal_processor = MultimodalProcessor()
        print("✓ 多模态处理系统已就绪")
        
        print()
        print("=" * 80)
        print("系统初始化完成，可以开始诊断")
        print("=" * 80)
        print()
    
    def _load_departments(self, config_path: str) -> List[Dict]:
        """加载科室配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config['departments']
    
    def diagnose(
        self, 
        case_data: Dict,
        include_images: bool = True
    ) -> Dict:
        """
        对病例进行诊断
        
        Args:
            case_data: 病例数据字典
            include_images: 是否处理图像数据
            
        Returns:
            完整的诊断结果
        """
        print("\n" + "=" * 80)
        print("开始诊断流程")
        print("=" * 80 + "\n")
        
        # 1. 处理多模态输入（如果有图像）
        if include_images and 'images' in case_data and case_data['images']:
            print("正在分析医学影像...")
            enhanced_case = self.multimodal_processor.prepare_case_with_images(
                case_data,
                IMAGE_ANALYSIS_TEMPLATE
            )
            print("✓ 影像分析完成\n")
        else:
            enhanced_case = case_data
        
        # 2. 各科室医生独立诊断
        print("正在进行多科室诊断...")
        department_diagnoses = []
        
        for i, agent in enumerate(self.doctor_agents, 1):
            print(f"  [{i}/{len(self.doctor_agents)}] {agent.name} 正在诊断...")
            
            diagnosis = agent.diagnose(enhanced_case)
            department_diagnoses.append(diagnosis)
            
            if diagnosis['is_relevant']:
                print(f"      ✓ {agent.name} 发现相关症状 (相关度: {diagnosis['relevance_score']:.2f})")
            else:
                print(f"      - {agent.name} 未发现明显相关症状")
        
        print("\n✓ 多科室诊断完成\n")
        
        # 3. 会诊汇总
        print("正在进行会诊汇总...")
        consultation_result = self.consultation_agent.consult(
            enhanced_case,
            department_diagnoses
        )
        print("✓ 会诊汇总完成\n")
        
        # 4. 组合最终结果
        final_result = {
            'case_data': enhanced_case,
            'department_diagnoses': department_diagnoses,
            'consultation': consultation_result,
            'summary': self.consultation_agent.generate_summary(consultation_result)
        }
        
        print("=" * 80)
        print("诊断流程完成")
        print("=" * 80 + "\n")
        
        return final_result
    
    def print_diagnosis(self, result: Dict):
        """
        打印诊断结果
        
        Args:
            result: 诊断结果字典
        """
        print(result['summary'])
    
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
        
        print(f"诊断结果已保存到: {output_path}")


def main():
    """主函数 - 示例用法"""
    
    # 初始化系统
    system = MedicalDiagnosisSystem()
    
    # 示例病例1：疑似急性冠脉综合征
    case1 = {
        "patient_info": {
            "age": 55,
            "gender": "男",
            "chief_complaint": "持续胸痛3天，伴有呼吸困难"
        },
        "symptoms": [
            "胸部中央压榨性疼痛",
            "疼痛放射到左臂和下颌",
            "呼吸急促",
            "大汗淋漓",
            "恶心"
        ],
        "medical_history": [
            "高血压10年",
            "糖尿病5年",
            "吸烟史30年",
            "高脂血症"
        ],
        "vital_signs": {
            "血压": "160/95 mmHg",
            "心率": "102次/分",
            "体温": "37.2°C",
            "血氧饱和度": "94%",
            "呼吸频率": "22次/分"
        }
    }
    
    print("\n" + "=" * 80)
    print("示例病例：疑似急性冠脉综合征")
    print("=" * 80)
    
    # 执行诊断
    result1 = system.diagnose(case1, include_images=False)
    
    # 打印结果
    system.print_diagnosis(result1)
    
    # 保存结果
    system.save_diagnosis(result1, "./diagnosis_result_case1.json")
    
    print("\n" + "=" * 80)
    print("示例运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
