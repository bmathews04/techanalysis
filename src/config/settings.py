"""
Application-wide configuration values.

Keep this file lightweight and focused on safe defaults.
Avoid putting business logic here.
"""

from __future__ import annotations

DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_TICKER = "AAPL"

SUPPORTED_PERIODS = [
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "max",
]

SUPPORTED_INTERVALS = [
    "1d",
    "1wk",
]

MIN_REQUIRED_ROWS = 60

PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

ROLLING_WINDOWS = {
    "short_ma": 20,
    "medium_ma": 50,
    "long_ma": 200,
    "rsi": 14,
    "atr": 14,
    "bbands": 20,
    "volume_ma": 20,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
}
