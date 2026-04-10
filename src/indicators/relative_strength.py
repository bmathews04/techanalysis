"""
Relative strength calculations.

Primary responsibility:
- compare the analyzed ticker against a benchmark
- compute ratio-based relative strength and recent performance spreads
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_relative_strength_features(
    df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    close_col: str = "Close",
    benchmark_close_col: str = "Close",
) -> pd.DataFrame:
    """
    Add relative strength features versus a benchmark dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Primary ticker dataframe.
    benchmark_df : pd.DataFrame
        Benchmark dataframe, typically SPY.
    close_col : str
        Close column in primary dataframe.
    benchmark_close_col : str
        Close column in benchmark dataframe.
    """
    out = df.copy()
    bench = benchmark_df.copy()

    joined = out[[close_col]].join(
        bench[[benchmark_close_col]].rename(columns={benchmark_close_col: "Benchmark_Close"}),
        how="left",
    )

    joined["Benchmark_Close"] = joined["Benchmark_Close"].ffill()

    out["Benchmark_Close"] = joined["Benchmark_Close"]

    out["RS_Ratio"] = np.where(
        out["Benchmark_Close"].notna() & (out["Benchmark_Close"] != 0),
        out[close_col] / out["Benchmark_Close"],
        np.nan,
    )

    out["RS_Ratio_SMA_20"] = out["RS_Ratio"].rolling(window=20, min_periods=20).mean()
    out["RS_Ratio_SMA_50"] = out["RS_Ratio"].rolling(window=50, min_periods=50).mean()

    out["RS_Above_20"] = out["RS_Ratio"] > out["RS_Ratio_SMA_20"]
    out["RS_Above_50"] = out["RS_Ratio"] > out["RS_Ratio_SMA_50"]

    out["Ticker_Return_20d_pct"] = out[close_col].pct_change(periods=20) * 100.0
    out["Benchmark_Return_20d_pct"] = out["Benchmark_Close"].pct_change(periods=20) * 100.0
    out["Relative_Performance_20d_pct"] = (
        out["Ticker_Return_20d_pct"] - out["Benchmark_Return_20d_pct"]
    )

    out["Ticker_Return_60d_pct"] = out[close_col].pct_change(periods=60) * 100.0
    out["Benchmark_Return_60d_pct"] = out["Benchmark_Close"].pct_change(periods=60) * 100.0
    out["Relative_Performance_60d_pct"] = (
        out["Ticker_Return_60d_pct"] - out["Benchmark_Return_60d_pct"]
    )

    return out
