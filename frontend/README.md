# Agent Hospital Frontend

模块化的 Streamlit 前端界面

## 📁 项目结构

```
frontend/
├── app.py                      # 主入口文件
├── state/                      # 状态管理
│   ├── __init__.py
│   └── session_state.py       # Session State 初始化
├── components/                 # 可复用组件
│   ├── __init__.py
│   ├── sidebar.py             # 侧边栏组件
│   └── treatment_flow.py      # 治疗流程可视化组件
├── views/                      # 页面视图模块
│   ├── __init__.py
│   ├── treatment_page.py      # 治疗流程页面
│   ├── statistics_page.py     # 统计页面
│   ├── case_base_page.py      # 病例库页面
│   ├── experience_base_page.py # 经验库页面
│   └── usage_guide_page.py    # 使用说明页面
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── hospital_manager.py    # 医院初始化和管理
│   └── data_utils.py          # 数据处理和统计
└── README.md                   # 本文档
```

## 🚀 启动方式

使用项目根目录的启动脚本：

```bash
python start_hospital.py
```

或者直接运行：

```bash
streamlit run frontend/app.py
```

## 📝 模块说明

### 1. **app.py** - 主入口
- 页面配置
- Session State 初始化
- 布局和标签页管理
- 组件和页面渲染

### 2. **state/** - 状态管理
- `session_state.py`: 统一管理所有 session state 变量

### 3. **components/** - 可复用组件
- `sidebar.py`: 侧边栏控制面板（初始化、治疗设置、系统管理）
- `treatment_flow.py`: 治疗流程可视化（8步治疗流程展示）

### 4. **views/** - 页面视图模块
- `treatment_page.py`: 实时治疗流程可视化
- `statistics_page.py`: 医院统计信息和图表
- `case_base_page.py`: 病例库详情和查看
- `experience_base_page.py`: 经验库详情和查看
- `usage_guide_page.py`: 使用说明文档

### 5. **utils/** - 工具函数
- `hospital_manager.py`: 医院系统初始化、保存、清空等管理功能
- `data_utils.py`: 数据处理、统计计算、图表生成等

## ✨ 优势

### 相比原始单文件版本：

1. **模块化**: 功能清晰分离，易于维护
2. **可复用**: 组件可在多处复用
3. **可测试**: 各模块可独立测试
4. **可扩展**: 新增页面或功能更简单
5. **可读性**: 代码结构清晰，易于理解

## 🔧 开发指南

### 添加新页面示例

1. 在 `views/` 创建 `my_page.py`：
```python
import streamlit as st

def render_my_page():
    st.subheader("我的新页面")
    # 页面内容...
```

2. 在 `app.py` 中引入：
```python
from frontend.views.my_page import render_my_page
```

3. 在 `app.py` 中添加到标签页：
```python
# ...
if page == "我的新页面":
    render_my_page()
# ...
```

### 添加新组件

1. 在 `components/` 目录创建新的组件文件
2. 实现 `render_xxx()` 或相关函数
3. 在需要的地方导入使用

### 添加新工具函数

1. 在 `utils/` 目录创建新的工具文件
2. 实现相关函数
3. 在需要的地方导入使用

## 📦 依赖

与主项目相同，见根目录 `requirements.txt`

## 🆚 与原版对比

- **原版**: `app_hospital_streamlit.py` (938行单文件)
- **新版**: 模块化结构，分布在多个文件中
- **功能**: 完全一致
- **优势**: 更易维护和扩展
