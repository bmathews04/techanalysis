"""
Momentum indicator calculations.

Primary responsibility:
- RSI
- MACD
- basic momentum change features
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.settings import ROLLING_WINDOWS


def add_rsi(
    df: pd.DataFrame,
    column: str = "Close",
    window: int = ROLLING_WINDOWS["rsi"],
) -> pd.DataFrame:
    """
    Add Relative Strength Index (RSI).

    Uses Wilder-style smoothing via exponential moving averages.
    """
    out = df.copy()

    delta = out[column].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["RSI_14"] = 100 - (100 / (1 + rs))

    # Handle edge cases explicitly
    out.loc[(avg_loss == 0) & (avg_gain > 0), "RSI_14"] = 100
    out.loc[(avg_gain == 0) & (avg_loss > 0), "RSI_14"] = 0

    return out


def add_macd(
    df: pd.DataFrame,
    column: str = "Close",
    fast: int = ROLLING_WINDOWS["macd_fast"],
    slow: int = ROLLING_WINDOWS["macd_slow"],
    signal: int = ROLLING_WINDOWS["macd_signal"],
) -> pd.DataFrame:
    """
    Add MACD line, signal line, and histogram.
    """
    out = df.copy()

    ema_fast = out[column].ewm(span=fast, adjust=False).mean()
    ema_slow = out[column].ewm(span=slow, adjust=False).mean()

    out["MACD_line"] = ema_fast - ema_slow
    out["MACD_signal"] = out["MACD_line"].ewm(span=signal, adjust=False).mean()
    out["MACD_hist"] = out["MACD_line"] - out["MACD_signal"]

    return out


def add_momentum_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple bullish/bearish momentum flags for v1 interpretation.
    """
    out = df.copy()

    if "RSI_14" in out.columns:
        out["RSI_bullish_regime"] = out["RSI_14"] >= 50
        out["RSI_overbought"] = out["RSI_14"] >= 70
        out["RSI_oversold"] = out["RSI_14"] <= 30

    required = {"MACD_line", "MACD_signal", "MACD_hist"}
    if required.issubset(out.columns):
        out["MACD_bullish_cross_state"] = out["MACD_line"] > out["MACD_signal"]
        out["MACD_hist_rising"] = out["MACD_hist"].diff() > 0

    return out


def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for main v1 momentum features.
    """
    out = df.copy()
    out = add_rsi(out)
    out = add_macd(out)
    out = add_momentum_flags(out)
    return out
