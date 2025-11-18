"""
Agent Hospital 使用示例
展示如何使用模拟医院系统的各个组件
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator


def example_1_generate_patient():
    """示例1: 生成病人"""
    print("\n" + "=" * 60)
    print("示例1: 生成病人")
    print("=" * 60)
    
    # 初始化病人生成器
    patient_gen = PatientGenerator()
    
    # 生成一个随机病人
    patient = patient_gen.generate_patient()
    
    print(f"\n生成的病人信息:")
    print(f"  姓名: {patient.name}")
    print(f"  年龄: {patient.age}岁")
    print(f"  性别: {patient.gender}")
    print(f"  疾病: {patient.disease}")
    print(f"  症状数: {len(patient.symptoms)}")
    print(f"  主要症状: {', '.join(patient.symptoms[:5])}")
    
    return patient


def example_2_single_treatment():
    """示例2: 单个病人治疗"""
    print("\n" + "=" * 60)
    print("示例2: 单个病人治疗流程")
    print("=" * 60)
    
    # 初始化医院
    hospital = AgentHospital()
    
    # 生成病人
    patient_gen = PatientGenerator()
    patient = patient_gen.generate_patient()
    
    print(f"\n病人: {patient.name}, 疾病: {patient.disease}")
    
    # 治疗
    record = hospital.simulate_patient_treatment(patient, verbose=True)
    
    return record


def example_3_batch_treatment():
    """示例3: 批量病人治疗"""
    print("\n" + "=" * 60)
    print("示例3: 批量病人治疗")
    print("=" * 60)
    
    # 初始化
    hospital = AgentHospital()
    patient_gen = PatientGenerator()
    
    # 生成5个病人
    patients = patient_gen.generate_batch_patients(count=5)
    
    # 批量治疗
    records = hospital.simulate_batch_treatments(
        patients,
        verbose=False,
        progress_interval=2
    )
    
    return records


def example_4_department_treatment():
    """示例4: 特定科室病人治疗"""
    print("\n" + "=" * 60)
    print("示例4: 心脏科病人治疗")
    print("=" * 60)
    
    # 初始化
    hospital = AgentHospital()
    patient_gen = PatientGenerator()
    
    # 生成心脏科相关病人
    patients = patient_gen.generate_patients_by_department(
        department_keywords=['胸痛', '心悸', '心脏'],
        count=3
    )
    
    print(f"\n生成 {len(patients)} 个心脏科相关病人")
    
    # 治疗
    records = hospital.simulate_batch_treatments(
        patients,
        verbose=False
    )
    
    return records


def example_5_knowledge_growth():
    """示例5: 观察知识库增长"""
    print("\n" + "=" * 60)
    print("示例5: 知识库增长观察")
    print("=" * 60)
    
    # 初始化
    hospital = AgentHospital()
    patient_gen = PatientGenerator()
    
    # 初始状态
    initial_case_count = len(hospital.case_base)
    initial_rule_count = len(hospital.experience_base)
    
    print(f"\n初始状态:")
    print(f"  病例库: {initial_case_count} 案例")
    print(f"  经验库: {initial_rule_count} 规则")
    
    # 治疗10个病人
    patients = patient_gen.generate_batch_patients(count=10)
    hospital.simulate_batch_treatments(patients, verbose=False)
    
    # 最终状态
    final_case_count = len(hospital.case_base)
    final_rule_count = len(hospital.experience_base)
    
    print(f"\n治疗10个病人后:")
    print(f"  病例库: {final_case_count} 案例 (+{final_case_count - initial_case_count})")
    print(f"  经验库: {final_rule_count} 规则 (+{final_rule_count - initial_rule_count})")
    
    return hospital


def example_6_doctor_evolution():
    """示例6: 医生进化观察"""
    print("\n" + "=" * 60)
    print("示例6: 医生进化过程")
    print("=" * 60)
    
    # 初始化
    hospital = AgentHospital()
    patient_gen = PatientGenerator()
    
    # 获取心脏科医生
    cardiology_doctor = hospital.get_doctor("心脏科")
    
    print(f"\n观察医生: {cardiology_doctor.name}")
    
    # 第一轮：5个病人
    print("\n第一轮: 治疗5个病人")
    patients_1 = patient_gen.generate_patients_by_department(
        ['胸痛', '心悸'],
        count=5
    )
    hospital.simulate_batch_treatments(patients_1, verbose=False)
    
    stats_1 = cardiology_doctor.get_stats()
    print(f"  诊断准确率: {stats_1['diagnosis_accuracy']:.2%}")
    print(f"  治疗成功率: {stats_1['treatment_success_rate']:.2%}")
    
    # 第二轮：5个病人
    print("\n第二轮: 再治疗5个病人")
    patients_2 = patient_gen.generate_patients_by_department(
        ['胸痛', '心悸'],
        count=5
    )
    hospital.simulate_batch_treatments(patients_2, verbose=False)
    
    stats_2 = cardiology_doctor.get_stats()
    print(f"  诊断准确率: {stats_2['diagnosis_accuracy']:.2%}")
    print(f"  治疗成功率: {stats_2['treatment_success_rate']:.2%}")
    
    # 分析进化
    accuracy_improvement = stats_2['diagnosis_accuracy'] - stats_1['diagnosis_accuracy']
    print(f"\n进化效果:")
    print(f"  准确率提升: {accuracy_improvement:+.2%}")
    
    return hospital


def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print(" " * 25 + "Agent Hospital 使用示例")
    print("=" * 80)
    
    try:
        # 示例1: 生成病人
        example_1_generate_patient()
        
        input("\n按Enter继续下一个示例...")
        
        # 示例2: 单个治疗
        example_2_single_treatment()
        
        input("\n按Enter继续下一个示例...")
        
        # 示例3: 批量治疗
        example_3_batch_treatment()
        
        input("\n按Enter继续下一个示例...")
        
        # 示例4: 特定科室
        example_4_department_treatment()
        
        input("\n按Enter继续下一个示例...")
        
        # 示例5: 知识增长
        example_5_knowledge_growth()
        
        input("\n按Enter继续下一个示例...")
        
        # 示例6: 医生进化
        example_6_doctor_evolution()
        
        print("\n" + "=" * 80)
        print(" " * 30 + "所有示例完成!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Hospital 使用示例')
    parser.add_argument(
        '--example',
        type=str,
        default='all',
        choices=['1', '2', '3', '4', '5', '6', 'all'],
        help='选择要运行的示例'
    )
    
    args = parser.parse_args()
    
    if args.example == '1':
        example_1_generate_patient()
    elif args.example == '2':
        example_2_single_treatment()
    elif args.example == '3':
        example_3_batch_treatment()
    elif args.example == '4':
        example_4_department_treatment()
    elif args.example == '5':
        example_5_knowledge_growth()
    elif args.example == '6':
        example_6_doctor_evolution()
    else:
        run_all_examples()
