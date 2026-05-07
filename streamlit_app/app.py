from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure repository root is importable when Streamlit runs from streamlit_app/
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.agent.energy_agent import build_energy_commentary
from backend.data.yf_adapter import SYMBOLS, fetch_history, latest_snapshot


def extract_latest_close(data: pd.DataFrame) -> float | None:
    close_data = data.get("close")
    if close_data is None:
        return None

    if isinstance(close_data, pd.DataFrame):
        last_row = close_data.iloc[-1].dropna()
        if last_row.empty:
            return None
        return float(last_row.iloc[0])

    close_series = pd.to_numeric(close_data, errors="coerce").dropna()
    if close_series.empty:
        return None
    return float(close_series.iloc[-1])


st.set_page_config(page_title="Energy Trading Agent PoC", layout="wide")
st.title("Energy Trading Agent (PoC)")
st.caption("覆盖品种：Brent / WTI / Henry Hub / TTF")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    symbol = st.selectbox("选择品种", list(SYMBOLS.keys()))
with col2:
    period = st.selectbox("周期", ["1mo", "3mo", "6mo", "1y"], index=2)
with col3:
    interval = st.selectbox("频率", ["1d", "1h"], index=0)

if st.button("刷新行情"):
    st.session_state["refresh"] = True

if st.session_state.get("refresh", True):
    data = fetch_history(symbol, period=period, interval=interval)
    if data.empty:
        st.warning("未拉取到数据，请稍后再试或检查 ticker 可用性。")
    else:
        close_value = extract_latest_close(data)
        if close_value is None:
            st.warning("无法解析最新收盘价。")
        else:
            st.metric("最新收盘价", f"{close_value:.2f}")
        st.line_chart(data["close"])
        st.dataframe(data.tail(20), use_container_width=True)

st.divider()
st.subheader("研究问答")
question = st.text_input("输入你的问题", "请概览四个品种今天的价格表现")

if st.button("生成解读"):
    snapshots = [latest_snapshot(name) for name in SYMBOLS.keys()]
    answer = build_energy_commentary(question, snapshots)
    st.markdown("### Agent 输出")
    st.text(answer)

st.caption("运行方式：streamlit run streamlit_app/app.py")
