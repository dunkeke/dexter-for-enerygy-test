from __future__ import annotations

import streamlit as st

from backend.agent.energy_agent import build_energy_commentary
from backend.data.yf_adapter import SYMBOLS, fetch_history, latest_snapshot

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
        latest = data.iloc[-1]
        st.metric("最新收盘价", f"{latest['close']:.2f}")
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
