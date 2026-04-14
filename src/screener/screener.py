"""
Market screener utilities.

Primary responsibility:
- run the existing single-ticker pipeline across many tickers
- classify each ticker into bullish / bearish buckets
- return a clean result object for the Streamlit UI
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.pipeline.build_analysis import AnalysisResult, build_full_analysis


@dataclass(frozen=True)
class ScreenedTicker:
    ticker: str
    classification: str
    trend_label: str
    agreement_label: str
    trend_score: int
    momentum_score: int
    volatility_score: int
    volume_score: int
    structure_score: int
    summary_text: str


@dataclass(frozen=True)
class ScreenResult:
    strong_bullish: list[ScreenedTicker]
    bullish: list[ScreenedTicker]
    strong_bearish: list[ScreenedTicker]
    bearish: list[ScreenedTicker]
    mixed: list[ScreenedTicker]
    skipped: list[tuple[str, str]]


def parse_tickers(raw_text: str) -> list[str]:
    """
    Parse comma-separated, newline-separated, or space-separated tickers.
    """
    if not raw_text or not raw_text.strip():
        return []

    normalized = raw_text.replace(",", "\n").replace(";", "\n").replace("\t", "\n")
    tickers: list[str] = []

    for line in normalized.splitlines():
        for token in line.strip().split():
            cleaned = token.strip().upper()
            if cleaned and cleaned not in tickers:
                tickers.append(cleaned)

    return tickers


def classify_analysis(result: AnalysisResult) -> str:
    """
    Convert the existing pipeline output into a screener bucket.

    This keeps the screener aligned with the app's current rule system.
    """
    trend_label = result.trend.label
    agreement_label = result.agreement.label

    strong_bullish = (
        trend_label in {
            "Strong uptrend",
            "Healthy uptrend",
            "Breakout / continuation attempt",
        }
        and agreement_label == "Strong bullish agreement"
        and result.scores.trend >= 70
        and result.scores.momentum >= 60
    )

    bullish = (
        trend_label in {
            "Strong uptrend",
            "Healthy uptrend",
            "Breakout / continuation attempt",
            "Bullish reversal attempt",
        }
        and agreement_label in {
            "Strong bullish agreement",
            "Moderate bullish agreement",
        }
    )

    strong_bearish = (
        trend_label in {
            "Healthy downtrend",
            "Breakdown / continuation attempt",
        }
        and agreement_label == "Strong bearish agreement"
        and result.scores.trend <= 35
        and result.scores.momentum <= 40
    )

    bearish = (
        trend_label in {
            "Healthy downtrend",
            "Breakdown / continuation attempt",
        }
        and agreement_label in {
            "Strong bearish agreement",
            "Moderate bearish agreement",
        }
    )

    if strong_bullish:
        return "Strong bullish"
    if strong_bearish:
        return "Strong bearish"
    if bullish:
        return "Bullish"
    if bearish:
        return "Bearish"
    return "Mixed"

def _to_screened_ticker(result: AnalysisResult) -> ScreenedTicker:
    classification = classify_analysis(result)

    return ScreenedTicker(
        ticker=result.ticker,
        classification=classification,
        trend_label=result.trend.label,
        agreement_label=result.agreement.label,
        trend_score=result.scores.trend,
        momentum_score=result.scores.momentum,
        volatility_score=result.scores.volatility,
        volume_score=result.scores.volume,
        structure_score=result.scores.structure,
        summary_text=result.summary_text,
    )


def _sort_key(item: ScreenedTicker) -> tuple[int, int, int]:
    """
    Higher trend / momentum / structure names go first.
    """
    return (
        item.trend_score,
        item.momentum_score,
        item.structure_score,
    )


def run_market_screen(
    tickers: Iterable[str],
    period: str,
    interval: str,
    benchmark: str = "SPY",
) -> ScreenResult:
    """
    Run the existing full analysis across a list of tickers.
    """
    strong_bullish: list[ScreenedTicker] = []
    bullish: list[ScreenedTicker] = []
    strong_bearish: list[ScreenedTicker] = []
    bearish: list[ScreenedTicker] = []
    mixed: list[ScreenedTicker] = []
    skipped: list[tuple[str, str]] = []

    for raw_ticker in tickers:
        ticker = raw_ticker.strip().upper()
        if not ticker:
            continue

        try:
            result = build_full_analysis(
                ticker=ticker,
                period=period,
                interval=interval,
                benchmark=benchmark,
            )
            screened = _to_screened_ticker(result)

            if screened.classification == "Strong bullish":
                strong_bullish.append(screened)
            elif screened.classification == "Bullish":
                bullish.append(screened)
            elif screened.classification == "Strong bearish":
                strong_bearish.append(screened)
            elif screened.classification == "Bearish":
                bearish.append(screened)
            else:
                mixed.append(screened)

        except Exception as exc:
            skipped.append((ticker, str(exc)))

    strong_bullish.sort(key=_sort_key, reverse=True)
    bullish.sort(key=_sort_key, reverse=True)

    strong_bearish.sort(
        key=lambda x: (x.trend_score, x.momentum_score, x.structure_score)
    )
    bearish.sort(
        key=lambda x: (x.trend_score, x.momentum_score, x.structure_score)
    )

    mixed.sort(key=_sort_key, reverse=True)

    return ScreenResult(
        strong_bullish=strong_bullish,
        bullish=bullish,
        strong_bearish=strong_bearish,
        bearish=bearish,
        mixed=mixed,
        skipped=skipped,
    )
