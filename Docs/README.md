# 智能多模态医疗诊断系统 (MedicM2 A1)

## 系统概述

这是一个基于多智能体协作的智能医疗诊断系统，能够处理多模态医疗数据（文本、图像等），通过多个专科医生 Agent 协作诊断，最终由会诊 Agent 给出综合诊断结果。

## 系统架构

### 核心组件

1. **多专科医生 Agent**
   - 心脏科医生 (Cardiology)
   - 神经科医生 (Neurology)
   - 肿瘤科医生 (Oncology)
   - 呼吸科医生 (Pulmonology)
   - 消化科医生 (Gastroenterology)

2. **RAG 知识库系统**
   - 每个专科有独立的向量知识库
   - 基于专业医学文献和临床指南
   - 支持语义检索和上下文增强

3. **会诊 Agent**
   - 综合各专科意见
   - 分析病因优先级
   - 给出最终诊断和治疗方案

4. **多模态处理**
   - 文本病历分析
   - 医学影像识别
   - 多模态信息融合

## 安装配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env`，并填入你的 OpenAI API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 初始化知识库

首次运行时，系统会自动为每个专科创建知识库。你也可以手动添加医学文献到 `knowledge_base/` 对应科室文件夹中。

## 使用方法

### 基本使用

```python
from main import MedicalDiagnosisSystem

# 初始化系统
system = MedicalDiagnosisSystem()

# 准备病例
case = {
    "patient_info": {
        "age": 55,
        "gender": "男",
        "chief_complaint": "持续胸痛3天，伴有呼吸困难"
    },
    "symptoms": [
        "胸部中央压榨性疼痛",
        "疼痛放射到左臂",
        "呼吸急促",
        "出汗",
        "恶心"
    ],
    "medical_history": [
        "高血压10年",
        "糖尿病5年",
        "吸烟史30年"
    ],
    "vital_signs": {
        "血压": "160/95 mmHg",
        "心率": "102次/分",
        "体温": "37.2°C",
        "血氧": "94%"
    }
}

# 执行诊断
result = system.diagnose(case)

# 打印结果
print(result)
```

### 多模态诊断（包含影像）

```python
case_with_image = {
    "patient_info": {...},
    "symptoms": [...],
    "images": [
        "path/to/chest_xray.jpg",
        "path/to/ecg.png"
    ]
}

result = system.diagnose(case_with_image)
```

## 项目结构

```
A1/
├── .env                    # 环境变量配置
├── .env.example           # 环境变量示例
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── config/
│   └── departments.json  # 科室配置
├── knowledge_base/       # RAG 知识库
│   ├── cardiology/       # 心脏科知识库
│   ├── neurology/        # 神经科知识库
│   ├── oncology/         # 肿瘤科知识库
│   ├── pulmonology/      # 呼吸科知识库
│   └── gastroenterology/ # 消化科知识库
├── agents/
│   ├── base_agent.py     # Agent 基类
│   ├── doctor_agent.py   # 专科医生 Agent
│   └── consultation_agent.py # 会诊 Agent
├── rag/
│   ├── vector_store.py   # 向量存储管理
│   └── retriever.py      # 知识检索器
├── utils/
│   ├── multimodal.py     # 多模态处理工具
│   └── prompt_templates.py # 提示词模板
└── main.py              # 主程序入口
```

## 特性

- ✅ 多专科医生协作诊断
- ✅ 基于 RAG 的专业知识增强
- ✅ 多模态输入支持（文本+图像）
- ✅ 智能会诊系统
- ✅ 可扩展的科室配置
- ✅ 完整的诊断报告生成

## 注意事项

1. 本系统仅供学习和研究使用，不能替代专业医疗诊断
2. 使用前请确保已正确配置 OpenAI API Key
3. 建议使用 GPT-4 模型以获得更好的诊断效果
4. 知识库需要专业医学文献支持，初始版本包含示例数据

## 开发计划

- [ ] 添加更多专科
- [ ] 支持更多医学影像格式
- [ ] 增加诊断置信度评估
- [ ] 添加治疗方案推荐系统
- [ ] 实现诊断历史追踪

## License

MIT License
