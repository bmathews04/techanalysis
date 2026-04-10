"""
Technical category scoring.

Primary responsibility:
- assign 0-100 scores to major technical categories
- keep scoring interpretable and rule-based for v1
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SignalScores:
    trend: int
    momentum: int
    volatility: int
    volume: int
    structure: int


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _safe_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def score_trend(df: pd.DataFrame) -> int:
    latest = df.iloc[-1]

    score = 50.0

    close = _safe_float(latest.get("Close"))
    sma20 = _safe_float(latest.get("SMA_20"))
    sma50 = _safe_float(latest.get("SMA_50"))
    sma200 = _safe_float(latest.get("SMA_200"))

    if sma20 and close > sma20:
        score += 10
    if sma50 and close > sma50:
        score += 15
    if sma200 and close > sma200:
        score += 20

    if _safe_bool(latest.get("EMA_stack_bullish")):
        score += 10
    if _safe_bool(latest.get("EMA_stack_bearish")):
        score -= 20

    if _safe_float(latest.get("SMA_20_slope_pct_5")) > 0:
        score += 5
    else:
        score -= 5

    if _safe_float(latest.get("SMA_50_slope_pct_5")) > 0:
        score += 5
    else:
        score -= 5

    if _safe_float(latest.get("SMA_200_slope_pct_5")) > 0:
        score += 5
    else:
        score -= 5

    return _clamp_score(score)


def score_momentum(df: pd.DataFrame) -> int:
    latest = df.iloc[-1]
    score = 50.0

    rsi = _safe_float(latest.get("RSI_14"), 50)

    if rsi >= 60:
        score += 20
    elif rsi >= 50:
        score += 10
    elif rsi <= 40:
        score -= 15

    if _safe_bool(latest.get("MACD_bullish_cross_state")):
        score += 15
    else:
        score -= 10

    if _safe_bool(latest.get("MACD_hist_rising")):
        score += 10
    else:
        score -= 5

    if _safe_bool(latest.get("RSI_overbought")):
        score -= 5  # still bullish, but can be extended
    if _safe_bool(latest.get("RSI_oversold")):
        score -= 10

    return _clamp_score(score)


def score_volatility(df: pd.DataFrame) -> int:
    """
    Score the 'quality' of current volatility for participation.

    Higher score = volatility is relatively constructive / not excessively chaotic.
    """
    latest = df.iloc[-1]
    score = 60.0

    atr_pct = _safe_float(latest.get("ATR_pct_of_close"), 0.0)
    bb_width = _safe_float(latest.get("BB_width_pct"), 0.0)

    if atr_pct <= 2:
        score += 15
    elif atr_pct <= 4:
        score += 5
    elif atr_pct > 6:
        score -= 20

    if bb_width <= 10:
        score += 10
    elif bb_width > 25:
        score -= 15

    if _safe_bool(latest.get("ATR_expanding")):
        score -= 5
    if _safe_bool(latest.get("BB_width_expanding")):
        score -= 5

    if _safe_bool(latest.get("ATR_contracting")):
        score += 5

    return _clamp_score(score)


def score_volume(df: pd.DataFrame) -> int:
    latest = df.iloc[-1]
    score = 50.0

    rel_vol = _safe_float(latest.get("Relative_Volume_20"), 1.0)

    if rel_vol >= 1.5:
        score += 15
    elif rel_vol >= 1.0:
        score += 8
    elif rel_vol < 0.8:
        score -= 10

    if _safe_bool(latest.get("OBV_above_MA")):
        score += 15
    else:
        score -= 10

    if _safe_bool(latest.get("Bullish_volume_confirmation")):
        score += 15

    if _safe_bool(latest.get("Bearish_volume_confirmation")):
        score -= 15

    return _clamp_score(score)


def score_structure(df: pd.DataFrame) -> int:
    latest = df.iloc[-1]
    score = 50.0

    if _safe_bool(latest.get("Breakout_Confirmed")):
        score += 20
    if _safe_bool(latest.get("Breakdown_Confirmed")):
        score -= 20

    if _safe_bool(latest.get("Bullish_Bar_Structure")):
        score += 10
    if _safe_bool(latest.get("Bearish_Bar_Structure")):
        score -= 10

    pct_to_resistance = _safe_float(latest.get("Pct_to_Resistance"), 0.0)
    pct_above_support = _safe_float(latest.get("Pct_above_Support"), 0.0)

    if pct_to_resistance > 0 and pct_to_resistance <= 2:
        score -= 5  # near resistance can reduce upside room
    if pct_above_support >= 2:
        score += 5

    return _clamp_score(score)


def build_signal_scores(df: pd.DataFrame) -> SignalScores:
    """
    Build the full category scorecard.
    """
    return SignalScores(
        trend=score_trend(df),
        momentum=score_momentum(df),
        volatility=score_volatility(df),
        volume=score_volume(df),
        structure=score_structure(df),
    )
