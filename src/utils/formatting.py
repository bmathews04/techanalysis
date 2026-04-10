"""
Formatting helpers for UI display and text output.

Primary responsibility:
- keep lightweight display formatting out of page files
- standardize common number and percent presentation
"""

from __future__ import annotations

import math


def format_price(value: float | int | None, decimals: int = 2) -> str:
    """
    Format a numeric value as a price-like string.
    """
    if value is None:
        return "N/A"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if math.isnan(num):
        return "N/A"

    return f"{num:,.{decimals}f}"


def format_percent(value: float | int | None, decimals: int = 2) -> str:
    """
    Format a numeric value as a percent string.
    """
    if value is None:
        return "N/A"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if math.isnan(num):
        return "N/A"

    return f"{num:.{decimals}f}%"


def format_multiple(value: float | int | None, decimals: int = 2) -> str:
    """
    Format a numeric value as an 'x' multiple.
    """
    if value is None:
        return "N/A"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if math.isnan(num):
        return "N/A"

    return f"{num:.{decimals}f}x"


def format_score(value: float | int | None) -> str:
    """
    Format a score on a 0-100 scale.
    """
    if value is None:
        return "N/A"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if math.isnan(num):
        return "N/A"

    return f"{round(num)}/100"


def format_confidence_10(value: float | int | None, decimals: int = 1) -> str:
    """
    Format a confidence score on a 0-10 scale.
    """
    if value is None:
        return "N/A"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if math.isnan(num):
        return "N/A"

    return f"{num:.{decimals}f}/10"
