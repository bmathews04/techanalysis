"""
Market data fetching utilities.

Primary responsibility:
- fetch OHLCV price data for a single ticker
- return a pandas DataFrame in raw form for downstream normalization

This module should not perform indicator calculations.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FetchResult:
    ticker: str
    period: str
    interval: str
    data: pd.DataFrame


def clean_ticker(ticker: str) -> str:
    """
    Normalize ticker input from the user.

    Examples:
    - ' aapl ' -> 'AAPL'
    - 'msft' -> 'MSFT'
    """
    if not isinstance(ticker, str):
        raise TypeError("Ticker must be a string.")

    cleaned = ticker.strip().upper()
    if not cleaned:
        raise ValueError("Ticker cannot be empty.")

    return cleaned


def fetch_ohlcv(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = False,
) -> FetchResult:
    """
    Fetch OHLCV data from Yahoo Finance via yfinance.
    """
    cleaned_ticker = clean_ticker(ticker)

    try:
        import yfinance as yf
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "yfinance is required to fetch market data. Install it from requirements.txt."
        ) from exc

    try:
        df = yf.download(
            tickers=cleaned_ticker,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            progress=False,
            threads=False,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to fetch data for {cleaned_ticker}: {exc}") from exc

    if df is None or df.empty:
        raise ValueError(
            f"No market data returned for ticker '{cleaned_ticker}' "
            f"with period='{period}' and interval='{interval}'."
        )

    return FetchResult(
        ticker=cleaned_ticker,
        period=period,
        interval=interval,
        data=df.copy(),
    )
