"""
数据迁移脚本 - 将全局病例库和经验库迁移到科室隔离存储
用于Agent Hospital系统改造，实现科室内闭环演化
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class KnowledgeBaseMigrator:
    """知识库迁移工具"""
    
    def __init__(
        self,
        old_case_base_path: str = "./knowledge/case_base",
        old_experience_base_path: str = "./knowledge/experience_base",
        departments_config: str = "./config/departments.json",
        backup_suffix: str = "_backup"
    ):
        """
        初始化迁移工具
        
        Args:
            old_case_base_path: 旧病例库路径
            old_experience_base_path: 旧经验库路径
            departments_config: 科室配置文件路径
            backup_suffix: 备份后缀
        """
        self.old_case_base = old_case_base_path
        self.old_exp_base = old_experience_base_path
        self.backup_suffix = backup_suffix
        
        # 加载科室配置
        with open(departments_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.departments = config['departments']
        
        # 创建科室名称到ID的映射
        self.dept_name_to_id = {
            dept['name']: dept['id'] for dept in self.departments
        }
        
        # 添加别名映射
        for dept in self.departments:
            for alias in dept.get('department_aliases', []):
                self.dept_name_to_id[alias] = dept['id']
        
        # 迁移统计
        self.stats = {
            'cases_migrated': 0,
            'cases_by_department': {},
            'rules_migrated': 0,
            'rules_by_department': {},
            'errors': []
        }
    
    def backup_old_data(self):
        """备份旧数据"""
        print("=" * 60)
        print("步骤1: 备份原有数据")
        print("=" * 60)
        
        # 备份病例库
        if os.path.exists(self.old_case_base):
            backup_case_path = self.old_case_base + self.backup_suffix
            if not os.path.exists(backup_case_path):
                shutil.copytree(self.old_case_base, backup_case_path)
                print(f"✓ 病例库已备份至: {backup_case_path}")
            else:
                print(f"⚠ 备份已存在: {backup_case_path}")
        else:
            print("⚠ 旧病例库不存在，跳过备份")
        
        # 备份经验库
        if os.path.exists(self.old_exp_base):
            backup_exp_path = self.old_exp_base + self.backup_suffix
            if not os.path.exists(backup_exp_path):
                shutil.copytree(self.old_exp_base, backup_exp_path)
                print(f"✓ 经验库已备份至: {backup_exp_path}")
            else:
                print(f"⚠ 备份已存在: {backup_exp_path}")
        else:
            print("⚠ 旧经验库不存在，跳过备份")
        
        print()
    
    def migrate_case_base(self):
        """迁移病例库"""
        print("=" * 60)
        print("步骤2: 迁移病例库")
        print("=" * 60)
        
        if not os.path.exists(self.old_case_base):
            print("⚠ 旧病例库不存在，跳过迁移")
            print()
            return
        
        # 遍历所有病例文件
        case_files = [f for f in os.listdir(self.old_case_base) 
                     if f.endswith('.json') and f != 'stats.json']
        
        print(f"找到 {len(case_files)} 个病例文件")
        
        for filename in case_files:
            try:
                file_path = os.path.join(self.old_case_base, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    case = json.load(f)
                
                # 确定科室
                dept_name = case.get('department', '未知')
                dept_id = self.dept_name_to_id.get(dept_name)
                
                if dept_id:
                    # 创建科室子目录
                    dept_path = os.path.join(self.old_case_base, dept_id)
                    os.makedirs(dept_path, exist_ok=True)
                    
                    # 移动文件到科室子目录
                    new_path = os.path.join(dept_path, filename)
                    shutil.copy2(file_path, new_path)
                    
                    # 更新统计
                    self.stats['cases_migrated'] += 1
                    if dept_id not in self.stats['cases_by_department']:
                        self.stats['cases_by_department'][dept_id] = 0
                    self.stats['cases_by_department'][dept_id] += 1
                else:
                    # 科室未配置，记录错误
                    self.stats['errors'].append({
                        'type': 'case',
                        'file': filename,
                        'reason': f"未知科室: {dept_name}"
                    })
                    print(f"  ⚠ 跳过病例 {filename}: 未知科室 '{dept_name}'")
                    
            except Exception as e:
                self.stats['errors'].append({
                    'type': 'case',
                    'file': filename,
                    'reason': str(e)
                })
                print(f"  ✗ 迁移病例 {filename} 失败: {e}")
        
        print(f"\n✓ 病例迁移完成: {self.stats['cases_migrated']} 个")
        for dept_id, count in self.stats['cases_by_department'].items():
            dept_name = next((d['name'] for d in self.departments if d['id'] == dept_id), dept_id)
            print(f"  - {dept_name}: {count} 个")
        print()
    
    def migrate_experience_base(self):
        """迁移经验库"""
        print("=" * 60)
        print("步骤3: 迁移经验库")
        print("=" * 60)
        
        if not os.path.exists(self.old_exp_base):
            print("⚠ 旧经验库不存在，跳过迁移")
            print()
            return
        
        # 遍历所有规则文件
        rule_files = [f for f in os.listdir(self.old_exp_base) 
                     if f.endswith('.json') and f != 'stats.json']
        
        print(f"找到 {len(rule_files)} 个规则文件")
        
        for filename in rule_files:
            try:
                file_path = os.path.join(self.old_exp_base, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    rule = json.load(f)
                
                # 确定科室
                dept_name = rule.get('department', '未知')
                dept_id = self.dept_name_to_id.get(dept_name)
                
                if dept_id:
                    # 创建科室子目录
                    dept_path = os.path.join(self.old_exp_base, dept_id)
                    os.makedirs(dept_path, exist_ok=True)
                    
                    # 移动文件到科室子目录
                    new_path = os.path.join(dept_path, filename)
                    shutil.copy2(file_path, new_path)
                    
                    # 更新统计
                    self.stats['rules_migrated'] += 1
                    if dept_id not in self.stats['rules_by_department']:
                        self.stats['rules_by_department'][dept_id] = 0
                    self.stats['rules_by_department'][dept_id] += 1
                else:
                    # 科室未配置，记录错误
                    self.stats['errors'].append({
                        'type': 'rule',
                        'file': filename,
                        'reason': f"未知科室: {dept_name}"
                    })
                    print(f"  ⚠ 跳过规则 {filename}: 未知科室 '{dept_name}'")
                    
            except Exception as e:
                self.stats['errors'].append({
                    'type': 'rule',
                    'file': filename,
                    'reason': str(e)
                })
                print(f"  ✗ 迁移规则 {filename} 失败: {e}")
        
        print(f"\n✓ 经验规则迁移完成: {self.stats['rules_migrated']} 条")
        for dept_id, count in self.stats['rules_by_department'].items():
            dept_name = next((d['name'] for d in self.departments if d['id'] == dept_id), dept_id)
            print(f"  - {dept_name}: {count} 条")
        print()
    
    def cleanup_root_level_files(self):
        """清理根目录的旧文件"""
        print("=" * 60)
        print("步骤4: 清理根目录文件")
        print("=" * 60)
        
        # 移动根目录的病例文件到_unmigrated子目录
        if os.path.exists(self.old_case_base):
            unmigrated_path = os.path.join(self.old_case_base, "_unmigrated")
            root_files = [f for f in os.listdir(self.old_case_base) 
                         if f.endswith('.json') and f != 'stats.json' and 
                         os.path.isfile(os.path.join(self.old_case_base, f))]
            
            if root_files:
                os.makedirs(unmigrated_path, exist_ok=True)
                for f in root_files:
                    shutil.move(
                        os.path.join(self.old_case_base, f),
                        os.path.join(unmigrated_path, f)
                    )
                print(f"✓ 移动 {len(root_files)} 个未迁移的病例文件到 {unmigrated_path}")
        
        # 移动根目录的规则文件
        if os.path.exists(self.old_exp_base):
            unmigrated_path = os.path.join(self.old_exp_base, "_unmigrated")
            root_files = [f for f in os.listdir(self.old_exp_base) 
                         if f.endswith('.json') and f != 'stats.json' and 
                         os.path.isfile(os.path.join(self.old_exp_base, f))]
            
            if root_files:
                os.makedirs(unmigrated_path, exist_ok=True)
                for f in root_files:
                    shutil.move(
                        os.path.join(self.old_exp_base, f),
                        os.path.join(unmigrated_path, f)
                    )
                print(f"✓ 移动 {len(root_files)} 个未迁移的规则文件到 {unmigrated_path}")
        
        print()
    
    def generate_stats_report(self):
        """生成统计报告"""
        print("=" * 60)
        print("迁移统计报告")
        print("=" * 60)
        
        print(f"\n总体统计:")
        print(f"  病例迁移: {self.stats['cases_migrated']} 个")
        print(f"  规则迁移: {self.stats['rules_migrated']} 条")
        print(f"  错误数量: {len(self.stats['errors'])} 个")
        
        if self.stats['errors']:
            print(f"\n迁移错误:")
            for error in self.stats['errors'][:10]:  # 只显示前10个错误
                print(f"  - [{error['type']}] {error['file']}: {error['reason']}")
            if len(self.stats['errors']) > 10:
                print(f"  ... 还有 {len(self.stats['errors']) - 10} 个错误")
        
        # 保存完整报告
        report_path = f"./migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n完整报告已保存至: {report_path}")
        print("=" * 60)
    
    def run_migration(self):
        """执行完整迁移流程"""
        print("\n" + "=" * 60)
        print("Agent Hospital 知识库迁移工具")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"科室数量: {len(self.departments)}")
        print("=" * 60)
        print()
        
        # 步骤1: 备份
        self.backup_old_data()
        
        # 步骤2: 迁移病例库
        self.migrate_case_base()
        
        # 步骤3: 迁移经验库
        self.migrate_experience_base()
        
        # 步骤4: 清理
        self.cleanup_root_level_files()
        
        # 步骤5: 生成报告
        self.generate_stats_report()
        
        print("\n迁移完成！")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="迁移Agent Hospital知识库到科室隔离存储"
    )
    parser.add_argument(
        '--case-base',
        default='./knowledge/case_base',
        help='病例库路径 (默认: ./knowledge/case_base)'
    )
    parser.add_argument(
        '--experience-base',
        default='./knowledge/experience_base',
        help='经验库路径 (默认: ./knowledge/experience_base)'
    )
    parser.add_argument(
        '--config',
        default='./config/departments.json',
        help='科室配置文件路径 (默认: ./config/departments.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际执行迁移'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("⚠ 试运行模式 - 不会实际修改文件")
        print()
    
    migrator = KnowledgeBaseMigrator(
        old_case_base_path=args.case_base,
        old_experience_base_path=args.experience_base,
        departments_config=args.config
    )
    
    if not args.dry_run:
        # 确认执行
        print("此操作将修改知识库文件结构，建议提前备份。")
        confirm = input("确认继续? (yes/no): ")
        if confirm.lower() != 'yes':
            print("迁移已取消")
            return
    
    migrator.run_migration()


if __name__ == "__main__":
    main()
