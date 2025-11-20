"""
Agent Hospital 控制台批量模拟脚本
支持命令行参数配置，自动保存详细治疗记录和统计信息

【新功能】实时保存：每完成一个病人就保存到 treatment_records.json
这样即使用户手动终止（Ctrl+C），已完成的记录也会保存！

使用示例：
    # 基础用法：模拟10个病人（默认）
    python run_simulation.py
    python run_simulation.py -n 10
    
    # 科室筛选：模拟20个心脏科病人
    python run_simulation.py -n 20 -d 心脏科
    
    # 显示详细过程：观察完整的8个事件治疗流程
    python run_simulation.py -n 5 -v
    
    # 大批量模拟：100个病人（不显示详细过程，实时保存到treatment_records.json）
    python run_simulation.py -n 100
    
    # 不保存详细记录：仅保存统计摘要
    python run_simulation.py -n 50 --no-save-details
    
    # 不实时保存到treatment_records.json（仅保存到simulation_results）
    python run_simulation.py -n 100 --no-realtime-save
    
    # 指定输出目录
    python run_simulation.py -n 20 -o ./my_results
    
    # 查看所有参数说明
    python run_simulation.py --help
"""
import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.agent_hospital import AgentHospital
from simulation.patient_generator import PatientGenerator
from frontend.utils.treatment_records_manager import TreatmentRecordsManager


class SimulationRunner:
    """医院模拟运行器"""
    
    def __init__(self, output_dir: str = "./simulation_results", enable_realtime_save: bool = True):
        """
        初始化模拟运行器
        
        Args:
            output_dir: 输出目录
            enable_realtime_save: 是否启用实时保存到 treatment_records.json
        """
        self.output_dir = output_dir
        self.enable_realtime_save = enable_realtime_save
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化治疗记录管理器（用于实时保存）
        if enable_realtime_save:
            self.records_manager = TreatmentRecordsManager()
        
        print("\n" + "=" * 70)
        print(" " * 15 + "🏥 Agent Hospital 模拟系统")
        print("=" * 70)
        
        # 初始化医院系统
        print("\n[1/2] 正在初始化医院系统...")
        self.hospital = AgentHospital()
        
        # 初始化病人生成器
        print("\n[2/2] 正在加载病人数据集...")
        self.patient_gen = PatientGenerator()
        
        print("\n" + "=" * 70)
        print("✅ 系统初始化完成！")
        print("=" * 70)
        print(f"\n📊 系统信息:")
        print(f"  • 科室数量: {len(self.hospital.departments)}")
        print(f"  • 医生数量: {len(self.hospital.doctor_agents)}")
        print(f"  • 数据集疾病: {len(self.patient_gen)} 种")
        print(f"  • 病例库: {sum(len(cb) for cb in self.hospital.department_case_bases.values())} 个案例")
        print(f"  • 经验库: {sum(len(eb) for eb in self.hospital.department_experience_bases.values())} 条规则")
        print()
    
    def run_batch_simulation(
        self,
        num_patients: int,
        department_filter: Optional[str] = None,
        verbose: bool = True,
        save_details: bool = True
    ) -> dict:
        """
        运行批量模拟
        
        Args:
            num_patients: 病人数量
            department_filter: 科室筛选（None表示全部科室）
            verbose: 是否显示详细治疗过程
            save_details: 是否保存详细记录
            
        Returns:
            模拟统计结果
        """
        print("\n" + "=" * 70)
        print(f"🎯 开始批量模拟")
        print("=" * 70)
        print(f"  • 病人数量: {num_patients}")
        print(f"  • 科室筛选: {department_filter or '全部科室'}")
        print(f"  • 详细日志: {'是' if verbose else '否'}")
        print(f"  • 保存详细记录: {'是' if save_details else '否'}")
        print(f"  • 实时保存到 treatment_records.json: {'是' if self.enable_realtime_save else '否'}")
        print()
        
        # 生成病人
        print(f"\n📋 正在生成 {num_patients} 位病人...")
        
        if department_filter and department_filter != "全部":
            # 根据科室筛选生成病人
            dept_keywords = self._get_department_keywords(department_filter)
            if dept_keywords:
                patients = self.patient_gen.generate_patients_by_department(
                    department_keywords=dept_keywords,
                    count=num_patients
                )
            else:
                patients = self.patient_gen.generate_batch_patients(count=num_patients)
        else:
            patients = self.patient_gen.generate_batch_patients(count=num_patients)
        
        print(f"✅ 病人生成完成")
        
        # 开始治疗
        print(f"\n🏥 开始治疗流程...\n")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 批量治疗
        # 定义实时保存回调函数
        def save_record_callback(record):
            if self.enable_realtime_save:
                self.records_manager.save_record(record)
        
        records = self.hospital.simulate_batch_treatments(
            patients,
            verbose=verbose,
            progress_interval=max(1, num_patients // 10),  # 动态调整进度报告间隔
            record_callback=save_record_callback if self.enable_realtime_save else None
        )
        
        # 记录结束时间
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 收集统计信息
        stats = self._collect_statistics(records, duration)
        
        # 保存结果
        if save_details:
            self._save_simulation_results(records, stats, department_filter)
        
        # 显示总结
        self._print_summary(stats)
        
        return stats
    
    def _get_department_keywords(self, department_name: str) -> List[str]:
        """获取科室关键词"""
        for dept in self.hospital.departments:
            if dept['name'] == department_name:
                return dept.get('keywords', [])
        return []
    
    def _collect_statistics(self, records: List[dict], duration: float) -> dict:
        """收集统计信息"""
        total = len(records)
        successful = sum(1 for r in records if r.get('success') and r.get('outcome', {}).get('is_recovered'))
        correct_diagnosis = sum(1 for r in records if r.get('success') and r.get('outcome', {}).get('is_diagnosis_correct'))
        
        # 按科室统计
        by_department = {}
        for record in records:
            if not record.get('success'):
                continue
            
            triage = record.get('triage', {})
            dept = triage.get('recommended_departments', ['未知'])[0]
            
            if dept not in by_department:
                by_department[dept] = {
                    'total': 0,
                    'recovered': 0,
                    'correct_diagnosis': 0
                }
            
            by_department[dept]['total'] += 1
            if record.get('outcome', {}).get('is_recovered'):
                by_department[dept]['recovered'] += 1
            if record.get('outcome', {}).get('is_diagnosis_correct'):
                by_department[dept]['correct_diagnosis'] += 1
        
        # 按疾病统计
        by_disease = {}
        for record in records:
            disease = record.get('ground_truth_disease', '未知')
            if disease not in by_disease:
                by_disease[disease] = {
                    'total': 0,
                    'recovered': 0,
                    'correct_diagnosis': 0
                }
            
            by_disease[disease]['total'] += 1
            if record.get('success') and record.get('outcome', {}).get('is_recovered'):
                by_disease[disease]['recovered'] += 1
            if record.get('success') and record.get('outcome', {}).get('is_diagnosis_correct'):
                by_disease[disease]['correct_diagnosis'] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_patients': total,
            'successful_treatments': successful,
            'correct_diagnoses': correct_diagnosis,
            'treatment_success_rate': successful / total if total > 0 else 0,
            'diagnosis_accuracy': correct_diagnosis / total if total > 0 else 0,
            'by_department': by_department,
            'by_disease': by_disease,
            'knowledge_base_stats': {
                'total_cases': sum(len(cb) for cb in self.hospital.department_case_bases.values()),
                'total_rules': sum(len(eb) for eb in self.hospital.department_experience_bases.values())
            }
        }
    
    def _save_simulation_results(self, records: List[dict], stats: dict, department_filter: Optional[str]):
        """保存模拟结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细记录
        records_file = os.path.join(
            self.output_dir,
            f"simulation_{timestamp}.json"
        )
        
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': timestamp,
                    'department_filter': department_filter,
                    'num_patients': len(records)
                },
                'statistics': stats,
                'treatment_records': records
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细记录已保存: {records_file}")
        
        # 保存统计摘要
        summary_file = os.path.join(
            self.output_dir,
            f"summary_{timestamp}.json"
        )
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"💾 统计摘要已保存: {summary_file}")
        
        # 生成可读的文本报告
        report_file = os.path.join(
            self.output_dir,
            f"report_{timestamp}.txt"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write(" " * 20 + "Agent Hospital 模拟报告\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"生成时间: {stats['timestamp']}\n")
            f.write(f"运行时长: {stats['duration_seconds']:.2f} 秒\n")
            f.write(f"科室筛选: {department_filter or '全部科室'}\n\n")
            
            f.write("总体统计:\n")
            f.write(f"  • 总病人数: {stats['total_patients']}\n")
            f.write(f"  • 治疗成功: {stats['successful_treatments']} ({stats['treatment_success_rate']:.1%})\n")
            f.write(f"  • 诊断正确: {stats['correct_diagnoses']} ({stats['diagnosis_accuracy']:.1%})\n\n")
            
            f.write("知识库统计:\n")
            f.write(f"  • 病例库: {stats['knowledge_base_stats']['total_cases']} 个案例\n")
            f.write(f"  • 经验库: {stats['knowledge_base_stats']['total_rules']} 条规则\n\n")
            
            if stats['by_department']:
                f.write("各科室统计:\n")
                for dept, dept_stats in stats['by_department'].items():
                    total = dept_stats['total']
                    recovered = dept_stats['recovered']
                    correct = dept_stats['correct_diagnosis']
                    f.write(f"  • {dept}:\n")
                    f.write(f"      - 病人数: {total}\n")
                    f.write(f"      - 治疗成功率: {recovered}/{total} ({recovered/total:.1%})\n")
                    f.write(f"      - 诊断准确率: {correct}/{total} ({correct/total:.1%})\n")
        
        print(f"💾 文本报告已保存: {report_file}")
    
    def _print_summary(self, stats: dict):
        """打印统计摘要"""
        print("\n" + "=" * 70)
        print(" " * 25 + "📊 模拟总结")
        print("=" * 70)
        print(f"\n⏱️  运行时长: {stats['duration_seconds']:.2f} 秒")
        print(f"👥 总病人数: {stats['total_patients']}")
        print(f"✅ 治疗成功: {stats['successful_treatments']} ({stats['treatment_success_rate']:.1%})")
        print(f"🎯 诊断正确: {stats['correct_diagnoses']} ({stats['diagnosis_accuracy']:.1%})")
        
        print(f"\n📚 知识库增长:")
        print(f"  • 病例库: {stats['knowledge_base_stats']['total_cases']} 个案例")
        print(f"  • 经验库: {stats['knowledge_base_stats']['total_rules']} 条规则")
        
        if stats['by_department']:
            print(f"\n🏥 各科室表现:")
            for dept, dept_stats in sorted(stats['by_department'].items(), 
                                          key=lambda x: x[1]['total'], 
                                          reverse=True):
                total = dept_stats['total']
                recovered = dept_stats['recovered']
                correct = dept_stats['correct_diagnosis']
                print(f"  • {dept}: {total}人 | 成功率 {recovered/total:.1%} | 准确率 {correct/total:.1%}")
        
        print("\n" + "=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Agent Hospital 控制台批量模拟系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 模拟10个病人（全部科室，实时保存到treatment_records.json）
  python run_simulation.py -n 10
  
  # 模拟20个心脏科病人，显示详细过程
  python run_simulation.py -n 20 -d 心脏科 -v
  
  # 模拟100个病人，每完成一个就保存（即使中断也有记录）
  python run_simulation.py -n 100
  
  # 模拟50个病人，不实时保存（仅保存到simulation_results）
  python run_simulation.py -n 50 --no-realtime-save
  
  # 模拟100个病人，不保存详细记录（仅保存统计摘要）
  python run_simulation.py -n 100 --no-save-details
        """
    )
    
    parser.add_argument(
        '-n', '--num-patients',
        type=int,
        default=10,
        help='病人数量（默认: 10）'
    )
    
    parser.add_argument(
        '-d', '--department',
        type=str,
        default=None,
        choices=[None, '全部', '心脏科', '神经科', '肿瘤科', '呼吸科', '消化科'],
        help='科室筛选（默认: 全部科室）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='显示详细治疗过程'
    )
    
    parser.add_argument(
        '--no-verbose',
        action='store_true',
        default=False,
        help='不显示详细治疗过程（默认）'
    )
    
    parser.add_argument(
        '--save-details',
        action='store_true',
        default=True,
        help='保存详细治疗记录（默认）'
    )
    
    parser.add_argument(
        '--no-save-details',
        action='store_true',
        default=False,
        help='不保存详细治疗记录'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='./simulation_results',
        help='输出目录（默认: ./simulation_results）'
    )
    
    parser.add_argument(
        '--no-realtime-save',
        action='store_true',
        default=False,
        help='不实时保存到 treatment_records.json（默认会实时保存）'
    )
    
    args = parser.parse_args()
    
    # 处理verbose参数
    verbose = args.verbose and not args.no_verbose
    
    # 处理save_details参数
    save_details = args.save_details and not args.no_save_details
    
    # 处理realtime_save参数
    enable_realtime_save = not args.no_realtime_save
    
    try:
        # 创建模拟运行器
        runner = SimulationRunner(
            output_dir=args.output_dir,
            enable_realtime_save=enable_realtime_save
        )
        
        # 运行模拟
        stats = runner.run_batch_simulation(
            num_patients=args.num_patients,
            department_filter=args.department,
            verbose=verbose,
            save_details=save_details
        )
        
        print("\n✅ 模拟完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，程序退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
