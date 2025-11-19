"""
经验库 (Experience Base) - Agent Hospital 系统
存储从失败案例中学到的规则和经验
"""
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from collections import defaultdict
from utils.prompt_templates import EXPERIENCE_RULE_GENERATION_TEMPLATE


class ExperienceBase:
    """
    经验库
    根据论文 "Agent Hospital" 实现
    当医生诊断失败时，通过反思生成经验规则，避免重复错误
    """
    
    def __init__(self, storage_path: str = "./knowledge/experience_base"):
        """
        初始化经验库
        
        Args:
            storage_path: 经验库存储路径
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 内存中的经验索引
        self.rules = []  # 所有规则列表
        self.rule_index = {}  # rule_id -> rule 映射
        self.department_index = defaultdict(list)  # department -> rule_ids 映射
        self.disease_index = defaultdict(list)  # disease -> rule_ids 映射
        self.symptom_index = defaultdict(list)  # symptom -> rule_ids 映射
        
        # 统计信息
        self.stats = {
            'total_rules': 0,
            'by_department': defaultdict(int),
            'by_disease': defaultdict(int),
            'successful_applications': 0,  # 成功应用规则的次数
            'failed_applications': 0  # 应用规则后仍失败的次数
        }
        
        # 加载已有规则
        self._load_rules()
    
    def add_rule(self, rule_data: Dict) -> str:
        """
        添加一条经验规则
        
        Args:
            rule_data: 规则数据字典，应包含：
                - rule_content: 规则内容（自然语言描述）
                - trigger_conditions: 触发条件（症状、病史等）
                - recommendation: 推荐的诊断或检查
                - source_case: 来源案例
                - department: 科室
                - disease: 相关疾病
                - confidence: 规则置信度
                
        Returns:
            规则ID
        """
        # 生成规则ID
        rule_id = self._generate_rule_id()
        
        # 添加元数据
        rule = {
            'rule_id': rule_id,
            'timestamp': datetime.now().isoformat(),
            'application_count': 0,  # 应用次数
            'success_count': 0,  # 成功次数
            'status': 'active',  # active, inactive
            **rule_data
        }
        
        # 添加到内存索引
        self.rules.append(rule)
        self.rule_index[rule_id] = rule
        
        # 更新科室索引
        if 'department' in rule:
            self.department_index[rule['department']].append(rule_id)
            self.stats['by_department'][rule['department']] += 1
        
        # 更新疾病索引
        if 'disease' in rule:
            self.disease_index[rule['disease']].append(rule_id)
            self.stats['by_disease'][rule['disease']] += 1
        
        # 更新症状索引
        if 'trigger_conditions' in rule and 'symptoms' in rule['trigger_conditions']:
            for symptom in rule['trigger_conditions']['symptoms']:
                self.symptom_index[symptom].append(rule_id)
        
        # 更新统计
        self.stats['total_rules'] += 1
        
        # 持久化
        self._save_rule(rule)
        self._save_stats()
        
        return rule_id
    
    def retrieve_applicable_rules(
        self,
        symptoms: List[str],
        medical_history: List[str] = None,
        department: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        检索适用的经验规则
        
        Args:
            symptoms: 症状列表
            medical_history: 病史
            department: 科室
            top_k: 返回前k个最相关的规则
            
        Returns:
            适用规则列表，按相关度排序
        """
        # 筛选候选规则
        candidate_ids = set()
        
        # 从症状索引中查找
        for symptom in symptoms:
            if symptom in self.symptom_index:
                candidate_ids.update(self.symptom_index[symptom])
        
        # 从科室索引中查找
        if department and department in self.department_index:
            dept_ids = set(self.department_index[department])
            if candidate_ids:
                candidate_ids &= dept_ids  # 取交集
            else:
                candidate_ids = dept_ids
        
        if not candidate_ids:
            return []
        
        # 获取候选规则
        candidates = [self.rule_index[rid] for rid in candidate_ids]
        
        # 计算相关度
        scored_rules = []
        for rule in candidates:
            relevance = self._calculate_relevance(
                symptoms,
                medical_history or [],
                rule
            )
            scored_rules.append({
                'rule': rule,
                'relevance': relevance
            })
        
        # 按相关度和成功率排序
        scored_rules.sort(
            key=lambda x: (
                x['relevance'],
                x['rule']['success_count'] / max(x['rule']['application_count'], 1)
            ),
            reverse=True
        )
        
        # 返回top_k个规则
        return [
            {
                **item['rule'],
                'relevance_score': item['relevance']
            }
            for item in scored_rules[:top_k]
        ]
    
    def record_rule_application(
        self,
        rule_id: str,
        success: bool
    ):
        """
        记录规则应用结果
        
        Args:
            rule_id: 规则ID
            success: 是否成功
        """
        if rule_id not in self.rule_index:
            return
        
        rule = self.rule_index[rule_id]
        rule['application_count'] += 1
        
        if success:
            rule['success_count'] += 1
            self.stats['successful_applications'] += 1
        else:
            self.stats['failed_applications'] += 1
        
        # 更新置信度
        rule['confidence'] = rule['success_count'] / rule['application_count']
        
        # 如果规则失败率太高，标记为inactive
        if rule['application_count'] >= 5 and rule['confidence'] < 0.3:
            rule['status'] = 'inactive'
        
        # 持久化更新
        self._save_rule(rule)
        self._save_stats()
    
    def generate_rule_from_failure(
        self,
        failed_case: Dict,
        correct_diagnosis: str,
        wrong_diagnosis: str,
        llm_generator
    ) -> Optional[str]:
        """
        从失败案例生成经验规则
        
        Args:
            failed_case: 失败的案例
            correct_diagnosis: 正确诊断
            wrong_diagnosis: 错误诊断
            llm_generator: LLM生成器（BaseAgent实例）
            
        Returns:
            生成的规则ID，如果生成失败则返回None
        """
        # 构建反思提示词（使用模板）
        symptoms = failed_case.get('symptoms', [])
        medical_history = failed_case.get('medical_history', [])
        patient_info = failed_case.get('patient_info', {})
        
        prompt = EXPERIENCE_RULE_GENERATION_TEMPLATE.format(
            patient_age=patient_info.get('age', '未知'),
            patient_gender=patient_info.get('gender', '未知'),
            symptoms=', '.join(symptoms),
            medical_history=', '.join(medical_history) if medical_history else '无',
            wrong_diagnosis=wrong_diagnosis,
            correct_diagnosis=correct_diagnosis
        )
        
        try:
            response = llm_generator.generate_response(
                prompt,
                system_message="你是一位经验丰富的临床医生，擅长从失败案例中总结经验。"
            )
            
            # 解析响应
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                rule_data = json.loads(json_match.group())
            else:
                print("无法解析LLM生成的规则")
                return None
            
            # 添加额外信息
            rule_data['disease'] = correct_diagnosis
            rule_data['department'] = failed_case.get('department', '未知')
            rule_data['source_case'] = {
                'case_id': failed_case.get('case_id', 'unknown'),
                'wrong_diagnosis': wrong_diagnosis,
                'correct_diagnosis': correct_diagnosis
            }
            
            # 添加规则到经验库
            rule_id = self.add_rule(rule_data)
            
            return rule_id
            
        except Exception as e:
            print(f"生成经验规则失败: {e}")
            return None
    
    def format_rules_for_reference(self, rules: List[Dict]) -> str:
        """
        格式化规则为参考文本
        
        Args:
            rules: 规则列表
            
        Returns:
            格式化的文本
        """
        if not rules:
            return "暂无相关经验规则"
        
        text_parts = ["相关经验规则：\n"]
        
        for i, rule in enumerate(rules, 1):
            confidence = rule.get('confidence', 0)
            success_rate = (rule['success_count'] / max(rule['application_count'], 1)) \
                          if rule['application_count'] > 0 else confidence
            
            text_parts.append(f"""
规则 {i} (置信度: {confidence:.2f}, 成功率: {success_rate:.2f}):
{rule['rule_content']}

推荐: {rule.get('recommendation', '无')}
依据: {rule.get('reasoning', '无')[:100]}...
""")
        
        return "\n".join(text_parts)
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """获取指定ID的规则"""
        return self.rule_index.get(rule_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return dict(self.stats)
    
    def _calculate_relevance(
        self,
        query_symptoms: List[str],
        query_history: List[str],
        rule: Dict
    ) -> float:
        """
        计算查询和规则的相关度
        """
        trigger_conditions = rule.get('trigger_conditions', {})
        rule_symptoms = set(trigger_conditions.get('symptoms', []))
        
        query_symptoms_set = set(query_symptoms)
        
        # 计算症状匹配度
        if query_symptoms_set and rule_symptoms:
            relevance = len(query_symptoms_set & rule_symptoms) / \
                       len(rule_symptoms)
        else:
            relevance = 0
        
        # 考虑规则的历史表现
        if rule['application_count'] > 0:
            success_rate = rule['success_count'] / rule['application_count']
            relevance = relevance * 0.7 + success_rate * 0.3
        
        return relevance
    
    def _generate_rule_id(self) -> str:
        """生成规则ID"""
        import time
        timestamp = int(time.time() * 1000)
        return f"RULE{timestamp:016d}"
    
    def _save_rule(self, rule: Dict):
        """保存单个规则到文件"""
        rule_file = os.path.join(
            self.storage_path,
            f"{rule['rule_id']}.json"
        )
        with open(rule_file, 'w', encoding='utf-8') as f:
            json.dump(rule, f, ensure_ascii=False, indent=2)
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = os.path.join(self.storage_path, "stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def _load_rules(self):
        """从文件加载所有规则"""
        if not os.path.exists(self.storage_path):
            return
        
        # 加载统计信息
        stats_file = os.path.join(self.storage_path, "stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                loaded_stats = json.load(f)
                self.stats['total_rules'] = loaded_stats.get('total_rules', 0)
                self.stats['successful_applications'] = loaded_stats.get('successful_applications', 0)
                self.stats['failed_applications'] = loaded_stats.get('failed_applications', 0)
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
        
        # 加载所有规则文件
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json') and filename != 'stats.json':
                rule_file = os.path.join(self.storage_path, filename)
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rule = json.load(f)
                        
                        # 重建索引
                        rule_id = rule['rule_id']
                        self.rules.append(rule)
                        self.rule_index[rule_id] = rule
                        
                        if 'department' in rule:
                            self.department_index[rule['department']].append(rule_id)
                        
                        if 'disease' in rule:
                            self.disease_index[rule['disease']].append(rule_id)
                        
                        if 'trigger_conditions' in rule and 'symptoms' in rule['trigger_conditions']:
                            for symptom in rule['trigger_conditions']['symptoms']:
                                self.symptom_index[symptom].append(rule_id)
                except Exception as e:
                    print(f"加载规则文件 {filename} 失败: {e}")
    
    def clear(self):
        """清空经验库（谨慎使用）"""
        self.rules = []
        self.rule_index = {}
        self.department_index = defaultdict(list)
        self.disease_index = defaultdict(list)
        self.symptom_index = defaultdict(list)
        self.stats = {
            'total_rules': 0,
            'by_department': defaultdict(int),
            'by_disease': defaultdict(int),
            'successful_applications': 0,
            'failed_applications': 0
        }
    
    def __len__(self):
        return len(self.rules)
    
    def __str__(self):
        return f"ExperienceBase(rules={len(self.rules)}, departments={len(self.department_index)})"
