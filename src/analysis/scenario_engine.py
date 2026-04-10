"""
Scenario engine.

Primary responsibility:
- generate bull, base, and bear technical scenarios
- define what conditions matter next
- keep outputs educational and conditional
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analysis.trend_classifier import TrendClassification


@dataclass(frozen=True)
class Scenario:
    title: str
    trigger: str
    implication: str
    watch_items: list[str]


@dataclass(frozen=True)
class ScenarioSet:
    bull: Scenario
    base: Scenario
    bear: Scenario


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def build_scenarios(
    df: pd.DataFrame,
    trend: TrendClassification,
) -> ScenarioSet:
    """
    Build bull/base/bear technical scenarios from the latest bar.
    """
    latest = df.iloc[-1]

    close = _safe_float(latest.get("Close"))
    resistance = _safe_float(latest.get("Rolling_Resistance_20"))
    support = _safe_float(latest.get("Rolling_Support_20"))
    sma20 = _safe_float(latest.get("SMA_20"))
    sma50 = _safe_float(latest.get("SMA_50"))
    rsi = _safe_float(latest.get("RSI_14"), 50.0)

    bull_trigger = (
        f"Price holds above near-term support and reasserts strength through {resistance:.2f}."
        if resistance
        else "Price continues to hold support and reassert upward momentum."
    )
    bull_implication = (
        "That would strengthen the case for trend continuation and suggest buyers still control the tape."
    )
    bull_watch = [
        "Follow-through after any breakout attempt",
        "Momentum staying constructive rather than fading",
        "Volume support on advancing sessions",
    ]

    base_trigger = (
        f"Price stays between {support:.2f} and {resistance:.2f} while momentum cools but does not break."
        if support and resistance
        else "Price consolidates without a major technical failure or breakout."
    )
    base_implication = (
        "That would point to digestion or consolidation rather than a decisive directional move."
    )
    base_watch = [
        "Whether pullbacks remain orderly",
        "Whether support continues to hold",
        "Whether volatility contracts or expands",
    ]

    bear_trigger = (
        f"Price loses support around {support:.2f} and fails to reclaim it."
        if support
        else "Price loses near-term support and momentum deteriorates further."
    )
    bear_implication = (
        "That would weaken the current thesis and raise the odds of a deeper correction or trend deterioration."
    )
    bear_watch = [
        "Loss of key moving averages",
        "Expanding downside volatility",
        "Weak volume profile on attempted rebounds",
    ]

    if trend.label in {"Strong uptrend", "Healthy uptrend"}:
        bull_trigger = (
            f"Price respects the 20-day/50-day trend area and pushes through {resistance:.2f}."
            if resistance
            else "Price continues to respect trend support and prints higher highs."
        )
        base_trigger = (
            f"Price consolidates above the 50-day area near {sma50:.2f} without structural damage."
            if sma50
            else "Price digests gains without materially damaging the broader trend."
        )
        bear_trigger = (
            f"Price loses the 50-day area near {sma50:.2f} and momentum slips below a constructive regime."
            if sma50
            else "Price loses intermediate trend support and momentum weakens materially."
        )

    elif trend.label in {"Healthy downtrend", "Breakdown / continuation attempt"}:
        bull_trigger = (
            f"Price reclaims the 20-day/50-day area and momentum improves meaningfully from RSI {rsi:.1f}."
            if sma50
            else "Price reclaims key trend levels and momentum improves materially."
        )
        bull_implication = (
            "That would signal trend repair is beginning and the bearish case is weakening."
        )

        base_trigger = "Price continues drifting lower or sideways without strong reversal evidence."
        base_implication = (
            "That would keep the technical picture defensive rather than decisively improved."
        )

        bear_trigger = (
            f"Price remains below resistance near {resistance:.2f} and breaks to fresh relative lows."
            if resistance
            else "Price remains suppressed below trend resistance and extends the breakdown."
        )
        bear_implication = (
            "That would reinforce the bearish structure and suggest sellers remain in control."
        )

    elif trend.label == "Bullish reversal attempt":
        bull_trigger = (
            f"Price reclaims the 50-day area near {sma50:.2f} and holds above it."
            if sma50
            else "Price continues repairing trend structure and confirms momentum improvement."
        )
        bull_implication = (
            "That would improve the odds that the reversal is becoming something more durable."
        )

        base_trigger = (
            f"Price oscillates between support near {support:.2f} and resistance near {resistance:.2f}."
            if support and resistance
            else "Price chops sideways while the attempted repair remains incomplete."
        )
        base_implication = (
            "That would keep the chart in a proving phase rather than a fully restored uptrend."
        )

        bear_trigger = (
            f"Price rolls back under support near {support:.2f} and loses recent momentum."
            if support
            else "Price loses recent improvement and slips back into a weaker structure."
        )
        bear_implication = (
            "That would imply the reversal attempt failed to gain traction."
        )

    return ScenarioSet(
        bull=Scenario(
            title="Bull case",
            trigger=bull_trigger,
            implication=bull_implication,
            watch_items=bull_watch,
        ),
        base=Scenario(
            title="Base case",
            trigger=base_trigger,
            implication=base_implication,
            watch_items=base_watch,
        ),
        bear=Scenario(
            title="Bear case",
            trigger=bear_trigger,
            implication=bear_implication,
            watch_items=bear_watch,
        ),
    )
