"""
病人 Agent - Agent Hospital 系统
根据论文 "Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents" 实现
"""
from typing import Dict, List, Optional
from .base_agent import BaseAgent
import random
import time


class PatientAgent(BaseAgent):
    """病人 Agent - 模拟病人的疾病状态和行为"""
    
    def __init__(
        self, 
        name: str,
        age: int,
        gender: str,
        disease: str,
        symptoms: List[str],
        medical_history: List[str] = None,
        **kwargs
    ):
        """
        初始化病人 Agent
        
        Args:
            name: 病人姓名
            age: 年龄
            gender: 性别 (男/女)
            disease: 患病名称 (ground truth)
            symptoms: 症状列表
            medical_history: 既往病史
            **kwargs: 传递给基类的其他参数
        """
        role = f"患有{disease}的病人"
        super().__init__(name=name, role=role, **kwargs)
        
        # 基本信息
        self.age = age
        self.gender = gender
        self.patient_id = self._generate_patient_id()
        
        # 疾病信息
        self.disease = disease  # ground truth，病人自己不知道
        self.symptoms = symptoms
        self.medical_history = medical_history or []
        
        # 病情状态
        self.condition_status = "sick"  # sick, recovering, recovered
        self.treatment_history = []  # 治疗历史
        self.visit_count = 0  # 就诊次数
        
        # 检查结果
        self.examination_reports = {}  # 医学检查报告
        
        # 当前诊断和治疗
        self.current_diagnosis = None
        self.current_treatment = None
        
        # 满意度
        self.satisfaction = None
        
        # 病程时间线
        self.timeline = []
        self._add_timeline_event("疾病发作", f"出现{disease}相关症状")
    
    def _generate_patient_id(self) -> str:
        """生成病人ID"""
        timestamp = int(time.time() * 1000)
        return f"P{timestamp}{random.randint(1000, 9999)}"
    
    def _add_timeline_event(self, event_type: str, description: str):
        """添加时间线事件"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'description': description
        }
        self.timeline.append(event)
        self.add_thinking_step(event_type, description)
    
    def describe_symptoms(self) -> str:
        """
        描述症状（病人主诉）
        病人自己不知道疾病名称，只能描述症状
        """
        self.add_thinking_step(
            "症状描述",
            f"{self.name} 开始向医生描述症状..."
        )
        
        # 构建主诉
        if len(self.symptoms) == 0:
            chief_complaint = "感觉身体不适"
        elif len(self.symptoms) <= 3:
            chief_complaint = "、".join(self.symptoms)
        else:
            # 随机选择3-5个主要症状描述
            main_symptoms = random.sample(
                self.symptoms, 
                min(5, len(self.symptoms))
            )
            chief_complaint = "、".join(main_symptoms)
        
        # 生成自然语言描述
        prompt = f"""你是一位{self.age}岁的{self.gender}性病人，名叫{self.name}。
你现在感到身体不适，来到医院就诊。

你的主要症状包括：
{chief_complaint}

请用第一人称，以病人的口吻自然地描述你的不适症状，不要提及具体的疾病名称（因为你不知道自己得了什么病）。
描述应该：
1. 使用通俗易懂的语言，不要使用医学术语
2. 描述症状出现的时间、程度、特点等
3. 表达你的担忧和不适感
4. 长度控制在100-150字

直接输出描述，不要有其他内容。
"""
        
        description = self.generate_response(
            prompt,
            system_message="你是一位来就诊的病人，正在向医生描述你的症状。"
        )
        
        self._add_timeline_event("主诉", description)
        
        return description
    
    def provide_medical_history(self) -> str:
        """提供既往病史"""
        if not self.medical_history:
            return "无特殊既往病史"
        
        history_text = "既往病史：\n" + "\n".join(
            f"- {h}" for h in self.medical_history
        )
        
        self._add_timeline_event("病史询问", history_text)
        
        return history_text
    
    def undergo_examination(self, examination_type: str, result: Dict) -> bool:
        """
        接受医学检查
        
        Args:
            examination_type: 检查类型
            result: 检查结果
            
        Returns:
            是否接受检查
        """
        self.add_thinking_step(
            "接受检查",
            f"正在接受{examination_type}检查..."
        )
        
        # 存储检查结果
        self.examination_reports[examination_type] = result
        
        self._add_timeline_event(
            "医学检查",
            f"完成{examination_type}检查"
        )
        
        return True
    
    def receive_diagnosis(self, diagnosis: Dict) -> str:
        """
        接收诊断结果
        
        Args:
            diagnosis: 诊断结果字典
            
        Returns:
            病人的反应
        """
        self.current_diagnosis = diagnosis
        self.visit_count += 1
        
        self.add_thinking_step(
            "接收诊断",
            f"收到诊断结果：{diagnosis.get('diagnosis_text', '未提供')}"
        )
        
        self._add_timeline_event(
            "诊断",
            f"第{self.visit_count}次就诊，医生诊断：{diagnosis.get('diagnosis_text', '未提供')[:50]}..."
        )
        
        # 生成病人反应
        is_correct = self._check_diagnosis_correctness(diagnosis)
        
        if is_correct:
            reaction = f"谢谢医生，我会按照您的建议进行治疗。"
            self.satisfaction = "satisfied"
        else:
            reaction = f"好的医生，我理解了。希望能尽快康复。"
            self.satisfaction = "neutral"
        
        return reaction
    
    def receive_treatment(self, treatment: Dict) -> bool:
        """
        接收治疗方案
        
        Args:
            treatment: 治疗方案字典
            
        Returns:
            是否接受治疗
        """
        self.current_treatment = treatment
        self.treatment_history.append({
            'timestamp': time.time(),
            'treatment': treatment,
            'diagnosis': self.current_diagnosis
        })
        
        self._add_timeline_event(
            "接受治疗",
            f"开始按照治疗方案进行治疗"
        )
        
        return True
    
    def evaluate_treatment_outcome(self) -> Dict:
        """
        评估治疗效果
        模拟病人康复过程
        
        Returns:
            治疗效果评估
        """
        self.add_thinking_step(
            "评估治疗效果",
            "正在评估治疗后的身体状况..."
        )
        
        # 检查诊断是否正确
        is_diagnosis_correct = self._check_diagnosis_correctness(
            self.current_diagnosis
        )
        
        # 根据诊断准确性模拟康复情况
        if is_diagnosis_correct:
            # 诊断正确，大概率康复
            recovery_probability = 0.85
        else:
            # 诊断错误，小概率康复（可能是自愈或巧合）
            recovery_probability = 0.15
        
        is_recovered = random.random() < recovery_probability
        
        if is_recovered:
            self.condition_status = "recovered"
            outcome = "recovered"
            feedback = f"感谢医生的治疗，我的症状已经明显好转了！"
            self.satisfaction = "very_satisfied"
        else:
            self.condition_status = "not_improved"
            outcome = "not_improved"
            feedback = f"症状似乎没有明显改善，我可能需要再次就诊。"
            self.satisfaction = "dissatisfied"
        
        self._add_timeline_event(
            "治疗效果评估",
            f"治疗结果: {outcome}"
        )
        
        result = {
            'patient_id': self.patient_id,
            'patient_name': self.name,
            'outcome': outcome,
            'is_recovered': is_recovered,
            'is_diagnosis_correct': is_diagnosis_correct,
            'feedback': feedback,
            'satisfaction': self.satisfaction,
            'ground_truth_disease': self.disease,
            'diagnosed_disease': self._extract_disease_from_diagnosis(
                self.current_diagnosis
            ) if self.current_diagnosis else None
        }
        
        return result
    
    def _check_diagnosis_correctness(self, diagnosis: Dict) -> bool:
        """检查诊断是否正确"""
        if not diagnosis:
            return False
        
        diagnosed_disease = self._extract_disease_from_diagnosis(diagnosis)
        if not diagnosed_disease:
            return False
        
        # 简单的字符串匹配检查
        # 在实际应用中可能需要更复杂的匹配逻辑
        return (
            self.disease.lower() in diagnosed_disease.lower() or
            diagnosed_disease.lower() in self.disease.lower()
        )
    
    def _extract_disease_from_diagnosis(self, diagnosis: Dict) -> Optional[str]:
        """从诊断结果中提取疾病名称"""
        if 'disease' in diagnosis:
            return diagnosis['disease']
        if 'diagnosis_text' in diagnosis:
            # 简单提取，实际可能需要更复杂的NLP
            return diagnosis['diagnosis_text'][:50]
        return None
    
    def get_case_summary(self) -> Dict:
        """
        获取病例摘要
        
        Returns:
            完整的病例信息
        """
        return {
            'patient_id': self.patient_id,
            'patient_info': {
                'name': self.name,
                'age': self.age,
                'gender': self.gender,
            },
            'ground_truth_disease': self.disease,
            'symptoms': self.symptoms,
            'medical_history': self.medical_history,
            'examination_reports': self.examination_reports,
            'visit_count': self.visit_count,
            'treatment_history': self.treatment_history,
            'condition_status': self.condition_status,
            'satisfaction': self.satisfaction,
            'timeline': self.timeline
        }
    
    def __str__(self):
        return f"病人: {self.name} ({self.age}岁, {self.gender})"
    
    def __repr__(self):
        return f"<PatientAgent: {self.name}, 疾病={self.disease}>"
