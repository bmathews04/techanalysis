"""
Evidence builder.

Primary responsibility:
- convert technical state into grouped evidence lists
- keep the UI display clean and readable
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analysis.signal_scores import SignalScores
from src.analysis.trend_classifier import TrendClassification


@dataclass(frozen=True)
class EvidenceBundle:
    trend: list[str]
    momentum: list[str]
    volatility: list[str]
    volume: list[str]
    structure: list[str]
    risk_flags: list[str]


def _safe_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def build_evidence(
    df: pd.DataFrame,
    trend: TrendClassification,
    scores: SignalScores,
) -> EvidenceBundle:
    """
    Build grouped evidence statements from the latest technical state.
    """
    latest = df.iloc[-1]

    trend_items: list[str] = []
    momentum_items: list[str] = []
    volatility_items: list[str] = []
    volume_items: list[str] = []
    structure_items: list[str] = []
    risk_flags: list[str] = []

    close = _safe_float(latest.get("Close"))
    sma20 = _safe_float(latest.get("SMA_20"))
    sma50 = _safe_float(latest.get("SMA_50"))
    sma200 = _safe_float(latest.get("SMA_200"))
    rsi = _safe_float(latest.get("RSI_14"), 50.0)
    atr_pct = _safe_float(latest.get("ATR_pct_of_close"), 0.0)
    rel_vol = _safe_float(latest.get("Relative_Volume_20"), 1.0)
    pct_to_resistance = _safe_float(latest.get("Pct_to_Resistance"), 999.0)
    pct_above_support = _safe_float(latest.get("Pct_above_Support"), 0.0)

    # Trend evidence
    if sma20 and close > sma20:
        trend_items.append("Price is trading above the 20-day moving average.")
    else:
        trend_items.append("Price is trading below the 20-day moving average.")

    if sma50 and close > sma50:
        trend_items.append("Price is holding above the 50-day moving average.")
    else:
        trend_items.append("Price is below the 50-day moving average.")

    if sma200 and close > sma200:
        trend_items.append("Price remains above the 200-day moving average.")
    else:
        trend_items.append("Price is below the 200-day moving average.")

    if _safe_bool(latest.get("EMA_stack_bullish")):
        trend_items.append("The EMA stack is bullish, with shorter averages above longer ones.")
    elif _safe_bool(latest.get("EMA_stack_bearish")):
        trend_items.append("The EMA stack is bearish, with shorter averages below longer ones.")

    if _safe_float(latest.get("SMA_20_slope_pct_5")) > 0:
        trend_items.append("The short-term trend slope is positive.")
    if _safe_float(latest.get("SMA_50_slope_pct_5")) > 0:
        trend_items.append("The intermediate trend slope is positive.")
    if _safe_float(latest.get("SMA_200_slope_pct_5")) < 0:
        risk_flags.append("The long-term trend slope remains weak.")

    trend_items.append(f"Trend score: {scores.trend}/100.")
    trend_items.append(f"Regime classification: {trend.label}.")

    # Momentum evidence
    if rsi >= 60:
        momentum_items.append(f"RSI is {rsi:.1f}, which reflects strong momentum.")
    elif rsi >= 50:
        momentum_items.append(f"RSI is {rsi:.1f}, which reflects constructive momentum.")
    elif rsi <= 40:
        momentum_items.append(f"RSI is {rsi:.1f}, which reflects weak momentum.")
    else:
        momentum_items.append(f"RSI is {rsi:.1f}, which reflects a more neutral momentum profile.")

    if _safe_bool(latest.get("MACD_bullish_cross_state")):
        momentum_items.append("MACD is above its signal line.")
    else:
        momentum_items.append("MACD is below its signal line.")

    if _safe_bool(latest.get("MACD_hist_rising")):
        momentum_items.append("MACD histogram is improving.")
    else:
        momentum_items.append("MACD histogram is softening or not improving.")

    if _safe_bool(latest.get("RSI_overbought")):
        risk_flags.append("Momentum is elevated enough to suggest near-term extension risk.")
    if _safe_bool(latest.get("RSI_oversold")):
        risk_flags.append("Momentum is oversold, which can create instability even if a bounce occurs.")

    momentum_items.append(f"Momentum score: {scores.momentum}/100.")

    # Volatility evidence
    volatility_items.append(f"ATR is {atr_pct:.2f}% of price.")

    if _safe_bool(latest.get("ATR_expanding")):
        volatility_items.append("ATR is expanding, which suggests rising movement intensity.")
    elif _safe_bool(latest.get("ATR_contracting")):
        volatility_items.append("ATR is contracting, which suggests calmer price behavior.")

    bb_width = _safe_float(latest.get("BB_width_pct"), 0.0)
    volatility_items.append(f"Bollinger Band width is {bb_width:.2f}%.")

    if _safe_bool(latest.get("BB_width_contracting")):
        volatility_items.append("Bollinger Band width is contracting, which may indicate compression.")
    elif _safe_bool(latest.get("BB_width_expanding")):
        volatility_items.append("Bollinger Band width is expanding, which may indicate a more active phase.")

    if _safe_bool(latest.get("Close_above_BB_upper")):
        risk_flags.append("Price is pressing above the upper Bollinger Band, which can reflect extension.")
    if _safe_bool(latest.get("Close_below_BB_lower")):
        risk_flags.append("Price is pressing below the lower Bollinger Band, which reflects technical weakness.")

    volatility_items.append(f"Volatility score: {scores.volatility}/100.")

    # Volume evidence
    volume_items.append(f"Relative volume is {rel_vol:.2f}x its 20-period average.")

    if rel_vol >= 1.5:
        volume_items.append("Recent trading activity is meaningfully above normal.")
    elif rel_vol < 0.8:
        volume_items.append("Recent trading activity is lighter than normal.")

    if _safe_bool(latest.get("OBV_above_MA")):
        volume_items.append("On-balance volume is above its recent average.")
    else:
        volume_items.append("On-balance volume is not showing strong confirmation.")

    if _safe_bool(latest.get("Bullish_volume_confirmation")):
        volume_items.append("Recent upside action has volume confirmation.")
    if _safe_bool(latest.get("Bearish_volume_confirmation")):
        risk_flags.append("Recent downside action has meaningful volume confirmation.")

    volume_items.append(f"Volume score: {scores.volume}/100.")

    # Structure evidence
    if _safe_bool(latest.get("Breakout_Confirmed")):
        structure_items.append("Price has closed above recent resistance.")
    if _safe_bool(latest.get("Breakdown_Confirmed")):
        structure_items.append("Price has closed below recent support.")

    if _safe_bool(latest.get("Bullish_Bar_Structure")):
        structure_items.append("Recent bar structure is bullish.")
    elif _safe_bool(latest.get("Bearish_Bar_Structure")):
        structure_items.append("Recent bar structure is bearish.")

    resistance = latest.get("Rolling_Resistance_20")
    support = latest.get("Rolling_Support_20")

    if pd.notna(resistance):
        structure_items.append(f"Recent resistance reference: {float(resistance):.2f}.")
    if pd.notna(support):
        structure_items.append(f"Recent support reference: {float(support):.2f}.")

    if pct_to_resistance != 999.0 and pct_to_resistance <= 2.0:
        risk_flags.append("Price is close to resistance, which can reduce immediate upside room.")
    if pct_above_support >= 0:
        structure_items.append(f"Price is {pct_above_support:.2f}% above recent support.")

    structure_items.append(f"Structure score: {scores.structure}/100.")

    return EvidenceBundle(
        trend=trend_items,
        momentum=momentum_items,
        volatility=volatility_items,
        volume=volume_items,
        structure=structure_items,
        risk_flags=risk_flags,
    )
