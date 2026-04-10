"""
Recent changes engine.

Primary responsibility:
- detect notable recent technical developments
- summarize the last few meaningful state changes
"""

from __future__ import annotations

from typing import List

import pandas as pd


def _latest_crossed_above(series_a: pd.Series, series_b: pd.Series, lookback: int = 10) -> bool:
    """
    Return True if series_a crossed above series_b within the recent lookback window.
    """
    if len(series_a) < 2 or len(series_b) < 2:
        return False

    diff = series_a - series_b
    crossed = (diff > 0) & (diff.shift(1) <= 0)

    return bool(crossed.tail(lookback).fillna(False).any())


def _latest_crossed_below(series_a: pd.Series, series_b: pd.Series, lookback: int = 10) -> bool:
    """
    Return True if series_a crossed below series_b within the recent lookback window.
    """
    if len(series_a) < 2 or len(series_b) < 2:
        return False

    diff = series_a - series_b
    crossed = (diff < 0) & (diff.shift(1) >= 0)

    return bool(crossed.tail(lookback).fillna(False).any())


def build_recent_changes(df: pd.DataFrame, lookback: int = 10) -> List[str]:
    """
    Build a readable list of recent technical developments.
    """
    changes: list[str] = []

    if {"Close", "SMA_50"}.issubset(df.columns):
        if _latest_crossed_above(df["Close"], df["SMA_50"], lookback=lookback):
            changes.append("Price reclaimed the 50-day moving average recently.")
        elif _latest_crossed_below(df["Close"], df["SMA_50"], lookback=lookback):
            changes.append("Price lost the 50-day moving average recently.")

    if {"Close", "SMA_20"}.issubset(df.columns):
        if _latest_crossed_above(df["Close"], df["SMA_20"], lookback=lookback):
            changes.append("Price moved back above the 20-day moving average.")
        elif _latest_crossed_below(df["Close"], df["SMA_20"], lookback=lookback):
            changes.append("Price slipped below the 20-day moving average.")

    if "RSI_14" in df.columns:
        rsi = df["RSI_14"]
        if _latest_crossed_above(rsi, pd.Series(50, index=rsi.index), lookback=lookback):
            changes.append("RSI moved back above 50, indicating improving momentum.")
        elif _latest_crossed_below(rsi, pd.Series(50, index=rsi.index), lookback=lookback):
            changes.append("RSI moved below 50, indicating weaker momentum.")

    if {"MACD_line", "MACD_signal"}.issubset(df.columns):
        if _latest_crossed_above(df["MACD_line"], df["MACD_signal"], lookback=lookback):
            changes.append("MACD triggered a recent bullish crossover.")
        elif _latest_crossed_below(df["MACD_line"], df["MACD_signal"], lookback=lookback):
            changes.append("MACD triggered a recent bearish crossover.")

    if "Breakout_Confirmed" in df.columns and bool(df["Breakout_Confirmed"].tail(lookback).fillna(False).any()):
        changes.append("Price recently confirmed a breakout above prior resistance.")

    if "Breakdown_Confirmed" in df.columns and bool(df["Breakdown_Confirmed"].tail(lookback).fillna(False).any()):
        changes.append("Price recently confirmed a breakdown below prior support.")

    if "ATR_expanding" in df.columns and bool(df["ATR_expanding"].tail(3).fillna(False).all()):
        changes.append("Volatility has been expanding over the last few bars.")

    if "BB_width_contracting" in df.columns and bool(df["BB_width_contracting"].tail(3).fillna(False).all()):
        changes.append("Bollinger Band width has been contracting, suggesting compression.")

    if "OBV_above_MA" in df.columns:
        recent_obv = df["OBV_above_MA"].tail(lookback)
        if recent_obv.iloc[-1] and not bool(recent_obv.iloc[:-1].fillna(False).all()):
            changes.append("On-balance volume has improved relative to its recent average.")

    return changes[:6]
