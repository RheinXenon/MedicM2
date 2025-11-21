"""
Agent Hospital - 模拟医院系统
实现论文 "Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents" 中的完整治疗循环
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from agents.nurse_agent import NurseAgent
from agents.evolving_doctor_agent import EvolvingDoctorAgent
from agents.consultation_agent import ConsultationCoordinatorAgent
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
        
        # 保存基础路径以便为每个科室创建子库
        self.case_base_path = case_base_path
        self.experience_base_path = experience_base_path
        
        # 为每个科室创建独立的病例库和经验库
        self.department_case_bases = {}
        self.department_experience_bases = {}
        
        total_cases = 0
        total_rules = 0
        for dept in self.departments:
            dept_id = dept['id']
            # 使用工厂方法创建，带缓存
            case_base = MedicalCaseBase.get_instance(
                storage_path=case_base_path,
                department_id=dept_id
            )
            experience_base = ExperienceBase.get_instance(
                storage_path=experience_base_path,
                department_id=dept_id
            )
            
            self.department_case_bases[dept_id] = case_base
            self.department_experience_bases[dept_id] = experience_base
            
            total_cases += len(case_base)
            total_rules += len(experience_base)
        
        print(f"✓ 科室病例库: 总计 {total_cases} 个案例")
        print(f"✓ 科室经验库: 总计 {total_rules} 条规则")
        
        # 初始化护士Agents
        self.triage_nurse = NurseAgent(name="李护士", specialty="分诊")
        self.examination_nurse = NurseAgent(name="陈护士", specialty="检查")
        self.consultation_agent = ConsultationCoordinatorAgent()
        print(f"✓ 初始化护士团队")
        
        # 初始化医生Agents，为每个医生注入科室特定的知识库
        self.doctor_agents = {}
        for dept in self.departments:
            dept_id = dept['id']
            doctor = EvolvingDoctorAgent(
                department_info=dept,
                retriever=self.retriever,
                case_base=self.department_case_bases[dept_id],
                experience_base=self.department_experience_bases[dept_id]
            )
            self.doctor_agents[dept['name']] = doctor
        print(f"✓ 初始化 {len(self.doctor_agents)} 位医生（科室隔离知识库）")
        
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
        模拟完整的病人治疗流程，支持多科室协同与会诊
        """
        if verbose:
            print("\n" + "=" * 60)
            print(f"开始治疗病人: {patient_agent.name}")
            print("=" * 60)

        treatment_record = {
            'patient_id': patient_agent.patient_id,
            'patient_name': patient_agent.name,
            'ground_truth_disease': patient_agent.disease,
            'events': [],
            'department_sessions': []
        }

        try:
            # 事件1: 疾病发作
            if verbose:
                print("\n[事件1] 疾病发作")
            treatment_record['events'].append({
                'event_type': 'disease_onset',
                'description': f"{patient_agent.name} 感到不适，决定就医"
            })

            # 事件2: 分诊
            if verbose:
                print("\n[事件2] 分诊")
            triage_result = self.triage_nurse.triage(patient_agent)
            treatment_record['triage'] = triage_result

            # 构建分诊队列
            pending_departments = [
                dept for dept in triage_result['recommended_departments']
                if dept in self.doctor_agents
            ] or [list(self.doctor_agents.keys())[0]]

            visited_departments = set()
            current_department = pending_departments.pop(0)
            consultation_requested = False
            latest_diagnosis = None
            last_doctor_agent = None
            aggregated_examinations = dict(patient_agent.examination_reports)

            # 事件3+: 挂号及多科室会诊
            session_index = 0
            while current_department:
                session_index += 1
                visited_departments.add(current_department)

                treatment_record['events'].append({
                    'event_type': 'registration',
                    'department': current_department,
                    'description': f"第{session_index}次挂号 - {current_department}"
                })

                session_record, diagnosis_result, doctor = self._run_department_session(
                    patient_agent,
                    current_department,
                    aggregated_examinations,
                    verbose
                )

                session_record['sequence'] = session_index
                treatment_record['department_sessions'].append(session_record)
                last_doctor_agent = doctor
                latest_diagnosis = diagnosis_result

                next_action = diagnosis_result.get('next_action', 'continue')
                suggested_departments = diagnosis_result.get('suggested_departments') or []
                self._enqueue_departments(
                    pending_departments,
                    suggested_departments,
                    visited_departments
                )

                treatment_record['events'].append({
                    'event_type': 'department_session',
                    'department': current_department,
                    'next_action': next_action,
                    'diagnosed_disease': diagnosis_result.get('disease')
                })

                if next_action == 'handoff':
                    current_department = self._pop_next_department(
                        pending_departments,
                        visited_departments
                    ) or self._get_fallback_department(visited_departments)
                    if current_department:
                        continue
                    break
                elif next_action == 'consult':
                    consultation_requested = True
                    current_department = self._pop_next_department(
                        pending_departments,
                        visited_departments
                    )
                    if current_department:
                        continue
                    break
                else:
                    break

            if latest_diagnosis is None:
                latest_diagnosis = {
                    'disease': '未生成诊断',
                    'diagnosis_reasoning': '流程异常，未得到医生诊断',
                    'treatment_plan': {},
                    'confidence': 'low'
                }

            # 事件6: 会诊或最终诊断
            if consultation_requested and len(treatment_record['department_sessions']) > 1:
                if verbose:
                    print("\n[会诊] 启动多科室联合会诊")
                final_diagnosis = self._run_consultation(patient_agent, treatment_record['department_sessions'])
            else:
                final_diagnosis = latest_diagnosis

            treatment_record['diagnosis'] = final_diagnosis

            if verbose:
                print(f"\n[最终诊断] {final_diagnosis.get('disease', '未知')} (置信度: {final_diagnosis.get('confidence', 'unknown')})")

            # 病人接收诊断与治疗
            patient_agent.receive_diagnosis(final_diagnosis)

            if verbose:
                print("\n[事件7] 治疗方案")

            treatment_plan = final_diagnosis.get('treatment_plan', {})
            patient_agent.receive_treatment(treatment_plan)

            treatment_record['events'].append({
                'event_type': 'medicine_dispensary',
                'treatment_plan': treatment_plan
            })

            # 事件8: 康复评估
            if verbose:
                print("\n[事件8] 康复评估")

            treatment_outcome = patient_agent.evaluate_treatment_outcome()
            treatment_record['outcome'] = treatment_outcome

            if verbose:
                if treatment_outcome['is_recovered']:
                    print("  ✓ 治疗成功！病人康复")
                else:
                    print("  ✗ 治疗效果不佳，可能需要复诊")

                if treatment_outcome['is_diagnosis_correct']:
                    print("  ✓ 诊断正确")
                else:
                    print("  ✗ 诊断错误")
                    print(f"    错误诊断: {final_diagnosis.get('disease')}")
                    print(f"    正确诊断: {patient_agent.disease}")

            if last_doctor_agent and latest_diagnosis:
                last_doctor_agent.learn_from_treatment_outcome(
                    patient_agent,
                    latest_diagnosis,
                    treatment_outcome
                )

            final_department = treatment_record['department_sessions'][-1]['department'] \
                if treatment_record['department_sessions'] else triage_result['recommended_departments'][0]
            self._update_stats(
                final_department,
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
        final_department = treatment_record['department_sessions'][-1]['department'] \
            if treatment_record['department_sessions'] else triage_result['recommended_departments'][0]
        treatment_record['department_case_base_size'] = len(
            self.department_case_bases.get(
                next((d['id'] for d in self.departments if d['name'] == final_department), None),
                []
            )
        ) if hasattr(self, 'department_case_bases') else 0

        if verbose:
            print("\n" + "=" * 60)
            print("治疗流程完成")
            print("=" * 60)

        return treatment_record
    
    def simulate_batch_treatments(
        self,
        patient_agents: List,
        verbose: bool = False,
        progress_interval: int = 10,
        record_callback=None
    ) -> List[Dict]:
        """
        批量模拟病人治疗
        
        Args:
            patient_agents: 病人Agent列表
            verbose: 是否打印详细信息
            progress_interval: 进度报告间隔
            record_callback: 每完成一个病人后的回调函数，接收 record 参数
            
        Returns:
            治疗记录列表
        """
        print(f"\n开始批量治疗 {len(patient_agents)} 位病人...")
        
        records = []
        for i, patient in enumerate(patient_agents, 1):
            record = self.simulate_patient_treatment(patient, verbose=verbose)
            records.append(record)
            
            # 调用回调函数（如果提供）
            if record_callback is not None:
                try:
                    record_callback(record)
                except Exception as e:
                    print(f"\n⚠️  保存记录时出错: {e}")
            
            if i % progress_interval == 0 or i == len(patient_agents):
                self._print_progress(i, len(patient_agents))
        
        print("\n批量治疗完成！")
        self.print_statistics()
        
        return records
    
    def _determine_examinations(
        self,
        patient_agent,
        doctor,
        existing_results: Optional[Dict] = None
    ) -> List[str]:
        """
        确定需要的检查项目
        简化版：根据症状推荐基本检查
        """
        existing_results = existing_results or {}
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
        
        # 最多3个检查，且避免重复
        filtered = []
        for exam in examinations:
            if exam not in filtered:
                filtered.append(exam)
        return filtered[:3]

    def _run_department_session(
        self,
        patient_agent,
        department_name: str,
        examination_results: Dict,
        verbose: bool
    ) -> Tuple[Dict, Dict, EvolvingDoctorAgent]:
        """执行单个科室的问诊-检查-诊断流程"""
        doctor = self.doctor_agents[department_name]

        if verbose:
            print(f"\n[科室] {department_name} - {doctor.name} 问诊")

        requested_exams = self._determine_examinations(
            patient_agent,
            doctor,
            examination_results
        )

        new_exams = []
        for exam_type in requested_exams:
            if exam_type in examination_results:
                continue
            if verbose:
                print(f"  → 进行检查: {exam_type}")
            exam_result = self.examination_nurse.conduct_examination(
                patient_agent,
                exam_type
            )
            examination_results[exam_type] = exam_result
            new_exams.append(exam_type)

        diagnosis_result = doctor.diagnose_with_evolution(
            patient_agent,
            examination_results
        )

        if verbose:
            print(f"  → 诊断结果: {diagnosis_result.get('disease', '未知')} (next_action={diagnosis_result.get('next_action', 'continue')})")

        session_record = {
            'department': department_name,
            'doctor': doctor.name,
            'requested_examinations': requested_exams,
            'new_examinations': new_exams,
            'diagnosis': diagnosis_result
        }

        return session_record, diagnosis_result, doctor

    def _run_consultation(
        self,
        patient_agent,
        department_sessions: List[Dict]
    ) -> Dict:
        """使用会诊Agent整合多科室意见"""
        consultation_result = self.consultation_agent.run_consultation(
            patient_agent,
            department_sessions
        )

        final_info = consultation_result.get('final_diagnosis', {})
        disease = final_info.get('primary') or '待定'
        differential = final_info.get('secondary', [])

        return {
            'disease': disease,
            'diagnosis_reasoning': consultation_result.get('rationale', ''),
            'differential_diagnosis': differential,
            'treatment_plan': consultation_result.get('treatment_plan', {}),
            'confidence': consultation_result.get('confidence', 'medium'),
            'key_factors': ['multi-department consultation'],
            'follow_up': consultation_result.get('follow_up', {}),
            'source': 'consultation',
            'thinking_process': consultation_result
        }

    def _enqueue_departments(
        self,
        queue: List[str],
        candidates: List[str],
        visited: set
    ):
        for dept in candidates:
            if dept in self.doctor_agents and dept not in visited and dept not in queue:
                queue.append(dept)

    def _pop_next_department(
        self,
        queue: List[str],
        visited: set
    ) -> Optional[str]:
        while queue:
            dept = queue.pop(0)
            if dept not in visited:
                return dept
        return None

    def _get_fallback_department(self, visited: set) -> Optional[str]:
        for dept in self.doctor_agents.keys():
            if dept not in visited:
                return dept
        return None
    
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
        
        print(f"\n病例库统计（按科室）:")
        for dept_id, case_base in self.department_case_bases.items():
            case_stats = case_base.get_stats()
            if case_stats['total_cases'] > 0:
                dept_name = next((d['name'] for d in self.departments if d['id'] == dept_id), dept_id)
                print(f"  {dept_name}: {case_stats['total_cases']} 个案例")
        
        print(f"\n经验库统计（按科室）:")
        for dept_id, exp_base in self.department_experience_bases.items():
            exp_stats = exp_base.get_stats()
            if exp_stats['total_rules'] > 0:
                dept_name = next((d['name'] for d in self.departments if d['id'] == dept_id), dept_id)
                print(f"  {dept_name}: {exp_stats['total_rules']} 条规则 (成功应用: {exp_stats['successful_applications']})")
        
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
    
    def get_department_stats(self) -> Dict:
        """获取所有科室的统计信息"""
        dept_stats = {}
        for dept_id in self.department_case_bases.keys():
            dept_name = next((d['name'] for d in self.departments if d['id'] == dept_id), dept_id)
            dept_stats[dept_name] = {
                'cases': len(self.department_case_bases[dept_id]),
                'rules': len(self.department_experience_bases[dept_id])
            }
        return dept_stats
    
    def __str__(self):
        total_cases = sum(len(cb) for cb in self.department_case_bases.values())
        total_rules = sum(len(eb) for eb in self.department_experience_bases.values())
        return (
            f"Agent Hospital\n"
            f"  科室数: {len(self.departments)}\n"
            f"  医生数: {len(self.doctor_agents)}\n"
            f"  病例库: {total_cases} 案例（科室隔离）\n"
            f"  经验库: {total_rules} 规则（科室隔离）\n"
            f"  总治疗: {self.stats['total_patients']} 病人"
        )
