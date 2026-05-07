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


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        # For single ticker downloads, first level is OHLCV and second level is ticker.
        # Keep first level so downstream access is stable (close/open/high/low/volume).
        df.columns = [str(col[0]).lower() for col in df.columns]
    else:
        df.columns = [str(col).lower() for col in df.columns]
    return df


def fetch_history(symbol_name: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    symbol = SYMBOLS[symbol_name]
    df = yf.download(symbol.ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if df.empty:
        return pd.DataFrame()

    df = _normalize_columns(df)
    if "close" not in df.columns:
        return pd.DataFrame()

    df.index = pd.to_datetime(df.index)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])
    if df.empty:
        return pd.DataFrame()

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
