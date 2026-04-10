"""
Normalization helpers for market data.

Primary responsibility:
- standardize column names and index format
- flatten yfinance outputs if needed
- ensure downstream modules receive a predictable DataFrame
"""

from __future__ import annotations

import pandas as pd

from src.config.settings import PRICE_COLUMNS


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten a MultiIndex column structure if yfinance returns one.

    For single-ticker downloads, some yfinance versions may return:
    ('Open', 'AAPL'), ('High', 'AAPL'), etc.

    We standardize that back to:
    Open, High, Low, Close, Volume
    """
    out = df.copy()

    if isinstance(out.columns, pd.MultiIndex):
        flattened = []

        for col in out.columns:
            if not isinstance(col, tuple):
                flattened.append(str(col))
                continue

            # Prefer the price field if present in the tuple
            first = str(col[0]).strip()
            second = str(col[1]).strip() if len(col) > 1 else ""

            if first in PRICE_COLUMNS:
                flattened.append(first)
            elif second in PRICE_COLUMNS:
                flattened.append(second)
            else:
                flattened.append("_".join(str(x) for x in col if str(x).strip()))

        out.columns = flattened

    return out


def _standardize_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the DataFrame index is a sorted DatetimeIndex with no timezone.
    """
    out = df.copy()

    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index, errors="coerce")

    out = out[~out.index.isna()].copy()
    out = out.sort_index()

    if getattr(out.index, "tz", None) is not None:
        out.index = out.index.tz_localize(None)

    out.index.name = "Date"
    return out


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize common column naming quirks.
    """
    out = df.copy()

    rename_map = {}
    for col in out.columns:
        normalized = str(col).strip().title()
        rename_map[col] = normalized

    out = out.rename(columns=rename_map)

    # Some providers may use Adj Close. Keep it if present, but analysis will
    # focus on Close unless explicitly changed later.
    return out


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all columns to numeric where possible.
    """
    out = df.copy()
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw OHLCV market data into a predictable schema.

    Expected output:
    - DatetimeIndex named 'Date'
    - columns like Open, High, Low, Close, Volume
    - numeric dtypes where possible
    - duplicate index rows removed

    Parameters
    ----------
    df : pd.DataFrame
        Raw price data from provider.

    Returns
    -------
    pd.DataFrame
        Cleaned and normalized market data.
    """
    out = df.copy()

    out = _flatten_columns(out)
    out = _standardize_columns(out)
    out = _standardize_index(out)
    out = _coerce_numeric(out)

    out = out[~out.index.duplicated(keep="last")].copy()

    # Keep only rows that have at least one real value
    out = out.dropna(how="all")

    return out
