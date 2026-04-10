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

from src.analysis.extension_score import ExtensionScore, build_extension_score
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
from src.explain.risk_builder import RiskFramework, build_risk_framework
from src.explain.summary_text import build_summary_text
from src.indicators.advanced_volatility import add_advanced_volatility_features
from src.indicators.momentum import add_momentum_features
from src.indicators.relative_strength import add_relative_strength_features
from src.indicators.structure import add_structure_features
from src.indicators.trend import add_trend_features
from src.indicators.volatility import add_volatility_features
from src.indicators.volume import add_volume_features


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    period: str
    interval: str
    benchmark: str
    data: pd.DataFrame
    validation: ValidationResult
    trend: TrendClassification
    scores: SignalScores
    agreement: SignalAgreement
    extension: ExtensionScore
    guidance: ParticipationGuidance
    scenarios: ScenarioSet
    recent_changes: list[str]
    evidence: EvidenceBundle
    risk: RiskFramework
    summary_text: str


def build_full_analysis(
    ticker: str = DEFAULT_TICKER,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
    min_rows: int = MIN_REQUIRED_ROWS,
    benchmark: str = "SPY",
) -> AnalysisResult:
    """
    Run the full single-ticker technical analysis pipeline.
    """
    cleaned_ticker = clean_ticker(ticker)
    cleaned_benchmark = clean_ticker(benchmark)

    fetch_result = fetch_ohlcv(
        ticker=cleaned_ticker,
        period=period,
        interval=interval,
    )

    benchmark_result = fetch_ohlcv(
        ticker=cleaned_benchmark,
        period=period,
        interval=interval,
    )

    df = normalize_ohlcv(fetch_result.data)
    df, validation = validate_ohlcv(df, min_rows=min_rows)

    benchmark_df = normalize_ohlcv(benchmark_result.data)
    benchmark_df, _ = validate_ohlcv(benchmark_df, min_rows=min_rows)

    # Indicators
    df = add_trend_features(df)
    df = add_momentum_features(df)
    df = add_volatility_features(df)
    df = add_volume_features(df)
    df = add_structure_features(df)
    df = add_relative_strength_features(df, benchmark_df=benchmark_df)
    df = add_advanced_volatility_features(df)

    # Analysis / interpretation
    trend = classify_trend_regime(df)
    scores = build_signal_scores(df)
    agreement = build_signal_agreement(scores)
    extension = build_extension_score(df)
    guidance = build_participation_guidance(df, trend, scores, agreement)
    scenarios = build_scenarios(df, trend)
    recent_changes = build_recent_changes(df)
    evidence = build_evidence(df, trend, scores)
    risk = build_risk_framework(df, trend)
    summary_text = build_summary_text(cleaned_ticker, trend, scores, agreement, guidance)

    return AnalysisResult(
        ticker=cleaned_ticker,
        period=period,
        interval=interval,
        benchmark=cleaned_benchmark,
        data=df,
        validation=validation,
        trend=trend,
        scores=scores,
        agreement=agreement,
        extension=extension,
        guidance=guidance,
        scenarios=scenarios,
        recent_changes=recent_changes,
        evidence=evidence,
        risk=risk,
        summary_text=summary_text,
    )
