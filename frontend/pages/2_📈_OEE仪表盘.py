import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="OEE仪表盘 - ChatBI OEE", page_icon="📈", layout="wide")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.charts import (
    render_oee_gauges,
    render_oee_trend,
    render_equipment_ranking,
    render_downtime_pie,
)

st.title("📈 OEE 可视化仪表盘")


def fetch_api(endpoint: str, params: dict = None):
    """调用后端API"""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/v1{endpoint}", params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


with st.sidebar:
    st.subheader("📅 数据筛选")

    production_line = st.selectbox(
        "🏭 产线",
        options=["全部", "A线", "B线", "C线", "D线", "E线", "F线"],
        index=0,
    )

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

    refresh = st.button("🔄 刷新数据", use_container_width=True)

    st.divider()
    st.caption("Powered by Qwen + FastAPI")

params = {
    "start_date": str(start_date),
    "end_date": str(end_date),
    "production_line": "" if production_line == "全部" else production_line,
}

overview = fetch_api("/oee/overview", params)
if overview is None:
    st.warning(
        "⚠️ 无法连接到后端API服务。请确保已启动 FastAPI 后端：\n\n"
        "```\npython -m backend.app.main\n```"
    )
    st.stop()

# ====== 第一行: OEE 概览仪表盘 ======
st.subheader("🎯 OEE 概览")
render_oee_gauges(overview)

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    total_output = overview.get("total_output", 0) or 0
    st.metric("总产出", f"{total_output:,}")
with col_b:
    total_good = overview.get("total_good", 0) or 0
    st.metric("合格数", f"{total_good:,}")
with col_c:
    total_defect = overview.get("total_defect", 0) or 0
    st.metric("不良数", f"{total_defect:,}")
with col_d:
    record_count = overview.get("record_count", 0) or 0
    st.metric("记录数", f"{record_count:,}")

st.divider()

# ====== 第二行: OEE 趋势 ======
st.subheader("📉 OEE 趋势分析")
trend_params = {**params, "group_by": group_by}
trend_data = fetch_api("/oee/trend", trend_params)
if trend_data:
    render_oee_trend(trend_data)

st.divider()

# ====== 第三行: 设备排名 + 车间对比 ======
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 设备OEE排名")
    ranking_data = fetch_api("/oee/equipment-ranking", params)
    if ranking_data:
        render_equipment_ranking(ranking_data)

with col_right:
    st.subheader("🏭 车间OEE对比")
    workshop_data = fetch_api("/oee/workshop-summary", params)
    if workshop_data:
        df_ws = pd.DataFrame(workshop_data)
        st.dataframe(
            df_ws.style.format({
                "OEE": "{:.1f}%",
                "可用率": "{:.1f}%",
                "性能率": "{:.1f}%",
                "质量率": "{:.1f}%",
            }).background_gradient(subset=["OEE"], cmap="RdYlGn", vmin=60, vmax=90),
            use_container_width=True,
            height=400,
        )

st.divider()

# ====== 第四行: 停机分析 ======
st.subheader("⏱️ 停机分析")
downtime_data = fetch_api("/oee/downtime-analysis", params)

if downtime_data:
    col_dt1, col_dt2 = st.columns(2)

    with col_dt1:
        st.markdown("**停机原因分布**")
        if downtime_data.get("by_category"):
            render_downtime_pie(downtime_data["by_category"])

    with col_dt2:
        st.markdown("**设备停机时长排名**")
        if downtime_data.get("by_equipment"):
            df_dt = pd.DataFrame(downtime_data["by_equipment"])
            df_dt = df_dt.sort_values("总停机时长_分钟", ascending=True)
            palette = px.colors.qualitative.Set2
            workshops = df_dt["车间"].unique().tolist()
            color_map = {w: palette[i % len(palette)] for i, w in enumerate(workshops)}

            fig = go.Figure()
            shown_legend = set()
            for _, row in df_dt.iterrows():
                ws = row["车间"]
                fig.add_trace(go.Bar(
                    x=[row["总停机时长_分钟"]],
                    y=[row["设备名称"]],
                    orientation="h",
                    marker_color=color_map[ws],
                    name=ws,
                    legendgroup=ws,
                    showlegend=ws not in shown_legend,
                    text=[f"{row['总停机时长_分钟']:.0f}"],
                    textposition="auto",
                ))
                shown_legend.add(ws)

            chart_height = max(360, len(df_dt) * 36)
            fig.update_layout(
                title="设备停机时长排名",
                barmode="stack",
                height=chart_height,
                bargap=0.2,
                xaxis_title="停机时长 (分钟)",
                yaxis=dict(type="category"),
                margin=dict(l=120, r=20, t=40, b=40),
                legend=dict(title="车间"),
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()

# ====== 第五行: 损失分析 ======
st.subheader("📊 六大损失分析")
loss_data = fetch_api("/oee/loss-analysis", params)
if loss_data:
    df_loss = pd.DataFrame(loss_data)
    st.dataframe(
        df_loss.style.background_gradient(
            subset=["可用性损失_分钟", "性能损失_分钟", "质量损失_分钟"],
            cmap="Reds",
        ),
        use_container_width=True,
    )
