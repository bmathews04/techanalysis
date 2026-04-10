"""
Plain-English summary builder.

Primary responsibility:
- translate technical state into a concise readable summary
- keep language educational, not advisory
"""

from __future__ import annotations

from src.analysis.participation_guidance import ParticipationGuidance
from src.analysis.signal_agreement import SignalAgreement
from src.analysis.signal_scores import SignalScores
from src.analysis.trend_classifier import TrendClassification


def _score_descriptor(score: int) -> str:
    if score >= 80:
        return "very strong"
    if score >= 65:
        return "constructive"
    if score >= 50:
        return "mixed but acceptable"
    if score >= 35:
        return "fragile"
    return "weak"


def build_summary_text(
    ticker: str,
    trend: TrendClassification,
    scores: SignalScores,
    agreement: SignalAgreement,
    guidance: ParticipationGuidance,
) -> str:
    """
    Build the main top-of-page educational summary paragraph.
    """
    trend_desc = trend.label.lower()
    momentum_desc = _score_descriptor(scores.momentum)
    structure_desc = _score_descriptor(scores.structure)
    volatility_desc = _score_descriptor(scores.volatility)

    opening = (
        f"{ticker} is currently in a {trend_desc}, with trend quality registering as "
        f"{_score_descriptor(scores.trend)} and overall signal alignment reading as "
        f"'{agreement.label.lower()}'."
    )

    middle = (
        f"Momentum appears {momentum_desc}, structure looks {structure_desc}, and the current "
        f"volatility environment is {volatility_desc} for participation quality."
    )

    closing = (
        f"From an educational decision-making standpoint, the current posture is best described as "
        f"'{guidance.posture.lower()}', because {guidance.summary[0].lower() + guidance.summary[1:]}"
    )

    return " ".join([opening, middle, closing])
