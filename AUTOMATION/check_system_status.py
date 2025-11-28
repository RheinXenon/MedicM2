"""
系统状态检查脚本
帮助快速了解当前系统的知识库状态和历史表现
"""
import os
import json
from datetime import datetime


def check_knowledge_bases():
    """检查知识库状态"""
    print("\n" + "=" * 60)
    print("📚 知识库状态")
    print("=" * 60)
    
    # 检查病例库
    case_base_path = "../knowledge/case_base"
    if os.path.exists(case_base_path):
        total_cases = 0
        for dept_dir in os.listdir(case_base_path):
            dept_path = os.path.join(case_base_path, dept_dir)
            if os.path.isdir(dept_path):
                cases = [f for f in os.listdir(dept_path) if f.endswith('.json') and f != 'stats.json']
                if cases:
                    print(f"  病例库 - {dept_dir}: {len(cases)} 个案例")
                    total_cases += len(cases)
        if total_cases == 0:
            print("  病例库: 空（尚未积累案例）")
        else:
            print(f"  总计: {total_cases} 个案例")
    else:
        print("  病例库: 未创建")
    
    # 检查经验库
    exp_base_path = "../knowledge/experience_base"
    if os.path.exists(exp_base_path):
        total_rules = 0
        for dept_dir in os.listdir(exp_base_path):
            dept_path = os.path.join(exp_base_path, dept_dir)
            if os.path.isdir(dept_path):
                rules = [f for f in os.listdir(dept_path) if f.endswith('.json') and f != 'stats.json']
                if rules:
                    print(f"  经验库 - {dept_dir}: {len(rules)} 条规则")
                    total_rules += len(rules)
        if total_rules == 0:
            print("  经验库: 空（尚未积累规则）")
        else:
            print(f"  总计: {total_rules} 条规则")
    else:
        print("  经验库: 未创建")


def check_simulation_results():
    """检查历史模拟结果"""
    print("\n" + "=" * 60)
    print("📊 历史模拟结果")
    print("=" * 60)
    
    results_path = "../simulation_results"
    if not os.path.exists(results_path):
        print("  暂无历史模拟记录")
        return
    
    summaries = sorted([f for f in os.listdir(results_path) if f.startswith('summary_')])
    
    if not summaries:
        print("  暂无历史模拟记录")
        return
    
    print(f"  共 {len(summaries)} 次模拟记录\n")
    
    # 显示最近5次
    recent = summaries[-5:]
    print("  最近5次模拟:")
    print("  " + "-" * 50)
    
    for summary_file in recent:
        try:
            with open(os.path.join(results_path, summary_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', '未知')[:16]
            total = data.get('total_patients', 0)
            accuracy = data.get('diagnosis_accuracy', 0) * 100
            success_rate = data.get('treatment_success_rate', 0) * 100
            
            print(f"  {timestamp} | {total}人 | 准确率: {accuracy:.1f}% | 成功率: {success_rate:.1f}%")
        except Exception as e:
            print(f"  {summary_file}: 读取失败 ({e})")
    
    print("  " + "-" * 50)
    
    # 计算趋势
    if len(summaries) >= 2:
        try:
            with open(os.path.join(results_path, summaries[-1]), 'r', encoding='utf-8') as f:
                latest = json.load(f)
            with open(os.path.join(results_path, summaries[0]), 'r', encoding='utf-8') as f:
                earliest = json.load(f)
            
            latest_acc = latest.get('diagnosis_accuracy', 0) * 100
            earliest_acc = earliest.get('diagnosis_accuracy', 0) * 100
            change = latest_acc - earliest_acc
            
            if change > 0:
                print(f"\n  📈 趋势: 准确率从 {earliest_acc:.1f}% → {latest_acc:.1f}% (+{change:.1f}%)")
            elif change < 0:
                print(f"\n  📉 趋势: 准确率从 {earliest_acc:.1f}% → {latest_acc:.1f}% ({change:.1f}%)")
            else:
                print(f"\n  ➡️ 趋势: 准确率保持在 {latest_acc:.1f}%")
        except:
            pass


def check_improvement_log():
    """检查改进日志"""
    print("\n" + "=" * 60)
    print("📝 改进日志状态")
    print("=" * 60)
    
    log_path = "./improvement_log.md"  # 同目录
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计改进次数
        improvements = content.count("## 改进 #")
        print(f"  已记录 {improvements} 次改进尝试")
        
        # 查找最新改进
        import re
        matches = list(re.finditer(r'## 改进 #(\d+)', content))
        if matches:
            last = matches[-1]
            print(f"  最新: 改进 #{last.group(1)}")
    else:
        print("  改进日志文件不存在")


def main():
    print("\n" + "=" * 60)
    print("🏥 MedicM2 系统状态检查")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_knowledge_bases()
    check_simulation_results()
    check_improvement_log()
    
    print("\n" + "=" * 60)
    print("✅ 状态检查完成")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 运行模拟 (从项目根目录): python run_simulation.py -n 20")
    print("  - 查看详细日志: python run_simulation.py -n 5 -v")
    print("  - 检查状态 (从AUTOMATION目录): python check_system_status.py")
    print()


if __name__ == "__main__":
    main()
