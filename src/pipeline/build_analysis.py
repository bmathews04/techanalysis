"""
End-to-end analysis pipeline.

Primary responsibility:
- fetch, normalize, and validate market data
- compute indicators and analysis outputs
- return one clean result object for the Streamlit UI
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analysis.participation_guidance import (
    ParticipationGuidance,
    build_participation_guidance,
)
from src.analysis.recent_changes import build_recent_changes
from src.analysis.scenario_engine import ScenarioSet, build_scenarios
from src.analysis.signal_agreement import SignalAgreement, build_signal_agreement
from src.analysis.signal_scores import SignalScores, build_signal_scores
from src.analysis.trend_classifier import TrendClassification, classify_trend_regime
from src.config.settings import (
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    DEFAULT_TICKER,
    MIN_REQUIRED_ROWS,
)
from src.data.fetch import clean_ticker, fetch_ohlcv
from src.data.normalize import normalize_ohlcv
from src.data.validate import ValidationResult, validate_ohlcv
from src.explain.evidence_builder import EvidenceBundle, build_evidence
from src.explain.summary_text import build_summary_text
from src.indicators.momentum import add_momentum_features
from src.indicators.structure import add_structure_features
from src.indicators.trend import add_trend_features
from src.indicators.volatility import add_volatility_features
from src.indicators.volume import add_volume_features


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    period: str
    interval: str
    data: pd.DataFrame
    validation: ValidationResult
    trend: TrendClassification
    scores: SignalScores
    agreement: SignalAgreement
    guidance: ParticipationGuidance
    scenarios: ScenarioSet
    recent_changes: list[str]
    evidence: EvidenceBundle
    summary_text: str


def build_full_analysis(
    ticker: str = DEFAULT_TICKER,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
    min_rows: int = MIN_REQUIRED_ROWS,
) -> AnalysisResult:
    """
    Run the full single-ticker technical analysis pipeline.

    Parameters
    ----------
    ticker : str
        Ticker symbol to analyze.
    period : str
        Historical period to fetch.
    interval : str
        Data interval to use.
    min_rows : int
        Minimum rows required after validation.

    Returns
    -------
    AnalysisResult
        A structured object ready for the UI layer.
    """
    cleaned_ticker = clean_ticker(ticker)

    fetch_result = fetch_ohlcv(
        ticker=cleaned_ticker,
        period=period,
        interval=interval,
    )

    df = normalize_ohlcv(fetch_result.data)
    df, validation = validate_ohlcv(df, min_rows=min_rows)

    # Indicators
    df = add_trend_features(df)
    df = add_momentum_features(df)
    df = add_volatility_features(df)
    df = add_volume_features(df)
    df = add_structure_features(df)

    # Analysis / interpretation
    trend = classify_trend_regime(df)
    scores = build_signal_scores(df)
    agreement = build_signal_agreement(scores)
    guidance = build_participation_guidance(df, trend, scores, agreement)
    scenarios = build_scenarios(df, trend)
    recent_changes = build_recent_changes(df)
    evidence = build_evidence(df, trend, scores)
    summary_text = build_summary_text(cleaned_ticker, trend, scores, agreement, guidance)

    return AnalysisResult(
        ticker=cleaned_ticker,
        period=period,
        interval=interval,
        data=df,
        validation=validation,
        trend=trend,
        scores=scores,
        agreement=agreement,
        guidance=guidance,
        scenarios=scenarios,
        recent_changes=recent_changes,
        evidence=evidence,
        summary_text=summary_text,
    )
