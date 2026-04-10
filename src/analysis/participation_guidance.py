"""
Participation guidance engine.

Primary responsibility:
- translate technical state into educational participation framing
- avoid direct trade instructions
- provide a clear posture and reasoning
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analysis.signal_agreement import SignalAgreement
from src.analysis.signal_scores import SignalScores
from src.analysis.trend_classifier import TrendClassification


@dataclass(frozen=True)
class ParticipationGuidance:
    posture: str
    confidence: float
    summary: str
    considerations: list[str]
    caution_flags: list[str]


def _safe_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def build_participation_guidance(
    df: pd.DataFrame,
    trend: TrendClassification,
    scores: SignalScores,
    agreement: SignalAgreement,
) -> ParticipationGuidance:
    """
    Build educational participation guidance from the latest technical state.
    """
    latest = df.iloc[-1]

    rsi = _safe_float(latest.get("RSI_14"), 50.0)
    close_vs_sma20 = _safe_float(latest.get("Close_vs_SMA_20_pct"), 0.0)
    close_vs_sma50 = _safe_float(latest.get("Close_vs_SMA_50_pct"), 0.0)
    atr_pct = _safe_float(latest.get("ATR_pct_of_close"), 0.0)
    pct_to_resistance = _safe_float(latest.get("Pct_to_Resistance"), 999.0)

    breakout = _safe_bool(latest.get("Breakout_Confirmed"))
    breakdown = _safe_bool(latest.get("Breakdown_Confirmed"))
    overbought = _safe_bool(latest.get("RSI_overbought"))
    oversold = _safe_bool(latest.get("RSI_oversold"))
    bb_upper = _safe_bool(latest.get("Close_above_BB_upper"))
    bb_lower = _safe_bool(latest.get("Close_below_BB_lower"))

    considerations: list[str] = []
    caution_flags: list[str] = []

    posture = "Patience / selective participation"
    confidence = 5.0
    summary = (
        "The current setup appears mixed, so a more selective and patient stance is favored."
    )

    strong_bullish = (
        trend.label in {"Strong uptrend", "Healthy uptrend", "Breakout / continuation attempt"}
        and scores.trend >= 65
        and scores.momentum >= 55
    )
    strong_bearish = (
        trend.label in {"Healthy downtrend", "Breakdown / continuation attempt"}
        and scores.trend <= 40
    )

    extended_upside = (
        overbought
        or bb_upper
        or close_vs_sma20 >= 5
        or close_vs_sma50 >= 10
    )

    elevated_volatility = atr_pct >= 4.5
    near_resistance = pct_to_resistance <= 2.0 if pct_to_resistance != 999.0 else False

    if strong_bullish and not extended_upside and agreement.label in {
        "Strong bullish agreement",
        "Moderate bullish agreement",
    }:
        posture = "Trend-friendly / accumulation-friendly"
        confidence = 8.2
        summary = (
            "The chart environment is constructive, with trend and momentum supportive enough "
            "to favor measured participation rather than extreme defensiveness."
        )
        considerations.extend(
            [
                "The broader trend is supportive.",
                "Momentum is aligned with the trend.",
                "This kind of environment is often more forgiving than a mixed chart.",
            ]
        )

    elif strong_bullish and extended_upside:
        posture = "Pullback-friendly / avoid chasing extension"
        confidence = 7.4
        summary = (
            "The broader trend remains constructive, but the chart looks somewhat extended, "
            "which lowers the quality of aggressive upside chasing."
        )
        considerations.extend(
            [
                "The larger trend still looks healthy.",
                "A cleaner reset or pullback may offer a more favorable decision point.",
                "Trend strength is constructive, but timing quality is less ideal at current extension.",
            ]
        )
        caution_flags.append("Short-term extension is elevated.")

    elif breakout and scores.structure >= 65 and scores.volume >= 50:
        posture = "Breakout-watch / confirmation-focused"
        confidence = 7.1
        summary = (
            "The chart is attempting to push into a new leg higher, but follow-through matters "
            "more than the initial move itself."
        )
        considerations.extend(
            [
                "Recent resistance has been challenged or exceeded.",
                "Confirmation quality improves if the move continues to hold above the breakout area.",
                "Volume and follow-through are important here.",
            ]
        )

    elif trend.label == "Bullish reversal attempt":
        posture = "Early improvement / defined-risk mindset"
        confidence = 6.0
        summary = (
            "Conditions are improving on a short-term basis, but the chart has not yet fully "
            "proved itself as a durable trend."
        )
        considerations.extend(
            [
                "Short-term momentum is improving.",
                "Intermediate trend structure is still in repair mode.",
                "This kind of setup often needs more confirmation than an established uptrend.",
            ]
        )
        caution_flags.append("Trend repair is incomplete.")

    elif strong_bearish:
        posture = "Defensive / caution zone"
        confidence = 8.0
        summary = (
            "The technical backdrop remains weak, so defensive positioning and elevated selectivity "
            "make more sense than optimistic participation."
        )
        considerations.extend(
            [
                "Trend structure remains weak.",
                "Momentum is not yet showing durable improvement.",
                "This environment generally demands more caution than a constructive trend.",
            ]
        )

    elif oversold and scores.momentum < 45:
        posture = "Capitulation-watch / avoid assuming immediate recovery"
        confidence = 5.8
        summary = (
            "The chart may be washed out on a short-term basis, but oversold readings alone do not "
            "guarantee a durable recovery."
        )
        considerations.extend(
            [
                "Oversold conditions can create bounces, but not always trend reversals.",
                "Stronger evidence would include support holding and momentum improving.",
                "Short-term reflex strength and true trend repair are not the same thing.",
            ]
        )
        caution_flags.append("Oversold does not equal safe.")

    else:
        posture = "Patience / no clear edge"
        confidence = 5.2
        summary = (
            "The technical picture is not especially clean right now, so patience may be more useful "
            "than forcing a directional opinion."
        )
        considerations.extend(
            [
                "Signals are mixed or only partially aligned.",
                "Better opportunities often come when trend, momentum, and structure tell a clearer story.",
                "No-action can be a high-quality decision in low-edge conditions.",
            ]
        )

    if elevated_volatility:
        caution_flags.append("Volatility is elevated.")
    if near_resistance:
        caution_flags.append("Price is near resistance.")
    if breakdown:
        caution_flags.append("Recent support has failed.")
    if bb_lower:
        caution_flags.append("Price is pressing the lower Bollinger Band.")

    return ParticipationGuidance(
        posture=posture,
        confidence=round(confidence, 1),
        summary=summary,
        considerations=considerations,
        caution_flags=caution_flags,
    )
