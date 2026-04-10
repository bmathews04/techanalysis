"""
Validation helpers for normalized market data.

Primary responsibility:
- verify required columns exist
- verify enough history exists
- verify OHLC relationships are sensible
- return clear errors for the Streamlit UI
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config.settings import MIN_REQUIRED_ROWS, PRICE_COLUMNS


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    message: str
    row_count: int


def _check_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in PRICE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "Market data is missing required columns: "
            + ", ".join(missing)
        )


def _check_minimum_rows(df: pd.DataFrame, min_rows: int) -> None:
    if len(df) < min_rows:
        raise ValueError(
            f"Not enough data to analyze ticker. "
            f"Received {len(df)} rows; need at least {min_rows}."
        )


def _check_ohlc_integrity(df: pd.DataFrame) -> None:
    """
    Basic sanity checks for OHLC bars.
    """
    invalid_high = df["High"] < df[["Open", "Close", "Low"]].max(axis=1)
    invalid_low = df["Low"] > df[["Open", "Close", "High"]].min(axis=1)
    negative_volume = df["Volume"] < 0

    if invalid_high.any():
        raise ValueError("Invalid OHLC data detected: some High values are inconsistent.")

    if invalid_low.any():
        raise ValueError("Invalid OHLC data detected: some Low values are inconsistent.")

    if negative_volume.any():
        raise ValueError("Invalid volume data detected: negative volume found.")


def _drop_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows where core OHLC values are missing.
    """
    out = df.copy()
    out = out.dropna(subset=["Open", "High", "Low", "Close"])
    return out


def validate_ohlcv(
    df: pd.DataFrame,
    min_rows: int = MIN_REQUIRED_ROWS,
) -> tuple[pd.DataFrame, ValidationResult]:
    """
    Validate normalized OHLCV data.

    Parameters
    ----------
    df : pd.DataFrame
        Normalized market data.
    min_rows : int
        Minimum number of rows required for analysis.

    Returns
    -------
    tuple[pd.DataFrame, ValidationResult]
        Cleaned validated dataframe and validation summary.

    Raises
    ------
    ValueError
        If required columns or minimum row count checks fail.
    """
    out = df.copy()
    out = _drop_invalid_rows(out)

    _check_required_columns(out)
    _check_minimum_rows(out, min_rows)
    _check_ohlc_integrity(out)

    return out, ValidationResult(
        is_valid=True,
        message="Market data validated successfully.",
        row_count=len(out),
    )
