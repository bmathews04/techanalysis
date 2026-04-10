"""
Extension scoring.

Primary responsibility:
- estimate how stretched price is relative to key trend references
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ExtensionScore:
    score: int
    label: str
    reason: str


def _safe_float(value: object, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    return float(value)


def build_extension_score(df: pd.DataFrame) -> ExtensionScore:
    """
    Build a 0-100 extension score where higher means more stretched.
    """
    latest = df.iloc[-1]

    ext20 = abs(_safe_float(latest.get("Extension_vs_SMA20_pct"), 0.0))
    ext50 = abs(_safe_float(latest.get("Extension_vs_SMA50_pct"), 0.0))
    bb_pos = _safe_float(latest.get("BB_Position_pct"), 50.0)
    rsi = _safe_float(latest.get("RSI_14"), 50.0)

    raw = 0.0

    if ext20 >= 8:
        raw += 35
    elif ext20 >= 5:
        raw += 25
    elif ext20 >= 3:
        raw += 15

    if ext50 >= 12:
        raw += 30
    elif ext50 >= 8:
        raw += 20
    elif ext50 >= 5:
        raw += 10

    if bb_pos >= 95 or bb_pos <= 5:
        raw += 20
    elif bb_pos >= 85 or bb_pos <= 15:
        raw += 10

    if rsi >= 70 or rsi <= 30:
        raw += 15
    elif rsi >= 65 or rsi <= 35:
        raw += 8

    score = max(0, min(100, int(round(raw))))

    if score >= 70:
        return ExtensionScore(
            score=score,
            label="Highly extended",
            reason="Price is stretched relative to trend references and/or momentum extremes.",
        )
    if score >= 45:
        return ExtensionScore(
            score=score,
            label="Moderately extended",
            reason="The chart is somewhat stretched, so timing quality may be less forgiving.",
        )
    return ExtensionScore(
        score=score,
        label="Not materially extended",
        reason="Price is not showing major stretch relative to core trend references.",
    )
