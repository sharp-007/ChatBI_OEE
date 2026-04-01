import streamlit as st

st.set_page_config(
    page_title="ChatBI OEE - 智能OEE分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 ChatBI OEE 智能分析平台")
st.markdown("---")

st.markdown("""
### 欢迎使用 ChatBI OEE 智能分析平台

本平台集成了 **自然语言查询** 和 **OEE可视化仪表盘** 两大核心功能：

- **💬 对话查询**：使用自然语言提问，系统自动生成SQL查询并可视化展示结果
- **📈 OEE仪表盘**：实时查看设备综合效率（OEE）指标、趋势和停机分析

---

#### 快速开始

👈 请从左侧导航栏选择功能页面：

| 页面 | 功能 |
|------|------|
| 💬 对话查询 | 用自然语言提问，获取数据分析结果 |
| 📈 OEE仪表盘 | 查看OEE概览、趋势、设备排名、停机分析 |

#### OEE 知识

**OEE（Overall Equipment Effectiveness）** 是衡量设备综合效率的国际通用指标：

$$OEE = 可用率 \\times 性能率 \\times 质量率$$

| 等级 | OEE范围 | 说明 |
|------|---------|------|
| 世界级 | ≥ 85% | 达到行业顶尖水平 |
| 良好 | 70%~85% | 有一定改进空间 |
| 需改善 | < 70% | 存在较大改进空间 |
""")
