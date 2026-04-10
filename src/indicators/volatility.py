"""
Volatility indicator calculations.

Primary responsibility:
- ATR
- Bollinger Bands
- Bollinger width
- simple volatility regime helpers
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.settings import ROLLING_WINDOWS


def add_true_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add True Range (TR).
    """
    out = df.copy()

    prev_close = out["Close"].shift(1)

    tr_components = pd.concat(
        [
            (out["High"] - out["Low"]).abs(),
            (out["High"] - prev_close).abs(),
            (out["Low"] - prev_close).abs(),
        ],
        axis=1,
    )

    out["TR"] = tr_components.max(axis=1)
    return out


def add_atr(
    df: pd.DataFrame,
    window: int = ROLLING_WINDOWS["atr"],
) -> pd.DataFrame:
    """
    Add Average True Range (ATR) using Wilder-style smoothing.
    """
    out = df.copy()

    if "TR" not in out.columns:
        out = add_true_range(out)

    out["ATR_14"] = out["TR"].ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    out["ATR_pct_of_close"] = np.where(
        out["Close"].notna() & (out["Close"] != 0),
        (out["ATR_14"] / out["Close"]) * 100.0,
        np.nan,
    )

    return out


def add_bollinger_bands(
    df: pd.DataFrame,
    column: str = "Close",
    window: int = ROLLING_WINDOWS["bbands"],
    num_std: float = 2.0,
) -> pd.DataFrame:
    """
    Add Bollinger Bands and width metrics.
    """
    out = df.copy()

    rolling_mean = out[column].rolling(window=window, min_periods=window).mean()
    rolling_std = out[column].rolling(window=window, min_periods=window).std(ddof=0)

    out["BB_mid"] = rolling_mean
    out["BB_upper"] = rolling_mean + (num_std * rolling_std)
    out["BB_lower"] = rolling_mean - (num_std * rolling_std)

    out["BB_width_pct"] = np.where(
        rolling_mean.notna() & (rolling_mean != 0),
        ((out["BB_upper"] - out["BB_lower"]) / rolling_mean) * 100.0,
        np.nan,
    )

    out["Close_vs_BB_mid_pct"] = np.where(
        out["BB_mid"].notna() & (out["BB_mid"] != 0),
        ((out[column] - out["BB_mid"]) / out["BB_mid"]) * 100.0,
        np.nan,
    )

    out["Close_above_BB_upper"] = out[column] > out["BB_upper"]
    out["Close_below_BB_lower"] = out[column] < out["BB_lower"]

    return out


def add_volatility_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple v1 volatility state helpers.
    """
    out = df.copy()

    if "BB_width_pct" in out.columns:
        bb_width_ma = out["BB_width_pct"].rolling(window=20, min_periods=10).mean()
        out["BB_width_expanding"] = out["BB_width_pct"] > bb_width_ma
        out["BB_width_contracting"] = out["BB_width_pct"] < bb_width_ma

    if "ATR_pct_of_close" in out.columns:
        atr_ma = out["ATR_pct_of_close"].rolling(window=20, min_periods=10).mean()
        out["ATR_expanding"] = out["ATR_pct_of_close"] > atr_ma
        out["ATR_contracting"] = out["ATR_pct_of_close"] < atr_ma

    return out


def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper for main v1 volatility features.
    """
    out = df.copy()
    out = add_true_range(out)
    out = add_atr(out)
    out = add_bollinger_bands(out)
    out = add_volatility_flags(out)
    return out
