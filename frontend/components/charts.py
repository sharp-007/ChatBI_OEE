import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def render_chart(chart_config: dict, data: dict):
    """根据图表配置和数据渲染图表"""
    if not data.get("rows"):
        st.info("暂无数据")
        return

    df = pd.DataFrame(data["rows"])
    chart_type = chart_config.get("chart_type", "table")
    title = chart_config.get("title", "查询结果")
    x_field = chart_config.get("x_field", "")
    y_field = chart_config.get("y_field", "")

    try:
        if chart_type == "bar":
            _render_bar(df, x_field, y_field, title)
        elif chart_type == "line":
            _render_line(df, x_field, y_field, title)
        elif chart_type == "pie":
            _render_pie(df, x_field, y_field, title)
        elif chart_type == "gauge":
            _render_gauge(df, y_field, title)
        elif chart_type == "scatter":
            _render_scatter(df, x_field, y_field, title)
        else:
            _render_table(df, title)
    except Exception:
        _render_table(df, title)


def _render_bar(df: pd.DataFrame, x_field: str, y_field: str, title: str):
    y_fields = [f.strip() for f in y_field.split(",")]
    valid_y = [f for f in y_fields if f in df.columns]

    if not valid_y or x_field not in df.columns:
        _render_table(df, title)
        return

    if len(valid_y) == 1:
        fig = px.bar(df, x=x_field, y=valid_y[0], title=title,
                     color_discrete_sequence=px.colors.qualitative.Set2)
    else:
        fig = go.Figure()
        colors = px.colors.qualitative.Set2
        for i, col in enumerate(valid_y):
            fig.add_trace(go.Bar(
                name=col, x=df[x_field], y=df[col],
                marker_color=colors[i % len(colors)],
            ))
        fig.update_layout(title=title, barmode="group")

    fig.update_layout(
        xaxis_tickangle=-45,
        height=450,
        margin=dict(l=40, r=40, t=60, b=80),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_line(df: pd.DataFrame, x_field: str, y_field: str, title: str):
    y_fields = [f.strip() for f in y_field.split(",")]
    valid_y = [f for f in y_fields if f in df.columns]

    if not valid_y or x_field not in df.columns:
        _render_table(df, title)
        return

    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, col in enumerate(valid_y):
        fig.add_trace(go.Scatter(
            x=df[x_field], y=df[col], mode="lines+markers",
            name=col, line=dict(color=colors[i % len(colors)], width=2),
        ))

    fig.update_layout(title=title, height=450, margin=dict(l=40, r=40, t=60, b=60))
    st.plotly_chart(fig, use_container_width=True)


def _render_pie(df: pd.DataFrame, x_field: str, y_field: str, title: str):
    if x_field not in df.columns or y_field not in df.columns:
        _render_table(df, title)
        return

    fig = px.pie(df, names=x_field, values=y_field, title=title,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


def _render_gauge(df: pd.DataFrame, y_field: str, title: str):
    if y_field not in df.columns:
        _render_table(df, title)
        return

    value = float(df[y_field].iloc[0])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title},
        delta={"reference": 85, "increasing": {"color": "#2ecc71"}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#3498db"},
            "steps": [
                {"range": [0, 60], "color": "#e74c3c30"},
                {"range": [60, 75], "color": "#f39c1230"},
                {"range": [75, 85], "color": "#f1c40f30"},
                {"range": [85, 100], "color": "#2ecc7130"},
            ],
            "threshold": {
                "line": {"color": "#e74c3c", "width": 3},
                "thickness": 0.8,
                "value": 85,
            },
        },
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


def _render_scatter(df: pd.DataFrame, x_field: str, y_field: str, title: str):
    if x_field not in df.columns or y_field not in df.columns:
        _render_table(df, title)
        return

    fig = px.scatter(df, x=x_field, y=y_field, title=title,
                     color_discrete_sequence=["#3498db"])
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


def _render_table(df: pd.DataFrame, title: str):
    st.subheader(title)
    st.dataframe(df, use_container_width=True, height=400)


def render_oee_gauges(overview: dict):
    """渲染OEE四个仪表盘"""
    metrics = [
        ("OEE", overview.get("avg_oee", 0), 85),
        ("可用率", overview.get("avg_availability", 0), 90),
        ("性能率", overview.get("avg_performance", 0), 95),
        ("质量率", overview.get("avg_quality", 0), 99),
    ]

    cols = st.columns(4)
    colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6"]

    for i, (name, value, target) in enumerate(metrics):
        with cols[i]:
            val = float(value) if value else 0
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={"text": name, "font": {"size": 16}},
                number={"suffix": "%", "font": {"size": 28}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar": {"color": colors[i]},
                    "steps": [
                        {"range": [0, 60], "color": "#ff634720"},
                        {"range": [60, target], "color": "#ffd70020"},
                        {"range": [target, 100], "color": "#32cd3220"},
                    ],
                    "threshold": {
                        "line": {"color": "#e74c3c", "width": 2},
                        "thickness": 0.75,
                        "value": target,
                    },
                },
            ))
            fig.update_layout(
                height=220,
                margin=dict(l=20, r=20, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_oee_trend(trend_data: list[dict]):
    """渲染OEE趋势折线图"""
    if not trend_data:
        st.info("暂无趋势数据")
        return

    df = pd.DataFrame(trend_data)
    date_col = df.columns[0]

    fig = go.Figure()
    metrics = {"OEE": "#3498db", "可用率": "#2ecc71", "性能率": "#e67e22", "质量率": "#9b59b6"}

    for name, color in metrics.items():
        if name in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col], y=df[name],
                mode="lines+markers", name=name,
                line=dict(color=color, width=2),
            ))

    fig.add_hline(y=85, line_dash="dash", line_color="#e74c3c",
                  annotation_text="世界级OEE (85%)")
    fig.update_layout(
        title="OEE趋势",
        xaxis_title=date_col,
        yaxis_title="百分比 (%)",
        height=400,
        margin=dict(l=40, r=40, t=60, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_equipment_ranking(ranking_data: list[dict]):
    """渲染设备OEE排名柱状图"""
    if not ranking_data:
        st.info("暂无排名数据")
        return

    df = pd.DataFrame(ranking_data)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df["设备名称"], x=df["OEE"],
        orientation="h", name="OEE",
        marker_color=["#2ecc71" if v >= 85 else "#f39c12" if v >= 70 else "#e74c3c"
                       for v in df["OEE"]],
        text=[f"{v}%" for v in df["OEE"]],
        textposition="auto",
    ))

    fig.add_vline(x=85, line_dash="dash", line_color="#e74c3c",
                  annotation_text="85%")
    fig.update_layout(
        title="设备OEE排名",
        xaxis_title="OEE (%)",
        height=max(300, len(df) * 45),
        margin=dict(l=120, r=40, t=60, b=40),
        yaxis=dict(categoryorder="total ascending"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_downtime_pie(downtime_data: list[dict]):
    """渲染停机分类饼图"""
    if not downtime_data:
        st.info("暂无停机数据")
        return

    df = pd.DataFrame(downtime_data)
    fig = px.pie(
        df, names="停机分类", values="总停机时长_分钟",
        title="停机原因分布",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
