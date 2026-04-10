from __future__ import annotations

import numpy as np
import pandas as pd

from src.indicators.momentum import add_momentum_features
from src.indicators.structure import add_structure_features
from src.indicators.trend import add_trend_features
from src.indicators.volatility import add_volatility_features
from src.indicators.volume import add_volume_features


def make_sample_ohlcv(rows: int = 260) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=rows, freq="D")

    close = np.linspace(100, 150, rows)
    open_ = close - 0.5
    high = close + 1.0
    low = close - 1.0
    volume = np.linspace(1_000_000, 2_000_000, rows)

    df = pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


def test_trend_features_add_expected_columns() -> None:
    df = make_sample_ohlcv()
    out = add_trend_features(df)

    expected = {
        "SMA_20",
        "SMA_50",
        "SMA_200",
        "EMA_20",
        "EMA_50",
        "EMA_200",
        "EMA_stack_bullish",
        "EMA_stack_bearish",
        "Close_vs_SMA_20_pct",
        "Close_vs_SMA_50_pct",
        "Close_vs_SMA_200_pct",
    }

    assert expected.issubset(set(out.columns))


def test_momentum_features_add_expected_columns() -> None:
    df = make_sample_ohlcv()
    out = add_momentum_features(df)

    expected = {
        "RSI_14",
        "MACD_line",
        "MACD_signal",
        "MACD_hist",
        "RSI_bullish_regime",
        "MACD_bullish_cross_state",
    }

    assert expected.issubset(set(out.columns))


def test_volatility_features_add_expected_columns() -> None:
    df = make_sample_ohlcv()
    out = add_volatility_features(df)

    expected = {
        "TR",
        "ATR_14",
        "ATR_pct_of_close",
        "BB_mid",
        "BB_upper",
        "BB_lower",
        "BB_width_pct",
    }

    assert expected.issubset(set(out.columns))


def test_volume_features_add_expected_columns() -> None:
    df = make_sample_ohlcv()
    out = add_volume_features(df)

    expected = {
        "Volume_MA_20",
        "Relative_Volume_20",
        "OBV",
        "OBV_MA_20",
        "OBV_above_MA",
    }

    assert expected.issubset(set(out.columns))


def test_structure_features_add_expected_columns() -> None:
    df = make_sample_ohlcv()
    out = add_structure_features(df)

    expected = {
        "Swing_High",
        "Swing_Low",
        "Rolling_Resistance_20",
        "Rolling_Support_20",
        "Breakout_Confirmed",
        "Breakdown_Confirmed",
        "Bullish_Bar_Structure",
        "Bearish_Bar_Structure",
    }

    assert expected.issubset(set(out.columns))


def test_indicator_pipeline_preserves_row_count() -> None:
    df = make_sample_ohlcv()
    original_len = len(df)

    out = add_trend_features(df)
    out = add_momentum_features(out)
    out = add_volatility_features(out)
    out = add_volume_features(out)
    out = add_structure_features(out)

    assert len(out) == original_len
