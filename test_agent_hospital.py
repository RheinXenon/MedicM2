"""
Agent Hospital 测试脚本
测试整个模拟医院系统的运行
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator


def test_single_patient_treatment():
    """测试单个病人的完整治疗流程"""
    print("\n" + "=" * 60)
    print("测试1: 单个病人治疗流程")
    print("=" * 60)
    
    # 初始化医院
    hospital = AgentHospital()
    
    # 初始化病人生成器
    patient_gen = PatientGenerator()
    
    # 生成一个病人
    print("\n生成测试病人...")
    patient = patient_gen.generate_patient()
    print(f"  病人: {patient.name}, {patient.age}岁, {patient.gender}")
    print(f"  疾病: {patient.disease}")
    print(f"  症状数: {len(patient.symptoms)}")
    
    # 进行治疗
    record = hospital.simulate_patient_treatment(patient, verbose=True)
    
    # 打印结果
    print("\n治疗结果:")
    print(f"  成功: {record['success']}")
    if 'outcome' in record:
        print(f"  康复: {record['outcome']['is_recovered']}")
        print(f"  诊断正确: {record['outcome']['is_diagnosis_correct']}")
    
    return record


def test_batch_treatment_small():
    """测试小批量病人治疗（10个）"""
    print("\n" + "=" * 60)
    print("测试2: 小批量治疗 (10个病人)")
    print("=" * 60)
    
    # 初始化医院
    hospital = AgentHospital()
    
    # 初始化病人生成器
    patient_gen = PatientGenerator()
    
    # 生成10个病人
    print("\n生成10个测试病人...")
    patients = patient_gen.generate_batch_patients(count=10)
    
    # 批量治疗
    records = hospital.simulate_batch_treatments(
        patients,
        verbose=False,
        progress_interval=5
    )
    
    # 保存记录
    output_dir = "./simulation_results"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"test_small_batch_{timestamp}.json")
    hospital.save_records(output_path)
    
    return records


def test_department_specific_treatment():
    """测试特定科室的病人治疗"""
    print("\n" + "=" * 60)
    print("测试3: 特定科室治疗 (心脏科)")
    print("=" * 60)
    
    # 初始化医院
    hospital = AgentHospital()
    
    # 初始化病人生成器
    patient_gen = PatientGenerator()
    
    # 生成心脏科相关病人
    print("\n生成心脏科相关病人...")
    cardiology_keywords = ['胸痛', '心悸', '呼吸困难', '心电图', '心脏']
    patients = patient_gen.generate_patients_by_department(
        department_keywords=cardiology_keywords,
        count=5
    )
    
    print(f"生成了 {len(patients)} 个心脏科相关病人")
    
    # 治疗
    records = hospital.simulate_batch_treatments(
        patients,
        verbose=False,
        progress_interval=2
    )
    
    return records


def test_doctor_evolution():
    """测试医生的进化学习过程"""
    print("\n" + "=" * 60)
    print("测试4: 医生进化测试")
    print("=" * 60)
    
    # 初始化医院
    hospital = AgentHospital()
    
    # 初始化病人生成器
    patient_gen = PatientGenerator()
    
    # 获取心脏科医生
    cardiology_doctor = hospital.get_doctor("心脏科")
    
    print(f"\n初始状态:")
    print(f"  {cardiology_doctor}")
    
    # 第一批：5个病人
    print(f"\n第一批：治疗5个病人...")
    patients_batch1 = patient_gen.generate_patients_by_department(
        department_keywords=['胸痛', '心悸', '心脏'],
        count=5
    )
    hospital.simulate_batch_treatments(patients_batch1, verbose=False)
    
    stats_after_batch1 = cardiology_doctor.get_stats()
    print(f"\n第一批后统计:")
    print(f"  治疗病人数: {stats_after_batch1['total_patients_treated']}")
    print(f"  诊断准确率: {stats_after_batch1['diagnosis_accuracy']:.2%}")
    print(f"  治疗成功率: {stats_after_batch1['treatment_success_rate']:.2%}")
    
    # 第二批：5个病人
    print(f"\n第二批：治疗5个病人...")
    patients_batch2 = patient_gen.generate_patients_by_department(
        department_keywords=['胸痛', '心悸', '心脏'],
        count=5
    )
    hospital.simulate_batch_treatments(patients_batch2, verbose=False)
    
    stats_after_batch2 = cardiology_doctor.get_stats()
    print(f"\n第二批后统计:")
    print(f"  治疗病人数: {stats_after_batch2['total_patients_treated']}")
    print(f"  诊断准确率: {stats_after_batch2['diagnosis_accuracy']:.2%}")
    print(f"  治疗成功率: {stats_after_batch2['treatment_success_rate']:.2%}")
    
    # 检查是否有进化
    accuracy_improvement = (stats_after_batch2['diagnosis_accuracy'] - 
                           stats_after_batch1['diagnosis_accuracy'])
    
    print(f"\n进化效果:")
    print(f"  诊断准确率提升: {accuracy_improvement:+.2%}")
    
    # 检查病例库和经验库
    case_stats = hospital.case_base.get_stats()
    exp_stats = hospital.experience_base.get_stats()
    
    print(f"\n知识积累:")
    print(f"  病例库案例数: {case_stats['total_cases']}")
    print(f"  经验库规则数: {exp_stats['total_rules']}")
    
    return {
        'batch1_stats': stats_after_batch1,
        'batch2_stats': stats_after_batch2,
        'accuracy_improvement': accuracy_improvement
    }


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Agent Hospital 系统测试套件")
    print("=" * 60)
    
    try:
        # 测试1: 单个病人
        test_single_patient_treatment()
        
        # 测试2: 小批量
        test_batch_treatment_small()
        
        # 测试3: 特定科室
        test_department_specific_treatment()
        
        # 测试4: 医生进化
        test_doctor_evolution()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Hospital 测试脚本')
    parser.add_argument(
        '--test',
        type=str,
        default='all',
        choices=['single', 'batch', 'department', 'evolution', 'all'],
        help='选择测试类型'
    )
    
    args = parser.parse_args()
    
    if args.test == 'single':
        test_single_patient_treatment()
    elif args.test == 'batch':
        test_batch_treatment_small()
    elif args.test == 'department':
        test_department_specific_treatment()
    elif args.test == 'evolution':
        test_doctor_evolution()
    else:
        run_all_tests()
