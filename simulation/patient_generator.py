"""
病人生成器 - Agent Hospital 系统
从CMeIEV2数据集自动生成病人Agent
"""
import json
import random
from typing import Dict, List, Optional
from agents.patient_agent import PatientAgent


class PatientGenerator:
    """
    病人生成器
    根据论文 "Agent Hospital" 中的方法，自动生成病人Agent
    """
    
    def __init__(self, dataset_path: str = "./datasets/高质量医疗样本集_20251118.json"):
        """
        初始化病人生成器
        
        Args:
            dataset_path: 数据集路径
        """
        self.dataset_path = dataset_path
        self.disease_data = []
        self.load_dataset()
        
        # 中文姓名库
        self.family_names = [
            '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
            '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧'
        ]
        
        self.given_names_male = [
            '伟', '强', '磊', '军', '洋', '勇', '杰', '涛', '明', '超',
            '鹏', '辉', '健', '波', '凯', '峰', '浩', '刚', '斌', '鑫'
        ]
        
        self.given_names_female = [
            '芳', '娜', '静', '丽', '敏', '莉', '秀', '娟', '英', '华',
            '玲', '婷', '红', '霞', '梅', '琳', '燕', '雪', '萍', '倩'
        ]
    
    def load_dataset(self):
        """加载数据集"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.disease_data = data.get('样本数据', [])
                print(f"成功加载 {len(self.disease_data)} 条疾病数据")
        except Exception as e:
            print(f"加载数据集失败: {e}")
            self.disease_data = []
    
    def generate_patient(
        self,
        disease_name: Optional[str] = None,
        age_range: tuple = (20, 80),
        gender: Optional[str] = None
    ) -> PatientAgent:
        """
        生成一个病人Agent
        
        Args:
            disease_name: 指定疾病名称，如果为None则随机选择
            age_range: 年龄范围
            gender: 性别 ('男'/'女')，如果为None则随机
            
        Returns:
            生成的病人Agent
        """
        # 1. 选择疾病
        if disease_name:
            # 查找指定疾病
            disease_info = self._find_disease_by_name(disease_name)
            if not disease_info:
                print(f"未找到疾病 {disease_name}，随机选择")
                disease_info = random.choice(self.disease_data)
        else:
            # 随机选择疾病
            disease_info = random.choice(self.disease_data)
        
        disease = disease_info['疾病名称']
        
        # 2. 生成基本信息
        if not gender:
            gender = random.choice(['男', '女'])
        
        age = random.randint(age_range[0], age_range[1])
        name = self._generate_name(gender)
        
        # 3. 提取症状
        symptoms = disease_info.get('症状', [])
        if len(symptoms) > 20:
            # 如果症状太多，随机选择一部分（模拟病人不会表现所有症状）
            num_symptoms = random.randint(5, min(15, len(symptoms)))
            symptoms = random.sample(symptoms, num_symptoms)
        
        # 4. 生成既往病史
        medical_history = self._generate_medical_history(disease_info, age)
        
        # 5. 创建病人Agent
        patient = PatientAgent(
            name=name,
            age=age,
            gender=gender,
            disease=disease,
            symptoms=symptoms,
            medical_history=medical_history
        )
        
        return patient
    
    def generate_batch_patients(
        self,
        count: int,
        disease_distribution: Optional[Dict[str, float]] = None
    ) -> List[PatientAgent]:
        """
        批量生成病人
        
        Args:
            count: 生成数量
            disease_distribution: 疾病分布字典 {疾病名: 概率}
                如果为None，则均匀分布
                
        Returns:
            病人Agent列表
        """
        patients = []
        
        for i in range(count):
            # 根据分布选择疾病
            if disease_distribution:
                disease_name = random.choices(
                    list(disease_distribution.keys()),
                    weights=list(disease_distribution.values()),
                    k=1
                )[0]
            else:
                disease_name = None
            
            patient = self.generate_patient(disease_name=disease_name)
            patients.append(patient)
            
            if (i + 1) % 10 == 0:
                print(f"已生成 {i + 1}/{count} 个病人...")
        
        return patients
    
    def generate_patients_by_department(
        self,
        department_keywords: List[str],
        count: int
    ) -> List[PatientAgent]:
        """
        根据科室关键词生成相关病人
        
        Args:
            department_keywords: 科室关键词列表
            count: 生成数量
            
        Returns:
            病人Agent列表
        """
        # 筛选相关疾病
        relevant_diseases = []
        for disease_info in self.disease_data:
            symptoms = disease_info.get('症状', [])
            symptom_text = ' '.join(symptoms)
            
            # 检查是否包含关键词
            for keyword in department_keywords:
                if keyword in symptom_text or keyword in disease_info['疾病名称']:
                    relevant_diseases.append(disease_info)
                    break
        
        if not relevant_diseases:
            print("未找到相关疾病，使用所有疾病")
            relevant_diseases = self.disease_data
        
        print(f"找到 {len(relevant_diseases)} 个相关疾病")
        
        # 生成病人
        patients = []
        for i in range(count):
            disease_info = random.choice(relevant_diseases)
            disease_name = disease_info['疾病名称']
            
            patient = self.generate_patient(disease_name=disease_name)
            patients.append(patient)
        
        return patients
    
    def _find_disease_by_name(self, disease_name: str) -> Optional[Dict]:
        """根据疾病名称查找疾病信息"""
        for disease_info in self.disease_data:
            if disease_name in disease_info['疾病名称']:
                return disease_info
            # 检查同义词
            if '同义词' in disease_info:
                for synonym in disease_info['同义词']:
                    if disease_name in synonym or synonym in disease_name:
                        return disease_info
        return None
    
    def _generate_name(self, gender: str) -> str:
        """生成中文姓名"""
        family_name = random.choice(self.family_names)
        
        if gender == '男':
            given_name_pool = self.given_names_male
        else:
            given_name_pool = self.given_names_female
        
        # 生成1-2个字的名字
        if random.random() > 0.3:
            # 2个字的名字
            given_name = random.choice(given_name_pool) + random.choice(given_name_pool)
        else:
            # 1个字的名字
            given_name = random.choice(given_name_pool)
        
        return family_name + given_name
    
    def _generate_medical_history(
        self,
        disease_info: Dict,
        age: int
    ) -> List[str]:
        """生成既往病史"""
        history = []
        
        # 根据年龄添加常见病史
        if age > 50:
            common_conditions = ['高血压', '糖尿病', '高脂血症']
            # 随机添加1-2个
            num_conditions = random.randint(0, 2)
            if num_conditions > 0:
                history.extend(random.sample(common_conditions, num_conditions))
        
        # 从疾病的病因或相关信息提取
        if '病因' in disease_info:
            causes = disease_info['病因']
            if isinstance(causes, list) and causes:
                # 随机选择1-2个相关的既往因素
                if len(causes) > 0:
                    relevant_cause = random.choice(causes)
                    if len(relevant_cause) < 50:  # 只保留简短的
                        history.append(relevant_cause)
        
        # 如果没有病史，添加"无特殊"
        if not history:
            history = ['无特殊既往病史']
        
        return history
    
    def get_disease_statistics(self) -> Dict:
        """获取数据集疾病统计信息"""
        stats = {
            'total_diseases': len(self.disease_data),
            'diseases_by_symptom_count': {},
            'sample_diseases': []
        }
        
        # 按症状数量分类
        for disease_info in self.disease_data:
            symptom_count = len(disease_info.get('症状', []))
            if symptom_count not in stats['diseases_by_symptom_count']:
                stats['diseases_by_symptom_count'][symptom_count] = 0
            stats['diseases_by_symptom_count'][symptom_count] += 1
        
        # 随机采样10个疾病名称
        if len(self.disease_data) > 0:
            sample_size = min(10, len(self.disease_data))
            samples = random.sample(self.disease_data, sample_size)
            stats['sample_diseases'] = [d['疾病名称'] for d in samples]
        
        return stats
    
    def __len__(self):
        return len(self.disease_data)
    
    def __str__(self):
        return f"PatientGenerator(diseases={len(self.disease_data)})"
