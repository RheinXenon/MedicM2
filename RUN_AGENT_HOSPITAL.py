"""
Agent Hospital 主运行脚本
基于论文 "Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents" 实现
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" " * 20 + "Agent Hospital - 模拟医院系统")
    print(" " * 15 + "A Simulacrum of Hospital with Evolvable Medical Agents")
    print("=" * 80)
    
    # 1. 初始化系统
    print("\n[步骤 1/4] 初始化 Agent Hospital...")
    hospital = AgentHospital()
    
    # 2. 初始化病人生成器
    print("\n[步骤 2/4] 初始化病人生成器...")
    patient_gen = PatientGenerator()
    
    # 显示数据集统计
    stats = patient_gen.get_disease_statistics()
    print(f"  ✓ 数据集包含 {stats['total_diseases']} 种疾病")
    print(f"  ✓ 示例疾病: {', '.join(stats['sample_diseases'][:5])}...")
    
    # 3. 配置模拟参数
    print("\n[步骤 3/4] 配置模拟参数...")
    
    # 用户输入或使用默认值
    try:
        num_patients = int(input("\n请输入要生成的病人数量 (建议: 20-50，按Enter使用默认20): ") or "20")
    except:
        num_patients = 20
    
    print(f"\n将生成 {num_patients} 个病人进行模拟治疗")
    
    # 4. 开始模拟
    print("\n[步骤 4/4] 开始模拟治疗...")
    print("-" * 80)
    
    # 生成病人
    print(f"\n正在生成 {num_patients} 个病人...")
    patients = patient_gen.generate_batch_patients(count=num_patients)
    print(f"✓ 成功生成 {len(patients)} 个病人")
    
    # 显示病人样本
    print("\n病人样本:")
    for i, patient in enumerate(patients[:5], 1):
        print(f"  {i}. {patient.name} ({patient.age}岁, {patient.gender}) - {patient.disease}")
    if len(patients) > 5:
        print(f"  ... 还有 {len(patients) - 5} 个病人")
    
    # 批量治疗
    print(f"\n\n开始批量治疗 {num_patients} 个病人...")
    print("这可能需要一些时间，请耐心等待...\n")
    
    records = hospital.simulate_batch_treatments(
        patients,
        verbose=False,
        progress_interval=5
    )
    
    # 5. 显示结果
    print("\n\n" + "=" * 80)
    print(" " * 30 + "模拟结果总结")
    print("=" * 80)
    
    hospital.print_statistics()
    
    # 6. 保存结果
    output_dir = "./simulation_results"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"agent_hospital_simulation_{timestamp}.json")
    
    hospital.save_records(output_path)
    
    # 7. 显示知识库增长
    print("\n知识库增长情况:")
    case_stats = hospital.case_base.get_stats()
    exp_stats = hospital.experience_base.get_stats()
    
    print(f"  病例库:")
    print(f"    总案例数: {case_stats['total_cases']}")
    print(f"    各科室案例分布: {dict(case_stats['by_department'])}")
    
    print(f"\n  经验库:")
    print(f"    总规则数: {exp_stats['total_rules']}")
    print(f"    成功应用次数: {exp_stats['successful_applications']}")
    print(f"    失败应用次数: {exp_stats['failed_applications']}")
    
    # 8. 医生进化情况
    print("\n医生进化情况:")
    for dept_name, doctor in hospital.doctor_agents.items():
        stats = doctor.get_stats()
        if stats['total_patients_treated'] > 0:
            print(f"\n  {dept_name} - {doctor.name}:")
            print(f"    治疗病人数: {stats['total_patients_treated']}")
            print(f"    诊断准确率: {stats['diagnosis_accuracy']:.2%}")
            print(f"    治疗成功率: {stats['treatment_success_rate']:.2%}")
    
    print("\n" + "=" * 80)
    print(" " * 25 + "模拟完成！感谢使用！")
    print("=" * 80)
    
    # 9. 提示后续操作
    print("\n后续操作建议:")
    print(f"  1. 查看详细记录: {output_path}")
    print(f"  2. 运行测试脚本: python test_agent_hospital.py")
    print(f"  3. 继续训练医生: 再次运行本脚本，使用相同的病例库和经验库")
    print(f"  4. 分析医生进化: 观察诊断准确率随病人数量的变化")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        import traceback
        traceback.print_exc()
