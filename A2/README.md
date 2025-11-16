# 智能多模态医疗诊断系统 - Streamlit版本

## 概述

这是一个基于Streamlit的智能医疗诊断系统前端应用，能够展示多个医生Agent的诊断过程和思考细节。

## 主要特性

- 🎨 **友好的Web界面**: 使用Streamlit构建的现代化Web界面
- 🏥 **多科室诊断**: 支持心脏科、神经科、肿瘤科、呼吸科、消化科等多个科室
- 🧠 **思考过程可视化**: 详细展示每个Agent的思考步骤和决策过程
- 📊 **实时进度显示**: 诊断过程中实时显示进度
- 💾 **报告导出**: 支持导出JSON和文本格式的诊断报告
- 🔍 **知识检索展示**: 显示RAG检索到的专业知识

## 文件结构

```
A2/
├── app.py                    # Streamlit主应用
├── start.py                  # 快捷启动脚本
├── medical_system.py         # 医疗诊断系统核心类
├── requirements.txt          # Python依赖
├── .env                      # 环境配置
├── agents/                   # Agent模块
│   ├── base_agent.py        # 基础Agent（增强版）
│   ├── doctor_agent.py      # 专科医生Agent（增强版）
│   └── consultation_agent.py # 会诊Agent（增强版）
├── config/                   # 配置文件
│   └── departments.json     # 科室配置
├── rag/                      # RAG模块
│   ├── vector_store.py      # 向量存储
│   └── retriever.py         # 知识检索器
└── utils/                    # 工具模块
    ├── embeddings.py        # 嵌入模型
    ├── multimodal.py        # 多模态处理
    └── prompt_templates.py  # 提示词模板
```

## 安装步骤

1. 确保已安装Python 3.8+

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量（编辑 `.env` 文件）：
```
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_api_base
OPENAI_MODEL=your_model_name
EMBEDDING_API_KEY=your_embedding_key
EMBEDDING_API_BASE=your_embedding_base
EMBEDDING_MODEL=your_embedding_model
```

## 运行应用

### 方法1: 使用快捷启动脚本（推荐）

在A2目录下运行：

```bash
python start.py
```

脚本会自动启动Streamlit应用并在浏览器中打开界面。

### 方法2: 直接启动Streamlit

在A2目录下运行：

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 使用说明

### 1. 输入病例信息

在左侧边栏中输入：
- **基本信息**: 年龄、性别、主诉
- **临床表现**: 患者的症状（每行一个）
- **既往史**: 患者的病史（每行一个）
- **生命体征**: 血压、心率、体温、血氧、呼吸频率

### 2. 开始诊断

点击"开始诊断"按钮，系统将：
1. 分析病例信息
2. 各科室独立诊断
3. 进行多学科会诊
4. 生成最终报告

### 3. 查看结果

诊断完成后，可以查看：

- **诊断统计**: 参与科室数、相关科室数、用时等
- **各科室诊断详情**: 
  - 每个科室的诊断意见
  - 相关度和置信度评分
  - 参考的专业知识
  - 详细的思考过程
- **多学科会诊报告**: 综合各科室意见的最终诊断
- **会诊专家思考过程**: 会诊专家的决策过程

### 4. 导出报告

可以下载：
- **完整报告 (JSON)**: 包含所有诊断细节
- **摘要报告 (TXT)**: 文本格式的诊断摘要

## 与A1版本的区别

### A1版本（命令行）
- 在控制台中输出诊断结果
- 文本格式，不易查看
- 缺少可视化展示

### A2版本（Streamlit）
- Web界面，直观易用
- 详细展示每个Agent的思考过程
- 实时进度显示
- 支持报告导出
- 更好的用户体验

## 核心功能说明

### Agent思考过程记录

增强的Agent类会记录每个思考步骤：
- 相关性分析
- 知识检索
- LLM请求和响应
- 诊断结论

### 可视化展示

- **思考步骤卡片**: 展示每个思考步骤的内容和时间
- **科室诊断卡片**: 用不同颜色区分相关和不相关科室
- **指标展示**: 相关度、置信度等关键指标
- **可折叠面板**: 详细信息可按需展开

### 实时进度

诊断过程中显示：
- 当前正在执行的步骤
- 进度百分比
- 预计剩余时间

## 技术栈

- **前端框架**: Streamlit
- **LLM**: OpenAI API兼容接口
- **向量数据库**: ChromaDB
- **RAG框架**: LangChain
- **嵌入模型**: BGE-Large-ZH

## 注意事项

1. 确保A1文件夹的知识库存在（A2会使用A1的知识库）
2. 确保API密钥配置正确
3. 首次运行时会初始化知识库，可能需要一些时间
4. 建议使用Chrome或Edge浏览器访问

## 故障排除

### 测试API连接

如果遇到"生成回复失败"或"NoneType"错误，请先测试API连接：

```bash
python test_api.py
```

这个脚本会检查：
- API配置是否正确
- API连接是否正常
- 模型是否可用
- 嵌入模型是否正常

### 常见错误

#### 1. "生成回复失败: 'NoneType' object is not subscriptable"
**原因:** API返回了空响应或None
**解决方法:**
- 运行 `python test_api.py` 测试API
- 检查.env文件中的配置：
  - `OPENAI_API_KEY` 是否正确
  - `OPENAI_API_BASE` 是否正确
  - `OPENAI_MODEL` 是否支持chat.completions格式
- 确认API余额充足
- 检查网络连接

#### 2. 系统初始化失败
- 检查.env文件配置
- 确认A1的knowledge_base文件夹存在
- 查看控制台错误信息

#### 3. 诊断失败
- 检查API密钥是否有效
- 确认网络连接正常
- 查看详细错误信息
- 检查模型是否支持所需功能

#### 4. 页面显示异常
- 刷新浏览器页面
- 清除浏览器缓存
- 重启Streamlit应用

## 未来改进

- [ ] 添加医学影像上传和分析
- [ ] 支持历史病例查询
- [ ] 增加用户认证和权限管理
- [ ] 添加更多科室
- [ ] 优化诊断速度
- [ ] 增加诊断准确率统计
