"""
Volume indicator calculations.

Primary responsibility:
- rolling volume average
- relative volume
- On-Balance Volume (OBV)
- simple volume confirmation flags
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.settings import ROLLING_WINDOWS


def add_volume_ma(
    df: pd.DataFrame,
    window: int = ROLLING_WINDOWS["volume_ma"],
) -> pd.DataFrame:
    """
    Add rolling average volume and relative volume.
    """
    out = df.copy()

    out["Volume_MA_20"] = out["Volume"].rolling(window=window, min_periods=window).mean()

    out["Relative_Volume_20"] = np.where(
        out["Volume_MA_20"].notna() & (out["Volume_MA_20"] != 0),
        out["Volume"] / out["Volume_MA_20"],
        np.nan,
    )

    return out


def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add On-Balance Volume (OBV).
    """
    out = df.copy()

    price_diff = out["Close"].diff()

    direction = np.select(
        [
            price_diff > 0,
            price_diff < 0,
        ],
        [
            1,
            -1,
        ],
        default=0,
    )

    out["OBV"] = (direction * out["Volume"].fillna(0)).cumsum()
    out["OBV_MA_20"] = out["OBV"].rolling(window=20, min_periods=20).mean()
    out["OBV_above_MA"] = out["OBV"] > out["OBV_MA_20"]

    return out


def add_volume_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple v1 volume-state helpers.
    """
    out = df.copy()

    if "Relative_Volume_20" in out.columns:
        out["High_relative_volume"] = out["Relative_Volume_20"] >= 1.5
        out["Low_relative_volume"] = out["Relative_Volume_20"] <= 0.8

    # Helpful for later narrative generation
    out["Up_day"] = out["Close"] > out["Close"].shift(1)
    out["Down_day"] = out["Close"] < out["Close"].shift(1)

    if "Relative_Volume_20" in out.columns:
        out["Bullish_volume_confirmation"] = out["Up_day"] & (out["Relative_Volume_20"] > 1.0)
        out["Bearish_volume_confirmation"] = out["Down_day"] & (out["Relative_Volume_20"] > 1.0)

    return out


def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for main v1 volume features.
    """
    out = df.copy()
    out = add_volume_ma(out)
    out = add_obv(out)
    out = add_volume_flags(out)
    return out
