"""
Market data fetching utilities.

Primary responsibility:
- fetch OHLCV price data for a single ticker
- return a pandas DataFrame in raw form for downstream normalization
"""

from __future__ import annotations

from dataclasses import dataclass
import time

import pandas as pd


@dataclass(frozen=True)
class FetchResult:
    ticker: str
    period: str
    interval: str
    data: pd.DataFrame


def clean_ticker(ticker: str) -> str:
    if not isinstance(ticker, str):
        raise TypeError("Ticker must be a string.")

    cleaned = ticker.strip().upper()
    if not cleaned:
        raise ValueError("Ticker cannot be empty.")

    return cleaned


def _is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "ratelimit" in text
        or "rate limit" in text
        or "too many requests" in text
        or "yfratelimiterror" in text
    )


def fetch_ohlcv(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = False,
    max_retries: int = 4,
    retry_delay_seconds: float = 2.0,
) -> FetchResult:
    """
    Fetch OHLCV data from Yahoo Finance via yfinance.

    Retries when rate-limited and raises a friendly error if all attempts fail.
    """
    cleaned_ticker = clean_ticker(ticker)

    try:
        import yfinance as yf
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "yfinance is required to fetch market data. Install it from requirements.txt."
        ) from exc

    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            df = yf.download(
                tickers=cleaned_ticker,
                period=period,
                interval=interval,
                auto_adjust=auto_adjust,
                progress=False,
                threads=False,
            )

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

        except Exception as exc:  # pragma: no cover
            last_exc = exc

            if attempt >= max_retries:
                break

            if _is_rate_limit_error(exc):
                sleep_for = retry_delay_seconds * (2 ** attempt)
                time.sleep(sleep_for)
                continue

            # non-rate-limit error: do not keep retrying forever
            time.sleep(0.5)

    if last_exc and _is_rate_limit_error(last_exc):
        raise RuntimeError(
            f"Yahoo Finance rate-limited ticker '{cleaned_ticker}'. "
            "Try again in a few minutes, reduce the ticker list size, or screen in batches."
        ) from last_exc

    raise RuntimeError(f"Failed to fetch data for {cleaned_ticker}: {last_exc}") from last_exc
