# Agent Hospital - 可进化的模拟医院系统

基于论文 **"Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents"** (Tsinghua AIR) 实现的医疗AI模拟系统。

## 📋 系统概述

Agent Hospital 是一个完整的医疗模拟系统，实现了可进化学习的医生Agent：

- **病人Agent** - 从CMeIEV2数据集生成，包含715种疾病
- **护士Agent** - 负责分诊和医学检查
- **医生Agent** - 5个科室（心脏科、神经科、肿瘤科、呼吸科、消化科），可从治疗中学习进化
- **病例库** - 自动积累成功案例
- **经验库** - 从失败中生成经验规则

### 核心特性

✅ **8个事件完整治疗循环** - 疾病发作 → 分诊 → 挂号 → 问诊 → 检查 → 诊断 → 治疗 → 康复  
✅ **MedAgent-Zero** - 医生Agent从零开始，通过治疗病人不断进化  
✅ **知识自动积累** - 成功案例存入病例库，失败案例生成经验规则  
✅ **诊断准确率提升** - 随着治疗病人数增加，准确率持续提高  

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

### 3. 运行模拟

**方式1：可视化界面（推荐）🎨**

```bash
# 启动 Web 可视化界面
python start_hospital.py

# 或直接运行
python app_hospital.py
```

在浏览器中访问 `http://localhost:7860`，可以：
- 实时观察治疗过程
- 查看医生进化统计
- 可视化病例库和经验库
- 交互式生成和治疗病人

**方式2：命令行模式**

```bash
# 主程序 - 批量模拟
python RUN_AGENT_HOSPITAL.py

# 测试套件 - 验证功能
python test_agent_hospital.py

# 使用示例 - 学习使用
python example_usage.py
```

## 🏥 系统架构

```
Agent Hospital
├── frontend/                    # 前端组件层 ✨ NEW
│   ├── components/              # UI组件
│   │   ├── progress_bar.py      # 横向进度条组件
│   │   └── patient_card.py      # 患者卡片组件
│   ├── styles/                  # 样式系统
│   │   └── custom_css.py        # 自定义CSS样式
│   ├── README.md                # 组件文档
│   └── USAGE_EXAMPLE.md         # 使用示例
├── agents/                      # Agent层
│   ├── patient_agent.py         # 病人Agent
│   ├── nurse_agent.py          # 护士Agent（分诊+检查）
│   └── evolving_doctor_agent.py # 可进化医生Agent
├── knowledge/                   # 知识层
│   ├── medical_case_base.py    # 病例库
│   └── experience_base.py      # 经验库
├── simulation/                  # 模拟层
│   ├── agent_hospital.py       # 医院模拟器
│   └── patient_generator.py    # 病人生成器
└── datasets/                    # 数据集
    └── 高质量医疗样本集_20251118.json  # 715种疾病
```

### 医生进化机制

```
病人症状 → 检索病例库（相似案例）
        → 检索经验库（适用规则）
        → 检索知识库（专业知识）
        → LLM综合分析 → 生成诊断

治疗结果 → 成功：添加到病例库
        → 失败：反思生成新规则
```

## 🎨 可视化界面特性

启动 Web 界面后，您可以：

### 1. 横向进度条展示 ✨ **全新设计**
- 🎯 **8个步骤节点**：病例输入 → 智能分诊 → 挂号登记 → 医生问诊 → 医学检查 → AI诊断 → 治疗方案 → 康复评估
- 🌈 **现代化卡片设计**：渐变背景、圆形节点、连接线组成完整进度条
- 🎭 **动态状态展示**：
  - ✅ 绿色脉冲动画 - 已完成步骤
  - 🔵 蓝色脉冲动画 - 进行中步骤
  - 🔴 红色抖动动画 - 失败步骤
  - ⚪ 灰色 - 未执行步骤
- 🔍 **详情展开**：点击查看每个步骤的详细信息
- 📋 **批量展示**：支持同时显示多位患者的治疗卡片

### 2. 实时治疗观察
- 📝 查看完整的治疗日志
- 🏥 观察8个事件的治疗流程
- 👨‍⚕️ 看到每个Agent的决策过程

### 3. 医生进化统计
- 📊 各科室医生表现对比
- 📈 诊断准确率和治疗成功率
- 🎯 实时更新的统计图表

### 4. 知识库可视化
- 📚 病例库增长情况
- 🧠 经验库规则详情
- 🔍 按科室和疾病分类浏览

### 5. 交互式操作
- 🎛️ 调整病人数量和科室筛选
- 💾 保存当前状态
- 🗑️ 清空知识库重新训练
- 📊 显示所有历史记录或最近记录

## �📊 运行示例

### 可视化界面操作流程

1. 启动界面：`python start_hospital.py`
2. 点击"初始化系统"
3. 设置病人数量（如：5）
4. 选择科室（如：心脏科）
5. 点击"开始治疗"
6. 观察实时日志和统计图表

### 命令行测试医生进化

```bash
python test_agent_hospital.py --test evolution
```

输出示例：
```
第一批: 治疗5个病人
  诊断准确率: 65.0%
  治疗成功率: 60.0%

第二批: 再治疗5个病人  
  诊断准确率: 80.0%  ⬆ +15%
  治疗成功率: 75.0%  ⬆ +15%

病例库: 7个案例
经验库: 3条规则
```

### 批量模拟治疗

```bash
python RUN_AGENT_HOSPITAL.py
# 输入病人数量，如：20
```

结果自动保存到 `simulation_results/` 目录。

## 🎯 主要功能

### 1. 自动生成病人
从CMeIEV2数据集（715种疾病）自动生成病人Agent，包含真实的症状、病史。

### 2. 完整治疗流程
模拟8个事件：疾病发作 → 分诊 → 挂号 → 问诊 → 检查 → 诊断 → 治疗 → 康复评估。

### 3. 医生进化学习
- **成功案例** → 存入病例库，供后续参考
- **失败案例** → LLM反思，生成经验规则

### 4. 知识持续积累
- 病例库：`knowledge/case_base/*.json`
- 经验库：`knowledge/experience_base/*.json`
- 重启程序继续使用已有知识

## 📈 验证医生进化

观察关键指标：
- **诊断准确率** - 随治疗病人数提升
- **病例库增长** - 每次成功 +1
- **经验库增长** - 每次失败 +1
- **规则成功率** - 自动跟踪

## 🔧 自定义配置

### 添加新科室
编辑 `config/departments.json`:
```json
{
  "id": "new_dept",
  "name": "新科室名",
  "keywords": ["关键词1", "关键词2"]
}
```

### 调整病人生成
修改 `simulation/patient_generator.py` 中的生成逻辑。

## 📝 主要文件

| 文件 | 说明 |
|------|------|
| `app_hospital_streamlit.py` | 🎨 **可视化Web界面（Streamlit）** |
| `start_hospital.py` | 🚀 启动脚本 |
| `RUN_AGENT_HOSPITAL.py` | 命令行批量模拟 |
| `test_agent_hospital.py` | 测试脚本 |
| `example_usage.py` | 使用示例 |
| **frontend/** | **前端组件目录 ✨** |
| `frontend/components/progress_bar.py` | 横向进度条组件 |
| `frontend/components/patient_card.py` | 患者卡片组件 |
| `frontend/styles/custom_css.py` | 自定义CSS样式 |
| **agents/** | **Agent层** |
| `agents/patient_agent.py` | 病人Agent |
| `agents/nurse_agent.py` | 护士Agent |
| `agents/evolving_doctor_agent.py` | 医生Agent |
| **knowledge/** | **知识层** |
| `knowledge/medical_case_base.py` | 病例库 |
| `knowledge/experience_base.py` | 经验库 |
| **simulation/** | **模拟层** |
| `simulation/agent_hospital.py` | 医院模拟器 |
| `simulation/patient_generator.py` | 病人生成器 |

## 🎓 论文参考

```
Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents
Junkai Li, et al.
Institute for AI Industry Research (AIR), Tsinghua University, 2024
```

核心贡献：
- **SEAL范式** - Simulacrum-based Evolutionary Agent Learning
- **MedAgent-Zero** - 零标注数据的医生进化方法
- **闭环学习** - 从虚拟世界到真实世界的能力迁移

## ⚠️ 免责声明

本系统仅用于研究和教育目的，不应用于实际医疗诊断。

## 📄 许可证

本项目仅用于学术研究。

---

**版本**: 2.0 ✨ | **实现日期**: 2024-11-18 | **数据集**: CMeIEV2 (715疾病)

### 🎉 版本更新记录

**v2.0 (2024-11-18)** - 前端界面全面升级
- ✨ 新增横向进度条组件
- 🎨 现代化患者卡片设计
- 🎭 动态状态动画（脉冲、抖动）
- 📁 模块化前端组件结构
- 🔍 详情展开交互功能
- 📊 批量患者卡片展示

**v1.0 (2024-11-18)** - 初始版本
- 🏥 完整的Agent Hospital系统
- 🧠 医生进化学习机制
- 📚 病例库和经验库
- 🎨 基础Web可视化界面
