"""
Market structure calculations.

Primary responsibility:
- swing highs and lows
- rolling support and resistance
- breakout / breakdown helpers
- simple trend-structure flags
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_swing_points(
    df: pd.DataFrame,
    left_bars: int = 3,
    right_bars: int = 3,
) -> pd.DataFrame:
    """
    Add simple swing high / swing low detection.

    A swing high is a bar whose High is the maximum over a centered window.
    A swing low is a bar whose Low is the minimum over a centered window.

    Notes
    -----
    This is intentionally simple and readable for v1.
    The last few rows will naturally be NaN/False due to centered windows.
    """
    out = df.copy()

    window = left_bars + right_bars + 1

    rolling_high = out["High"].rolling(window=window, center=True, min_periods=window).max()
    rolling_low = out["Low"].rolling(window=window, center=True, min_periods=window).min()

    out["Swing_High"] = out["High"].eq(rolling_high)
    out["Swing_Low"] = out["Low"].eq(rolling_low)

    out["Swing_High_Price"] = np.where(out["Swing_High"], out["High"], np.nan)
    out["Swing_Low_Price"] = np.where(out["Swing_Low"], out["Low"], np.nan)

    return out


def add_recent_structure_levels(
    df: pd.DataFrame,
    lookback: int = 20,
) -> pd.DataFrame:
    """
    Add rolling support/resistance style levels using prior data only.

    Resistance = prior rolling highest high
    Support    = prior rolling lowest low
    """
    out = df.copy()

    out["Rolling_Resistance_20"] = out["High"].rolling(window=lookback, min_periods=lookback).max().shift(1)
    out["Rolling_Support_20"] = out["Low"].rolling(window=lookback, min_periods=lookback).min().shift(1)

    out["Close_above_resistance"] = (
        out["Rolling_Resistance_20"].notna() & (out["Close"] > out["Rolling_Resistance_20"])
    )
    out["Close_below_support"] = (
        out["Rolling_Support_20"].notna() & (out["Close"] < out["Rolling_Support_20"])
    )

    return out


def add_structure_distances(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add percent distance from close to rolling support / resistance.
    """
    out = df.copy()

    if "Rolling_Resistance_20" in out.columns:
        out["Pct_to_Resistance"] = np.where(
            out["Rolling_Resistance_20"].notna() & (out["Rolling_Resistance_20"] != 0),
            ((out["Rolling_Resistance_20"] - out["Close"]) / out["Rolling_Resistance_20"]) * 100.0,
            np.nan,
        )

    if "Rolling_Support_20" in out.columns:
        out["Pct_above_Support"] = np.where(
            out["Rolling_Support_20"].notna() & (out["Rolling_Support_20"] != 0),
            ((out["Close"] - out["Rolling_Support_20"]) / out["Rolling_Support_20"]) * 100.0,
            np.nan,
        )

    return out


def add_breakout_breakdown_flags(
    df: pd.DataFrame,
    confirm_with_close: bool = True,
) -> pd.DataFrame:
    """
    Add simple breakout / breakdown state helpers.
    """
    out = df.copy()

    if {"Rolling_Resistance_20", "Rolling_Support_20"}.issubset(out.columns):
        if confirm_with_close:
            out["Breakout_Confirmed"] = out["Close_above_resistance"]
            out["Breakdown_Confirmed"] = out["Close_below_support"]
        else:
            out["Breakout_Confirmed"] = out["High"] > out["Rolling_Resistance_20"]
            out["Breakdown_Confirmed"] = out["Low"] < out["Rolling_Support_20"]

    return out


def add_higher_high_lower_low_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple bar-to-bar structure flags.

    This is not a full market structure model, but it helps narrative generation.
    """
    out = df.copy()

    out["Higher_High"] = out["High"] > out["High"].shift(1)
    out["Higher_Low"] = out["Low"] > out["Low"].shift(1)
    out["Lower_High"] = out["High"] < out["High"].shift(1)
    out["Lower_Low"] = out["Low"] < out["Low"].shift(1)

    out["Bullish_Bar_Structure"] = out["Higher_High"] & out["Higher_Low"]
    out["Bearish_Bar_Structure"] = out["Lower_High"] & out["Lower_Low"]

    return out


def add_range_features(
    df: pd.DataFrame,
    window: int = 20,
) -> pd.DataFrame:
    """
    Add simple rolling range metrics.
    """
    out = df.copy()

    out["Range_High_20"] = out["High"].rolling(window=window, min_periods=window).max()
    out["Range_Low_20"] = out["Low"].rolling(window=window, min_periods=window).min()

    out["Range_Width_20"] = out["Range_High_20"] - out["Range_Low_20"]
    out["Range_Width_Pct_20"] = np.where(
        out["Close"].notna() & (out["Close"] != 0),
        (out["Range_Width_20"] / out["Close"]) * 100.0,
        np.nan,
    )

    return out


def add_structure_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for main v1 market-structure features.
    """
    out = df.copy()
    out = add_swing_points(out)
    out = add_recent_structure_levels(out)
    out = add_structure_distances(out)
    out = add_breakout_breakdown_flags(out)
    out = add_higher_high_lower_low_flags(out)
    out = add_range_features(out)
    return out
