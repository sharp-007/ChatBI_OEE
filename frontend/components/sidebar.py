import streamlit as st
from datetime import date, timedelta


def render_sidebar():
    """渲染侧边栏：日期筛选和系统信息"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
        st.title("ChatBI OEE")
        st.caption("智能对话式OEE分析平台")

        st.divider()

        st.subheader("📅 数据筛选")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=date(2026, 1, 1),
                min_value=date(2026, 1, 1),
                max_value=date(2026, 3, 31),
            )
        with col2:
            end_date = st.date_input(
                "结束日期",
                value=date(2026, 3, 31),
                min_value=date(2026, 1, 1),
                max_value=date(2026, 3, 31),
            )

        group_by = st.selectbox(
            "趋势聚合维度",
            options=["day", "week", "month"],
            format_func=lambda x: {"day": "按天", "week": "按周", "month": "按月"}[x],
            index=2,
        )

        st.divider()

        st.subheader("💡 提问示例")
        examples = [
            "本月OEE最高的设备是哪台？",
            "一车间3月份的OEE趋势如何？",
            "哪台设备的停机时间最长？",
            "各车间的质量率对比情况",
            "2月份非计划停机的主要原因是什么？",
            "注塑机的可用率和性能率表现",
        ]
        for ex in examples:
            if st.button(ex, key=f"example_{ex}", use_container_width=True):
                st.session_state["prefill_question"] = ex

        st.divider()
        st.caption("Powered by Qwen + FastAPI + Streamlit")

    return str(start_date), str(end_date), group_by
