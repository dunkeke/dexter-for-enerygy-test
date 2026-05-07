from __future__ import annotations

from typing import List


def build_energy_commentary(question: str, snapshots: List[dict]) -> str:
    lines = [f"问题：{question}", "", "快速市场解读："]
    for snap in snapshots:
        if snap.get("status") != "ok":
            lines.append(f"- {snap['symbol']}: 暂无数据")
            continue
        direction = "上涨" if snap["change"] >= 0 else "下跌"
        lines.append(
            f"- {snap['symbol']}: 最新价 {snap['close']:.2f}, 日变动 {snap['change']:+.2f} ({snap['change_pct']:+.2f}%), {direction}。"
        )

    lines.append("")
    lines.append("提示：当前版本为 PoC（yfinance 数据源）。交易前请做二次校验。")
    return "\n".join(lines)
