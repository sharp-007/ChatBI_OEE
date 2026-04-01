import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="对话查询 - ChatBI OEE", page_icon="💬", layout="wide")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.charts import render_chart


st.title("💬 对话查询")
st.caption("用自然语言提问，AI 自动查询数据库并可视化展示")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.subheader("💡 提问示例")
    examples = [
        "本月OEE最高的设备是哪台？",
        "一车间3月份的OEE趋势如何？",
        "哪台设备的停机时间最长？",
        "各车间的质量率对比",
        "2月份非计划停机的主要原因",
        "注塑机的可用率和性能率表现",
        "2026年1月各设备的产量统计",
        "哪个产线的不良率最高？",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill_question"] = ex
            st.rerun()

    st.divider()
    if st.button("🗑️ 清空对话记录", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.caption("Powered by Qwen + FastAPI")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg:
            render_chart(msg["chart_config"], msg["chart_data"])
        if "sql" in msg:
            with st.expander("查看SQL"):
                st.code(msg["sql"], language="sql")
        if "dataframe" in msg:
            with st.expander("查看数据表"):
                st.dataframe(pd.DataFrame(msg["dataframe"]), use_container_width=True)

prefill = st.session_state.pop("prefill_question", None)
prompt = st.chat_input("请输入你的数据分析问题...", key="chat_input")

if prefill:
    prompt = prefill

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("正在分析数据..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/chat",
                    json={"question": prompt},
                    timeout=60,
                )

                if response.status_code == 200:
                    result = response.json()

                    if result.get("success"):
                        st.markdown(result["interpretation"])

                        chart_config = result.get("chart_config", {})
                        data = result.get("data", {})
                        if data.get("rows"):
                            render_chart(chart_config, data)

                        with st.expander("查看生成的SQL"):
                            st.code(result["sql"], language="sql")

                        with st.expander(f"查看数据表 ({data.get('row_count', 0)} 行)"):
                            st.dataframe(
                                pd.DataFrame(data.get("rows", [])),
                                use_container_width=True,
                            )

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": result["interpretation"],
                            "sql": result["sql"],
                            "chart_config": chart_config,
                            "chart_data": data,
                            "dataframe": data.get("rows", []),
                        })
                    else:
                        error_msg = f"查询失败: {result.get('error', '未知错误')}"
                        st.error(error_msg)
                        if result.get("sql"):
                            with st.expander("查看生成的SQL"):
                                st.code(result["sql"], language="sql")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg,
                        })
                else:
                    error_msg = f"API请求失败 (HTTP {response.status_code})"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                    })
            except requests.exceptions.ConnectionError:
                error_msg = (
                    "⚠️ 无法连接到后端API服务。\n\n"
                    "请确保已启动 FastAPI 后端：\n"
                    "```\ncd ChatBI_OEE\n"
                    "python -m backend.app.main\n```"
                )
                st.warning(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                })
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                })
