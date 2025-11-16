# 使用指南

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
# 编辑 .env 文件，填入你的 OpenAI API Key
OPENAI_API_KEY=your_api_key_here
```

### 2. 运行示例

#### 方式一：运行预设示例

```bash
# 交互式运行所有示例
python run_examples.py

# 运行单个示例
python run_examples.py 急性冠脉综合征

# 运行所有示例
python run_examples.py all
```

#### 方式二：使用主程序

```bash
python main.py
```

#### 方式三：在代码中使用

```python
from main import MedicalDiagnosisSystem

# 初始化系统
system = MedicalDiagnosisSystem()

# 准备病例数据
case = {
    "patient_info": {
        "age": 55,
        "gender": "男",
        "chief_complaint": "胸痛3天"
    },
    "symptoms": [
        "胸部压榨性疼痛",
        "呼吸困难"
    ],
    "medical_history": [
        "高血压",
        "糖尿病"
    ],
    "vital_signs": {
        "血压": "160/95 mmHg",
        "心率": "102次/分"
    }
}

# 执行诊断
result = system.diagnose(case)

# 打印结果
system.print_diagnosis(result)
```

## 病例数据格式

### 基本结构

```python
case_data = {
    # 患者基本信息（必填）
    "patient_info": {
        "age": 55,                    # 年龄
        "gender": "男",                # 性别
        "chief_complaint": "主诉内容"  # 主诉
    },
    
    # 症状列表（必填）
    "symptoms": [
        "症状1",
        "症状2",
        "症状3"
    ],
    
    # 既往史（选填）
    "medical_history": [
        "既往疾病1",
        "既往疾病2"
    ],
    
    # 生命体征（选填）
    "vital_signs": {
        "血压": "120/80 mmHg",
        "心率": "75次/分",
        "体温": "36.5°C",
        "血氧饱和度": "98%"
    },
    
    # 医学影像（选填）
    "images": [
        "path/to/xray.jpg",
        "path/to/ct.jpg"
    ]
}
```

## 多模态输入

### 添加医学影像

```python
case_with_images = {
    "patient_info": {...},
    "symptoms": [...],
    
    # 添加影像文件路径
    "images": [
        "./images/chest_xray.jpg",
        "./images/ecg.png"
    ]
}

# 系统会自动分析影像
result = system.diagnose(case_with_images)
```

### 支持的影像类型

- X光片
- CT影像
- MRI影像
- 超声影像
- 心电图
- 其他医学影像

## 输出结果

### 结果结构

```python
result = {
    'case_data': {...},              # 原始病例数据（包含影像分析）
    'department_diagnoses': [...],   # 各科室诊断结果
    'consultation': {...},           # 会诊结果
    'summary': "..."                 # 格式化的会诊报告
}
```

### 各科室诊断结果

```python
department_diagnosis = {
    'department': '心脏科',
    'department_id': 'cardiology',
    'is_relevant': True,
    'relevance_score': 0.85,
    'diagnosis': '详细的诊断内容...',
    'confidence': 'high',
    'retrieved_knowledge': [...]
}
```

### 会诊结果

```python
consultation = {
    'consultation_report': '完整的会诊报告...',
    'participating_departments': ['心脏科', '呼吸科'],
    'total_departments_consulted': 2,
    'all_diagnoses': [...],
    'case_summary': '...'
}
```

## 自定义配置

### 修改科室配置

编辑 `config/departments.json`：

```json
{
  "departments": [
    {
      "id": "cardiology",
      "name": "心脏科",
      "name_en": "Cardiology",
      "description": "...",
      "specialties": ["冠心病", "心律失常", ...],
      "keywords": ["胸痛", "心悸", ...]
    }
  ]
}
```

### 添加知识库

在 `knowledge_base/{department_id}/` 目录下添加 `.txt` 文件：

```
knowledge_base/
  cardiology/
    基础知识.txt
    诊疗指南.txt
    病例分析.txt
```

系统会自动加载所有文本文件到向量数据库。

### 修改模型参数

编辑 `.env` 文件：

```bash
# 使用的模型
OPENAI_MODEL=gpt-4-turbo-preview
VISION_MODEL=gpt-4-vision-preview

# 温度参数
DOCTOR_TEMPERATURE=0.7        # 医生诊断温度
CONSULTATION_TEMPERATURE=0.3   # 会诊温度（更保守）

# RAG 参数
CHUNK_SIZE=500               # 文档块大小
CHUNK_OVERLAP=50             # 块重叠大小
TOP_K_RETRIEVAL=5            # 检索文档数量
```

## 高级用法

### 单独使用某个组件

#### 使用知识检索

```python
from rag.vector_store import VectorStore
from rag.retriever import KnowledgeRetriever

vector_store = VectorStore()
retriever = KnowledgeRetriever(vector_store)

# 检索知识
docs = retriever.retrieve(
    query="急性心肌梗死的诊断标准",
    department_id="cardiology",
    top_k=3
)
```

#### 使用多模态处理器

```python
from utils.multimodal import MultimodalProcessor

processor = MultimodalProcessor()

# 分析单张图像
result = processor.analyze_image(
    image_path="./xray.jpg",
    prompt="请分析这张胸部X光片",
    image_type="X光片"
)
```

#### 直接使用医生 Agent

```python
from agents.doctor_agent import DoctorAgent
from rag.retriever import KnowledgeRetriever

dept_info = {
    "id": "cardiology",
    "name": "心脏科",
    "name_en": "Cardiology",
    "description": "...",
    "specialties": [...],
    "keywords": [...]
}

agent = DoctorAgent(dept_info, retriever)
diagnosis = agent.diagnose(case_data)
```

## 故障排查

### 常见问题

1. **API Key 错误**
   - 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
   - 确认 API Key 有足够的额度

2. **知识库为空**
   - 首次运行会自动创建知识库
   - 检查 `knowledge_base/` 目录下是否有 `.txt` 文件
   - 删除 `chroma_db/` 目录后重新运行以重建知识库

3. **图像分析失败**
   - 检查图像文件路径是否正确
   - 确认使用的模型支持视觉功能
   - 检查图像文件格式（支持 jpg, png 等）

4. **导入错误**
   - 确保在项目根目录（A1文件夹）下运行
   - 检查是否安装了所有依赖包

### 日志和调试

系统会在控制台输出详细的运行信息：

```
- ✓ 表示成功完成
- - 表示跳过或不相关
- 错误信息会清晰显示
```

## 性能优化

### 提高响应速度

1. 减少 `TOP_K_RETRIEVAL` 数量（默认5）
2. 使用更快的模型（如 gpt-3.5-turbo）
3. 减少知识库文档数量

### 提高诊断准确性

1. 增加专业知识库内容
2. 使用更强大的模型（gpt-4）
3. 调整温度参数（降低以获得更保守的结果）

## 扩展系统

### 添加新科室

1. 在 `config/departments.json` 添加科室配置
2. 在 `knowledge_base/` 创建对应目录
3. 添加该科室的专业知识文档
4. 重启系统自动加载

### 自定义提示词

编辑 `utils/prompt_templates.py` 中的模板：

```python
DOCTOR_DIAGNOSIS_TEMPLATE = """
你的自定义提示词...
"""
```

## 注意事项

1. **仅供学习研究使用**：本系统不能替代专业医疗诊断
2. **数据隐私**：请勿使用真实患者数据
3. **API 费用**：使用 GPT-4 会产生较高费用，注意控制
4. **知识库质量**：诊断质量依赖于知识库的专业性和完整性

## 技术支持

如遇到问题，请检查：

1. Python 版本（建议 3.8+）
2. 依赖包版本
3. API Key 配置
4. 网络连接

更多信息请参考 `README.md`。
