"""
Advanced volatility features for v1.5 intelligence.

Primary responsibility:
- squeeze / compression detection
- ATR percentile approximation
- extension scoring inputs
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_squeeze_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple squeeze/compression logic based on Bollinger width and ATR compression.

    This is intentionally lightweight and rule-based.
    """
    out = df.copy()

    if "BB_width_pct" in out.columns:
        bb_width_rolling_120_min = out["BB_width_pct"].rolling(window=120, min_periods=60).min()
        bb_width_rolling_120_max = out["BB_width_pct"].rolling(window=120, min_periods=60).max()

        out["BB_width_percentile_approx"] = np.where(
            (bb_width_rolling_120_max - bb_width_rolling_120_min).notna()
            & ((bb_width_rolling_120_max - bb_width_rolling_120_min) != 0),
            (
                (out["BB_width_pct"] - bb_width_rolling_120_min)
                / (bb_width_rolling_120_max - bb_width_rolling_120_min)
            )
            * 100.0,
            np.nan,
        )

    if "ATR_pct_of_close" in out.columns:
        atr_rolling_120_min = out["ATR_pct_of_close"].rolling(window=120, min_periods=60).min()
        atr_rolling_120_max = out["ATR_pct_of_close"].rolling(window=120, min_periods=60).max()

        out["ATR_percentile_approx"] = np.where(
            (atr_rolling_120_max - atr_rolling_120_min).notna()
            & ((atr_rolling_120_max - atr_rolling_120_min) != 0),
            (
                (out["ATR_pct_of_close"] - atr_rolling_120_min)
                / (atr_rolling_120_max - atr_rolling_120_min)
            )
            * 100.0,
            np.nan,
        )

    if {"BB_width_percentile_approx", "ATR_percentile_approx"}.issubset(out.columns):
        out["Squeeze_On"] = (
            (out["BB_width_percentile_approx"] <= 20)
            & (out["ATR_percentile_approx"] <= 25)
        )
        out["Volatility_Compression"] = (
            (out["BB_width_percentile_approx"] <= 35)
            & (out["ATR_percentile_approx"] <= 40)
        )
    else:
        out["Squeeze_On"] = False
        out["Volatility_Compression"] = False

    return out


def add_extension_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add price extension metrics relative to moving averages and Bollinger location.
    """
    out = df.copy()

    if {"Close", "SMA_20"}.issubset(out.columns):
        out["Extension_vs_SMA20_pct"] = np.where(
            out["SMA_20"].notna() & (out["SMA_20"] != 0),
            ((out["Close"] - out["SMA_20"]) / out["SMA_20"]) * 100.0,
            np.nan,
        )

    if {"Close", "SMA_50"}.issubset(out.columns):
        out["Extension_vs_SMA50_pct"] = np.where(
            out["SMA_50"].notna() & (out["SMA_50"] != 0),
            ((out["Close"] - out["SMA_50"]) / out["SMA_50"]) * 100.0,
            np.nan,
        )

    if {"Close", "BB_upper", "BB_lower"}.issubset(out.columns):
        band_range = out["BB_upper"] - out["BB_lower"]
        out["BB_Position_pct"] = np.where(
            band_range.notna() & (band_range != 0),
            ((out["Close"] - out["BB_lower"]) / band_range) * 100.0,
            np.nan,
        )

    return out


def add_advanced_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for advanced volatility-related features.
    """
    out = df.copy()
    out = add_squeeze_features(out)
    out = add_extension_features(out)
    return out
