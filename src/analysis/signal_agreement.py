"""
Signal agreement logic.

Primary responsibility:
- interpret whether technical categories are aligned or conflicting
- produce a readable agreement label and explanation
"""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.signal_scores import SignalScores


@dataclass(frozen=True)
class SignalAgreement:
    label: str
    score: int
    reason: str


def build_signal_agreement(scores: SignalScores) -> SignalAgreement:
    """
    Convert category scores into an overall alignment summary.

    Interpretation:
    - High agreement means multiple categories point in the same direction
    - Mixed agreement means categories conflict or show uneven conviction
    """
    values = [
        scores.trend,
        scores.momentum,
        scores.volatility,
        scores.volume,
        scores.structure,
    ]

    avg_score = round(sum(values) / len(values))

    bullish_count = sum(v >= 65 for v in values)
    bearish_count = sum(v <= 35 for v in values)
    neutral_count = len(values) - bullish_count - bearish_count

    # Strong bullish agreement
    if bullish_count >= 4:
        return SignalAgreement(
            label="Strong bullish agreement",
            score=avg_score,
            reason=(
                "Most technical categories are aligned in a constructive direction, "
                "which increases confidence in the current bullish read."
            ),
        )

    # Strong bearish agreement
    if bearish_count >= 4:
        return SignalAgreement(
            label="Strong bearish agreement",
            score=avg_score,
            reason=(
                "Most technical categories are aligned in a weak or deteriorating direction, "
                "which increases confidence in the current bearish read."
            ),
        )

    # Moderate bullish agreement
    if bullish_count >= 3 and bearish_count == 0:
        return SignalAgreement(
            label="Moderate bullish agreement",
            score=avg_score,
            reason=(
                "Several major categories are supportive, though one or more areas remain less decisive."
            ),
        )

    # Moderate bearish agreement
    if bearish_count >= 3 and bullish_count == 0:
        return SignalAgreement(
            label="Moderate bearish agreement",
            score=avg_score,
            reason=(
                "Several major categories are weak, though one or more areas remain less decisive."
            ),
        )

    # Mixed / conflicted
    if bullish_count >= 1 and bearish_count >= 1:
        return SignalAgreement(
            label="Mixed / conflicting signals",
            score=avg_score,
            reason=(
                "Some categories are constructive while others are cautionary, "
                "which reduces conviction and favors selectivity."
            ),
        )

    # Mostly neutral
    if neutral_count >= 3:
        return SignalAgreement(
            label="Mostly neutral / low-conviction",
            score=avg_score,
            reason=(
                "The chart is not showing strong cross-category alignment, "
                "which suggests a lower-edge environment."
            ),
        )

    return SignalAgreement(
        label="Moderate mixed agreement",
        score=avg_score,
        reason=(
            "The technical picture is somewhat directional, but not all categories are aligned."
        ),
    )
