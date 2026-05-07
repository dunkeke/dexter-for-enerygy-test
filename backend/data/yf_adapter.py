from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class CommoditySymbol:
    code: str
    label: str
    ticker: str


SYMBOLS: Dict[str, CommoditySymbol] = {
    "Brent": CommoditySymbol("Brent", "Brent Crude", "BZ=F"),
    "WTI": CommoditySymbol("WTI", "WTI Crude", "CL=F"),
    "Henry Hub": CommoditySymbol("Henry Hub", "Henry Hub Nat Gas", "NG=F"),
    "TTF": CommoditySymbol("TTF", "Dutch TTF Gas", "TTF=F"),
}


def fetch_history(symbol_name: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    symbol = SYMBOLS[symbol_name]
    df = yf.download(symbol.ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if df.empty:
        return pd.DataFrame()

    df = df.rename(columns=str.lower)
    df.index = pd.to_datetime(df.index)
    df["symbol"] = symbol.code
    df["source"] = "yfinance"
    df["ingested_at"] = datetime.now(timezone.utc)
    return df


def latest_snapshot(symbol_name: str) -> dict:
    df = fetch_history(symbol_name, period="5d", interval="1d")
    if df.empty:
        return {"symbol": symbol_name, "status": "no_data"}

    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    close = float(last["close"])
    prev_close = float(prev["close"])
    change = close - prev_close
    pct = (change / prev_close * 100) if prev_close else 0.0
    return {
        "symbol": symbol_name,
        "close": close,
        "change": change,
        "change_pct": pct,
        "timestamp": str(df.index[-1]),
        "status": "ok",
    }
