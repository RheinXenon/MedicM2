"""
医疗病例库 (Medical Case Base) - Agent Hospital 系统
存储成功治疗的病例，用于医生Agent的学习和参考
"""
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import pickle
from collections import defaultdict


class MedicalCaseBase:
    """
    医疗病例库
    根据论文 "Agent Hospital" 实现
    存储成功诊断和治疗的案例，支持相似案例检索
    """
    
    def __init__(self, storage_path: str = "./knowledge/case_base"):
        """
        初始化病例库
        
        Args:
            storage_path: 病例库存储路径
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 内存中的病例索引
        self.cases = []  # 所有病例列表
        self.case_index = {}  # case_id -> case 映射
        self.department_index = defaultdict(list)  # department -> case_ids 映射
        self.disease_index = defaultdict(list)  # disease -> case_ids 映射
        
        # 统计信息
        self.stats = {
            'total_cases': 0,
            'successful_cases': 0,
            'by_department': defaultdict(int),
            'by_disease': defaultdict(int)
        }
        
        # 加载已有病例
        self._load_cases()
    
    def add_case(self, case_data: Dict) -> str:
        """
        添加一个成功的病例
        
        Args:
            case_data: 病例数据字典，应包含：
                - patient_info: 病人基本信息
                - symptoms: 症状列表
                - medical_history: 既往病史
                - examination_results: 检查结果
                - diagnosis: 诊断结果
                - treatment: 治疗方案
                - outcome: 治疗结果
                - department: 科室
                - doctor_name: 医生姓名
                
        Returns:
            病例ID
        """
        # 生成病例ID
        case_id = self._generate_case_id()
        
        # 添加元数据
        case = {
            'case_id': case_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'successful',
            **case_data
        }
        
        # 添加到内存索引
        self.cases.append(case)
        self.case_index[case_id] = case
        
        # 更新科室索引
        if 'department' in case:
            self.department_index[case['department']].append(case_id)
            self.stats['by_department'][case['department']] += 1
        
        # 更新疾病索引
        if 'diagnosis' in case and 'disease' in case['diagnosis']:
            disease = case['diagnosis']['disease']
            self.disease_index[disease].append(case_id)
            self.stats['by_disease'][disease] += 1
        
        # 更新统计
        self.stats['total_cases'] += 1
        self.stats['successful_cases'] += 1
        
        # 持久化
        self._save_case(case)
        self._save_stats()
        
        return case_id
    
    def retrieve_similar_cases(
        self,
        query_symptoms: List[str],
        query_history: List[str] = None,
        department: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        检索相似病例
        
        Args:
            query_symptoms: 查询症状列表
            query_history: 查询病史
            department: 限定科室
            top_k: 返回前k个最相似的病例
            
        Returns:
            相似病例列表，按相似度排序
        """
        # 筛选候选病例
        if department and department in self.department_index:
            candidate_ids = self.department_index[department]
            candidates = [self.case_index[cid] for cid in candidate_ids]
        else:
            candidates = self.cases
        
        if not candidates:
            return []
        
        # 计算相似度
        scored_cases = []
        for case in candidates:
            similarity = self._calculate_similarity(
                query_symptoms,
                query_history or [],
                case
            )
            scored_cases.append({
                'case': case,
                'similarity': similarity
            })
        
        # 按相似度排序
        scored_cases.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 返回top_k个案例
        return [
            {
                **item['case'],
                'similarity_score': item['similarity']
            }
            for item in scored_cases[:top_k]
        ]
    
    def retrieve_by_disease(self, disease: str, limit: int = 10) -> List[Dict]:
        """
        根据疾病名称检索病例
        
        Args:
            disease: 疾病名称
            limit: 最多返回的病例数
            
        Returns:
            病例列表
        """
        if disease not in self.disease_index:
            return []
        
        case_ids = self.disease_index[disease][:limit]
        return [self.case_index[cid] for cid in case_ids]
    
    def retrieve_by_department(
        self, 
        department: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        根据科室检索病例
        
        Args:
            department: 科室名称
            limit: 最多返回的病例数
            
        Returns:
            病例列表
        """
        if department not in self.department_index:
            return []
        
        case_ids = self.department_index[department][:limit]
        return [self.case_index[cid] for cid in case_ids]
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """获取指定ID的病例"""
        return self.case_index.get(case_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return dict(self.stats)
    
    def format_case_for_reference(self, case: Dict) -> str:
        """
        格式化病例为参考文本
        
        Args:
            case: 病例字典
            
        Returns:
            格式化的文本
        """
        patient_info = case.get('patient_info', {})
        symptoms = case.get('symptoms', [])
        diagnosis = case.get('diagnosis', {})
        treatment = case.get('treatment', {})
        
        text = f"""病例 #{case['case_id']}
        
病人信息：
- 年龄：{patient_info.get('age', '未知')}岁
- 性别：{patient_info.get('gender', '未知')}

主要症状：
{self._format_list(symptoms[:5])}

诊断：{diagnosis.get('disease', '未记录')}

治疗方案：
{treatment.get('summary', '未记录')}

治疗结果：成功康复
"""
        return text
    
    def _calculate_similarity(
        self,
        query_symptoms: List[str],
        query_history: List[str],
        case: Dict
    ) -> float:
        """
        计算查询和病例的相似度
        使用简单的Jaccard相似度
        """
        # 提取病例的症状和病史
        case_symptoms = set(case.get('symptoms', []))
        case_history = set(case.get('medical_history', []))
        
        query_symptoms_set = set(query_symptoms)
        query_history_set = set(query_history)
        
        # 计算症状相似度（权重0.7）
        if query_symptoms_set or case_symptoms:
            symptom_similarity = len(query_symptoms_set & case_symptoms) / \
                               len(query_symptoms_set | case_symptoms) if \
                               (query_symptoms_set | case_symptoms) else 0
        else:
            symptom_similarity = 0
        
        # 计算病史相似度（权重0.3）
        if query_history_set or case_history:
            history_similarity = len(query_history_set & case_history) / \
                               len(query_history_set | case_history) if \
                               (query_history_set | case_history) else 0
        else:
            history_similarity = 0
        
        # 加权平均
        similarity = 0.7 * symptom_similarity + 0.3 * history_similarity
        
        return similarity
    
    def _generate_case_id(self) -> str:
        """生成病例ID"""
        import time
        timestamp = int(time.time() * 1000)
        return f"CASE{timestamp:016d}"
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表为文本"""
        if not items:
            return "无"
        return "\n".join(f"- {item}" for item in items)
    
    def _save_case(self, case: Dict):
        """保存单个病例到文件"""
        case_file = os.path.join(
            self.storage_path,
            f"{case['case_id']}.json"
        )
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(case, f, ensure_ascii=False, indent=2)
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = os.path.join(self.storage_path, "stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def _load_cases(self):
        """从文件加载所有病例"""
        if not os.path.exists(self.storage_path):
            return
        
        # 加载统计信息
        stats_file = os.path.join(self.storage_path, "stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                loaded_stats = json.load(f)
                # 恢复defaultdict
                self.stats['total_cases'] = loaded_stats.get('total_cases', 0)
                self.stats['successful_cases'] = loaded_stats.get('successful_cases', 0)
                if 'by_department' in loaded_stats:
                    self.stats['by_department'] = defaultdict(
                        int,
                        loaded_stats['by_department']
                    )
                if 'by_disease' in loaded_stats:
                    self.stats['by_disease'] = defaultdict(
                        int,
                        loaded_stats['by_disease']
                    )
        
        # 加载所有病例文件
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json') and filename != 'stats.json':
                case_file = os.path.join(self.storage_path, filename)
                try:
                    with open(case_file, 'r', encoding='utf-8') as f:
                        case = json.load(f)
                        
                        # 重建索引
                        case_id = case['case_id']
                        self.cases.append(case)
                        self.case_index[case_id] = case
                        
                        if 'department' in case:
                            self.department_index[case['department']].append(case_id)
                        
                        if 'diagnosis' in case and 'disease' in case['diagnosis']:
                            disease = case['diagnosis']['disease']
                            self.disease_index[disease].append(case_id)
                except Exception as e:
                    print(f"加载病例文件 {filename} 失败: {e}")
    
    def clear(self):
        """清空病例库（谨慎使用）"""
        self.cases = []
        self.case_index = {}
        self.department_index = defaultdict(list)
        self.disease_index = defaultdict(list)
        self.stats = {
            'total_cases': 0,
            'successful_cases': 0,
            'by_department': defaultdict(int),
            'by_disease': defaultdict(int)
        }
    
    def __len__(self):
        return len(self.cases)
    
    def __str__(self):
        return f"MedicalCaseBase(cases={len(self.cases)}, departments={len(self.department_index)})"
