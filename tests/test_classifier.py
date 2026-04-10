from __future__ import annotations

import pandas as pd

from src.analysis.signal_agreement import build_signal_agreement
from src.analysis.signal_scores import SignalScores, build_signal_scores
from src.analysis.trend_classifier import classify_trend_regime


def make_bullish_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Close": 120.0,
                "SMA_20": 115.0,
                "SMA_50": 110.0,
                "SMA_200": 100.0,
                "EMA_stack_bullish": True,
                "EMA_stack_bearish": False,
                "RSI_14": 62.0,
                "MACD_bullish_cross_state": True,
                "MACD_hist_rising": True,
                "SMA_20_slope_pct_5": 1.2,
                "SMA_50_slope_pct_5": 1.0,
                "SMA_200_slope_pct_5": 0.4,
                "Breakout_Confirmed": False,
                "Breakdown_Confirmed": False,
                "ATR_pct_of_close": 2.5,
                "BB_width_pct": 9.0,
                "ATR_expanding": False,
                "BB_width_expanding": False,
                "ATR_contracting": True,
                "Relative_Volume_20": 1.2,
                "OBV_above_MA": True,
                "Bullish_volume_confirmation": True,
                "Bearish_volume_confirmation": False,
                "Bullish_Bar_Structure": True,
                "Bearish_Bar_Structure": False,
                "Pct_to_Resistance": 3.0,
                "Pct_above_Support": 4.0,
            }
        ]
    )


def make_bearish_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Close": 80.0,
                "SMA_20": 85.0,
                "SMA_50": 90.0,
                "SMA_200": 100.0,
                "EMA_stack_bullish": False,
                "EMA_stack_bearish": True,
                "RSI_14": 38.0,
                "MACD_bullish_cross_state": False,
                "MACD_hist_rising": False,
                "SMA_20_slope_pct_5": -1.0,
                "SMA_50_slope_pct_5": -0.8,
                "SMA_200_slope_pct_5": -0.3,
                "Breakout_Confirmed": False,
                "Breakdown_Confirmed": True,
                "ATR_pct_of_close": 7.0,
                "BB_width_pct": 28.0,
                "ATR_expanding": True,
                "BB_width_expanding": True,
                "ATR_contracting": False,
                "Relative_Volume_20": 1.4,
                "OBV_above_MA": False,
                "Bullish_volume_confirmation": False,
                "Bearish_volume_confirmation": True,
                "Bullish_Bar_Structure": False,
                "Bearish_Bar_Structure": True,
                "Pct_to_Resistance": 12.0,
                "Pct_above_Support": -1.0,
            }
        ]
    )


def test_classify_trend_regime_strong_uptrend() -> None:
    df = make_bullish_frame()
    result = classify_trend_regime(df)

    assert result.label == "Strong uptrend"
    assert result.confidence >= 8.0


def test_classify_trend_regime_breakdown_or_downtrend() -> None:
    df = make_bearish_frame()
    result = classify_trend_regime(df)

    assert result.label in {
        "Healthy downtrend",
        "Breakdown / continuation attempt",
    }


def test_build_signal_scores_returns_valid_ranges() -> None:
    df = make_bullish_frame()
    scores = build_signal_scores(df)

    assert 0 <= scores.trend <= 100
    assert 0 <= scores.momentum <= 100
    assert 0 <= scores.volatility <= 100
    assert 0 <= scores.volume <= 100
    assert 0 <= scores.structure <= 100


def test_build_signal_agreement_strong_bullish() -> None:
    scores = SignalScores(
        trend=85,
        momentum=78,
        volatility=70,
        volume=80,
        structure=76,
    )
    agreement = build_signal_agreement(scores)

    assert agreement.label == "Strong bullish agreement"


def test_build_signal_agreement_mixed() -> None:
    scores = SignalScores(
        trend=80,
        momentum=72,
        volatility=45,
        volume=30,
        structure=55,
    )
    agreement = build_signal_agreement(scores)

    assert agreement.label == "Mixed / conflicting signals"
