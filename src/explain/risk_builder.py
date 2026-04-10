"""
Risk and invalidation builder.

Primary responsibility:
- identify what breaks the current thesis
- surface key technical risk areas in plain English
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analysis.trend_classifier import TrendClassification


@dataclass(frozen=True)
class RiskFramework:
    invalidation_level: str
    key_risks: list[str]
    thesis_breakers: list[str]


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def _safe_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def build_risk_framework(
    df: pd.DataFrame,
    trend: TrendClassification,
) -> RiskFramework:
    """
    Build a simple invalidation/risk framework from the latest technical state.
    """
    latest = df.iloc[-1]

    sma20 = _safe_float(latest.get("SMA_20"))
    sma50 = _safe_float(latest.get("SMA_50"))
    sma200 = _safe_float(latest.get("SMA_200"))
    support = _safe_float(latest.get("Rolling_Support_20"))
    resistance = _safe_float(latest.get("Rolling_Resistance_20"))
    rsi = _safe_float(latest.get("RSI_14"), 50.0)
    atr_pct = _safe_float(latest.get("ATR_pct_of_close"), 0.0)
    rel_perf_20 = _safe_float(latest.get("Relative_Performance_20d_pct"), 0.0)

    key_risks: list[str] = []
    thesis_breakers: list[str] = []

    invalidation_level = "No clear invalidation level identified yet."

    if trend.label in {"Strong uptrend", "Healthy uptrend", "Breakout / continuation attempt"}:
        if support:
            invalidation_level = (
                f"A decisive loss of recent support near {support:.2f} would materially weaken the bullish thesis."
            )
        elif sma50:
            invalidation_level = (
                f"A decisive loss of the 50-day area near {sma50:.2f} would materially weaken the bullish thesis."
            )

        thesis_breakers.extend(
            [
                "Loss of intermediate support",
                "Momentum fading below a constructive regime",
                "Failed breakout behavior or inability to hold higher lows",
            ]
        )

    elif trend.label in {"Healthy downtrend", "Breakdown / continuation attempt"}:
        if resistance:
            invalidation_level = (
                f"A decisive reclaim of resistance near {resistance:.2f} would weaken the bearish thesis."
            )
        elif sma50:
            invalidation_level = (
                f"A decisive reclaim of the 50-day area near {sma50:.2f} would weaken the bearish thesis."
            )

        thesis_breakers.extend(
            [
                "Reclaim of resistance",
                "Improving momentum and trend repair",
                "Failed breakdown behavior",
            ]
        )

    else:
        if support:
            invalidation_level = (
                f"Recent support near {support:.2f} is an important reference level for near-term thesis integrity."
            )
        elif sma20:
            invalidation_level = (
                f"The 20-day area near {sma20:.2f} is an important short-term reference level."
            )

        thesis_breakers.extend(
            [
                "Loss of key support",
                "Failure to improve from the current mixed state",
                "Volatility expansion in the wrong direction",
            ]
        )

    if atr_pct >= 4.5:
        key_risks.append("Volatility is elevated, which can make timing and risk control more difficult.")
    if rsi >= 70:
        key_risks.append("Momentum is stretched enough to raise short-term extension risk.")
    if rsi <= 30:
        key_risks.append("Oversold conditions can remain unstable even if a bounce develops.")
    if rel_perf_20 < 0:
        key_risks.append("The ticker has lagged its benchmark recently, which weakens leadership quality.")
    if _safe_bool(latest.get("Breakdown_Confirmed")):
        key_risks.append("Recent support failure is a direct caution signal.")
    if _safe_bool(latest.get("Close_above_BB_upper")):
        key_risks.append("Price is extended above the upper Bollinger Band.")
    if _safe_bool(latest.get("Close_below_BB_lower")):
        key_risks.append("Price is pressing below the lower Bollinger Band, which reflects technical weakness.")
    if _safe_bool(latest.get("Squeeze_On")):
        key_risks.append("Compression is high, so a larger move may be approaching but direction still matters.")

    if sma200 and trend.label in {"Healthy uptrend", "Strong uptrend"}:
        thesis_breakers.append(f"A decisive loss of the long-term trend zone near {sma200:.2f} would be a major warning sign.")

    return RiskFramework(
        invalidation_level=invalidation_level,
        key_risks=key_risks,
        thesis_breakers=thesis_breakers,
    )
