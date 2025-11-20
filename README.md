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
```

在浏览器中访问 `http://localhost:8501`，可以：
- 实时观察治疗过程
- 查看医生进化统计
- 可视化病例库和经验库
- 交互式生成和治疗病人

**方式2：控制台批量模拟 💻**

```bash
# 基础用法：模拟10个病人
python run_simulation.py -n 10

# 科室筛选：模拟20个心脏科病人
python run_simulation.py -n 20 -d 心脏科

# 显示详细过程：观察完整治疗流程
python run_simulation.py -n 5 -v

# 大批量模拟：100个病人（不显示详细过程）
python run_simulation.py -n 100
```

**方式3：功能测试**

```bash
# 完整测试套件
python test_agent_hospital.py

# 单个病人治疗测试
python test_agent_hospital.py --test single

# 医生进化测试
python test_agent_hospital.py --test evolution
```

## 🏥 系统架构

```
Agent Hospital
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

### 1. 实时治疗观察
- 📝 查看完整的治疗日志
- 🏥 观察8个事件的治疗流程
- 👨‍⚕️ 看到每个Agent的决策过程

### 2. 医生进化统计
- 📊 各科室医生表现对比
- 📈 诊断准确率和治疗成功率
- 🎯 实时更新的统计图表

### 3. 知识库可视化
- 📚 病例库增长情况
- 🧠 经验库规则详情
- 🔍 按科室和疾病分类浏览

### 4. 交互式操作
- 🎛️ 调整病人数量和科室筛选
- 💾 保存当前状态
- �️ 清空知识库重新训练

## 📊 运行示例

### 控制台批量模拟（推荐用于数据生成）

```bash
# 快速模拟10个病人
python run_simulation.py -n 10

# 输出示例：
# ✅ 治疗成功: 8/10 (80.0%)
# 🎯 诊断正确: 7/10 (70.0%)
# 📚 病例库: 15 个案例
# 📚 经验库: 5 条规则
```

**高级用法：**
```bash
# 心脏科专项模拟（50个病人）
python run_simulation.py -n 50 -d 心脏科

# 大批量模拟（无详细日志，仅统计）
python run_simulation.py -n 200

# 详细观察治疗过程（适合学习）
python run_simulation.py -n 3 -v
```

结果自动保存到 `simulation_results/` 目录：
- `simulation_*.json` - 完整治疗记录
- `summary_*.json` - 统计摘要
- `report_*.txt` - 可读文本报告

### 可视化界面操作

1. 启动：`python start_hospital.py`
2. 初始化系统
3. 设置参数（病人数、科室）
4. 开始治疗
5. 实时观察流程和统计

### 功能测试

```bash
# 医生进化测试
python test_agent_hospital.py --test evolution

# 输出示例：
# 第一批: 5个病人 → 准确率 65.0%
# 第二批: 5个病人 → 准确率 80.0% ⬆ +15%
```

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
| `start_hospital.py` | 🚀 启动Web可视化界面 |
| `run_simulation.py` | 💻 **控制台批量模拟（推荐）** |
| `test_agent_hospital.py` | 🧪 功能测试套件 |
| `frontend/app.py` | 🎨 Streamlit可视化主程序 |
| `simulation/agent_hospital.py` | 🏥 医院模拟核心 |
| `agents/evolving_doctor_agent.py` | 👨‍⚕️ 可进化医生Agent |
| `agents/nurse_agent.py` | 👩‍⚕️ 护士Agent（分诊+检查） |
| `simulation/patient_generator.py` | 🤒 病人生成器 |
| `knowledge/medical_case_base.py` | 📚 病例库 |
| `knowledge/experience_base.py` | 🧠 经验库 |

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

**版本**: 1.0 | **实现日期**: 2024-11-18 | **数据集**: CMeIEV2 (715疾病)
