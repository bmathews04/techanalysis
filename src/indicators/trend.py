"""
Trend indicator calculations.

Primary responsibility:
- moving averages
- slope calculations
- trend distance metrics
- MA alignment helpers
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.settings import ROLLING_WINDOWS


def add_sma(
    df: pd.DataFrame,
    column: str = "Close",
    windows: tuple[int, ...] = (
        ROLLING_WINDOWS["short_ma"],
        ROLLING_WINDOWS["medium_ma"],
        ROLLING_WINDOWS["long_ma"],
    ),
) -> pd.DataFrame:
    """
    Add simple moving averages for the given column.
    """
    out = df.copy()

    for window in windows:
        out[f"SMA_{window}"] = out[column].rolling(window=window, min_periods=window).mean()

    return out


def add_ema(
    df: pd.DataFrame,
    column: str = "Close",
    windows: tuple[int, ...] = (
        ROLLING_WINDOWS["short_ma"],
        ROLLING_WINDOWS["medium_ma"],
        ROLLING_WINDOWS["long_ma"],
    ),
) -> pd.DataFrame:
    """
    Add exponential moving averages for the given column.
    """
    out = df.copy()

    for window in windows:
        out[f"EMA_{window}"] = out[column].ewm(span=window, adjust=False).mean()

    return out


def add_ma_slope(
    df: pd.DataFrame,
    ma_columns: tuple[str, ...] = ("SMA_20", "SMA_50", "SMA_200"),
    periods: int = 5,
) -> pd.DataFrame:
    """
    Add simple slope proxies for moving averages using percentage change over N periods.
    """
    out = df.copy()

    for col in ma_columns:
        if col in out.columns:
            out[f"{col}_slope_pct_{periods}"] = out[col].pct_change(periods=periods) * 100.0

    return out


def add_price_vs_ma_distance(
    df: pd.DataFrame,
    price_col: str = "Close",
    ma_columns: tuple[str, ...] = ("SMA_20", "SMA_50", "SMA_200"),
) -> pd.DataFrame:
    """
    Add percent distance from price to selected moving averages.
    """
    out = df.copy()

    for col in ma_columns:
        if col in out.columns:
            out[f"{price_col}_vs_{col}_pct"] = np.where(
                out[col].notna() & (out[col] != 0),
                ((out[price_col] - out[col]) / out[col]) * 100.0,
                np.nan,
            )

    return out


def add_ema_stack_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add boolean flags for EMA alignment.

    Bullish stack:
        EMA_20 > EMA_50 > EMA_200

    Bearish stack:
        EMA_20 < EMA_50 < EMA_200
    """
    out = df.copy()

    required = {"EMA_20", "EMA_50", "EMA_200"}
    if not required.issubset(out.columns):
        return out

    out["EMA_stack_bullish"] = (
        (out["EMA_20"] > out["EMA_50"]) & (out["EMA_50"] > out["EMA_200"])
    )
    out["EMA_stack_bearish"] = (
        (out["EMA_20"] < out["EMA_50"]) & (out["EMA_50"] < out["EMA_200"])
    )

    return out


def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for the main v1 trend features.
    """
    out = df.copy()
    out = add_sma(out)
    out = add_ema(out)
    out = add_ma_slope(out)
    out = add_price_vs_ma_distance(out)
    out = add_ema_stack_flags(out)
    return out
