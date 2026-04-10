from __future__ import annotations

import pandas as pd

from src.pipeline.build_analysis import build_full_analysis


class DummyFetchResult:
    def __init__(self, ticker: str, period: str, interval: str, data: pd.DataFrame) -> None:
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.data = data


def make_sample_data(rows: int = 260) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=rows, freq="D")

    close = pd.Series(range(100, 100 + rows), dtype=float)
    df = pd.DataFrame(
        {
            "Open": close - 1.0,
            "High": close + 1.0,
            "Low": close - 2.0,
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=dates,
    )
    return df


def test_build_full_analysis_returns_expected_shape(monkeypatch) -> None:
    sample_df = make_sample_data()

    def mock_fetch_ohlcv(ticker: str, period: str, interval: str):
        return DummyFetchResult(
            ticker=ticker,
            period=period,
            interval=interval,
            data=sample_df,
        )

    monkeypatch.setattr("src.pipeline.build_analysis.fetch_ohlcv", mock_fetch_ohlcv)

    result = build_full_analysis("AAPL", period="1y", interval="1d")

    assert result.ticker == "AAPL"
    assert result.validation.is_valid is True
    assert isinstance(result.data, pd.DataFrame)
    assert len(result.data) == len(sample_df)
    assert isinstance(result.summary_text, str)
    assert len(result.summary_text) > 0


def test_build_full_analysis_contains_core_outputs(monkeypatch) -> None:
    sample_df = make_sample_data()

    def mock_fetch_ohlcv(ticker: str, period: str, interval: str):
        return DummyFetchResult(
            ticker=ticker,
            period=period,
            interval=interval,
            data=sample_df,
        )

    monkeypatch.setattr("src.pipeline.build_analysis.fetch_ohlcv", mock_fetch_ohlcv)

    result = build_full_analysis("MSFT", period="1y", interval="1d")

    assert result.trend.label != ""
    assert 0 <= result.scores.trend <= 100
    assert result.agreement.label != ""
    assert result.guidance.posture != ""
    assert result.scenarios.bull.title == "Bull case"
    assert isinstance(result.recent_changes, list)
    assert isinstance(result.evidence.trend, list)
