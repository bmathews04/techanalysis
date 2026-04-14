from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from src.data.sp500_tickers import SP500_TICKERS
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
    if not raw_text or not raw_text.strip():
        return []

    normalized = (
        raw_text.replace(",", "\n")
        .replace(";", "\n")
        .replace("\t", "\n")
    )

    tickers: list[str] = []
    seen: set[str] = set()

    for line in normalized.splitlines():
        for token in line.strip().split():
            cleaned = token.strip().upper()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                tickers.append(cleaned)

    return tickers


def get_sp500_tickers(use_live_fetch: bool = False) -> list[str]:
    """
    Return S&P 500 tickers.

    By default this uses a local baked-in list for reliability.
    Set use_live_fetch=True if you want to attempt Wikipedia first.
    """
    if not use_live_fetch:
        return list(SP500_TICKERS)

    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    try:
        tables = pd.read_html(url)
        if not tables:
            return list(SP500_TICKERS)

        companies = tables[0]
        if "Symbol" not in companies.columns:
            return list(SP500_TICKERS)

        raw_tickers = (
            companies["Symbol"]
            .astype(str)
            .str.strip()
            .str.upper()
            .tolist()
        )

        cleaned: list[str] = []
        seen: set[str] = set()

        for ticker in raw_tickers:
            normalized = ticker.replace(".", "-")
            if normalized and normalized not in seen:
                seen.add(normalized)
                cleaned.append(normalized)

        return cleaned if cleaned else list(SP500_TICKERS)

    except Exception:
        return list(SP500_TICKERS)


def classify_analysis(result: AnalysisResult) -> str:
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


def _bullish_sort_key(item: ScreenedTicker) -> tuple[int, int, int, int, int]:
    return (
        item.trend_score,
        item.momentum_score,
        item.structure_score,
        item.volume_score,
        item.volatility_score,
    )


def _bearish_sort_key(item: ScreenedTicker) -> tuple[int, int, int, int, int]:
    return (
        item.trend_score,
        item.momentum_score,
        item.structure_score,
        item.volume_score,
        item.volatility_score,
    )


def run_market_screen(
    tickers: Iterable[str],
    period: str,
    interval: str,
    benchmark: str = "SPY",
    per_ticker_pause_seconds: float = 0.35,
) -> ScreenResult:
    """
    Run the existing full analysis across a list of tickers.
    """
    import time

    ticker_list = [t.strip().upper() for t in tickers if str(t).strip()]

    strong_bullish: list[ScreenedTicker] = []
    bullish: list[ScreenedTicker] = []
    strong_bearish: list[ScreenedTicker] = []
    bearish: list[ScreenedTicker] = []
    mixed: list[ScreenedTicker] = []
    skipped: list[tuple[str, str]] = []

    for idx, ticker in enumerate(ticker_list):
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

        if per_ticker_pause_seconds > 0 and idx < len(ticker_list) - 1:
            time.sleep(per_ticker_pause_seconds)

    strong_bullish.sort(key=_bullish_sort_key, reverse=True)
    bullish.sort(key=_bullish_sort_key, reverse=True)
    strong_bearish.sort(key=_bearish_sort_key)
    bearish.sort(key=_bearish_sort_key)
    mixed.sort(key=_bullish_sort_key, reverse=True)

    return ScreenResult(
        strong_bullish=strong_bullish,
        bullish=bullish,
        strong_bearish=strong_bearish,
        bearish=bearish,
        mixed=mixed,
        skipped=skipped,
    )

def slice_ticker_batch(
    tickers: list[str],
    batch_size: int,
    batch_number: int,
) -> tuple[list[str], int, int, int]:
    """
    Return one batch of tickers plus batch metadata.

    batch_number is 1-based.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    if batch_number <= 0:
        raise ValueError("batch_number must be greater than 0.")

    total = len(tickers)
    if total == 0:
        return [], 0, 0, 0

    start_idx = (batch_number - 1) * batch_size
    end_idx = min(start_idx + batch_size, total)

    if start_idx >= total:
        return [], start_idx, end_idx, total

    return tickers[start_idx:end_idx], start_idx, end_idx, total

def merge_screen_results(results: list[ScreenResult]) -> ScreenResult:
    """
    Merge many batch-level ScreenResult objects into one combined result.
    """
    strong_bullish: list[ScreenedTicker] = []
    bullish: list[ScreenedTicker] = []
    strong_bearish: list[ScreenedTicker] = []
    bearish: list[ScreenedTicker] = []
    mixed: list[ScreenedTicker] = []
    skipped: list[tuple[str, str]] = []

    for result in results:
        strong_bullish.extend(result.strong_bullish)
        bullish.extend(result.bullish)
        strong_bearish.extend(result.strong_bearish)
        bearish.extend(result.bearish)
        mixed.extend(result.mixed)
        skipped.extend(result.skipped)

    strong_bullish.sort(key=_bullish_sort_key, reverse=True)
    bullish.sort(key=_bullish_sort_key, reverse=True)
    strong_bearish.sort(key=_bearish_sort_key)
    bearish.sort(key=_bearish_sort_key)
    mixed.sort(key=_bullish_sort_key, reverse=True)

    return ScreenResult(
        strong_bullish=strong_bullish,
        bullish=bullish,
        strong_bearish=strong_bearish,
        bearish=bearish,
        mixed=mixed,
        skipped=skipped,
    )

def split_into_batches(tickers: list[str], batch_size: int) -> list[list[str]]:
    """
    Split tickers into sequential batches.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    return [
        tickers[i:i + batch_size]
        for i in range(0, len(tickers), batch_size)
    ]
