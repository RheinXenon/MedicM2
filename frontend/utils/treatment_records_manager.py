"""
治疗记录管理模块
负责保存和加载治疗记录到JSON文件
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class TreatmentRecordsManager:
    """治疗记录管理器"""
    
    def __init__(self, records_file: str = "./data/treatment_records.json"):
        """
        初始化治疗记录管理器
        
        Args:
            records_file: JSON记录文件路径
        """
        self.records_file = records_file
        self.records: List[Dict] = []
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
        
        # 加载现有记录
        self.load_records()
    
    def load_records(self) -> List[Dict]:
        """
        从JSON文件加载治疗记录
        
        Returns:
            治疗记录列表
        """
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = data.get('records', [])
                    return self.records
            except Exception as e:
                print(f"加载治疗记录失败: {e}")
                self.records = []
                return []
        else:
            self.records = []
            return []
    
    def save_record(self, record: Dict) -> bool:
        """
        保存单条治疗记录
        
        Args:
            record: 治疗记录字典
            
        Returns:
            是否保存成功
        """
        try:
            # 添加时间戳
            if 'timestamp' not in record:
                record['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加到记录列表（最新的在最前面）
            self.records.insert(0, record)
            
            # 保存到文件
            self._save_to_file()
            return True
        except Exception as e:
            print(f"保存治疗记录失败: {e}")
            return False
    
    def _save_to_file(self):
        """保存所有记录到JSON文件"""
        data = {
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_records': len(self.records),
            'records': self.records
        }
        
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_records(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """
        获取治疗记录（支持分页）
        
        Args:
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            治疗记录列表
        """
        if limit is None:
            return self.records[offset:]
        else:
            return self.records[offset:offset + limit]
    
    def get_total_count(self) -> int:
        """
        获取记录总数
        
        Returns:
            记录总数
        """
        return len(self.records)
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        if not self.records:
            return {
                'total_records': 0,
                'successful_treatments': 0,
                'failed_treatments': 0,
                'diagnosis_accuracy': 0.0,
                'treatment_success_rate': 0.0
            }
        
        total = len(self.records)
        successful = sum(1 for r in self.records if r.get('outcome', {}).get('is_recovered', False))
        diagnosis_correct = sum(1 for r in self.records if r.get('outcome', {}).get('is_diagnosis_correct', False))
        
        return {
            'total_records': total,
            'successful_treatments': successful,
            'failed_treatments': total - successful,
            'diagnosis_accuracy': (diagnosis_correct / total) * 100 if total > 0 else 0.0,
            'treatment_success_rate': (successful / total) * 100 if total > 0 else 0.0
        }
    
    def clear_records(self) -> bool:
        """
        清空所有记录
        
        Returns:
            是否清空成功
        """
        try:
            self.records = []
            self._save_to_file()
            return True
        except Exception as e:
            print(f"清空记录失败: {e}")
            return False
    
    def get_stats_by_department(self) -> Dict:
        """
        获取按科室分组的统计信息
        
        Returns:
            按科室分组的统计字典
        """
        dept_stats = {}
        
        for record in self.records:
            # 获取科室信息（从分诊或诊断结果中）
            triage_info = record.get('triage', {})
            dept = None
            
            if isinstance(triage_info, dict):
                recommended_depts = triage_info.get('recommended_departments', [])
                if recommended_depts:
                    dept = recommended_depts[0]
            
            if not dept:
                dept = "未知科室"
            
            # 初始化科室统计
            if dept not in dept_stats:
                dept_stats[dept] = {
                    'total_patients': 0,
                    'successful_treatments': 0,
                    'failed_treatments': 0,
                    'diagnosis_correct': 0,
                    'diagnosis_incorrect': 0
                }
            
            # 更新统计
            dept_stats[dept]['total_patients'] += 1
            
            outcome = record.get('outcome', {})
            if outcome.get('is_recovered', False):
                dept_stats[dept]['successful_treatments'] += 1
            else:
                dept_stats[dept]['failed_treatments'] += 1
            
            if outcome.get('is_diagnosis_correct', False):
                dept_stats[dept]['diagnosis_correct'] += 1
            else:
                dept_stats[dept]['diagnosis_incorrect'] += 1
        
        # 计算百分比
        for dept, stats in dept_stats.items():
            total = stats['total_patients']
            if total > 0:
                stats['diagnosis_accuracy'] = (stats['diagnosis_correct'] / total) * 100
                stats['treatment_success_rate'] = (stats['successful_treatments'] / total) * 100
            else:
                stats['diagnosis_accuracy'] = 0.0
                stats['treatment_success_rate'] = 0.0
        
        return dept_stats
    
    def get_disease_distribution(self) -> Dict:
        """
        获取疾病分布统计
        
        Returns:
            疾病分布字典
        """
        disease_count = {}
        
        for record in self.records:
            disease = record.get('ground_truth_disease', '未知疾病')
            disease_count[disease] = disease_count.get(disease, 0) + 1
        
        # 按数量排序
        sorted_diseases = sorted(disease_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_diseases)
    
    def get_time_series_stats(self, days: int = 30) -> List[Dict]:
        """
        获取时间序列统计（按天分组）
        
        Args:
            days: 统计最近多少天的数据
            
        Returns:
            时间序列统计列表
        """
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # 获取日期范围
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        
        # 按日期分组统计
        daily_stats = defaultdict(lambda: {
            'date': None,
            'total': 0,
            'successful': 0,
            'diagnosis_correct': 0
        })
        
        for record in self.records:
            timestamp_str = record.get('timestamp', '')
            try:
                record_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").date()
                
                # 只统计指定天数内的数据
                if record_date >= start_date:
                    date_key = record_date.strftime("%Y-%m-%d")
                    daily_stats[date_key]['date'] = date_key
                    daily_stats[date_key]['total'] += 1
                    
                    outcome = record.get('outcome', {})
                    if outcome.get('is_recovered', False):
                        daily_stats[date_key]['successful'] += 1
                    if outcome.get('is_diagnosis_correct', False):
                        daily_stats[date_key]['diagnosis_correct'] += 1
            except:
                continue
        
        # 转换为列表并排序
        result = sorted(daily_stats.values(), key=lambda x: x['date'] or '')
        return result
    
    def get_recent_records_summary(self, limit: int = 10) -> List[Dict]:
        """
        获取最近记录的摘要信息
        
        Args:
            limit: 返回记录数量
            
        Returns:
            记录摘要列表
        """
        summaries = []
        
        for record in self.records[:limit]:
            summary = {
                'patient_name': record.get('patient_name', '未知'),
                'disease': record.get('ground_truth_disease', '未知'),
                'timestamp': record.get('timestamp', '未知'),
                'department': '未知',
                'is_recovered': record.get('outcome', {}).get('is_recovered', False),
                'is_diagnosis_correct': record.get('outcome', {}).get('is_diagnosis_correct', False)
            }
            
            # 获取科室信息
            triage_info = record.get('triage', {})
            if isinstance(triage_info, dict):
                recommended_depts = triage_info.get('recommended_departments', [])
                if recommended_depts:
                    summary['department'] = recommended_depts[0]
            
            summaries.append(summary)
        
        return summaries
    
    def export_records(self, export_path: str) -> bool:
        """
        导出记录到指定路径
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            export_data = {
                'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_records': len(self.records),
                'statistics': self.get_stats(),
                'records': self.records
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出记录失败: {e}")
            return False
