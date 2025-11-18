"""
Agent Hospital - 模拟医院系统
实现论文 "Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents" 中的完整治疗循环
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from agents.nurse_agent import NurseAgent
from agents.evolving_doctor_agent import EvolvingDoctorAgent
from knowledge.medical_case_base import MedicalCaseBase
from knowledge.experience_base import ExperienceBase
from rag.vector_store import VectorStore
from rag.retriever import KnowledgeRetriever


class AgentHospital:
    """
    Agent Hospital - 模拟医院
    
    实现8个主要事件的完整治疗循环：
    1. Disease Onset - 疾病发作
    2. Triage - 分诊
    3. Registration - 挂号
    4. Consultation - 问诊
    5. Medical Examination - 医学检查
    6. Diagnosis - 诊断
    7. Medicine Dispensary - 取药
    8. Convalescence - 康复评估
    """
    
    def __init__(
        self,
        config_path: str = "./config/departments.json",
        case_base_path: str = "./knowledge/case_base",
        experience_base_path: str = "./knowledge/experience_base"
    ):
        """
        初始化Agent Hospital
        
        Args:
            config_path: 科室配置文件路径
            case_base_path: 病例库存储路径
            experience_base_path: 经验库存储路径
        """
        print("=" * 60)
        print("初始化 Agent Hospital 模拟医院系统")
        print("=" * 60)
        
        # 加载科室配置
        self.departments = self._load_departments(config_path)
        print(f"✓ 加载 {len(self.departments)} 个科室")
        
        # 初始化知识库和检索器
        self.vector_store = VectorStore(persist_directory="./chroma_db")
        self.retriever = KnowledgeRetriever(self.vector_store)
        print(f"✓ 初始化知识库")
        
        # 初始化病例库和经验库
        self.case_base = MedicalCaseBase(storage_path=case_base_path)
        self.experience_base = ExperienceBase(storage_path=experience_base_path)
        print(f"✓ 病例库: {len(self.case_base)} 个案例")
        print(f"✓ 经验库: {len(self.experience_base)} 条规则")
        
        # 初始化护士Agents
        self.triage_nurse = NurseAgent(name="李护士", specialty="分诊")
        self.examination_nurse = NurseAgent(name="陈护士", specialty="检查")
        print(f"✓ 初始化护士团队")
        
        # 初始化医生Agents
        self.doctor_agents = {}
        for dept in self.departments:
            doctor = EvolvingDoctorAgent(
                department_info=dept,
                retriever=self.retriever,
                case_base=self.case_base,
                experience_base=self.experience_base
            )
            self.doctor_agents[dept['name']] = doctor
        print(f"✓ 初始化 {len(self.doctor_agents)} 位医生")
        
        # 治疗记录
        self.treatment_records = []
        
        # 统计信息
        self.stats = {
            'total_patients': 0,
            'successful_treatments': 0,
            'failed_treatments': 0,
            'by_department': {}
        }
        
        print("=" * 60)
        print("Agent Hospital 初始化完成！")
        print("=" * 60)
    
    def simulate_patient_treatment(
        self,
        patient_agent,
        verbose: bool = True
    ) -> Dict:
        """
        模拟完整的病人治疗流程
        
        Args:
            patient_agent: 病人Agent对象
            verbose: 是否打印详细信息
            
        Returns:
            治疗记录字典
        """
        if verbose:
            print("\n" + "=" * 60)
            print(f"开始治疗病人: {patient_agent.name}")
            print("=" * 60)
        
        treatment_record = {
            'patient_id': patient_agent.patient_id,
            'patient_name': patient_agent.name,
            'ground_truth_disease': patient_agent.disease,
            'events': []
        }
        
        try:
            # 事件1: 疾病发作 (Disease Onset)
            if verbose:
                print("\n[事件1] 疾病发作")
            treatment_record['events'].append({
                'event_type': 'disease_onset',
                'description': f"{patient_agent.name} 感到不适，决定就医"
            })
            
            # 事件2: 分诊 (Triage)
            if verbose:
                print("\n[事件2] 分诊")
            triage_result = self.triage_nurse.triage(patient_agent)
            treatment_record['triage'] = triage_result
            
            recommended_dept = triage_result['recommended_departments'][0]
            if verbose:
                print(f"  → 分诊护士推荐科室: {recommended_dept}")
            
            # 事件3: 挂号 (Registration)
            if verbose:
                print("\n[事件3] 挂号")
            treatment_record['events'].append({
                'event_type': 'registration',
                'department': recommended_dept,
                'description': f"病人挂号至 {recommended_dept}"
            })
            
            # 获取对应科室的医生
            if recommended_dept not in self.doctor_agents:
                # 如果推荐的科室不存在，使用第一个科室
                recommended_dept = list(self.doctor_agents.keys())[0]
                if verbose:
                    print(f"  ⚠ 科室不存在，转至 {recommended_dept}")
            
            doctor = self.doctor_agents[recommended_dept]
            
            # 事件4: 问诊 (Consultation)
            if verbose:
                print(f"\n[事件4] 问诊 - {doctor.name}")
            
            # 医生决定需要的检查
            examination_types = self._determine_examinations(
                patient_agent,
                doctor
            )
            
            if verbose:
                print(f"  → 需要进行检查: {', '.join(examination_types)}")
            
            # 事件5: 医学检查 (Medical Examination)
            if verbose:
                print("\n[事件5] 医学检查")
            
            examination_results = {}
            for exam_type in examination_types:
                exam_result = self.examination_nurse.conduct_examination(
                    patient_agent,
                    exam_type
                )
                examination_results[exam_type] = exam_result
                
                if verbose:
                    print(f"  → 完成 {exam_type}")
            
            treatment_record['examinations'] = examination_results
            
            # 事件6: 诊断 (Diagnosis)
            if verbose:
                print(f"\n[事件6] 诊断 - {doctor.name}")
            
            diagnosis_result = doctor.diagnose_with_evolution(
                patient_agent,
                examination_results
            )
            
            treatment_record['diagnosis'] = diagnosis_result
            
            if verbose:
                print(f"  → 诊断: {diagnosis_result.get('disease', '未知')}")
                print(f"  → 置信度: {diagnosis_result.get('confidence', 'unknown')}")
            
            # 病人接收诊断
            patient_reaction = patient_agent.receive_diagnosis(diagnosis_result)
            
            # 事件7: 取药/治疗 (Medicine Dispensary)
            if verbose:
                print("\n[事件7] 治疗方案")
            
            treatment_plan = diagnosis_result.get('treatment_plan', {})
            patient_agent.receive_treatment(treatment_plan)
            
            if verbose:
                medications = treatment_plan.get('medications', [])
                if medications:
                    print(f"  → 处方药物: {', '.join(medications[:3])}")
            
            treatment_record['events'].append({
                'event_type': 'medicine_dispensary',
                'treatment_plan': treatment_plan
            })
            
            # 事件8: 康复评估 (Convalescence)
            if verbose:
                print("\n[事件8] 康复评估")
            
            treatment_outcome = patient_agent.evaluate_treatment_outcome()
            treatment_record['outcome'] = treatment_outcome
            
            if verbose:
                if treatment_outcome['is_recovered']:
                    print(f"  ✓ 治疗成功！病人康复")
                else:
                    print(f"  ✗ 治疗效果不佳，可能需要复诊")
                
                if treatment_outcome['is_diagnosis_correct']:
                    print(f"  ✓ 诊断正确")
                else:
                    print(f"  ✗ 诊断错误")
                    print(f"    错误诊断: {diagnosis_result.get('disease')}")
                    print(f"    正确诊断: {patient_agent.disease}")
            
            # 医生从治疗结果中学习
            doctor.learn_from_treatment_outcome(
                patient_agent,
                diagnosis_result,
                treatment_outcome
            )
            
            # 更新统计
            self._update_stats(
                recommended_dept,
                treatment_outcome['is_recovered']
            )
            
            treatment_record['success'] = True
            
        except Exception as e:
            print(f"\n❌ 治疗过程出错: {e}")
            import traceback
            traceback.print_exc()
            treatment_record['success'] = False
            treatment_record['error'] = str(e)
        
        # 保存治疗记录
        self.treatment_records.append(treatment_record)
        
        if verbose:
            print("\n" + "=" * 60)
            print("治疗流程完成")
            print("=" * 60)
        
        return treatment_record
    
    def simulate_batch_treatments(
        self,
        patient_agents: List,
        verbose: bool = False,
        progress_interval: int = 10
    ) -> List[Dict]:
        """
        批量模拟病人治疗
        
        Args:
            patient_agents: 病人Agent列表
            verbose: 是否打印详细信息
            progress_interval: 进度报告间隔
            
        Returns:
            治疗记录列表
        """
        print(f"\n开始批量治疗 {len(patient_agents)} 位病人...")
        
        records = []
        for i, patient in enumerate(patient_agents, 1):
            record = self.simulate_patient_treatment(patient, verbose=verbose)
            records.append(record)
            
            if i % progress_interval == 0 or i == len(patient_agents):
                self._print_progress(i, len(patient_agents))
        
        print("\n批量治疗完成！")
        self.print_statistics()
        
        return records
    
    def _determine_examinations(
        self,
        patient_agent,
        doctor
    ) -> List[str]:
        """
        确定需要的检查项目
        简化版：根据症状推荐基本检查
        """
        examinations = ['血常规']  # 基本检查
        
        symptoms_text = ' '.join(patient_agent.symptoms)
        
        # 根据症状关键词添加检查
        if any(keyword in symptoms_text for keyword in ['心', '胸', '心悸', '心律']):
            examinations.append('心电图')
        
        if any(keyword in symptoms_text for keyword in ['头', '脑', '神经', '意识']):
            examinations.append('CT检查')
        
        if any(keyword in symptoms_text for keyword in ['呼吸', '肺', '咳嗽', '气促']):
            examinations.append('胸部X光')
        
        if any(keyword in symptoms_text for keyword in ['腹', '肝', '胃', '肠']):
            examinations.append('腹部B超')
        
        return examinations[:3]  # 最多3个检查
    
    def _update_stats(self, department: str, is_successful: bool):
        """更新统计信息"""
        self.stats['total_patients'] += 1
        
        if is_successful:
            self.stats['successful_treatments'] += 1
        else:
            self.stats['failed_treatments'] += 1
        
        if department not in self.stats['by_department']:
            self.stats['by_department'][department] = {
                'total': 0,
                'successful': 0,
                'failed': 0
            }
        
        dept_stats = self.stats['by_department'][department]
        dept_stats['total'] += 1
        if is_successful:
            dept_stats['successful'] += 1
        else:
            dept_stats['failed'] += 1
    
    def _print_progress(self, current: int, total: int):
        """打印进度"""
        percentage = (current / total) * 100
        success_rate = (self.stats['successful_treatments'] / 
                       max(self.stats['total_patients'], 1)) * 100
        
        print(f"\r进度: {current}/{total} ({percentage:.1f}%) | "
              f"成功率: {success_rate:.1f}%", end='', flush=True)
    
    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("Agent Hospital 统计信息")
        print("=" * 60)
        
        total = self.stats['total_patients']
        if total == 0:
            print("暂无治疗记录")
            return
        
        success_rate = (self.stats['successful_treatments'] / total) * 100
        
        print(f"\n总体统计:")
        print(f"  总病人数: {total}")
        print(f"  成功治疗: {self.stats['successful_treatments']} ({success_rate:.1f}%)")
        print(f"  治疗失败: {self.stats['failed_treatments']}")
        
        print(f"\n病例库统计:")
        case_stats = self.case_base.get_stats()
        print(f"  总案例数: {case_stats['total_cases']}")
        
        print(f"\n经验库统计:")
        exp_stats = self.experience_base.get_stats()
        print(f"  总规则数: {exp_stats['total_rules']}")
        print(f"  成功应用: {exp_stats['successful_applications']}")
        
        print(f"\n各科室统计:")
        for dept_name, doctor in self.doctor_agents.items():
            doctor_stats = doctor.get_stats()
            if doctor_stats['total_patients_treated'] > 0:
                print(f"\n  {dept_name}:")
                print(f"    治疗病人数: {doctor_stats['total_patients_treated']}")
                print(f"    诊断准确率: {doctor_stats['diagnosis_accuracy']:.1%}")
                print(f"    治疗成功率: {doctor_stats['treatment_success_rate']:.1%}")
        
        print("\n" + "=" * 60)
    
    def save_records(self, output_path: str):
        """保存治疗记录"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'treatment_records': self.treatment_records
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n治疗记录已保存至: {output_path}")
    
    def _load_departments(self, config_path: str) -> List[Dict]:
        """加载科室配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config['departments']
    
    def get_doctor(self, department_name: str) -> Optional[EvolvingDoctorAgent]:
        """获取指定科室的医生"""
        return self.doctor_agents.get(department_name)
    
    def __str__(self):
        return (
            f"Agent Hospital\n"
            f"  科室数: {len(self.departments)}\n"
            f"  医生数: {len(self.doctor_agents)}\n"
            f"  病例库: {len(self.case_base)} 案例\n"
            f"  经验库: {len(self.experience_base)} 规则\n"
            f"  总治疗: {self.stats['total_patients']} 病人"
        )
