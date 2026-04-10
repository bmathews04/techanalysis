"""
Trend regime classification.

Primary responsibility:
- classify the ticker into a readable market state
- return both label and supporting metadata
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TrendClassification:
    label: str
    confidence: float
    reason: str


def _safe_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def classify_trend_regime(df: pd.DataFrame) -> TrendClassification:
    """
    Classify the most recent bar into a broad trend regime.

    Expected inputs are the indicator columns created earlier.
    """
    latest = df.iloc[-1]

    close = _safe_float(latest.get("Close"))
    sma20 = _safe_float(latest.get("SMA_20"))
    sma50 = _safe_float(latest.get("SMA_50"))
    sma200 = _safe_float(latest.get("SMA_200"))

    ema_stack_bullish = _safe_bool(latest.get("EMA_stack_bullish"))
    ema_stack_bearish = _safe_bool(latest.get("EMA_stack_bearish"))

    rsi = _safe_float(latest.get("RSI_14"), default=50.0)
    macd_bullish = _safe_bool(latest.get("MACD_bullish_cross_state"))
    macd_hist_rising = _safe_bool(latest.get("MACD_hist_rising"))

    sma20_slope = _safe_float(latest.get("SMA_20_slope_pct_5"))
    sma50_slope = _safe_float(latest.get("SMA_50_slope_pct_5"))
    sma200_slope = _safe_float(latest.get("SMA_200_slope_pct_5"))

    breakout = _safe_bool(latest.get("Breakout_Confirmed"))
    breakdown = _safe_bool(latest.get("Breakdown_Confirmed"))

    above_20 = close > sma20 if sma20 else False
    above_50 = close > sma50 if sma50 else False
    above_200 = close > sma200 if sma200 else False

    slopes_positive = sma20_slope > 0 and sma50_slope > 0
    slopes_negative = sma20_slope < 0 and sma50_slope < 0

    long_term_positive = sma200_slope >= 0
    long_term_negative = sma200_slope < 0

    # Strong uptrend
    if (
        above_20
        and above_50
        and above_200
        and ema_stack_bullish
        and slopes_positive
        and long_term_positive
        and rsi >= 55
        and macd_bullish
    ):
        confidence = 9.0 if macd_hist_rising else 8.4
        reason = (
            "Price is above the 20/50/200-day moving averages, the EMA stack is bullish, "
            "and momentum remains supportive."
        )
        return TrendClassification("Strong uptrend", confidence, reason)

    # Healthy uptrend
    if (
        above_50
        and above_200
        and long_term_positive
        and rsi >= 50
    ):
        confidence = 7.8 if above_20 else 7.1
        reason = (
            "The broader trend remains constructive with price above key medium- and long-term "
            "trend levels, though momentum is less forceful than a strong uptrend."
        )
        return TrendClassification("Healthy uptrend", confidence, reason)

    # Breakout / continuation attempt
    if breakout and above_50 and rsi >= 50:
        confidence = 7.2
        reason = (
            "Price has pushed above recent resistance while the intermediate trend remains constructive."
        )
        return TrendClassification("Breakout / continuation attempt", confidence, reason)

    # Range-bound / consolidation
    if (
        (above_200 and not above_20 and not below(close, sma50))
        or (abs(rsi - 50) <= 7 and not breakout and not breakdown)
    ):
        confidence = 5.8
        reason = (
            "Signals are mixed and the chart appears to be consolidating rather than trending cleanly."
        )
        return TrendClassification("Range-bound / consolidation", confidence, reason)

    # Reversal attempt
    if above_20 and not above_50 and rsi > 50 and macd_bullish:
        confidence = 5.9
        reason = (
            "Short-term conditions are improving, but the chart has not yet fully repaired its "
            "intermediate trend structure."
        )
        return TrendClassification("Bullish reversal attempt", confidence, reason)

    # Healthy downtrend
    if (
        not above_50
        and not above_200
        and ema_stack_bearish
        and slopes_negative
        and long_term_negative
        and rsi <= 45
    ):
        confidence = 8.1
        reason = (
            "Price is below key trend levels, the EMA stack is bearish, and momentum remains weak."
        )
        return TrendClassification("Healthy downtrend", confidence, reason)

    # Breakdown / continuation attempt
    if breakdown and not above_50 and rsi <= 45:
        confidence = 7.0
        reason = (
            "Price has broken below recent support while trend and momentum remain weak."
        )
        return TrendClassification("Breakdown / continuation attempt", confidence, reason)

    # Default / mixed
    return TrendClassification(
        label="Mixed / transition",
        confidence=5.0,
        reason=(
            "The chart is showing a transitional or mixed condition with no dominant technical regime."
        ),
    )


def below(value: float, threshold: float) -> bool:
    """
    Small helper to keep conditional logic readable.
    """
    return value < threshold if threshold else False
